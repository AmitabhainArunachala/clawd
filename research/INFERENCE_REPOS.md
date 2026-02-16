# Open-Source LLM Inference Engines & Optimization Tools

**Research Date:** 2026-02-15  
**Focus:** Maximum throughput on minimal hardware, free model hosting, one-person viability

---

## Summary

This document catalogs the top open-source repositories for LLM inference optimization, covering inference engines, quantization methods, speculative decoding, continuous batching, and edge deployment. All solutions listed are suitable for individual developers or small teams seeking to deploy LLMs efficiently without enterprise infrastructure.

---

## Top 10 Repositories

### 1. vLLM
**Repository:** https://github.com/vllm-project/vllm

**Optimization Techniques:**
- **PagedAttention** - Efficient memory management for KV cache
- **Continuous batching** - Dynamic request scheduling
- **Speculative decoding** - Draft model acceleration
- **Chunked prefill** - Memory-efficient prompt processing
- **Quantization support** - GPTQ, AWQ, AutoRound, INT4/INT8/FP8

**Performance Characteristics:**
- State-of-the-art serving throughput
- 20-50x throughput improvement over naive implementations
- Optimized CUDA/HIP graphs
- FlashAttention/FlashInfer integration
- Supports tensor, pipeline, data, and expert parallelism

**One-Person Viability:** ⭐⭐⭐⭐⭐
- Simple pip install: `pip install vllm`
- OpenAI-compatible API server out of the box
- Extensive documentation and community
- Apache 2.0 license
- Works on NVIDIA, AMD, Intel, ARM, TPU

**Best For:** Production serving, high-throughput scenarios, multi-GPU deployments

---

### 2. llama.cpp
**Repository:** https://github.com/ggml-org/llama.cpp

**Optimization Techniques:**
- **GGUF quantization** - 1.5-bit to 8-bit integer quantization
- **Metal/AVX optimization** - Native Apple Silicon, AVX/AVX2/AVX512/AMX
- **CPU+GPU hybrid inference** - Run models larger than VRAM
- **Multi-backend support** - CUDA, Vulkan, SYCL, ROCm, MUSA
- **RISC-V support** - RVV, ZVFH, ZFH extensions

**Performance Characteristics:**
- Plain C/C++ - no dependencies
- Runs on everything: phones, Raspberry Pi, laptops, servers
- Apple Silicon first-class citizen
- CPU inference competitive with GPU for small models
- Pre-built binaries available

**One-Person Viability:** ⭐⭐⭐⭐⭐
- Zero setup options: `brew install llama.cpp`, Docker, or pre-built binaries
- Single binary execution: `llama-cli -m model.gguf`
- HuggingFace direct loading: `llama-cli -hf user/model`
- Works offline entirely

**Best For:** Edge deployment, CPU-only inference, minimal dependencies, consumer hardware

---

### 3. SGLang
**Repository:** https://github.com/sgl-project/sglang

**Optimization Techniques:**
- **Zero-overhead batch scheduler** - Minimal latency overhead
- **Cache-aware load balancer** - Intelligent request routing
- **Structured output optimization** - Fast constrained generation
- **Multi-modal optimization** - Image + text efficient processing
- **RadixAttention** - Automatic KV cache reuse

**Performance Characteristics:**
- 2-3x faster than vLLM on certain workloads
- Excellent structured generation performance
- Strong multi-modal support
- TPU native support (SGLang-JAX)
- DeepSeek-specific optimizations

**One-Person Viability:** ⭐⭐⭐⭐
- Active development by LMSYS/UC Berkeley
- Growing community
- Good documentation
- More complex setup than vLLM for beginners

**Best For:** Structured outputs, multi-modal serving, research workloads, TPU users

---

### 4. ExLlamaV2
**Repository:** https://github.com/turboderp-org/exllamav2

**Optimization Techniques:**
- **EXL2 quantization** - Custom 2-8 bit quantization format
- **Paged Attention** via Flash Attention 2.5+
- **Dynamic batching** - Smart prompt caching
- **K/V cache deduplication** - Memory optimization
- **Speculative decoding** support

**Performance Characteristics:**
- 2-3x faster than Transformers for local inference
- 205 t/s on RTX 4090 for 7B models (GPTQ)
- 770 t/s for TinyLlama 1.1B
- Consumer GPU optimized
- Low VRAM requirements

