# Gold Standard Configs Analysis

## Overview

**Location:** `~/mech-interp-latent-lab-phase1/configs/gold/`

**Total Config Files:** 29 (numbered 01-28 with some duplicate numbering)

## Config Inventory

| # | Filename | Experiment Name | Runnable | Tier | Description |
|---|----------|-----------------|----------|------|-------------|
| 01 | `01_existence.json` | `confound_validation` | ✅ YES | CANONICAL | Pipeline 1: Verify R_V contraction exists with confound controls |
| 02 | `02_causality.json` | `rv_l27_causal_validation` | ✅ YES | CANONICAL | Pipeline 2: Prove L27 is causal for geometric contraction |
| 03 | `03_layer_map.json` | `path_patching_mechanism` | ✅ YES | DISCOVERY | Pipeline 3: Map R_V trajectory across all layers |
| 04 | `04_head_validation.json` | `head_ablation_validation` | ✅ YES | CANONICAL | Pipeline 4: Validate KV-head group effects with controls |
| 05 | `05_behavior_strict.json` | `behavior_strict` | ✅ YES | ARCHIVE | Behavioral strictness testing |
| 06 | `06_temporal_stability.json` | `temporal_stability` | ✅ YES | DISCOVERY | Temporal stability analysis |
| 07 | `07_hysteresis.json` | `hysteresis` | ✅ YES | DISCOVERY | Hysteresis testing |
| 08 | `08_kv_mechanism.json` | `kv_mechanism` | ✅ YES | DISCOVERY | KV mechanism analysis |
| 09a | `09_steering.json` | `steering` | ✅ YES | ARCHIVE | Steering experiments |
| 09b | `09_extended_alpha.json` | `steering` | ✅ YES | ARCHIVE | Extended alpha steering |
| 09c | `09_layer_matrix.json` | `steering_layer_matrix` | ✅ YES | ARCHIVE | Layer matrix steering |
| 09d | `09_steering_analysis.json` | `steering_analysis` | ✅ YES | ARCHIVE | Steering analysis |
| 10 | `10_minimal_recursive_intervention.json` | `minimal_recursive_intervention` | ✅ YES | ARCHIVE | Minimal recursive intervention |
| 11a | `11_circuit_discovery.json` | `circuit_discovery` | ✅ YES | ARCHIVE | Circuit discovery |
| 11b | `11_head_specific_intervention.json` | `sprint_head_specific_steering` | ✅ YES | ARCHIVE | Head-specific steering sprint |
| 12 | `12_extended_context_steering.json` | `extended_context_steering` | ✅ YES | ARCHIVE | Extended context steering |
| 13 | `13_steering_control.json` | `steering_control` | ✅ YES | ARCHIVE | Steering control experiments |
| 14 | `14_triple_system_intervention.json` | `triple_system_intervention` | ✅ YES | ARCHIVE | Triple system intervention |
| 15 | `15_surgical_sweep.json` | `surgical_sweep` | ✅ YES | ARCHIVE | Surgical sweep experiments |
| 16 | `16_verification_sweep.json` | `verification_sweep` | ✅ YES | ARCHIVE | Verification sweep |
| 17 | `17_p1_ablation.json` | `p1_ablation` | ✅ YES | ARCHIVE | P1 ablation study |
| 18 | `18_retrocompute_mode_score.json` | `retrocompute_mode_score` | ✅ YES | ARCHIVE | Retrocompute mode score |
| 19 | `19_ioi_causal_test.json` | `ioi_causal_test` | ✅ YES | ARCHIVE | IOI causal testing |
| 20 | `20_importance_sweep.json` | `importance_sweep` | ✅ YES | ARCHIVE | Importance sweep analysis |
| 21 | `21_geometry_behavior.json` | `geometry_behavior` | ✅ YES | ARCHIVE | Geometry behavior study |
| 22 | `22_clarity_champion_test.json` | `p1_ablation` | ✅ YES | ARCHIVE | Clarity champion test (variant) |
| 23 | `23_clarity_expanded_test.json` | `p1_ablation` | ✅ YES | ARCHIVE | Clarity expanded test (variant) |
| 24 | `24_source_isolation.json` | `source_isolation_diagnostic` | ✅ YES | ARCHIVE | Source isolation diagnostic |
| 25a | `25_layer_sweep.json` | `layer_sweep` | ✅ YES | DISCOVERY | Layer sweep (full) |
| 25b | `25_layer_sweep_small.json` | `layer_sweep` | ✅ YES | DISCOVERY | Layer sweep (small) |
| 26 | `26_vproj_sweep.json` | `layer_sweep` | ✅ YES | DISCOVERY | V-projection sweep (uses layer_sweep) |
| 27 | `27_kitchen_sink.json` | `kitchen_sink` | ✅ YES | ARCHIVE | Kitchen sink test |
| 28 | `28_mixtral_causal_validation.json` | `rv_causal_validation` | ⚠️ UNKNOWN | - | Mixtral 8x7B R_V causal validation |

