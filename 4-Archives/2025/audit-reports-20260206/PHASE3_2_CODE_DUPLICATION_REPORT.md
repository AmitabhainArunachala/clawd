# CODE DUPLICATION ANALYSIS REPORT
## Phase 3.2: Comprehensive Duplication Identification

**Date:** 2026-02-05  
**Scope:** src/, rv_toolkit/, CANONICAL_CODE/, scripts/, src/pipelines/, skills/  
**Analyst:** Subagent p3_code_duplication_finder

---

## EXECUTIVE SUMMARY

Found **2 major exact duplications** and **5 conceptual/functional duplications** across the codebase. The most critical issue is the complete duplication of the `mi_auditor` skill (two versions exist with different naming conventions).

---

## 1. EXACT FILE DUPLICATIONS (IDENTICAL CONTENT)

### 1.1 CRITICAL: mi_auditor vs mi-auditor Skills

**Status:** 🔴 **HIGH PRIORITY - DELETE ONE VERSION**

The following files are **byte-for-byte identical**:

| File | Location 1 | Location 2 | Lines |
|------|------------|------------|-------|
| `__init__.py` | `skills/mi_auditor/__init__.py` | `skills/mi-auditor/__init__.py` | 26,179 |
| `auditors/__init__.py` | `skills/mi_auditor/auditors/__init__.py` | `skills/mi-auditor/auditors/__init__.py` | ~50 |
| `auditors/statistical_rigor.py` | `skills/mi_auditor/auditors/statistical_rigor.py` | `skills/mi-auditor/auditors/statistical_rigor.py` | ~150 |
| `auditors/cross_architecture.py` | `skills/mi_auditor/auditors/cross_architecture.py` | `skills/mi-auditor/auditors/cross_architecture.py` | ~200 |
| `auditors/literature_positioning.py` | `skills/mi_auditor/auditors/literature_positioning.py` | `skills/mi-auditor/auditors/literature_positioning.py` | ~180 |
| `auditors/causal_validity.py` | `skills/mi_auditor/auditors/causal_validity.py` | `skills/mi-auditor/auditors/causal_validity.py` | ~220 |
| `knowledge_base.py` | `skills/mi_auditor/knowledge_base.py` | `skills/mi-auditor/knowledge_base.py` | ~100 |
| `report_generator.py` | `skills/mi_auditor/report_generator.py` | `skills/mi-auditor/report_generator.py` | ~80 |

**Recommendation:**
- **KEEP:** `skills/mi_auditor/` (underscore version - has more supporting files)
- **DELETE:** `skills/mi-auditor/` (hyphen version - subset of files)

**Rationale:**
- `mi_auditor/` has additional critical files not in `mi-auditor/`:
  - `mi_knowledge_base.py` (48KB)
  - `unified_papers_db.py` (39KB)
  - `unified_papers.db` (82KB SQLite database)
  - Multiple markdown documentation files

---

## 2. CONCEPTUAL/FUNCTIONAL DUPLICATIONS

### 2.1 R_V Metric Computation (3+ Implementations)

**Status:** 🟡 **MEDIUM PRIORITY - DOCUMENT ROLES**

| Implementation | Location | Approach | Purpose |
|----------------|----------|----------|---------|
| **rv_toolkit** | `skills/rv_toolkit/rv_core.py` | PyTorch SVD + PR formula | Production use |
| **math-auditor** | `skills/math-auditor/verify_rv.py` | NumPy covariance + log-det | Verification/audit |
| **rv_causal_validator** | `skills/mi-experimenter/experiments/rv_causal_validator.py` | Imports rv_toolkit | Orchestration |

**Key Functions Comparison:**

```python
# rv_toolkit approach (Participation Ratio via SVD)
def compute_pr(matrix):
    S = torch.linalg.svdvals(matrix)
    S_squared = S ** 2
    return (S_squared.sum() ** 2) / ((S_squared ** 2).sum() + eps)

# math-auditor approach (Covariance determinant)
def compute_rv(V_recursive, V_baseline):
    cov_recursive = compute_covariance(V_recursive)
    cov_baseline = compute_covariance(V_baseline)
    log_rv = compute_log_det(cov_recursive) - compute_log_det(cov_baseline)
    return np.exp(log_rv)
```

