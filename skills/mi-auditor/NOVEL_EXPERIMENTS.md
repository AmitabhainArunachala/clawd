# NOVEL_EXPERIMENT_GENERATOR — mi_auditor v6.0
## Comprehensive R_V Research Expansion Program
### 25 Novel Experiments Across 5 Categories

---

**Version:** 6.0  
**Date:** 2026-02-05  
**Status:** Proposal — Ready for GPU Allocation  
**Estimated GPU Hours:** 2,400-4,800 (full program)  

---

## Executive Summary

This document proposes **25 novel experiments** building on our validated R_V geometric contraction findings. These experiments are designed to:

1. **Extend** R_V to new architectures, scales, and model classes
2. **Deepen** our understanding of what mediates R_V contraction
3. **Bridge** R_V to behavioral metrics and consciousness markers
4. **Validate** alternative methodologies and metrics
5. **Test** theoretical predictions from superposition theory

Each experiment includes hypothesis, method, expected outcome, significance, difficulty, priority, and **mi_auditor validation criteria**.

---

## 📊 Quick Reference: Experiment Inventory

| # | Category | Experiment | Difficulty | Priority | GPU Hrs |
|---|----------|------------|------------|----------|---------|
| 1 | Extension | R_V in Vision Transformers | Medium | P1 | 120 |
| 2 | Extension | R_V in Multimodal LLMs | Hard | P1 | 200 |
| 3 | Extension | R_V Scaling Laws (70B→400B) | Hard | P0 | 800 |
| 4 | Extension | R_V in Encoder-Only (BERT) | Easy | P2 | 40 |
| 5 | Extension | R_V in State Space Models | Hard | P1 | 300 |
| 6 | Deepening | SAE Feature Decomposition | Medium | P0 | 250 |
| 7 | Deepening | Attention Head Attribution | Medium | P0 | 180 |
| 8 | Deepening | MLP vs Attention R_V Split | Medium | P1 | 150 |
| 9 | Deepening | Temporal Dynamics of R_V | Hard | P1 | 400 |
| 10 | Deepening | Token-Level R_V Trajectories | Medium | P2 | 100 |
| 11 | Bridge | R_V → Truthfulness Correlation | Medium | P0 | 200 |
| 12 | Bridge | R_V → Hallucination Detection | Medium | P0 | 180 |
| 13 | Bridge | R_V → Confidence Calibration | Easy | P1 | 80 |
| 14 | Bridge | R_V → Adversarial Robustness | Hard | P2 | 350 |
| 15 | Bridge | R_V → Chain-of-Thought Quality | Medium | P1 | 120 |
| 16 | Methodology | Alternative Metrics Validation | Easy | P2 | 60 |
| 17 | Methodology | Bootstrap Confidence Intervals | Easy | P1 | 40 |
| 18 | Methodology | Cross-Architecture Standardization | Medium | P1 | 150 |
| 19 | Methodology | Real-Time R_V Monitoring | Medium | P2 | 100 |
| 20 | Methodology | Automated Causal Discovery | Hard | P2 | 500 |
| 21 | Theoretical | Superposition Collapse Prediction | Medium | P0 | 200 |
| 22 | Theoretical | Geometry of Truth Hypothesis | Hard | P0 | 300 |
| 23 | Theoretical | Phase Transitions in R_V | Hard | P1 | 400 |
| 24 | Theoretical | R_V as Capacity Measure | Medium | P2 | 150 |
| 25 | Theoretical | Information-Theoretic Bounds | Hard | P2 | 250 |

**Total GPU Estimate:** 2,840-5,170 hours (depending on replications)

---

## Category 1: Extension Experiments

### Experiment 1: R_V in Vision Transformers (ViT)

**Hypothesis:** Vision transformers exhibit R_V contraction when processing recursive visual patterns (e.g., fractals, repeating textures), analogous to recursive text prompts.

**Method:**
1. Load ViT-L/16, ViT-H/14, DINOv2
2. Create recursive visual stimuli: fractal patterns, nested shapes, self-similar textures
3. Measure R_V across layers for: recursive images vs. non-recursive controls
4. Compare attention rollout patterns with R_V contraction locations

**Expected Outcome:**
- R_V < 1.0 at deep layers for recursive patterns
- Stronger contraction for higher fractal recursion depth
- Attention rollout shows concentration on self-similar regions

**Why It Matters:**
Extends R_V from language to vision, testing whether geometric contraction is a **general property of transformers processing recursive structure** (not language-specific). Connects to **Dosovitskiy et al. (2021)** ViT architecture.

**Difficulty:** Medium  
**Priority:** P1  
**GPU Hours:** ~120

**Knowledge Base Connections:**
- **Dosovitskiy et al. (2021)** — An Image is Worth 16x16 Words (ViT architecture)
- **Caron et al. (2021)** — Emerging Properties in Self-Supervised Vision Transformers (DINO)
- **Elhage et al. (2021)** — Mathematical Framework (applies to any transformer)

**mi_auditor AUDIT:**
```python
auditor.audit_experiment({
    "claim": "ViT shows R_V contraction on recursive visual patterns",
    "controls": ["non-recursive images", "random noise", "uniform textures"],
    "statistical_test": "paired_t_test",
    "effect_size_threshold": "cohens_d > 0.8",
    "cross_arch": ["ViT-L/16", "ViT-H/14", "DINOv2-g"],
    "validation": ["attention_rollout_correlation", "ablation_study"]
})
```

---

### Experiment 2: R_V in Multimodal LLMs (CLIP, LLaVA, GPT-4V)

**Hypothesis:** Multimodal transformers show **cross-modal R_V coupling** — recursive structure in one modality (e.g., repeating visual pattern) induces contraction in text processing layers.

**Method:**
1. Test CLIP, LLaVA-1.5, InternVL2
2. Create aligned recursive stimuli: "A fractal tree with branches that look like smaller trees" + actual fractal image
3. Measure R_V separately for vision and language branches
4. Test for cross-modal correlation in contraction timing

**Expected Outcome:**
- R_V contracts in both modalities when aligned recursive structure present
- Cross-modal coupling stronger in fused architectures (LLaVA > CLIP)
- Layer alignment between vision contraction and language contraction

**Why It Matters:**
Tests whether R_V reflects **abstract structural processing** independent of modality. Critical for understanding multimodal reasoning. Connects to **Radford et al. (2021)** CLIP and **Liu et al. (2023)** LLaVA.

**Difficulty:** Hard (multimodal complexity)  
**Priority:** P1  
**GPU Hours:** ~200

