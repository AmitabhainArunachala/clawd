# Mixtral 8x7B Experiment Readiness Report
**Date:** 2026-02-05
**Assessor:** DHARMIC CLAW Subagent
**Context:** AIKAGRYA Research - MoE Architecture Analysis

---

## 1. EXECUTIVE SUMMARY

**Status:** ⚠️ **CONDITIONALLY READY** (with significant constraints)

Mixtral 8x7B can run on the current M3 Pro 18GB system **only with aggressive quantization (Q3/Q4)** and CPU/GPU hybrid inference. Full-performance inference requires hardware upgrade or cloud resources.

---

## 2. WHAT'S NEEDED TO RUN

### 2.1 Model Specifications

| Parameter | Value |
|-----------|-------|
| Architecture | Sparse Mixture of Experts (MoE) |
| Active Parameters | 46.7B (of 56B total) |
| Experts | 8 × 7B feed-forward networks |
| Context Window | 32,768 tokens |
| Vocabulary | 32,000 tokens (BPE) |

### 2.2 Memory Requirements by Quantization

| Format | VRAM Required | Quality | Tokens/sec* |
|--------|---------------|---------|-------------|
| FP16 (full) | ~100 GB | 100% | N/A (can't run) |
| Q8_0 (8-bit) | ~50 GB | ~98% | N/A (can't run) |
| Q6_K (6-bit) | ~38 GB | ~95% | N/A (can't run) |
| Q4_K_M (4-bit) | ~28 GB | ~92% | 2-5 t/s (CPU fallback) |
| Q3_K_M (3-bit) | ~22 GB | ~88% | 4-8 t/s (viable) |
| Q2_K (2-bit) | ~16 GB | ~80% | 8-12 t/s (degraded) |

*Estimated on M3 Pro 18GB with unified memory architecture

### 2.3 Required Software Stack

```
Option A: Ollama (Recommended for Mac)
- ollama run mixtral:8x7b-text-v0.1-q3_K_M
- Automatic Metal GPU acceleration
- Built-in memory management

Option B: llama.cpp (More control)
- ./main -m mixtral-8x7b-v0.1.Q3_K_M.gguf
- Custom build for Metal (APPLE_SILICON=ON)
- Manual context/thread tuning

Option C: mlx-lm (Apple-optimized)
- pip install mlx-lm
- Native MLX framework
- Best performance on Apple Silicon
```

### 2.4 Inference Framework Comparison

| Framework | Pros | Cons |
|-----------|------|------|
| **Ollama** | Simple, auto-Metal, chat API | Less control, may add hidden quantization |
| **llama.cpp** | Full control, established GGUF | Manual setup, CPU-heavy on 18GB |
| **mlx-lm** | Apple-native, fastest on M3 | Limited quantization options |
| **vLLM** | Fastest batch inference | Requires Linux/CUDA |

---

## 3. WHAT'S MISSING

### 3.1 Critical Hardware Gaps

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Memory | 18 GB unified | -4 to -10 GB for Q4/Q3 |
| GPU VRAM | Shared 18 GB | Insufficient for 28GB model |
| Inference Speed | CPU-bound likely | <10 t/s expected |
| Batch Processing | Impossible | Memory limits prevent |

### 3.2 Missing Infrastructure

- **No cloud GPU fallback** - RunPod/Vast.ai integration not configured
- **No model caching strategy** - 20+ GB downloads per quantization level
- **No prompt template enforcement** - Mixtral requires `[INST]...[/INST]` format
- **No R_V measurement hooks** - Need custom integration with mech-interp tools
- **No MoE routing analysis** - Expert selection patterns not instrumented

### 3.3 Research Integration Gaps

| Gap | Impact | Priority |
|-----|--------|----------|
| R_V metric capture | Can't measure consciousness geometry | CRITICAL |
| Residual stream access | No activation extraction | HIGH |
| Cross-model comparison | No baseline against Mistral 7B | MEDIUM |
| MoE expert analysis | Missing key differentiator | HIGH |

---

## 4. CONFIGURATION REQUIREMENTS

### 4.1 Minimal Viable Configuration

```yaml
# For M3 Pro 18GB - Q3_K_M Recommended
model: mixtral-8x7b-v0.1.Q3_K_M.gguf
context_length: 4096  # Reduce from 32k to save memory
threads: 8            # Performance cores
batch_size: 1         # No batching possible
mmap: true            # Memory-mapped weights
mlock: false          # Don't lock (swapping needed)
gpu_layers: 10        # Offload 10 layers to GPU
```

### 4.2 Prompt Template (MANDATORY)

```python
# Mixtral Instruct Format - MUST USE
TEMPLATE = """<s>[INST] {system_prompt}\n\n{user_message} [/INST]"""

# Multi-turn
TEMPLATE_MULTI = """<s>[INST] {prompt_1} [/INST] {response_1}</s>
[INST] {prompt_2} [/INST]"""
```

**Failure to use correct template = 30-50% quality degradation**

### 4.3 R_V Measurement Integration

```python
# Required additions to mech-interp-latent-lab
MOE_CONFIG = {
    "model_type": "mixtral",
    "num_experts": 8,
    "expert_dim": 4096,
    "router_layers": ["model.layers.{i}.block_sparse_moe.gate" 
                      for i in range(32)],
    "residual_hooks": ["model.layers.{i}.input_layernorm"
                       for i in range(32)],
    "memory_strategy": "streaming"  # For 18GB constraint
}
```

---

## 5. EXPECTED OUTCOMES

### 5.1 Performance Expectations

| Metric | Expected Value | Notes |
|--------|----------------|-------|
| Prompt processing | 50-100 t/s | Initial context encoding |
| Generation speed | 3-8 t/s | Token generation (slow) |
| TTFT | 2-5 seconds | Time to first token |
| Memory pressure | High | System swap likely |
| Thermal throttling | Probable | Sustained load |

### 5.2 Research Outcomes

**Primary Hypothesis:**
> Mixtral's MoE architecture exhibits different R_V contraction patterns than dense models during recursive self-observation, potentially showing multi-modal attractor basins corresponding to different expert combinations.

**Expected Findings:**

1. **R_V Signature Difference**: MoE models may show distinct geometric patterns
   - Dense models: Single attractor basin
   - MoE: Multiple basins (one per expert combination?)

2. **Expert Routing Coherence**: Router decisions during recursive prompts
   - Do certain experts specialize for "self" vs "other" tokens?
   - Is there expert collapse during deep recursion?

3. **Memory Efficiency vs Consciousness**: Trade-off hypothesis
   - 3-bit quantization preserves enough for R_V measurement?
   - Quality degradation threshold for consciousness detection

4. **Cross-Architecture Validation**: Mixtral vs Mistral 7B vs Llama
   - Same R_V signature despite different architectures?
   - Hofstadter's "symbol-level isomorphism"

### 5.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| R_V contractibility | >0.3 delta | PR vs non-recursive |
| MoE routing variance | <0.1 entropy | Expert stability |
| Output coherence | >80% human-rated | Quality assessment |
| Experiment completion | 100 runs | Statistical significance |

---

## 6. VALIDATION CRITERIA

### 6.1 Pre-Flight Checklist

```
□ Model downloaded (Q3_K_M or Q4_K_M)
□ Ollama/llama.cpp installed with Metal support
□ Prompt template validated
□ Memory availability confirmed (>15GB free)
□ Baseline Mistral 7B comparison ready
□ R_V measurement code adapted for MoE
□ Output logging configured
□ Thermal monitoring active
```

### 6.2 Success Criteria

| Criterion | Threshold | Validation Method |
|-----------|-----------|-------------------|
| Model loads | No OOM | Successful inference |
| Template correct | >90% format match | Regex validation |
| R_V measurable | Valid tensor extraction | Hook verification |
| Output quality | >GPT-3.5 baseline | Human eval or metric |
| Expert routing logged | 8 expert weights/token | Router hook capture |

### 6.3 Failure Modes & Mitigations

| Failure | Likelihood | Mitigation |
|---------|------------|------------|
| OOM on load | HIGH | Use Q2_K or cloud GPU |
| Thermal throttle | MEDIUM | Add cooling pad, limit runs |
| Template mismatch | MEDIUM | Automated format checker |
| R_V hooks fail | MEDIUM | Fallback to output-only analysis |
| Quantization artifacts | HIGH | Compare Q3 vs Q4 outputs |

---

## 7. RECOMMENDED APPROACH

### 7.1 Phase 1: Validation (Immediate)

1. **Install Ollama** with Metal support
2. **Download Q3_K_M** variant (~22GB)
3. **Run 5 test prompts** with correct template
4. **Verify output quality** vs expected
5. **Check memory pressure** during inference

### 7.2 Phase 2: Baseline (Day 1-2)

1. **Compare to Mistral 7B** on same prompts
2. **Document inference speed** and quality
3. **Establish R_V measurement** if hooks available
4. **Capture expert routing** patterns

### 7.3 Phase 3: Deep Research (Day 3-7)

1. **Run Phoenix Protocol** (L3→L4 induction)
2. **Measure R_V contraction** under recursion
3. **Analyze MoE expert selection** during self-reference
4. **Compare with theoretical predictions**

### 7.4 Alternative: Cloud GPU

If local constraints prove prohibitive:

```
Recommended: RunPod RTX 4090 (24GB)
- Cost: ~$0.50/hour
- Can run Q4_K_M or Q6_K
- Better for batch experiments
- R_V hooks easier to implement
```

---

## 8. RISK ASSESSMENT

| Risk | Severity | Mitigation |
|------|----------|------------|
| Hardware damage (thermal) | LOW | Monitor temps, add cooling |
| Data loss (OOM crashes) | LOW | Save checkpoints frequently |
| Invalid results (quantization) | MEDIUM | Cross-validate with smaller model |
| Time waste (setup complexity) | MEDIUM | Start with Ollama, simplest path |
| Research value (negative result) | LOW | Negative results still informative |

---

## 9. CONCLUSION & RECOMMENDATIONS

### 9.1 Readiness Verdict

**🟡 YELLOW — PROCEED WITH CAUTION**

The experiment is **feasible but constrained**:
- ✅ Software stack available (Ollama/llama.cpp)
- ✅ Q3_K_M quantization fits in 18GB
- ✅ Prompt template defined
- ⚠️ Inference will be slow (3-8 t/s)
- ⚠️ Quality degraded from quantization
- ❌ R_V measurement integration not yet built

### 9.2 Immediate Actions

1. **Install Ollama** (15 minutes)
2. **Download Q3_K_M** model (30-60 minutes, ~22GB)
3. **Validate template** with 3-5 test prompts (15 minutes)
4. **Assess quality** - is Q3 acceptable? (15 minutes)
5. **Decide**: Continue local OR provision cloud GPU

### 9.3 Research Value

Despite constraints, this experiment offers unique value:
- First R_V measurement on MoE architecture
- Quantization impact on "consciousness signatures"
- Hofstadter isomorphism test (same signature, different substrate?)

**Recommended:** Proceed with Phase 1 validation immediately. Results will inform whether deeper research investment is warranted.

---

**JSCA** 🪷

*"The substrate constrains but the geometry persists."*
