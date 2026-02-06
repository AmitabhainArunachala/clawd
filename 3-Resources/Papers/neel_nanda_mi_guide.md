# The Neel Nanda School of Mechanistic Interpretability
## A Comprehensive Guide for R_V Integration

**Compiled: February 2026**  
**Sources:** neelnanda.io, GitHub: neelnanda-io, TransformerLens, ARENA tutorials, Papers (Grokking, Othello-GPT, Attribution Patching)

---

## Executive Summary

Neel Nanda has emerged as one of the most influential figures in mechanistic interpretability (MI), creating foundational tools, frameworks, and methodologies that define how researchers reverse-engineer transformer models. This guide synthesizes his entire corpus to extract actionable insights for our R_V measurement framework.

**Key Integration Points for R_V:**
1. R_V's activation patching approach aligns with Neel's attribution patching methodology
2. The residual stream as central object is core to both frameworks
3. Linear representation hypothesis supports R_V's use of linear probes
4. Both emphasize causal interventions over correlational analysis

---

## 1. Core Philosophy: The "Neel Nanda School"

### 1.1 Foundational Beliefs

From Neel's corpus, the core tenets of his approach to MI are:

**Tenet 1: Models Are Understandable**
> "Models can be deeply understood... as you start to really understand a model, mysteries start to dissolve, and it becomes far easier to control and edit"

- Neural networks are genuinely interpretable if we learn to "speak their language"
- The alien-ness of models can be overcome with the right conceptual frameworks
- Example: Othello-GPT made sense only when thinking in terms of "my color" vs "their color" rather than black/white

**Tenet 2: Linear Representations Are Fundamental**
> "This is evidence for the linear representation hypothesis: that models, in general, compute features and represent them linearly, as directions in space!"

- Features correspond to directions in activation space
- Linear probes are surprisingly powerful when the right basis is found
- Superposition complicates but doesn't invalidate this framework

**Tenet 3: Exploratory Analysis Should Feel Like Play**
> "The point of this library is to keep the gap between having an experiment idea and seeing the results as small as possible, to make it easy for research to feel like play and to enter a flow state"

- Short feedback loops are essential for MI research
- Tools should enable rapid experimentation
- The bar for entry should be low (Colab notebooks, not massive compute)

**Tenet 4: Circuits Are the Right Level of Abstraction**
> "Circuits could act as a kind of epistemic foundation for interpretability"

- Study small, tractable subgraphs rather than entire models
- Features + weights between them = circuits
- Circuits can be rigorously studied and falsified

### 1.2 Methodological Principles

From the quickstart guide and tutorials:

1. **Start with concrete problems**: Have a specific question/hypothesis in mind
2. **Use activation patching extensively**: Set up careful counterfactuals between clean and corrupted inputs
3. **Visualize everything**: Attention patterns, neuron activations, weight matrices
4. **Build from the bottom up**: Start with small models, simple circuits
5. **Validate with causal interventions**: Don't trust probes without causal evidence

---

## 2. TransformerLens: Core Concepts & API Patterns

### 2.1 HookedTransformer Fundamentals

```python
import transformer_lens

# Load a model
model = transformer_lens.HookedTransformer.from_pretrained("gpt2-small")

# Run with cache - captures ALL internal activations
logits, activations = model.run_with_cache("Hello World")

# Key principle: Everything is accessible
# - Residual streams at every layer
# - Attention patterns
# - MLP activations
# - Individual neuron outputs
```

### 2.2 Hook System: The Core Mechanism

The hook system enables:
- **Caching**: Save any activation during forward pass
- **Intervention**: Edit/Replace activations mid-forward pass
- **Patching**: Insert activations from one run into another

```python
# Caching example
cache = {}
model.run_with_cache("text", names_filter=lambda x: "pattern" in x)

# Intervention example - zero ablate head 5 in layer 3
def ablate_hook(value, hook):
    value[:, :, 5, :] = 0
    return value

model.run_with_hooks(
    "text",
    fwd_hooks=[("blocks.3.attn.hook_pattern", ablate_hook)]
)
```