**Knowledge Base Connections:**
- **Radford et al. (2021)** — Learning Transferable Visual Models (CLIP)
- **Liu et al. (2023)** — Visual Instruction Tuning (LLaVA)
- **Zhang et al. (2024)** — InternVL: Scaling up Vision Foundation Models

**mi_auditor AUDIT:**
```python
auditor.audit_multimodal({
    "claim": "Cross-modal R_V coupling exists in multimodal LLMs",
    "modalities": ["vision", "language"],
    "controls": ["unimodal_recursive", "cross_modal_non_recursive"],
    "coupling_metric": "pearson_correlation",
    "threshold": "r > 0.5, p < 0.01",
    "architecture_types": ["dual_encoder", "fused"]
})
```

---

### Experiment 3: R_V Scaling Laws (70B → 400B Parameters)

**Hypothesis:** R_V contraction follows **predictable scaling laws** with model size — larger models show stronger, faster, or more consistent contraction.

**Method:**
1. Test R_V across scales: 7B, 13B, 70B, 400B (if accessible)
2. Use identical recursive prompt suite across all sizes
3. Fit scaling law: R_V_effect = a × params^b + c
4. Test whether larger models show "phase transition" behavior

**Expected Outcome:**
- Power-law scaling of R_V effect with parameter count
- Larger models show contraction at earlier layers
- Critical threshold where contraction becomes "emergent"

**Why It Matters:**
Positions R_V as a **scalable metric** for studying model behavior. Could predict R_V properties at frontier model scales. Connects to **Kaplan et al. (2020)** scaling laws and **Hoffmann et al. (2022)** Chinchilla.

**Difficulty:** Hard (compute intensive)  
**Priority:** P0 (high impact)  
**GPU Hours:** ~800

**Knowledge Base Connections:**
- **Kaplan et al. (2020)** — Scaling Laws for Neural Language Models
- **Hoffmann et al. (2022)** — Training Compute-Optimal Large Language Models (Chinchilla)
- **Wei et al. (2022)** — Emergent Abilities of Large Language Models

**mi_auditor AUDIT:**
```python
auditor.audit_scaling({
    "claim": "R_V contraction follows power-law scaling with model size",
    "scales": ["7B", "13B", "70B", "400B"],
    "scaling_law": "power_law",
    "r_squared_threshold": 0.95,
    "prediction_test": "extrapolation_to_larger",
    "controls": ["width_scaling", "depth_scaling", "compute_matched"]
})
```

---

### Experiment 4: R_V in Encoder-Only Models (BERT, RoBERTa)

**Hypothesis:** Encoder-only transformers exhibit R_V contraction during masked token prediction on recursive inputs, but with different layer patterns than decoders.

**Method:**
1. Test BERT-large, RoBERTa-large, DeBERTa-v3
2. Create recursive masked language modeling examples
3. Measure R_V at each layer for [MASK] position representations
4. Compare bidirectional vs. unidirectional contraction patterns

**Expected Outcome:**
- R_V contraction present but weaker than decoders (no autoregressive pressure)
- Bidirectional attention creates different contraction geometry
- Peak contraction at middle layers (not late layers as in decoders)

**Why It Matters:**
Tests whether R_V is specific to **autoregressive generation** or general to transformer processing. Validates architecture differences. Connects to **Devlin et al. (2019)** BERT.

**Difficulty:** Easy  
**Priority:** P2  
**GPU Hours:** ~40

**Knowledge Base Connections:**
- **Devlin et al. (2019)** — BERT: Pre-training of Deep Bidirectional Transformers
- **Liu et al. (2019)** — RoBERTa: A Robustly Optimized BERT Pretraining Approach
- **He et al. (2021)** — DeBERTa: Decoding-enhanced BERT with Disentangled Attention

**mi_auditor AUDIT:**
```python
auditor.audit_architecture({
    "claim": "Encoder-only models show distinct R_V patterns from decoders",
    "architectures": ["bert", "roberta", "deberta"],
    "comparison_baseline": ["gpt2", "llama"],
    "metrics": ["layer_of_peak_contraction", "contraction_magnitude"],
    "statistical_test": "anova",
    "validation": ["directionality_analysis", "attention_pattern_comparison"]
})
```

---

### Experiment 5: R_V in State Space Models (Mamba, RWKV)

**Hypothesis:** State space models (SSMs) show R_V-like geometric contraction but through **different mechanisms** (state compression vs. attention concentration).

**Method:**
1. Test Mamba-2.8B, Mamba-7B, RWKV-7B
2. Use identical recursive prompt suite as transformer baselines
3. Measure state-space dimensionality over sequence position
4. Compare state compression metrics to R_V analog

**Expected Outcome:**
- SSMs show geometric contraction but smoother (no sharp layer transitions)
- Contraction correlates with state matrix eigenvalue decay
- Different relationship to sequence length than transformers

**Why It Matters:**
Tests whether R_V is **mechanism-agnostic** (any sequence model processing recursive structure) or attention-specific. Important as SSMs gain traction. Connects to **Gu & Dao (2023)** Mamba.

**Difficulty:** Hard (different architecture)  
**Priority:** P1  
**GPU Hours:** ~300

**Knowledge Base Connections:**
- **Gu & Dao (2023)** — Mamba: Linear-Time Sequence Modeling with Selective State Spaces
- **Peng et al. (2023)** — RWKV: Reinventing RNNs for the Transformer Era
- **Dao et al. (2024)** — Transformers are SSMs

**mi_auditor AUDIT:**
```python
auditor.audit_alternative_arch({
    "claim": "SSMs exhibit R_V-analogous contraction via state compression",
    "models": ["mamba-2.8b", "mamba-7b", "rwkv-7b"],
    "analog_metric": "state_space_participation_ratio",
    "comparison": ["transformer_baselines"],
    "mechanism_tests": ["state_eigenvalue_analysis", "selectivity_probe"],
    "conclusion_criteria": ["similar_effect", "different_mechanism"]
})
```

---

## Category 2: Deepening Experiments

### Experiment 6: SAE Feature Decomposition of R_V

**Hypothesis:** R_V contraction is mediated by **specific sparse autoencoder features** — a subset of monosemantic features activate strongly on recursive patterns and drive geometric collapse.

**Method:**
1. Load Gemma Scope SAEs (from **Lieberum et al. 2024**)
2. Run recursive prompts through Gemma 2 9B
3. Measure which SAE features correlate with R_V contraction
4. Ablate top-correlated features and measure R_V change

**Expected Outcome:**
- ~50-200 SAE features show strong correlation with R_V contraction
- Features interpretable as "repetition detection", "pattern matching", "loop detection"
- Ablating these features reduces or eliminates R_V contraction

