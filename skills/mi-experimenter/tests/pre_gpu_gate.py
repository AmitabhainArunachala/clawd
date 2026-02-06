#!/usr/bin/env python3
"""
Pre-GPU Gate — Validation before burning GPU hours
All checks must pass before any GPU cluster runs
"""

import sys
import subprocess
import importlib
from pathlib import Path

CHECKS_PASSED = 0
CHECKS_FAILED = 0

def check(name, condition, details=""):
    global CHECKS_PASSED, CHECKS_FAILED
    if condition:
        print(f"✅ {name}")
        CHECKS_PASSED += 1
        return True
    else:
        print(f"❌ {name}")
        if details:
            print(f"   {details}")
        CHECKS_FAILED += 1
        return False

print("=" * 70)
print("PRE-GPU GATE — Validation Checklist")
print("=" * 70)

# 1. Import checks
print("\n1. IMPORT CHECKS")
try:
    from mi_experimenter import RVCausalValidator
    check("RVCausalValidator imports", True)
except ImportError as e:
    check("RVCausalValidator imports", False, str(e))

try:
    from mi_experimenter import CrossArchitectureSuite
    check("CrossArchitectureSuite imports", True)
except ImportError as e:
    check("CrossArchitectureSuite imports", False, str(e))

try:
    from mi_experimenter import MLPAblator
    check("MLPAblator imports", True)
except ImportError as e:
    check("MLPAblator imports", False, str(e))

# 2. Smoke test
print("\n2. SMOKE TEST (GPT-2)")
smoke_test = Path(__file__).parent / "smoke_test.py"
if smoke_test.exists():
    result = subprocess.run(
        ["python3", str(smoke_test), "--quick"],
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes max
    )
    check("Smoke test completes", result.returncode == 0, result.stderr)
else:
    check("Smoke test exists", False, "smoke_test.py not found")

# 3. Determinism check
print("\n3. DETERMINISM CHECK")
try:
    import torch
    torch.manual_seed(42)
    x1 = torch.randn(10)
    
    torch.manual_seed(42)
    x2 = torch.randn(10)
    
    check("PyTorch deterministic", torch.allclose(x1, x2))
except Exception as e:
    check("PyTorch deterministic", False, str(e))

# 4. Code quality
print("\n4. CODE QUALITY")
experiments_dir = Path(__file__).parent.parent / "experiments"
if experiments_dir.exists():
    py_files = list(experiments_dir.glob("*.py"))
    check(f"Experiments directory has files", len(py_files) > 0, f"Found {len(py_files)} files")
    
    # Check for TODO/FIXME
    todo_count = 0
    for f in py_files:
        content = f.read_text()
        todo_count += content.count("TODO") + content.count("FIXME") + content.count("XXX")
    check("Low TODO count", todo_count < 10, f"Found {todo_count} TODOs/FIXMEs")
else:
    check("Experiments directory exists", False)

# 5. Documentation sync
print("\n5. DOCUMENTATION SYNC")
skill_md = Path(__file__).parent.parent / "SKILL.md"
if skill_md.exists():
    content = skill_md.read_text()
    check("SKILL.md exists", True)
    check("SKILL.md mentions RVCausalValidator", "RVCausalValidator" in content)
    check("SKILL.md has corrected status", "TIER 1: IRONCLAD" in content)
else:
    check("SKILL.md exists", False)

# Summary
print("\n" + "=" * 70)
print(f"SUMMARY: {CHECKS_PASSED} passed, {CHECKS_FAILED} failed")
print("=" * 70)

if CHECKS_FAILED == 0:
    print("✅ ALL CHECKS PASSED — GPU ready")
    sys.exit(0)
else:
    print("❌ CHECKS FAILED — Fix before GPU run")
    print("\nRun: cd ~/clawd/skills/mi-experimenter && python3 tests/smoke_test.py")
    sys.exit(1)
