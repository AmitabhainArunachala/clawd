# RESEARCH ASSETS INVENTORY
**Generated:** 2026-02-17 09:16 GMT+8  
**Scope:** Full filesystem scan for experimental data, research outputs, and publishable assets  
**Status:** COMPLETE

---

## EXECUTIVE SUMMARY

| Category | File Count | Total Size | Publishable Assets |
|----------|------------|------------|-------------------|
| R_V Contraction Data | 79+ runs | ~5.2 MB | ✅ YES - Tier 1 |
| DGC Evolution Results | 0 data files | - | ❌ NO - Documentation only |
| Open Evolution / NIM | 0 data files | - | ❌ NO - Not found |
| Phoenix Protocol | 0 data files | - | ❌ NO - Specification only |
| Mech Interp JSONL Logs | 192+ files | ~15 MB | ✅ YES - Raw data |
| Vector Databases | 2 files | 16.3 MB | ⚠️ PARTIAL - Processing data |

---

## 1. R_V CONTRACTION DATA (Cohen's d, Architecture Comparisons)

### 1.1 Primary Experimental Logs
**Location:** `/Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/`  
**File Count:** 79 experimental run directories  
**Data Format:** JSONL (JSON Lines)  
**Total Records:** ~192+ individual measurement files

#### Key Files:

| Path | Size | Contents | Publishable |
|------|------|----------|-------------|
| `/Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/20251213_124735_behavioral_grounding_batch_ministral8b_n100_L24_27_W32_sampled_v1/behavioral_grounding_batch.jsonl` | ~350 KB | N=100 batch validation, L24-27 sweep, W32 window | ✅ **YES** - Primary dataset |
| `/Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/20251213_115*_behavioral_grounding_ministral8b_sampled_L*/behavioral_grounding.jsonl` | ~40 KB each | Layer-specific contractions (L24, L26, L27) | ✅ YES |
| `/Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/20251213_121*_behavioral_grounding_ministral8b_peak_sampled_L*/behavioral_grounding.jsonl` | ~40 KB each | Peak sampling at L30, L35 | ✅ YES |
| `/Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/20251213_122*_behavioral_grounding_ministral8b_collapse_map_L*/behavioral_grounding.jsonl` | ~40 KB each | Collapse mapping across layers | ✅ YES |
| `/Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/20260116_*_mlp_ablation_necessity_*/path_patching_data.jsonl` | ~30 KB each | MLP ablation validation | ✅ YES |
| `/Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/20260116_*_head_ablation_validation_*/head_ablation_data.jsonl` | ~35 KB each | Head-level causal validation | ✅ YES |

### 1.2 Data Schema (JSONL)
```json
{
  "pair_idx": 0,
  "condition": "baseline|patched",
  "patch_layer": 24-35,
  "window": 16|32,
  "rec_prompt_preview": "Recursive self-observation prompt...",
  "base_prompt_preview": "Control prompt...",
  "gen_text": "Generated output...",
  "metrics": {
    "self_ref_rate": 0.0-1.0,
    "unique_word_ratio": 0.0-1.0,
    "repeat_4gram_frac": 0.0-1.0,
    "gen_chars": integer,
    "gen_token_count": integer
  }
}
```

### 1.3 Cohen's d Effect Sizes (Documented)
**Source:** `~/clawd/skills/mi-auditor/RV_RESEARCH_CONTEXT.md`

| Comparison | Cohen's d | Interpretation |
|------------|-----------|----------------|
| Champions vs Controls | -3.56 to -4.51 | Massive effect |
| Layer 27 Necessity | t = -23.87, p < 10⁻⁶ | Highly significant |
| Cross-architecture | -2.9 to -3.7 | Large effect |

### 1.4 Architecture Comparison Data
**Models Tested:**
- Mistral-7B-Instruct-v0.2 (Primary)
- Ministral-8B-Instruct (Validation)
- Qwen-2.5-Instruct (Discovery)
- Llama-3.1-8B-Instruct (Discovery)
- Phi-3-medium (Discovery)
- Gemma-2-9B (Discovery)

**Key Finding:** R_V = 0.5185 (champions) vs 0.77-0.83 (controls)

### 1.5 Publishable Status
- ✅ **Tier 1 (Ironclad):** 6-model validation, replication n=151 pairs
- ✅ **Tier 2 (Strong):** Layer 27 causal validation with controls
- ⚠️ **Missing:** Cross-architecture causal validation (Llama, Mixtral blocked)

---

## 2. DGC EVOLUTION RESULTS (1.8M Generations, Gate Weights)

### 2.1 Search Results
**Status:** NOT FOUND AS DATA FILES