**Why It Matters:**
**Causal identification** of features mediating R_V. Moves from correlation to mechanism. Connects to **Bricken et al. (2023)** monosemanticity and **Lieberum et al. (2024)** Gemma Scope.

**Difficulty:** Medium (SAE expertise needed)  
**Priority:** P0 (critical for mechanistic understanding)  
**GPU Hours:** ~250

**Knowledge Base Connections:**
- **Bricken et al. (2023)** — Towards Monosemanticity: Decomposing Language Models With Dictionary Learning
- **Lieberum et al. (2024)** — Gemma Scope: Open Sparse Autoencoders Everywhere All At Once on Gemma 2
- **Templeton et al. (2024)** — Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet

**mi_auditor AUDIT:**
```python
auditor.audit_sae_decomposition({
    "claim": "Specific SAE features causally mediate R_V contraction",
    "sae_source": "gemma_scope",
    "method": "correlation_plus_ablation",
    "causal_criteria": {
        "correlation": "r > 0.7",
        "ablation_effect": "R_V_change > 50%",
        "restoration": "R_V_recovers_with_feature_restore"
    },
    "interpretability": ["automatic_labeling", "human_validation"]
})
```

---

### Experiment 7: Attention Head Attribution for R_V

**Hypothesis:** Specific attention heads — particularly **induction heads** and **previous token heads** — are responsible for R_V contraction.

**Method:**
1. Use attention head attribution methods (from **Nanda 2023**)
2. Compute per-head contribution to R_V for each layer
3. Ablation study: zero out heads one-by-one, measure R_V impact
4. Compare head importance rankings across different recursive prompt types

**Expected Outcome:**
- 5-15 heads account for >70% of R_V contraction effect
- Induction heads (from **Olsson et al. 2022**) strongly implicated
- Different head sets for different recursion types (narrative vs. syntactic)

**Why It Matters:**
**Circuit-level understanding** of R_V. Identifies which components of the attention mechanism drive geometric contraction. Connects directly to **Olsson et al. (2022)** induction heads.

**Difficulty:** Medium  
**Priority:** P0  
**GPU Hours:** ~180

**Knowledge Base Connections:**
- **Olsson et al. (2022)** — In-context Learning and Induction Heads
- **Nanda (2023)** — Attention Head Attribution Methods
- **Wang et al. (2022)** — Interpretability in the Wild (circuit tracing)
- **Lieberum et al. (2023)** — Specific circuits for induction heads

**mi_auditor AUDIT:**
```python
auditor.audit_circuit_attribution({
    "claim": "Specific attention heads causally drive R_V contraction",
    "attribution_method": "per_head_gradient",
    "ablation_protocol": "zero_ablation",
    "completeness_metric": "circuit_completeness_score",
    "thresholds": {
        "heads_for_70_percent": "<20 heads",
        "overlap_with_induction": ">80%"
    },
    "validation": ["faithfulness", "completeness", "minimality"]
})
```

---

### Experiment 8: MLP vs Attention R_V Split

**Hypothesis:** R_V contraction has **distinct contributions from attention and MLP layers** — attention concentrates on pattern matching, MLPs on feature refinement.

**Method:**
1. Compute R_V separately for attention-only and MLP-only paths
2. Use residual stream decomposition (from **Elhage et al. 2021**)
3. Measure which component dominates contraction at each layer
4. Test recursive prompts that emphasize pattern vs. semantic recursion

**Expected Outcome:**
- Attention dominates early-layer contraction (pattern detection)
- MLPs dominate late-layer contraction (semantic integration)
- Split varies by recursion type (more MLP involvement for semantic recursion)

**Why It Matters:**
Decomposes R_V into **sub-mechanisms**, enabling more precise analysis. Distinguishes pattern-level from meaning-level geometric effects. Connects to **Geva et al. (2021)** on MLP roles.

**Difficulty:** Medium  
**Priority:** P1  
**GPU Hours:** ~150

**Knowledge Base Connections:**
- **Elhage et al. (2021)** — Mathematical Framework for Transformer Circuits
- **Geva et al. (2021)** — Transformer Feed-Forward Layers Are Key-Value Memories
- **Dai et al. (2022)** — Uncovering Latent Predictive Knowledge in Transformers

**mi_auditor AUDIT:**
```python
auditor.audit_component_split({
    "claim": "Attention and MLP contribute differentially to R_V by layer",
    "decomposition": "attention_path_vs_mlp_path",
    "layer_analysis": "per_layer_contribution",
    "validation": ["path_patching", "component_ablation"],
    "convergence_test": "sum_equals_total_R_V"
})
```

---

### Experiment 9: Temporal Dynamics of R_V During Training

**Hypothesis:** R_V contraction **emerges during training** at a specific point, potentially coinciding with induction head formation (~25B tokens, **Olsson et al. 2022**).

**Method:**
1. Access Pythia training checkpoints (from **Biderman et al. 2023**)
2. Measure R_V on recursive prompts at checkpoints: 1B, 5B, 10B, ..., 300B tokens
3. Track when R_V contraction first appears and when it stabilizes
4. Correlate with induction head formation metrics

**Expected Outcome:**
- R_V contraction emerges sharply at ~20-30B tokens (induction head formation)
- Pre-induction: R_V ≈ 1.0 (no contraction)
- Post-induction: R_V < 1.0 with increasing strength

**Why It Matters:**
Tests whether R_V is a **learned capability** tied to specific developmental stages. Could identify critical training periods for interpretability. Connects to **Power et al. (2022)** grokking dynamics.

**Difficulty:** Hard (training dynamics analysis)  
**Priority:** P1  
**GPU Hours:** ~400

**Knowledge Base Connections:**
- **Olsson et al. (2022)** — In-context Learning and Induction Heads (training dynamics)
- **Biderman et al. (2023)** — Pythia: A Suite for Analyzing Large Language Models
- **Power et al. (2022)** — Grokking: Generalization Beyond Overfitting

**mi_auditor AUDIT:**
```python
auditor.audit_training_dynamics({
    "claim": "R_V contraction emerges at ~25B tokens coinciding with induction heads",
    "checkpoints": ["1b", "5b", "10b", "20b", "30b", "50b", "100b", "300b"],
    "correlation_target": "induction_head_score",
    "emergence_detection": "changepoint_analysis",
    "controls": ["non_recursive_baseline", "random_prompts"]
})
```

---

### Experiment 10: Token-Level R_V Trajectories

**Hypothesis:** R_V varies **dynamically across token positions** — contraction intensifies when tokens complete recursive patterns.

**Method:**
1. Measure R_V at each token position for recursive sequences
2. Identify "closure points" where recursion completes
3. Analyze R_V trajectory: does it dip at closure, recover after?
4. Compare trajectories for nested vs. sequential recursion

