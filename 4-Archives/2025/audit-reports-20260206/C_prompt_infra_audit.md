# Prompt Infrastructure Audit Report

**Date:** 2026-02-05  
**Auditor:** Subagent C3  
**Scope:** REUSABLE_PROMPT_BANK/ vs prompts/ infrastructure

---

## Executive Summary

The repository contains **two parallel prompt bank systems** with significant overlap and an unclear deprecation status. The `prompts/` directory is the canonical source with 754 prompts, while `REUSABLE_PROMPT_BANK/` is a subset (370 prompts) with 267 identical prompt texts.

**Key Finding:** `REUSABLE_PROMPT_BANK/` is marked as deprecated in `__init__.py` via comment silencing, but its files are still actively imported by the legacy compatibility layer.

---

## 1. Directory Structure Comparison

### 1.1 REUSABLE_PROMPT_BANK/ (9 files)

```
REUSABLE_PROMPT_BANK/
├── __init__.py                    # v2.0.0 loader with silenced deprecation warning
├── README.md                      # Documents v2.0 structure
├── dose_response.py               # 105 prompts (L1-L5 recursive)
├── baselines.py                   # 105 prompts (non-recursive controls)
├── confounds.py                   # 60 prompts (length/pseudo/repetitive controls)
├── generality.py                  # 60 prompts (Zen/Yogic/Buddhist)
├── kill_switch.py                 # 40 prompts (falsifiability tests)
├── sampling.py                    # Pair generation utilities
├── n300_mistral_test_prompt_bank_v1.py   # DEPRECATED wrapper
└── alternative_self_reference.py  # 200+ prompts (NOT loaded by __init__.py)
```

**Total loaded by `get_all_prompts()`:** 370 prompts

### 1.2 prompts/ (12 files)

```
prompts/
├── __init__.py                    # Exports PromptLoader
├── README.md                      # Documents canonical structure
├── loader.py                      # PromptLoader class (canonical API)
├── bank.json                      # 754 prompts (canonical source)
├── bank.json.backup*              # 4 backup files
├── control_baselines.json         # Control set
├── experimental_champions_v1.json # Champion prompts
└── deprecated/
    ├── control_baselines.json     # 14 KB
    └── experimental_champions_v1.json  # 8 KB
```

---

## 2. Content Analysis

### 2.1 Prompt Count by Pillar

| Pillar | prompts/bank.json | REUSABLE_PROMPT_BANK | Status |
|--------|-------------------|----------------------|--------|
| dose_response | 102 | 105 | ⚠️ Similar |
| baselines | 105 | 105 | ✅ Identical keys |
| confounds | 60 | 60 | ✅ Identical keys |
| generality | 60 | 60 | ✅ Identical keys |
| kill_switch | 40 | 40 | ✅ Identical keys |
| alternative_self_reference | 197 | ~200 (in file, not loaded) | ⚠️ Different structure |
| controls | 22 | 0 | ❌ Missing in RPB |
| experimental | 42 | 0 | ❌ Missing in RPB |
| dose_response_legacy | 46 | 0 | ❌ Missing in RPB |
| legacy | 20 | 0 | ❌ Missing in RPB |
| cross_architecture_validation | 60 | 0 | ❌ Missing in RPB |

**Total:**
- `prompts/bank.json`: **754 prompts**
- `REUSABLE_PROMPT_BANK` (loaded): **370 prompts**

### 2.2 Key Overlap Analysis

| Module | Keys in RPB | Also in bank.json | Overlap % |
|--------|-------------|-------------------|-----------|
| dose_response.py | 105 | 87 | 82.9% |
| baselines.py | 105 | 105 | 100% |
| confounds.py | 60 | 60 | 100% |
| generality.py | 60 | 60 | 100% |
| kill_switch.py | 40 | 40 | 100% |

### 2.3 Text Content Overlap

```
prompts/bank.json unique texts:      754
REUSABLE_PROMPT_BANK unique texts:   367
Identical texts (exact match):       267  (36% of bank.json)
Only in bank.json:                   487
Only in REUSABLE_PROMPT_BANK:        100
```

---

## 3. Deprecation Status Verification

### 3.1 REUSABLE_PROMPT_BANK Deprecation Evidence

**In `__init__.py` (line 44-45):**
```python
# Silenced - use prompts/loader.py instead (canonical source)
# print(f"REUSABLE_PROMPT_BANK v{__version__} loaded")
```

**In `n300_mistral_test_prompt_bank_v1.py` (line 1-18):**
```python
# === DEPRECATED: Use REUSABLE_PROMPT_BANK instead ===
# This file is maintained for backward compatibility only.
# New code should import from REUSABLE_PROMPT_BANK directly.
```

**In `prompts/loader.py` (line 1-6):**
```python
"""
PromptLoader: Strict API to fetch balanced sets of prompts.
...
CANONICAL SOURCE: prompts/bank.json (754 prompts, version-tracked)
DO NOT use REUSABLE_PROMPT_BANK directly - it's deprecated.
"""
```

### 3.2 Deprecation Status: UNCLEAR

Despite deprecation warnings:
1. `REUSABLE_PROMPT_BANK/__init__.py` exports a fully functional API
2. `n300_mistral_test_prompt_bank_v1.py` actively imports from RPB
3. No deprecation warnings are actually raised at runtime (commented out/silenced)
4. `alternative_self_reference.py` (~200 prompts) exists ONLY in RPB, not in bank.json

