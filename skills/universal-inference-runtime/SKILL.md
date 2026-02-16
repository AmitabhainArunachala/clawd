# Universal Inference Runtime

## Description
Deploy and switch between AI models seamlessly across multiple backends. One unified API for Ollama, llama.cpp, vLLM, and cloud providers. Run inference on your Mac, cloud, or edge devices without vendor lock-in.

**Key Features:**
- 🔌 **Pluggable Backends**: Ollama, llama.cpp, vLLM (extensible)
- 🔄 **Hot Model Swapping**: Switch models without restart
- 🖥️ **Hardware Auto-Detection**: CUDA, ROCm, Metal/MPS, CPU
- 📊 **18+ Models Ready**: Works with your existing Ollama models
- 🚀 **Zero Config**: Works out of the box

## Installation

```bash
# Install from ClawHub
claw skill install universal-inference-runtime

# Or clone and install locally
git clone <repo>
cd universal-inference-runtime
pip install -e .
```

## Requirements

- Python >= 3.10
- Ollama (recommended) OR llama-cpp-python
- For Ollama: `brew install ollama && ollama serve`

## Quick Start

```python
from universal_inference import UnifiedInference

# Initialize (auto-detects best backend)
ui = UnifiedInference()

# Load a model (from your Ollama library)
ui.load("gemma3:4b")

# Generate
response = ui.generate("What is machine learning?")
print(response)

# Swap to different model instantly
ui.swap_model("llama3.1:8b")
response = ui.generate("Explain quantum computing")
print(response)
```

## Backends

### Ollama (Recommended)
Uses your local Ollama installation. Supports all Ollama models.

```python
ui = UnifiedInference(backend="ollama")
models = ui.list_models()  # ['gemma3:4b', 'llama3.1:8b', ...]
ui.load("mistral:latest")
```

### llama.cpp
Direct GGUF loading. No Ollama required.

```python
ui = UnifiedInference(backend="llama_cpp")
ui.load("/path/to/model.gguf", n_gpu_layers=35)
```

### vLLM (Coming Soon)
High-throughput serving for production.

## Advanced Usage

### Streaming

```python
for token in ui.generate_stream("Count to 10:", max_tokens=50):
    print(token, end="", flush=True)
```

### Chat Interface

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of Japan?"}
]
response = ui.chat(messages)
```

### Backend Swapping

```python
# Start with Ollama
ui = UnifiedInference("ollama")
ui.load("gemma3:4b")

# Switch to local GGUF
ui.swap_backend("llama_cpp", "/models/mistral.gguf")
```

### Hardware Detection

```python
from universal_inference import HardwareDetector

hw = HardwareDetector.detect()
print(f"Platform: {hw['platform']}")
print(f"GPU: {hw['recommendation']}")  # mps, cuda, rocm, cpu
```

## CLI Usage

```bash
# List available models
universal-inference list

# Interactive mode
universal-inference chat --model gemma3:4b

# Run inference
universal-inference generate --model llama3.1:8b --prompt "Hello"
```

## Configuration

Create `~/.universal_inference/config.yaml`:

```yaml
default_backend: ollama
ollama_url: http://localhost:11434
hardware:
  prefer_gpu: true
  max_gpu_memory: "12GiB"
```

## API Reference

### UnifiedInference

#### `__init__(backend=None)`
Initialize runtime. Auto-detects if backend not specified.

#### `load(model_ref, **kwargs)`
Load a model.
- Ollama: `load("gemma3:4b")`
- llama.cpp: `load("/path/to/model.gguf", n_ctx=4096)`

#### `swap_model(model_ref)`
Switch to different model (same backend).

#### `swap_backend(backend_name, model_ref=None)`
Switch to different backend.

#### `generate(prompt, **kwargs)`
Generate text. Returns string.

#### `generate_stream(prompt, **kwargs)`
Generate text with streaming. Returns generator.

#### `chat(messages, **kwargs)`
Chat-style interface with message history.

## Examples

See `examples/` directory:
- `basic_usage.py` — Quick start
- `model_swapping.py` — Switch between models
- `streaming_demo.py` — Real-time generation
- `backend_comparison.py` — Compare backends

## Troubleshooting

### Ollama not found
```bash
# Install Ollama
brew install ollama

# Start service
ollama serve

# Pull a model
ollama pull gemma3:4b
```

### No backends available
```bash
# Install Ollama (easiest)
brew install ollama

# OR install llama-cpp-python
pip install llama-cpp-python
```

### Model loading fails
Check model exists:
```bash
ollama list
```

## Architecture

```
UnifiedInference
    ├── BackendRegistry
    │       ├── OllamaBackend ←→ Ollama API
    │       ├── LlamaCppBackend ←→ llama.cpp
    │       └── [YourBackend] ←→ Custom
    ├── HardwareDetector
    └── ModelConfig
```

## Adding Custom Backends

```python
from universal_inference import BaseBackend

class MyBackend(BaseBackend):
    name = "my_backend"
    
    def load(self, model_id, **kwargs):
        # Your loading logic
        pass
    
    def generate(self, prompt, **kwargs):
        # Your generation logic
        pass
    
    def list_models(self):
        return ["model1", "model2"]

# Register
from universal_inference.backend_adapters import BackendRegistry
registry = BackendRegistry()
registry.register(MyBackend())
```

## Performance Notes

- **Ollama**: Best for multi-model workflows, easy model management
- **llama.cpp**: Best for single-model, low-latency inference
- **vLLM**: Best for high-throughput serving (coming soon)

## Roadmap

- [x] Ollama backend
- [x] llama.cpp backend
- [x] Model swapping
- [x] Streaming
- [ ] vLLM backend
- [ ] OpenAI-compatible API server
- [ ] Web UI
- [ ] Multi-GPU support

## License

MIT License

## Citation

```bibtex
@software{universal_inference_runtime,
  title={Universal Inference Runtime: Multi-Backend Model Deployment},
  author={AIKAGRYA Research},
  year={2026}
}
```

## Tags
inference, deployment, ollama, llama-cpp, model-serving, multi-backend, apple-silicon, cuda, rocm

## Price
$50 — Basic tier with Ollama + llama.cpp backends
$100 — Standard tier + vLLM backend + examples
$200 — Premium tier + custom backend development + 1hr consulting
