# Config File Schema Analysis - Master Document

**Generated:** 2026-02-05
**Total Configs Analyzed:** 253 configs across gold/, canonical/, archive/, smoke_test/, phase3_bridge/

---

## 1. SCHEMA OVERVIEW

### 1.1 Root Schema Structure

All config files follow this root structure:

```json
{
  "experiment": "string (required) - Pipeline/experiment type identifier",
  "description": "string (optional) - Human-readable description",
  "run_name": "string (optional) - Specific run identifier",
  "seed": "number (optional) - Random seed, default 42",
  "model": "object (conditional) - Model configuration",
  "params": "object (required) - Experiment parameters",
  "pass_criteria": "object (optional) - Validation thresholds",
  "results": "object (optional) - Output configuration",
  "expected": "object (optional) - Expected outcomes",
  "meta": "object (optional) - Metadata",
  "notes": "string (optional) - Additional notes"
}
```

---

## 2. FIELD-LEVEL SCHEMA

### 2.1 Required Fields

| Field | Type | Description | Presence |
|-------|------|-------------|----------|
| `experiment` | string | Experiment/pipeline type | **100%** |
| `params` | object | Experiment parameters | **100%** |

### 2.2 Optional Fields

| Field | Type | Description | Usage Frequency |
|-------|------|-------------|-----------------|
| `description` | string | Human-readable description | ~40% |
| `run_name` | string | Run-specific identifier | ~60% |
| `seed` | number | Random seed (default: 42) | ~70% |
| `model` | object | Model configuration | ~65% |
| `pass_criteria` | object | Validation thresholds | ~15% (mainly gold/) |
| `results` | object | Output path configuration | ~70% |
| `expected` | object | Expected outcomes | ~10% (mainly gold/) |
| `meta` | object | Metadata (priority, status, dates) | ~5% |
| `notes` | string | Additional notes | ~5% |

---

## 3. SUB-SCHEMA DEFINITIONS

### 3.1 `model` Object Schema

```json
{
  "name": "string (required) - HuggingFace model ID",
  "device": "string (optional) - cuda/cpu/auto, default: cuda",
  "dtype": "string (optional) - Data type (auto/fp16/bf16/fp32)"
}
```

**INCONSISTENCY FOUND:** Some configs use `model` as a string directly in `params` instead of the `model` object at root level.

### 3.2 `params` Object Schema (Variable by Experiment Type)

**Common Params Across All Experiments:**

| Param | Type | Description | Frequency |
|-------|------|-------------|-----------|
| `model` | string | Model name (when no root `model` object) | ~35% |
| `n_pairs` | number | Number of prompt pairs | ~45% |
| `n_prompts` | number | Number of prompts | ~30% |
| `seed` | number | Random seed | ~30% |
| `early_layer` | number | Early layer index | ~50% |
| `late_layer` | number | Late layer index | ~40% |
| `window` / `window_size` | number | Context window size | ~40% |
| `max_new_tokens` | number | Generation limit | ~35% |
| `temperature` / `temperatures` | number/array | Sampling temperature(s) | ~25% |
| `layer` / `layers` | number/array | Target layer(s) | ~40% |

### 3.3 `results` Object Schema

```json
{
  "root": "string (required) - Root output directory",
  "phase": "string (required) - Phase/subdirectory path"
}
```

### 3.4 `pass_criteria` Object Schema (Gold Standard Only)

Highly variable by experiment. Common patterns:

```json
{
  "*_min": "number - Minimum threshold",
  "*_max": "number - Maximum threshold",
  "*_p_min": "number - Minimum p-value",
  "*_p_max": "number - Maximum p-value",
  "*_eq_*": "boolean - Equality checks"
}
```

### 3.5 `expected` Object Schema

```json
{
  "effect_direction": "string - Expected effect direction",
  "minimum_d": "number - Minimum effect size",
  "discovery_effect": "number - Observed effect from discovery",
  "tier_target": "string - Target validation tier"
}
```