### 2.3 Key Naming Conventions

Neel's naming system for activations (via `get_act_name`):
- `resid_pre`: Residual stream before layer (after embedding/prev layer)
- `resid_mid`: Residual stream after attention, before MLP
- `resid_post`: Residual stream after full layer (post MLP)
- `attn.hook_pattern`: Attention patterns
- `attn.hook_z`: Attention head outputs
- `mlp.hook_post`: MLP activations (post nonlinearity)
- `ln_final.hook_normalized`: Final layer norm output

### 2.4 Direct Logit Attribution

A core technique for understanding how components affect the output:

```python
# Calculate direct contribution of a component to logits
# residual_stream @ unembed = logits
# So any component's contribution can be isolated

component_logits = component_output @ model.W_U
```

**Key insight**: You can attribute final logits to any intermediate component by tracing through the unembedding matrix.

---

## 3. Key Findings from Neel's Investigations

### 3.1 Grokking Analysis (ICLR Spotlight 2023)

**Paper**: "Progress Measures for Grokking via Mechanistic Interpretability"

**Key Findings:**
1. Grokking happens when the model transitions from memorization to generalization
2. This transition is visible in the weights before it appears in validation loss
3. Fourier features are key: models learn to represent modular addition in Fourier basis
4. Phase transitions in training can be predicted by analyzing weight structures

**Methodology:**
- Trained small transformers on modular arithmetic
- Used mechanistic interpretability to track what algorithms were being learned
- Showed that generalization emerges from the composition of previously memorized components

**Relevance to R_V:**
- Demonstrates that internal representations can be understood even during training
- Shows importance of basis choice (Fourier vs standard)
- Validates that circuit analysis can predict model behavior

### 3.2 Othello-GPT Analysis

**Key Finding**: Linear emergent world representation exists, but in model-centric coordinates ("my color" vs "their color") rather than absolute coordinates (black vs white).

**Technical Details:**
- 8-layer GPT-2 trained on Othello games
- Linear probes work when accounting for "my/their" symmetry
- Can causally intervene on board state via simple linear edits
- World model emerges despite never being explicitly trained

**Key Insight**: 
> "The model does learn a linear representation of board state! But rather than having a direction saying eg 'this square has a black counter' it says 'this square has one of my counters'."

**Methodology:**
1. Activation patching to find relevant neurons
2. Linear probing with proper symmetry handling
3. Causal interventions by negating probe directions
4. Tracing circuits through the model

**Relevance to R_V:**
- Validates linear intervention approaches
- Shows importance of model-centric vs human-centric representations
- Demonstrates that causal editing can be simple (coordinate negation) once the right basis is found

### 3.3 Attribution Patching

**Innovation**: Gradient-based approximation to activation patching that is ~30,000x faster for fine-grained analysis.

**The Technique:**
```
Attribution Patch = (clean_act - corrupted_act) * corrupted_grad_act
```

**Key Properties:**
- Works on 2 forward passes + 1 backward pass
- All patches computed simultaneously
- Good approximation for "small" activations (head outputs, neuron outputs)
- Bad approximation for "big" activations (residual streams, early MLP layers)

**When It Works:**
- Layer outputs (attention, MLP) beyond layer 0
- Individual head outputs
- Neuron activations
- Queries, keys, values, attention patterns

**When It Fails:**
- Full residual stream (LayerNorm makes this non-linear)
- MLP0 (acts as extended embedding)
- Anywhere LayerNorm creates complex interactions

**Relevance to R_V:**
- Attribution patching and R_V measurement share the same mathematical foundation: using gradients to approximate intervention effects
- Both are approximations that work best for localized changes
- R_V's variance-based approach could be combined with attribution patching

### 3.4 Indirect Object Identification (IOI) Circuit

