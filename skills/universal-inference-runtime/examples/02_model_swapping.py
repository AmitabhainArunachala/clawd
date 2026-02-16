#!/usr/bin/env python3
"""Model swapping example."""

import sys
sys.path.insert(0, '..')

from universal_inference import UnifiedInference

print("=" * 60)
print("MODEL SWAPPING EXAMPLE")
print("=" * 60)

ui = UnifiedInference()

# Test 1: gemma3:4b
print("\n[Test 1] gemma3:4b")
ui.load("gemma3:4b")
r1 = ui.generate("2+2=?")
print(f"  Q: 2+2=?")
print(f"  A: {r1.strip()}")

# Test 2: Swap to mistral
print("\n[Test 2] Swapping to mistral:latest...")
ui.swap_model("mistral:latest")
r2 = ui.generate("Capital of Japan? One word.")
print(f"  Q: Capital of Japan?")
print(f"  A: {r2.strip()}")

# Test 3: Swap to llama3.1
print("\n[Test 3] Swapping to llama3.1:8b...")
ui.swap_model("llama3.1:8b")
r3 = ui.generate("What is AI? One sentence.")
print(f"  Q: What is AI?")
print(f"  A: {r3.strip()[:50]}...")

print("\n" + "=" * 60)
print("All swaps completed successfully!")
print("=" * 60)