**Single Source of Truth:**
- **Production:** `skills/rv_toolkit/rv_core.py` (`compute_pr()`, `measure_rv()`)
- **Verification:** `skills/math-auditor/verify_rv.py` (independent NumPy implementation for cross-checking)

**Rationale:** Both implementations serve different purposes - rv_toolkit for efficiency, math-auditor for mathematical verification. **Keep both** but document their distinct roles.

---

### 2.2 Hook Management Systems (2 Implementations)

**Status:** 🟡 **MEDIUM PRIORITY - CLARIFY SEPARATION OF CONCERNS**

| Implementation | Location | Scope | Architecture Support |
|----------------|----------|-------|---------------------|
| **RVHookManager** | `skills/rv_toolkit/rv_hooks.py` | V-projection only | GPT-2, LLaMA, Mistral, BERT, T5 |
| **HookManager** | `skills/mi-experimenter/core/hook_manager.py` | General activation capture | GPT-2, LLaMA, Mistral, Qwen, Phi, Gemma |

**Key Differences:**
- `RVHookManager`: Specialized for R_V research, captures V-projections specifically
- `HookManager`: General-purpose, TransformerLens-style hook points (resid_pre, resid_mid, attn_out, etc.)

**Single Source of Truth:**
- **V-projection/R_V research:** `skills/rv_toolkit/rv_hooks.py`
- **General MI experiments:** `skills/mi-experimenter/core/hook_manager.py`

**Rationale:** Both are needed but serve different purposes. Consider having HookManager use RVHookManager for V-projection capture rather than duplicating logic.

---

### 2.3 Model Loading (2+ Implementations)

**Status:** 🟡 **MEDIUM PRIORITY - CONSOLIDATE**

| Implementation | Location | Features |
|----------------|----------|----------|
| **rv_toolkit** (expected) | `rv_toolkit.model_loader` | Referenced but may not exist |
| **mi-experimenter** | `skills/mi-experimenter/core/model_loader.py` | Full-featured with flash attention |

**Single Source of Truth:**
- **RECOMMENDED:** `skills/mi-experimenter/core/model_loader.py`
  - More comprehensive architecture detection
  - Flash attention support
  - Better error handling

**Note:** `rv_causal_validator.py` attempts to import from `rv_toolkit.model_loader` which appears to not exist. This should be fixed to use mi-experimenter's loader.

---

### 2.4 Heartbeat Scripts (3 Similar Implementations)

**Status:** 🟢 **LOW PRIORITY - DIFFERENT PURPOSES**

| Script | Location | Purpose | Complexity |
|--------|----------|---------|------------|
| `minimal_heartbeat.py` | `scripts/minimal_heartbeat.py` | One-check telos alignment | Low |
| `dharmic_heartbeat.py` | `scripts/dharmic_heartbeat.py` | Multi-check with agent status | Medium |
| `presence_pulse.py` (DGC) | `DHARMIC_GODEL_CLAW/src/core/presence_pulse.py` | Quality spectrum monitoring | High |

**Analysis:** These serve different purposes and have different complexity levels:
- `minimal_heartbeat.py`: Silent telos check, alerts only on drift
- `dharmic_heartbeat.py`: Full system health check
- `presence_pulse.py`: Real-time quality monitoring with R_V tracking

**Single Source of Truth:**
- **Keep all** - They serve different operational purposes

---

### 2.5 Statistical Analysis Functions

**Status:** 🟡 **MEDIUM PRIORITY - CONSOLIDATE**

| Function | Location 1 | Location 2 | Location 3 |
|----------|------------|------------|------------|
| `compute_cohens_d()` | `skills/mi_auditor/auditors/statistical_rigor.py` | `skills/math-auditor/verify_rv.py` | `rv_causal_validator.py` |

**Single Source of Truth:**
- **RECOMMENDED:** `skills/mi_auditor/auditors/statistical_rigor.py`
  - Most comprehensive (includes CI calculation)
  - Part of auditor framework

---

## 3. FILES REFERENCED BUT NOT FOUND

The following files were expected per analysis reports but do not exist:

