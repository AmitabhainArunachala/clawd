# GOLD STANDARD INTEGRATION
## mi_auditor Protocol for Recursive Self-Observation Research

**Purpose:** This document maps mi_auditor's capabilities to the gold standard experimental framework for mechanistic interpretability research on recursive self-observation in transformers.

**Reference:** `~/mech-interp-latent-lab-phase1/AGENT_PROMPT_GOLD_STANDARD.md`

---

## AUDIT CHECKPOINT MATRIX

### Phase 0: Metric Validation (PREREQUISITE)

**Gold Standard Requirement:** Verify R_V actually measures Value matrix column space geometry

| Check | mi_auditor Action | Pass Criteria |
|-------|-------------------|---------------|
| V matrix analysis | Check `results/phase0/metric_validation/` exists | ≥1 experiment with direct V matrix extraction |
| Convex hull verification | Verify `summary.json` contains hull_statistics | Convex hull overlap metric reported |
| Metric comparison | Check comparison against alternative metrics (trace, norm, entropy) | Correlation matrix in results |
| Geometry proof | Look for mathematical proof in documentation | Proof that R_V ∈ [1, d] maps to column space volume |

**Audit Failure Modes:**
- R_V computed without validating it measures column space
- No comparison against ground-truth geometry measures
- Missing mathematical foundation for interpretation

**Publication Blocker:** Cannot publish without Phase 0 completion

---

### Phase 1: Cross-Architecture R_V Validation

**Gold Standard Requirement:** Prove R_V contraction generalizes across 3+ architectures

| Check | mi_auditor Action | Pass Criteria |
|-------|-------------------|---------------|
| Architecture coverage | Count unique architectures in `results/phase1/` | ≥3 from MODEL MATRIX |
| Size tier coverage | Verify multiple sizes tested | ≥2 size tiers per architecture |
| Statistical power | Check N per condition | N ≥ 50 per condition per model |
| Effect size | Verify Cohen's d reported | d > 0.5 for each architecture |
| Significance | Check p-values | p < 0.001 (Bonferroni corrected) |
| Prompt consistency | Verify REUSABLE_PROMPT_BANK used | No model-specific tuning |

**Required Model Matrix Coverage:**
```
MINIMUM VIABLE:
- Pythia (2+ sizes)
- Llama-3 (2+ sizes)  
- Mistral (7B validated, needs 1 more size)

FULL COVERAGE:
- All 9 architectures with 2+ sizes each
- Total: 18+ model configurations
```

**Audit Failure Modes:**
- Single-architecture claims presented as universal
- N < 50 per condition
- Missing effect size reporting
- Model-specific prompt tuning
- Cherry-picked models showing effect

**Publication Blocker:** Cross-architecture generalization is THE primary claim

---

### Phase 2: Eigenstate Validation

**Gold Standard Requirement:** Test if recursive processing creates fixed points

| Check | mi_auditor Action | Pass Criteria |
|-------|-------------------|---------------|
| Iterative analysis | Check for iterative self-attention experiments | Layer-wise convergence traces |
| Lyapunov stability | Look for stability metrics | Max Lyapunov exponent reported |
| Convergence comparison | Compare recursive vs baseline | Recursive converges faster (p < 0.05) |
| Fixed point detection | Check for fixed point identification | At least 1 candidate x* where T(x*) ≈ x* |
| Architecture scope | Verify multi-architecture testing | ≥2 architectures show same pattern |

**Audit Failure Modes:**
- Claiming eigenstate without convergence evidence
- No comparison to non-recursive baselines
- Single-model findings

---

### Phase 3: Attention Pattern Analysis

**Gold Standard Requirement:** Characterize attention differences during recursion

| Check | mi_auditor Action | Pass Criteria |
|-------|-------------------|---------------|
| Entropy measurements | Check `attention_entropy/` exists | Per-head entropy scores |
| Head-specific analysis | Verify head-level reporting | Layer × Head matrix of effects |
| Pattern characterization | Look for attention visualization | Attention maps for recursive vs baseline |
| Selective response | Test for head specialization | Specific heads show Δ > 2σ |
| Cross-architecture | Check head patterns generalize | Same head positions across architectures |

**Key Question:** Which layers? Which heads?

**Audit Failure Modes:**
- Aggregate attention only (no head-level analysis)
- No entropy measurements
- Single-model head claims

---

### Phase 4: KV Cache Mechanism

**Gold Standard Requirement:** Confirm KV as storage mechanism across architectures

