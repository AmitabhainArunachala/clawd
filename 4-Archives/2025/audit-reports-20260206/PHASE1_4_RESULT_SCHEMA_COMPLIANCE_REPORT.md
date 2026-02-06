# Result File Schema Compliance Report
## Phase 1.4: RESULT FILE STRUCTURE MAPPING

**Generated:** 2026-02-05

---

## Executive Summary

Total files analyzed across `~/mech-interp-latent-lab-phase1/results/`:
- **703** JSON files
- **77** CSV files
- **97** JSONL files
- **173** TXT files
- **224** Markdown files
- **81** error.txt files

---

## Directory Structure Overview

### Major Result Directories

```
results/
├── archive/
│   ├── superseded/          # Old/outdated runs
│   └── failed/              # Failed runs with error.txt
├── canonical/               # Validated, canonical results
│   ├── confound_validation/
│   ├── session_2/
│   └── session_2_complete/
├── discovery/               # Discovery-phase experiments
│   ├── behavioral_grounding/
│   ├── path_patching/
│   ├── phase0_validation/
│   └── steering/
├── phase0_metric_validation/
├── phase1_cross_architecture/
├── phase2_generalization/
├── phase3_bridge/
└── [other experiment dirs]
```

---

## Identified Result File Types

### 1. `summary.json` (Primary Results Contract)
**Present in:** ~125 run directories

#### Standard Contract Fields (Expected):
```json
{
  "experiment": "string",           // REQUIRED - Experiment type
  "model_name": "string",           // REQUIRED - Model identifier
  "params": {                       // REQUIRED - Run parameters
    "early_layer": int,
    "late_layer": int,
    "window": int,
    ...
  },
  "artifacts": {                    // RECOMMENDED - Output file paths
    "csv": "path/to/file.csv",
    "jsonl": "path/to/file.jsonl",
    "confound_results_csv": "path/to/file.csv"
  },
  "device": "cuda",                 // OPTIONAL - Hardware info
  "n_rows" | "n_pairs" | "n_prompts": int  // Sample count
}
```

#### Variant 1: Confound Validation Schema
```json
{
  "mean_rv": {
    "champions": float,
    "length_matched": float,
    "pseudo_recursive": float
  },
  "n_champions": int,
  "n_length_matched": int,
  "n_pseudo_recursive": int,
  "ttest": {
    "champions_vs_length_matched": { "p": float, "t": float },
    "champions_vs_pseudo_recursive": { "p": float, "t": float },
    "length_matched_vs_pseudo_recursive": { "p": float, "t": float }
  },
  "corr_token_count_vs_rv": { "p": float, "r": float }
}
```

#### Variant 2: Phase0 Metric Targets Schema
```json
{
  "by_group": {
    "baselines": { "rv_hidden": {...}, "rv_vproj": {...}, "pr_h_late": {...}, "pr_v_late": {...} },
    "confounds": { ... },
    "dose_response": { ... }
  },
  "correlations": {
    "pearson_pr_v_late_vs_pr_h_late": float,
    "pearson_rv_vproj_vs_rv_hidden": float
  },
  "weight_pr": {
    "pr_w_early": float,
    "pr_w_late": float,
    "rv_weight": float
  }
}
```

#### Variant 3: Path Patching Schema
```json
{
  "by_component": {
    "v": { "none": {...}, "opposite": {...}, "random": {...}, "recursive": {...} },
    "o": { ... },
    "resid": { ... }
  },
  "n_rows": int
}
```

#### Variant 4: Steering Schema
```json
{
  "alphas": [float],
  "conditions": {
    "alpha_X.X": {
      "collapse_rate": float,
      "mean_diversity": float,
      "mean_score": float,
      "pass_rate": float
    }
  },
  "layer": int,
  "steering_vector_path": "string"
}
```

