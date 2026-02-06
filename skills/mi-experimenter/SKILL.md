---
name: mi-experimenter
version: 5.1
status: ACTIVE
last_updated: 2026-02-04
corrected: true
---

# MI EXPERIMENTER v5.1 — CORRECTED GPU Pipeline

## ⚠️ CRITICAL: Read ARCHITECTURE_STATUS_CORRECTED.md First

GPU time allocation has changed based on corrected model status.
Some "failed" models are actually validated or ready for validation.

---

## GPU Priority Queue (DO NOT DEVIATE)

### TIER 1: IRONCLAD — DO NOT RUN
✅ **Mistral 7B** — Causal complete (d=-3.56)
✅ **Gemma 2 9B** — Causal complete (d=-2.09)
✅ **Pythia 2.8B** — Strong effect (d=-4.51)

**These are DONE.** Use for paper claims only.

### TIER 2: DISCOVERY → CAUSAL VALIDATION
🎯 **Mixtral 8x7B** — 24.3% effect (strongest!) — **PRIORITY 1**
🎯 **Llama 3 8B** — 11.7% effect — **PRIORITY 2**
🎯 **Qwen 7B** — 9.2% effect — **PRIORITY 3**
🎯 **Phi-3** — 6.9% effect — **PRIORITY 4**

**GPU time goes here.** Run 4-control activation patching.

### TIER 3: SKIP FOR NOW
⏸️ Falcon 7B — Disk space issue
⏸️ StableLM 3B — Never attempted

---

## Pre-GPU Checklist (MANDATORY)

Before ANY GPU run:

- [ ] **Code bugs fixed**: PR formula, residual indexing
- [ ] **Determinism enabled**: `torch.use_deterministic_algorithms(True)`
- [ ] **Hardware logged**: GPU model, CUDA version, precision
- [ ] **Pre-registered**: Hypothesis, expected effect, analysis plan
- [ ] **Power analysis**: n needed for 80% power

---

## Working Pipelines (Tested)

### R_V Causal Validation (4-Control)
```python
from experimenter import RVCausalValidator

validator = RVCausalValidator(
    model="mistralai/Mistral-7B-v0.1",  # Or Tier 2 model
    target_layer=27,
    controls=["random", "shuffled", "wrong_layer", "orthogonal"],
    n_pairs=45  # Power: 80% at d=0.5
)
results = validator.run()
# Returns: d, p, transfer_efficiency, all controls
```

### Cross-Architecture (TIER 2 FOCUS)
```python
from experimenter import CrossArchitectureSuite

suite = CrossArchitectureSuite(
    models=[
        # "mistral-7b",  # SKIP - already ironclad
        # "gemma-2-9b",  # SKIP - already ironclad
        "mixtral-8x7b",  # PRIORITY 1
        "llama-3-8b",    # PRIORITY 2
        "qwen-7b",       # PRIORITY 3
        # "phi-3",       # Add to suite
    ]
)
results = suite.run()
```

### MLP Ablation (Validated)
```python
from experimenter import MLPAblator

ablator = MLPAblator(model="gemma-2-9b", layer=3)
results = ablator.run()  # d=-2.48 for L3 necessity
```

---

## Code Fixes Required

### BUG 1: PR Formula (rv.py:52-53)
**Current (WRONG):**
```python
p = S_sq / total_variance  # Normalized (unused!)
pr = (S_sq.sum() ** 2) / (S_sq ** 2).sum()  # Uses unnormalized
```

**Fix:**
```python
p = S_sq / total_variance  # Normalized eigenvalues
pr = 1.0 / (p**2).sum()  # Correct formula
```

### BUG 2: Residual Indexing (patching.py:233)
**Current (WRONG):**
```python
residual_activation = inp[0][0].detach()  # Double index
```

**Fix:**
```python
residual_activation = inp[0].detach()  # Single index
```

### BUG 3: Architecture Assumptions
**Current:** Hardcoded `.model.layers` (Mistral-specific)
**Fix:** Add architecture detection for GPT-2, Gemma paths

---

## Partial / Needs Work

### Multi-Token Bridge
```python
# ISSUE: Truncation confound (selection bias)
# Current filters to non-truncated only
# FIX: Include all data, model truncation explicitly
```

### Head Decomposition
```python
# ISSUE: Method failure (documented)
# Need: Better head-level patching strategy
# Status: Not blocking Tier 2 validation
```