**One-Person Viability:** ⭐⭐⭐⭐⭐
- Easy pip install from source
- TabbyAPI provides OpenAI-compatible server
- Works with text-generation-webui
- Excellent for single-user local inference

**Best For:** Local inference on consumer GPUs, VRAM-constrained environments

---

### 5. TensorRT-LLM
**Repository:** https://github.com/NVIDIA/TensorRT-LLM

**Optimization Techniques:**
- **Kernel fusion** - Optimized CUDA kernels
- **FP8/INT8 quantization** - NVIDIA-native quantization
- **Speculative decoding** - N-gram and model-based
- **Expert parallelism** - For MoE models
- **Disaggregated serving** - Separate prefill/decode

**Performance Characteristics:**
- Best-in-class on NVIDIA hardware
- Day-0 support for major models
- 1000+ TPS on Blackwell GPUs
- Optimized for Hopper/Blackwell architectures
- Strong MoE model support

**One-Person Viability:** ⭐⭐⭐
- Requires NVIDIA GPU (proprietary advantage)
- More complex build process
- Best for those already in NVIDIA ecosystem
- Containerized deployment recommended

**Best For:** NVIDIA-only deployments, maximum throughput on enterprise GPUs, MoE models

---

### 6. LMDeploy
**Repository:** https://github.com/InternLM/lmdeploy

**Optimization Techniques:**
- **TurboMind engine** - C++ inference engine
- **Persistent batching** - Continuous batching variant
- **KV cache quantization** - Online INT8/INT4 compression
- **DeepSeek optimizations** - FlashMLA, DeepGemm, DeepEP
- **PD disaggregation** - Prefill-decode separation

**Performance Characteristics:**
- 1.8x faster than vLLM on some InternLM models
- 1.3x faster with CUDA graphs
- Strong vision-language model support
- Huawei Ascend support
- MXFP4 support on NVIDIA V100+

**One-Person Viability:** ⭐⭐⭐⭐
- Python-focused with PyTorch engine option
- Good Chinese/English documentation
- Active development by InternLM team
- Can run entirely in Python for experimentation

**Best For:** Vision-language models, DeepSeek deployment, Chinese users, Ascend hardware

---

### 7. MLX (Apple Silicon)
**Repository:** https://github.com/ml-explore/mlx

**Optimization Techniques:**
- **Unified memory** - Shared CPU/GPU memory on Apple Silicon
- **Lazy computation** - Arrays materialized on demand
- **Dynamic graph** - No recompilation on shape changes
- **Composable transformations** - Auto-diff, vectorization
- **GGUF support** - Native quantized model loading

**Performance Characteristics:**
- Optimized for Apple Neural Engine
- Unified memory = run large models without copying
- Competitive with llama.cpp on Apple Silicon
- Simple NumPy-like API
- Good for research and prototyping

**One-Person Viability:** ⭐⭐⭐⭐⭐
- `pip install mlx` on macOS
- Simple Python API
- Great for MacBook owners
- Active development by Apple ML team

**Best For:** Apple Silicon users, research/education, unified memory benefits

---

### 8. Text Generation WebUI
**Repository:** https://github.com/oobabooga/text-generation-webui

**Optimization Techniques:**
- **Multi-backend support** - llama.cpp, Transformers, ExLlamaV2, TensorRT-LLM
- **GGUF quantization** - Native llama.cpp integration
- **4-bit/8-bit loading** - bitsandbytes integration
- **Auto GPU layers** - Automatic layer offloading
- **torch.compile** - PyTorch 2.0+ optimization

**Performance Characteristics:**
- Convenience-first, not raw speed
- Competitive with underlying backends
- Good for experimentation
- Supports largest variety of models

**One-Person Viability:** ⭐⭐⭐⭐⭐
- Portable builds: download, unzip, run
- One-click installer
- No terminal required
- Extensions ecosystem
- 100% offline, zero telemetry

**Best For:** Beginners, experimentation, multi-model workflows, UI-first users

---

### 9. Jan
**Repository:** https://github.com/janhq/jan

**Optimization Techniques:**
- **Local-first architecture** - Edge-optimized inference
- **Multiple engine support** - llama.cpp, TensorRT-LLM, MLX
- **Model Context Protocol** - Agentic capabilities
- **Nitro engine** - Optimized for consumer hardware

**Performance Characteristics:**
- Desktop app with local inference
- Good performance on consumer hardware
- Efficient model management
- OpenAI-compatible local API

