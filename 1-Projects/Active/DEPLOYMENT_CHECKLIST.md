# 🛡️ OACP Deployment Safety Checklist

> **⚠️ CRITICAL:** Complete ALL checks before ANY git push or PyPI upload.  
> **🔒 Guardian:** Run `python scripts/deploy_guardian.py` to verify automatically.

---

## Pre-Flight Status

| Check | Status | Verified By |
|-------|--------|-------------|
| Tests Passing | ⬜ | |
| Files Present | ⬜ | |
| Secrets Clean | ⬜ | |
| Versions Synced | ⬜ | |
| Docs Updated | ⬜ | |
| Backward Compatible | ⬜ | |
| **FINAL GO/NO-GO** | ⬜ | |

---

## 1. ✅ Tests MUST Pass

### Required Test Suites

```bash
# Run these commands and verify ALL pass
pytest tests/ -v                           # Unit tests
pytest tests/ -m integration -v            # Integration tests
pytest tests/ --cov=oacp --cov-report=term-missing  # Coverage
```

### Coverage Requirements

- [ ] **Minimum 80%** overall coverage
- [ ] **Minimum 90%** for core/ modules
- [ ] **100%** for security-critical code (attestation/, protocol/)

### Smoke Tests

```bash
# Quick functionality check
python -c "import oacp; print(oacp.__version__)"
python scripts/smoke_test.py
```

### Platform Matrix

- [ ] Tests pass on Python 3.9
- [ ] Tests pass on Python 3.10
- [ ] Tests pass on Python 3.11
- [ ] Tests pass on Python 3.12
- [ ] Tests pass on Linux
- [ ] Tests pass on macOS (if applicable)

---

## 2. 📁 Files MUST Be Present

### Critical Files Checklist

```
Repository Root
├── pyproject.toml          # Package metadata & build config
├── README.md               # Primary documentation
├── LICENSE                 # Apache 2.0 or MIT
├── CHANGELOG.md            # Version history
├── .gitignore              # Prevents secret leakage
├── MANIFEST.in             # Specifies package files
│
├── oacp/                   # Main package
│   ├── __init__.py         # Version info MUST be here
│   ├── core/
│   ├── protocol/
│   ├── runtime/
│   └── attestation/
│
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_protocol.py
│   └── conftest.py
│
├── scripts/                # Utility scripts
│   └── deploy_guardian.py  # THIS CHECKLIST AUTOMATION
│
└── docs/                   # Documentation
    ├── API.md
    ├── PROTOCOL.md
    └── DEPLOYMENT.md
```

### Version File Locations (MUST be consistent)

- [ ] `oacp/__init__.py` → `__version__ = "X.Y.Z"`
- [ ] `pyproject.toml` → `version = "X.Y.Z"`
- [ ] `CHANGELOG.md` → Header for version X.Y.Z exists

---

## 3. 🔐 Secrets MUST NOT Be in Repo

### Secret Patterns to Reject

```bash
# Run these scans BEFORE committing
git-secrets --scan                          # AWS keys, etc.
truffleHog --regex --entropy=False .       # Deep secret scan
detect-secrets scan --all-files             # Alternative scanner
```

### Explicitly Forbidden

- [ ] No API keys (OpenAI, Anthropic, etc.)
- [ ] No AWS credentials (access key ID, secret key)
- [ ] No database connection strings with passwords
- [ ] No private keys (.pem, .key files)
- [ ] No `.env` files committed
- [ ] No `credentials.json` or similar
- [ ] No hardcoded passwords in test files
- [ ] No JWT secrets or signing keys

### Safe Configuration Pattern

```python
# ✅ CORRECT: Use environment variables
import os
API_KEY = os.environ.get("OACP_API_KEY")

# ❌ WRONG: Hardcoded secret
API_KEY = "sk-abc123xyz789"
```

### .gitignore Requirements

```gitignore
# Secrets
.env
.env.*
*.pem
*.key
*credentials*
secrets.json
config/local*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
```

---

## 4. 🔢 Version Numbers MUST Be Consistent

### Version Synchronization Check

All these files MUST have the same version number:

```bash
# Extract versions - should all match
grep "__version__" oacp/__init__.py
grep "version" pyproject.toml | head -1
grep -E "^##? \[?[0-9]+\.[0-9]+\.[0-9]+" CHANGELOG.md | head -1
```

### Semantic Versioning Rules

