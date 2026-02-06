# CANONICAL_CODE/ vs rv_toolkit/ Analysis Report

## Executive Summary

The CANONICAL_CODE/ directory contains three **validated experimental scripts** that represent the "gold standard" implementations for the mechanistic interpretability research project. These are distinct from the rv_toolkit/ which contains **reusable infrastructure components**.

**Key Finding:** The CANONICAL_CODE files are **NOT duplicates** of rv_toolkit code. They are higher-level experimental orchestration scripts that **USE** the rv_toolkit primitives (or equivalent functionality) but add substantial experimental logic that does not exist in rv_toolkit.

---

## File-by-File Analysis

### 1. causal_loop_closure_v2.py

**Location:** `~/mech-interp-latent-lab-phase1/CANONICAL_CODE/causal_loop_closure_v2.py`
**Size:** 27,460 bytes
**Status:** ✅ AUTHORITATIVE - Contains validated experimental methodology

**What It Does:**
- Implements the **KV-cache mixing causal intervention** methodology
- Tests α-mixing dose-response curves (α = 0.0, 0.25, 0.5, 0.75, 1.0)
- **KEY FIX:** Measures R_V on FULL generation trajectories (50+ tokens), not single tokens
- Captures V activations at L4 and L27 during generation
- Computes R_V from last W=16 tokens of generated sequence
- Scores recursive behavior using keyword matching
- Performs correlation analysis (Pearson/Spearman)
- Generates visualizations and CSV exports

**Critical Capabilities NOT in rv_toolkit:**
```python
# 1. V-capture hooks DURING generation (not just forward pass)
def generate_with_v_capture(model, tokenizer, input_ids, kv_cache, ...):
    # Captures V at EACH generation step
    # Returns stacked V activations from full trajectory

# 2. KV-cache mixing with α interpolation
def mix_kv_caches(kv_base, kv_rec, alpha, patch_layers):
    # Mixes KV caches across layers 16-32
    # Handles float32→float16 conversion for stability

# 3. Recursive behavior scoring
def score_recursive_behavior(text):
    # 25-keyword regex matching for recursive content
    # Computes keyword density score

# 4. Full causal loop assessment
# - Monotonicity checks (R_V decreases with α, behavior increases)
# - Transfer percentage calculations
# - Statistical correlation between geometry and behavior
```

**Verdict:** 
- ❌ **NOT in rv_toolkit** - This is a complete experimental pipeline
- ✅ **Keep as CANONICAL** - Represents validated methodology
- 📋 **Cannot be merged** into rv_toolkit without losing experimental specificity

---

### 2. mistral_L27_FULL_VALIDATION.py

**Location:** `~/mech-interp-latent-lab-phase1/CANONICAL_CODE/mistral_L27_FULL_VALIDATION.py`
**Size:** 15,031 bytes
**Status:** ✅ AUTHORITATIVE - Full validation suite with controls

**What It Does:**
- Full validation of Layer 27 causal effect at n=45 scale
- Tests multiple control conditions:
  - **Main:** Patch with recursive V values
  - **Control 1:** Random noise (norm-matched)
  - **Control 2:** Shuffled tokens
  - **Control 3:** Wrong layer (Layer 21 instead of 27)