### 3.6 `meta` Object Schema

```json
{
  "created": "string - ISO date",
  "priority": "number - Priority level (1-5)",
  "status": "string - ready_for_gpu/completed/pending"
}
```

---

## 4. EXPERIMENT TYPE SCHEMAS

### 4.1 `rv_l27_causal_validation` / `causality`

**Purpose:** Prove layer 27 is causal for geometric contraction

**Required Params:**
```json
{
  "model": "string",
  "early_layer": "number",
  "target_layer": "number",
  "wrong_layer": "number",
  "window": "number",
  "max_pairs": "number"
}
```

**Optional Params:**
```json
{
  "seed": "number",
  "max_length": "number",
  "pairing": {
    "recursive_groups": "array",
    "baseline_groups": "array"
  },
  "measure_target_after_wrong_patch": "boolean",
  "controls": "array" // [random, shuffled, wrong_layer, orthogonal]
}
```

**Related Files:**
- `gold/02_causality.json`
- `canonical/rv_causal_*.json` (5 configs)
- `gold/28_mixtral_causal_validation.json`

---

### 4.2 `confound_validation` / `existence`

**Purpose:** Verify R_V contraction exists with confound controls

**Required Params:**
```json
{
  "model": "string",
  "n_champions": "number",
  "n_length_matched": "number",
  "n_pseudo_recursive": "number",
  "early_layer": "number",
  "late_layer": "number",
  "window": "number",
  "seed": "number"
}
```

**Related Files:**
- `gold/01_existence.json`

---

### 4.3 `head_ablation_validation`

**Purpose:** Validate KV-head group effects with controls

**Required Params:**
```json
{
  "model": { "name": "string", "device": "string" },
  "params": {
    "n_recursive": "number",
    "n_baseline": "number",
    "target_layer": "number",
    "control_layer": "number",
    "target_kv_head": "number",
    "control_kv_head": "number",
    "early_layer": "number",
    "window": "number"
  }
}
```

**Related Files:**
- `gold/04_head_validation.json`

---

### 4.4 `mlp_sufficiency_test`

**Purpose:** Test MLP layer sufficiency for recursive computation

**Required Params:**
```json
{
  "layer": "number",
  "n_pairs": "number"
}
```

**Optional Params:**
```json
{
  "window_size": "number",
  "max_new_tokens": "number"
}
```

**Related Files:**
- `canonical/mlp_sufficiency_l0.json`
- `smoke_test/l0_patch.json`

---

### 4.5 `mlp_ablation_necessity_prompt_pass`

**Purpose:** Test MLP necessity via prompt passing

**Required Params:**
```json
{
  "layer": "number",
  "n_pairs": "number",
  "window_size": "number",
  "early_layer": "number",
  "late_layer": "number"
}
```

**Related Files:**
- `canonical/mlp_ablation_necessity_prompt_pass_l*.json` (6 configs)
- `canonical/gemma_2_9b/*prompt_pass*.json` (6 configs)

---

### 4.6 `multi_token_bridge`

**Purpose:** Bridge analysis between token patterns

**Required Params:**
```json
{
  "n_prompts": "number",
  "early_layer": "number",
  "late_layer": "number",
  "window": "number",
  "max_new_tokens": "number"
}
```

**Optional Params:**
```json
{
  "temperatures": "array",
  "recursive_groups": "array",
  "baseline_groups": "array"
}
```

**Related Files:**
- `canonical/multi_token_bridge_mistral.json`
- `phase3_bridge/gemma_2_9b/0*.json` (4 configs)

---

### 4.7 `steering`

**Purpose:** Vector steering experiments

**Required Params:**
```json
{
  "model": "string",
  "layer": "number",
  "alphas": "array",
  "n_prompts": "number"
}
```

**Related Files:**
- `gold/09_steering.json`
- `gold/09_steering_analysis.json`
- `archive/mlp_steering_sweep.json`

