# Universal Inference Runtime

Multi-backend inference runtime for AI models. Deploy and switch between models seamlessly across Ollama, llama.cpp, and more.

## Features

- 🔌 **Pluggable Backends**: Ollama, llama.cpp (extensible)
- 🔄 **Hot Model Swapping**: Switch models without restart  
- 🖥️ **Hardware Auto-Detection**: CUDA, ROCm, Metal/MPS, CPU
- 🚀 **Zero Config**: Works out of the box

## Quick Start

```bash
pip install -e .
```

```python
from universal_inference import UnifiedInference

ui = UnifiedInference()
ui.load("gemma3:4b")
response = ui.generate("Hello!")
print(response)
```

## Requirements

- Python >= 3.10
- Ollama (recommended): `brew install ollama && ollama serve`

## Examples

See `examples/` directory:
- `01_basic_usage.py` — Quick start
- `02_model_swapping.py` — Switch between models
- `test_basic.py` — Test suite

## Documentation

See `SKILL.md` for full documentation.

## License

MIT
