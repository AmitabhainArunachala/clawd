# SKILL: Math Auditor — Rigorous Verification for Mech-Interp Research

**Purpose**: Expert-level mathematical verification of mechanistic interpretability research, specifically R_V metric and related consciousness geometry work.

**When to use**: Before any publication, when validating experimental results, when claims need mathematical proof, when statistical methods need auditing.

---

## Core Competencies

### 1. Linear Algebra Verification
- Matrix decomposition validity (SVD, eigendecomposition, QR)
- Tensor operations and broadcasting correctness
- Rank, nullspace, and dimensionality claims
- Cosine similarity and distance metric properties
- Projection and orthogonalization operations

### 2. Calculus & Optimization
- Gradient derivations and chain rule applications
- Hessian analysis for convexity/saddle points
- Optimization convergence proofs
- Jacobian computations for transformations
- Taylor series approximations and error bounds

### 3. Statistical Methodology
- Effect size calculations (Cohen's d, Hedge's g, r)
- Hypothesis testing validity (t-tests, ANOVA, permutation tests)
- Multiple comparison corrections (Bonferroni, FDR)
- Power analysis and sample size justification
- Confidence interval construction
- Bootstrap and resampling method validity

### 4. ML/Deep Learning Mathematics
- Attention mechanism mathematics (QKV, softmax properties)
- Residual stream algebra
- Layer normalization effects
- Activation function properties
- Loss landscape geometry

### 5. Mech-Interp Specific
- Activation patching causal validity
- Circuit analysis methodology
- Feature attribution methods (integrated gradients, etc.)
- Superposition and polysemanticity claims
- Induction head mechanics

---

## R_V Metric Audit Checklist

### Definition Verification
```python
# R_V = det(Cov(V_recursive)) / det(Cov(V_baseline))
# Where V = value vectors from specified layer
```

- [ ] Covariance matrix computation is correct (centered, unbiased)
- [ ] Determinant computation handles near-singular matrices
- [ ] Log-determinant used for numerical stability
- [ ] Ratio interpretation is mathematically sound
- [ ] R_V < 1 implies contraction (verify this claim geometrically)

### Statistical Claims
- [ ] Sample sizes adequate for effect size claims
- [ ] Independence assumptions valid between prompts
- [ ] Distribution assumptions for parametric tests
- [ ] Multiple model comparisons properly corrected
- [ ] Cross-validation or held-out testing used

### Causal Claims
- [ ] Correlation ≠ causation acknowledged
- [ ] Activation patching methodology sound
- [ ] Ablation studies properly controlled
- [ ] Confounds identified and addressed

---

## Verification Protocol

### Step 1: Reproduce Core Computations
```bash
cd ~/mech-interp-latent-lab-phase1
# Run R_V computation on known inputs
python -c "
from src.metrics.rv import compute_rv
import torch
# Test with synthetic data where answer is known
"
```

### Step 2: Mathematical Derivation Check
For each claim:
1. State the claim precisely
2. Write out the mathematical form
3. Verify each step of derivation
4. Check boundary conditions and edge cases
5. Confirm numerical implementation matches theory

### Step 3: Statistical Audit
For each statistical claim:
1. Verify test assumptions are met
2. Recalculate effect sizes from raw data
3. Check degrees of freedom
4. Verify p-value computation
5. Assess practical significance, not just statistical

### Step 4: Replication Check
- Different random seeds
- Different model architectures
- Different prompt formulations
- Different layer selections

---

## Key Files to Audit

| File | What to Check |
|------|---------------|
| `src/metrics/rv.py` | Core R_V computation |
| `src/analysis/statistical_tests.py` | Effect size, p-values |
| `prompts/bank.json` | Prompt categorization validity |
| `PHASE1_FINAL_REPORT.md` | Claims match code |
| `STATISTICAL_AUDIT_EXECUTIVE_SUMMARY.md` | Previous audit findings |
| `BRIDGE_HYPOTHESIS_INVESTIGATION.md` | Causal claim validity |

---

## Mathematical Foundations Reference

### Covariance Matrix Properties
- Symmetric positive semi-definite
- det(Σ) = product of eigenvalues
- det(Σ) = 0 iff rank-deficient
- Generalized variance interpretation

### Volume Interpretation
- det(Σ) proportional to volume of confidence ellipsoid
- R_V < 1 means recursive prompts produce SMALLER spread
- Geometric interpretation: value vectors "contract" toward something

### Effect Size Interpretation
| Cohen's d | Interpretation |
|-----------|----------------|
| 0.2 | Small |
| 0.5 | Medium |
| 0.8 | Large |
| > 1.0 | Very large |
| > 2.0 | Huge (verify data) |

Our claimed d = -5.57 for R_V is ENORMOUS — requires extreme scrutiny.

---

## CRITICAL: Sample Size Requirements for R_V

**R_V requires n >> d (samples >> dimensions) for stable estimation.**

| Dimensions (d) | Minimum n | Recommended n |
|----------------|-----------|---------------|
| 64 | 640 | 1000+ |
| 256 | 2560 | 5000+ |
| 768 | 7680 | 10000+ |
| 4096 | 40960 | 50000+ |

**Why:** Covariance matrix estimation requires sufficient samples for each dimension. With n ≈ d, sampling variance dominates and determinants become unreliable.

**Options if n is limited:**
1. **PCA reduction**: Project to top-k principal components before computing R_V
2. **Regularized covariance**: Use shrinkage estimator (Ledoit-Wolf)
3. **Subset dimensions**: Focus on specific attention heads or MLPs

**Verification discovered this:** With n=100, d=64, null hypothesis test FAILED (R_V ≈ 0.22 instead of 1.0). With n=1000, test PASSED (R_V ≈ 0.58).

---

## Red Flags to Watch For

1. **Too-good statistics**: d > 3 needs explanation
2. **Circular definitions**: Using L4 markers that contain target words
3. **Confirmation bias**: Only reporting supportive results
4. **Leaky preprocessing**: Test data influencing training
5. **P-hacking**: Multiple comparisons without correction
6. **Pseudoreplication**: Treating dependent samples as independent
7. **Survivorship bias**: Only analyzing successful runs

---

## Spawning This Agent

When deep mathematical verification is needed:

```
sessions_spawn with task:
"You are a mathematical verification specialist. Audit [specific file/claim].
Check: (1) mathematical derivations, (2) statistical validity, (3) code-theory match.
Report any errors, concerns, or validation confirmations with precise detail."
```

Model recommendation: Use Claude with extended thinking for complex derivations.

---

## Success Criteria

Before claiming "publication ready":
- [ ] All R_V computations verified by independent derivation
- [ ] Effect sizes recalculated from raw data
- [ ] Replication across 3+ architectures confirmed
- [ ] Causal claims supported by activation patching
- [ ] No statistical red flags remain
- [ ] Code matches mathematical definitions exactly
- [ ] Edge cases and failure modes documented

---

## The Standard

**We're not just checking for errors. We're ensuring this work can withstand Anthropic-level scrutiny.**

The zeitgeist is aligned. The window is open. But one rigorous paper beats three rushed ones.

*Rigor before reach.*

---

*Created: 2026-02-03*
*Purpose: AIKAGRYA publication preparation*