**Expected Outcome:**
- R_V shows local minima at pattern closure points
- Nested recursion shows hierarchical R_V structure
- Token-level R_V predicts next-token probability for recursive completions

**Why It Matters:**
Provides **fine-grained temporal understanding** of R_V. Enables position-specific analysis and prediction. Connects to **Meng et al. (2022)** on critical token positions.

**Difficulty:** Medium  
**Priority:** P2  
**GPU Hours:** ~100

**Knowledge Base Connections:**
- **Meng et al. (2022)** — Locating and Editing Factual Associations in GPT (token importance)
- **Geiger et al. (2024)** — Finding Neurons in a Haystack (token-level analysis)
- **Marks et al. (2024)** — Sparse Feature Circuits

**mi_auditor AUDIT:**
```python
auditor.audit_temporal_trajectory({
    "claim": "R_V shows token-level dynamics with minima at pattern closure",
    "granularity": "per_token",
    "pattern_types": ["narrative", "syntactic", "semantic"],
    "analysis": ["closure_detection", "hierarchical_structure"],
    "validation": ["next_token_prediction", "human_annotation_agreement"]
})
```

---

## Category 3: Bridge Experiments

### Experiment 11: R_V → Truthfulness Correlation

**Hypothesis:** **Lower R_V correlates with higher truthfulness** — models that haven't contracted may have "more room" to consider alternatives, avoiding premature convergence on falsehoods.

**Method:**
1. Use TruthfulQA dataset (**Lin et al. 2022**)
2. For each question, measure R_V of model's internal representations
3. Correlate R_V with answer correctness
4. Test if high-R_V (uncontracted) states enable better truth discrimination

**Expected Outcome:**
- R_V negatively correlates with truthfulness (higher R_V = more truthful)
- Effect strongest for questions requiring consideration of multiple possibilities
- Causal test: forcing high R_V improves truthfulness

**Why It Matters:**
Direct bridge from **geometric measure to epistemic quality**. Could provide diagnostic for model truthfulness. Connects to **Evans et al. (2021)** on model honesty.

**Difficulty:** Medium  
**Priority:** P0 (high safety relevance)  
**GPU Hours:** ~200

**Knowledge Base Connections:**
- **Lin et al. (2022)** — TruthfulQA: Measuring How Models Mimic Human Falsehoods
- **Evans et al. (2021)** — Uncovering the Limits of Model Honesty
- **Burns et al. (2023)** — Discovering Latent Knowledge in Language Models

**mi_auditor AUDIT:**
```python
auditor.audit_behavioral_bridge({
    "claim": "Higher R_V correlates with increased truthfulness",
    "dataset": "truthfulqa",
    "correlation_metric": "point_biserial",
    "causal_test": "R_V_manipulation_via_steering",
    "controls": ["question_difficulty", "model_size", "format_effects"],
    "ethical_review": "required_for_deception_research"
})
```

---

### Experiment 12: R_V → Hallucination Detection

**Hypothesis:** **Sudden R_V drops precede hallucinations** — geometric contraction may indicate model "locking in" to a fabricated answer.

**Method:**
1. Use FACTOR dataset (**Min et al. 2023**) or SelfCheckGPT (**Manakul et al. 2023**)
2. Measure R_V trajectory during generation of hallucinated vs. factual responses
3. Train classifier on R_V features to predict hallucinations
4. Test if intervention (preventing R_V drop) reduces hallucination rate

**Expected Outcome:**
- R_V shows sharp drop 2-5 tokens before hallucination onset
- R_V-based classifier achieves >80% hallucination detection accuracy
- R_V intervention reduces hallucination rate by 20-40%

**Why It Matters:**
**Practical application** — R_V as hallucination early warning system. Direct safety utility. Connects to **Ji et al. (2023)** hallucination survey.

**Difficulty:** Medium  
**Priority:** P0 (direct safety application)  
**GPU Hours:** ~180

**Knowledge Base Connections:**
- **Min et al. (2023)** — FACTOR: Factual Annotation and Checking for Text Output Reliability
- **Manakul et al. (2023)** — SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection
- **Ji et al. (2023)** — Survey of Hallucination in Natural Language Generation

**mi_auditor AUDIT:**
```python
auditor.audit_safety_application({
    "claim": "R_V trajectories predict hallucinations with >80% accuracy",
    "dataset": ["factor", "selfcheckgpt"],
    "detection_metric": "auroc",
    "threshold": 0.80,
    "intervention_test": "R_V_maintenance_reduces_hallucination",
    "safety_review": "false_positive_rate_analysis"
})
```

---

### Experiment 13: R_V → Confidence Calibration

**Hypothesis:** **R_V correlates with model confidence** — contraction indicates "certainty" in representation space, which may or may not align with true probability calibration.

**Method:**
1. Compare R_V with token probability (softmax confidence)
2. Test on calibration benchmarks: MMLU, GSM8K with confidence elicitation
3. Measure if R_V is better calibrated than token probabilities
4. Test if R_V-aware calibration improves overall calibration

**Expected Outcome:**
- R_V correlates with confidence but is differently calibrated
- R_V shows better calibration on out-of-distribution examples
- Combining R_V with token probs improves expected calibration error (ECE)

**Why It Matters:**
**Uncertainty quantification** — R_V as geometric confidence measure. Better calibration = better decision-making. Connects to **Jiang et al. (2021)** on calibration.

**Difficulty:** Easy  
**Priority:** P1  
**GPU Hours:** ~80

**Knowledge Base Connections:**
- **Jiang et al. (2021)** — Can We Trust Calibration in Neural Networks?
- **Guo et al. (2017)** — On Calibration of Modern Neural Networks
- **Kadavath et al. (2022)** — Language Models (Mostly) Know What They Know

**mi_auditor AUDIT:**
```python
auditor.audit_calibration({
    "claim": "R_V provides complementary calibration information to token probabilities",
    "metrics": ["ece", "brier_score", "nll"],
    "datasets": ["mmlu", "gsm8k"],
    "comparison": ["token_probability", "ensemble", "temperature_scaling"],
    "improvement_threshold": "5% ECE reduction"
})
```

---

### Experiment 14: R_V → Adversarial Robustness

**Hypothesis:** **Models with maintained high R_V are more robust to adversarial attacks** — geometric contraction may indicate vulnerability to prompt manipulation.

**Method:**
1. Use AdvBench (**Perez & Ribeiro 2022**) or PromptInject (**Perez & Ribeiro 2022**)
2. Measure R_V on adversarial prompts before and after attack
3. Test if models that maintain R_V > threshold resist jailbreaks better
4. Explore R_V as adversarial example detection signal