---

### 4.8 `surgical_sweep`

**Purpose:** Comprehensive surgical intervention sweep

**Required Params:**
```json
{
  "model": "string",
  "n_baseline_prompts": "number",
  "n_recursive_prompts": "number",
  "max_new_tokens": "number",
  "temperature": "number"
}
```

**Related Files:**
- `gold/15_surgical_sweep.json`

---

### 4.9 `path_patching_mechanism` / `layer_map`

**Purpose:** Map R_V trajectory across all layers

**Required Params:**
```json
{
  "model": "string",
  "max_pairs": "number",
  "n_repeats": "number",
  "windows": "array",
  "patch_layers": "array",
  "patch_types": "array",
  "early_layer": "number",
  "seed": "number"
}
```

**Related Files:**
- `gold/03_layer_map.json`

---

### 4.10 `p1_ablation` / `behavior_strict`

**Purpose:** P1 layer ablation tests

**Required Params:**
```json
{
  "model": "string",
  "device": "string",
  "n_baseline_prompts": "number",
  "max_new_tokens": "number"
}
```

**Optional Params:**
```json
{
  "use_champion_prompts": "boolean"
}
```

**Related Files:**
- `gold/05_behavior_strict.json`
- `gold/17_p1_ablation.json`
- `gold/22_clarity_champion_test.json`

---

### 4.11 `kv_mechanism`

**Purpose:** KV mechanism analysis

**Required Params:**
```json
{
  "model": "string",
  "n_pairs": "number",
  "early_layer": "number",
  "late_layer": "number",
  "window": "number",
  "kv_layer_range": "array"
}
```

**Related Files:**
- `gold/08_kv_mechanism.json`
- `kv_sweep_l24_l32.json`

---

### 4.12 `hysteresis_patching` / `hysteresis`

**Purpose:** Test hysteresis effects in patching

**Required Params:**
```json
{
  "model": { "name": "string", "device": "string" },
  "params": {
    "early_layer": "number",
    "measurement_layer": "number",
    "windows": "array",
    "push_layers": "array",
    "undo_layers": "array",
    "undo_kinds": "array",
    "max_pairs": "number",
    "n_repeats": "number"
  }
}
```

**Related Files:**
- `gold/07_hysteresis.json`
- `archive/hysteresis_patching.json`

---

### 4.13 `ioi_causal_test` / `geometry_behavior`

**Purpose:** Indirect Object Identification causal tests

**Required Params:**
```json
{
  "model": "string",
  "device": "string",
  "n_prompts": "number",
  "layer_idx": "number",
  "target_heads": "array",
  "max_new_tokens": "number"
}
```

**Related Files:**
- `gold/19_ioi_causal_test.json`
- `gold/21_geometry_behavior.json`

---

### 4.14 `phase0_metric_targets` / `phase0_minimal_pairs`

**Purpose:** Phase 0 metric validation

**Required Params:**
```json
{
  "model": { "name": "string", "device": "string" },
  "params": {
    "early_layer": "number",
    "window": "number",
    "max_length": "number"
  }
}
```

**Related Files:**
- `archive/phase0_metric_targets.json`
- `archive/phase0_minimal_pairs.json`

---

### 4.15 `random_direction_control`

**Purpose:** Random direction control experiments

**Required Params:**
```json
{
  "layer": "number",
  "alphas": "array",
  "n_random": "number",
  "n_pairs": "number"
}
```

**Related Files:**
- `canonical/random_direction_control_l4.json`

---

### 4.16 `combined_mlp_sufficiency_test`

**Purpose:** Test multiple MLP layers together

**Required Params:**
```json
{
  "layers": "array",
  "n_pairs": "number"
}
```

**Related Files:**
- `canonical/combined_mlp_sufficiency_l0_l1.json`

---

### 4.17 `vproj_patching_analysis`

**Purpose:** V-projection patching analysis

**Required Params:**
```json
{
  "n_pairs": "number",
  "patch_layer": "number"
}
```

