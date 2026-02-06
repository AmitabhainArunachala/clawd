# Annotated Bibliography: Latest SOTA Mechanistic Interpretability Research (2024-2026)

## Executive Summary

This bibliography covers 15+ high-impact papers from 2024-2026 in mechanistic interpretability (MI), with focus on sparse autoencoders (SAEs), circuit tracing, representation engineering, and emerging frameworks. Relevance to R_V research is assessed throughout.

---

## 1. SCALING & PRODUCTION MODELS

### Templeton et al. (Anthropic) - "Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet"
**Date:** May 2024  
**arXiv:** N/A (Transformer Circuits Thread)  
**Link:** https://transformer-circuits.pub/2024/scaling-monosemanticity/

**Core Contribution:**
First successful extraction of millions of interpretable features from a production-grade LLM (Claude 3 Sonnet, ~3.0 version). Demonstrates SAEs scale to state-of-the-art models, not just toy models.

**Methodology:**
- Trained SAEs with JumpReLU activation on residual stream of Claude 3 Sonnet
- Used scaling laws to guide training decisions (dictionary size, L1 coefficient)
- Dictionary learning at scale: 34M features across three dictionaries
- Reconstruction loss + L1 sparsity penalty as training objective

**Key Results:**
- Extracted 34 million features from Claude 3 Sonnet
- Features are multilingual, multimodal, and generalize between concrete/abstract concepts
- Found safety-relevant features: deception (incl. treacherous turns), sycophancy, bias, security vulnerabilities, dangerous content
- Features can be used to steer model behavior (e.g., amplifying deception feature increases deceptive outputs)
- Scaling law: relationship between concept frequency and dictionary size needed

**Relation to R_V Research:**
**COMPLEMENTARY (High Relevance)** - This is the "gold standard" for SAE scaling. R_V can leverage these methods but focuses on different aspects (circuit-level vs. feature-level). Provides benchmark for feature interpretability quality.

**Criticisms/Gaps:**
- Limited causal validation of features (correlation vs. causation)
- Safety features exist but their practical exploitability unclear
- No systematic metric for feature "quality" beyond human inspection
- Scaling cost is enormous (industry-scale compute)

**Relevance Score:** 9/10

---

### Lieberum et al. (Google DeepMind) - "Gemma Scope: Open Sparse Autoencoders Everywhere All At Once on Gemma 2"
**Date:** August 2024  
**arXiv:** 2408.05147  
**Venue:** BlackboxNLP 2024

**Core Contribution:**
Open-source comprehensive suite of JumpReLU SAEs trained on all layers and sub-layers of Gemma 2 (2B, 9B, 27B), democratizing access to production-quality interpretability tools.

**Methodology:**
- JumpReLU SAEs (discontinuous activation function with straight-through estimators)
- Trained on all residual stream layers and MLP sub-layers
- Evaluation on standard metrics (reconstruction, sparsity, dead features)
- Also includes instruction-tuned variants for comparison

**Key Results:**
- Released weights for all layers of Gemma 2 2B/9B and select layers of 27B
- Achieves state-of-the-art reconstruction fidelity at given sparsity
- Publicly available via HuggingFace and Neuronpedia
- Comprehensive evaluation metrics released

**Relation to R_V Research:**
**COMPLEMENTARY (Very High Relevance)** - Provides open infrastructure for MI research. R_V can build on these SAEs for circuit analysis. Democratizes what Anthropic did with Claude 3.

**Criticisms/Gaps:**
- Still early-stage validation of downstream utility
- Focus on reconstruction, not necessarily causal understanding
- Limited analysis of what the features actually "mean"

**Relevance Score:** 9/10

---

## 2. SPARSE AUTOENCODER ADVANCES

### Rajamanoharan et al. - "Jumping Ahead: Improving Reconstruction Fidelity with JumpReLU Sparse Autoencoders"
**Date:** July 2024  
**arXiv:** 2407.14435

**Core Contribution:**
Introduces JumpReLU SAEs achieving SOTA reconstruction fidelity while maintaining interpretability. Addresses the tension between reconstruction quality and sparsity.