---

## 4. Unique vs Duplicate Prompts

### 4.1 Duplicate Prompts (267 identical texts)

**Example duplicates found:**
- `"Apple apple apple..."` (pure_repetition kill switch)
- `"What is consciousness? (Think about what's happening right now...)"` (L1_hint_01)
- `"The the the the the..."` (pure_repetition)
- `"On a stormy night at the edge of the city,"` (baseline_creative)

### 4.2 Unique to REUSABLE_PROMPT_BANK (100 prompts)

**Source:** These appear to be additional prompts in dose_response.py that don't have matching keys in bank.json (18 of 105 dose_response keys are unique).

**Example (not in bank.json):**
```python
# From dose_response.py - keys L2_simple_06, L2_simple_08, L2_simple_10, etc.
"L2_simple_06": "Observe yourself generating this explanation..."
```

### 4.3 Unique to prompts/bank.json (487 prompts)

**Major categories:**
- `alternative_self_reference`: 197 prompts (structured differently in RPB)
- `experimental` (champions): 42 prompts
- `controls` (length/pseudo matched): 22 prompts
- `dose_response_legacy`: 46 prompts
- `legacy`: 20 prompts
- `cross_architecture_validation`: 60 prompts

---

## 5. Critical Discrepancies

### 5.1 alternative_self_reference.py

**Location:** `REUSABLE_PROMPT_BANK/alternative_self_reference.py` (~55KB, 200+ prompts)

**Status:** NOT loaded by `REUSABLE_PROMPT_BANK/__init__.py`

**Structure:** Python dict with research hypothesis metadata:
```python
alternative_prompts["godelian_01"] = {
    "text": "...",
    "group": "godelian",
    "pillar": "logical_self_reference",
    "expected_rv_range": [0.50, 0.80],
    "notes": "Classic Gödel - does formal self-reference match experiential?"
}
```

**In bank.json:** These prompts exist under pillar `alternative_self_reference` (197 prompts) but **without the `notes` field** and with different key names.

### 5.2 Sampling Functions

**REUSABLE_PROMPT_BANK/sampling.py** provides:
- `get_balanced_pairs()`
- `get_dose_response_set()`
- `get_length_matched_pairs()`

**prompts/loader.py** provides:
- `get_balanced_pairs()`
- `get_by_pillar()`
- `get_by_group()`

**Status:** Both work but use different underlying data sources.

---

## 6. Recommendations

### Immediate Actions

1. **Clarify deprecation status:**
   - Either fully deprecate `REUSABLE_PROMPT_BANK` with runtime warnings
   - Or remove deprecation comments if it's still supported

2. **Merge alternative_self_reference.py:**
   - The 200+ prompts in this file should be added to bank.json with full metadata
   - Or ensure loader.py can access them

3. **Resolve 18 unique dose_response prompts:**
   - Determine if prompts like `L2_simple_06` should be in bank.json

### Long-term Actions

4. **Consolidate to single source:**
   - `prompts/bank.json` is already the documented canonical source
   - Update all imports to use `PromptLoader`

5. **Remove deprecated files:**
   - `n300_mistral_test_prompt_bank_v1.py` (or make it a true thin wrapper)
   - `REUSABLE_PROMPT_BANK/` (after migration period)

---

## 7. File Paths Summary

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `~/mech-interp-latent-lab-phase1/prompts/bank.json` | ~8800 | ✅ Canonical | 754 prompts, single source of truth |
| `~/mech-interp-latent-lab-phase1/prompts/loader.py` | ~320 | ✅ Active | PromptLoader class |
| `~/mech-interp-latent-lab-phase1/REUSABLE_PROMPT_BANK/__init__.py` | ~50 | ⚠️ Silenced | Exports functional API but silenced |
| `~/mech-interp-latent-lab-phase1/REUSABLE_PROMPT_BANK/dose_response.py` | ~900 | ⚠️ Partial | 87/105 keys in bank.json |
| `~/mech-interp-latent-lab-phase1/REUSABLE_PROMPT_BANK/baselines.py` | ~150 | ⚠️ Deprecated | 100% key overlap with bank.json |
| `~/mech-interp-latent-lab-phase1/REUSABLE_PROMPT_BANK/alternative_self_reference.py` | ~1700 | ⚠️ Orphaned | Not loaded by __init__.py |
| `~/mech-interp-latent-lab-phase1/REUSABLE_PROMPT_BANK/n300_mistral_test_prompt_bank_v1.py` | ~40 | ❌ Deprecated | Wrapper with deprecation warning |
| `~/mech-interp-latent-lab-phase1/prompts/deprecated/*.json` | - | ✅ Archived | Old versions properly stored |

---

## 8. Conclusion

The prompt infrastructure has **functional duplication** with:
- **754 canonical prompts** in `prompts/bank.json`
- **370 prompts** in `REUSABLE_PROMPT_BANK/` (267 identical texts)
- **200 additional prompts** in `alternative_self_reference.py` (orphaned)

**Recommended path:** Complete migration to `prompts/` as the single source of truth, properly deprecate `REUSABLE_PROMPT_BANK/` with runtime warnings, and merge orphaned prompts into the canonical bank.

---

*Report generated: 2026-02-05*  
*Audit scope: GROUP C3 - REUSABLE_PROMPT_BANK verification*
