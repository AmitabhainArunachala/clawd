# Top Model Architecture & Data Pipeline Repositories

*Research compiled: 2026-02-15*

**Focus:** Efficient architectures and data pipelines that scale down for solo developers

---

## 1. 🦙 Transformers: Llama / Mistral / Qwen / DeepSeek

### **Meta Llama Models**
- **URL:** https://github.com/meta-llama/llama
- **Purpose:** Official Meta Llama 2/3 implementation, reference architecture
- **Efficiency:** 
  - Grouped Query Attention (GQA) for inference speed
  - SwiGLU activation, RoPE positional encoding
  - FlashAttention-2 compatible
- **One-Person Viability:** ⭐⭐⭐
  - Clean reference code (~500 lines core model)
  - Good starting point, but lacks training infrastructure
  - Use HuggingFace transformers for practical work

### **HuggingFace Transformers**
- **URL:** https://github.com/huggingface/transformers
- **Purpose:** Universal model hub with implementations for 100+ architectures
- **Efficiency:**
  - `AutoModel` for automatic architecture detection
  - `bitsandbytes` integration for 4-bit/8-bit inference
  - `accelerate` for distributed training
- **One-Person Viability:** ⭐⭐⭐⭐⭐
  - One-liner model loading: `AutoModel.from_pretrained("mistralai/Mistral-7B")`
  - Pre-built training scripts in `examples/`
  - Massive community, extensive docs

### **Unsloth**
- **URL:** https://github.com/unslothai/unsloth
- **Purpose:** 2-5x faster finetuning, 70% less memory for Llama/Mistral
- **Efficiency:**
  - Hand-optimized Triton kernels
  - Automatic gradient checkpointing
  - 4-bit/8-bit QLoRA out of the box
- **One-Person Viability:** ⭐⭐⭐⭐⭐
  - Drop-in replacement for HF trainers
  - Single-GPU finetuning of 70B models possible
  - Colab notebooks provided

### **axolotl**
- **URL:** https://github.com/OpenAccess-AI-Collective/axolotl
- **Purpose:** YAML-configured LLM training (finetuning focus)
- **Efficiency:**
  - FSDP, DeepSpeed, QLoRA support
  - Pre-configured for popular datasets
  - Multi-GPU scaling
- **One-Person Viability:** ⭐⭐⭐⭐
  - YAML configs > writing training loops
  - Great for common tasks, less flexible for research

---

## 2. ⚡ Alternative Architectures

### **Mamba / State Space Models**

#### **state-spaces/mamba**
- **URL:** https://github.com/state-spaces/mamba
- **Purpose:** Official Mamba (S4) and Mamba-2 implementation
- **Efficiency:**
  - Linear complexity vs quadratic attention
  - Selective state spaces for long sequences
  - Hardware-aware fused CUDA kernels
- **One-Person Viability:** ⭐⭐⭐⭐
  - Drop-in attention replacement
  - ~30% faster training, much faster on long sequences
  - Requires custom CUDA setup

#### **mamba-minimal**
- **URL:** https://github.com/johnma2006/mamba-minimal
- **Purpose:** Pure PyTorch Mamba implementation (educational)
- **Efficiency:**
  - No custom CUDA kernels (slower but simpler)
  - ~200 lines of readable code
- **One-Person Viability:** ⭐⭐⭐⭐⭐
  - Best for understanding/learning
  - Easy to modify for research

### **RWKV**

#### **RWKV-LM**
- **URL:** https://github.com/BlinkDL/RWKV-LM
- **Purpose:** RNN with Transformer-level performance, constant VRAM usage
- **Efficiency:**
  - O(1) inference memory (vs O(n) for attention)
  - Trainable with parallelization tricks
  - 14B model runs on single consumer GPU
- **One-Person Viability:** ⭐⭐⭐⭐⭐
  - Minimal dependencies
  - Great for edge deployment
  - Active Discord community

### **RetNet**

#### **microsoft/RetNet**
- **URL:** https://github.com/microsoft/torchscale/tree/main/examples/fairseq/models/retnet
- **Purpose:** Microsoft's "Transformer killer" with parallel+recurrent training
- **Efficiency:**
  - Parallel training, recurrent inference
  - Chunkwise retention for long sequences
- **One-Person Viability:** ⭐⭐⭐
  - Experimental, less ecosystem support
  - Good for research exploration

---

## 3. 🔄 Data Processing Pipelines

### **FineWeb / datatrove**

#### **huggingface/datatrove**
- **URL:** https://github.com/huggingface/datatrove
- **Purpose:** Large-scale data processing for LLM pretraining
- **Efficiency:**
  - Pipeline-based architecture
  - Built-in deduplication (MinHash, exact)
  - Multiprocessing + memory mapping
- **One-Person Viability:** ⭐⭐⭐⭐
  - Handles Common Crawl scale
  - Modular blocks easy to customize
  - Good for 1-10TB scale

### **dclm**
- **URL:** https://github.com/mlfoundations/dclm
- **Purpose:** DataComp for Language Models - best practices data pipeline
- **Efficiency:**
  - Proven filtering heuristics
  - Quality scoring models included
  - End-to-end from crawl to tokens
- **One-Person Viability:** ⭐⭐⭐⭐
  - Research-validated approach
  - Good starting point, may need customization

### **deduplicate-text-datasets**
- **URL:** https://github.com/google-research/deduplicate-text-datasets
- **Purpose:** Google's suffix array deduplication (used in PaLM, GPT-3)
- **Efficiency:**
  - Exact substring deduplication
  - Handles 100GB+ datasets
  - Memory-efficient suffix arrays
