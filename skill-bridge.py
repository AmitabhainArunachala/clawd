#!/usr/bin/env python3
"""
skill-bridge: Unified Skill Launcher
Makes all 37+ skills actually executable by detecting type and launching correctly.
"""

import sys
import subprocess
from pathlib import Path
import argparse

SKILL_DIR = Path.home() / "clawd" / "skills"

def detect_skill_type(skill_path: Path) -> str:
    """Detect what type of skill this is."""
    if not skill_path.exists():
        return "missing"
    
    # Check for CLI entry point
    if (skill_path / "cli.py").exists():
        return "cli"
    
    # Check for Python package with main
    if (skill_path / "__init__.py").exists():
        return "package"
    
    # Check for setup.py (installable)
    if (skill_path / "setup.py").exists() or (skill_path / "pyproject.toml").exists():
        return "installable"
    
    # Check for SKILL.md only
    if (skill_path / "SKILL.md").exists():
        return "documentation"
    
    return "unknown"

def launch_skill(skill_name: str, args: list) -> int:
    """Launch a skill with given arguments."""
    skill_path = SKILL_DIR / skill_name
    skill_type = detect_skill_type(skill_path)
    
    if skill_type == "missing":
        print(f"❌ Skill '{skill_name}' not found in {SKILL_DIR}")
        return 1
    
    if skill_type == "cli":
        # Run CLI directly
        return subprocess.run([sys.executable, str(skill_path / "cli.py"), *args]).returncode
    
    if skill_type == "package":
        # Add to path and try to import main
        sys.path.insert(0, str(skill_path.parent))
        module_name = skill_name.replace("-", "_")
        try:
            module = __import__(module_name)
            if hasattr(module, 'main'):
                return module.main(args)
            else:
                print(f"⚠️  Skill '{skill_name}' has no main() function")
                print(f"Available: {[x for x in dir(module) if not x.startswith('_')]}")
                return 1
        except Exception as e:
            print(f"❌ Import error: {e}")
            return 1
    
    if skill_type == "installable":
        # Try to run as module
        module_name = skill_name.replace("-", "_")
        return subprocess.run([sys.executable, "-m", module_name, *args]).returncode
    
    if skill_type == "documentation":
        print(f"📖 Skill '{skill_name}' is documentation-only")
        print(f"   See: {skill_path / 'SKILL.md'}")
        return 0
    
    print(f"❓ Unknown skill type for '{skill_name}'")
    return 1

def list_skills():
    """List all skills and their types."""
    print("=" * 60)
    print("🔧 SKILL-BRIDGE: Available Skills")
    print("=" * 60)
    
    for skill_dir in sorted(SKILL_DIR.iterdir()):
        if skill_dir.is_dir():
            skill_type = detect_skill_type(skill_dir)
            icon = {"cli": "🔌", "package": "📦", "installable": "⚙️", 
                   "documentation": "📖", "unknown": "❓", "missing": "❌"}.get(skill_type, "❓")
            print(f"{icon} {skill_dir.name:<30} ({skill_type})")
    
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="skill-bridge: Launch any Clawd skill",
        usage="skill-bridge [-l] <skill-name> [args...]"
    )
    parser.add_argument("skill", nargs="?", help="Name of skill to launch")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to skill")
    parser.add_argument("-l", "--list", action="store_true", help="List all skills")
    
    args = parser.parse_args()
    
    if args.list:
        list_skills()
        return 0
    
    if not args.skill:
        parser.print_help()
        return 1
    
    return launch_skill(args.skill, args.args)

if __name__ == "__main__":
    sys.exit(main())