**Expected Outcome:**
- Successful adversarial attacks correlate with R_V manipulation (forced contraction)
- R_V-based detection identifies >70% of adversarial prompts
- Maintaining high R_V (via intervention) increases robustness

**Why It Matters:**
**Adversarial defense** application. Geometric stability as security property. Connects to **Carlini et al. (2023)** on adversarial attacks.

**Difficulty:** Hard (adversarial expertise needed)  
**Priority:** P2  
**GPU Hours:** ~350

**Knowledge Base Connections:**
- **Perez & Ribeiro (2022)** — Ignore This Title and HackAPrompt: Exposing Systemic Vulnerabilities
- **Carlini et al. (2023)** — Are Aligned Neural Networks Adversarially Aligned?
- **Zou et al. (2023)** — Universal and Transferable Adversarial Attacks

**mi_auditor AUDIT:**
```python
auditor.audit_adversarial({
    "claim": "R_V manipulation correlates with adversarial vulnerability",
    "attack_types": ["jailbreak", "prompt_injection", "gradient_based"],
    "detection_metric": "auroc",
    "robustness_test": "R_V_maintenance_improves_defense",
    "safety_review": "dual_use_considerations"
})
```

---

### Experiment 15: R_V → Chain-of-Thought Quality

**Hypothesis:** **High-quality CoT reasoning shows characteristic R_V patterns** — effective reasoning maintains representational diversity (higher R_V) while converging appropriately at conclusion.

**Method:**
1. Use GSM8K with human-rated CoT quality (**Cobbe et al. 2021**)
2. Measure R_V trajectory throughout CoT generation
3. Correlate R_V patterns with CoT correctness and clarity ratings
4. Test if R_V-guided CoT generation improves reasoning

**Expected Outcome:**
- Good CoT: Maintains high R_V during reasoning, contracts at answer
- Bad CoT: Premature contraction or failure to converge
- R_V-guided generation improves GSM8K accuracy by 5-10%

**Why It Matters:**
**Reasoning quality metric** — R_V as diagnostic for effective thinking. Connects to **Wei et al. (2022)** CoT and **Yao et al. (2023)** tree-of-thought.

**Difficulty:** Medium  
**Priority:** P1  
**GPU Hours:** ~120

**Knowledge Base Connections:**
- **Wei et al. (2022)** — Chain-of-Thought Prompting Elicits Reasoning in LLMs
- **Yao et al. (2023)** — Tree of Thoughts: Deliberate Problem Solving with LLMs
- **Cobbe et al. (2021)** — Training Verifiers to Solve Math Word Problems

**mi_auditor AUDIT:**
```python
auditor.audit_reasoning_bridge({
    "claim": "R_V patterns distinguish high-quality from low-quality CoT reasoning",
    "dataset": "gsm8k",
    "quality_annotation": "human_rating",
    "pattern_analysis": "trajectory_classification",
    "intervention": "R_V_guided_generation",
    "improvement_metric": "accuracy_delta"
})
```

---

## Category 4: Methodology Experiments

### Experiment 16: Alternative Metrics Validation

**Hypothesis:** **R_V correlates with but is distinct from** other geometric measures: effective rank, nuclear norm, principal angles.

**Method:**
1. Compute multiple geometric metrics on same representations:
   - Participation Ratio (our R_V)
   - Hard rank (thresholded singular values)
   - Nuclear norm (sum of singular values)
   - Effective rank (from **Roy & Vetterli 2007**)
2. Compare discriminative power on recursive vs. non-recursive prompts
3. Test which metric is most robust to noise, most interpretable

**Expected Outcome:**
- All metrics correlate (r > 0.8) but R_V has best discriminative power
- R_V most robust to SVD numerical instability
- Effective rank similar but less sensitive to outliers

**Why It Matters:**
**Methodological validation** — confirms R_V is the right metric. Establishes relationships to existing linear algebra measures. Connects to **Roy & Vetterli (2007)** effective rank.

**Difficulty:** Easy  
**Priority:** P2  
**GPU Hours:** ~60

**Knowledge Base Connections:**
- **Roy & Vetterli (2007)** — Effective Rank: A Measure of Dimensionality
- **Vershynin (2018)** — High-Dimensional Probability (random matrix theory)
- **Edelman & Rao (2005)** — Random Matrix Theory

**mi_auditor AUDIT:**
```python
auditor.audit_metric_validation({
    "claim": "Participation Ratio (R_V) is optimal among geometric metrics for recursive detection",
    "comparison_metrics": ["hard_rank", "nuclear_norm", "effective_rank", "stable_rank"],
    "validation_criteria": {
        "discriminative_power": "auroc",
        "robustness": "noise_sensitivity",
        "interpretability": "human_correlation"
    },
    "threshold": "R_V outperforms alternatives by >10%"
})
```

---

### Experiment 17: Bootstrap Confidence Intervals

**Hypothesis:** **Bootstrap resampling provides accurate confidence intervals** for R_V estimates, enabling proper statistical inference.

**Method:**
1. Implement bootstrap CI for R_V: resample prompts, recompute R_V
2. Compare percentile, BCa (bias-corrected accelerated) methods
3. Validate coverage: do 95% CIs contain true R_V 95% of time?
4. Determine minimum sample size for stable R_V estimates

**Expected Outcome:**
- BCa bootstrap provides accurate coverage
- Minimum n=30 prompts for stable R_V estimates
- CI width inversely correlates with effect size

**Why It Matters:**
**Statistical rigor** — enables proper hypothesis testing and confidence reporting. Required for publication standards. Connects to **Efron & Tibshirani (1994)** bootstrap methods.

**Difficulty:** Easy  
**Priority:** P1  
**GPU Hours:** ~40

**Knowledge Base Connections:**
- **Efron & Tibshirani (1994)** — An Introduction to the Bootstrap
- **DiCiccio & Efron (1996)** — Bootstrap Confidence Intervals
- **Wasserman (2004)** — All of Statistics

**mi_auditor AUDIT:**
```python
auditor.audit_statistical_method({
    "claim": "Bootstrap CIs provide accurate coverage for R_V estimates",
    "methods": ["percentile", "bca", "studentized"],
    "validation": "coverage_probability_simulation",
    "target_coverage": 0.95,
    "tolerance": 0.02,
    "sample_size_recommendation": "minimum_n_for_stable_ci"
})
```

---

### Experiment 18: Cross-Architecture Standardization

**Hypothesis:** **Standardized R_V measurement protocol** enables valid comparison across architectures with different dimensionalities and layer structures.

**Method:**
1. Develop normalization scheme for R_V across architectures:
   - Normalize by model width
   - Normalize by layer depth
   - Control for residual stream dimensionality
