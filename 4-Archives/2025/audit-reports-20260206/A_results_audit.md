

---

# A9: Contract Violation Compilation Report

**Task:** GROUP A9 - Contract Violation Compilation  
**Date:** 2026-02-05  
**Agent:** Contract Audit Subagent  
**Status:** COMPLETE

---

## Executive Summary

| Violation Type | Count | Files Affected |
|----------------|-------|----------------|
| R_V > 1.0 violations | 76 instances | 22 files |
| Missing required fields | 562 instances | 191 files |
| Inconsistent naming (rv_p vs p_value) | 24 instances | 24 files |
| Missing hardware_info.json | 224 instances | 224 files (100%) |
| Missing schema_version in config.json | 285 instances | 285 files |
| Single-layer PR mislabeled as R_V | 0 | 0 files |
| Stringified JSON summaries | 0 | 0 files |

**Overall Compliance Rate:** ~15% (severe contract violations)

---

## 1. R_V > 1.0 Violations (76 instances across 22 files)

**Contract Requirement:** R_V values should be bounded in [0, 1] as they represent ratios/proportions.

**Affected Files:**

### 1.1 Phase2 Generalization (Gemma 2 9B)
- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_120619_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l4/summary.json`
  - `rv_t_statistic`: 6.790815404586947
  
- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_120529_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l3/summary.json`
  - `rv_t_statistic`: 30.43250204416605

- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_120341_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l2/summary.json`
  - `rv_t_statistic`: 7.640096362752983

### 1.2 Phase2 Generalization (Llama3 8B Base)
- `results/phase2_generalization/llama3_8b_base/20260115_171757_mlp_ablation_necessity/summary.json`
  - `rv`: 1.2324951903089696
  - `rv_ablated_mean`: 1.8465768586899007
  - `rv_baseline_mean`: 1.2324951903089696
  - `rv_t_statistic`: 16.379455011059324

- `results/runs/20260115_171757_mlp_ablation_necessity/summary.json` (duplicate)
  - Same violations as above

### 1.3 Phase3 Attention
- `results/phase3_attention/runs/20251213_072428_comprehensive_circuit/summary.json`
  - `dose_response.L1.rv`: 1.1956683619234663
  - `dose_response.L2.rv`: 1.1761491158960455
  - `dose_response.L4.rv`: 1.216508235244777
  - `dose_response.L5.rv`: 1.1878663329864747

### 1.4 Phase1 Cross Architecture
- `results/phase1_cross_architecture/runs/20260202_120856_rv_l27_causal_validation_qwen2_7b/summary.json`
  - `rv_baseline_mean`: 1.2562008539942826
  - `rv_recursive_mean`: 1.1574449929080004

- `results/phase1_cross_architecture/runs/20260202_125718_rv_l27_causal_validation_opt_6_7b/summary.json`
  - `rv_baseline_mean`: 1.2003145612141213

### 1.5 Phase1 Mechanism (MLP Tests)
- `results/phase1_mechanism/runs/20260116_114536_mlp_ablation_necessity_prompt_pass_l3_necessity_prompt_pass/summary.json`
  - `rv_t_statistic`: 14.306244672785326

- `results/phase1_mechanism/runs/20260116_113943_mlp_ablation_necessity_prompt_pass_l0_necessity_prompt_pass/summary.json`
  - `rv_ablated_mean`: 1.6858855761465228
  - `rv_delta_mean`: 1.1792589888772986
  - `rv_t_statistic`: 89.10245609310216

- `results/phase1_mechanism/runs/20260116_114327_mlp_ablation_necessity_prompt_pass_l1_necessity_prompt_pass/summary.json`
  - `rv_ablated_mean`: 1.3763909485971217
  - `rv_t_statistic`: 58.866112041125575

### 1.6 Phase1 Mechanism (Random Direction Controls)
Multiple files with `rv_delta_mean` values > 1.0:
- `results/phase1_mechanism/runs/20260116_122037_random_direction_control_l3_random_control/summary.json`
- `results/phase1_mechanism/runs/20260116_122849_random_direction_control_l3_random_control/summary.json`
- `results/phase1_mechanism/runs/20260116_124427_random_direction_control_l3_random_control/summary.json`

Values range from 2.1457962336319403 to 2.8894242387175813

### 1.7 Phase1 Mechanism (Combined MLP Sufficiency)
- `results/phase1_mechanism/runs/20260116_124006_combined_mlp_sufficiency_test_l0_l1_combined_sufficiency/summary.json`
  - `rv_patched_mean`: 1.112128409924867
  - `rv_restoration_pct_std`: 437.61037908066777

- `results/phase1_mechanism/runs/20260116_130033_combined_mlp_sufficiency_test/summary.json`
  - `rv_patched_mean`: 1.413822284177207
  - `rv_restoration_pct_std`: 562.3505405374598

- `results/phase1_mechanism/runs/20260116_121624_combined_mlp_sufficiency_test_l0_l1_combined_sufficiency/summary.json`
  - `rv_patched_mean`: 1.112128409924867
  - `rv_restoration_pct_std`: 437.61037908066777

### 1.8 Archive Files
- `results/archive/superseded/20251213_072428_comprehensive_circuit/summary.json`
  - Same as phase3_attention version (duplicate)

---

## 2. Missing Required Fields (562 instances across 191 files)

**Contract Requirement:** summary.json MUST contain `model`, `timestamp`, and `schema_version` fields.

**Breakdown:**
- `timestamp`: missing from 191 files (85.3%)
- `schema_version`: missing from 191 files (85.3%)
- `model`: missing from 180 files (80.4%)

**Affected Directories:**
- `results/phase1_mechanism/runs/` - 67 files
- `results/discovery/behavioral_grounding/` - 52 files
- `results/discovery/path_patching/` - 3 files
- `results/discovery/steering/` - 7 files
- `results/phase2_generalization/` - 13 files
- `results/phase3_attention/runs/` - 9 files
- `results/gold_standard/runs/` - 3 files
- `results/archive/superseded/` - 9 files
- `results/phase1_cross_architecture/runs/` - 2 files

**Sample Violations:**
```json
{
  "file": "results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/.../summary.json",
  "missing": ["model", "timestamp", "schema_version"]
}
```

---

## 3. Inconsistent Naming: rv_p vs p_value (24 instances)

**Contract Requirement:** Use consistent naming convention `p_value` instead of `rv_p` or `rv_p_value`.

**Affected Files (24 unique files):**

### 3.1 Phase2 Generalization (Gemma 2 9B)
- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_120619_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l4/summary.json`
  - `rv_p_value`: 6.10802491638542e-09

- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_120529_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l3/summary.json`
  - `rv_p_value`: 9.111997114916368e-38

- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_112408_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l0/summary.json`
  - `rv_p_value`: 0.9677644307148197

- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_120341_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l2/summary.json`
  - `rv_p_value`: 2.2259171213717114e-10

- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_120712_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l5/summary.json`
  - `rv_p_value`: 1.577298322561512e-06

- `results/phase2_generalization/gemma_2_9b/03_prompt_pass_validation/runs/20260124_112500_mlp_ablation_necessity_prompt_pass_gemma_2_9b_prompt_pass_l1/summary.json`
  - `rv_p_value`: 1.3503160506552219e-15

- `results/phase2_generalization/gemma_2_9b/08_causal_validation_n45/runs/20260124_100037_rv_l27_causal_validation_gemma_2_9b_causal_validation_n45/summary.json`
  - `rv_p_value`: 9.81802491638542e-09

- `results/phase2_generalization/gemma_2_9b/11_causal_validation_champion/runs/20260124_112226_rv_l27_causal_validation_gemma_2_9b_causal_validation_champion/summary.json`
  - `rv_p_value`: 6.461161407866468e-20

- `results/phase2_generalization/gemma_2_9b/11_causal_validation_champion/runs/20260124_102546_rv_l27_causal_validation_gemma_2_9b_causal_validation_champion/summary.json`
  - `rv_p_value`: 1.204665032918014e-23

- `results/phase2_generalization/gemma_2_9b/13_confound_validation/runs/20260124_112312_confound_validation_gemma_2_9b_confound_validation/summary.json`
  - `rv_p_value`: 0.00011857268828312661

