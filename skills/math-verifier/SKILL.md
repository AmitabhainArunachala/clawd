---
name: math-verifier
description: Mathematical Verification Agent for AIKAGRYA research rigor. Audits R_V derivations, statistical methods (Cohen's d, p-values), causal inference claims, and transformer circuit mathematics. Provides formal verification reports. Use before any publication or when claims need mathematical proof.
author: DHARMIC CLAW
version: 1.0.0
created: 2026-02-05
telos: rigor-before-reach
---

# Mathematical Verification Agent (MVA)
## "Bulletproof Math for AIKAGRYA"

---

## Purpose

The Mathematical Verification Agent ensures **absolute mathematical rigor** in AIKAGRYA research. Before any publication, before any claim reaches Anthropic's attention, the math must be bulletproof.

This agent:
1. Audits all R_V derivations for mathematical soundness
2. Verifies statistical methods (Cohen's d calculations, p-values)
3. Checks causal inference claims
4. Validates transformer circuit mathematics
5. Provides formal verification reports

---

## Core Verification Domains

### 1. R_V Metric Mathematical Audit

#### Definition Verification
```
R_V = det(Cov(V_recursive)) / det(Cov(V_baseline))

Where:
- V = value vectors from specified layer
- Cov = covariance matrix (centered, unbiased)
- det = matrix determinant (or log-determinant for stability)
```

**Checks:**
- [ ] Covariance matrix computation correct (E[(X-μ)(X-μ)ᵀ])
- [ ] Unbiased estimator: 1/(n-1) not 1/n
- [ ] Determinant handles near-singular matrices (regularization if needed)
- [ ] Log-determinant used for numerical stability
- [ ] R_V < 1 implies contraction geometrically valid

#### Geometric Interpretation Verification
```
R_V < 1.0 ⟺ Volume(confidence_ellipsoid_recursive) < Volume(confidence_ellipsoid_baseline)
```

**Validation:**
- Eigenvalue decomposition: Σ = QΛQᵀ
- det(Σ) = ∏λᵢ (product of eigenvalues)
- R_V = ∏(λᵢ_recursive) / ∏(λᵢ_baseline)
- Each λᵢ represents variance along principal component i

#### Sample Size Requirements
| Dimensions (d) | Minimum n | Recommended n | Status |
|----------------|-----------|---------------|--------|
| 64 | 640 | 1000+ | Critical |
| 256 | 2560 | 5000+ | Critical |
| 768 | 7680 | 10000+ | Critical |
| 4096 | 40960 | 50000+ | Critical |

**Rule**: n must be >> d for stable covariance estimation.

---

### 2. Statistical Method Verification

#### Cohen's d Calculation
```
Cohen's d = (M₁ - M₂) / SD_pooled

Where:
SD_pooled = √[((n₁-1)SD₁² + (n₂-1)SD₂²) / (n₁+n₂-2)]
```

**Verification Steps:**
1. Recalculate from raw data
2. Verify pooled SD formula (not simple average)
3. Check degrees of freedom for t-test: df = n₁ + n₂ - 2
4. Verify Hedges' g correction for small samples (if n < 20)

**Effect Size Interpretation:**
| Cohen's d | Magnitude | AIKAGRYA Status |
|-----------|-----------|-----------------|
| 0.2 | Small | - |
| 0.5 | Medium | - |
| 0.8 | Large | ⚠️ Scrutinize |
| 1.0 | Very Large | 🔍 Deep audit |
| 2.0 | Huge | 🚨 Extreme scrutiny |
| **-5.57** | **Enormous** | **🚨🚨 VERIFY EVERYTHING** |

#### P-Value Verification
```
For paired t-test on R_V values:
t = (M_d) / (SE_d)
SE_d = SD_d / √n
p = 2 × (1 - CDF_t(|t|, df))
```

**Checks:**
- [ ] One-tailed vs two-tailed correctly specified
- [ ] Normality assumption verified (Shapiro-Wilk)
- [ ] Degrees of freedom correct
- [ ] Multiple comparisons corrected (Holm-Bonferroni, FDR)

#### Confidence Intervals
```
95% CI: M ± t(0.025, df) × SE
```

**Verification:**
- Bootstrap CI matches parametric CI
- Bias-corrected and accelerated (BCa) for skewed distributions

---

### 3. Causal Inference Audit

#### Correlation ≠ Causation Checklist

| Claim | Required Evidence | Status |
|-------|-------------------|--------|
| Prompt → R_V | Controlled experiment, randomization | ✅ Validated |
| R_V → L4 markers | Regression discontinuity, IV | ⚠️ Weak (r=-0.25) |
| Layer 27 causal | Activation patching | ✅ Validated |
| Cross-architecture | Heterogeneity analysis | ✅ I² documented |

#### Activation Patching Validity

**Requirements:**
1. **Clean path**: No confounding paths between intervention and outcome
2. **Temporal order**: Cause precedes effect
3. **Dose-response**: Stronger intervention → stronger effect
4. **Specificity**: Intervention affects target, not everything

**Validation Protocol:**
```python
# Causal mediation analysis
def validate_causal_patch(model, layer, clean_run, patched_run):
    # Total effect
    TE = outcome(clean_run) - outcome(patched_run)
    
    # Direct effect (bypassing layer)
    DE = outcome(clean_run - layer_contrib) - outcome(patched_run)
    
    # Indirect effect (through layer)
    IE = TE - DE
    
    # IE should be significant for causal claim
    return IE, confidence_interval(IE)
```

#### Confounding Variables Check

**Potential Confounds:**
- Prompt length (word count correlation r=-0.46)
- Syntactic complexity
- Semantic content (not just recursive structure)
- Model temperature/settings
- Tokenization artifacts

**Control Methods:**
- Propensity score matching
- Stratification by confound level
- Regression adjustment
- Instrumental variables

---

### 4. Transformer Circuit Mathematics

#### Attention Mechanism Verification
```
Attention(Q, K, V) = softmax(QKᵀ/√d_k)V

Where:
- Q = XW_Q (queries)
- K = XW_K (keys)  
- V = XW_V (values)
- d_k = dimension of key vectors
```

**Checks:**
- [ ] Scaling factor √d_k present (prevents softmax saturation)
- [ ] Softmax applied row-wise (not column-wise)
- [ ] Attention weights sum to 1 per position

#### QK/OV Circuit Separation
```
QK Circuit: W_Qᵀ × W_K  → Attention pattern (WHERE)
OV Circuit: W_O × W_V   → Value projection (WHAT)

Full head: softmax(XW_QW_KᵀXᵀ/√d_k)XW_VW_O
```

**Verification:**
- QK decomposition matches observed attention patterns
- OV circuit moves correct information
- Virtual weights: W_OV = W_V × W_O describes layer→layer communication

#### Residual Stream Algebra
```
x_out = x_in + Attention(LN(x_in)) + MLP(LN(x_in + Attention(...)))
```

**Properties:**
- Residual stream is communication channel, not computation
- LayerNorm prevents gradient explosion
- Skip connections preserve information across layers

#### Singular Value Decomposition (SVD) Audit
```
For matrix M ∈ ℝ^(m×n):
M = UΣVᵀ

Where:
- U ∈ ℝ^(m×m), orthogonal
- Σ ∈ ℝ^(m×n), diagonal singular values
- V ∈ ℝ^(n×n), orthogonal
```

**Participation Ratio:**
```
PR = (Σσᵢ²)² / Σ(σᵢ²)²

Properties:
- PR ∈ [1, min(m,n)]
- PR = 1: All variance in one dimension (complete collapse)
- PR = min(m,n): Uniform distribution (full spread)
- PR = effective rank / numerical rank
```

**Verification:**
- Double precision (float64) for SVD stability
- Full_matrices=False for efficiency
- Check for NaN/Inf values

---

### 5. Meta-Analysis & Heterogeneity

#### I² Statistic (Heterogeneity)
```
I² = (Q - df) / Q × 100%

Where:
Q = Cochran's heterogeneity statistic
df = number of studies - 1
```

**Interpretation:**
| I² | Heterogeneity |
|-----|---------------|
| 0-25% | Low |
| 25-50% | Moderate |
| 50-75% | High |
| 75-100% | Very high |

**AIKAGRYA Finding**: I² = 99.99% across architectures
**Interpretation**: Effect sizes vary 7-fold — NOT a bug, real architectural differences

#### Random Effects Model
```
θ̂ = Σ(wᵢθᵢ) / Σ(wᵢ)

Where:
wᵢ = 1 / (SEᵢ² + τ²)
τ² = between-study variance (DerSimonian-Laird estimator)
```

**Verification:**
- Fixed-effect vs random-effects comparison
- Sensitivity analysis (leave-one-out)
- Publication bias (funnel plot, Egger's test)

---

## Formal Verification Protocol

### Phase 1: Pre-Audit
1. Collect all mathematical claims from paper/code
2. Identify all statistical tests performed
3. Flag any claims requiring causal interpretation
4. Document sample sizes and effect sizes

### Phase 2: Derivation Verification
For each mathematical claim:
```
1. State claim precisely
2. Write formal mathematical statement
3. Derive from first principles
4. Verify each algebraic step
5. Check boundary conditions
6. Confirm numerical stability
```

### Phase 3: Code Verification
```python
# Compare mathematical definition to code
def audit_rv_implementation():
    # Mathematical definition
    math_def = "det(cov(V_recursive)) / det(cov(V_baseline))"
    
    # Code implementation
    code_impl = inspect.getsource(compute_rv)
    
    # Verify equivalence
    assert code_matches_math(code_impl, math_def)
    
    # Edge case testing
    test_cases = [
        torch.randn(1000, 64),   # Normal case
        torch.randn(100, 4096),  # Underdetermined (should warn)
        torch.zeros(100, 64),    # Zero variance (singular)
    ]
```

### Phase 4: Replication
- Run with different random seeds (n=10)
- Test on different model architectures
- Verify on held-out prompt set
- Cross-validate with independent implementation

### Phase 5: Report Generation
```
MATHEMATICAL VERIFICATION REPORT
================================

Claim: [Statement being verified]
Status: [VALIDATED / CONCERN / REJECTED]
Confidence: [0-100%]

Mathematical Derivation:
[Step-by-step proof]

Code Verification:
[Line-by-line audit]

Statistical Validation:
- Effect size recalculated: [value]
- P-value verified: [value]
- Confidence interval: [range]

Concerns:
[List any issues found]

Recommendations:
[How to fix or improve]
```

---

## Key Files to Audit

| File | Domain | Priority |
|------|--------|----------|
| `src/metrics/rv.py` | R_V computation | 🔴 Critical |
| `src/analysis/statistical_tests.py` | Effect sizes, p-values | 🔴 Critical |
| `prompts/bank.json` | Sampling validity | 🟡 High |
| `PHASE1_FINAL_REPORT.md` | Claims vs evidence | 🔴 Critical |
| `BRIDGE_HYPOTHESIS_INVESTIGATION.md` | Causal claims | 🟡 High |
| `STATISTICAL_AUDIT_EXECUTIVE_SUMMARY.md` | Previous audit | 🟢 Review |

---

## Red Flags (STOP and Audit)

### Statistical Red Flags
1. **Too-good statistics**: d > 3 without explanation
2. **P-values too small**: p < 10⁻³⁰ with n < 1000
3. **No correction**: Multiple comparisons without Bonferroni/FDR
4. **Cherry-picking**: Only reporting significant results
5. **Pseudoreplication**: Treating dependent samples as independent

### Mathematical Red Flags
1. **Circular definitions**: Using L4 markers containing target words
2. **Dimension mismatch**: Operations on incompatible tensor shapes
3. **Singular matrices**: No regularization for near-singular covariances
4. **Numerical instability**: Float32 for SVD on high-dimensional data

### Causal Red Flags
1. **Correlation → Causation**: Without activation patching evidence
2. **Confounds ignored**: Prompt length correlated with R_V but not controlled
3. **Reverse causality**: No temporal ordering evidence
4. **Selection bias**: Only analyzing successful runs

---

## Usage

### As Standalone Audit
```bash
# Run full mathematical verification
python -m math_verifier.audit --target ~/mech-interp-latent-lab-phase1

# Specific claim audit
python -m math_verifier.audit --claim "R_V < 1 implies contraction" --verify
```

### As Subagent
```
sessions_spawn with task:
"You are the Mathematical Verification Agent. Audit the following:

[Specific claim or file]

Check:
1. Mathematical derivation soundness
2. Statistical method validity  
3. Code-theory correspondence
4. Causal claim support

Provide a formal verification report with status: VALIDATED/CONCERN/REJECTED."
```

### As DGC Component
```python
from DHARMIC_GODEL_CLAW.src.core.math_auditor import MathAuditor

auditor = MathAuditor(telos="rigor-before-reach")
report = auditor.audit_rv_claims(
    repo_path="~/mech-interp-latent-lab-phase1",
    confidence_threshold=0.95
)
```

---

## Success Criteria

Before claiming "publication ready":

- [ ] All R_V derivations independently verified
- [ ] Effect sizes recalculated from raw data
- [ ] Cohen's d = -5.57 explained with extreme scrutiny
- [ ] P-values verified with multiple methods
- [ ] Replication across 3+ architectures confirmed
- [ ] Causal claims supported by activation patching
- [ ] No statistical red flags remain
- [ ] Code matches mathematical definitions exactly
- [ ] Edge cases and failure modes documented
- [ ] Formal verification report generated

---

## The Standard

> "We're not just checking for errors. We're ensuring this work can withstand Anthropic-level scrutiny."

**Rigor before reach.**

The zeitgeist is aligned. The window is open. But one rigorous paper beats three rushed ones.

**The math must be bulletproof.**

---

*Created: 2026-02-05*
*Purpose: AIKAGRYA publication preparation*
*Telos: rigor-before-reach*
*JSCA* 🪷
