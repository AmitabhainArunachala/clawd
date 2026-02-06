# RV Toolkit Test Coverage Mapping

**Generated:** 2026-02-05  
**Scope:** `/Users/dhyana/clawd/skills/rv_toolkit/`

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Python Files | 4 |
| Total Lines of Code | ~850 |
| Test Files | **0** |
| Test Coverage | **0%** |
| Criticality | HIGH - Mathematical correctness essential |

**Status:** 🔴 **NO TESTS EXIST** - Complete testing gap

---

## 1. Source Code Inventory

### 1.1 File Structure
```
skills/rv_toolkit/
├── __init__.py          # 75 lines - Public API exports
├── rv_core.py           # 280 lines - Core PR computation
├── rv_hooks.py          # 425 lines - Model hooking system
├── rv_triton.py         # 310 lines - Triton acceleration
└── SKILL.md             # Documentation
```

### 1.2 Module Breakdown

#### `rv_core.py` - Core PyTorch Implementation
| Function | Lines | Complexity | Test Status |
|----------|-------|------------|-------------|
| `compute_pr()` | 45-85 | Medium (SVD, tensor ops) | ❌ NO TESTS |
| `measure_rv()` | 88-165 | High (multi-dim, per-head) | ❌ NO TESTS |
| `compute_rv_spectrum()` | 168-215 | Medium (SVD + stats) | ❌ NO TESTS |
| Convenience aliases (`pr`, `rv`) | 218 | Low | ❌ NO TESTS |

**Key Logic to Test:**
- Participation Ratio formula: `PR = (Σ S²)² / Σ S⁴`
- Batched input handling (2D, 3D, 4D tensors)
- Numerical stability (`eps` handling)
- Per-head attention analysis
- Singular value spectrum statistics

#### `rv_hooks.py` - Model Hooking System
| Class/Function | Lines | Complexity | Test Status |
|----------------|-------|------------|-------------|
| `ActivationCapture` dataclass | 20-35 | Low | ❌ NO TESTS |
| `RVHookManager` class | 38-380 | HIGH | ❌ NO TESTS |
| `find_v_projections()` | 335-350 | Low | ❌ NO TESTS |
| `quick_rv_measure()` | 353-380 | Medium | ❌ NO TESTS |
| `GPT2RVHooks` | 386-390 | Low | ❌ NO TESTS |
| `LLaMAHooks` | 393-397 | Low | ❌ NO TESTS |
| `BERTRVHooks` | 400-404 | Low | ❌ NO TESTS |

**Key Logic to Test:**
- V-projection layer auto-detection (regex patterns)
- Hook attachment/detachment lifecycle
- Context manager (`capture()`) behavior
- Architecture-specific patterns (GPT-2, LLaMA, BERT, T5)
- QKV splitting for GPT-2 style models

#### `rv_triton.py` - Triton Acceleration
| Function | Lines | Complexity | Test Status |
|----------|-------|------------|-------------|
| `_pr_from_sv_kernel` (Triton) | 38-75 | HIGH | ❌ NO TESTS |
| `_pr_stats_kernel` (Triton) | 78-125 | HIGH | ❌ NO TESTS |
| `compute_pr_triton()` | 128-170 | Medium | ❌ NO TESTS |
| `compute_pr_stats_triton()` | 173-220 | Medium | ❌ NO TESTS |
| `measure_rv_triton()` | 223-260 | Medium | ❌ NO TESTS |
| `is_triton_available()` | 263-265 | Low | ❌ NO TESTS |
| `get_backend_info()` | 268-285 | Low | ❌ NO TESTS |

**Key Logic to Test:**
- Triton kernel correctness vs PyTorch reference
- Graceful fallback when Triton unavailable
- GPU/CPU handling
- Batch processing in kernels

#### `__init__.py` - Public API
| Item | Lines | Test Status |
|------|-------|-------------|
| Core imports | 15-25 | ❌ NO TESTS |
| Triton imports | 27-36 | ❌ NO TESTS |
| Hooks imports | 38-47 | ❌ NO TESTS |
| `__all__` exports | 49-66 | ❌ NO TESTS |

---

## 2. Test Gap Analysis

### 2.1 Critical Gaps (High Priority)

#### 🔴 Mathematical Correctness
**Risk:** Incorrect PR calculations would invalidate research
```python
# MUST TEST:
- Identity matrix → PR ≈ dimension
- Rank-1 matrix → PR ≈ 1
- Random Gaussian → PR ≈ min(M,N)
- Zero matrix → PR = 0 (or eps handling)
- Known analytical cases
```

#### 🔴 Numerical Stability
**Risk:** Division by zero, NaN propagation
```python
# MUST TEST:
- All-zero inputs
- Very small singular values
- Very large singular values
- Mixed scale inputs
- Gradient flow (if applicable)
```

#### 🔴 Shape Handling
**Risk:** Silent failures on unexpected input shapes
```python
# MUST TEST:
- 2D matrices: (M, N)
- 3D batched: (batch, M, N)
- 4D attention: (batch, heads, seq, dim)
- Edge cases: (1, 1), (0, N), empty tensors
```

### 2.2 Integration Gaps (Medium Priority)

#### 🟡 Model Hook Integration
```python
# MUST TEST:
- Hook attaches to correct layers
- Hook detaches cleanly (no memory leaks)
- Multiple forward passes
- Multi-layer models
- Missing layer patterns
```

#### 🟡 Architecture Support
```python
# SHOULD TEST:
- GPT-2 style (c_attn QKV combined)
- LLaMA/Mistral (separate v_proj)
- BERT (attention.self.value)
- T5 (SelfAttention.v)
- Custom patterns
```

### 2.3 Performance/Compatibility Gaps (Lower Priority)