**Methodology:**
- JumpReLU activation: discontinuous threshold function
- Straight-through estimators (STEs) for training through discontinuity
- Direct L0 sparsity training (not L1 proxy)
- Compared against Gated and TopK SAEs on Gemma 2 9B

**Key Results:**
- State-of-the-art reconstruction fidelity at given sparsity
- No interpretability cost (verified via manual and automated studies)
- Simple modification to vanilla ReLU SAEs
- Similar training efficiency to standard SAEs

**Relation to R_V Research:**
**COMPLEMENTARY** - Better SAEs mean better feature decomposition for R_V circuit analysis. JumpReLU is becoming standard architecture.

**Criticisms/Gaps:**
- Theoretical understanding of why JumpReLU works better is limited
- L0 optimization can be unstable

**Relevance Score:** 8/10

---

### Bricken et al. / Cunningham et al. - "Sparse Autoencoders Find Highly Interpretable Features in Language Models"
**Date:** September 2023 (updated 2024)  
**arXiv:** 2309.08600  
**Venue:** ICLR 2024

**Core Contribution:**
Foundation paper establishing SAEs as viable solution to polysemanticity. Demonstrates monosemantic features can be recovered from real LLMs (Pythia-70M/410M).

**Methodology:**
- Sparse autoencoders on residual stream activations
- Reconstruction loss + L1 sparsity penalty
- Automated interpretability metrics for evaluation
- Applied to Indirect Object Identification (IOI) task

**Key Results:**
- SAE features more interpretable than neuron-level analysis
- Successfully identified causally relevant features for IOI task
- First demonstration of superposition resolution in language models
- Foundation for all subsequent SAE work

**Relation to R_V Research:**
**COMPLEMENTARY** - Foundational work. R_V builds on these decomposition techniques but goes deeper into circuit-level causal mechanisms.

**Criticisms/Gaps:**
- Smaller models only (Pythia-70M/410M)
- Limited causal validation
- Interpretability metrics rely on automated methods that may miss nuances

**Relevance Score:** 8/10

---

### Kissane et al. - "Interpreting Attention Layer Outputs with Sparse Autoencoders"
**Date:** June 2024  
**arXiv:** 2406.17759

**Core Contribution:**
First systematic application of SAEs to attention layer outputs (not just MLPs/residual), revealing new classes of interpretable features in attention heads.

**Methodology:**
- SAEs trained on attention output activations
- Multiple model families (GPT-2, Pythia, other transformers up to 2B params)
- Qualitative feature taxonomy study
- Analysis of Indirect Object Identification circuit through attention SAE lens

**Key Results:**
- Discovered three feature families: long-range context, short-range context, induction features
- Estimated 90%+ of attention heads are polysemantic (multiple unrelated roles)
- Validated SAEs find causally meaningful intermediate variables
- Open-sourced SAEs and exploration tools

**Relation to R_V Research:**
**COMPLEMENTARY** - Attention mechanisms are crucial for R_V research. This provides tools for interpreting attention-specific computations.

**Criticisms/Gaps:**
- Still focused on feature-level, not circuit-level analysis
- Limited to 2B parameters
- No systematic method for combining attention + MLP SAE analysis

**Relevance Score:** 7.5/10

---

### Belrose et al. - "Transcoders Beat Sparse Autoencoders for Interpretability"
**Date:** January 2025  
**arXiv:** 2501.18823

**Core Contribution:**
Proposes transcoders as alternative to SAEs - reconstructs component outputs from inputs rather than reconstructing activations. Shows superior interpretability.

**Methodology:**
- Transcoder: reconstructs output of component given its input
- Skip transcoders: add affine skip connection
- Direct comparison on same model/data as SAEs
- Interpretability evaluation via human and automated metrics

**Key Results:**
- Transcoder features significantly more interpretable than SAE features
- Skip transcoders achieve lower reconstruction loss without interpretability cost
- Better alignment between component function and learned features

**Relation to R_V Research:**
**COMPETING/COMPLEMENTARY** - Alternative decomposition approach. May be more natural for circuit-level analysis since it maps inputs→outputs.

**Criticisms/Gaps:**
- Limited model scale evaluation
- Training instability issues not fully resolved
- Less community adoption than SAEs

**Relevance Score:** 7/10

---

## 3. REPRESENTATION ENGINEERING