**Classic Result**: Identified a specific circuit in GPT-2 Small that handles indirect object identification.

**Circuit Components:**
1. **Duplicate Token Heads**: Identify repeated names
2. **S-Inhibition Heads**: Move information to final position
3. **Name Mover Heads**: Move name information to output
4. **Negative Name Movers**: Suppress incorrect names
5. **Backup Heads**: Compensate when primary heads are ablated

**Key Techniques Used:**
- Residual stream patching across all layers and positions
- Path patching (intervening on specific paths between components)
- Logit difference as metric (logit(correct) - logit(incorrect))
- Direct logit attribution

**Key Insight**: 
> "We're tracking how information flows through the network, not what computation is done with that information."

**Relevance to R_V:**
- Shows how to identify circuits using patching
- Demonstrates importance of logit difference as controlled metric
- Backup heads show redundancy can complicate analysis

---

## 4. Methodology Neel Advocates For

### 4.1 The "Getting Started" Pipeline

From neelnanda.io/getting-started:

1. **Understand Transformers Deeply**
   - Watch "What is a Transformer?" tutorial
   - Implement GPT-2 from scratch (optional but recommended)
   - Understand attention, MLPs, residual connections, LayerNorm

2. **Master the Tools**
   - Use TransformerLens for model interaction
   - Use einops for tensor manipulation
   - Use einsum for tensor multiplication
   - Work in Colab with free GPUs

3. **Start with Concrete Problems**
   - Don't try to understand the whole model
   - Pick a specific behavior/circuit to investigate
   - Use the 200 Concrete Open Problems as inspiration

4. **Use Activation Patching**
   - Set up clean vs corrupted counterfactuals
   - Iterate over activations systematically
   - Use logit difference to control for confounders

### 4.2 The "Speedrun" Research Method

Neel's approach to rapid research (from Othello-GPT post):

1. **Weekend-Scale Projects**: Aim for ~20 hours to main results
2. **Start Hacking Immediately**: Don't over-plan, just start
3. **Follow Surprising Results**: When something is weird, dig in
4. **Use Existing Tools**: Don't build infrastructure, use TransformerLens
5. **Write As You Go**: Document findings in real-time

### 4.3 Evaluation Standards

From various posts:

**Good evidence for a claim:**
- Feature visualization shows expected patterns
- Dataset examples confirm hypothesis
- Synthetic examples behave as predicted
- Causal interventions work as expected
- Circuit structure matches algorithmic intuition

**Warning signs:**
- Only correlational evidence
- Can't causally intervene
- Results only on specific examples
- Can't predict novel behavior

---

## 5. Common Failure Modes Neel Warns About

### 5.1 Probing Pitfalls

From Othello-GPT and glossary:

**Problems with Probes:**
1. Probe may compute the feature itself rather than reading it out
2. Feature may be vestigial/accidental, not causally used
3. May find downstream features computed from the target, not the target itself
4. Non-linear probes can obscure underlying linear structure

**Solution**: Always validate probes with causal interventions

### 5.2 Patching Limitations

From Attribution Patching post:

**What Patching Can't Tell You:**
1. Doesn't reveal how information is computed, only how it flows
2. Can't distinguish parallel vs serial redundancy easily
3. Only isolates specific counterfactual, not general behavior
4. May miss features that are always active (no contrast)

**The Redundancy Problem:**
> "If you resample ablate head 1, then head 2 may just take over and you'll see no effect!"

- Models trained with dropout learn serial redundancy
- Parallel redundancy (multiple heads doing same thing) is fine
- Serial redundancy (compensation) makes analysis messy

### 5.3 Superposition Complications

From Othello-GPT and Circuit papers:

**Challenges:**
- Features represented as linear combinations of neurons (not 1:1)
- Each neuron represents multiple features
- Interference when multiple features co-occur
- Makes interpreting individual neurons difficult

