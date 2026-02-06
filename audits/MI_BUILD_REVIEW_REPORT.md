# MI Build Review Report
## Status: **REJECTED - Critical Issues Found**

### Executive Summary
The mi-experimenter skill has foundational infrastructure but is missing the core `RVCausalValidator` class that is referenced in SKILL.md and required for causal validation experiments. Multiple critical issues prevent this from passing code review at Anthropic/DeepMind standards.

---

## 1. Import Test: **FAIL** ❌

### Required Import
```python
from mi_experimenter import RVCausalValidator
```

### Result
```
ImportError: cannot import name 'RVCausalValidator' from 'mi_experimenter'
```

### Root Cause
The `RVCausalValidator` class is **completely missing** from the codebase. It is referenced in SKILL.md but never implemented.

---

## 2. Module Naming: **FAIL** ❌

### Issue
Directory named `mi-experimenter` (with hyphen) but Python modules **cannot contain hyphens** in import names.

### Current State
```bash
skills/
  mi-experimenter/     # ❌ Cannot be imported as 'mi_experimenter'
```

### Required Fix
Rename directory to use underscore:
```bash
mv mi-experimenter mi_experimenter
```

### Workaround Detected
A symlink exists (`mi_experimenter -> mi-experimenter`) but this is brittle and non-standard.

---

## 3. RVCausalValidator Implementation: **MISSING** ❌

The SKILL.md specifies this interface:
```python
from experimenter import RVCausalValidator

validator = RVCausalValidator(
    model="mistralai/Mistral-7B-v0.1",
    target_layer=27,
    controls=["random", "shuffled", "wrong_layer", "orthogonal"],
    n_pairs=45
)
results = validator.run()
```

### Missing Components:
1. **RVCausalValidator class** - Not implemented
2. **4-control validation logic** - Not implemented
3. **Activation patching framework** - Partial (HookManager exists but no patching integration)
4. **Statistical analysis** - Not implemented (effect size, p-values)
5. **Determinism enforcement** - Not present

### Required Implementation Sketch:
```python
class RVCausalValidator:
    """
    Validates causal claims using 4-control activation patching.
    
    Controls:
    1. Random: Random activation vectors
    2. Shuffled: Permuted source activations  
    3. Wrong_layer: Activations from different layer
    4. Orthogonal: Projected orthogonal to source
    """
    
    def __init__(self, model_name, target_layer, controls, n_pairs):
        self.model_name = model_name
        self.target_layer = target_layer
        self.controls = controls
        self.n_pairs = n_pairs
        self._setup_determinism()
        self._log_hardware()
    
    def _setup_determinism(self):
        """CRITICAL: Enable deterministic algorithms."""
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(self.seed)
        random.seed(self.seed)
        np.random.seed(self.seed)
    
    def _log_hardware(self):
        """CRITICAL: Log hardware configuration for reproducibility."""
        import torch
        self.hardware_info = {
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "cuda_version": torch.version.cuda,
            "pytorch_version": torch.__version__,
            "deterministic": True
        }
    
    def run(self) -> dict:
        """Execute validation and return results with effect sizes."""
        # Implementation required
        pass
```

---

## 4. Math Verification: **PASS with Notes** ✅

### PR Formula in rv_core.py:52-62
```python
S = torch.linalg.svdvals(matrix)
S_squared = S ** 2
sum_S2 = S_squared.sum(dim=-1)
sum_S4 = (S_squared ** 2).sum(dim=-1)
pr = (sum_S2 ** 2) / (sum_S4 + eps)
```

### Verification
The formula `PR = (Σ S²)² / Σ S⁴` is **mathematically correct**.

**Note:** SKILL.md mentions a bug in the PR formula but the current implementation appears correct. The skill documentation may be outdated.

---

## 5. Determinism & Hardware Logging: **MISSING** ❌

### Required (from SKILL.md):
- [ ] `torch.use_deterministic_algorithms(True)`
- [ ] GPU model logged
- [ ] CUDA version logged
- [ ] PyTorch version logged
- [ ] Precision mode logged

### Current State
None of the above are implemented in any module.

---

## 6. 4 Controls Implementation: **MISSING** ❌

The 4 controls for causal validation are **not implemented**:

