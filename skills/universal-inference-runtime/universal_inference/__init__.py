"""Modular Unified Inference — Swappable Backends."""

import sys
sys.path.insert(0, '/Users/dhyana/anti-nvidia-swarm/00-core')

from runtime.backend_adapters import get_backend, list_backends, BaseBackend
from runtime.unified_inference import HardwareDetector, ModelConfig
from typing import Optional, Dict, Any, Generator, List
import logging

logger = logging.getLogger("anti-nvidia.unified")


class ModularUnifiedInference:
    """
    Unified inference with pluggable backends.
    
    Usage:
        # Auto-detect best backend
        ui = ModularUnifiedInference()
        ui.load("gemma3:4b")  # Uses Ollama
        
        # Or specify backend
        ui = ModularUnifiedInference(backend="ollama")
        ui.load("llama3.1:8b")
        
        # Generate
        response = ui.generate("Hello!")
        
        # Swap models easily
        ui.load("mistral:latest")  # Same backend, different model
        
        # Or swap backends
        ui = ModularUnifiedInference(backend="llama_cpp")
        ui.load("/path/to/model.gguf")
    """
    
    def __init__(self, backend: Optional[str] = None):
        self.hardware = HardwareDetector.detect()
        self.backend: Optional[BaseBackend] = None
        self.config: Optional[ModelConfig] = None
        self._loaded_model: Optional[str] = None
        
        # Initialize backend
        available = list_backends()
        if backend:
            if backend not in available:
                raise ValueError(f"Backend '{backend}' not available. Options: {available}")
            self.backend = get_backend(backend)
        else:
            self.backend = get_backend()  # Get default
        
        if self.backend:
            logger.info("UnifiedInference: using %s backend", self.backend.name)
        else:
            logger.error("UnifiedInference: no backend available!")
    
    def list_models(self) -> List[str]:
        """List available models for current backend."""
        if not self.backend:
            return []
        return self.backend.list_models()
    
    def load(self, model_ref: str, **kwargs) -> bool:
        """
        Load a model.
        
        For Ollama: model_ref is model name (e.g., "gemma3:4b")
        For llama.cpp: model_ref is path to GGUF file
        """
        if not self.backend:
            raise RuntimeError("No backend available!")
        
        success = self.backend.load(model_ref, **kwargs)
        if success:
            self._loaded_model = model_ref
            logger.info("Loaded: %s via %s", model_ref, self.backend.name)
        return success
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if not self.backend:
            raise RuntimeError("No backend available!")
        if not self._loaded_model:
            raise RuntimeError("No model loaded. Call load() first.")
        
        return self.backend.generate(prompt, **kwargs)
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream generation tokens."""
        if not self.backend:
            raise RuntimeError("No backend available!")
        if not self._loaded_model:
            raise RuntimeError("No model loaded. Call load() first.")
        
        yield from self.backend.generate_stream(prompt, **kwargs)
    
    def unload(self) -> None:
        """Unload current model."""
        if self.backend:
            self.backend.unload()
            self._loaded_model = None
    
    def swap_model(self, model_ref: str, **kwargs) -> bool:
        """Convenience: unload current, load new."""
        self.unload()
        return self.load(model_ref, **kwargs)
    
    def swap_backend(self, backend_name: str, model_ref: Optional[str] = None) -> bool:
        """
        Swap to different backend and optionally load a model.
        
        Example:
            ui.swap_backend("ollama", "gemma3:4b")
            ui.swap_backend("llama_cpp", "/path/to/local.gguf")
        """
        self.unload()
        
        new_backend = get_backend(backend_name)
        if not new_backend:
            logger.error("Backend %s not available", backend_name)
            return False
        
        self.backend = new_backend
        logger.info("Swapped to %s backend", backend_name)
        
        if model_ref:
            return self.load(model_ref)
        return True
    
    def info(self) -> Dict[str, Any]:
        """Get runtime information."""
        return {
            "hardware": self.hardware,
            "backend": self.backend.name if self.backend else None,
            "loaded_model": self._loaded_model,
            "available_backends": list_backends()
        }
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat-style interface with message history.
        
        messages: [{"role": "user", "content": "..."}, ...]
        """
        # Simple conversion — backends handle formatting
        prompt = self._format_chat(messages)
        return self.generate(prompt, **kwargs)
    
    def _format_chat(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages to prompt string."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                formatted.append(f"<|system|>\n{content}</s>")
            elif role == "user":
                formatted.append(f"<|user|>\n{content}</s>")
            elif role == "assistant":
                formatted.append(f"<|assistant|>\n{content}</s>")
        formatted.append("<|assistant|>\n")
        return "\n".join(formatted)


# Aliases for convenience
UnifiedInference = ModularUnifiedInference


if __name__ == "__main__":
    print("=== MODULAR UNIFIED INFERENCE TEST ===")
    print()
    
    # Test 1: Auto-detect backend
    print("Test 1: Auto-detect backend")
    ui = ModularUnifiedInference()
    info = ui.info()
    print(f"  Hardware: {info['hardware']['platform']} ({info['hardware']['arch']})")
    print(f"  Backend: {info['backend']}")
    print(f"  Available: {info['available_backends']}")
    print()
    
    # Test 2: Load and generate
    print("Test 2: Load gemma3:4b via Ollama")
    ui.load("gemma3:4b")
    response = ui.generate("What is 2+2? One word.")
    print(f"  Response: {response.strip()}")
    print()
    
    # Test 3: Swap model
    print("Test 3: Swap to llama3.1:8b")
    ui.swap_model("llama3.1:8b")
    response = ui.generate("Capital of Japan? One word.")
    print(f"  Response: {response.strip()}")
    print()
    
    # Test 4: Streaming
    print("Test 4: Streaming generation")
    ui.swap_model("gemma3:4b")
    print("  Response: ", end="", flush=True)
    for token in ui.generate_stream("Count: 1, 2, ", max_tokens=10):
        print(token, end="", flush=True)
    print()
    print()
    
    # Test 5: Chat interface
    print("Test 5: Chat interface")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]
    response = ui.chat(messages, max_tokens=30)
    print(f"  Response: {response[:60]}...")
    print()
    
    print("=== ALL TESTS PASSED ===")
    print("Modular inference system ready.")
    print("Easy model swapping: ui.swap_model('new-model')")
    print("Easy backend swapping: ui.swap_backend('backend', 'model')")