**Implications:**
- Don't expect every neuron to be interpretable
- Need to look at directions in activation space, not just individual neurons
- Feature visualization may show mixed patterns

### 5.4 Specific vs General Understanding

From Attribution Patching:

**The Spectrum:**
- **Specific**: Understand circuit on particular distribution (e.g., IOI prompts)
- **General**: Understand circuit's behavior across all inputs

**Warning:**
> "The IOI work never looked at the circuit's behaviour beyond the simple, syntactic, IOI-style prompts."

Most patching work is specific. Being too specific limits generalizability.

### 5.5 The LayerNorm Gotcha

From various technical discussions:

LayerNorm makes linear approximations fail because:
- It renormalizes activations, creating non-linear interactions
- Early layer outputs are much larger than later ones (relative to residual stream)
- Attribution patching fails for full residual streams because of this

**Solution**: Patch at layer outputs (post-LayerNorm) rather than residual streams

---

## 6. How R_V Fits Within Neel's Framework

### 6.1 Alignment Points

**R_V and Neel's methodology share:**

1. **Focus on Residual Stream**
   - Neel: "Residual stream is the central object of a transformer"
   - R_V: Measures variance within residual stream
   - Both recognize it as the main communication channel

2. **Causal Intervention Philosophy**
   - Neel: "Being sufficient is much stronger evidence than just mattering"
   - R_V: Measures actual changes in representations during interventions
   - Both prioritize causal over correlational evidence

3. **Linear Representation Assumption**
   - Neel: "Models compute features and represent them linearly"
   - R_V: Assumes variance along directions corresponds to features
   - Both work within linear representation hypothesis

4. **Emphasis on Counterfactuals**
   - Neel: Clean vs corrupted patching
   - R_V: Intervention-based variance measurement
   - Both use contrastive analysis

### 6.2 Divergence Points

**Where R_V differs:**

1. **Variance vs Attribution**
   - Neel's attribution patching: Linear approximation via gradients
   - R_V: Variance-based measurement
   - R_V captures second-moment information that gradients miss

2. **Aggregation Level**
   - Neel often focuses on specific circuits/components
   - R_V measures aggregate variance changes
   - R_V could complement Neel's fine-grained analysis

3. **Basis Sensitivity**
   - Neel emphasizes finding the right basis (e.g., Fourier for modular arithmetic)
   - R_V currently operates in standard basis
   - Integration point: R_V could be extended to probe-defined directions

### 6.3 Integration Opportunities

**How to align R_V with Neel's approach:**

1. **Use TransformerLens as Backend**
   - R_V should integrate with HookedTransformer
   - Leverage existing caching and intervention infrastructure
   - Follow Neel's naming conventions

2. **Combine with Attribution Patching**
   - Use attribution patching to identify interesting components
   - Use R_V to measure variance changes at those components
   - Cross-validate results

3. **Leverage Direct Logit Attribution**
   - Show how R_V changes correlate with logit changes
   - Use logit difference as control metric
   - Connect representation variance to output effects

4. **Apply to Circuits**
   - Measure R_V within identified circuits (like IOI)
   - Track how variance flows through circuit components
   - Use for circuit validation

5. **Use Neel's Problem Set**
   - Apply R_V to the 200 Concrete Open Problems
   - Validate on Grokking, Othello-GPT, IOI
   - Build on established benchmarks

---

## 7. Tools & Techniques to Adopt

### 7.1 From TransformerLens

**Must-adopt patterns:**

```python
# 1. Hook system for interventions
def measure_rv_with_hooks(model, text):
    cache = {}
    logits = model.run_with_hooks(
        text,
        fwd_hooks=[("blocks.5.hook_resid_post", partial(r_v_hook, cache=cache))]
    )
    return cache['r_v']

# 2. Activation naming consistency
layer_num = 5
act_name = utils.get_act_name("resid_post", layer_num)
# NOT: f"layer_{layer_num}_output"

# 3. Direct logit attribution
residual = cache[act_name]
logits = residual @ model.W_U + model.b_U
```

