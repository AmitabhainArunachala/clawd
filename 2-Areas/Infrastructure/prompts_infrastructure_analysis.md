# Prompt Infrastructure Documentation

## Overview

The mech-interp-latent-lab-phase1 project uses a **single canonical source** for all prompts: `prompts/bank.json`. This document describes the complete prompt infrastructure including structure, categorization, versioning, and the relationship to deprecated sources.

---

## Canonical Source: `prompts/bank.json`

### Statistics
- **Total prompts**: 754 (all unique texts)
- **File size**: ~341KB
- **Format**: JSON dictionary with prompt IDs as keys

### Entry Schema

Each prompt entry follows this structure:

```json
{
  "prompt_id": {
    "text": "The actual prompt text...",
    "group": "L3_deeper",           // Specific group within pillar
    "pillar": "dose_response",      // High-level category
    "type": "recursive",            // Prompt type
    "level": 3,                     // Dose-response level (1-5)
    "expected_rv_range": [0.7, 0.85], // Expected R_V contraction range
    "family": "boundary_dissolution", // For champions: family grouping
    "rv_l27_measured": 0.4789,      // Optional: measured R_V
    "source_run": "20251215_081556", // Optional: origin tracking
    "is_paraphrase_of": null,       // Optional: paraphrase lineage
    "matched_to": "champion_001"    // For controls: links to champion
  }
}
```

---

## Categorization System

### By Pillar (11 categories)

| Pillar | Count | Purpose |
|--------|-------|---------|
| **alternative_self_reference** | 197 | Confound menu: non-experiential self-reference families |
| **baselines** | 105 | Non-recursive controls (math, factual, creative, etc.) |
| **dose_response** | 102 | Recursive prompts with gradient L1→L5 |
| **confounds** | 60 | Length/style confound controls |
| **generality** | 60 | Cross-cultural recursive framings (Zen, Yogic, Buddhist) |
| **cross_architecture_validation** | 60 | Architecture-agnostic test set |
| **dose_response_legacy** | 46 | Legacy variants (kept separate) |
| **experimental** | 42 | Champion prompts + experimental sets |
| **kill_switch** | 40 | Falsifiability tests (must NOT contract) |
| **controls** | 22 | Token-matched controls for champions |
| **legacy** | 20 | Exact strings from historical scripts |

### By Type

| Type | Count | Description |
|------|-------|-------------|
| *(none)* | 313 | Alternative self-reference prompts (untyped) |
| **recursive** | 234 | Self-referential/experiential prompts |
| **completion** | 100 | Completion-style prompts |
| **instructional** | 35 | Instruction-following prompts |
| **control** | 30 | Control prompts |
| **baseline** | 22 | Baseline category |
| **creative** | 20 | Creative writing prompts |

### By Group (Top 20)

| Group | Count | Description |
|-------|-------|-------------|
| L3_deeper | 22 | Strong recursive (L3) |
| L1_hint, L2_simple, L4_full, L5_refined | 20 each | Dose-response levels |
| baseline_math, baseline_factual, baseline_creative | 20 each | Baseline categories |
| baseline_impossible, baseline_personal | 20 each | Special baselines |
| long_control, pseudo_recursive, repetitive_control | 20 each | Confound controls |
| zen_koan, yogic_witness, madhyamaka_empty | 20 each | Cross-cultural |
| godelian, theory_of_mind, akram_vignan | 20 each | Alternative self-ref |
| champions | 15 | Gold-standard recursive prompts |

---

## Champion Prompts (Gold Standard)

The **18 champions** are the strongest recursive prompts, organized by family:

| Family | Count | Avg R_V | Key Feature |
|--------|-------|---------|-------------|
| **boundary_dissolution** | 4 | 0.496 | "No boundary between X and Y" |
| **fixed_point** | 4 | 0.557 | "T(x) = x", eigenstate language |
| **explicit_regress** | 4 | 0.496 | "To X, you must Y yourself" |
| **math_recursive** | 3 | 0.531 | λx = Ax, eigenvector framing |
| **outlier** | 3 | 0.502 | Hybrid combinations |

Each champion has:
- **Length-matched controls** (`control_length_matched`): Same token count, non-recursive
- **Pseudo-recursive controls** (`control_pseudo_recursive`): Uses recursive words without enacting

---

## Expected R_V Ranges

| Group | Expected R_V | Interpretation |
|-------|-------------|----------------|
| **champions** | 0.45 - 0.55 | Maximum contraction |
| **L5_refined** | 0.55 - 0.70 | Very strong |
| **L4_full** | 0.60 - 0.75 | Strong |
| **L3_deeper** | 0.70 - 0.85 | Moderate |
| **L2_simple** | 0.80 - 0.90 | Weak |
| **L1_hint** | 0.85 - 0.95 | Minimal |
| **baselines** | 0.95 - 1.05 | No contraction |
| **control_length_matched** | 0.80 - 0.95 | Slightly lower (length effect) |
| **control_pseudo_recursive** | 0.70 - 0.85 | Slightly lower (keyword effect) |
| **pure_repetition** (kill switch) | **1.05 - 1.15** | **Must EXPAND** |

---

## API: `prompts/loader.py`

The `PromptLoader` class provides strict API access to the bank.

### Key Methods