## Runnable Status Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Runnable** | 28 | Have registered experiment handlers in `src/pipelines/registry.py` |
| **Unknown** | 1 | `28_mixtral_causal_validation.json` - experiment name `rv_causal_validation` not in registry |

## Config Schema Analysis

### Common Schema Fields

All configs share a common base structure:

```json
{
  "experiment": "string",        // Required: maps to registry handler
  "description?": "string",      // Optional: human-readable description
  "params": {                     // Required: experiment parameters
    "model": "string",           // Required: model name
    "device?": "string",         // Optional: cuda/auto/cpu
    // ... experiment-specific params
  },
  "pass_criteria?": { ... },     // Optional: validation criteria
  "results?": {                   // Optional: result output config
    "root": "string",
    "phase": "string"
  },
  "expected?": { ... },          // Optional: expected outcomes
  "meta?": { ... }               // Optional: metadata
}
```

### Schema Variants by Tier

#### CANONICAL Tier (Pipelines 1-4)
```json
{
  "experiment": "<canonical_name>",
  "description": "Gold Standard Pipeline N: ...",
  "params": {
    "model": "mistralai/Mistral-7B-v0.1",
    "seed": 42,
    // Experiment-specific params
  },
  "pass_criteria": { ... },      // Validation thresholds
  "results": { "root": "results", "phase": "gold_standard" }
}
```

#### DISCOVERY Tier
```json
{
  "experiment": "<discovery_name>",
  "params": {
    "model": "mistralai/Mistral-7B-v0.1",
    // Feature-specific params
  }
}
```

#### ARCHIVE Tier
```json
{
  "experiment": "<archive_name>",
  "params": {
    "model": "mistralai/Mistral-7B-v0.1",
    "n_prompts": N,
    "max_new_tokens": N
  }
}
```

## Config Hierarchy & Relationships