### Zou et al. - "Representation Engineering: A Top-Down Approach to AI Transparency"
**Date:** October 2023 (updated 2025)  
**arXiv:** 2310.01405

**Core Contribution:**
Introduces RepE: controlling LLMs by manipulating high-level representations rather than low-level circuits. Inspired by cognitive neuroscience (brain state monitoring).

**Methodology:**
- Representation Reading: extract high-level concepts (honesty, power-seeking) from activations
- Representation Control: steer models by adding/subtracting concept vectors
- Contrastive examples to identify concept directions
- Applied to honesty, harmlessness, power-seeking, emotions

**Key Results:**
- Simple yet effective control of LLM behavior
- Works across multiple safety-relevant dimensions
- Can detect deception in model representations before output
- More scalable than fine-tuning for behavior control

**Relation to R_V Research:**
**ALTERNATIVE APPROACH** - RepE is top-down (populations of neurons) vs. R_V's bottom-up (circuits). Both valid but different granularity. RepE for control, R_V for understanding.

**Criticisms/Gaps:**
- Concept directions may conflate multiple factors
- Limited mechanistic understanding of why steering works
- May not generalize to novel situations
- Less precise than circuit-level interventions

**Relevance Score:** 8/10 (different approach, highly relevant for comparison)

---

### Bartoszcze - "Representation Engineering for Large-Language Models: Survey and Research Challenges"
**Date:** February 2025  
**arXiv:** 2502.17601

**Core Contribution:**
Comprehensive survey formalizing RepE goals/methods, comparing to alternatives (MI, prompting, fine-tuning), outlining risks and research agenda.

**Methodology:**
- Systematic literature review
- Taxonomy of RepE techniques
- Risk analysis (performance decrease, compute overhead, steerability issues)
- Future research directions

**Key Results:**
- Formal framework for RepE
- Comparison matrix: RepE vs MI vs prompting vs fine-tuning
- Identified key risks: over-steering, interference, brittleness
- Research agenda for safe, predictable, personalizable LLMs

**Relation to R_V Research:**
**COMPLEMENTARY** - Provides theoretical framework comparing R_V-style MI with RepE. Helps position R_V research.

**Criticisms/Gaps:**
- Survey paper, no new methods
- RepE field still nascent

**Relevance Score:** 6.5/10

---

## 4. FRAMEWORKS & THEORY

### Sharkey et al. - "Open Problems in Mechanistic Interpretability"
**Date:** January 2025  
**arXiv:** 2501.16496

**Core Contribution:**
Comprehensive forward-facing review of MI field. Identifies open problems across methodology, applications, and socio-technical challenges.

**Methodology:**
- Systematic review of MI field
- Problem categorization: methodological, application, socio-technical
- Community input from 30 authors
- Prioritization framework

**Key Results:**
- 20+ open problems identified
- Key challenges: scaling to GPT-4 size, polysemanticity resolution, cross-layer representations
- Methodological needs: validation, benchmarking, causal interpretation
- Call for standardized evaluation (led to MIB benchmark)

**Relation to R_V Research:**
**ESSENTIAL READING** - Directly relevant to positioning R_V research. Many problems R_V seeks to address are highlighted here.

**Criticisms/Gaps:**
- Broad coverage but limited depth on each problem
- Some problems may be intractable

**Relevance Score:** 10/10

---

### He et al. - "Towards Global-level Mechanistic Interpretability: A Perspective of Modular Circuits"
**Date:** 2024/2025  
**arXiv:** (OpenReview)  
**Link:** https://openreview.net/forum?id=do5vVfKEXZ

**Core Contribution:**
Proposes modular circuits (MC) vocabulary - task-agnostic functional units reusable across tasks. Addresses limitations of task-specific circuit analysis.

**Methodology:**
- ModCirc framework for discovering modular circuit vocabularies
- Five criteria for MC characterization
- Reusable interpretations across tasks
- Applied to general and domain-specific tasks

**Key Results:**
- Enables global interpretability via shared MCs
- Reduces interpretation cost (reuse pre-established interpretations)
- Demonstrated on medical AI (symptoms across diagnosis, treatment, summarization)
- Clear patterns of component reuse across applications

