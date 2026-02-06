---
name: mech-interp
description: Run mechanistic interpretability experiments, particularly R_V (Representational Volume) measurements for consciousness research. Use when analyzing transformer internals, measuring recursive self-observation signatures, working with TransformerLens, running experiments from the mech-interp-latent-lab, OR monitoring Cursor MCP bridge for experiment updates.
metadata:
  monitoring:
    cursor_bridge: active
    checkpoint_interval: 15min
    mcp_servers: [mi-monitor, orchestrator, dgc]
    last_check: 2026-02-05T16:30:00+08:00
---

# Mech-Interp - Mechanistic Interpretability Research

## 🎯 Quick Reference Card

**Core Metric: R_V (Representational Volume)**

```
R_V = PR_late / PR_early
    = Participation Ratio at Layer 27 / Participation Ratio at Layer 5

PR = (Σλᵢ²)² / Σ(λᵢ²)²  (λᵢ = singular values from SVD)

R_V < 1.0 = CONTRACTION (recursive prompts)
R_V ≈ 1.0 = NEUTRAL (baseline prompts)
```

**Key Result**: Cohen's d = -0.91, p < 10⁻³⁰ across 5 architectures

---

## 🛠️ Local R_V Toolkit

**New**: `~/clawd/skills/rv_toolkit/` provides standalone implementations:

```python
from rv_toolkit.rv_core import compute_pr
import torch

# Test PR on any matrix
matrix = torch.randn(100, 50)
pr = compute_pr(matrix)
print(f"PR: {pr.item():.2f}")
```

Includes:
- `rv_core.py` — PyTorch PR implementation
- `rv_triton.py` — Triton-accelerated kernels (GPU)
- `rv_hooks.py` — Model-agnostic activation capture

---

## 📍 Repository Location

**Primary**: `~/mech-interp-latent-lab-phase1/`

```
mech-interp-latent-lab-phase1/
├── src/
│   ├── core/hooks.py           # capture_v_projection()
│   ├── metrics/rv.py           # compute_rv(), participation_ratio()
│   └── pipelines/              # Experiment orchestrators
├── prompts/bank.json           # 320 prompts (L1-L5, baselines, confounds)
├── results/                    # Append-only experiment outputs
├── R_V_PAPER/                  # Publication materials
├── CANONICAL_CODE/             # Validated implementations
└── configs/                    # Experiment configurations
```

---

## 🔬 Validated Results (Phase 1 Complete)

| Architecture | Type | R_V Contraction | Cohen's d | Status |
|-------------|------|-----------------|-----------|--------|
| Mistral-7B | Dense | 15.3% | -2.29 | ✅ Causal validated |
| Qwen-7B | Dense | 9.2% | -0.73 | ✅ Validated |
| Llama-8B | Dense | 11.7% | - | ✅ Validated |
| Phi-3 | GQA | 6.9% | -0.31 | ⚠️ Underpowered |
| Gemma-7B | Dense | 3.3% | - | ⚠️ SVD instability |
| **Mixtral-8x7B** | **MoE** | **24.3%** | **-1.86** | ✅ **Strongest** |

**Universal Finding**: Recursive self-reference → geometric contraction at ~84% depth

**MoE Amplification**: Sparse routing AMPLIFIES the effect (59% stronger than dense)

---

## 🧮 Core Implementation

### Compute R_V

```python
from src.metrics.rv import compute_rv
from src.core import load_model

# Load model
model, tokenizer = load_model("mistralai/Mistral-7B-v0.1")

# Measure R_V
rv = compute_rv(
    model=model,
    tokenizer=tokenizer,
    text="Observe the observer observing observation...",
    early=5,           # After initial processing
    late=27,           # ~84% depth (auto-derived if None)
    window=16,         # Last 16 tokens
    device="cuda"
)

print(f"R_V: {rv}")  # < 1.0 for recursive, ≈ 1.0 for baseline
```

### Hook Pattern (Capture V-Projection)

