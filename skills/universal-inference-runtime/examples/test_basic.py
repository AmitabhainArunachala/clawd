#!/usr/bin/env python3
"""Quick test script for Universal Inference Runtime."""

import sys
sys.path.insert(0, '..')

def test():
    """Run basic tests."""
    print("Testing Universal Inference Runtime...")
    
    # Import
    try:
        from universal_inference import UnifiedInference
        print("✓ Import successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Initialize
    try:
        ui = UnifiedInference()
        print(f"✓ Initialized (backend: {ui.backend.name})")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False
    
    # List models
    try:
        models = ui.list_models()
        print(f"✓ Listed {len(models)} models")
    except Exception as e:
        print(f"✗ List models failed: {e}")
        return False
    
    # Load model
    try:
        ui.load("gemma3:4b")
        print("✓ Loaded gemma3:4b")
    except Exception as e:
        print(f"✗ Load model failed: {e}")
        return False
    
    # Generate
    try:
        response = ui.generate("Hi")
        print(f"✓ Generated response ({len(response)} chars)")
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        return False
    
    # Swap
    try:
        ui.swap_model("mistral:latest")
        print("✓ Swapped to mistral:latest")
    except Exception as e:
        print(f"✗ Swap failed: {e}")
        return False
    
    print("\n✅ ALL TESTS PASSED")
    return True

if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)