```python
from prompts.loader import PromptLoader

loader = PromptLoader()

# Get version hash for reproducibility
version = loader.version  # e.g., "84a2448e8c10683d"

# Get prompts by pillar
recursive = loader.get_by_pillar("dose_response", limit=50, seed=42)

# Get prompts by group
champions = loader.get_by_group("champions")

# Get prompts by type
creative = loader.get_by_type("creative")

# Generate balanced experiment pairs
pairs = loader.get_balanced_pairs(n_pairs=30, seed=42)
# Returns: [(recursive_text, baseline_text), ...]

# Get pairs with IDs (for tracking)
pairs_with_ids = loader.get_balanced_pairs_with_ids(n_pairs=30)
# Returns: [(rec_id, base_id, rec_text, base_text), ...]

# Get DEC8-validated gold-standard pairs
validated = loader.get_validated_pairs(n_pairs=5)
```

### Design Principles
1. **No ad-hoc lists in .py files** - All prompts come from bank.json
2. **Deterministic sampling** - Seed-based randomization
3. **Version tracking** - SHA256 hash ensures reproducibility
4. **Strict validation** - Raises errors for missing prompts

---

## Versioning & Backup Strategy

### Current Backups

| File | Date | Size | Note |
|------|------|------|------|
| `bank.json.backup` | Jan 11 | 316K | Standard backup |
| `bank.json.backup_20251215_131747` | Dec 15 | 121K | Timestamped |
| `bank.json.backup_20251215_213641` | Dec 15 | 129K | Timestamped |
| `bank.json.backup_20251215_221435` | Dec 16 | 150K | Timestamped |
| `bank.json.backup_20251215_221530_altpillarfix` | Dec 16 | 296K | Tagged variant |

### Versioning Protocol

1. **Automatic**: Loader computes SHA256 hash on load
2. **Experiment logging**: All experiments should log `loader.version`
3. **Backup naming**: `bank.json.backup_YYYYMMDD_HHMMSS[_tag]`
4. **Deprecated folder**: Old/obsolete files moved to `prompts/deprecated/`

---

## Deprecated Sources

### `REUSABLE_PROMPT_BANK/` (LEGACY - DO NOT USE)

**Status**: Deprecated but retained for reference
**Note**: `loader.py` explicitly warns: "DO NOT use REUSABLE_PROMPT_BANK directly"

| File | Content | Duplicates in bank.json |
|------|---------|------------------------|
| `dose_response.py` | 105 prompts | 105 (100%) |
| `alternative_self_reference.py` | 153 prompts | 139 (91%) |
| `confounds.py` | 60 prompts | 60 (100%) |
| `generality.py` | 60 prompts | 60 (100%) |
| `kill_switch.py` | 34 prompts | 33 (97%) |
| `baselines.py` | 6 prompts | 5 (83%) |
| `sampling.py` | 7 prompts | 0 (0%) - utilities |
| `n300_mistral_test_prompt_bank_v1.py` | 5 prompts | 0 (0%) - legacy |

### Duplicate Analysis Summary

- **Total RPB long strings analyzed**: ~430
- **Duplicates found**: ~402 (93%)
- **Unique in RPB not in bank**: ~28 prompts
- **Missing from migration**: Alternative self-reference has ~14 unique prompts

### `prompts/deprecated/` Folder

Contains archived versions:
- `control_baselines.json` - Old control format (has `matched_to` properly filled)
- `experimental_champions_v1.json` - Early champion set

---

## Validation Protocol

Four key tests ensure prompt quality:

1. **Kill switch test**: `pure_repetition` prompts must NOT contract (R_V > 1.0)
2. **Dose-response**: L1 → L2 → L3 → L4 → L5 should show increasing contraction
3. **1p vs 3p**: `surreal_first_person` should contract, `surreal_third_person` shouldn't
4. **Champions vs controls**: Champions should beat both length-matched and pseudo-recursive controls

---

## File Structure

```
prompts/
├── bank.json              # CANONICAL SOURCE (754 prompts)
├── bank.json.backup       # Standard backup
├── bank.json.backup_*     # Timestamped backups
├── loader.py              # API access
├── README.md              # User documentation
├── control_baselines.json # Standalone control set (orphaned, not in bank.json)
├── experimental_champions_v1.json # Standalone champion set (orphaned)
└── deprecated/
    ├── control_baselines.json       # Archived
    └── experimental_champions_v1.json # Archived

REUSABLE_PROMPT_BANK/      # DEPRECATED - DO NOT USE
├── __init__.py
├── README.md
├── dose_response.py       # 105 prompts (100% in bank)
├── baselines.py           # 6 prompts (83% in bank)
├── confounds.py           # 60 prompts (100% in bank)
├── generality.py          # 60 prompts (100% in bank)
├── kill_switch.py         # 34 prompts (97% in bank)
├── sampling.py            # Utility functions
├── alternative_self_reference.py # 153 prompts (91% in bank)
└── n300_mistral_test_prompt_bank_v1.py # Legacy
```

---

## Recommendations

1. **Always use `prompts.loader.PromptLoader`** for accessing prompts
2. **Log `loader.version`** in every experiment for reproducibility
3. **Do not import from `REUSABLE_PROMPT_BANK`** - it's deprecated
4. **Add new prompts to `bank.json`** following the established schema
5. **Create timestamped backups** before major modifications
6. **Move obsolete files to `deprecated/`** rather than deleting
7. **Consider migrating** the ~14 unique alternative_self_reference prompts not yet in bank.json