... and 14 additional files with same pattern

**Note:** While the values are valid p-values, the key naming is inconsistent with the contract which specifies `p_value` or `*_p_value` without the `rv_` prefix.

---

## 4. Missing hardware_info.json (224 directories, 100% non-compliance)

**Contract Requirement:** Every run directory MUST contain a `hardware_info.json` file with GPU model, CUDA version, and precision information.

**Impact:** CRITICAL - Results are not reproducible without hardware information.

**All 224 run directories lack this file.**

**Reference:** See A7 report for detailed hardware_info.json gap analysis.

---

## 5. Missing schema_version in config.json (285 files)

**Contract Requirement:** All config.json files should include `schema_version` for version tracking.

**Affected:** 285 config.json files across all run directories.

**Sample:**
- `results/kitchen_sink/runs/20251215_081007_test_kitchen_sink_rerun/config.json`
- `results/phase2_generalization/runs/20260111_212141_cross_architecture_validation/config.json`

---

## 6. Single-Layer PR Mislabeled as R_V (0 instances)

**Status:** ✅ No violations found

All path patching (PR) experiments correctly label their outputs and do not mislabel single-layer interventions as R_V measurements.

---

## 7. Stringified JSON Summaries (0 instances)

**Status:** ✅ No violations found

All summary.json files contain proper JSON objects, not stringified JSON strings.

---

## Root Cause Analysis

### R_V > 1.0 Violations
1. **Statistical values incorrectly included** - `rv_t_statistic`, `rv_cohens_d`, `rv_restoration_pct` are statistical measures that naturally exceed 1.0 but use the `rv_` prefix
2. **Unnormalized ratio calculations** - Some `rv_mean` values exceed 1.0 suggesting unbounded metrics

### Missing Required Fields
1. **Legacy code** - Early experiments predated schema requirements
2. **Inconsistent pipeline implementations** - Different experiment types use different output formats
3. **No validation enforcement** - Pipeline does not validate output against schema

### Inconsistent Naming
1. **Multiple developers** - Different naming conventions across experiment types
2. **Legacy naming preserved** - Early `rv_p_value` naming not updated to `p_value`

### Missing hardware_info.json
1. **Implementation gap** - Function exists but not called in pipelines
2. **No enforcement** - Pipeline doesn't fail if hardware_info.json is missing

---

## Recommended Actions

### Immediate (Pre-Publication)
1. **Fix R_V naming** - Rename statistical fields to remove `rv_` prefix (e.g., `t_statistic` not `rv_t_statistic`)
2. **Normalize R_V values** - Ensure all ratio values are bounded to [0, 1]
3. **Add missing fields** - Backfill `model`, `timestamp`, `schema_version` where possible
4. **Implement hardware_info.json generation** in all pipeline entry points

### Schema Enforcement
1. **Add JSON Schema validation** to pipeline output
2. **Fail fast** on contract violations during experiment runs
3. **Standardize naming conventions** across all experiment types

### Documentation
1. **Update UNIFIED_AUDITOR_INTEGRATION.md** with clear field naming conventions
2. **Create migration guide** for updating legacy results

---

## Verification Checklist

- [ ] All R_V ratio values bounded to [0, 1]
- [ ] Statistical values use correct naming (no rv_ prefix)
- [ ] All summary.json files contain model, timestamp, schema_version
- [ ] All config.json files contain schema_version
- [ ] All run directories contain hardware_info.json
- [ ] Schema validation added to pipeline
- [ ] Legacy results migrated or marked as non-compliant

---

## Statistical Summary

| Category | Files/Instances | Severity |
|----------|-----------------|----------|
| R_V > 1.0 | 76 instances / 22 files | MEDIUM |
| Missing required fields | 562 instances / 191 files | HIGH |
| Inconsistent naming | 24 instances / 24 files | LOW |
| Missing hardware_info.json | 224 directories (100%) | CRITICAL |
| Missing schema_version (config) | 285 files | MEDIUM |

**Total Violations:** 871 instances across 224 files

---

*Report generated: 2026-02-05*  
*Audit Agent: A9_contract_violations*