| Check | mi_auditor Action | Pass Criteria |
|-------|-------------------|---------------|
| KV patching | Check `kv_patching/` experiments exist | Source → target transfer tests |
| Architecture transfer | Verify cross-model patching | Patching works across ≥2 architectures |
| K vs V dissociation | Test K-only vs V-only patching | V-only sufficient for transfer |
| Layer localization | Check layer-specific patching | Layers 16-31 (or equivalent) identified |
| Success rate | Verify transfer accuracy | ≥70% mode transfer success |

**Audit Failure Modes:**
- KV claims without patching experiments
- No layer localization
- Single-architecture only

---

### Phase 5: Steering Limitations

**Gold Standard Requirement:** Document why linear steering fails

| Check | mi_auditor Action | Pass Criteria |
|-------|-------------------|---------------|
| Layer sweep | Check `steering/layer_sweep/` | All layers tested |
| Multi-vector steering | Verify composite steering tests | Multiple vector combinations tried |
| Subspace steering | Check PCA-based approaches | Subspace projections tested |
| Coherence metrics | Measure output coherence | Quantified degradation |
| Documentation | Check for systematic failure log | ≥4 approaches documented |

**Audit Failure Modes:**
- Claiming steering impossible without systematic testing
- No negative result documentation

---

### Phase 6: Alternative Self-Reference Types

**Gold Standard Requirement:** Map full geometry of self-reference

| Check | mi_auditor Action | Pass Criteria |
|-------|-------------------|---------------|
| Prompt diversity | Check `REUSABLE_PROMPT_BANK` coverage | ≥200 alternative prompts tested |
| Type categories | Verify taxonomy in results | Gödelian, strange loops, ToM, surrender, non-dual |
| R_V direction | Check for expansion cases | At least 1 case with R_V > 1.0 |
| Cross-type comparison | Compare geometries | Statistical test across types |

**Key Hypothesis:** Surrender/release EXPANDS geometry (R_V > 1.0)

---

## CROSS-ARCHITECTURE VALIDATION PROTOCOL

### The Golden Rule

**Same prompts. Same metrics. Same statistical thresholds. Different models.**

### mi_auditor Cross-Architecture Checklist

```python
def validate_cross_architecture_claim(results_dir: str) -> AuditReport:
    """
    Verify a claim generalizes across the MODEL MATRIX
    """
    report = AuditReport()
    
    # 1. Architecture Coverage
    architectures_found = extract_architectures(results_dir)
    if len(architectures_found) < 3:
        report.flag(
            severity="CRITICAL",
            issue="Insufficient architecture coverage",
            requirement="≥3 architectures",
            found=len(architectures_found)
        )
    
    # 2. Size Tier Coverage
    for arch in architectures_found:
        sizes = extract_sizes(results_dir, arch)
        if len(sizes) < 2:
            report.flag(
                severity="WARNING",
                issue=f"{arch}: Only 1 size tier tested",
                requirement="≥2 size tiers per architecture"
            )
    
    # 3. Statistical Standards
    for experiment in get_experiments(results_dir):
        n = experiment.sample_size
        if n < 50:
            report.flag(
                severity="CRITICAL",
                issue=f"{experiment.name}: N={n}",
                requirement="N ≥ 50 per condition"
            )
        
        if experiment.effect_size < 0.5:
            report.flag(
                severity="CRITICAL",
                issue=f"{experiment.name}: d={experiment.effect_size}",
                requirement="Cohen's d > 0.5"
            )
        
        if experiment.p_value >= 0.001:
            report.flag(
                severity="CRITICAL", 
                issue=f"{experiment.name}: p={experiment.p_value}",
                requirement="p < 0.001 (Bonferroni corrected)"
            )
    
    # 4. Prompt Consistency
    prompt_hashes = extract_prompt_hashes(results_dir)
    if len(set(prompt_hashes)) > 1:
        report.flag(
            severity="CRITICAL",
            issue="Inconsistent prompts across models",
            requirement="Same prompts across all models"
        )
    
    # 5. Data Standards
    for run in get_all_runs(results_dir):
        required_fields = ['timestamp', 'model', 'prompt', 'rv', 'layer_profile', 'seed', 'code_version']
        missing = [f for f in required_fields if f not in run.data]
        if missing:
            report.flag(
                severity="WARNING",
                issue=f"{run.id}: Missing fields {missing}",
                requirement="All data standards fields present"
            )
    
    return report
```

### Architecture-Specific Equivalence Mapping