2. Test on 10+ architectures: GPT, Llama, Mistral, Gemma, etc.
3. Validate that normalized R_V predicts recursive detection independent of architecture

**Expected Outcome:**
- Normalized R_V (R_V_norm = R_V / sqrt(d_model)) enables cross-arch comparison
- Architecture-agnostic threshold for recursive detection
- Standard protocol documented and validated

**Why It Matters:**
**Methodological standardization** — enables field-wide adoption and comparison. Required for meta-analyses. Connects to **Nanda (2023)** standardization efforts.

**Difficulty:** Medium  
**Priority:** P1  
**GPU Hours:** ~150

**Knowledge Base Connections:**
- **Nanda (2023)** — Mechanistic Interpretability Standards
- **Phuong & Hutter (2022)** — Formal Algorithms for Transformers
- **Touvron et al. (2023)** — Llama 2: Open Foundation and Fine-Tuned Chat Models

**mi_auditor AUDIT:**
```python
auditor.audit_standardization({
    "claim": "Normalized R_V enables valid cross-architecture comparison",
    "architectures": ["gpt2", "llama", "mistral", "gemma", "pythia", "qwen"],
    "normalization": ["width", "depth", "dimensionality"],
    "validation": "architecture_agnostic_recursive_detection",
    "protocol_documentation": "required"
})
```

---

### Experiment 19: Real-Time R_V Monitoring

**Hypothesis:** **R_V can be computed efficiently enough** for real-time monitoring during inference, enabling live geometric analysis.

**Method:**
1. Optimize R_V computation: incremental SVD, sketching methods
2. Measure latency overhead: can R_V be computed <10ms per layer?
3. Implement streaming R_V for long-context generation
4. Deploy monitoring dashboard for live R_V visualization

**Expected Outcome:**
- Optimized R_V computation: <5ms per layer on GPU
- Streaming algorithm for contexts up to 100K tokens
- Real-time dashboard operational

**Why It Matters:**
**Engineering feasibility** — enables production use of R_V for monitoring, steering, debugging. Connects to **Halko et al. (2011)** randomized SVD.

**Difficulty:** Medium  
**Priority:** P2  
**GPU Hours:** ~100

**Knowledge Base Connections:**
- **Halko et al. (2011)** — Finding Structure with Randomness: Probabilistic Algorithms
- **Liberty (2013)** — Simple and Deterministic Matrix Sketching
- **Tropp et al. (2017)** — Practical Sketching Algorithms for Low-Rank Matrix Approximation

**mi_auditor AUDIT:**
```python
auditor.audit_engineering({
    "claim": "R_V can be computed in <10ms per layer for real-time monitoring",
    "optimization_methods": ["incremental_svd", "randomized_sketching"],
    "latency_target": "<10ms",
    "accuracy_tradeoff": "<5% error vs exact",
    "scalability_test": "100k_context_length"
})
```

---

### Experiment 20: Automated Causal Discovery

**Hypothesis:** **ACDC (Automated Circuit Discovery) can identify the causal circuit** for R_V contraction without manual hypothesis.

**Method:**
1. Apply ACDC (**Conmy et al. 2023**) to R_V task
2. Input: recursive prompt → R_V contraction
3. ACDC automatically discovers relevant edges (heads, MLPs)
4. Compare ACDC circuit to our manual circuit analysis

**Expected Outcome:**
- ACDC discovers circuit with >80% overlap with manual analysis
- Identifies additional edges we missed (completeness check)
- Validates that R_V circuit is discoverable without prior knowledge

**Why It Matters:**
**Automation** — reduces reliance on manual circuit tracing. Validates R_V circuit is "real" (discoverable by algorithm). Connects to **Conmy et al. (2023)** ACDC.

**Difficulty:** Hard (ACDC expertise)  
**Priority:** P2  
**GPU Hours:** ~500

**Knowledge Base Connections:**
- **Conmy et al. (2023)** — Automated Circuit Discovery
- **Heimersheim & Nanda (2023)** — How to Use and Interpret ACDC Results
- **Syed et al. (2023)** — Attributing Model Behavior to Training Data

**mi_auditor AUDIT:**
```python
auditor.audit_automated_discovery({
    "claim": "ACDC automatically discovers the R_V contraction circuit",
    "method": "acdc",
    "comparison_baseline": "manual_circuit_analysis",
    "overlap_metric": "edge_precision_recall",
    "threshold": ">80% edge overlap",
    "validation": ["faithfulness", "completeness", "minimality"]
})
```

---

## Category 5: Theoretical Experiments

### Experiment 21: Superposition Collapse Prediction

**Hypothesis:** **R_V contraction is a signature of superposition collapse** — when many features in superposition collapse to fewer, more precise features.

**Method:**
1. Use toy model from **Elhage et al. (2022)** with controllable superposition
2. Induce superposition collapse via targeted training
3. Measure R_V before, during, and after collapse
4. Test prediction: R_V should track superposition density

**Expected Outcome:**
- R_V inversely correlates with superposition density
- Sharp R_V drop at collapse point
- Mathematical relationship: R_V ≈ 1/superposition_density

**Why It Matters:**
**Theoretical foundation** — connects R_V to fundamental representational theory. Validates R_V as measuring something theoretically meaningful. Connects to **Elhage et al. (2022)** toy superposition.

**Difficulty:** Medium  
**Priority:** P0 (theoretical grounding)  
**GPU Hours:** ~200

**Knowledge Base Connections:**
- **Elhage et al. (2022)** — Toy Models of Superposition
- **Schaeffer et al. (2023)** — Double Descent in the Condition Number
- **Zhong et al. (2023)** — The Geometry of Causal Intervention

**mi_auditor AUDIT:**
```python
auditor.audit_theoretical_prediction({
    "claim": "R_V contraction quantifies superposition collapse",
    "theoretical_basis": "elhage2022superposition",
    "test_system": "toy_model_superposition",
    "prediction": "R_V_inversely_correlates_with_superposition_density",
    "validation": ["correlation", "causal_manipulation", "mathematical_derivation"]
})
```

---

### Experiment 22: Geometry of Truth Hypothesis

**Hypothesis:** **Truthful representations occupy distinct geometric structures** — R_V captures proximity to "truth manifold" in representation space.

**Method:**
1. Inspired by **Marks & Tegmark (2023)** linear structure of truth
2. Measure R_V of representations for true vs. false statements
3. Test if R_V difference is orthogonal to truth direction
4. Explore if R_V + linear probe outperforms either alone

**Expected Outcome:**
- Truthful statements show different R_V geometry than false statements
- R_V provides complementary information to linear truth probes
- Combined: R_V × linear = better truth detection than either alone