#### 🟢 Triton Acceleration
```python
# SHOULD TEST:
- Triton vs PyTorch numerical equivalence
- Fallback when Triton unavailable
- GPU memory efficiency
- Kernel launch overhead
```

---

## 3. Recommended Test Suite

### 3.1 Unit Tests (`test_rv_core.py`)

```python
# Test Categories:

1. test_compute_pr_basic()
   - Known matrices with analytical solutions
   - Verify PR formula correctness

2. test_compute_pr_shapes()
   - 2D, 3D, 4D, 5D+ tensors
   - Batched computation consistency

3. test_compute_pr_numerical_stability()
   - Zero matrices
   - Near-zero singular values
   - Very large/small values

4. test_measure_rv_modes()
   - reduce="mean", "median", "none"
   - per_head=True/False
   - num_heads inference

5. test_compute_rv_spectrum()
   - Singular value ordering
   - Stats dictionary completeness
   - Entropy calculation
```

### 3.2 Hook Tests (`test_rv_hooks.py`)

```python
# Test Categories:

1. test_hook_manager_init()
   - Auto-detection of layers
   - Custom pattern matching
   - Empty model handling

2. test_hook_lifecycle()
   - attach() adds hooks
   - detach() removes hooks
   - clear() resets captures

3. test_capture_context_manager()
   - Proper setup/teardown
   - Exception handling
   - clear_before/clear_after options

4. test_architecture_patterns()
   - Mock GPT-2 model
   - Mock LLaMA model
   - Mock BERT model
   - Pattern matching accuracy

5. test_compute_rv_from_captures()
   - Correct aggregation
   - Per-head breakdown
   - Empty capture handling
```

### 3.3 Triton Tests (`test_rv_triton.py`)

```python
# Test Categories:

1. test_triton_availability()
   - is_triton_available() correctness
   - get_backend_info() structure

2. test_triton_correctness()
   - Same results as PyTorch
   - Various input sizes
   - Numerical precision

3. test_triton_fallback()
   - CPU tensors → PyTorch fallback
   - Small tensors → PyTorch (not worth Triton)
   - Missing Triton → graceful fallback
```

### 3.4 Integration Tests (`test_rv_integration.py`)

```python
# Test Categories:

1. test_end_to_end_simple_model()
   - Create minimal transformer
   - Run full pipeline
   - Verify output structure

2. test_real_model_gpt2()
   - Load tiny GPT-2
   - Measure R_V
   - Check results reasonable

3. test_api_exports()
   - All __all__ items importable
   - No circular imports
   - Backward compatibility
```

---

## 4. Testing Infrastructure Needed

### 4.1 Test Dependencies
```toml
[tool.pytest.ini_options]
testpaths = ["skills/rv_toolkit/tests"]
python_files = ["test_*.py"]

[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-xdist>=3.0",  # Parallel execution
    "hypothesis>=6.0",     # Property-based testing
    "torch>=2.0",
]
```

### 4.2 Test Directory Structure
```
skills/rv_toolkit/
└── tests/
    ├── __init__.py
    ├── conftest.py           # Shared fixtures
    ├── test_rv_core.py       # ~30 tests
    ├── test_rv_hooks.py      # ~25 tests
    ├── test_rv_triton.py     # ~15 tests
    ├── test_integration.py   # ~10 tests
    └── fixtures/
        ├── mock_models.py    # Dummy transformers
        └── known_matrices.py # Analytical test cases
```

### 4.3 CI/CD Integration
```yaml
# .github/workflows/test-rv-toolkit.yml
name: Test RV Toolkit
on:
  push:
    paths: ['skills/rv_toolkit/**']
  pull_request:
    paths: ['skills/rv_toolkit/**']

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ['3.9', '3.10', '3.11']
        torch: ['2.0', '2.1', '2.2']
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest skills/rv_toolkit/tests/ --cov=rv_toolkit
```

---

## 5. Risk Assessment

| Component | Risk Level | Impact if Broken | Test Priority |
|-----------|------------|------------------|---------------|
| `compute_pr()` | 🔴 CRITICAL | Invalid research results | P0 |
| `measure_rv()` | 🔴 CRITICAL | Wrong analysis conclusions | P0 |
| `RVHookManager` | 🟡 HIGH | Failed model integration | P1 |
| `rv_triton` | 🟡 MEDIUM | Performance degradation | P2 |
| Architecture hooks | 🟢 LOW | Limited model support | P3 |

---

## 6. Testing Recommendations

### Immediate Actions (This Week)
1. ✅ Create `skills/rv_toolkit/tests/` directory
2. ✅ Write `test_rv_core.py` with 10 basic correctness tests
3. ✅ Add CI workflow for automated testing

### Short Term (Next 2 Weeks)
1. 📝 Achieve 80% coverage on `rv_core.py`
2. 📝 Write hook lifecycle tests
3. 📝 Add numerical stability tests

### Medium Term (Next Month)
1. 📝 Achieve 90% overall coverage
2. 📝 Add integration tests with real models
3. 📝 Property-based testing with Hypothesis
4. 📝 Performance regression tests

### Long Term (Ongoing)
1. 📝 Mutation testing
2. 📝 Fuzz testing for robustness
3. 📝 Benchmark suite for performance

---

## 7. Summary

**Current State:**  
🔴 **ZERO TEST COVERAGE** - rv_toolkit has no automated tests

**Critical Gaps:**
- Mathematical correctness unverified
- No numerical stability validation
- Hook system untested
- Architecture support unchecked

**Next Steps:**
1. Create test directory structure
2. Implement core correctness tests (highest priority)
3. Add CI/CD pipeline
4. Gradually expand coverage

**Estimated Effort:** 2-3 days for basic coverage, 1 week for comprehensive testing

---

*Document generated by Phase 3.6: Test → Code Coverage Mapping*