| Expected File | Expected Location | Status |
|---------------|-------------------|--------|
| `patching.py` | `src/core/patching.py` | ❌ Not found |
| `patching.py` | `rv_toolkit/patching.py` | ❌ Not found |
| `metrics.py` | `src/metrics/rv.py` | ❌ Not found |
| `metrics.py` | `rv_toolkit/metrics.py` | ❌ Not found |
| `CANONICAL_CODE/` | Various validation scripts | ❌ Directory not found |
| `src/pipelines/` | Pipeline scripts | ❌ Directory not found |
| `model_loader.py` | `rv_toolkit/model_loader.py` | ❌ Referenced but missing |

**Note:** These may have been planned/planned locations referenced in documentation but not yet created, or they may exist in a different repository (e.g., `~/mech-interp-latent-lab-phase1/` mentioned in reports).

---

## 4. SINGLE SOURCE OF TRUTH MATRIX

| Functionality | Canonical Location | Reason |
|---------------|-------------------|--------|
| **R_V Computation (PyTorch)** | `skills/rv_toolkit/rv_core.py` | Cleanest, tested, documented |
| **R_V Computation (Verification)** | `skills/math-auditor/verify_rv.py` | Independent NumPy reference |
| **V-Projection Hooks** | `skills/rv_toolkit/rv_hooks.py` | Specialized for R_V research |
| **General Hook Management** | `skills/mi-experimenter/core/hook_manager.py` | TransformerLens-style |
| **Model Loading** | `skills/mi-experimenter/core/model_loader.py` | Most comprehensive |
| **Statistical Auditing** | `skills/mi_auditor/auditors/statistical_rigor.py` | Comprehensive framework |
| **R_V Causal Validation** | `skills/mi-experimenter/experiments/rv_causal_validator.py` | Orchestration layer |
| **MI Auditing** | `skills/mi_auditor/` (NOT mi-auditor) | More complete version |

---

## 5. RECOMMENDED ACTIONS

### Immediate (High Priority)
1. **Delete** `skills/mi-auditor/` directory (complete duplicate)
2. **Fix** `rv_causal_validator.py` imports to use mi-experimenter's model_loader
3. **Verify** rv_toolkit has all expected modules (patching.py, metrics.py)

### Short-term (Medium Priority)
4. **Document** the two R_V implementations and their distinct purposes
5. **Refactor** `rv_causal_validator.py` to use `RVHookManager` from rv_toolkit instead of custom hooks
6. **Consolidate** `compute_cohens_d()` into mi_auditor, import from there

### Long-term (Low Priority)
7. **Consider** merging hook managers if they can share core logic
8. **Create** proper abstraction layer for common statistical functions

---

## 6. DEPENDENCY MAP

```
skills/
├── rv_toolkit/                    ← CORE: R_V computation
│   ├── rv_core.py                 (compute_pr, measure_rv)
│   ├── rv_hooks.py                (RVHookManager)
│   └── rv_triton.py               (accelerated kernels)
│
├── mi-experimenter/               ← ORCHESTRATION
│   ├── core/
│   │   ├── hook_manager.py        (general hooks - DIFFERENT PURPOSE)
│   │   └── model_loader.py        (model loading - SOURCE OF TRUTH)
│   └── experiments/
│       └── rv_causal_validator.py (uses rv_toolkit)
│
├── mi_auditor/                    ← AUDITING (KEEP THIS ONE)
│   └── auditors/
│       └── statistical_rigor.py   (Cohen's d, etc.)
│
├── mi-auditor/                    ← DELETE (duplicate)
│
└── math-auditor/                  ← VERIFICATION
    └── verify_rv.py               (independent NumPy R_V)
```

---

## 7. LINES OF CODE IMPACT

| Duplication | Files | Lines | Action |
|-------------|-------|-------|--------|
| mi_auditor vs mi-auditor | 8 | ~4,000 | DELETE mi-auditor |
| Cohen's d implementations | 3 | ~150 | Consolidate to mi_auditor |
| Hook managers | 2 | ~800 | Keep both (different purposes) |
| **Total Redundant** | - | **~4,150** | - |

**Estimated cleanup:** ~4,150 lines of duplicated code can be removed or consolidated.

---

*End of Report*