### Pipeline Dependencies (Sequential)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        GOLD STANDARD PIPELINES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Pipeline 1: Existence (01)                                                  │
│  ├── Validates: R_V contraction exists with confound controls                │
│  └── Output: Baseline for causality testing                                  │
│       │                                                                      │
│       ▼                                                                      │
│  Pipeline 2: Causality (02)                                                  │
│  ├── Validates: L27 is causal for geometric contraction                      │
│  ├── Depends on: Pipeline 1 (knows R_V exists)                               │
│  └── Output: Confirmed causal layer                                          │
│       │                                                                      │
│       ▼                                                                      │
│  Pipeline 3: Layer Map (03)                                                  │
│  ├── Maps: R_V trajectory across all layers                                  │
│  ├── Depends on: Pipeline 2 (knows L27 is causal)                            │
│  └── Output: Layer-wise mechanism map                                        │
│       │                                                                      │
│       ▼                                                                      │
│  Pipeline 4: Head Validation (04)                                            │
│  ├── Validates: KV-head group effects with controls                          │
│  ├── Depends on: Pipeline 3 (knows layer map)                                │
│  └── Output: Head-specific causal validation                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Experiment Group Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXPERIMENT GROUPS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEERING GROUP (09a-d, 12, 13)                                              │
│  ├── 09_steering.json           - Base steering                              │
│  ├── 09_extended_alpha.json     - Extended alpha range                       │
│  ├── 09_layer_matrix.json       - Layer matrix analysis                      │
│  ├── 09_steering_analysis.json  - Detailed analysis                          │
│  ├── 12_extended_context_steering.json - Long context                        │
│  └── 13_steering_control.json   - Control experiments                        │
│                                                                              │
│  ABLATION GROUP (17, 22, 23)                                                 │
│  ├── 17_p1_ablation.json        - Base P1 ablation                           │
│  ├── 22_clarity_champion_test.json - Champion variant                        │
│  └── 23_clarity_expanded_test.json - Expanded variant                        │
│                                                                              │
│  LAYER SWEEP GROUP (25a, 25b, 26)                                            │
│  ├── 25_layer_sweep.json        - Full layer sweep (8-27)                    │
│  ├── 25_layer_sweep_small.json  - Small sweep (20-27)                        │
│  └── 26_vproj_sweep.json        - V-projection sweep (16-30)                 │
│                                                                              │
│  CLARITY/VERIFICATION GROUP (16, 18-21)                                      │
│  ├── 16_verification_sweep.json - Multi-config verification                  │
│  ├── 18_retrocompute_mode_score.json - Mode scoring                          │
│  ├── 19_ioi_causal_test.json    - IOI-specific testing                       │
│  ├── 20_importance_sweep.json   - Head importance analysis                   │
│  └── 21_geometry_behavior.json  - Geometry-behavior link                     │
│                                                                              │
│  SINGLETONS                                                                    │
│  ├── 05_behavior_strict.json    - Behavioral strictness                      │
│  ├── 06_temporal_stability.json - Temporal analysis                          │
│  ├── 07_hysteresis.json         - Hysteresis testing                         │
│  ├── 08_kv_mechanism.json       - KV mechanism                               │
│  ├── 10_minimal_recursive_intervention.json                                  │
│  ├── 11_circuit_discovery.json  - Circuit discovery                          │
│  ├── 11_head_specific_intervention.json - Head steering                      │
│  ├── 14_triple_system_intervention.json                                      │
│  ├── 15_surgical_sweep.json     - Surgical sweep                             │
│  ├── 24_source_isolation.json   - Source isolation                           │
│  ├── 27_kitchen_sink.json       - Kitchen sink                               │
│  └── 28_mixtral_causal_validation.json - Mixtral validation                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Model Distribution

| Model | Configs Using It |
|-------|------------------|
| `mistralai/Mistral-7B-v0.1` | 01-16, 22-27 |
| `mistralai/Mistral-7B-Instruct-v0.2` | 16, 17 |
| `mistralai/Mistral-7B-Instruct-v0.3` | 18-21 |
| `mistralai/Mixtral-8x7B-v0.1` | 28 |

## Registry Mapping

### Full Registry Status