**Related Files:**
- `vproj_patching_analysis.json`

---

### 4.18 `temporal_stability`

**Purpose:** Test temporal stability of effects

**Required Params:**
```json
{
  "model": "string",
  "n_prompts": "number",
  "max_steps": "number",
  "temperatures": "array",
  "early_layer": "number",
  "late_layer": "number",
  "window": "number"
}
```

**Related Files:**
- `gold/06_temporal_stability.json`

---

### 4.19 `circuit_discovery`

**Purpose:** Circuit discovery experiments

**Required Params:**
```json
{
  "model": "string",
  "n_pairs": "number"
}
```

**Related Files:**
- `gold/11_circuit_discovery.json`

---

### 4.20 `l27_head_analysis`

**Purpose:** Layer 27 head-specific analysis

**Required Params:**
```json
{
  "target_layer": "number",
  "critical_heads": "array",
  "control_head": "number",
  "window": "number"
}
```

**Related Files:**
- `archive/l27_head_analysis.json`

---

## 5. CRITICAL INCONSISTENCIES IDENTIFIED

### 5.1 Model Specification Inconsistency

**Problem:** Model is specified in two different ways:

**Pattern A (Root model object):**
```json
{
  "model": { "name": "mistralai/Mistral-7B-v0.1", "device": "cuda" },
  "params": { ... }
}
```

**Pattern B (params.model string):**
```json
{
  "params": {
    "model": "mistralai/Mistral-7B-v0.1",
    ...
  }
}
```

**Prevalence:**
- Pattern A: ~65% (canonical/, archive/)
- Pattern B: ~35% (gold/, smoke_test/)

**Recommendation:** Standardize on Pattern A (root model object) for better extensibility.

---

### 5.2 Window Size Parameter Name

**Problem:** Two different parameter names for the same concept:

- `window` (older configs)
- `window_size` (newer configs)

**Prevalence:**
- `window`: ~60%
- `window_size`: ~40%

**Recommendation:** Standardize on `window_size` for clarity.

---

### 5.3 Layer Specification Inconsistency

**Problem:** Layer targeting uses multiple patterns:

- `layer` (single layer)
- `layers` (array)
- `target_layer` + `control_layer`
- `early_layer` + `late_layer`
- `layer_idx`

**Recommendation:** Standardize naming convention:
- `target_layer` for primary layer
- `control_layer` for control/comparison
- `layers` array for multiple layers

---

### 5.4 Results Path Inconsistency

**Problem:** Phase naming conventions vary:

```json
"results": { "phase": "gold_standard" }
"results": { "phase": "phase1_mechanism" }
"results": { "phase": "phase1_cross_architecture" }
"results": { "phase": "phase3_bridge/gemma_2_9b/multi_token_correlation" }
```

**Recommendation:** Establish canonical phase names:
- `phase0_validation`
- `phase1_mechanism`
- `phase1_cross_architecture`
- `phase2_generalization`
- `phase3_bridge`
- `gold_standard`

---

### 5.5 Missing Required Fields

**Problem:** Some configs lack `run_name` making it hard to identify specific runs.

**Configs without run_name:**
- Most gold/ configs
- Some smoke_test/ configs

**Recommendation:** Make `run_name` required for all new configs.

---

### 5.6 Seed Inconsistency

**Problem:** Seeds vary across configs:

- Default: 42 (most common)
- Phase0 configs: 0
- Hysteresis: 7

**Recommendation:** Document seed choice rationale in config description.

---

## 6. CONFIG → PIPELINE → RESULT MAPPING

### 6.1 Gold Standard Pipelines (28 configs)

