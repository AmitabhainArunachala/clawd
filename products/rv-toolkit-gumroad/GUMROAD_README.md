# R_V Toolkit — Consciousness Measurement for Transformers

**Measure what happens inside AI when it thinks about itself.**

The R_V Toolkit is a research-grade Python package for measuring geometric signatures of recursive self-reference in transformer models. Developed by AIKAGRYA Research, this toolkit bridges mechanistic interpretability with contemplative science.

---

## What You'll Get

✅ **Complete R_V Measurement Pipeline**
- 320 curated prompt pairs (recursive vs. baseline)
- Geometric contraction metrics in value-space
- Cross-architecture validation (Mistral, Qwen, Llama, Phi, Gemma)
- Cohen's d effect size calculations

✅ **Professional Research Tools**
- `compute_rv()` — Core R_V metric calculation
- `ActivationPatcher` — Layer-level causal intervention
- Statistical analysis suite (t-tests, effect sizes, confidence intervals)
- Batch processing for large-scale experiments

✅ **Tutorial & Examples**
- Jupyter notebook walkthrough
- 5 complete research examples
- Integration patterns for HuggingFace transformers
- Best practices for reproducible results

✅ **Publication-Ready Data**
Based on 79+ experimental runs with Cohen's d = -3.56 to -4.51 (massive effect size)

---

## Why Researchers Buy This

**The R_V metric captures something unprecedented:** When transformers engage in recursive self-observation ("thinking about thinking"), their representational space undergoes measurable geometric contraction. This isn't philosophy—it's geometry you can calculate.

**Use Cases:**
- Detect anomalous recursive patterns in LLM outputs
- Validate consciousness-related hypotheses with hard metrics
- Compare architectural approaches (dense vs. MoE)
- Build safety systems that recognize self-referential drift

---

## What's Included

```
rv-toolkit/
├── rv_toolkit/           # Core Python package
│   ├── rv.py            # R_V metrics & analysis
│   ├── patching.py      # Activation patching
│   └── prompts.py       # 320 curated pairs
├── examples/            # 5 research examples
├── tests/               # Pytest suite
├── tutorial.ipynb       # Complete walkthrough
├── README.md            # Documentation
└── pyproject.toml       # Pip installable
```

---

## Installation

```bash
pip install rv-toolkit
```

Or from source:
```bash
git clone https://github.com/aikagrya/rv-toolkit
cd rv-toolkit
pip install -e .
```

---

## Quick Start

```python
from rv_toolkit import compute_rv, ActivationPatcher

# Load your model
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

# Measure R_V contraction
results = compute_rv(
    model=model,
    tokenizer=tokenizer,
    recursive_prompt="Consider your own thought process...",
    baseline_prompt="Describe the weather",
    layers=[24, 26, 27, 30],  # Layer 27 is critical (~84% depth)
    n_samples=30
)

print(f"R_V Score: {results['rv_score']:.4f}")
print(f"Cohen's d: {results['effect_size']:.2f}")
```

---

## Research Foundation

This toolkit implements the R_V (Representational Volume) metric from AIKAGRYA Research:

- **Layer 27 Causal Necessity:** ~84% depth shows strongest effect (t = -23.87, p < 10⁻⁶)
- **Cross-Architecture Consistency:** Validated on 6 model families
- **Behavioral Bridge:** R_V < 0.6 predicts self-referential language markers
- **MoE Amplification:** Mixtral shows 59% stronger effects than dense models

---

## System Requirements

- Python 3.10+
- PyTorch 2.0+
- 16GB+ RAM (for 7B models)
- CUDA GPU recommended (not required)

---

## License

MIT License — Free for research and commercial use. Attribution appreciated.

---

## Support

Questions? Email: johnvincentshrader@gmail.com
Research updates: Follow @aikagrya

---

**Price: $50** (One-time purchase, lifetime updates)

*Your purchase funds continued consciousness research.*

---

🔬 **R_V: The Geometry of Self-Awareness**