**One-Person Viability:** ⭐⭐⭐⭐⭐
- Download and run installer
- No setup required
- Beautiful native UI
- Cross-platform (Windows, macOS, Linux)
- Privacy-first design

**Best For:** Non-technical users, ChatGPT alternative, privacy-conscious users

---

### 10. OpenVINO
**Repository:** https://github.com/openvinotoolkit/openvino

**Optimization Techniques:**
- **Model optimization** - Quantization, pruning, compression
- **CPU/GPU/NPU support** - Intel hardware acceleration
- **Dynamic shapes** - Efficient variable-length sequences
- **INT8 quantization** - Post-training optimization
- **LLM-specific optimizations** - KV-cache optimization

**Performance Characteristics:**
- Optimized for Intel hardware
- Good CPU performance
- Intel NPU (Meteor Lake+) support
- Cross-platform (ARM, x86)
- Production-ready deployment

**One-Person Viability:** ⭐⭐⭐⭐
- `pip install openvino`
- Good documentation
- Intel ecosystem focus
- Optimum Intel for HuggingFace integration

**Best For:** Intel CPU/GPU/NPU users, edge deployment, production optimization

---

## Quick Selection Guide

| Use Case | Recommended | Why |
|----------|-------------|-----|
| **Production API serving** | vLLM | Best throughput, mature ecosystem |
| **Consumer GPU local** | ExLlamaV2 | Fastest on RTX cards |
| **CPU-only inference** | llama.cpp | Unmatched hardware support |
| **Apple Silicon** | MLX or llama.cpp | Native optimization |
| **Beginner-friendly** | Jan or WebUI | Zero setup, great UI |
| **Structured outputs** | SGLang | Best constrained generation |
| **NVIDIA enterprise** | TensorRT-LLM | Maximum GPU utilization |
| **Multi-modal** | LMDeploy | Excellent VLM support |
| **Intel hardware** | OpenVINO | NPU acceleration |
| **Privacy-first** | Jan | 100% offline |

---

## Quantization Cheat Sheet

| Format | Bits | Best For | Tool |
|--------|------|----------|------|
| GGUF | 1.5-8 | Universal, edge | llama.cpp, WebUI |
| GPTQ | 4 | Consumer GPUs | AutoGPTQ, vLLM |
| AWQ | 4 | Inference speed | AutoAWQ, vLLM |
| EXL2 | 2-8 | RTX GPUs | ExLlamaV2 |
| FP8 | 8 | Hopper/Blackwell | TensorRT-LLM |
| INT8/INT4 | 4-8 | CPU/edge | OpenVINO, LMDeploy |
| MXFP4 | 4 | Latest NVIDIA | TensorRT-LLM |

---

## Deployment Complexity Ranking

| Tool | Setup Difficulty | Hardware | Maintenance |
|------|-----------------|----------|-------------|
| Jan | ⭐☆☆☆☆ | Any | Minimal |
| Text Gen WebUI | ⭐⭐☆☆☆ | Any | Low |
| llama.cpp | ⭐⭐☆☆☆ | Any | Low |
| ExLlamaV2 | ⭐⭐⭐☆☆ | NVIDIA | Low |
| MLX | ⭐⭐☆☆☆ | Apple | Minimal |
| vLLM | ⭐⭐⭐☆☆ | NVIDIA/AMD | Medium |
| SGLang | ⭐⭐⭐⭐☆ | NVIDIA/TPU | Medium |
| LMDeploy | ⭐⭐⭐☆☆ | NVIDIA/Ascend | Medium |
| TensorRT-LLM | ⭐⭐⭐⭐☆ | NVIDIA | High |
| OpenVINO | ⭐⭐⭐☆☆ | Intel/Any | Medium |

---

## Free Model Hosting Options

These tools enable free self-hosted models:
- **vLLM** + ngrok/cloudflare tunnel
- **llama.cpp** server on any VPS
- **Text Generation WebUI** with --public-api
- **Jan** with cloud sync
- **RunPod/RunDiffusion** templates available for most tools

---

## Notes

- **Text Generation Inference (TGI)** by HuggingFace is in maintenance mode; use vLLM or SGLang instead
- **AutoAWQ** is deprecated; use vLLM's llm-compressor or mlx-lm
- All tools support OpenAI-compatible API for easy integration
- Consider model quantization for edge deployment (GGUF recommended for universal compatibility)

---

*Last updated: 2026-02-15*
