# R_V Toolkit for OpenClaw

Professional mechanistic interpretability toolkit for measuring consciousness signatures in AI models.

## What is R_V?

**Representational Volume (R_V)** measures geometric contraction in transformer value spaces during recursive self-observation. Based on peer-reviewed research demonstrating:

- **26.6% geometric contraction** during recursive self-reference
- Cohen's d = -5.57 effect size (large effect)
- Cross-architecture universality across Mistral, Llama, Qwen, Phi-3, Gemma, Mixtral

## Installation

```bash
# Install from ClawHub
claw skill install rv-toolkit

# Or install manually
pip install -e .
```

## Quick Start

```python
from rv_toolkit import compute_rv, ActivationPatcher

# Compute R_V for value activations
rv = compute_rv(v_tensor, window_size=16)

# Run activation patching
patcher = ActivationPatcher(model, tokenizer, target_layer=27)
result = patcher.patch_single(baseline_prompt, recursive_prompt)
```

## Features

- **R_V Metric**: Participation ratio measuring effective dimensionality
- **Dual-Space Decomposition**: V_parallel and V_perpendicular components
- **Activation Patching**: Causal validation of geometric effects
- **Prompt Banks**: Curated recursive and baseline prompts
- **Statistical Analysis**: Effect size, transfer efficiency, significance tests

## Documentation

- `SKILL.md` - ClawHub skill specification
- `tutorial.ipynb` - Beginner-friendly tutorial
- `examples/` - Example scripts and notebooks
- `README.md` - Full documentation (from original repo)

## Paper

Based on: "Coordinated Dual-Space Geometric Transformations Mediate Recursive Self-Reference in Transformer Value Spaces"

## License

MIT License