- **One-Person Viability:** ⭐⭐⭐
  - Requires Rust compilation
  - Powerful but complex interface

### **MinHash CUDA**
- **URL:** https://github.com/ekzhu/minhashcuda
- **Purpose:** Fast near-duplicate detection on GPU
- **Efficiency:**
  - CUDA-accelerated MinHash
  - Jaccard similarity estimation
- **One-Person Viability:** ⭐⭐⭐⭐
  - Simple API for fuzzy dedup
  - Good for pre-filtering large datasets

---

## 4. 📊 Evaluation Frameworks

### **lm-evaluation-harness**
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Purpose:** The standard for LLM evaluation (200+ tasks)
- **Efficiency:**
  - One command: `lm_eval --model hf --model_args pretrained=model --tasks hellaswag,arc_easy`
  - Model caching, batch inference
  - HuggingFace, vLLM, OpenAI API support
- **One-Person Viability:** ⭐⭐⭐⭐⭐
  - Zero-config for standard benchmarks
  - Easy to add custom tasks
  - Industry standard (reported in most papers)

### **OpenLLM Leaderboard**
- **URL:** https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
- **Purpose:** Community benchmark aggregation
- **Efficiency:**
  - Automated evaluation pipeline
  - Normalized scores across tasks
- **One-Person Viability:** ⭐⭐⭐⭐
  - Submit models via HuggingFace
  - Good for comparing to SOTA

### **bigcode-evaluation-harness**
- **URL:** https://github.com/bigcode-project/bigcode-evaluation-harness
- **Purpose:** Code-specific evaluation (HumanEval, MBPP, etc.)
- **Efficiency:**
  - Execution-based evaluation (not just BLEU)
  - Multi-language support
- **One-Person Viability:** ⭐⭐⭐⭐
  - Essential for code models
  - Sandboxed execution included

### **MT-Bench / FastChat**
- **URL:** https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge
- **Purpose:** LLM-as-judge for open-ended evaluation
- **Efficiency:**
  - GPT-4 based judging
  - Multi-turn conversation evaluation
- **One-Person Viability:** ⭐⭐⭐⭐
  - Good for instruction-tuned models
  - Subjective but practical

---

## 5. 🧬 Synthetic Data Generation

### **self-instruct / Alpaca**
- **URL:** https://github.com/tatsu-lab/stanford_alpaca
- **Purpose:** Seed-based instruction generation with GPT
- **Efficiency:**
  - ~$500 to generate 52K instructions
  - Simple seed-and-generate approach
- **One-Person Viability:** ⭐⭐⭐⭐
  - Well-documented pipeline
  - Proven approach (Alpaca, Vicuna)

### **argilla/distilabel**
- **URL:** https://github.com/argilla-io/distilabel
- **Purpose:** Modern synthetic data generation framework
- **Efficiency:**
  - LLM-as-judge pipelines
  - Preference dataset generation (DPO/RLHF)
  - Async/concurrent generation
- **One-Person Viability:** ⭐⭐⭐⭐⭐
  - Modern Python, good docs
  - Handles synthetic data at scale
  - Integrates with Argilla for human review

### **Magpie**
- **URL:** https://github.com/magpie-align/magpie
- **Purpose:** Generate instruction data from model's own completions
- **Efficiency:**
  - No seed instructions needed
  - Leverages pretraining knowledge
  - ~1M samples for ~$200
- **One-Person Viability:** ⭐⭐⭐⭐
  - Self-bootstrapping approach
  - Good quality for the cost

### **glaive-function-calling**
- **URL:** https://huggingface.co/datasets/glaiveai/glaive-function-calling-v2
- **Purpose:** Synthetic function calling dataset generation
- **Efficiency:**
  - Tool-use format generation
  - Structured output training
- **One-Person Viability:** ⭐⭐⭐⭐
  - Great for agent/tool models
  - Template-based generation

---

## 🏆 Top 10 Recommendations for One-Person Teams

| Rank | Repository | Category | Why It Wins |
|------|------------|----------|-------------|
| 1 | **huggingface/transformers** | Transformers | Universal standard, vast ecosystem |
| 2 | **unsloth** | Training | 5x speedup, 70% memory savings |
| 3 | **lm-evaluation-harness** | Evaluation | Industry standard, 200+ tasks |
| 4 | **state-spaces/mamba** | Alternative Arch | Linear complexity, production-ready |
| 5 | **RWKV-LM** | Alternative Arch | O(1) memory, edge deployment |
| 6 | **datatrove** | Data Processing | Scales down, modular design |
| 7 | **distilabel** | Synthetic Data | Modern, async, preference data |
| 8 | **axolotl** | Training | YAML configs, zero-code training |
| 9 | **mamba-minimal** | Learning | Understand SSM in 200 lines |
| 10 | **bigcode-evaluation-harness** | Evaluation | Essential for code models |

---

## 💡 Quick Start Stack for Solo Developers

**Training Pipeline:**
```
Data: datatrove → datatrove (dedup) → tokenizers
Model: transformers (arch) + unsloth (training)
Eval: lm-evaluation-harness + bigcode-evaluation-harness
Data Gen: distilabel (synthetic instructions)
```

**Efficiency Tips:**
- Use **unsloth** for any finetuning (5x faster, works on smaller GPUs)
- Use **RWKV** for inference-heavy, memory-constrained deployments
- Use **datatrove** pipelines as templates, customize for your data
- Start with **lm-evaluation-harness** before building custom eval

---

## References

- Mamba paper: Gu & Dao, 2023
- RWKV paper: Peng et al., 2023
- Unsloth benchmarks: https://docs.unsloth.ai/
- DataComp: Li et al., 2024
- Self-Instruct: Wang et al., 2022
