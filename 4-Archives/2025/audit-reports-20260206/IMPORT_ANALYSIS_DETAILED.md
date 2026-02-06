# Import Graph Analysis - Detailed Report

## Executive Summary

**Repository:** /Users/dhyana/clawd  
**Analysis Date:** 2026-02-05  
**Total Python Files:** 80 (3 files had syntax errors and were excluded)  
**Internal Modules:** 49  
**External Dependencies:** 77  

---

## 1. Internal Import Architecture

### 1.1 Module Structure Overview

The repository has a complex multi-package structure with several distinct subsystems:

```
clawd/
├── Core Systems
│   ├── dharmic_security.py          # Security framework
│   ├── unified_gates.py             # Gate management
│   ├── agno_council_v2.py           # Council framework
│   └── DHARMIC_GODEL_CLAW/          # Core presence system
│
├── OACP (Open Agent Capability Protocol)
│   ├── core/                        # Attestation, capability, sandbox
│   ├── protocol/                    # A2A adapter, MCP bridge
│   └── runtime/                     # Execution engine
│
├── Skills Ecosystem
│   ├── rv_toolkit/                  # RV (Reinforcement Verification) toolkit
│   ├── mi-experimenter/             # MI (Mechanistic Interpretability) experiments
│   ├── mi_auditor/                  # MI audit framework (duplicate!)
│   ├── mi-auditor/                  # MI audit framework (duplicate!)
│   ├── dharmic-swarm/               # Swarm coordination
│   └── cosmic-krishna-coder/        # Proactive risk detection
│
└── Scripts & Utilities
    ├── scripts/                     # Deployment, heartbeat, email
    └── tests/                       # Test suites
```

### 1.2 Internal Dependency Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DEPENDENCY HIERARCHY                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Level 4 (Application)                                             │
│   ├── dgc_tui_demo ──→ dgc_tui_v2                                  │
│   ├── dgc_backup_models_test ──→ dgc_backup_models                 │
│   └── test_* modules ──→ various systems                           │
│                                                                     │
│   Level 3 (Integration)                                             │
│   ├── mi-experimenter ──→ rv_toolkit, mi-experimenter.core         │
│   ├── mi_auditor ──→ mi_auditor.auditors                           │
│   └── mi-auditor ──→ mi-auditor.auditors (DUPLICATE!)              │
│                                                                     │
│   Level 2 (Protocol)                                                │
│   ├── oacp.protocol ──→ oacp.core                                  │
│   └── oacp.runtime ──→ oacp.core                                   │
│                                                                     │
│   Level 1 (Core)                                                    │
│   ├── oacp.core.sandbox ──→ oacp.core.{attestation,capability}     │
│   ├── dharmic_security                                             │
│   └── unified_gates ──→ dharmic_security                           │
│                                                                     │
│   Level 0 (Foundation)                                              │
│   └── DHARMIC_GODEL_CLAW.src.core.presence_pulse                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. External Dependencies

### 2.1 Core Python Standard Library (28 modules)
- `ast`, `asyncio`, `collections`, `concurrent.futures`
- `contextlib`, `dataclasses`, `datetime`, `email.*`
- `enum`, `functools`, `hashlib`, `hmac`, `imaplib`
- `importlib`, `inspect`, `itertools`, `json`, `logging`
- `math`, `os`, `pathlib`, `random`, `re`, `secrets`
- `sqlite3`, `smtplib`, `subprocess`, `sys`, `threading`
- `time`, `traceback`, `typing`, `unittest`, `unittest.mock`, `uuid`, `warnings`

### 2.2 Third-Party Dependencies (15 packages)

#### AI/ML Stack
- **torch** - PyTorch for deep learning
- **torch.nn** - Neural network modules
- **transformers** - Hugging Face transformers
- **triton** / **triton.language** - GPU kernel optimization
- **openai** - OpenAI API client

#### Data Science
- **numpy** - Numerical computing
- **pandas** - Data manipulation
- **scipy** - Scientific computing

#### Web/API Framework
- **fastapi** - Web framework
- **httpx** - HTTP client
- **requests** - HTTP requests

#### UI/CLI
- **rich** family (rich.console, rich.table, rich.text, etc.) - Terminal UI
- **textual** family (textual.app, textual.widgets, etc.) - TUI framework

#### Testing/Utilities
- **pytest** - Testing framework
- **psutil** - System monitoring
- **pyyaml** (yaml) - YAML parsing

### 2.3 External Dependency Risk Assessment

| Risk Level | Dependencies | Mitigation |
|------------|--------------|------------|
| **High** | triton, torch, transformers | GPU-dependent, version sensitive |
| **Medium** | textual, fastapi | Rapidly evolving APIs |
| **Low** | numpy, pandas, rich | Stable, well-maintained |

---

## 3. Circular Dependencies

### ✅ Status: NO CIRCULAR DEPENDENCIES DETECTED

The codebase has a clean dependency graph with no import cycles. This is excellent architectural hygiene.

---

## 4. Duplicate Module Issues

### 4.1 Critical Issue: mi_auditor vs mi-auditor

**Problem:** Two nearly identical packages exist:
- `/skills/mi_auditor/` (underscore)
- `/skills/mi-auditor/` (hyphen)

Both contain:
- `__init__.py`
- `auditors/__init__.py`
- `auditors/causal_validity.py`
- `auditors/cross_architecture.py`
- `auditors/literature_positioning.py`
- `auditors/statistical_rigor.py`
- `knowledge_base.py`
- `report_generator.py`

**Impact:** 
- Confusion about which module to import
- Potential for code divergence
- Import errors depending on Python path