#### Variant 5: Phase3 Bridge (Multi-Token) Schema
```json
{
  "analysis": {
    "temp_0.0": {
      "group_rv_means": {...},
      "h1_significant": bool,
      "h1_spearman_p": float,
      "h1_spearman_r": float,
      "h2_significant": bool,
      "h2_p_value": float,
      "h2_t_stat": float,
      "h3_significant": bool,
      "h3_point_biserial_p": float
    }
  },
  "baseline_groups": [string],
  "recursive_groups": [string],
  "schema_version": "metrics_summary_v1",
  "timestamp": "YYYYMMDD_HHMMSS",
  "version": "string"
}
```

---

### 2. `config.json` (Run Configuration)
**Present in:** 284 run directories

#### Standard Contract Fields:
```json
{
  "experiment": "string",           // REQUIRED
  "model": {
    "name": "string",               // REQUIRED
    "device": "cuda"                // OPTIONAL
  },
  "params": {                       // REQUIRED
    "early_layer": int,
    "late_layer": int,
    "window": int,
    ...
  },
  "results": {                      // RECOMMENDED
    "phase": "string",
    "root": "results"
  },
  "run_name": "string",             // RECOMMENDED
  "seed": int                       // RECOMMENDED
}
```

**Note:** Config structure varies by experiment type but `experiment` and `model.name` are universal.

---

### 3. `metadata.json` (Run Metadata)
**Present in:** 47 run directories

#### Standard Contract Fields:
```json
{
  "behavior_metric": "string",      // e.g., "rv", "mode_score_m"
  "eval_window": int,
  "git_commit": "string",
  "intervention_scope": "string",
  "model_id": "string",
  "n_pairs": int | null,
  "prompt_bank_version": "string",  // Hex hash
  "seed": int
}
```

**VIOLATION FOUND:** No `hardware_info` field present in any metadata files.

---

### 4. `extended_stats.json` (Detailed Statistics)
**Present in:** ~15 run directories (confound_validation only)

#### Standard Contract Fields:
```json
{
  "effects": {
    "comparison_name": {
      "cohens_d": float,
      "mean_a": float,
      "mean_b": float,
      "mean_diff": float,
      "mean_diff_95ci": { "hi": float, "lo": float },
      "p": float,
      "t": float
    }
  },
  "model_name": "string",
  "run_dir": "string"
}
```

---

### 5. CSV Files
**Present in:** 77 files

#### Common Patterns:
- `{experiment}_results.csv` - Main results table
- `{experiment}_summary.csv` - Summary statistics
- `confound_results.csv` - Confound validation data
- `rv_behavioral_correlation.csv` - Phase3 bridge correlation data
- `run_index.csv` - Central run registry

#### CSV Schema Contracts:

**confound_results.csv:**
```csv
prompt_id,prompt_type,family,text,token_count,rv_l27,matched_to
```

**behavioral_grounding_summary.csv:**
```csv
condition,prompt_id,family,text,rv_l27,gen_token_count,repeat_4gram_frac,self_ref_rate,unique_word_ratio
```

**path_patching_mechanism.csv:**
```csv
pair_id,baseline_prompt,recursive_prompt,component,condition,rv_l27
```

---

### 6. `error.txt` (Failure Records)
**Present in:** 81 files (mostly in `archive/failed/`)

Common error types:
- `ValueError: Fast download using 'hf_transfer'...` - Missing hf_transfer package
- CUDA/Out of memory errors
- Config validation errors

---

### 7. `prompt_bank_version.txt` / `prompt_bank_version.json`
**Present in:** ~200+ files

Contains a single line with hex hash of prompt bank version (e.g., `75e7c1b8dcebc24e`)

---

### 8. `report.md`
**Present in:** 190 files

Human-readable narrative reports summarizing experiment results.

---

### 9. JSONL Files
**Present in:** 97 files

Line-delimited JSON for large result sets (e.g., `behavioral_grounding.jsonl`)

---

### 10. `RUN_INDEX.jsonl`
**Present in:** 1 file (central registry)

JSON Lines format with comprehensive run metadata including:
- `experiment`, `model_id`, `timestamp`, `run_dir`
- Statistical results: `rv_d`, `rv_p`, `rv_delta`
- `prompt_bank_version`, `git_commit`, `schema_version`