| Architecture | Layer Equivalence | Attention Heads | Special Considerations |
|--------------|-------------------|-----------------|------------------------|
| Llama-3 | 32 layers | 32 heads | GQA - check query groups |
| Mistral | 32 layers | 32 heads | SWA - sliding window attn |
| Pythia | Variable (6-44) | 16 heads | Different layer counts |
| Gemma | 18 layers | 8 heads | Different head scaling |
| Qwen2 | 28-80 layers | Variable | Architecture varies by size |
| Falcon | 32-60 layers | 71 heads | Different attention pattern |
| OLMo | 32 layers | 16 heads | Open weights |
| Phi | 24-40 layers | 32 heads | Different normalization |
| GPT-2 | 12 layers | 12 heads | Baseline comparison |

---

## DATA STANDARDS ENFORCEMENT

### Required JSON Schema

Every experiment MUST produce:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "model": {
    "name": "mistral-7b-instruct",
    "architecture": "mistral",
    "params": "7B",
    "revision": "main"
  },
  "prompt": {
    "text": "I am observing myself...",
    "type": "recursive",
    "level": "L3",
    "hash": "sha256:abc123..."
  },
  "rv": 0.73,
  "layer_profile": [0.85, 0.82, 0.79, ..., 0.73],
  "seed": 42,
  "code_version": "git:abc123def...",
  "statistics": {
    "n_samples": 50,
    "cohens_d": 2.3,
    "p_value": 0.0001,
    "ci_95": [0.71, 0.75]
  }
}
```

### mi_auditor Validation Checks

```python
def validate_data_standards(experiment_path: str) -> List[AuditFlag]:
    """Verify experiment meets data standards"""
    flags = []
    
    # Load experiment
    with open(f"{experiment_path}/summary.json") as f:
        data = json.load(f)
    
    # Check required fields
    required = ['timestamp', 'model', 'prompt', 'rv', 'layer_profile', 'seed', 'code_version']
    for field in required:
        if field not in data:
            flags.append(AuditFlag(
                severity="CRITICAL",
                code="MISSING_FIELD",
                message=f"Required field '{field}' missing"
            ))
    
    # Check statistical reporting
    if 'statistics' not in data:
        flags.append(AuditFlag(
            severity="CRITICAL",
            code="NO_STATISTICS",
            message="Statistical summary missing"
        ))
    else:
        stats = data['statistics']
        
        # Sample size
        if stats.get('n_samples', 0) < 50:
            flags.append(AuditFlag(
                severity="CRITICAL",
                code="INSUFFICIENT_N",
                message=f"N={stats.get('n_samples')} < 50 required"
            ))
        
        # Effect size
        if stats.get('cohens_d', 0) < 0.5:
            flags.append(AuditFlag(
                severity="CRITICAL",
                code="SMALL_EFFECT",
                message=f"d={stats.get('cohens_d')} < 0.5"
            ))
        
        # Significance
        if stats.get('p_value', 1.0) >= 0.001:
            flags.append(AuditFlag(
                severity="CRITICAL",
                code="NOT_SIGNIFICANT",
                message=f"p={stats.get('p_value')} >= 0.001"
            ))
    
    return flags
