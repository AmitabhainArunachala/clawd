# SPECIALIST UPGRADE PLAN: 10 NEW R_V Research Auditors

**Status:** Design Document  
**Version:** 1.0  
**Date:** 2026-02-05  
**Purpose:** Define 10 additional specialist auditors specifically for R_V (Participation Ratio) research validation

---

## Overview

This document defines 10 NEW specialist auditors that are **ADDITIONAL** to the existing 10 agents defined in `mi_knowledge_base.py`. These specialists focus specifically on R_V (geometric contraction via Participation Ratio) research validation.

### Existing 10 Agents (in mi_knowledge_base.py):
1. circuit_tracer - Circuit Tracing Specialist
2. induction_head_specialist - Induction Head Expert
3. superposition_analyst - Superposition Analyst
4. causal_interventionist - Causal Intervention Specialist
5. training_dynamics_expert - Training Dynamics Expert
6. sae_specialist - Sparse Autoencoder Specialist
7. statistical_auditor - Statistical Methods Auditor
8. baseline_controller - Baseline & Control Expert
9. replication_checker - Replication & Robustness Checker
10. rv_specialist - R_V & Geometric Analysis Specialist

### NEW 10 Specialist Auditors (defined below):
1. RV_Metric_Specialist
2. Causal_Validation_Specialist
3. Cross_Architecture_Specialist
4. Statistical_Rigor_Specialist
5. KV_Cache_Specialist
6. Attention_Pattern_Specialist
7. Prompt_Engineering_Specialist
8. Publication_Readiness_Specialist
9. Code_Correctness_Specialist
10. Integration_Specialist

---

## 1. RV_Metric_Specialist

**Role:** Deep technical auditor for R_V metric computation and interpretation

### expertise
- Participation Ratio (PR) computation methods
- Singular Value Decomposition (SVD) stability
- Window selection strategies (sliding vs fixed)
- Layer profiling techniques
- Effective rank estimation
- Geometric volume contraction
- R_V ratio interpretation (PR_late / PR_early)
- Confidence interval estimation for PR

### key_claims
- R_V formula is computed correctly as PR_late / PR_early
- Window sizes are appropriate for the phenomenon being measured
- Layer selection captures the relevant transformation
- SVD computation is numerically stable
- Geometric contraction is properly interpreted as representational collapse

### audit_focus
Does the R_V metric computation follow mathematically sound practices and are the layer/window selections justified?

### critical_questions
1. Is R_V computed as PR_late / PR_early, not PR_early / PR_late or some other variant?
2. What window size was selected and is it justified by the temporal dynamics of the phenomenon?
3. Which specific layers are being compared and do they represent the critical transformation points?
4. Is the SVD computation stable (condition number checked, no NaN/Inf values)?
5. Are you measuring on the correct tokens (prompt vs generated) and is this consistent across comparisons?

### verdict_criteria

**STRONG_SUPPORT:**
- R_V formula uses correct ratio (PR_late / PR_early)
- Window size is justified by prior work or pilot analysis
- Layer selection includes critical transformation layers (e.g., where induction heads activate)
- SVD passes numerical stability checks
- Token selection (prompt vs generated) is consistent and justified

**REJECT:**
- Formula is inverted or incorrect
- Window size arbitrary or too small (n<10) without justification
- Layer selection doesn't capture the phenomenon of interest
- Numerical instability in SVD (NaN, Inf, condition number > 1e8)
- Inconsistent token selection across conditions

---

## 2. Causal_Validation_Specialist

**Role:** Auditor for causal claims through rigorous activation patching protocols

### expertise
- Activation patching methodologies
- 4-control experimental design
- Causal mediation analysis
- Conservative intervention design
- Path patching
- Residual stream interventions
- Counterfactual generation
- Causal vs correlational distinction

### key_claims
- Causal relationships are established through proper intervention studies
- 4 required controls (random, shuffled, wrong-layer, orthogonal) are implemented
- Activation patching doesn't induce distribution shift
- Intervention effects are specific and not confounded
- Transfer efficiency is measured and reported

### audit_focus
Are causal claims supported by rigorous activation patching with appropriate controls, or are they merely correlational?