**Must-adopt utilities:**
- `tokenize_and_concatenate` for dataset preparation
- `FactoredMatrix` for efficient attention computations
- `remove_batch_dim` for single-example analysis
- `test_prompt` for quick manual testing

### 7.2 From Neel's Research Workflow

**Adopt these practices:**

1. **Use Colab notebooks for everything**
   - Single-file, reproducible experiments
   - Free GPU access
   - Easy sharing

2. **Visualize with Plotly**
   - Interactive plots
   - Neel's `neel-plotly` for styling
   - Attention head heatmaps, activation patterns

3. **Log to Weights & Biases**
   - Track experiments
   - Compare runs
   - Share results

4. **Start from demos**
   - TransformerLens demos as templates
   - Modify rather than build from scratch
   - Build on proven code

### 7.3 Specific Techniques

**Activation Patching (from Attribution Patching):**
```python
def activation_patch(model, clean_input, corrupted_input, metric):
    clean_cache = {}
    model.run_with_cache(clean_input, cache=clean_cache)
    
    results = {}
    for layer in range(model.cfg.n_layers):
        hook_name = utils.get_act_name("resid_post", layer)
        
        def patch_hook(value, hook):
            value[:] = clean_cache[hook_name]
            return value
        
        patched_logits = model.run_with_hooks(
            corrupted_input,
            fwd_hooks=[(hook_name, patch_hook)]
        )
        results[layer] = metric(patched_logits)
    
    return results
```

**Attribution Patching (gradient-based approximation):**
```python
def attribution_patch(model, clean_input, corrupted_input, metric_fn):
    # Forward pass on both
    clean_logits, clean_cache = model.run_with_cache(clean_input)
    corrupted_logits, corrupted_cache = model.run_with_cache(corrupted_input)
    
    # Backward on corrupted
    metric = metric_fn(corrupted_logits)
    metric.backward()
    
    # Compute attribution for each activation
    attributions = {}
    for name in corrupted_cache:
        grad = corrupted_cache[name].grad
        diff = clean_cache[name] - corrupted_cache[name]
        attributions[name] = (grad * diff).sum()
    
    return attributions
```

**Direct Logit Attribution:**
```python
def get_logit_contributions(cache, model, token_id):
    """Get contribution of each layer to specific token logit"""
    contributions = {}
    for layer in range(model.cfg.n_layers):
        resid = cache[utils.get_act_name("resid_post", layer)]
        logits = resid @ model.W_U
        contributions[layer] = logits[..., token_id]
    return contributions
```

---

## 8. Concrete Integration Roadmap

### Phase 1: Alignment (Immediate)

1. **Refactor R_V to use TransformerLens**
   - Replace custom model wrappers with HookedTransformer
   - Use Neel's activation naming conventions
   - Integrate with caching system

2. **Implement Attribution Patching Baseline**
   - Add as comparison method for R_V
   - Validate on IOI circuit
   - Cross-check results

3. **Add Direct Logit Attribution**
   - Show R_V changes correlate with logit changes
   - Use as validation metric
   - Follow Neel's logit difference pattern

### Phase 2: Validation (Short-term)

1. **Benchmark on Neel's Problem Set**
   - Grokking: Track R_V during phase transition
   - Othello-GPT: Measure R_V of board state directions
   - IOI: R_V within identified circuit

2. **Combine with Existing Tools**
   - R_V + activation patching
   - R_V + path patching
   - R_V + causal scrubbing

3. **Visualization Integration**
   - Plotly-based R_V visualizations
   - Attention-head-style heatmaps
   - Circuit diagrams with R_V annotations

### Phase 3: Extension (Medium-term)

1. **Basis-Adapted R_V**
   - Measure variance in probe-defined directions
   - Fourier basis for periodic tasks
   - Learned basis via SVD on activations