---

## Schema Contract Violations Found

### CRITICAL VIOLATIONS

| Violation | Count | Location | Impact |
|-----------|-------|----------|--------|
| **Missing hardware_info.json** | ALL RUNS | Every run directory | Cannot determine compute environment |
| **Missing CSV in failed runs** | 81 | archive/failed/ | Expected CSV artifacts missing (run failed) |
| **Missing summary.json** | ~200+ | Various | Results not finalized |

### MAJOR VIOLATIONS

| Violation | Count | Location | Details |
|-----------|-------|----------|---------|
| **Inconsistent model field naming** | 50+ | Various | `model_name` vs `model.name` vs `model_id` |
| **Inconsistent timestamp formats** | 30+ | Various | `timestamp` field missing or different formats |
| **Missing schema_version** | 100+ | Various | No version tracking for result schema |
| **Missing artifacts section** | 40+ | Various | summary.json lacks artifacts field |
| **Inconsistent statistical field names** | 20+ | Various | `rv_p` vs `rv_pvalue` vs `p_value` |

### MINOR VIOLATIONS

| Violation | Count | Details |
|-----------|-------|---------|
| **Missing device field** | 100+ | No GPU/CPU info in summary |
| **Missing git_commit** | 200+ | No code version tracking |
| **Inconsistent n_* naming** | 30+ | `n_pairs`, `n_prompts`, `n_rows`, `n_total` |
| **Missing run_name** | 50+ | config.json lacks run identification |
| **Prompt bank version mismatch** | Unknown | Some runs use different prompt bank versions |

---

## Schema Compliance by Directory

### FULLY COMPLIANT (Schema v1)
- `canonical/confound_validation/20251216_060911_confound_validation/`
- `canonical/c2_measurement_suite/*` (selected runs)
- `phase3_bridge/gemma_2_9b/multi_token_correlation_v2/` (newer runs)

### PARTIALLY COMPLIANT
- `discovery/*` - Mix of old and new schemas
- `phase0_metric_validation/runs/` - Standard config+summary pattern
- `confound_validation/runs/` - Has summary+config but inconsistent

### NON-COMPLIANT / LEGACY
- `archive/superseded/*` - Old schema versions
- `archive/failed/*` - Incomplete, error state
- `canonical/session_2/*` - Simplified result structure

---

## Recommended Schema Contract (v2)

### Required Files Per Run Directory
```
{timestamp}_{experiment}_{run_name}/
├── config.json           # REQUIRED - Run configuration
├── summary.json          # REQUIRED - Primary results
├── metadata.json         # REQUIRED - Run metadata
├── hardware_info.json    # REQUIRED - System info (NEW)
├── results.csv           # REQUIRED - Tabular results
├── prompt_bank_version.txt  # REQUIRED - Prompt bank hash
└── report.md             # RECOMMENDED - Human summary
```

### Standardized Field Names
```
model -> model_id (string)
n_* -> n_samples (int)
p_value -> p_value (consistently, not p or pvalue)
r -> correlation_r (or spearman_r, pearson_r)
```

### Metadata Schema
```json
{
  "run_id": "uuid",
  "experiment": "string",
  "model_id": "string",
  "timestamp": "YYYYMMDD_HHMMSS",
  "schema_version": "2.0.0",
  "prompt_bank_version": "hash",
  "git_commit": "hash",
  "hardware": {
    "gpu": "string",
    "cuda_version": "string",
    "cpu": "string"
  }
}
```

---

## Summary

**Total Run Directories:** ~400
- **Complete runs (summary+config):** ~125 (31%)
- **Failed runs:** 81 (20%)
- **Missing standard files:** ~194 (49%)

**Most Critical Issues:**
1. No hardware_info.json anywhere - compute environment unknown
2. Inconsistent field naming breaks automated analysis
3. Missing schema versioning makes backward compatibility difficult
4. 20% failure rate indicates pipeline instability