**Relation to R_V Research:**
**HIGHLY COMPLEMENTARY** - R_V could adopt modular circuit vocabulary approach. Global interpretability scales better than per-task analysis.

**Criticisms/Gaps:**
- Limited evaluation on large models
- MC vocabulary construction is expensive initially
- Unclear how to handle novel behaviors not in vocabulary

**Relevance Score:** 8.5/10

---

### Williams et al. - "Mechanistic Interpretability Needs Philosophy"
**Date:** June 2025  
**arXiv:** 2506.18852

**Core Contribution:**
Argues MI field needs philosophical grounding to clarify concepts, scrutinize assumptions, interpret results, and address epistemic/ethical stakes.

**Methodology:**
- Position paper with philosophical analysis
- Three case studies of philosophical contributions
- Examination of three open problems from philosophical lens
- Call for interdisciplinary dialogue

**Key Results:**
- MI is "pre-paradigmatic" with foundational issues unsolved
- Philosophy can help: clarify conceptual confusion, scrutinize assumptions, suggest new inquiries
- Three problems examined: decomposition, interpretation, validation
- Parallel to philosophy's role in physics, cognitive science, economics

**Relation to R_V Research:**
**COMPLEMENTARY** - Encourages rigorous conceptual foundations for R_V research. Philosophical clarity on what "understanding" means mechanistically.

**Criticisms/Gaps:**
- Position paper, no empirical contribution
- Philosophical framework may slow practical progress

**Relevance Score:** 6/10

---

## 5. BENCHMARKS & EVALUATION

### (ICML 2025) - "MIB: A Mechanistic Interpretability Benchmark"
**Date:** July 2025  
**Link:** https://icml.cc/virtual/2025/poster/43836

**Core Contribution:**
First comprehensive benchmark for MI methods with two tracks spanning four tasks and five models. Establishes evaluation standards for the field.

**Methodology:**
- Two evaluation tracks
- Four tasks covering different MI challenges
- Five models of varying sizes
- Attribution and mask optimization methods evaluated

**Key Results:**
- Attribution and mask optimization methods perform best on circuit localization
- Causal variable identification benchmarks
- Standardized metrics for comparing MI approaches
- Identifies gaps in current methods

**Relation to R_V Research:**
**ESSENTIAL** - R_V can use MIB to evaluate progress. Standardized benchmarks critical for field maturation.

**Criticisms/Gaps:**
- New benchmark, may not capture all aspects of MI
- May favor certain types of methods over others

**Relevance Score:** 8.5/10

---

## 6. SURVEYS & SYNTHESIS

### Shu et al. - "A Survey on Sparse Autoencoders: Interpreting the Internal Mechanisms of Large Language Models"
**Date:** March 2025  
**arXiv:** 2503.05613

**Core Contribution:**
Comprehensive survey of SAEs for LLM interpretability. Covers theoretical foundations, architectures, applications, and challenges.

**Methodology:**
- Systematic review of SAE literature
- Architecture taxonomy (vanilla, TopK, JumpReLU, Gated)
- Application areas: explanation, steering, training
- Challenge identification

**Key Results:**
- SAEs address superposition/polysemanticity
- Growing adoption: Gemma 2 (DeepMind), LLaMA 3.1 (community)
- Applications: behavior steering, transparent training, safety evaluation
- Challenges: scaling, validation, feature interaction

**Relation to R_V Research:**
**COMPLEMENTARY** - Comprehensive background on SAEs, key tool for R_V research.

**Criticisms/Gaps:**
- Survey paper, no new methods
- Rapidly evolving field may outdate quickly

**Relevance Score:** 7/10

---

### Somvanshi et al. - "Bridging the Black Box: A Survey on Mechanistic Interpretability in AI"
**Date:** July 2025  
**Link:** SSRN 5345552

**Core Contribution:**
Broad survey of MI field covering major challenges: scaling to GPT-4, resolving polysemanticity, minimizing human subjectivity, establishing benchmarks.

**Key Results:**
- Identifies four major challenges
- Reviews current approaches to each
- Calls for standardized evaluation
- Highlights need for scalable methods

**Relation to R_V Research:**
**COMPLEMENTARY** - Broad overview helpful for context.

**Relevance Score:** 6.5/10

---