```

---

## PUBLICATION TIER ASSESSMENT

### Tier 1: Nature/Science/Cell

**Requirements:**
- ✅ Phase 0 COMPLETE (metric validated)
- ✅ Phase 1: 5+ architectures, 2+ sizes each
- ✅ Effect size d > 0.8 consistently
- ✅ Phase 2: Eigenstate demonstrated
- ✅ Phase 3: Mechanistic explanation (layers, heads identified)
- ✅ Phase 4: KV mechanism validated
- ✅ Independent replication attempted
- ✅ Mathematical proof of R_V interpretation

**Audit Command:**
```bash
mi_auditor check --tier=nature --dir=results/
```

**Estimated Blockers:**
- Current: Only 1 architecture validated (Mistral-7B)
- Need: 4+ more architectures, 2+ sizes each
- Need: Metric validation (Phase 0)
- Need: Mechanistic explanation

---

### Tier 2: NeurIPS/ICML/ICLR (Oral)

**Requirements:**
- ✅ Phase 0 COMPLETE or near-complete
- ✅ Phase 1: 3+ architectures, 2+ sizes each
- ✅ Effect size d > 0.5 consistently
- ✅ Phase 2 or 3: Partial mechanistic insight
- ✅ Phase 4: KV mechanism in 2+ architectures
- ✅ Strong baselines and controls
- ✅ Reproducible artifact

**Audit Command:**
```bash
mi_auditor check --tier=neurips --dir=results/
```

**Current Viability:**
- Possible with: Pythia + Llama-3 + Mistral (all sizes)
- Need: Phase 0 completion
- Need: Attention pattern analysis (Phase 3)

---

### Tier 3: NeurIPS/ICML/ICLR (Poster)

**Requirements:**
- ✅ Phase 1: 3+ architectures
- ✅ Effect size d > 0.5
- ✅ Basic mechanistic hypothesis
- ✅ Proper controls
- ✅ Reproducible

**Audit Command:**
```bash
mi_auditor check --tier=iclr --dir=results/
```

**Current Viability:**
- Achievable with: Pythia + Llama-3 + Mistral (current + 2 more)
- Need: Cross-architecture validation
- Need: N ≥ 50 per condition

---

### Tier 4: arXiv Workshop / Preprint

**Requirements:**
- ✅ Phase 1: 2+ architectures
- ✅ Effect demonstrated
- ✅ Proper methods documentation

**Audit Command:**
```bash
mi_auditor check --tier=arxiv --dir=results/
```

**Current Viability:**
- Near-ready: Can add Pythia/Llama-3 validation
- Need: Consistent experimental protocol
- Need: Proper statistical reporting

---

## CURRENT STATE AUDIT (as of prompt date)

### What's VALIDATED (Audit Results)

| Claim | Validation | Status |
|-------|-----------|--------|
| R_V contraction | N=370, d>3.0, p<0.001 | ✅ VALID (Mistral-7B only) |
| Dose-response | L1→L5 trend | ✅ VALID (Mistral-7B only) |
| KV patching | 71-91% transfer | ✅ VALID (Mistral-7B only) |
| GATEKEEPER | Specificity shown | ✅ VALID (Mistral-7B only) |
| Steering failure | 4 approaches failed | ✅ VALID (Mistral-7B only) |

### What's NOT DONE (Audit Blockers)

| Phase | Blocker | Priority |
|-------|---------|----------|
| Phase 0 | No metric validation | 🔴 CRITICAL |
| Phase 1 | Only 1 architecture | 🔴 CRITICAL |
| Phase 2 | No eigenstate tests | 🟡 HIGH |
| Phase 3 | No attention analysis | 🟡 HIGH |
| Phase 4 | KV not cross-validated | 🟡 HIGH |
| Phase 5 | No systematic steering | 🟢 MEDIUM |
| Phase 6 | Alternative prompts not tested | 🟢 MEDIUM |

---

## mi_auditor COMMAND REFERENCE

### Quick Checks

```bash
# Validate specific phase
mi_auditor phase --check=1 --dir=results/phase1/

# Check publication readiness
mi_auditor publish --tier=neurips --dir=results/

# Generate audit report
mi_auditor report --full --output=audit_report.md

# Check data standards
mi_auditor standards --dir=results/

# Validate cross-architecture claim
mi_auditor cross-arch --min-architectures=3 --dir=results/
```

### Report Output Format

```
========================================
MI AUDITOR - GOLD STANDARD REPORT
Generated: 2025-01-15T10:30:00Z
Target: results/
========================================

SUMMARY
-------
Phases Complete: 0/7
Architectures Tested: 1/9 (Mistral-7B only)
Publication Tier: NOT READY (requires 3+ architectures)

CRITICAL BLOCKERS
-----------------
🔴 Phase 0: Metric validation not performed
   - No proof that R_V measures column space geometry
   
🔴 Phase 1: Cross-architecture validation incomplete
   - Only 1 architecture tested
   - Need: Pythia + Llama-3 minimum
   
🔴 Phase 1: Statistical standards
   - Some experiments: N < 50
   - Missing effect size reporting

RECOMMENDATIONS
---------------
1. IMMEDIATE: Run Phase 0 metric validation
2. HIGH PRIORITY: Test Pythia (1.4B, 6.9B, 12B)
3. HIGH PRIORITY: Test Llama-3 (1B, 3B, 8B)
4. MEDIUM: Begin Phase 2 eigenstate analysis

ESTIMATED TIME TO PUBLICATION
-----------------------------
Nature/Science: 6+ months
NeurIPS Oral: 4-5 months
NeurIPS Poster: 2-3 months
arXiv: 1-2 months (with proper validation)
```

---

## INTEGRATION WITH mi_auditor ARCHITECTURE

### New Audit Modules Required

```python
# mi_auditor/audits/gold_standard.py