**Recommendation:** Consolidate into a single package (prefer `mi_auditor` with underscore for PEP 8 compliance).

### 4.2 Other Duplicate Names

| Duplicate Name | Locations |
|----------------|-----------|
| tests | 3 locations (root, skills/mi_auditor/, skills/mi-auditor/) |
| knowledge_base | skills/mi_auditor/, skills/mi-auditor/ |
| report_generator | skills/mi_auditor/, skills/mi-auditor/ |
| core | skills/mi-experimenter/, oacp/ |
| auditors | skills/mi_auditor/, skills/mi-auditor/ |

**Impact:** Medium - May cause import confusion but scoped within packages.

---

## 5. Potentially Unused Imports

### 5.1 High Priority (Likely Unused)

| File | Import | Line |
|------|--------|------|
| `dharmic_security.py` | `hmac` | N/A |
| `skills/rv_toolkit/rv_hooks.py` | `compute_pr` | 39 |
| `skills/mi-experimenter/smoke_test.py` | `compute_pr` | 45 |
| `test_17_gates_critical.py` | `AgnoCouncilV2`, `DHARMIC_GATES` | 36 |

### 5.2 Type Hint Imports (May be False Positives)

Many typing imports (Union, Optional, Tuple, etc.) are flagged but may be used in:
- Type comments
- Forward references as strings
- IDE/static analysis

**Recommendation:** Use `from __future__ import annotations` to defer type evaluation.

### 5.3 Standard Library Imports

Common unused stdlib imports:
- `json` - Often imported for debugging but not used
- `sys` - Platform detection that was removed
- `math` - Mathematical constants/functions not used

---

## 6. Architectural Issues & Recommendations

### 6.1 High Severity

#### Issue 1: Duplicate mi_auditor Packages
**Severity:** 🔴 Critical  
**Recommendation:** 
1. Compare both packages for differences
2. Merge into `skills/mi_auditor/`
3. Remove `skills/mi-auditor/`
4. Update all imports

#### Issue 2: Inconsistent Naming Conventions
**Severity:** 🟡 Medium  
**Examples:**
- `dharmic_security` (underscore) vs `DHARMIC_GODEL_CLAW` (caps)
- `mi-experimenter` (hyphen) vs `mi_auditor` (underscore)

**Recommendation:** Adopt PEP 8 package naming (lowercase, underscores preferred over hyphens).

### 6.2 Medium Severity

#### Issue 3: Deep Module Nesting
**Examples:**
- `skills.mi-experimenter.experiments.cross_arch_suite`
- `DHARMIC_GODEL_CLAW.src.core.presence_pulse`

**Recommendation:** Flatten where possible. Consider:
- `mi_experimenter.cross_arch_suite`
- `dharmic_godel.presence_pulse`

#### Issue 4: Implicit Cross-Package Dependencies
**Observation:** `rv_toolkit` is imported by `mi-experimenter` - this is a skill-to-skill dependency that may indicate tight coupling.

**Recommendation:** Document cross-skill dependencies in a DEPENDENCIES.md file.

### 6.3 Low Severity

#### Issue 5: Unused Type Imports
**Recommendation:** Enable `from __future__ import annotations` to avoid runtime import of typing modules.

#### Issue 6: Mixed Import Styles
**Observation:** Mix of `import X` and `from X import Y` patterns.

**Recommendation:** Standardize on explicit imports: `from module import specific_name`.

---

## 7. Dependency Graph Visualization

### Key Connections

```
                    ┌──────────────────┐
                    │   dharmic_godel  │
                    │  (presence_pulse)│
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   unified    │ │   dharmic    │ │   dgc_tui    │
    │    gates     │ │   security   │ │     v2       │
    └──────────────┘ └──────────────┘ └──────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   agno_council   │
                    └──────────────────┘

    ┌──────────────┐         ┌──────────────┐
    │  mi_auditor  │◄───────►│ mi-auditor   │  ⚠️ DUPLICATE!
    │  (underscore)│         │  (hyphen)    │
    └──────┬───────┘         └──────────────┘
           │
           ▼
    ┌──────────────┐
    │   oacp       │
    │  (protocol)  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │  rv_toolkit  │
    └──────────────┘
```

---

## 8. Action Items

### Immediate (This Week)
1. [ ] Decide on single `mi_auditor` package location
2. [ ] Migrate all imports from `mi-auditor` to `mi_auditor`
3. [ ] Delete duplicate `mi-auditor/` directory
4. [ ] Run full test suite to verify

### Short Term (This Month)
1. [ ] Add `from __future__ import annotations` to all type-using modules
2. [ ] Clean up confirmed unused imports
3. [ ] Document cross-package dependencies
4. [ ] Create module naming convention guide

### Long Term (This Quarter)
1. [ ] Consider package consolidation (reduce nesting)
2. [ ] Implement import linting in CI/CD
3. [ ] Create architecture decision records (ADRs)
4. [ ] Establish dependency update policy

---

## 9. Appendix: Full File List

See `import_graph_analysis.json` for machine-readable dependency graph.

### Files by Category

| Category | Count | Files |
|----------|-------|-------|
| Core | 10 | dharmic_security, unified_gates, agno_council_v2, dgc_*, night_cycle, witness_threshold_detector, DHARMIC_GODEL_CLAW/* |
| OACP | 8 | oacp/**/* |
| Skills | 37 | skills/**/* |
| Scripts | 4 | scripts/* |
| Tests | 14 | test_*, tests/*, skills/**/tests/* |
| Utilities | 7 | dependency_mapper, generate_*, import_graph_analyzer |

---

*Report generated by import_graph_analyzer.py*