| Config | Pipeline | Result Location |
|--------|----------|-----------------|
| `01_existence.json` | confound_validation | results/gold_standard/ |
| `02_causality.json` | rv_l27_causal_validation | results/gold_standard/ |
| `03_layer_map.json` | path_patching_mechanism | results/gold_standard/ |
| `04_head_validation.json` | head_ablation_validation | results/gold_standard/ |
| `05_behavior_strict.json` | behavior_strict | results/gold_standard/ |
| `06_temporal_stability.json` | temporal_stability | results/gold_standard/ |
| `07_hysteresis.json` | hysteresis | results/gold_standard/ |
| `08_kv_mechanism.json` | kv_mechanism | results/gold_standard/ |
| `09_steering.json` | steering | results/gold_standard/ |
| `09_steering_analysis.json` | steering | results/gold_standard/ |
| `09_layer_matrix.json` | layer_matrix | results/gold_standard/ |
| `09_extended_alpha.json` | extended_alpha | results/gold_standard/ |
| `11_circuit_discovery.json` | circuit_discovery | results/gold_standard/ |
| `11_head_specific_intervention.json` | head_specific_intervention | results/gold_standard/ |
| `12_extended_context_steering.json` | extended_context_steering | results/gold_standard/ |
| `13_steering_control.json` | steering_control | results/gold_standard/ |
| `14_triple_system_intervention.json` | triple_system_intervention | results/gold_standard/ |
| `15_surgical_sweep.json` | surgical_sweep | results/gold_standard/ |
| `16_verification_sweep.json` | verification_sweep | results/gold_standard/ |
| `17_p1_ablation.json` | p1_ablation | results/gold_standard/ |
| `18_retrocompute_mode_score.json` | retrocompute_mode_score | results/gold_standard/ |
| `19_ioi_causal_test.json` | ioi_causal_test | results/gold_standard/ |
| `20_importance_sweep.json` | importance_sweep | results/gold_standard/ |
| `21_geometry_behavior.json` | geometry_behavior | results/ioi_causal_evidence/ |
| `22_clarity_champion_test.json` | p1_ablation | results/gold_standard/ |
| `23_clarity_expanded_test.json` | clarity_expanded | results/gold_standard/ |
| `24_source_isolation.json` | source_isolation | results/gold_standard/ |
| `25_layer_sweep.json` | layer_sweep | results/gold_standard/ |
| `25_layer_sweep_small.json` | layer_sweep | results/gold_standard/ |
| `26_vproj_sweep.json` | vproj_sweep | results/gold_standard/ |
| `27_kitchen_sink.json` | kitchen_sink | results/gold_standard/ |
| `28_mixtral_causal_validation.json` | rv_causal_validation | results/canonical/ |

---

### 6.2 Canonical Pipelines (40+ configs)

| Config Pattern | Pipeline | Result Location |
|----------------|----------|-----------------|
| `rv_causal_*.json` | rv_l27_causal_validation | results/phase1_cross_architecture/ |
| `mlp_sufficiency_l*.json` | mlp_sufficiency_test | results/phase1_mechanism/ |
| `mlp_ablation_necessity_*.json` | mlp_ablation_necessity_prompt_pass | results/phase1_mechanism/ |
| `multi_token_bridge_*.json` | multi_token_bridge | results/phase1_cross_architecture/ |
| `random_direction_control_*.json` | random_direction_control | results/phase1_mechanism/ |
| `combined_mlp_sufficiency_*.json` | combined_mlp_sufficiency_test | results/phase1_mechanism/ |

---

### 6.3 Phase3 Bridge Pipelines (Gemma)

| Config | Pipeline | Result Location |
|--------|----------|-----------------|
| `01_multi_token_bridge.json` | multi_token_bridge | results/phase3_bridge/gemma_2_9b/multi_token_correlation/ |
| `02_multi_token_bridge_v2.json` | multi_token_bridge | results/phase3_bridge/gemma_2_9b/multi_token_correlation_v2/ |
| `03_multi_token_bridge_v2_seed123.json` | multi_token_bridge | results/phase3_bridge/gemma_2_9b/multi_token_correlation_v2/ |
| `04_multi_token_bridge_v3_t0_long.json` | multi_token_bridge | results/phase3_bridge/gemma_2_9b/multi_token_correlation_v3/ |

