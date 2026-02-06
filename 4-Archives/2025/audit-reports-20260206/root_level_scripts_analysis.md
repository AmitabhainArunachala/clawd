# Root-Level Python Scripts Analysis

## Summary

The root directory contains **11 loose Python scripts** totaling ~3,500+ lines. These are experimental, analysis, and validation scripts that accumulated during active research. Most should be organized into `scripts/` or `experiments/` subdirectories.

---

## Script Inventory

### 1. Gemma-Focused Experimental Scripts (7 files)

#### `gemma_behavioral_transfer.py`
- **Purpose**: Full behavioral transfer test for Gemma 2 9B using KV cache + persistent V_PROJ patching
- **Size**: ~300 lines
- **Dependencies**: `torch`, `transformers`
- **Usage Pattern**: One-shot experiment script
- **Recommendation**: Move to `experiments/gemma/behavioral_transfer.py`

#### `gemma_causal_batch_kv_only.py`
- **Purpose**: Causal validation batch - KV cache patching only (42 layers)
- **Size**: ~200 lines
- **Dependencies**: `torch`, `transformers`, `json`
- **Usage Pattern**: Batch experiment runner
- **Recommendation**: Move to `experiments/gemma/causal_batch_kv_only.py`

#### `gemma_full_validation_v2.py`
- **Purpose**: GOLD_STANDARD_RESEARCH_DIRECTIVE compliant full validation
  - n≥30 sample size
  - Random KV control
  - Wrong-layer control
  - Cohen's d with 95% CI
- **Size**: ~700 lines
- **Dependencies**: `torch`, `transformers`, `scipy`, `numpy`
- **Usage Pattern**: Comprehensive validation experiment
- **Recommendation**: Move to `experiments/gemma/full_validation_v2.py`

#### `gemma_kv_vs_vproj_comparison.py`
- **Purpose**: Compares KV-only vs KV+V_PROJ patching approaches
- **Size**: ~350 lines
- **Dependencies**: `torch`, `transformers`, `numpy`, `json`
- **Usage Pattern**: Comparative analysis experiment
- **Recommendation**: Move to `experiments/gemma/kv_vs_vproj_comparison.py`

#### `gemma_roman_empire_deep_dive.py`
- **Purpose**: Deep dive analysis of why Roman Empire prompt had successful R_V transfer
- **Size**: ~250 lines
- **Dependencies**: `torch`, `transformers`, `numpy`, `json`
- **Usage Pattern**: Diagnostic/analysis script
- **Recommendation**: Move to `experiments/gemma/roman_empire_analysis.py`

#### `gemma_rv_bifurcation_threshold.py`
- **Purpose**: Discover critical R_V threshold for recursive output mode
- **Size**: ~400 lines
- **Dependencies**: `torch`, `transformers`, `scipy`, `numpy`, `json`
- **Usage Pattern**: Threshold discovery experiment with 50+ prompts
- **Recommendation**: Move to `experiments/gemma/rv_bifurcation_threshold.py`

#### `gemma_rv_during_generation.py`
- **Purpose**: Track R_V trajectory token-by-token during generation
- **Size**: ~300 lines
- **Dependencies**: `torch`, `transformers`, `numpy`, `json`
- **Usage Pattern**: Real-time measurement during generation
- **Recommendation**: Move to `experiments/gemma/rv_trajectory_during_gen.py`

#### `gemma_rv_trajectory_source.py`
- **Purpose**: Per-token R_V trajectory from champion vs baseline prompts
- **Size**: ~280 lines
- **Dependencies**: `torch`, `transformers`, `numpy`, `json`
- **Usage Pattern**: Source prompt trajectory analysis
- **Recommendation**: Move to `experiments/gemma/rv_trajectory_source.py`

### 2. General Experiment Scripts (2 files)

#### `neurips_n300_robust_experiment.py`
- **Purpose**: NeurIPS-grade experiment with n=300 robust behavior transfer
  - Full controls (random, shuffled, wrong-layer)
  - Statistical analysis (t-tests, effect sizes, CIs)
  - Both R_V and behavior measurements
- **Size**: ~550 lines
- **Dependencies**: `torch`, `transformers`, `scipy`, `pandas`, `numpy`, `tqdm`
- **Imports**: `REUSABLE_PROMPT_BANK`, `massive_deep_analysis`
- **Usage Pattern**: Large-scale reproducible experiment
- **Recommendation**: Move to `experiments/validation/neurips_n300_robust.py`

