#!/usr/bin/env python3
"""Ollama Bridge - Unified interface to local Ollama API."""

import urllib.request
import json
from typing import List, Dict, Any, Generator


class OllamaBridge:
    """Bridge to Ollama's local API. Works with any Ollama-installed model."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.models = self._list_models()
    
    def _list_models(self) -> List[str]:
        """List available Ollama models."""
        req = urllib.request.Request(f"{self.base_url}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return [m["name"] for m in data["models"]]
    
    def generate(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text with specified model."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    
    def generate_stream(self, model: str, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Stream generation tokens."""
        payload = {
            "model": model,
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
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get model information."""
        req = urllib.request.Request(f"{self.base_url}/api/show", 
                                      data=json.dumps({"model": model}).encode(),
                                      headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())


if __name__ == "__main__":
    # Test the bridge
    print("=== OLLAMA BRIDGE TEST ===")
    bridge = OllamaBridge()
    print(f"Available models: {len(bridge.models)}")
    for m in bridge.models[:5]:
        print(f"  - {m}")
    print("  ...")
    
    print()
    print("Testing inference on gemma3:4b...")
    result = bridge.generate("gemma3:4b", "What is 2+2? Answer in one word.")
    print(f"Response: {result['response'].strip()}")
    print(f"Tokens evaluated: {result['eval_count']}")
    print(f"Eval duration: {result['eval_duration']/1e9:.2f}s")
    print()
    print("=== SUCCESS ===")