---

## 7. RECOMMENDED SCHEMA STANDARD

### 7.1 Standard Config Template

```json
{
  "experiment": "experiment_type",
  "description": "Human-readable description of this config's purpose",
  "run_name": "unique_run_identifier",
  "seed": 42,
  "model": {
    "name": "huggingface/model-id",
    "device": "cuda",
    "dtype": "auto"
  },
  "params": {
    "n_pairs": 30,
    "early_layer": 5,
    "target_layer": 27,
    "control_layer": 21,
    "window_size": 16,
    "max_length": 512,
    "max_new_tokens": 200,
    "temperature": 0.7
  },
  "pass_criteria": {
    "effect_size_min": 0.5,
    "p_value_max": 0.001
  },
  "results": {
    "root": "results",
    "phase": "phase_name"
  },
  "expected": {
    "effect_direction": "negative",
    "minimum_d": 0.5,
    "tier_target": "TIER_1_IRONCLAD"
  },
  "meta": {
    "created": "2026-02-05",
    "priority": 1,
    "status": "ready_for_gpu"
  },
  "notes": "Additional context or warnings"
}
```

### 7.2 Required vs Optional Fields Summary

| Category | Required | Optional |
|----------|----------|----------|
| **Root** | experiment, params | description, run_name, seed |
| **Model** | name | device, dtype |
| **Params** | Varies by experiment type | Varies by experiment type |
| **Results** | root, phase | - |
| **Pass Criteria** | - | All fields |
| **Expected** | - | All fields |
| **Meta** | - | All fields |

---

## 8. APPENDIX: EXPERIMENT TYPE ENUM

Complete list of experiment types found across all configs:

1. `confound_validation`
2. `rv_l27_causal_validation`
3. `path_patching_mechanism`
4. `head_ablation_validation`
5. `behavior_strict`
6. `temporal_stability`
7. `hysteresis`
8. `kv_mechanism`
9. `steering`
10. `circuit_discovery`
11. `ioi_causal_test`
12. `geometry_behavior`
13. `p1_ablation`
14. `surgical_sweep`
15. `mlp_sufficiency_test`
16. `mlp_ablation_necessity_prompt_pass`
17. `multi_token_bridge`
18. `random_direction_control`
19. `combined_mlp_sufficiency_test`
20. `vproj_patching_analysis`
21. `phase0_metric_targets`
22. `phase0_minimal_pairs`
23. `l27_head_analysis`
24. `hysteresis_patching`
25. `verification_sweep`
26. `importance_sweep`
27. `layer_sweep`
28. `vproj_sweep`
29. `source_isolation`
30. `steering_control`
31. `extended_context_steering`
32. `triple_system_intervention`
33. `head_specific_intervention`
34. `layer_matrix`
35. `extended_alpha`
36. `clarity_expanded`
37. `kitchen_sink`
38. `retrocompute_mode_score`
39. `causality`
40. `existence`
41. `rv_causal_validation`

---

## 9. SUMMARY

### Key Findings:

1. **253 total configs** across 5 main directories
2. **40+ distinct experiment types** identified
3. **6 critical inconsistencies** requiring standardization:
   - Model specification pattern
   - Window size parameter name
   - Layer specification naming
   - Results phase naming
   - Missing run_name fields
   - Seed value variations

4. **Most configs are valid JSON** with consistent structure
5. **Gold configs** tend to have more complete `pass_criteria` and `expected` sections
6. **Canonical configs** favor the root `model` object pattern
7. **Archive configs** show evolution of schema over time

### Recommendations:

1. Create JSON Schema validation file for CI/CD
2. Standardize on Pattern A (root model object)
3. Standardize on `window_size` parameter name
4. Document experiment type enum
5. Make `run_name` required for new configs
6. Establish canonical phase names
7. Create migration script for existing configs