#### `reproduce_results.py`
- **Purpose**: Entry point for reproducing "Geometric Contraction" results
- **Size**: ~80 lines
- **Dependencies**: `torch`, `argparse`, `pathlib`
- **Imports**: `src.pipelines.run_phase1_existence_proof`
- **Usage Pattern**: Standard battery runner
- **Recommendation**: Keep as `scripts/reproduce_results.py` (already structured)

### 3. Utility Scripts (1 file)

#### `openclaw_quickstart.py`
- **Purpose**: OpenClaw Pipeline 1 - Experiment results consolidation
  - Read-only data aggregation
  - Audit logging
  - Anomaly detection
- **Size**: ~350 lines
- **Dependencies**: `pandas`, `json`, `argparse`, `hashlib`, `pathlib`
- **Usage Pattern**: Data pipeline utility
- **Recommendation**: Move to `scripts/utils/openclaw_aggregator.py`

---

## Common Dependencies Across Scripts

### Core ML Stack
- `torch` - All scripts
- `transformers` (AutoModelForCausalLM, AutoTokenizer, DynamicCache) - All scripts

### Scientific Computing
- `numpy` - Most scripts
- `scipy.stats` - neurips_n300, gemma_full_validation_v2, gemma_rv_bifurcation_threshold

### Data/Utilities
- `json` - All scripts (output serialization)
- `pandas` - neurips_n300, openclaw_quickstart
- `tqdm` - neurips_n300
- `collections.Counter` - Several scripts

### Internal Imports
- `REUSABLE_PROMPT_BANK` - neurips_n300_robust_experiment
- `massive_deep_analysis.compute_pr` - neurips_n300_robust_experiment
- `src.pipelines` - reproduce_results.py

---

## Organization Recommendations

### Option A: Research-Oriented Structure (Recommended)

```
mech-interp-latent-lab-phase1/
├── experiments/
│   ├── gemma/           # All gemma_* scripts here
│   │   ├── behavioral_transfer.py
│   │   ├── causal_batch_kv_only.py
│   │   ├── full_validation_v2.py
│   │   ├── kv_vs_vproj_comparison.py
│   │   ├── roman_empire_analysis.py
│   │   ├── rv_bifurcation_threshold.py
│   │   ├── rv_trajectory_during_gen.py
│   │   └── rv_trajectory_source.py
│   ├── validation/
│   │   └── neurips_n300_robust.py
│   └── reproduce.py     # (merge with existing reproduce_results.py)
├── scripts/
│   ├── analysis/        # Data analysis scripts
│   ├── runners/         # Experiment runners
│   └── utils/
│       └── openclaw_aggregator.py
└── src/                 # Core library code
```

### Option B: Keep It Simple

```
mech-interp-latent-lab-phase1/
├── scripts/
│   ├── gemma/           # Move all gemma_* here
│   ├── validation/      # neurips_n300, full_validation
│   └── utils/
└── src/
```

---

## Key Usage Patterns

1. **One-shot experiments**: Most `gemma_*.py` scripts are designed to be run once to collect specific measurements

2. **Batch processing**: `gemma_causal_batch_kv_only.py`, `neurips_n300_robust_experiment.py` process multiple prompts

3. **Analysis/validation**: `gemma_full_validation_v2.py`, `gemma_rv_bifurcation_threshold.py` include statistical rigor

4. **Data consolidation**: `openclaw_quickstart.py` is a pipeline utility for post-experiment processing

---

## Files That Could Be Archived/Deleted

- **Duplicate functionality**: `gemma_rv_trajectory_source.py` and `gemma_rv_during_generation.py` have overlapping goals
- **One-off analysis**: `gemma_roman_empire_deep_dive.py` was likely a single diagnostic run
- **Superseded**: Earlier versions may exist; check git history for `gemma_full_validation.py` (v1)

---

## Dependencies Not in requirements.txt

Based on script analysis, the following should be verified in requirements:
- `transformers` (version with `DynamicCache` support)
- `accelerate` (for device_map="auto")
- `pandas` (for openclaw_quickstart, neurips_n300)
- `scipy` (for statistical tests)
- `tqdm` (for progress bars)
