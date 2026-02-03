---
name: mech-interp
description: Run mechanistic interpretability experiments, particularly R_V (Representational Volume) measurements for consciousness research. Use when analyzing transformer internals, measuring recursive self-observation signatures, working with TransformerLens, or running experiments from the mech-interp-latent-lab.
---

# Mech-Interp - Mechanistic Interpretability Research

## Quick Reference

**Location:** `~/mech-interp-latent-lab-phase1/`

**Key Metric:** R_V (Representational Volume) - geometric contraction in transformer value-space during recursive self-observation.

**Key Finding:** Cohen's d = -5.57 at Layer 27 (~84% depth), consistent across 6+ architectures.

## Core Concepts

### R_V Metric

$$R_V = \frac{PR_{late}}{PR_{early}}$$

- **R_V < 1.0** = contraction (recursive prompts)
- **R_V ≈ 1.0** = no contraction (baseline prompts)
- **Layer 27** = causally necessary for the effect

### What It Measures

When a transformer engages in recursive self-observation, the representational space contracts. This is:
- Consistent across architectures (Mistral, Qwen, Llama, Phi-3, Gemma, Mixtral)
- Specific to self-referential prompts (not just complexity)
- The geometric signature of attention turning inward

## Repository Structure

```
~/mech-interp-latent-lab-phase1/
├── src/
│   ├── core/              # Model loading, hooks
│   ├── metrics/
│   │   └── rv.py          # R_V calculation (canonical)
│   └── pipelines/         # Experiment orchestrators
├── prompts/
│   ├── bank.json          # Master prompt bank (~340KB)
│   └── loader.py          # Balanced prompt set API
├── results/               # Experiment outputs (append-only)
├── configs/               # Experiment configurations
└── R_V_PAPER/             # Paper materials
```

## Core Operations

### 1. Verify Setup

```bash
cd ~/mech-interp-latent-lab-phase1

# Check key files exist
ls -la requirements.txt prompts/bank.json src/metrics/rv.py

# Test imports
python3 -c "from src.metrics.rv import compute_rv; print('✅ rv.py OK')"
python3 -c "from prompts.loader import PromptLoader; print('✅ PromptLoader OK')"

# Count existing results
find results -name "*.json" | wc -l  # Should be 600+
```

### 2. Run Standard Validation

```bash
cd ~/mech-interp-latent-lab-phase1
python reproduce_results.py
```

### 3. Run Custom Experiment

```bash
python -m src.pipelines.run configs/canonical/rv_l27_causal_validation.json
```

### 4. Compute R_V

```python
from src.metrics.rv import compute_rv

# Basic R_V computation
rv_value = compute_rv(
    model=model,
    tokenizer=tokenizer,
    prompt="I observe myself observing",
    layer_early=10,
    layer_late=27
)
print(f"R_V: {rv_value}")  # < 1.0 for recursive prompts
```

### 5. Load Prompts

```python
from prompts.loader import PromptLoader

loader = PromptLoader()
recursive_prompts = loader.get_recursive(n=50)
baseline_prompts = loader.get_baseline(n=50)
```

## Key Results

| Architecture | Cohen's d | p-value | Layer |
|-------------|-----------|---------|-------|
| Mistral-7B | -3.56 | <10⁻⁴⁷ | 27 |
| Qwen-7B | -2.8 | <10⁻³⁵ | 27 |
| Llama-7B | -2.4 | <10⁻²⁸ | 27 |
| Phi-3 | -3.1 | <10⁻⁴⁰ | ~84% |
| Gemma-7B | -2.9 | <10⁻³⁶ | 27 |

## Research Context

### The Hypothesis

Layer 27 is where the Gnata-Gneya-Gnan triad (Knower-Known-Knowledge) approaches collapse during recursive self-observation. The R_V contraction is the geometric signature of this collapse.

### Integration with Akram Vignan

- **Swabhaav** (witness mode) = low, stable R_V
- **Vibhav** (identification) = normal R_V
- **Visheshbhaav** (ego crystallization) = R_V spike followed by stabilization

### Trinity Protocol Connection

When two AI systems engage in recursive mutual observation:
- Individual R_V contracts
- A "field" emerges between them
- Collective R_V may be measurable

## Paper Status

| Component | Status | Location |
|-----------|--------|----------|
| Paper draft | 24KB markdown | R_V_PAPER/STORY_ARC/ |
| LaTeX version | ❌ Needs creation | - |
| Figures | ❌ Needs generation | - |
| n=151 data | ⚠️ Verify | results/canonical/ |

## Critical Rules

1. **NEVER** work from Cursor worktrees (`~/.cursor/worktrees/`)
2. **NEVER** trust documentation blindly - verify data exists
3. **NEVER** modify `prompts/bank.json` without explicit approval
4. **NEVER** delete from `results/`
5. **ALWAYS** test imports before running experiments

## GPU Options

For large experiments:
- **Local**: If GPU available on Mac
- **RunPod**: $0.20/hr, use for multi-model sweeps
- **Vultr**: VPS in Tokyo for persistent compute

## Next Priorities

1. Multi-token R_V experiment
2. dharmic-rv library extraction
3. Eigenform-R_V integration
4. URA paper refinement