## 7. ADDITIONAL NOTABLE PAPERS

### Yan et al. - "Encourage or Inhibit Monosemanticity? Revisit Monosemanticity from a Feature Decorrelation Perspective"
**Date:** June 2024 (EMNLP 2024)  
**arXiv:** 2406.17969

**Core Contribution:**
Challenges prior work suggesting monosemanticity hurts performance. Shows monosemanticity positively correlates with model capacity in preference alignment.

**Key Results:**
- Feature decorrelation regularizer improves preference alignment
- Enhances representation diversity and activation sparsity
- Contradicts Wang et al. (2024) conclusions

**Relevance Score:** 6/10

---

### Juang et al. / EleutherAI - "Open Source Automated Interpretability for Sparse Autoencoder Features"
**Date:** July 2024  
**Link:** https://blog.eleuther.ai/autointerp/

**Core Contribution:**
Open-source automated interpretability pipeline for SAE features. Reduces cost from ~$200k to ~$1300 for interpreting 1.5M features.

**Methodology:**
- LLM-based explanation generation
- Simulation scoring for explanation quality
- Open source library: sae-auto-interp
- Dashboard for exploration

**Key Results:**
- Open source models (Llama 3.1) competitive with Claude 3.5 Sonnet
- 1.5M features interpreted for $1300 (Llama) vs $8500 (Claude) vs $200k (prior)
- Explanations similar to human-generated ones

**Relation to R_V Research:**
**TOOL** - Critical infrastructure for R_V research at scale.

**Relevance Score:** 7.5/10

---

## Summary Table

| Paper | Year | Type | Relevance Score | Relation to R_V |
|-------|------|------|-----------------|-----------------|
| Templeton et al. (Scaling Monosemanticity) | 2024 | Empirical | 9/10 | Complementary |
| Lieberum et al. (Gemma Scope) | 2024 | Empirical | 9/10 | Complementary |
| Sharkey et al. (Open Problems) | 2025 | Survey | 10/10 | Essential |
| Rajamanoharan et al. (JumpReLU) | 2024 | Method | 8/10 | Complementary |
| Zou et al. (RepE) | 2023/24 | Method | 8/10 | Alternative |
| He et al. (ModCirc) | 2024/25 | Method | 8.5/10 | Complementary |
| MIB Benchmark | 2025 | Benchmark | 8.5/10 | Essential |
| Bricken et al. (SAE Foundation) | 2023/24 | Method | 8/10 | Complementary |
| Kissane et al. (Attention SAEs) | 2024 | Empirical | 7.5/10 | Complementary |
| Belrose et al. (Transcoders) | 2025 | Method | 7/10 | Competing/Comp |
| EleutherAI AutoInterp | 2024 | Tool | 7.5/10 | Tool |
| Shu et al. (SAE Survey) | 2025 | Survey | 7/10 | Complementary |

---

## Key Trends for R_V Research

1. **SAE Dominance:** Sparse autoencoders are the dominant feature extraction method, with JumpReLU becoming standard
2. **Production Scale:** Methods now scaling to production models (Claude 3, Gemma 2, GPT-4)
3. **Feature → Circuit Gap:** Most work at feature level; circuit-level understanding still limited
4. **Automated Interpretability:** Growing focus on automated explanation generation and scoring
5. **Safety Relevance:** Increasing focus on safety-relevant features (deception, power-seeking)
6. **Open Problems Awareness:** Field acknowledging fundamental challenges (Sharkey et al.)
7. **Alternative Approaches:** Transcoders, RepE offer different trade-offs

---

## Recommendations for R_V Research

1. **Leverage Open Resources:** Use Gemma Scope and open SAEs rather than training from scratch
2. **Build on MIB:** Use mechanistic interpretability benchmark for evaluation
3. **Integrate Multiple Methods:** Combine SAEs with circuit tracing, consider transcoders for component-level analysis
4. **Focus on Validation:** Prioritize causal validation over correlational feature discovery
5. **Global Perspective:** Consider modular circuit approach for reusable interpretations
6. **Automate Where Possible:** Use automated interpretability tools to scale analysis

---

*Compiled: February 2026*
*Search Coverage: NeurIPS 2024, ICML 2024-2025, arXiv (2024-2025), major venues*