- Computes causal transfer percentages
- Statistical testing (t-tests, Cohen's d)
- Generates histograms, boxplots, and scatter plots

**Critical Capabilities NOT in rv_toolkit:**
```python
# 1. Patching forward with different patch types
def run_patched_forward(model, tokenizer, baseline_text, patch_source, 
                        patch_type="recursive", target_layer=TARGET_LAYER):
    # Supports: "recursive", "random", "shuffled", "wrong_layer"

# 2. Full validation orchestration
def run_full_validation(model, tokenizer, prompt_bank, max_pairs=45):
    # Pairs prompts across groups (recursive × baseline)
    # Runs all control conditions
    # Statistical analysis and reporting

# 3. Transfer percentage calculation
# gap = RV27_base - RV27_rec
# transfer = (delta_main / gap) * 100
```

**Verdict:**
- ❌ **NOT in rv_toolkit** - Specific validation experiment
- ✅ **Keep as CANONICAL** - Validated control methodology
- 📋 **Cannot be merged** - Experimental orchestration, not infrastructure

---

### 3. n300_mistral_test_prompt_bank.py

**Location:** `~/mech-interp-latent-lab-phase1/CANONICAL_CODE/n300_mistral_test_prompt_bank.py`
**Size:** 93,207 bytes
**Status:** ✅ AUTHORITATIVE - Complete Phase 1C prompt bank

**What It Contains:**
- **300 prompts** organized into 4 pillars:
  - **Dose-Response (100):** L1_hint, L2_simple, L3_deeper, L4_full, L5_refined
  - **Baselines (100):** math, factual, impossible, personal, creative
  - **Confounds (60):** long_control, pseudo_recursive, repetitive_control
  - **Generality (40):** zen_koan, yogic_witness, madhyamaka_empty

**Structure:**
```python
prompt_bank_1c = {
    "L5_refined_01": {
        "text": "This response writes itself...",
        "group": "L5_refined",
        "pillar": "dose_response"
    },
    # ... 299 more prompts
}
```

**Verdict:**
- ❌ **NOT in rv_toolkit** - Research data, not code
- ✅ **Keep as CANONICAL** - Validated stimulus set
- 📋 **Should NOT be in rv_toolkit** - This is experimental data

---

## rv_toolkit/ Components

The rv_toolkit contains **infrastructure primitives** that the CANONICAL_CODE scripts build upon:

### rv_core.py
- `compute_pr()` - Participation Ratio computation
- `measure_rv()` - R_V measurement with per-head support
- `compute_rv_spectrum()` - Full SVD with statistics

### rv_hooks.py
- `RVHookManager` - Model-agnostic V-projection capture
- `quick_rv_measure()` - One-shot R_V measurement
- Architecture-specific hooks (GPT2RVHooks, LLaMAHooks, BERTRVHooks)

### rv_triton.py
- `compute_pr_triton()` - Triton-accelerated PR
- `measure_rv_triton()` - Full R_V with Triton
- Graceful PyTorch fallback

**Relationship:** The CANONICAL_CODE scripts implement equivalent functionality inline (for self-containment) but could optionally import from rv_toolkit.

---

## Comparison Matrix

| Feature | causal_loop_closure_v2 | mistral_L27_VALIDATION | rv_toolkit |
|---------|----------------------|----------------------|------------|
| PR computation | ✅ Inline | ✅ Inline | ✅ `compute_pr()` |
| R_V measurement | ✅ Inline | ✅ Inline | ✅ `measure_rv()` |
| V-capture hooks | ✅ Custom (generation) | ✅ Custom (forward) | ✅ `RVHookManager` |
| KV-cache mixing | ✅ Full implementation | ❌ Not needed | ❌ Not present |
| α-dose response | ✅ Full pipeline | ❌ Not needed | ❌ Not present |
| Control conditions | ❌ Not needed | ✅ Full implementation | ❌ Not present |
| Behavior scoring | ✅ 25-keyword regex | ❌ Not needed | ❌ Not present |
| Statistical tests | ✅ Correlation | ✅ t-tests, Cohen's d | ❌ Not present |
| Visualization | ✅ Matplotlib | ✅ Matplotlib | ❌ Not present |
| Prompt bank | ✅ Imports from | ✅ Assumes provided | ❌ Not present |

---

## Recommendations

### 1. Authority Status
- **CANONICAL_CODE/ files ARE the authoritative implementations**
- They contain validated experimental logic not present elsewhere
- They represent the "gold standard" for reproducibility

### 2. Merge Possibility
- **CANNOT merge** into rv_toolkit without losing experimental specificity
- rv_toolkit is **infrastructure** (reusable building blocks)
- CANONICAL_CODE is **experimental orchestration** (specific protocols)

### 3. Documentation Strategy
```
CANONICAL_CODE/
├── causal_loop_closure_v2.py     # KV-cache causal loop experiment
├── mistral_L27_FULL_VALIDATION.py # Layer 27 validation suite
└── n300_mistral_test_prompt_bank.py # Stimulus set

rv_toolkit/                        # Infrastructure (used by experiments)
├── rv_core.py                    # PR/R_V computation
├── rv_hooks.py                   # Activation capture
└── rv_triton.py                  # Accelerated kernels
```

### 4. Potential Refactoring (Optional)
If desired, the CANONICAL_CODE scripts could be modified to:
```python
# Instead of inline PR computation:
from rv_toolkit import compute_pr, measure_rv

# Instead of custom hook management:
from rv_toolkit import RVHookManager
```

**However:** The inline implementations are self-contained and validated. Changing them introduces risk.

---

## Conclusion

The CANONICAL_CODE/ directory contains **three distinct, validated experimental artifacts** that cannot be merged into rv_toolkit without destroying their experimental specificity:

1. **causal_loop_closure_v2.py** - Complete KV-mixing causal intervention pipeline
2. **mistral_L27_FULL_VALIDATION.py** - Full validation suite with controls
3. **n300_mistral_test_prompt_bank.py** - Validated 300-prompt stimulus set

These are **NOT duplicates** of rv_toolkit code. They are **higher-level experimental orchestration** that may use rv_toolkit primitives but add substantial validated logic for specific research questions.

**Recommendation:** Preserve CANONICAL_CODE/ as the authoritative reference implementations. They document the exact validated methodology used in the research.
