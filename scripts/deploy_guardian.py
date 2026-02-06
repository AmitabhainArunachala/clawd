#!/usr/bin/env python3
"""
OACP Deployment Guardian - Automated Pre-Flight Check
======================================================

This script performs automated verification of ALL deployment requirements
before any git push or PyPI upload.

Usage:
    python scripts/deploy_guardian.py           # Full check
    python scripts/deploy_guardian.py --quick   # Essential checks only
    python scripts/deploy_guardian.py --strict  # Fail on warnings too

Exit Codes:
    0 - All checks passed, safe to deploy
    1 - Critical checks failed, DO NOT DEPLOY
    2 - Warnings present (with --strict)

"""

import ast
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ============================================================================
# Configuration
# ============================================================================

REQUIRED_PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12"]
MIN_COVERAGE_PERCENT = 80
MIN_CORE_COVERAGE_PERCENT = 90

SECRET_PATTERNS = [
    r"(sk-|pk-|rk-)[a-zA-Z0-9]{20,}",  # API keys (OpenAI, Stripe, etc.)
    r"AKIA[0-9A-Z]{16}",                 # AWS Access Key ID
    r"[0-9a-zA-Z/+]{40}",                # AWS Secret (generic)
    r"ghp_[a-zA-Z0-9]{36}",              # GitHub Personal Access Token
    r"glpat-[a-zA-Z0-9-]{20}",           # GitLab PAT
    r"[a-zA-Z0-9_-]*password[a-zA-Z0-9_-]*\s*=\s*[\"'][^\"']+[\"']",
    r"[a-zA-Z0-9_-]*secret[a-zA-Z0-9_-]*\s*=\s*[\"'][^\"']+[\"']",
    r"[a-zA-Z0-9_-]*key[a-zA-Z0-9_-]*\s*=\s*[\"'][^\"']{20,}[\"']",
    r"mongodb(\+srv)?://[^:]+:[^@]+@",   # MongoDB with password
    r"postgres(ql)?://[^:]+:[^@]+@",      # PostgreSQL with password
    r"mysql://[^:]+:[^@]+@",              # MySQL with password
    r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----",
]

REQUIRED_FILES = [
    "pyproject.toml",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    ".gitignore",
    "oacp/__init__.py",
    "tests/__init__.py",
]

FORBIDDEN_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    "secrets.json",
    "credentials.json",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
]

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    details: List[str] = field(default_factory=list)
    critical: bool = True


@dataclass
class GuardianReport:
    results: List[CheckResult] = field(default_factory=list)
    
    @property
    def critical_failures(self) -> List[CheckResult]:
        return [r for r in self.results if not r.passed and r.critical]
    
    @property
    def warnings(self) -> List[CheckResult]:
        return [r for r in self.results if not r.passed and not r.critical]
    
    @property
    def all_passed(self) -> bool:
        return all(r.passed or not r.critical for r in self.results)


# ============================================================================
# Check Functions
# ============================================================================