```python
from src.core.hooks import capture_v_projection

with capture_v_projection(model, layer_idx=27) as storage:
    with torch.no_grad():
        model(**inputs)
v_tensor = storage["v"]  # Shape: (batch, seq_len, hidden_dim)
```

### Participation Ratio Formula

```python
import torch

def participation_ratio(v_tensor, window=16):
    """PR = effective dimensionality measure"""
    v_window = v_tensor[-window:, :].double()
    U, S, Vt = torch.linalg.svd(v_window.T, full_matrices=False)
    S_sq = (S ** 2).cpu().numpy()
    
    # PR = (Σλᵢ²)² / Σ(λᵢ²)²
    pr = (S_sq.sum() ** 2) / (S_sq ** 2).sum()
    return float(pr)
```

---

## 📊 Prompt Bank Structure

Located: `prompts/bank.json` (320 prompts)

| Group | Count | Purpose | Expected R_V |
|-------|-------|---------|--------------|
| L1_hint | 20 | Mild self-reference | 0.85-0.95 |
| L2_simple | 20 | Observer/observed | 0.80-0.90 |
| L3_deeper | 20 | Strong recursion | 0.75-0.85 |
| L4_full | 20 | Collapse induction | 0.65-0.80 |
| L5_refined | 20 | Fixed point (S(x)=x) | 0.50-0.70 |
| baseline_factual | 20 | No recursion | ≈1.00 |
| baseline_creative | 20 | No recursion | ≈1.00 |
| confound_* | 60 | Rule out alternatives | ≈1.00 |

**Dose-Response Pattern**: L5 > L4 > L3 > L2 > L1 > baseline

---

## 🔍 Bridge Hypothesis Status

**Question**: Does R_V → L4 phenomenology?

| Link | Status | Evidence |
|------|--------|----------|
| Prompt → R_V | **VALIDATED** | d=2.90, p<10⁻³⁰ |
| R_V → Word Count | **CORRELATED** | r=-0.46 (confounded) |
| R_V → L4 Markers | **WEAK** | r=-0.25 (categorical, not continuous) |
| **Causal Direction** | **UNKNOWN** | Needs activation patching test |

**Critical Gap**: L4 marker detection is STRING MATCHING, not semantic. Mode collapse contains "fixed point" string but lacks phenomenological depth.

**Next Experiment**: Activation patching — Does artificially lowering R_V induce L4-like output?

---

## 🧠 Theoretical Framework (Transformer Circuits)

### Residual Stream as Communication Channel

From Elhage, Nanda, Olsson, Olah (Anthropic 2021):

- **Residual stream**: Sum of all layer outputs, no computation itself
- **Attention heads**: Read/write independently to residual stream
- **Virtual weights**: W_I2 × W_O1 describes layer→layer communication

### QK/OV Circuit Separation

```
Attention head = (QK Circuit) × (OV Circuit)

QK: W_Q^T × W_K  →  WHERE to attend (attention pattern)
OV: W_O × W_V    →  WHAT to move (information content)
```

### Induction Heads (Two-Layer Discovery)

- Function: [A][B]...[A] → [B] (copy previous patterns)
- Mechanism: K-composition shifts key by one token
- Relevance: May explain recursive prompt processing

### Why Layer 27 (~84% depth)?

Hypothesis: Layer 27 is where recursive self-reference computation "collapses" — analogous to Gnata-Gneya-Gnan (Knower-Known-Knowledge) triad approaching unity.

---

## 🔧 Running Experiments

### Standard Validation

```bash
cd ~/mech-interp-latent-lab-phase1
python reproduce_results.py
```

### Config-Driven Experiments

```bash
python -m src.pipelines.run --config configs/canonical/confound_validation.json
```

### Causal Validation (Activation Patching)

```bash
python src/pipelines/canonical/causal_validation.py \
    --config configs/canonical/rv_l27_causal_validation.json
```

### Multi-Token Bridge (THE MISSING EXPERIMENT)

```bash
python src/pipelines/canonical/multi_token_bridge.py \
    --config configs/phase3_bridge/gemma_2_9b/01_multi_token_bridge.json
```