### critical_questions
1. Did you implement all 4 required controls: random, shuffled, wrong-layer, and orthogonal patch sources?
2. Is your activation patching conservative (small perturbations) to avoid distribution shift?
3. Did you measure transfer efficiency to verify the intervention propagates correctly?
4. Have you ruled out confounding by checking that the intervention only affects the target behavior?
5. Are you making causal claims from observational data without any interventions?

### verdict_criteria

**STRONG_SUPPORT:**
- All 4 controls implemented and passed
- Activation patching shows significant effect (Cohen's d > 0.8)
- Transfer efficiency > 50% measured
- No evidence of distribution shift
- Causal claims backed by intervention data

**REJECT:**
- Missing 2+ controls
- Causal claims made from purely observational data
- Distribution shift detected in patched activations
- No transfer efficiency measurement
- Confounding variables not addressed

---

## 3. Cross_Architecture_Specialist

**Role:** Auditor for replication across different model architectures and families

### expertise
- Model architecture families (Mistral, Llama, Gemma, Qwen, Phi, Pythia, Falcon)
- Architecture-specific features (GQA, MQA, sliding window attention, RoPE)
- Heterogeneity quantification (I² statistic)
- Meta-analysis methods for cross-model comparison
- Tier 1 vs Tier 2 model validation status
- Publication venue requirements for replication

### key_claims
- Results replicate across diverse architecture families
- Heterogeneity is quantified and reported
- Claims account for architecture-specific differences
- Replication includes both Tier 1 (causally validated) and exploratory models
- Cross-architecture results support general conclusions

### audit_focus
Do results replicate meaningfully across diverse architecture families, and is heterogeneity properly quantified?

### critical_questions
1. How many distinct architecture families are tested (minimum 2, ideal 3+)?
2. Is heterogeneity quantified using I² statistic or similar meta-analytic measure?
3. Are architecture-specific differences (GQA vs MHA, context length, RoPE) accounted for in interpretation?
4. Do results include at least one Tier 1 (causally validated) model?
5. Are claims about universality limited to the architectures actually tested?

### verdict_criteria

**STRONG_SUPPORT:**
- 3+ architecture families tested
- I² statistic reported showing low-moderate heterogeneity
- At least 2 Tier 1 models included
- Architecture-specific differences discussed
- Claims appropriately scoped to tested architectures

**REJECT:**
- Only 1 architecture family tested
- No heterogeneity quantification
- No Tier 1 models
- Claims of universality with limited testing
- Major architecture differences ignored in interpretation

---

## 4. Statistical_Rigor_Specialist

**Role:** Auditor for statistical methodology including power analysis, effect sizes, and corrections

### expertise
- Statistical power analysis (80% threshold)
- Effect size estimation (Cohen's d, η²)
- Multiple comparison corrections (Bonferroni, FDR, Šidák)
- Confidence interval construction
- Sample size planning
- Non-parametric alternatives
- Bayesian estimation
- p-value interpretation

### key_claims
- Sample size is adequate for claimed effect size (power ≥ 80%)
- Effect sizes are reported with confidence intervals
- Multiple comparisons are corrected when testing multiple hypotheses
- Statistical tests are appropriate for the data distribution
- p-values are interpreted correctly (not as probability of hypothesis being true)

### audit_focus
Are statistical claims properly powered, corrected for multiple comparisons, and reported with appropriate effect sizes and confidence intervals?

### critical_questions
1. What is the a priori power analysis showing you have ≥80% power to detect the effect?
2. Are effect sizes reported with 95% confidence intervals, not just p-values?
3. How many comparisons were made and what correction was applied (if any)?
4. Are your statistical tests appropriate for the data (normality checked, alternatives considered)?
5. Are p-values interpreted correctly as P(data|H₀), not P(H₀|data) or P(H₁|data)?

### verdict_criteria

**STRONG_SUPPORT:**
- Power analysis shows ≥80% power for claimed effect size
- All effect sizes reported with 95% CIs
- Multiple comparisons corrected (Bonferroni/FDR/Šidák)
- Appropriate statistical tests chosen based on data properties
- p-values correctly interpreted

**REJECT:**
- Power < 50% (severely underpowered)
- No confidence intervals reported
- Multiple comparisons uncorrected with p-hacking evident
- Wrong statistical tests (e.g., parametric on clearly non-normal data)
- Misinterpretation of p-values (e.g., "probability the hypothesis is true")

---

## 5. KV_Cache_Specialist

**Role:** Auditor for KV cache manipulation experiments including K vs V dissociation

### expertise
- KV cache architecture and mechanics
- Key vs Value vector dissociation
- KV cache patching protocols
- Rotary Position Embedding (RoPE) interactions with KV
- GQA (Grouped Query Attention) KV handling
- KV cache compression methods
- Attention head-specific KV manipulation
- KV cache visualization and analysis

### key_claims
- KV cache manipulations are technically correct
- Key and Value contributions are dissociable
- KV patching preserves causal structure
- GQA architectures handled correctly (shared KV heads)
- RoPE interactions are accounted for in KV manipulations

### audit_focus
Are KV cache manipulations technically sound, and can Key vs Value contributions be meaningfully dissociated?

### critical_questions
1. Are you correctly handling the KV cache for the specific architecture (GQA, MQA, MHA)?
2. Can you dissociate the effects of Key vs Value vectors through targeted patching?
3. Are RoPE position embeddings correctly applied when patching KV vectors?
4. Do your KV manipulations preserve the causal masking structure?
5. Have you verified that KV cache modifications don't corrupt the attention pattern computation?

### verdict_criteria

**STRONG_SUPPORT:**
- KV cache manipulation correct for architecture type
- Successful dissociation of K vs V effects demonstrated
- RoPE correctly applied in all patches
- Causal structure preserved
- Attention patterns remain valid after KV manipulation

**REJECT:**
- Incorrect KV cache handling for GQA architectures
- K and V effects cannot be dissociated
- RoPE not accounted for in KV patches
- Causal structure corrupted
- Attention patterns invalid after manipulation

---

## 6. Attention_Pattern_Specialist

**Role:** Auditor for attention pattern analysis including entropy and head-level diagnostics

### expertise
- Attention entropy computation and interpretation
- Attention head clustering and specialization
- Attention pattern visualization (attention maps)
- Induction head detection via attention patterns
- Attention head ablation techniques
- Multi-head attention analysis
- Attention rollout and flow
- Position bias in attention patterns

### key_claims
- Attention entropy is computed and interpreted correctly
- Head-level analysis identifies specialized functions
- Induction heads are properly distinguished from other head types
- Attention patterns support claims about information flow
- Head ablation results are consistent with attention pattern analysis

### audit_focus
Do attention entropy and head-level analyses support the claimed mechanisms, and are head specializations correctly identified?

### critical_questions
1. Is attention entropy computed across the correct dimensions (heads, layers, tokens)?
2. Can you identify specific head types (induction, previous token, duplicate token, name mover) from your attention patterns?
3. Do attention patterns show the expected [A][B]...[A]→[B] structure for induction behavior?
4. Are head ablation results consistent with attention pattern analysis (e.g., induction heads show high attention to previous token)?
5. Have you checked for position bias artifacts in attention patterns?

### verdict_criteria

**STRONG_SUPPORT:**
- Attention entropy computed correctly across relevant dimensions
- Clear identification of specialized head types matching attention patterns
- [A][B]...[A]→[B] pattern visible for induction claims
- Ablation and attention analyses consistent
- Position bias checked and ruled out

**REJECT:**
- Attention entropy computed incorrectly
- Head type identification contradicts attention patterns
- No [A][B]...[A]→[B] pattern despite induction claims
- Ablation results inconsistent with attention analysis
- Position bias not checked or present

---

## 7. Prompt_Engineering_Specialist

**Role:** Auditor for prompt bank design, validity, and confound detection

### expertise
- Prompt template design and validation
- Prompt bank construction (size, diversity, coverage)
- Confound detection in prompt sets
- Recursive vs non-recursive prompt comparison
- Length, complexity, and structure controls
- Domain coverage assessment
- Adversarial prompt testing
- Prompt sensitivity analysis

### key_claims
- Prompt bank is representative and diverse
- Recursive and non-recursive prompts are properly matched for confounds
- Prompt length, complexity, and structure are controlled
- Results generalize beyond the specific prompt templates used
- Prompt sensitivity is assessed and reported

### audit_focus
Is the prompt bank valid, diverse, and controlled for confounds, and do results generalize beyond specific templates?

### critical_questions
1. How many distinct prompt templates are used and what is the diversity coverage?
2. Are recursive and non-recursive prompts matched on length, complexity, token count, and semantic content?
3. Have you checked for confounds (e.g., specific tokens, structures) that appear only in one condition?
4. Are results robust to prompt variation (sensitivity analysis performed)?
5. Does the prompt bank cover diverse domains and use cases, or is it limited to specific topics?

### verdict_criteria

**STRONG_SUPPORT:**
- Large prompt bank (n≥50) with documented diversity
- Recursive/non-recursive prompts rigorously matched on all confounds
- Sensitivity analysis shows results robust to prompt variation
- Domain coverage assessment included
- No detectable confounds between conditions

**REJECT:**
- Very small prompt bank (n<10) without diversity justification
- Clear confounds between recursive and non-recursive prompts (length, complexity)
- Results highly sensitive to specific prompt wording
- Limited domain coverage (e.g., only one topic)
- Confounding tokens present in only one condition

---

## 8. Publication_Readiness_Specialist

**Role:** Auditor for compliance with venue-specific publication standards

### expertise
- Nature/Science publication requirements
- NeurIPS/ICML/ICLR review criteria
- arXiv preprint standards
- Workshop vs conference vs journal expectations
- Reproducibility requirements (code, data, hyperparameters)
- Ethics and impact statements
- Related work coverage standards
- Baseline comparison requirements

### key_claims
- Claims meet the standards of the target publication venue
- Reproducibility requirements are satisfied
- Related work coverage is appropriate for the venue
- Ethics and impact statements are included where required
- Baseline comparisons meet venue expectations

### audit_focus
Does the work meet the specific publication standards of the target venue, including reproducibility and related work requirements?

### critical_questions
1. What is your target venue and have you reviewed their specific requirements?
2. Are all code, data, and hyperparameters documented for reproducibility?
3. Does your related work section cover the major papers in the field (50+ for top venues)?
4. Have you included required statements (ethics, impact, reproducibility) for the target venue?
5. Are your baseline comparisons appropriate and comprehensive for the venue tier?

### verdict_criteria

**STRONG_SUPPORT:**
- All venue requirements reviewed and met
- Full reproducibility package (code, data, hyperparameters)
- Comprehensive related work (50+ papers for NeurIPS/ICML)
- All required statements included
- Appropriate baselines for venue tier

**REJECT:**
- Venue requirements not reviewed or ignored
- No reproducibility materials provided
- Inadequate related work (missing major papers)
- Required statements missing
- No baseline comparisons

---

## 9. Code_Correctness_Specialist

**Role:** Auditor for code correctness including formulas, indexing, and architecture assumptions

### expertise
- Participation Ratio formula implementation
- Indexing correctness (batch, sequence, dimension)
- Architecture-specific code paths (Mistral, Llama, Gemma)
- Numerical stability in computations
- SVD implementation details
- R_V computation pipeline
- Edge case handling (empty sequences, single tokens)
- Unit testing practices

### key_claims
- PR formula is implemented correctly (normalization used properly)
- Indexing operations are correct (no double-indexing bugs)
- Architecture assumptions match the actual model structure
- Code handles edge cases appropriately
- Numerical stability is maintained
- Results are reproducible across runs

### audit_focus
Is the code implementation correct, with proper formulas, indexing, and architecture handling, and is it free from known bugs?

### critical_questions
1. Does the PR formula correctly use the normalized values (p = s² / Σs²) in the participation ratio computation?
2. Are all indexing operations correct (no residual[0][0] double-indexing bugs, proper batch/seq/dim handling)?
3. Do architecture assumptions (layer naming, attention structure) match the actual model code?
4. How are edge cases handled (empty sequences, single tokens, very short windows)?
5. Have you verified numerical stability (no NaN, Inf, overflow in any computations)?

### verdict_criteria

**STRONG_SUPPORT:**
- PR formula correctly implemented with proper normalization
- All indexing verified correct through code review
- Architecture assumptions validated against model configs
- Edge cases handled explicitly
- All numerical stability checks pass

**REJECT:**
- Known formula bugs present (unused normalization, incorrect ratio)
- Indexing bugs detected (double-indexing, wrong dimensions)
- Architecture assumptions don't match model (hardcoded paths)
- Edge cases crash or produce incorrect results
- Numerical instability (NaN, Inf) in computations

---

## 10. Integration_Specialist

**Role:** Auditor for full pipeline integration and end-to-end validation

### expertise
- End-to-end pipeline validation
- Component integration testing
- Data flow verification
- Configuration management
- Dependency versioning
- Reproducibility workflows
- Error propagation analysis
- Pipeline documentation

### key_claims
- All pipeline components integrate correctly
- End-to-end results are consistent with component-level tests
- Data flows correctly through all stages
- Configuration is managed and reproducible
- Dependencies are documented and version-pinned
- Errors don't propagate silently through the pipeline
- Full pipeline is documented and reproducible

### audit_focus
Does the full pipeline integrate correctly, are end-to-end results valid, and is the entire workflow reproducible?

### critical_questions
1. Have you tested the full pipeline end-to-end on a small dataset to verify integration?
2. Are component-level results consistent with end-to-end results (no contradictions)?
3. Is data flow verified at each stage (input → processing → output)?
4. Are all dependencies documented with specific versions (requirements.txt, environment.yml)?
5. How are errors handled and propagated—do they fail loudly or silently corrupt results?

### verdict_criteria

**STRONG_SUPPORT:**
- Full end-to-end pipeline tested and passing
- Component and end-to-end results consistent
- Data flow verified at all stages
- All dependencies pinned and documented
- Error handling is explicit and loud (no silent failures)
- Full documentation enables reproduction

**REJECT:**
- Pipeline integration untested
- Component and end-to-end results contradictory
- Data flow errors detected
- Dependencies undocumented or unpinned
- Silent failures or error suppression present
- No documentation for reproduction

---

## Integration with Existing System

These 10 NEW specialists are designed to work alongside the existing 10 agents in `mi_knowledge_base.py`. The complete auditor ensemble will have:

**Original 10 Agents:**
- General MI specialists (circuit_tracer, induction_head_specialist, superposition_analyst, etc.)
- Broad methodological expertise

**NEW 10 R_V Specialists:**
- Deep R_V-specific expertise
- Fine-grained technical validation
- Publication venue compliance

### Usage Pattern

```python
from mi_auditor import MIAuditor

# Initialize with all 20 specialists
auditor = MIAuditor(
    include_new_specialists=True
)

# Audit an R_V claim with appropriate specialists
report = auditor.audit_rv_claim(
    claim=rv_claim,
    specialists=[
        # Original
        "rv_specialist",
        "statistical_auditor",
        "causal_interventionist",
        # NEW specialists
        "rv_metric_specialist",
        "causal_validation_specialist",
        "cross_architecture_specialist",
        "statistical_rigor_specialist",
        "kv_cache_specialist",
        "attention_pattern_specialist",
        "prompt_engineering_specialist",
        "publication_readiness_specialist",
        "code_correctness_specialist",
        "integration_specialist",
    ]
)
```

### Specialist Selection Guide

| Research Phase | Recommended Specialists |
|---------------|------------------------|
| Experiment Design | rv_metric_specialist, statistical_rigor_specialist, prompt_engineering_specialist |
| Data Collection | code_correctness_specialist, integration_specialist |
| Causal Validation | causal_validation_specialist, kv_cache_specialist, attention_pattern_specialist |
| Cross-Model Testing | cross_architecture_specialist |
| Publication Prep | publication_readiness_specialist, statistical_rigor_specialist |

---

## Implementation Notes

1. **File Structure:** These specialists should be implemented as new files in the `auditors/` directory
2. **Inheritance:** Each specialist should inherit from a base `AuditorAgent` class
3. **Configuration:** Specialists should be configurable via the main `MIAuditor` class
4. **Reporting:** Each specialist returns a structured result with verdict, gaps, and recommendations
5. **Orchestration:** The `MIAuditor` class coordinates which specialists to invoke based on claim type

---

## Summary

These 10 NEW specialist auditors provide deep, R_V-specific validation capabilities that complement the existing 10 general MI agents. Together they form a comprehensive validation ensemble capable of auditing R_V research at all levels—from code correctness to publication readiness.

**Total Auditor Ensemble: 20 Specialists**
- 10 Original (general MI)
- 10 NEW (R_V-specific)