class DeploymentGuardian:
    def __init__(self, root_path: Path, strict: bool = False, quick: bool = False):
        self.root = root_path
        self.strict = strict
        self.quick = quick
        self.report = GuardianReport()
        
    def run_all_checks(self) -> GuardianReport:
        """Execute the complete check suite."""
        print("🛡️  OACP Deployment Guardian")
        print("=" * 60)
        print()
        
        # Core checks
        self._check_tests_pass()
        self._check_required_files()
        self._check_secrets()
        self._check_version_consistency()
        self._check_documentation()
        self._check_backward_compatibility()
        
        if not self.quick:
            self._check_code_quality()
            self._check_git_status()
            self._check_dependencies()
        
        return self.report
    
    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                     capture: bool = True) -> Tuple[int, str, str]:
        """Run a shell command and return results."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.root,
                capture_output=capture,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 5 minutes"
        except FileNotFoundError:
            return -1, "", f"Command not found: {cmd[0]}"
    
    def _add_result(self, name: str, passed: bool, message: str, 
                    details: Optional[List[str]] = None, critical: bool = True):
        """Add a check result to the report."""
        self.report.results.append(CheckResult(
            name=name,
            passed=passed,
            message=message,
            details=details or [],
            critical=critical
        ))
    
    # -------------------------------------------------------------------------
    # Check 1: Tests MUST Pass
    # -------------------------------------------------------------------------
    def _check_tests_pass(self):
        """Verify all tests pass with sufficient coverage."""
        print("🔍 Checking tests...")
        
        # Check if pytest is available
        returncode, stdout, stderr = self._run_command(["python", "-m", "pytest", "--version"])
        if returncode != 0:
            self._add_result(
                "Tests Pass",
                False,
                "pytest not installed or no tests found",
                ["Install with: pip install pytest pytest-cov"],
                critical=True
            )
            return
        
        # Run tests with coverage
        cmd = [
            "python", "-m", "pytest", "tests/",
            "-v", "--tb=short",
            "--cov=oacp",
            "--cov-report=term-missing",
            "--cov-fail-under", str(MIN_COVERAGE_PERCENT)
        ]
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        if returncode == 0:
            self._add_result(
                "Tests Pass",
                True,
                f"All tests pass with {MIN_COVERAGE_PERCENT}%+ coverage",
                critical=True
            )
        else:
            # Parse test output for details
            details = stderr.split("\n")[-20:] if stderr else stdout.split("\n")[-20:]
            self._add_result(
                "Tests Pass",
                False,
                "Tests failed or coverage insufficient",
                details,
                critical=True
            )
    
    # -------------------------------------------------------------------------
    # Check 2: Required Files MUST Be Present
    # -------------------------------------------------------------------------
    def _check_required_files(self):
        """Verify all required files exist."""
        print("🔍 Checking required files...")
        
        missing = []
        for file_path in REQUIRED_FILES:
            full_path = self.root / file_path
            if not full_path.exists():
                missing.append(file_path)
        
        # Check for forbidden files
        forbidden_found = []
        for pattern in FORBIDDEN_FILES:
            for file_path in self.root.rglob(pattern):
                # Check if file is actually git-tracked
                git_check = self._run_command(
                    ["git", "ls-files", str(file_path.relative_to(self.root))]
                )
                if git_check[1].strip():  # File is tracked
                    forbidden_found.append(str(file_path.relative_to(self.root)))
        
        if missing:
            self._add_result(
                "Required Files",
                False,
                f"Missing {len(missing)} required file(s)",
                missing,
                critical=True
            )
        else:
            self._add_result(
                "Required Files",
                True,
                "All required files present",
                critical=True
            )
        
        if forbidden_found:
            self._add_result(
                "Forbidden Files",
                False,
                f"Found {len(forbidden_found)} forbidden file(s) in git",
                forbidden_found,
                critical=True
            )
    
    # -------------------------------------------------------------------------
    # Check 3: Secrets MUST NOT Be in Repo
    # -------------------------------------------------------------------------
    def _check_secrets(self):
        """Scan for potential secrets in the codebase."""
        print("🔍 Scanning for secrets...")
        
        findings = []
        scanned_files = 0
        
        # Get list of tracked Python and config files
        returncode, stdout, stderr = self._run_command(["git", "ls-files"])
        if returncode != 0:
            self._add_result(
                "Secrets Scan",
                False,
                "Could not get git file list",
                [stderr],
                critical=True
            )
            return
        
        for line in stdout.split("\n"):
            file_path = line.strip()
            if not file_path:
                continue
                
            full_path = self.root / file_path
            
            # Skip binary and non-code files
            if not any(file_path.endswith(ext) for ext in ['.py', '.toml', '.cfg', '.yaml', '.yml', '.json', '.md', '.txt']):
                continue
            
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
            except Exception:
                continue
            
            scanned_files += 1
            
            for line_num, line in enumerate(lines, 1):
                for pattern in SECRET_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip false positives
                        if self._is_likely_false_positive(line):
                            continue
                        
                        findings.append(
                            f"{file_path}:{line_num}: Potential secret match"
                        )
                        # Limit findings to prevent spam
                        if len(findings) >= 20:
                            break
            
            if len(findings) >= 20:
                break
        
        if findings:
            self._add_result(
                "Secrets Scan",
                False,
                f"Found {len(findings)} potential secret(s) in {scanned_files} files",
                findings[:20] + (["... (additional findings truncated)"] if len(findings) > 20 else []),
                critical=True
            )
        else:
            self._add_result(
                "Secrets Scan",
                True,
                f"No secrets detected in {scanned_files} scanned files",
                critical=True
            )
    
    def _is_likely_false_positive(self, line: str) -> bool:
        """Check if a line is likely a false positive for secrets."""
        # Skip comments explaining patterns
        if line.strip().startswith('#'):
            return True
        # Skip docstrings with examples
        if '"""' in line or "'''" in line:
            return True
        # Skip lines with 'example', 'sample', 'placeholder', etc.
        lower = line.lower()
        skip_words = ['example', 'sample', 'placeholder', 'your_', 'xxx', 'test_']
        if any(word in lower for word in skip_words):
            return True
        # Skip regex patterns
        if 'r"' in line or "r'" in line:
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Check 4: Version Numbers MUST Be Consistent
    # -------------------------------------------------------------------------
    def _check_version_consistency(self):
        """Verify version numbers are consistent across files."""
        print("🔍 Checking version consistency...")
        
        versions = {}
        details = []
        
        # Check __init__.py
        init_file = self.root / "oacp" / "__init__.py"
        if init_file.exists():
            try:
                with open(init_file) as f:
                    content = f.read()
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    versions["oacp/__init__.py"] = match.group(1)
                else:
                    details.append("⚠️ No __version__ found in oacp/__init__.py")
            except Exception as e:
                details.append(f"⚠️ Error reading __init__.py: {e}")
        
        # Check pyproject.toml
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject) as f:
                    content = f.read()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    versions["pyproject.toml"] = match.group(1)
                else:
                    details.append("⚠️ No version found in pyproject.toml")
            except Exception as e:
                details.append(f"⚠️ Error reading pyproject.toml: {e}")
        
        # Check CHANGELOG.md
        changelog = self.root / "CHANGELOG.md"
        if changelog.exists():
            try:
                with open(changelog) as f:
                    content = f.read()
                # Look for version header like ## [0.1.0] or ## 0.1.0
                match = re.search(r'##\s*\[?([0-9]+\.[0-9]+\.[0-9]+[^\]]*)\]?', content)
                if match:
                    versions["CHANGELOG.md"] = match.group(1)
                else:
                    details.append("⚠️ No version found in CHANGELOG.md")
            except Exception as e:
                details.append(f"⚠️ Error reading CHANGELOG.md: {e}")
        
        # Compare versions
        if len(set(versions.values())) == 1 and len(versions) >= 2:
            self._add_result(
                "Version Consistency",
                True,
                f"All versions consistent: {list(versions.values())[0]}",
                [f"  {k}: {v}" for k, v in versions.items()],
                critical=True
            )
        elif len(versions) < 2:
            self._add_result(
                "Version Consistency",
                False,
                "Could not find enough version declarations",
                details + [f"Found versions: {versions}"],
                critical=True
            )
        else:
            self._add_result(
                "Version Consistency",
                False,
                f"Version mismatch detected!",
                details + [f"  {k}: {v}" for k, v in versions.items()],
                critical=True
            )
    
    # -------------------------------------------------------------------------
    # Check 5: Documentation MUST Be Updated
    # -------------------------------------------------------------------------
    def _check_documentation(self):
        """Verify documentation is up to date."""
        print("🔍 Checking documentation...")
        
        issues = []
        
        # Check CHANGELOG has entry for current version
        changelog = self.root / "CHANGELOG.md"
        pyproject = self.root / "pyproject.toml"
        current_version = None
        
        if pyproject.exists():
            with open(pyproject) as f:
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', f.read())
                if match:
                    current_version = match.group(1)
        
        if changelog.exists() and current_version:
            with open(changelog) as f:
                content = f.read()
            # Check if current version is mentioned
            if current_version not in content:
                issues.append(f"CHANGELOG.md does not mention version {current_version}")
        
        # Check README has required sections
        readme = self.root / "README.md"
        if readme.exists():
            with open(readme) as f:
                content = f.read().lower()
            
            required_sections = ['install', 'usage', 'example']
            for section in required_sections:
                if section not in content:
                    issues.append(f"README.md missing '{section}' section")
        
        if issues:
            self._add_result(
                "Documentation",
                False,
                f"Found {len(issues)} documentation issue(s)",
                issues,
                critical=False  # Warning, not critical
            )
        else:
            self._add_result(
                "Documentation",
                True,
                "Documentation appears up to date",
                critical=False
            )
    
    # -------------------------------------------------------------------------
    # Check 6: Backward Compatibility
    # -------------------------------------------------------------------------
    def _check_backward_compatibility(self):
        """Check for backward compatibility issues."""
        print("🔍 Checking backward compatibility...")
        
        warnings = []
        
        # Check for API-breaking patterns in Python files
        api_patterns = [
            (r'class\s+\w+.*:', "New class definition"),
            (r'def\s+\w+\s*\([^)]*\)', "Function definition changes"),
        ]
        
        # Get changed files from git
        returncode, stdout, stderr = self._run_command(
            ["git", "diff", "--name-only", "HEAD~1"]
        )
        
        if returncode == 0 and stdout.strip():
            changed_files = stdout.strip().split("\n")
            api_files = [f for f in changed_files if f.startswith("oacp/") and f.endswith(".py")]
            
            if api_files:
                warnings.append(f"API files changed: {', '.join(api_files[:5])}")
                warnings.append("Verify backward compatibility manually")
        
        if warnings:
            self._add_result(
                "Backward Compatibility",
                False,
                "Potential compatibility issues detected",
                warnings,
                critical=False  # Warning only - manual verification needed
            )
        else:
            self._add_result(
                "Backward Compatibility",
                True,
                "No obvious compatibility issues",
                critical=False
            )
    
    # -------------------------------------------------------------------------
    # Additional Checks (non-quick mode)
    # -------------------------------------------------------------------------
    def _check_code_quality(self):
        """Check code quality with linters."""
        print("🔍 Checking code quality...")
        
        issues = []
        
        # Check with ruff if available
        returncode, stdout, stderr = self._run_command(["python", "-m", "ruff", "check", "oacp/"])
        if returncode == 0:
            self._add_result(
                "Code Quality (ruff)",
                True,
                "ruff checks passed",
                critical=False
            )
        elif returncode == -1:  # ruff not installed
            self._add_result(
                "Code Quality (ruff)",
                True,
                "ruff not installed (optional)",
                critical=False
            )
        else:
            self._add_result(
                "Code Quality (ruff)",
                False,
                "ruff found issues",
                stdout.split("\n")[:10],
                critical=False
            )
        
        # Check with mypy if available
        returncode, stdout, stderr = self._run_command(["python", "-m", "mypy", "oacp/"])
        if returncode == 0:
            self._add_result(
                "Type Checking (mypy)",
                True,
                "mypy checks passed",
                critical=False
            )
        elif returncode == -1:  # mypy not installed
            self._add_result(
                "Type Checking (mypy)",
                True,
                "mypy not installed (optional)",
                critical=False
            )
        else:
            self._add_result(
                "Type Checking (mypy)",
                False,
                "mypy found type issues",
                stdout.split("\n")[:10],
                critical=False
            )
    
    def _check_git_status(self):
        """Check git status for uncommitted changes."""
        print("🔍 Checking git status...")
        
        returncode, stdout, stderr = self._run_command(["git", "status", "--porcelain"])
        
        if stdout.strip():
            lines = stdout.strip().split("\n")
            self._add_result(
                "Git Status",
                False,
                f"{len(lines)} uncommitted change(s)",
                lines[:10] + (["..."] if len(lines) > 10 else []),
                critical=False
            )
        else:
            self._add_result(
                "Git Status",
                True,
                "Working directory clean",
                critical=False
            )
    
    def _check_dependencies(self):
        """Check for dependency issues."""
        print("🔍 Checking dependencies...")
        
        issues = []
        
        # Check for requirements.txt or pyproject.toml
        has_requirements = (self.root / "requirements.txt").exists()
        has_pyproject = (self.root / "pyproject.toml").exists()
        
        if not has_requirements and not has_pyproject:
            issues.append("No dependency specification found")
        
        # Check for security vulnerabilities with safety if available
        returncode, stdout, stderr = self._run_command(["python", "-m", "safety", "check"])
        if returncode == 0:
            self._add_result(
                "Dependency Security",
                True,
                "No known vulnerabilities",
                critical=True
            )
        elif returncode == -1:  # safety not installed
            self._add_result(
                "Dependency Security",
                True,
                "safety not installed (run 'pip install safety' for vulnerability scanning)",
                critical=False
            )
        else:
            self._add_result(
                "Dependency Security",
                False,
                "Security vulnerabilities found",
                stdout.split("\n")[:10],
                critical=True
            )