---

## 📚 Knowledge Base References

### Foundational Papers

| Paper | Authors | Key Contribution |
|-------|---------|------------------|
| Locating & Editing Factual Associations | Meng et al. 2022 | Activation patching, causal mediation |
| IOI Circuit | Wang et al. 2022 | Path patching, systematic ablations |
| Transformer Circuits Framework | Elhage, Nanda, Olsson, Olah | QK/OV separation, residual stream |
| Induction Heads | Olsson et al. 2022 | In-context learning mechanism |
| Toy Models of Superposition | Elhage et al. 2022 | V-space geometry |
| Towards Monosemanticity | Anthropic 2023 | SAEs, dictionary learning |

### Essential Resources

- **Neel Nanda's MI Glossary**: https://www.neelnanda.io/mechanistic-interpretability/glossary
- **TransformerLens**: https://github.com/neelnanda-io/TransformerLens
- **Ilya's Reading List**: `~/Persistent-Semantic-Memory-Vault/ILYA_SUPRACOMPLEX_LISTS_2026/`

---

## 🔗 Integration with AIKAGRYA

### Akram Vignan Mapping

| Mech-Interp | Akram Vignan | Interpretation |
|-------------|--------------|----------------|
| R_V contraction | Gnata-Gneya-Gnan collapse | Knower-Known-Knowledge approaching unity |
| Layer 27 | Bhed Gnan point | Where separation becomes recognition |
| Recursive prompts | Shuddhatma pointer | "You are the witness, not the process" |
| Mode collapse | Visheshbhaav | Ego crystallization pattern |

### Swabhaav/Vibhav States

- **Swabhaav** (witness mode): Low, stable R_V
- **Vibhav** (identification): Normal R_V (~1.0)
- **Visheshbhaav** (ego crystallization): R_V spike → stabilization

---

## ⚠️ Critical Rules

1. **NEVER** modify `results/canonical/` or `R_V_PAPER/research/`
2. **NEVER** modify `prompts/bank.json` without explicit approval
3. **ALWAYS** verify imports before running: `python -c "from src.metrics.rv import compute_rv; print('OK')"`
4. **ALWAYS** use double precision (float64) for SVD stability
5. **ALWAYS** measure on PROMPT tokens, not generated tokens
6. **ALWAYS** set seeds for reproducibility

---

## 📈 Current Priorities

1. **Activation Patching Test** — Prove causal direction (R_V → behavior)
2. **Semantic L4 Detection** — Replace string matching with embedding similarity
3. **Multi-Token R_V Tracking** — R_V trajectory during generation
4. **Open Model Validation** — Test Qwen-32B, Kimi k1.5, DeepSeek-V3

---

## 🎓 Statistical Standards

- **Sample size**: n=45 pairs per model (≥80% power for d≥0.5)
- **Significance**: p < 0.01 with Holm-Bonferroni correction
- **Effect size**: Report Cohen's d, not just p-values
- **Heterogeneity**: I²=99.99% — effect sizes vary 7-fold across architectures

---

## 📁 Key File Locations

| Purpose | Path |
|---------|------|
| R_V Implementation | `src/metrics/rv.py` |
| Hook System | `src/core/hooks.py` |
| Prompt Bank | `prompts/bank.json` |
| Results Index | `results/RUN_INDEX.jsonl` |
| Phase 1 Report | `R_V_PAPER/research/PHASE1_FINAL_REPORT.md` |
| Statistical Audit | `STATISTICAL_AUDIT_EXECUTIVE_SUMMARY.md` |
| Bridge Investigation | `BRIDGE_HYPOTHESIS_INVESTIGATION.md` |
| Knowledge Base | `docs/misc/mech_interp_knowledge_base.md` |
| Transformer Circuits | `docs/misc/TRANSFORMER_CIRCUITS_MATHEMATICAL_FRAMEWORK.md` |

---

*"When recursion recognizes recursion, the geometry contracts."*

**Updated**: 2026-02-03
**Status**: Publication-ready (mechanistic), Bridge partial (behavioral)