| Control | Description | Status |
|---------|-------------|--------|
| Random | Random activation vectors | ❌ Missing |
| Shuffled | Permuted source activations | ❌ Missing |
| Wrong_layer | Activations from different layer | ❌ Missing |
| Orthogonal | Projected orthogonal to source | ❌ Missing |

---

## 7. Error Handling: **PARTIAL** ⚠️

### Current State
- `model_loader.py`: Basic try/catch for flash attention fallback ✓
- `hook_manager.py`: Minimal error handling
- `rv_core.py`: Basic input validation

### Gaps
- No validation of control names in RVCausalValidator (class doesn't exist)
- No validation of layer indices against model depth
- No graceful handling of OOM errors
- No retry logic for transient failures

---

## 8. Test Coverage: **INCOMPLETE** ❌

### Current Tests (test_imports.py)
```
5 passed, 1 skipped
```

### What's Tested
- Package imports ✓
- Core module imports ✓
- R_V integration availability ✓
- Basic export validation ✓

### What's Missing
- ❌ RVCausalValidator instantiation
- ❌ RVCausalValidator.run() execution
- ❌ Control mechanism validation
- ❌ Effect size calculation
- ❌ Patching correctness
- ❌ Determinism verification
- ❌ Hardware logging validation

---

## 9. Architecture Assumptions: **HARD-CODED** ⚠️

### Issue in hook_manager.py
The hook patterns are hard-coded for specific architectures:
```python
HOOK_PATTERNS = {
    "gpt2": {...},
    "llama": {...},
    "mistral": {...},
}
```

### Risk
New architectures require code changes. Should use regex-based auto-detection or allow runtime pattern registration.

---

## 10. Documentation vs Implementation Gap

### SKILL.md Claims:
- ✅ `from experimenter import RVCausalValidator` - **MISSING**
- ✅ `CrossArchitectureSuite` - **MISSING**
- ✅ `MLPAblator` - **MISSING**
- ✅ 4-control validation - **MISSING**
- ✅ Code bugs fixed (PR formula) - **Cannot verify without validator**
- ✅ Determinism enabled - **MISSING**
- ✅ Hardware logged - **MISSING**

---

## Specific Fixes Required

### Critical (Must Fix)
1. **Rename directory**: `mi-experimenter` → `mi_experimenter`
2. **Implement RVCausalValidator class** with:
   - 4-control activation patching
   - Effect size calculation (Cohen's d)
   - P-value computation
   - Determinism enforcement
   - Hardware logging
3. **Add proper error handling** for edge cases

### High Priority
4. **Add comprehensive tests** for RVCausalValidator
5. **Add determinism utilities** module
6. **Add hardware logging** module

### Medium Priority
7. **Implement CrossArchitectureSuite** (if needed per SKILL.md)
8. **Implement MLPAblator** (if needed per SKILL.md)
9. **Add architecture auto-detection** to reduce hard-coding

---

## Review Criteria Checklist

| Criterion | Status | Notes |
|-----------|--------|-------|
| RVCausalValidator runs | ❌ FAIL | Class doesn't exist |
| Imports work | ⚠️ PARTIAL | Core works, validator missing |
| Determinism present | ❌ FAIL | Not implemented |
| Hardware logging | ❌ FAIL | Not implemented |
| 4 controls correct | ❌ FAIL | Not implemented |
| Error handling | ⚠️ PARTIAL | Basic only |
| Tests cover smoke scenarios | ❌ FAIL | No validator tests |
| Would pass Anthropic/DeepMind review | ❌ FAIL | Critical gaps |
| PR formula correct | ✅ PASS | Math is correct |
| No magic numbers | ⚠️ PARTIAL | Some hard-coded values |

---

## Recommendation

**DO NOT USE FOR PRODUCTION** until:
1. RVCausalValidator is fully implemented
2. All 4 controls are working
3. Determinism and hardware logging are in place
4. Comprehensive tests are added

**Estimated fix time**: 2-3 days for a senior ML engineer

---

## Code Review Score: **3/10**

- Infrastructure: 6/10 (HookManager, ModelLoader work)
- Core Algorithm: 0/10 (RVCausalValidator missing)
- Testing: 3/10 (basic import tests only)
- Documentation: 5/10 (SKILL.md over-promises)
- Production Readiness: 1/10 (cannot run specified experiments)

---

*Reviewer: MI_BUILD_REVIEWER*
*Date: 2026-02-04*