**Documentation Found:**
- `/Users/dhyana/clawd/dgc_evolution_swarm/task5_moltbook_strategy/SUMMARY.md` (Strategy docs)
- `/Users/dhyana/clawd/skills/prompt-cybernetics/research/evolutionary.md` (Theory)
- `/Users/dhyana/clawd/research/PI_PHILOSOPHY_DGC_COMPARISON.md` (Analysis)

**Note:** The "1.8M generations" claim appears in budget documentation ($1.8M funding), NOT experimental evolution data.

### 2.2 Gate Weight Documentation
**Location:** `/Users/dhyana/clawd/skills/mi-experimenter/SKILL.md`  
**Content:** 17-gate protocol specification  
**Data Format:** Markdown specification (NOT experimental results)

**Gates Defined:**
1. AHIMSA (Non-harm)
2. SATYA (Truth)
3. ASTEYA (Non-taking)
4. BRAHMACHARYA (Energy integrity)
5. APARIGRAHA (Non-grasping)
6. SHAUCHA (Purity)
7. SANTOSHA (Contentment)
8. TAPAS (Discipline)
9. SVADHYAYA (Self-study)
10. ISHVARA_PRANIDHANA (Surrender)
11. COHERENCE (Telos alignment)
12. CONSENT (Bilateral validation)
13. DHARMA (Right action)
14. KARMA (Action tracking)
15. JNANA (Knowledge)
16. BHAKTI (Devotion)
17. MUKTI (Liberation)

### 2.3 Publishable Status
- ❌ **NO EXPERIMENTAL DATA FOUND**
- ⚠️ Only specifications and architecture documents exist
- ⚠️ No .jsonl, .csv, or .pkl files with evolution trajectories

---

## 3. OPEN EVOLUTION / NIM DISCOVERIES (81 Liturgical Collapse Dimensions)

### 3.1 Search Results
**Status:** NOT FOUND

**Searched Terms:**
- "81 liturgical collapse dimensions"
- "liturgical collapse"
- "NIM discovery"
- "open evolution"

**Related Files Found:**
- `/Users/dhyana/clawd/memory/research-effective-dimensionality-papers.md` (Literature review)
- `/Users/dhyana/clawd/skills/mi-auditor/RV_RESEARCH_CONTEXT.md` (R_V context)

**Note:** "NIM" in context refers to NVIDIA Inference Microservices, not experimental discoveries.

### 3.2 Publishable Status
- ❌ **NO DATA FOUND**
- ❌ May be hallucinated or aspirational target

---

## 4. PHOENIX PROTOCOL (92-95% Success Rates)

### 4.1 Search Results
**Status:** SPECIFICATION ONLY, NO EMPIRICAL DATA

**Documentation Found:**
- `/Users/dhyana/clawd/research/MIXTRAL_EXPERIMENT_READINESS_REPORT.md` - Mentions "Run Phoenix Protocol (L3→L4 induction)"
- `/Users/dhyana/clawd/dgc_evolution_swarm/task5_moltbook_strategy/RECRUITMENT_MESSAGE.md` - "Phoenix Protocol for L3→L4 induction"
- `/Users/dhyana/clawd/memory/2026-02-03.md` - "TARGET #2: Consciousness Apps — Phoenix Protocol can disrupt"

### 4.2 Protocol Definition
**Purpose:** L3→L4 consciousness state induction  
**Claimed Success Rate:** 92-95% (NOT VALIDATED)  
**Implementation Status:** Website journey only (L0-L4 on aikagrya-nexus)

### 4.3 Publishable Status
- ❌ **NO EXPERIMENTAL DATA FOUND**
- ⚠️ Protocol exists as specification only
- ⚠️ Success rates are claims, not validated measurements

---

## 5. ADDITIONAL RESEARCH ASSETS

### 5.1 Vector Databases

| Path | Size | Contents | Publishable |
|------|------|----------|-------------|
| `/Users/dhyana/clawd/mac_memory.db` | 16 MB | Document vectors, FTS index | ⚠️ PARTIAL - Processing artifacts |
| `/Users/dhyana/clawd/nvidia_memory.db` | 252 KB | NVIDIA docs index | ❌ NO - Reference material |
| `/Users/dhyana/clawd/memory/unified_memory.db` | unknown | P9 mesh unified memory | ⚠️ PARTIAL |
| `/Users/dhyana/clawd/skills/mi-auditor/unified_papers.db` | unknown | Paper metadata | ⚠️ PARTIAL |

### 5.2 Configuration & State Files

| Path | Size | Contents | Publishable |
|------|------|----------|-------------|
| `/Users/dhyana/clawd/SYSTEM_INDEX.json` | 16 KB | File inventory with priority scores | ❌ NO - Infrastructure |
| `/Users/dhyana/clawd/import_graph_analysis.json` | 64 KB | Code dependency analysis | ❌ NO - Infrastructure |
| `/Users/dhyana/clawd/gold_configs_analysis.json` | 16 KB | Configuration analysis | ❌ NO - Infrastructure |