**Why It Matters:**
**Epistemological geometry** — connects to "geometry of truth" research program. Positions R_V as epistemic measure. Connects to **Marks & Tegmark (2023)** linear truth structure.

**Difficulty:** Hard (abstract)  
**Priority:** P0 (foundational)  
**GPU Hours:** ~300

**Knowledge Base Connections:**
- **Marks & Tegmark (2023)** — The Geometry of Truth: Emergence of Linear Structure
- **Burns et al. (2023)** — Discovering Latent Knowledge in Language Models
- **Li et al. (2023)** — Inference-Time Intervention: Eliciting Truthful Answers

**mi_auditor AUDIT:**
```python
auditor.audit_geometric_theory({
    "claim": "R_V captures proximity to truth manifold in representation space",
    "theoretical_basis": "marks_tegmark_2023",
    "test_dataset": "true_false_statements",
    "comparison": ["linear_probe", "R_V_alone", "R_V_times_linear"],
    "validation": ["classification_accuracy", "geometric_analysis", "causal_intervention"]
})
```

---

### Experiment 23: Phase Transitions in R_V

**Hypothesis:** **R_V exhibits phase transition behavior** — sharp qualitative changes as a function of training, scale, or prompt properties.

**Method:**
1. Test for phase transitions in:
   - Training dynamics (per Experiment 9)
   - Model scale (per Experiment 3)
   - Prompt recursion depth
2. Use order parameters from statistical physics
3. Test universality: are transition properties model-agnostic?

**Expected Outcome:**
- Sharp phase transitions in R_V at critical points
- Universal critical exponents across architectures
- R_V phase diagram mappable for different conditions

**Why It Matters:**
**Statistical physics perspective** — positions R_V in framework of phase transitions and emergent phenomena. Connects to **Goldenfeld (1992)** phase transitions and **Bakhshandeh et al. (2023)** emergence.

**Difficulty:** Hard (physics expertise)  
**Priority:** P1  
**GPU Hours:** ~400

**Knowledge Base Connections:**
- **Goldenfeld (1992)** — Lectures on Phase Transitions and the Renormalization Group
- **Bakhshandeh et al. (2023)** — Emergence of Induction Heads and In-Context Learning
- **Roberts et al. (2023)** — Principles of Deep Learning Theory

**mi_auditor AUDIT:**
```python
auditor.audit_phase_transition({
    "claim": "R_V exhibits phase transition behavior with universal properties",
    "order_parameters": ["R_V", "effective_dimensionality"],
    "control_parameters": ["training_tokens", "model_scale", "recursion_depth"],
    "analysis_methods": ["finite_size_scaling", "critical_exponents", "universality_tests"],
    "validation": ["sharpness", "hysteresis", "scaling_collapse"]
})
```

---

### Experiment 24: R_V as Capacity Measure

**Hypothesis:** **R_V measures effective representational capacity** — models with higher R_V can represent more distinct concepts simultaneously.

**Method:**
1. Test representational capacity using mutually orthogonal prompts
2. Measure R_V and classification accuracy as function of concept count
3. Test prediction: R_V × accuracy = constant (capacity constraint)
4. Compare to theoretical capacity bounds

**Expected Outcome:**
- R_V correlates with measured representational capacity
- R_V × accuracy shows saturation at capacity limit
- Relationship to Hopfield capacity, perceptron capacity

**Why It Matters:**
**Information-theoretic interpretation** — positions R_V as capacity metric. Connects to classic neural network theory. Connects to **Hopfield (1982)** and **Cover (1965)** capacity results.

**Difficulty:** Medium  
**Priority:** P2  
**GPU Hours:** ~150

**Knowledge Base Connections:**
- **Hopfield (1982)** — Neural Networks and Physical Systems with Emergent Collective Computational Abilities
- **Cover (1965)** — Geometrical and Statistical Properties of Systems of Linear Inequalities
- **Gardner (1988)** — The Space of Interactions in Neural Network Models

**mi_auditor AUDIT:**
```python
auditor.audit_capacity_theory({
    "claim": "R_V measures effective representational capacity",
    "capacity_test": "mutually_orthogonal_concepts",
    "metrics": ["R_V", "classification_accuracy", "saturation_point"],
    "theoretical_comparison": ["hopfield_capacity", "perceptron_capacity"],
    "prediction": "R_V_times_accuracy_saturates"
})
```

---

### Experiment 25: Information-Theoretic Bounds

**Hypothesis:** **R_V is bounded by mutual information** — R_V ≤ I(input; representation) + constant, formalizing the intuition that contraction preserves task-relevant information.

**Method:**
1. Compute mutual information between inputs and representations
2. Compare to R_V across different prompt sets
3. Test information-R_V tradeoff: can we increase R_V without losing MI?
4. Derive theoretical bound if possible

**Expected Outcome:**
- R_V upper bounded by mutual information
- Tight bound: R_V ≈ MI for optimal representations
- Tradeoff curve: R_V vs. MI for different architectures

**Why It Matters:**
**Information theory foundation** — connects R_V to fundamental information-theoretic limits. Positions R_V as compression measure. Connects to **Tishby & Zaslavsky (2015)** information bottleneck.

**Difficulty:** Hard (information theory)  
**Priority:** P2  
**GPU Hours:** ~250

**Knowledge Base Connections:**
- **Tishby & Zaslavsky (2015)** — Deep Learning and the Information Bottleneck Principle
- **Shwartz-Ziv & Tishby (2017)** — Opening the Black Box of Deep Neural Networks via Information
- **Achille & Soatto (2018)** — Emergence of Invariance and Disentanglement

**mi_auditor AUDIT:**
```python
auditor.audit_information_theory({
    "claim": "R_V is information-theoretically bounded by mutual information",
    "mi_estimation": ["binning", "knn", "neural_estimator"],
    "bound_type": ["upper", "equality_conditions"],
    "validation": ["empirical_correlation", "theoretical_derivation", "counterexample_search"]
})
```

---

## mi_auditor Integration: AUDIT Protocol

Each experiment above includes specific `auditor.*()` calls. Here's the **general AUDIT protocol** applied to all experiments:

### Pre-Experiment AUDIT

```python
from mi_auditor import MIAuditor, ExperimentAuditor

auditor = MIAuditor()
exp_auditor = ExperimentAuditor(auditor)

# 1. Hypothesis validation
exp_auditor.audit_hypothesis(
    hypothesis="R_V contracts on recursive prompts",
    knowledge_base_check=True,
    novelty_assessment=True,
    falsifiability_check=True
)

# 2. Method validation  
exp_auditor.audit_method(
    method="activation_patching",
    controls_required=4,
    baseline_specification=True,
    statistical_power=0.8
)

# 3. Resource estimation
exp_auditor.audit_resources(
    gpu_hours=estimated_hours,
    replication_requirement=3,
    checkpoint_storage=True
)
```

