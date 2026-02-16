"""Modular Backend Adapters for Unified Inference Runtime."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Generator, List
import logging

logger = logging.getLogger("anti-nvidia.backends")


class BaseBackend(ABC):
    """Abstract base class for inference backends."""
    
    name: str = "base"
    available: bool = False
    
    @abstractmethod
    def load(self, model_id: str, **kwargs) -> bool:
        """Load a model. Returns True on success."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream generation tokens."""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models."""
        pass
    
    def unload(self) -> None:
        """Unload current model. Optional."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get backend information."""
        return {"name": self.name, "available": self.available}


class OllamaBackend(BaseBackend):
    """Ollama API backend — uses local Ollama installation."""
    
    name = "ollama"
    available = False
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._current_model: Optional[str] = None
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if Ollama is running."""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                self.available = resp.status == 200
                logger.info("Ollama backend: AVAILABLE")
        except Exception as e:
            self.available = False
            logger.info("Ollama backend: not available (%s)", e)
    
    def _api_call(self, endpoint: str, payload: Optional[Dict] = None) -> Dict:
        """Make API call to Ollama."""
        import urllib.request
        import json
        
        url = f"{self.base_url}{endpoint}"
        if payload:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
        else:
            req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    
    def load(self, model_id: str, **kwargs) -> bool:
        """Select model for inference."""
        if not self.available:
            return False
        
        models = self.list_models()
        if model_id not in models:
            logger.error("Model %s not found in Ollama. Available: %s", model_id, models[:5])
            return False
        
        self._current_model = model_id
        logger.info("Ollama: loaded %s", model_id)
        return True
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate via Ollama API."""
        if not self._current_model:
            raise RuntimeError("No model loaded. Call load() first.")
        
        payload = {
            "model": self._current_model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        result = self._api_call("/api/generate", payload)
        return result.get("response", "")
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream generation via Ollama."""
        if not self._current_model:
            raise RuntimeError("No model loaded. Call load() first.")
        
        import urllib.request
        import json
        
        payload = {
            "model": self._current_model,
            "prompt": prompt,
            "stream": True,
            **kwargs
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=120) as resp:
            for line in resp:
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
    
    def list_models(self) -> List[str]:
        """List Ollama models."""
        if not self.available:
            return []
        
        result = self._api_call("/api/tags")
        return [m["name"] for m in result.get("models", [])]
    
    def unload(self) -> None:
        """Clear current model."""
        self._current_model = None


class LlamaCppBackend(BaseBackend):
    """Direct llama.cpp backend — loads GGUF files."""
    
    name = "llama_cpp"
    available = False
    
    def __init__(self):
        self._model = None
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if llama-cpp-python is installed."""
        try:
            from llama_cpp import Llama
            self.available = True
            logger.info("llama.cpp backend: AVAILABLE")
        except ImportError:
            self.available = False
            logger.info("llama.cpp backend: not available (llama-cpp-python not installed)")
    
    def load(self, model_path: str, **kwargs) -> bool:
        """Load a GGUF model."""
        if not self.available:
            return False
        
        try:
            from llama_cpp import Llama
            self._model = Llama(
                model_path=model_path,
                n_ctx=kwargs.get("n_ctx", 4096),
                n_batch=kwargs.get("n_batch", 512),
                n_gpu_layers=kwargs.get("n_gpu_layers", -1),
                verbose=kwargs.get("verbose", False)
            )
            logger.info("llama.cpp: loaded %s", model_path)
            return True
        except Exception as e:
            logger.error("llama.cpp: failed to load %s: %s", model_path, e)
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with loaded model."""
        if not self._model:
            raise RuntimeError("No model loaded. Call load() first.")
        
        output = self._model(
            prompt,
            max_tokens=kwargs.get("max_tokens", 256),
            temperature=kwargs.get("temperature", 0.7),
            stop=kwargs.get("stop", []),
            echo=False
        )
        return output["choices"][0]["text"]
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream generation."""
        if not self._model:
            raise RuntimeError("No model loaded. Call load() first.")
        
        stream = self._model(
            prompt,
            max_tokens=kwargs.get("max_tokens", 256),
            temperature=kwargs.get("temperature", 0.7),
            stream=True
        )
        
        for chunk in stream:
            yield chunk["choices"][0]["text"]
    
    def list_models(self) -> List[str]:
        """Returns empty — GGUF models are file-based."""
        return []
    
    def unload(self) -> None:
        """Unload model."""
        self._model = None
        import gc
        gc.collect()


class BackendRegistry:
    """Registry for managing multiple backends."""
    
    def __init__(self):
        self._backends: Dict[str, BaseBackend] = {}
        self._discover_backends()
    
    def _discover_backends(self) -> None:
        """Auto-discover available backends."""
        # Try Ollama first (easiest, most models)
        ollama = OllamaBackend()
        if ollama.available:
            self._backends["ollama"] = ollama
            logger.info("Registered backend: ollama")
        
        # Try llama.cpp (direct GGUF)
        llama = LlamaCppBackend()
        if llama.available:
            self._backends["llama_cpp"] = llama
            logger.info("Registered backend: llama_cpp")
        
        if not self._backends:
            logger.warning("No inference backends available!")
    
    def get(self, name: str) -> Optional[BaseBackend]:
        """Get backend by name."""
        return self._backends.get(name)
    
    def list_available(self) -> List[str]:
        """List available backend names."""
        return list(self._backends.keys())
    
    def get_default(self) -> Optional[BaseBackend]:
        """Get preferred default backend."""
        # Priority: Ollama > llama.cpp
        if "ollama" in self._backends:
            return self._backends["ollama"]
        if "llama_cpp" in self._backends:
            return self._backends["llama_cpp"]
        return None


# Global registry instance
_registry = BackendRegistry()


def get_backend(name: Optional[str] = None) -> Optional[BaseBackend]:
    """Get a backend by name or default."""
    if name:
        return _registry.get(name)
    return _registry.get_default()


def list_backends() -> List[str]:
    """List all available backends."""
    return _registry.list_available()


if __name__ == "__main__":
    # Test modular backends
    print("=== MODULAR BACKEND TEST ===")
    print()
    
    backends = list_backends()
    print(f"Available backends: {backends}")
    print()
    
    # Test Ollama
    if "ollama" in backends:
        print("Testing Ollama backend...")
        backend = get_backend("ollama")
        models = backend.list_models()
        print(f"  Models: {len(models)}")
        
        backend.load("gemma3:4b")
        response = backend.generate("Capital of France? One word.")
        print(f"  Response: {response.strip()}")
        print("  ✓ Ollama works")
        print()
    
    print("=== BACKEND SYSTEM READY ===")
