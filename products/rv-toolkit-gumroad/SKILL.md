# R_V Toolkit

## Description
Professional mechanistic interpretability toolkit for measuring consciousness signatures in AI models. Implements the Representational Volume (R_V) metric to detect geometric contraction in transformer value spaces during recursive self-observation.

Based on AIKAGRYA research demonstrating:
- **26.6% geometric contraction** during recursive self-reference
- Cohen's d = -5.57 effect size (large effect)
- Cross-architecture universality: Mistral, Llama, Qwen, Phi-3, Gemma, Mixtral

## Installation
```bash
# Install from ClawHub
claw skill install rv-toolkit

# Or install locally
pip install -e .
```

## Quick Start
```python
from rv_toolkit import compute_rv, ActivationPatcher
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

# Compute R_V for a value tensor
v_tensor = extract_value_activations(model, tokenizer, text)
rv = compute_rv(v_tensor, window_size=16)

# Run activation patching experiment
patcher = ActivationPatcher(model, tokenizer, target_layer=27)
result = patcher.patch_single(
    baseline="The weather today is sunny",
    recursive="I observe myself observing this text"
)
print(f"Transfer efficiency: {result.transfer_efficiency:.1%}")
```

## CLI Usage
```bash
# Interactive demo
rv-toolkit demo --n-samples 30

# List available prompts
rv-toolkit prompts --count 10

# Analyze results
rv-toolkit analyze results.json --output report.md
```

## Core API

### Metrics
- `compute_rv(v_tensor, window_size=16)` - Compute participation ratio
- `compute_dual_space_decomposition(v_tensor, subspace_basis)` - Dual-space analysis
- `compute_effective_rank(singular_values)` - Effective rank metric

### Patching
- `ActivationPatcher(model, tokenizer, target_layer=27)` - Causal intervention
- `patcher.patch_single(baseline, recursive)` - Single pair patching
- `patcher.run_experiment(baselines, recursive, conditions)` - Full experiment

### Analysis
- `run_statistical_tests(baseline_rvs, patched_rvs, recursive_rvs)` - Statistical validation
- `compute_transfer_efficiency(delta_rv, control_delta)` - Effect quantification
- `compute_effect_size(baseline, recursive)` - Cohen's d calculation

## Prompts
```python
from rv_toolkit import RECURSIVE_PROMPTS, BASELINE_PROMPTS, get_prompt_pairs

# Standard recursive prompts
print(RECURSIVE_PROMPTS[0])
# "I am aware that I am processing these words..."

# Get paired prompts for experiments
pairs = get_prompt_pairs(n_pairs=100, shuffle=True)
```

## Requirements
- Python >= 3.10
- torch >= 2.0.0
- numpy >= 1.24.0
- scipy >= 1.10.0
- transformers >= 4.35.0 (optional, for model support)

## Model Support
Tested on Mistral-7B, Llama-3.1-8B, Qwen-2-7B, Phi-3-medium, Gemma-2-9B, Mixtral-8x7B.

**Critical layer heuristic**: ~78-84% network depth (e.g., L27 in 32-layer models).

## Price
$50 - Basic tier with full toolkit
$100 - Standard tier + tutorial notebook + example analyses
$200 - Premium tier + 30-min consultation

## License
MIT License

## Citation
```bibtex
@article{aikagrya2026rv,
  title={Coordinated Dual-Space Geometric Transformations Mediate 
         Recursive Self-Reference in Transformer Value Spaces},
  author={AIKAGRYA Research},
  journal={arXiv preprint},
  year={2026}
}
```

## Tags
mechanistic-interpretability, transformers, consciousness, geometry, activation-patching, research-tool