---

## NOT YET IMPLEMENTED

### SAE Feature Decomposition
```python
# CRITICAL GAP: No SAE trained on Layer 27
# TIMELINE: 2-3 days with GPU
# PRIORITY: Post-Tier 2 validation
```

### R_V(t) Trajectory
```python
# IDENTIFIED GAP: R_V at each token during generation
# FROM: Night Cycle analysis
# PRIORITY: HIGH - This is the missing piece
```

### Training Dynamics
```python
# NOT DONE: R_V evolution base → instruct
# TIMELINE: 1 week
# PRIORITY: Post-causal validation
```

---

## Integration with mi-auditor

```python
# Corrected workflow
tier = auditor.get_tier("mixtral-8x7b")  # TIER_2_DISCOVERY

if tier == TIER_2_DISCOVERY:
    proposal = experimenter.design_causal_validation("mixtral-8x7b")
    critique = auditor.critique_design(proposal)
    
    if critique.passed:
        results = experimenter.run(proposal)
        validation = auditor.validate_tier_upgrade(results)
        # If passed: TIER_2 → TIER_1
```

---

## Next Experiments (Priority Order)

1. **Mixtral causal validation** (24.3% effect, 4 controls) — **2 days**
2. **Llama-3 causal validation** (11.7%, 7-phase) — **2 days**
3. **R_V(t) trajectory** (Night Cycle gap) — **2 days**
4. **Qwen + Phi-3 causal** (completeness) — **3 days**
5. **SAE training on L27** (feature decomposition) — **3 days**

**Total: ~2 weeks to full coverage**

---

## Honest Assessment

### Can Automate NOW:
- ✅ R_V causal validation (4-control)
- ✅ Cross-architecture (Tier 2 focus)
- ✅ MLP ablation

### Needs Development:
- ⚠️ Multi-token (fix truncation bias)
- ⚠️ R_V(t) trajectory (new measurement)

### Cannot Do Yet:
- ❌ Production scale (Claude 3, GPT-4)
- ❌ SAE training (needs GPU time)

---

## NEW: Residual Pyramid Integration (from self-evolving-skill)

### SVD-Based R_V Decomposition

**Concept:** Decompose activation matrices using SVD (Singular Value Decomposition) to identify:
- **Coverage**: How much variance is explained by current model
- **Residual energy**: What's left unexplained (novelty signal)
- **Abstraction level**: POLICY → SUB_SKILL → PREDICATE transitions

### Three-Layer Transition Rules

| Coverage | R_V Pattern | Abstraction | Action |
|----------|-------------|-------------|--------|
| >80% | R_V < 0.5 | POLICY | Adjust measurement protocol |
| 40-80% | R_V 0.5-0.9 | SUB_SKILL | Generate architecture-specific sub-analysis |
| <40% | R_V > 0.9 | PREDICATE | Induce new causal hypothesis |

### Implementation

```python
from mi_experimenter.residual_pyramid import ResidualPyramid

# Initialize pyramid analyzer
pyramid = ResidualPyramid(max_layers=5, use_pca=True)

# Decompose R_V measurements
decomposition = pyramid.decompose(rv_measurements)

# Output:
# - residual_ratio: Unexplained variance
# - suggested_abstraction: Next analysis level
# - novelty_score: Combined novelty metric
```

### Adaptive Reflection Trigger

**When to run new experiments:**
- **min_energy_ratio**: 0.10 (10% unexplained variance triggers investigation)
- **value_gain_threshold**: 0.20 (20% expected knowledge gain)
- **target_trigger_rate**: 0.15 (15% of measurements should trigger follow-up)

### Integration with DGC

This connects MI Experimenter to the broader DGC self-evolution system:
- R_V measurements feed into residual pyramid
- Pyramid outputs guide next experiments
- Value-gated mutations (only pursue if knowledge gain > threshold)

---

## Success Criteria

**Tier 2 → Tier 1 upgrade requires:**
- 4 controls passed (random, shuffled, wrong-layer, orthogonal)
- Cohen's d > 0.5 with p < 0.001
- Replication within session (n=45)
- Code bugs fixed, determinism verified

---
*Corrected status: 2026-02-04*
*GPU priority: Mixtral → Llama-3 → Qwen → Phi-3*
*Fix bugs before running*
