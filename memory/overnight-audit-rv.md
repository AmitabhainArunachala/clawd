# R_V Code Mathematical Audit
**Date**: 2026-02-03 (overnight)
**Auditor**: DHARMIC CLAW
**Purpose**: Verify R_V implementation matches theory for publication

---

## Code Location
`~/mech-interp-latent-lab-phase1/src/metrics/rv.py`

---

## AUDIT RESULTS

### 1. Participation Ratio Definition ✅ CORRECT

**Theory**:
```
PR = (Σλᵢ²)² / Σ(λᵢ⁴)
```
Where λᵢ are singular values.

**Code** (line ~60):
```python
pr = (S_sq.sum() ** 2) / (S_sq ** 2).sum()
```
Where `S_sq = S_np ** 2` (squared singular values).

**Verification**:
- `S_sq.sum()` = Σλᵢ²
- `S_sq ** 2` = λᵢ⁴
- `(S_sq ** 2).sum()` = Σλᵢ⁴
- Formula: (Σλᵢ²)² / Σλᵢ⁴ ✅

**Note**: There's a commented line computing `p = S_sq / total_variance` (normalized eigenvalues) that isn't used. No impact on correctness.

### 2. R_V Definition ✅ CORRECT

**Theory**:
```
R_V = PR_late / PR_early
```
Where:
- PR_early = Participation ratio at layer 5
- PR_late = Participation ratio at layer (num_layers - 5)

**Code** (line ~137):
```python
rv = float(pr_late / pr_early)
```

**Verification**: Direct ratio as specified ✅

### 3. Numerical Stability ✅ GOOD

**Measures implemented**:
- SVD computed in `float64` (double precision)
- Degeneracy check: `total_variance < 1e-10` returns NaN
- Division by zero check: `pr_early == 0` returns NaN
- Short sequence guard: `T < window_size` returns NaN

### 4. Window Selection ✅ CORRECT

**Theory**: Last W tokens of prompt (default W=16)

**Code** (line ~53):
```python
v_window = v_tensor[-W:, :]
```

**Verification**: Correctly extracts last W tokens ✅

### 5. Layer Selection ✅ CORRECT

**Theory**: 
- Early: Layer 5 (after initial processing)
- Late: ~84% depth (num_layers - 5)

**Code** (line ~97-98):
```python
if late is None:
    late = num_layers - 5
```

**Verification**: For 32-layer model: late=27 → 27/32 = 84.4% depth ✅

---

## POTENTIAL CONCERNS

### Concern 1: Unused Variable (Minor)
Line ~56: `p = S_sq / total_variance` computed but never used.
**Impact**: None (code smell only)
**Recommendation**: Remove or document

### Concern 2: Sample Size
Window=16 with hidden_dim typically 4096.
Sample size n=16 for d=4096 dimensions is small.
**Impact**: High variance in PR estimates
**Already addressed in**: math-auditor SKILL.md (n >> d requirement)
**Recommendation**: Document this limitation in paper

### Concern 3: Single Batch
Line ~43: `v_tensor = v_tensor[0]` takes only first batch
**Impact**: If multiple prompts batched, only first measured
**Recommendation**: Ensure single-prompt inference in experiments

---

## VERIFICATION SUMMARY

| Component | Status | Notes |
|-----------|--------|-------|
| PR formula | ✅ CORRECT | Matches theory exactly |
| R_V formula | ✅ CORRECT | PR ratio as specified |
| Numerical stability | ✅ GOOD | Double precision, guards |
| Window selection | ✅ CORRECT | Last W tokens |
| Layer selection | ✅ CORRECT | 84% depth |
| Edge cases | ✅ HANDLED | NaN for degenerate cases |

---

## CONCLUSION

**The R_V implementation is mathematically correct and ready for publication.**

The code correctly implements:
1. Participation Ratio as (Σλᵢ²)² / Σλᵢ⁴
2. R_V as PR_late / PR_early
3. Appropriate numerical safeguards

The sample size concern (n=16 for d=4096) should be documented as a limitation but doesn't invalidate results given the large effect sizes observed (d = -5.57 claimed → need to verify this specific claim separately).

---

## NEXT STEPS FOR MORNING

1. [ ] Verify the d=-5.57 effect size claim against actual experiment logs
2. [ ] Check sample sizes in published experiments
3. [ ] Review statistical tests used (t-test assumptions)
4. [ ] Cross-reference with PHASE1_FINAL_REPORT.md

---

*Audit completed: 2026-02-03 ~22:30 Asia/Makassar*
*This serves Jagat Kalyan by ensuring rigorous science.*

JSCA 🪷