| Version Change | When to Use |
|----------------|-------------|
| **MAJOR** (X.y.z) | Breaking API changes |
| **MINOR** (x.Y.z) | New features, backward compatible |
| **PATCH** (x.y.Z) | Bug fixes only |

### Pre-Release Checklist

- [ ] Version follows semver (e.g., `0.1.2`, `1.0.0a1`)
- [ ] No `dev`, `alpha`, or `rc` markers for production
- [ ] Git tag will match version exactly: `git tag vX.Y.Z`

---

## 5. 📚 Documentation MUST Be Updated

### Required Updates

- [ ] **CHANGELOG.md**: New version entry with date
  ```markdown
  ## [0.1.2] - 2026-02-05
  ### Added
  - New feature X
  ### Fixed
  - Bug Y (#123)
  ### Changed
  - Deprecated Z
  ```

- [ ] **README.md**: 
  - [ ] Installation instructions work
  - [ ] Quick start example runs
  - [ ] API changes documented
  - [ ] Badges updated (version, build status, coverage)

- [ ] **API.md**: All public functions/classes documented
- [ ] **PROTOCOL.md**: Protocol version updated if changed

### Documentation Quality

- [ ] No broken internal links
- [ ] Code examples are runnable
- [ ] Type hints present on public APIs
- [ ] Docstrings follow Google/NumPy style

---

## 6. 🔄 Backward Compatibility MUST Be Preserved

### API Compatibility Check

- [ ] All existing public functions still exist
- [ ] Function signatures unchanged (or extended with defaults)
- [ ] Return types unchanged (or documented migration)
- [ ] No removed modules without deprecation period

### Breaking Change Protocol

If breaking changes are **unavoidable**:

- [ ] MAJOR version bumped (semver)
- [ ] `DeprecationWarning` added in previous minor version
- [ ] Migration guide in CHANGELOG.md
- [ ] `UPGRADING.md` document if significant

### Runtime Compatibility

- [ ] Python 3.9+ support maintained
- [ ] No new required dependencies without discussion
- [ ] Optional dependencies handled gracefully

---

## 7. 🚀 Final Release Steps

### Git Workflow

```bash
# 1. Ensure clean working directory
git status  # Should be clean

# 2. Run full test suite
pytest tests/ -v --tb=short

# 3. Run guardian check
python scripts/deploy_guardian.py

# 4. Create signed commit
git add -A
git commit -S -m "Release vX.Y.Z"

# 5. Tag release
git tag -s vX.Y.Z -m "Release version X.Y.Z"

# 6. Push (only after ALL checks pass!)
git push origin main
git push origin vX.Y.Z
```

### PyPI Upload (if applicable)

```bash
# 1. Build distribution
python -m build

# 2. Verify build
twine check dist/*

# 3. Test upload to TestPyPI first!
twine upload --repository testpypi dist/*

# 4. Verify on TestPyPI
pip install --index-url https://test.pypi.org/simple/ oacp

# 5. Production upload (IRREVERSIBLE!)
twine upload dist/*
```

---

## 8. 🆘 Emergency Rollback

If a bad release occurs:

```bash
# Delete tag (if needed)
git push --delete origin vX.Y.Z
git tag -d vX.Y.Z

# PyPI yank (marks as broken, doesn't delete)
twine yank oacp-X.Y.Z

# Fix and re-release as X.Y.Z+1 (never reuse version!)
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT QUICK CHECK                   │
├─────────────────────────────────────────────────────────────┤
│ BEFORE PUSH:                                                │
│   ☐ pytest passes          ☐ guardian.py passes            │
│   ☐ version consistent     ☐ no secrets in git             │
│   ☐ changelog updated      ☐ backward compatible           │
├─────────────────────────────────────────────────────────────┤
│ COMMANDS:                                                   │
│   python scripts/deploy_guardian.py    # Full check        │
│   pytest tests/ -q                     # Quick test        │
│   git diff --stat                      # Review changes    │
├─────────────────────────────────────────────────────────────┤
│ EMERGENCY:                                                  │
│   git revert HEAD            # Undo last commit            │
│   twine yank oacp-X.Y.Z      # Remove from PyPI            │
└─────────────────────────────────────────────────────────────┘
```

---

## Guardian Sign-Off

**I confirm:**
- [ ] All automated checks pass
- [ ] I have reviewed the diff
- [ ] This release is safe to deploy

**Deployed by:** _________________  
**Date:** _________________  
**Version:** _________________

---

*Generated by OACP_DEPLOYMENT_GUARDIAN*  
*Last updated: 2026-02-05*