```python
# From src/pipelines/registry.py - 44 registered experiments

CANONICAL (8):
- rv_l27_causal_validation          ← 02_causality.json
- confound_validation               ← 01_existence.json
- random_direction_control          ← (no gold config)
- mlp_ablation_necessity_prompt_pass ← (no gold config)
- mlp_sufficiency_test              ← (no gold config)
- combined_mlp_sufficiency_test     ← (no gold config)
- head_ablation_validation          ← 04_head_validation.json
- multi_token_bridge                ← (no gold config)

DISCOVERY (12):
- behavioral_grounding              ← (no gold config)
- behavioral_grounding_batch        ← (no gold config)
- path_patching_mechanism           ← 03_layer_map.json
- temporal_stability                ← 06_temporal_stability.json
- hysteresis                        ← 07_hysteresis.json
- kv_mechanism                      ← 08_kv_mechanism.json
- layer_sweep                       ← 25_layer_sweep.json, 25_layer_sweep_small.json, 26_vproj_sweep.json
- logit_lens_analysis               ← (no gold config)
- vproj_patching_analysis           ← (no gold config)
- mlp_vproj_combined_sufficiency_test ← (no gold config)
- c2_rv_measurement                 ← (no gold config)
- gemma_full_circuit_analysis       ← (no gold config)
- gemma_head_decomposition          ← (no gold config)

ARCHIVE (24):
- phase1_existence                  ← (superseded by confound_validation)
- phase0_minimal_pairs              ← (no gold config)
- phase0_metric_targets             ← (no gold config)
- l27_head_analysis                 ← (no gold config)
- kv_sufficiency_matrix             ← (no gold config)
- behavioral_grounding              ← (no gold config)
- behavior_strict                   ← 05_behavior_strict.json
- steering                          ← 09_steering.json, 09_extended_alpha.json
- steering_analysis                 ← 09_steering_analysis.json
- steering_layer_matrix             ← 09_layer_matrix.json
- minimal_recursive_intervention    ← 10_minimal_recursive_intervention.json
- extended_context_steering         ← 12_extended_context_steering.json
- steering_control                  ← 13_steering_control.json
- triple_system_intervention        ← 14_triple_system_intervention.json
- surgical_sweep                    ← 15_surgical_sweep.json
- verification_sweep                ← 16_verification_sweep.json
- p1_ablation                       ← 17_p1_ablation.json, 22_clarity_champion_test.json, 23_clarity_expanded_test.json
- sprint_head_specific_steering     ← 11_head_specific_intervention.json
- retrocompute_mode_score           ← 18_retrocompute_mode_score.json
- ioi_causal_test                   ← 19_ioi_causal_test.json
- importance_sweep                  ← 20_importance_sweep.json
- geometry_behavior                 ← 21_geometry_behavior.json
- source_isolation_diagnostic       ← 24_source_isolation.json
- kitchen_sink                      ← 27_kitchen_sink.json
- circuit_discovery                 ← 11_circuit_discovery.json
- mlp_steering_sweep                ← (no gold config)
- position_specific_ablation        ← (no gold config)
```

## Execution Commands

```bash
# Run any gold config using the canonical runner:
python -m src.pipelines.run --config configs/gold/01_existence.json --results_root results

# Run with custom results root:
python -m src.pipelines.run --config configs/gold/02_causality.json --results_root results/phase2
```

## Key Findings

1. **28 of 29 configs are runnable** via the canonical runner
2. **Config 28 (Mixtral)** uses experiment name `rv_causal_validation` which is NOT in the registry - needs registration or config update
3. **Duplicate numbering exists:**
   - 09: 4 configs (steering variants)
   - 11: 2 configs (circuit + head-specific)
   - 25: 3 configs (layer sweep variants)
   - 17/22/23: All use `p1_ablation` experiment (3 variants)
4. **4 Canonical pipelines** have gold configs (01-04)
5. **3 Discovery experiments** have gold configs (03, 06-08, 25-26)
6. **22 Archive experiments** have gold configs

## Recommendations

1. **Fix config 28:** Register `rv_causal_validation` experiment or rename to existing `rv_l27_causal_validation`
2. **Consolidate duplicates:** Consider merging variant configs or using clearer naming
3. **Add missing canonical configs:** Several canonical experiments lack gold configs:
   - `random_direction_control`
   - `mlp_ablation_necessity_prompt_pass`
   - `mlp_sufficiency_test`
   - `combined_mlp_sufficiency_test`
   - `multi_token_bridge`