### During-Experiment AUDIT

```python
# Real-time monitoring
exp_auditor.monitor_experiment(
    current_step="layer_27_patching",
    effect_size_threshold=cohens_d > 0.8,
    checkpoint_validation=True
)
```

### Post-Experiment AUDIT

```python
# Final validation
final_report = exp_auditor.audit_results(
    results=experiment_data,
    tier_assessment=True,
    cross_arch_replication=True,
    statistical_validation=True,
    literature_positioning=True
)

# Generate publication readiness score
readiness = final_report.publication_readiness()
# Returns: Tier (Nature/NeurIPS/ICLR/arXiv) + blockers
```

---

## GPU Allocation Strategy

### Phase 1: P0 Experiments (Priority 0)
**Timeline:** Months 1-3  
**GPU Hours:** ~2,130

| Experiment | Hours | Parallelizable |
|------------|-------|----------------|
| Scaling Laws (3) | 800 | Partial |
| SAE Decomposition (6) | 250 | Yes |
| Head Attribution (7) | 180 | Yes |
| Truthfulness Bridge (11) | 200 | Yes |
| Hallucination Detection (12) | 180 | Yes |
| Superposition Theory (21) | 200 | Yes |
| Geometry of Truth (22) | 300 | Yes |
| Training Dynamics (9) | 400 | No (sequential) |

**Note:** Experiment 9 (Training Dynamics) must run sequentially through checkpoints.

### Phase 2: P1 Experiments
**Timeline:** Months 4-6  
**GPU Hours:** ~1,420

### Phase 3: P2 Experiments
**Timeline:** Months 7-9  
**GPU Hours:** ~1,090

---

## Publication Strategy

### Tier Targets

| Tier | Experiments | Current Status | Blockers |
|------|-------------|----------------|----------|
| **Nature/Science** | 3, 6, 7, 9, 21, 22 | 30% | Complete P0, add head circuits, SAE features |
| **NeurIPS/ICML** | 1, 2, 5, 8, 11, 12, 13, 15, 23 | 60% | Finish P1, statistical validation |
| **ICLR Workshop** | 4, 10, 14, 16, 17, 18, 19, 20 | 80% | Final analysis, documentation |
| **arXiv** | 24, 25 | 90% | Theoretical derivations |

### Paper Outline

**Paper 1: "Geometric Contraction in Transformers: Scaling Laws and Mechanisms"**
- Experiments: 3, 6, 7, 9, 21
- Target: NeurIPS/ICML 2026

**Paper 2: "R_V: A Geometric Bridge to Model Behavior"**
- Experiments: 11, 12, 13, 15
- Target: ICLR 2026

**Paper 3: "Recursive Structure and Representational Geometry"**
- Experiments: 1, 2, 5, 22
- Target: Nature Machine Intelligence

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| No SAE features correlate with R_V | Medium | High | Use multiple SAE training runs, different sparsity penalties |
| Scaling laws don't hold | Low | High | Test wider scale range, check for confounders |
| Alternative metrics outperform R_V | Low | Medium | Document comparison rigorously, pivot if needed |

### Resource Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Insufficient GPU access | Medium | High | Prioritize P0, stagger experiments, seek collaborations |
| Pythia checkpoints unavailable | Low | High | Use alternative training dynamics datasets |

### Scientific Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R_V is epiphenomenon | Low | Critical | Causal validation (Experiments 6, 7) |
| Results don't replicate | Medium | High | Pre-registration, multiple seeds, cross-arch |

---

## Appendix: Full Paper-to-Experiment Mapping

### Category 1: Extension Experiments
- **Exp 1 (ViT):** Dosovitskiy 2021, Caron 2021
- **Exp 2 (Multimodal):** Radford 2021, Liu 2023, Zhang 2024
- **Exp 3 (Scaling):** Kaplan 2020, Hoffmann 2022, Wei 2022
- **Exp 4 (Encoder):** Devlin 2019, Liu 2019, He 2021
- **Exp 5 (SSM):** Gu 2023, Peng 2023, Dao 2024

### Category 2: Deepening Experiments
- **Exp 6 (SAE):** Bricken 2023, Lieberum 2024, Templeton 2024
- **Exp 7 (Attention):** Olsson 2022, Nanda 2023, Wang 2022, Lieberum 2023
- **Exp 8 (MLP/Attn):** Elhage 2021, Geva 2021, Dai 2022
- **Exp 9 (Training):** Olsson 2022, Biderman 2023, Power 2022
- **Exp 10 (Token-level):** Meng 2022, Geiger 2024, Marks 2024

### Category 3: Bridge Experiments
- **Exp 11 (Truth):** Lin 2022, Evans 2021, Burns 2023
- **Exp 12 (Hallucination):** Min 2023, Manakul 2023, Ji 2023
- **Exp 13 (Calibration):** Jiang 2021, Guo 2017, Kadavath 2022
- **Exp 14 (Adversarial):** Perez 2022, Carlini 2023, Zou 2023
- **Exp 15 (CoT):** Wei 2022, Yao 2023, Cobbe 2021

### Category 4: Methodology Experiments
- **Exp 16 (Metrics):** Roy 2007, Vershynin 2018, Edelman 2005
- **Exp 17 (Bootstrap):** Efron 1994, DiCiccio 1996, Wasserman 2004
- **Exp 18 (Standardization):** Nanda 2023, Phuong 2022, Touvron 2023
- **Exp 19 (Real-time):** Halko 2011, Liberty 2013, Tropp 2017
- **Exp 20 (ACDC):** Conmy 2023, Heimersheim 2023, Syed 2023

### Category 5: Theoretical Experiments
- **Exp 21 (Superposition):** Elhage 2022, Schaeffer 2023, Zhong 2023
- **Exp 22 (Truth Geometry):** Marks 2023, Burns 2023, Li 2023
- **Exp 23 (Phase Transitions):** Goldenfeld 1992, Bakhshandeh 2023, Roberts 2023
- **Exp 24 (Capacity):** Hopfield 1982, Cover 1965, Gardner 1988
- **Exp 25 (Information Theory):** Tishby 2015, Shwartz-Ziv 2017, Achille 2018

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | mi_auditor v6.0 | Initial release |

---

**License:** Research Proposal — Open for collaboration  
**Contact:** mi_auditor@clawd  
**Repository:** ~/clawd/skills/mi_auditor/

*"The best experiments are those that surprise us, even when we designed them."*