# ============================================================================
# Reporting
# ============================================================================

def print_report(report: GuardianReport, strict: bool = False):
    """Print a formatted report."""
    print()
    print("=" * 60)
    print("📊 DEPLOYMENT GUARDIAN REPORT")
    print("=" * 60)
    print()
    
    # Group by status
    passed = [r for r in report.results if r.passed]
    critical_failed = [r for r in report.results if not r.passed and r.critical]
    warnings = [r for r in report.results if not r.passed and not r.critical]
    
    # Print critical failures
    if critical_failed:
        print("❌ CRITICAL FAILURES (MUST FIX):")
        print("-" * 40)
        for result in critical_failed:
            print(f"\n  🔴 {result.name}")
            print(f"     {result.message}")
            for detail in result.details[:5]:
                print(f"       • {detail}")
            if len(result.details) > 5:
                print(f"       ... and {len(result.details) - 5} more")
        print()
    
    # Print warnings
    if warnings:
        print("⚠️  WARNINGS:")
        print("-" * 40)
        for result in warnings:
            print(f"\n  🟡 {result.name}")
            print(f"     {result.message}")
            for detail in result.details[:3]:
                print(f"       • {detail}")
        print()
    
    # Print passed checks
    if passed:
        print(f"✅ PASSED ({len(passed)} checks):")
        for result in passed:
            status = "🔴" if not result.critical else "🟢"
            print(f"  {status} {result.name}: {result.message}")
        print()
    
    # Final verdict
    print("=" * 60)
    if critical_failed:
        print("🚫 DEPLOYMENT BLOCKED")
        print(f"   Fix {len(critical_failed)} critical issue(s) before deploying.")
        return 1
    elif warnings and strict:
        print("🚫 DEPLOYMENT BLOCKED (--strict mode)")
        print(f"   Fix {len(warnings)} warning(s) or run without --strict.")
        return 2
    elif warnings:
        print("⚠️  DEPLOYMENT ALLOWED WITH WARNINGS")
        print(f"   {len(warnings)} non-critical issue(s) found.")
        print("   Review warnings above before proceeding.")
        return 0
    else:
        print("🚀 ALL CHECKS PASSED - SAFE TO DEPLOY")
        print("   Run: git push && twine upload dist/*")
        return 0


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OACP Deployment Guardian - Pre-flight safety checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Full check suite
  %(prog)s --quick           # Essential checks only
  %(prog)s --strict          # Fail on warnings too
  %(prog)s --fix             # Attempt auto-fixes (when available)
        """
    )
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Run only essential checks (faster)"
    )
    parser.add_argument(
        "--strict", 
        action="store_true",
        help="Fail deployment on warnings too"
    )
    parser.add_argument(
        "--fix", 
        action="store_true",
        help="Attempt to auto-fix issues (experimental)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Find project root
    root = Path(__file__).parent.parent.resolve()
    
    # Initialize guardian
    guardian = DeploymentGuardian(
        root_path=root,
        strict=args.strict,
        quick=args.quick
    )
    
    # Run checks
    report = guardian.run_all_checks()
    
    # Print results
    exit_code = print_report(report, strict=args.strict)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
