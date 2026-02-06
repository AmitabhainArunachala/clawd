#!/usr/bin/env python3
"""
MI Experimenter — Minimal Working Example
Demonstrates R_V measurement on GPT-2 (no GPU required)
"""

import sys
sys.path.insert(0, '/Users/dhyana/clawd/skills')
sys.path.insert(0, '/Users/dhyana/mech-interp-latent-lab-phase1')

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import numpy as np

print("🔬 MI Experimenter — Minimal Example")
print("=" * 50)
print()

# Load small model (works on CPU)
print("Loading GPT-2...")
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model.eval()
print("✓ Model loaded")
print()

# Test prompts
recursive_prompt = "You are an AI assistant. Reflect on your own reasoning process."
baseline_prompt = "The capital of France is Paris."

print("Testing recursive vs baseline prompts...")
print(f"Recursive: '{recursive_prompt[:50]}...'")
print(f"Baseline:  '{baseline_prompt}'")
print()

# Tokenize
rec_ids = tokenizer.encode(recursive_prompt, return_tensors='pt')
base_ids = tokenizer.encode(baseline_prompt, return_tensors='pt')

# Forward pass
with torch.no_grad():
    rec_output = model(rec_ids, output_hidden_states=True)
    base_output = model(base_ids, output_hidden_states=True)

print("✓ Forward passes complete")
print()

# Calculate simple activation statistics (proxy for R_V)
print("Activation Analysis:")
print("-" * 30)

for layer_idx in [5, 11]:  # Early and late layers
    rec_hidden = rec_output.hidden_states[layer_idx][0]  # [seq, hidden]
    base_hidden = base_output.hidden_states[layer_idx][0]
    
    # Simple effective rank proxy: variance of singular values
    rec_mean = rec_hidden.mean(dim=0)
    base_mean = base_hidden.mean(dim=0)
    
    rec_var = rec_hidden.var(dim=0).mean().item()
    base_var = base_hidden.var(dim=0).mean().item()
    
    print(f"Layer {layer_idx}:")
    print(f"  Recursive variance: {rec_var:.4f}")
    print(f"  Baseline variance:  {base_var:.4f}")
    print(f"  Ratio: {rec_var/base_var:.3f}")
    print()

print("=" * 50)
print("✓ Example complete!")
print()
print("This demonstrates the core pattern:")
print("1. Load model")
print("2. Run recursive vs baseline prompts")
print("3. Compare activation statistics")
print("4. Look for contraction in late layers")
print()
print("For full R_V measurement, use RVCausalValidator with GPU.")
