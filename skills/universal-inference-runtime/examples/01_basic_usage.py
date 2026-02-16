#!/usr/bin/env python3
"""Basic usage example for Universal Inference Runtime."""

import sys
sys.path.insert(0, '..')

from universal_inference import UnifiedInference

print("=" * 60)
print("BASIC USAGE EXAMPLE")
print("=" * 60)

# Initialize (auto-detects best backend)
print("\n1. Initializing runtime...")
ui = UnifiedInference()
print(f"   Backend: {ui.backend.name if ui.backend else 'None'}")
print(f"   Hardware: {ui.info()['hardware']['recommendation']}")

# List available models
print("\n2. Available models:")
models = ui.list_models()
for m in models[:5]:
    print(f"   - {m}")
print(f"   ... and {len(models) - 5} more")

# Load and generate
print("\n3. Loading gemma3:4b...")
ui.load("gemma3:4b")

print("\n4. Generating response...")
response = ui.generate("What is the capital of France? One word.")
print(f"   Response: {response.strip()}")

print("\n" + "=" * 60)
print("SUCCESS! Universal Inference Runtime is working.")
print("=" * 60)
