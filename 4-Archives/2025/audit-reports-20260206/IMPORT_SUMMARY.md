# Import Graph Analysis - Executive Summary

## Overview
Complete import graph analysis for the clawd repository with **80 Python files**, **49 internal modules**, and **77 external dependencies**.

---

## Key Findings

### ✅ Strengths
1. **No Circular Dependencies** - Clean import graph with no cycles
2. **Clear Layer Architecture** - Well-defined hierarchy (Core → Protocol → Application)
3. **Minimal Cross-Coupling** - Most dependencies are within their domains

### ⚠️ Critical Issues
1. **Duplicate Packages: `mi_auditor` vs `mi-auditor`**
   - Both directories contain identical core files
   - `mi_auditor/` has additional features (papers DB, knowledge base)
   - **Action Required:** Delete `mi-auditor/` and consolidate imports

2. **77 External Dependencies**
   - Heavy ML/AI stack (torch, triton, transformers)
   - Multiple UI frameworks (rich, textual)
   - **Risk:** Version conflicts, especially with GPU-dependent packages

### 📊 Unused Imports
- **48 files** have potentially unused imports
- Many are type hints that can be optimized with `from __future__ import annotations`
- **Notable:** `dharmic_security.py` imports `hmac` but doesn't use it

---

## Module Dependency Tree

```
clawd/
├── Core (8 files)
│   ├── dharmic_security.py ◄── unified_gates.py
│   ├── unified_gates.py
│   ├── agno_council_v2.py ◄── test_17_gates, test_consent
│   └── DHARMIC_GODEL_CLAW/
│       └── presence_pulse.py ◄── dgc_tui_demo, dgc_tui_v2
│
├── OACP (8 files) - Clean hierarchical structure
│   ├── core/
│   │   ├── attestation.py
│   │   ├── capability.py ◄── ALL other oacp modules
│   │   └── sandbox.py
│   ├── protocol/
│   │   ├── a2a_adapter.py
│   │   └── mcp_bridge.py
│   └── runtime/
│       └── executor.py
│
├── Skills (37 files)
│   ├── rv_toolkit/ ─────────────────┐
│   ├── mi-experimenter/ ◄───────────┼── Cross-skill dependencies
│   ├── mi_auditor/                  │
│   └── mi-auditor/ ⚠️ DUPLICATE ────┘
│
└── Scripts & Tests (27 files)
    ├── scripts/ (deployment, email, heartbeat)
    └── tests/ (distributed across packages)
```

---

## External Dependency Matrix

| Category | Packages | Risk |
|----------|----------|------|
| **ML/AI** | torch, triton, transformers, openai | 🔴 High |
| **Data** | numpy, pandas, scipy | 🟢 Low |
| **Web** | fastapi, httpx, requests | 🟡 Medium |
| **UI** | rich, textual | 🟡 Medium |
| **Test** | pytest | 🟢 Low |

---

## Architectural Issues Summary

| Issue | Severity | Files Affected |
|-------|----------|----------------|
| Duplicate mi_auditor packages | 🔴 Critical | 2 directories |
| Unused imports | 🟡 Medium | 48 files |
| Deep nesting (5+ levels) | 🟡 Medium | ~10 files |
| Type hint imports at runtime | 🟡 Medium | 20+ files |
| Inconsistent naming | 🟢 Low | Several packages |

---

## Recommended Actions

### Immediate Priority 🔴
```bash
# 1. Remove duplicate mi-auditor package
rm -rf skills/mi-auditor/

# 2. Verify no imports reference mi-auditor (with hyphen)
grep -r "from skills.mi-auditor" --include="*.py" .
grep -r "import skills.mi-auditor" --include="*.py" .
```

### Short Term 🟡
1. Add `from __future__ import annotations` to type-heavy modules
2. Clean confirmed unused imports (hmac, compute_pr references)
3. Document cross-skill dependencies (rv_toolkit ↔ mi-experimenter)

### Long Term 🟢
1. Establish dependency version pinning (requirements.txt / poetry.lock)
2. Add import linting to CI (pylint, flake8-unused-imports)
3. Create architecture documentation (ADRs)

---

## Files Generated

| File | Description |
|------|-------------|
| `import_graph_analysis.json` | Machine-readable dependency graph |
| `import_analysis_report.txt` | Full text report |
| `IMPORT_ANALYSIS_DETAILED.md` | Detailed analysis with recommendations |
| `IMPORT_SUMMARY.md` | This executive summary |

---

## Import Graph Statistics

```
Total Files:           80 Python files
Internal Modules:      49
External Packages:     77
Circular Dependencies: 0 ✅
Max Import Depth:      5 levels
Cross-Module Imports:  12
```

---

*Analysis completed: 2026-02-05*