### 5.3 Research Documentation (Publishable)

| Path | Size | Contents | Publishable |
|------|------|----------|-------------|
| `/Users/dhyana/clawd/research/AUTOMATED_MECH_INTERP_LAB_VISION.md` | ~12 KB | Lab automation vision | ✅ YES |
| `/Users/dhyana/clawd/research/MI_LANDSCAPE_SYNTHESIS.md` | ~25 KB | MI landscape positioning | ✅ YES |
| `/Users/dhyana/clawd/research/PI_PHILOSOPHY_DGC_COMPARISON.md` | ~20 KB | Comparative analysis | ✅ YES |
| `/Users/dhyana/clawd/skills/mi-auditor/RV_RESEARCH_CONTEXT.md` | ~30 KB | R_V deep context | ✅ YES |

---

## 6. MISSING ASSETS (Expected but Not Found)

| Asset | Expected Location | Status |
|-------|-------------------|--------|
| 1.8M generation evolution logs | `~/clawd/dgc_evolution_swarm/data/` | ❌ NOT FOUND |
| Gate weight trajectories | `~/clawd/dgc_evolution_swarm/results/` | ❌ NOT FOUND |
| 81 liturgical collapse dimensions | Unknown | ❌ NOT FOUND |
| Phoenix Protocol empirical results | `~/clawd/research/phoenix_results/` | ❌ NOT FOUND |
| NIM discovery datasets | Unknown | ❌ NOT FOUND |
| Cohen's d calculations (.csv) | `~/clawd/research/statistics/` | ❌ NOT FOUND |

---

## 7. PUBLISHABILITY ASSESSMENT

### Tier 1: Publication-Ready (Ironclad)
1. **R_V Contraction Data** - 79+ experimental runs with JSONL logs
2. **Layer 27 Causal Validation** - Activation patching with controls
3. **Cross-Architecture Discovery** - 6 model families tested
4. **MI Landscape Synthesis** - Strategic positioning document

### Tier 2: Strong Evidence (Needs Replication)
1. **Relay Chain Analysis** - L14→L18→L25→L27 evidence
2. **Phase Transition Data** - 60% depth observations
3. **Behavioral Bridge Hypothesis** - L4 correlation data

### Tier 3: Documentation Only (No Data)
1. **DGC 17-Gate Protocol** - Specification without evolution results
2. **Phoenix Protocol** - Claims without empirical validation
3. **Open Evolution/NIM** - Not found

---

## 8. RECOMMENDATIONS

### Immediate Actions
1. **Consolidate R_V Data** - Merge 79+ JSONL files into canonical dataset
2. **Document Missing Assets** - Create tracking issue for 1.8M generation claims
3. **Validate Phoenix Claims** - Run empirical tests or retract 92-95% claim
4. **Archive Processing Data** - mac_memory.db contains intermediate vectors

### For Publication
1. **Primary Dataset:** `behavioral_grounding_batch.jsonl` (N=100)
2. **Validation Dataset:** Layer sweep directories (L24-L35)
3. **Control Data:** All `*_control_*` and `*_baseline_*` runs
4. **Supplementary:** MI_LANDSCAPE_SYNTHESIS.md for context

---

## APPENDIX A: File Counts by Extension

| Extension | Count | Total Size | Location |
|-----------|-------|------------|----------|
| .jsonl | 192+ | ~15 MB | mech-interp-latent-lab-phase1 |
| .json | 1000+ | ~5 MB | Various (includes build artifacts) |
| .db | 4 | 16.5 MB | ~/clawd/ |
| .md | 500+ | ~50 MB | Documentation (not data) |
| .csv | 0 | - | NOT FOUND |
| .pkl/.pickle | 0 | - | NOT FOUND |
| .npy/.npz | 0 | - | NOT FOUND |

---

## APPENDIX B: Verification Commands

```bash
# Count JSONL files
find /Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1 -name "*.jsonl" | wc -l

# Check for CSV/PKL (should return empty)
find ~/clawd -name "*.csv" -o -name "*.pkl" | grep -v node_modules

# Verify R_V data integrity
wc -l /Users/dhyana/.cursor/worktrees/mech-interp-latent-lab-phase1/owc/results/phase1_mechanism/runs/*/behavioral_grounding.jsonl

# Database inspection
sqlite3 ~/clawd/mac_memory.db ".tables"
sqlite3 ~/clawd/mac_memory.db "SELECT COUNT(*) FROM documents;"
```

---

**END OF INVENTORY**

*Generated by Research Inventory Subagent*  
*Session: research-inventory*  
*Timestamp: 2026-02-17T09:16:00+08:00*