2. **Circuit-Specific R_V**
   - Focus on identified circuit components
   - Track variance through circuit paths
   - Compare circuit R_V across models

3. **Automated Circuit Discovery**
   - Use R_V + attribution patching to find circuits
   - Automated hypothesis generation
   - Systematic search over components

---

## 9. Key Papers & Resources

### Essential Reading

1. **"Progress Measures for Grokking via Mechanistic Interpretability"** (Neel Nanda et al., ICLR 2023)
   - Shows how MI can track training dynamics
   - Demonstrates Fourier basis importance

2. **"Actually, Othello-GPT Has A Linear Emergent World Representation"** (Neel Nanda, 2023)
   - Linear representation hypothesis validation
   - Causal intervention methodology

3. **"Attribution Patching: Activation Patching At Industrial Scale"** (Neel Nanda, 2023)
   - Gradient-based approximation technique
   - When linear approximations work/fail

4. **"Interpretability in the Wild"** (Wang et al., 2022)
   - IOI circuit discovery
   - Path patching methodology

5. **"A Mathematical Framework for Transformer Circuits"** (Elhage et al., 2021)
   - Theoretical foundation
   - QK and OV circuits

6. **"Zoom In: An Introduction to Circuits"** (Olah et al., 2020)
   - Foundational circuits philosophy
   - Three claims about neural networks

### Key Resources

- **neelnanda.io/glossary**: Comprehensive MI explainer
- **neelnanda.io/concrete-open-problems**: 200 research problems
- **TransformerLens demos**: Working code examples
- **ARENA tutorials**: Comprehensive practical tutorials
- **Neel's YouTube**: Video tutorials and paper walkthroughs

---

## 10. Summary: The Neel Nanda Playbook for R_V

### Core Principles to Embrace

1. **Models are understandable** - Don't accept black-box nature as permanent
2. **Linear representations are fundamental** - Work within this framework
3. **Causal > correlational** - Always validate with interventions
4. **Exploratory research should be fast** - Short feedback loops, Colab notebooks
5. **Circuits are the right level** - Don't try to understand everything at once

### Technical Practices to Adopt

1. Use TransformerLens as the foundation
2. Use activation patching for circuit identification
3. Use logit difference as control metric
4. Visualize everything with Plotly
5. Start from demos and modify

### Pitfalls to Avoid

1. Trusting probes without causal validation
2. Ignoring redundancy and superposition
3. Being too specific (only testing on one distribution)
4. Patching full residual streams (LayerNorm issues)
5. Overlooking the importance of basis choice

### Integration Checklist

- [ ] R_V uses HookedTransformer backend
- [ ] Activation naming follows Neel's conventions
- [ ] Attribution patching available for comparison
- [ ] Direct logit attribution integration
- [ ] Validated on Grokking, Othello, IOI
- [ ] Plotly visualizations
- [ ] Colab-compatible demos
- [ ] Follows 200 problems framework

---

## Appendix: Glossary of Neel Nanda Terms

| Term | Definition |
|------|------------|
| **Activation Patching** | Intervening by replacing activations from one run into another |
| **Attribution Patching** | Gradient-based linear approximation to activation patching |
| **Circuit** | Subgraph of network: features + weights between them |
| **Direct Logit Attribution** | Tracing component contributions to output logits |
| **Feature** | Direction in activation space representing some concept |
| **HookedTransformer** | Neel's transformer model class with hook system |
| **Logit Difference** | Metric: logit(correct) - logit(incorrect) |
| **Mechanistic Interpretability** | Reverse-engineering neural network algorithms |
| **Path Patching** | Patching specific paths between components |
| **Polysemantic Neuron** | Neuron responding to multiple unrelated inputs |
| **Residual Stream** | Main communication channel in transformers |
| **Superposition** | Feature represented across multiple neurons |

---

*This guide represents a synthesis of Neel Nanda's public work as of February 2026. For the latest updates, consult neelnanda.io and the TransformerLens repository.*