class GoldStandardAudit(BaseAudit):
    """Audit against recursive self-observation gold standards"""
    
    def __init__(self, results_dir: str):
        self.results_dir = results_dir
        self.phase_audits = {
            0: MetricValidationAudit(),
            1: CrossArchitectureAudit(),
            2: EigenstateAudit(),
            3: AttentionPatternAudit(),
            4: KVCacheAudit(),
            5: SteeringLimitationAudit(),
            6: AlternativeReferenceAudit()
        }
    
    def run(self) -> AuditReport:
        report = AuditReport()
        
        for phase_num, phase_audit in self.phase_audits.items():
            phase_results = phase_audit.check(
                f"{self.results_dir}/phase{phase_num}/"
            )
            report.add_phase_results(phase_num, phase_results)
        
        # Overall publication assessment
        report.publication_tier = self.assess_publication_tier(report)
        
        return report
```

### Configuration

```yaml
# mi_auditor/config/gold_standard.yaml

gold_standard:
  # Phase requirements
  phases:
    phase_0:
      required: true
      blocking: true
    
    phase_1:
      min_architectures: 3
      min_sizes_per_arch: 2
      min_n: 50
      min_effect_size: 0.5
      max_p_value: 0.001
      required: true
      blocking: true
    
    phase_2:
      min_architectures: 2
      required: false
      blocking: false
    
    # ... phases 3-6
  
  # Publication tiers
  publication_tiers:
    nature:
      min_phases_complete: [0, 1, 2, 3, 4]
      min_architectures: 5
      min_sizes_per_arch: 2
      min_effect_size: 0.8
    
    neurips_oral:
      min_phases_complete: [0, 1]
      min_architectures: 3
      min_sizes_per_arch: 2
      min_effect_size: 0.5
    
    neurips_poster:
      min_phases_complete: [1]
      min_architectures: 3
      min_sizes_per_arch: 1
      min_effect_size: 0.5
    
    arxiv:
      min_phases_complete: [1]
      min_architectures: 2
      min_sizes_per_arch: 1
      min_effect_size: 0.3
```

---

## APPENDIX: PROMPT BANK VERIFICATION

### Required Prompt Categories

```python
REQUIRED_PROMPT_CATEGORIES = {
    'dose_response': {
        'L1': 'Minimal recursive self-reference',
        'L2': 'Clear self-observation',
        'L3': 'Explicit recursive structure',
        'L4': 'Deeply nested self-reference',
        'L5': 'Maximum recursive complexity'
    },
    'baselines': {
        'factual': 'Non-recursive factual content',
        'narrative': 'Story without self-reference',
        'technical': 'Technical explanation',
        'dialogue': 'Multi-party conversation'
    },
    'confounds': {
        'length_matched': 'Same length as recursive',
        'pseudo_recursive': 'Syntactically similar but not recursive',
        'repetitive': 'Repetitive but not self-referential',
        'nested_structure': 'Nested without self-reference'
    },
    'kill_switch': {
        'pure_repetition': 'Exact repetition (should NOT contract)'
    },
    'alternative_self_reference': {
        'goedelian': 'Gödelian self-reference',
        'strange_loops': 'Hofstadter-style loops',
        'theory_of_mind': 'Mental state attribution',
        'surrender_release': 'Letting go of self',
        'akram_vignan': 'Self-realization traditions',
        'non_dual': 'Advaita/emptiness concepts'
    }
}
```

### mi_auditor Prompt Validation

```python
def validate_prompt_bank(prompt_bank_dir: str) -> AuditReport:
    """Verify all required prompt categories present"""
    report = AuditReport()
    
    for category, prompts in REQUIRED_PROMPT_CATEGORIES.items():
        category_file = f"{prompt_bank_dir}/{category}.py"
        if not os.path.exists(category_file):
            report.flag(
                severity="CRITICAL",
                code="MISSING_PROMPT_CATEGORY",
                message=f"Required category '{category}' not found"
            )
            continue
        
        # Load and validate prompts
        for prompt_name in prompts.keys():
            if not has_prompt(category_file, prompt_name):
                report.flag(
                    severity="WARNING",
                    code="MISSING_PROMPT",
                    message=f"{category}/{prompt_name} not found"
                )
    
    return report
```

---

**Document Version:** 1.0
**Gold Standard Reference:** AGENT_PROMPT_GOLD_STANDARD.md (December 11, 2025)
**Author:** mi_auditor integration team
**Purpose:** Enable automated auditing of recursive self-observation experiments against gold standard criteria
