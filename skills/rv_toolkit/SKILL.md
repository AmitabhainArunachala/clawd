# R_V Measurement Toolkit (`rv_toolkit`)

Measure the effective rank of value projections in transformers using the Participation Ratio metric.

## What is R_V?

R_V measures how effectively a model uses its representational capacity by analyzing the singular value spectrum of activation matrices:

```
PR = (Σ S²)² / Σ S⁴
```

- **PR = 1**: All information in one dimension (rank-1)
- **PR = d**: Full utilization of d dimensions
- **Low PR**: Potential representation collapse, redundant heads
- **High PR**: Rich, distributed representations

## Quick Start

```python
from rv_toolkit import quick_rv_measure, compute_pr

# One-shot measurement on a model
results = quick_rv_measure(model, input_ids, num_heads=12)
print(f"Mean R_V: {results['mean_rv']:.2f}")
print(f"Bottleneck layer: {results['bottleneck_layer']}")

# Direct PR computation on any matrix
import torch
W = torch.randn(512, 768)
pr = compute_pr(W)  # Effective rank of the matrix
```

## Detailed Usage

### Hook-based Measurement

```python
from rv_toolkit import RVHookManager

manager = RVHookManager(model)

with manager.capture():
    outputs = model(input_ids)

# Per-layer R_V
layer_rvs = manager.compute_rv()

# Full summary with per-head analysis
summary = manager.compute_rv_summary(num_heads=12)
```

### Architecture-Specific Hooks

```python
from rv_toolkit import GPT2RVHooks, LLaMAHooks, BERTRVHooks

# Auto-detects correct layer patterns
manager = LLaMAHooks(model)
```

### Triton Acceleration

```python
from rv_toolkit import measure_rv_triton, is_triton_available

if is_triton_available():
    # Uses Triton kernels for PR computation
    rv = measure_rv_triton(activations)
else:
    # Falls back to PyTorch automatically
    pass
```

## Files

- `rv_core.py` - Core PyTorch implementation
- `rv_triton.py` - Triton kernels (with fallback)
- `rv_hooks.py` - Model-agnostic activation capture

## Interpretation Guide

| R_V Range | Interpretation |
|-----------|----------------|
| < 10 | Severe collapse, head may be prunable |
| 10-30 | Moderate utilization |
| 30-50 | Good utilization |
| > 50 | Excellent, near full-rank |

Compare across layers to find bottlenecks. Low R_V early layers may indicate embedding issues; low R_V in later layers may suggest capacity saturation.
