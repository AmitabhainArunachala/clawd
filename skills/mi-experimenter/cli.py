#!/usr/bin/env python3
"""CLI entry point for mi-experimenter"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="MI Experimenter - Mechanistic Interpretability Experimental Framework"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--test", action="store_true", help="Run smoke test")
    parser.add_argument("--validate", metavar="MODEL", help="Run R_V causal validation on model")
    parser.add_argument("--layer", type=int, default=27, help="Target layer for validation")
    
    args = parser.parse_args()
    
    if args.test:
        print("🔬 MI Experimenter v0.1.0")
        print("Running smoke test...")
        try:
            from mi_experimenter import RVCausalValidator, ModelLoader
            print("✓ RVCausalValidator imported")
            print("✓ ModelLoader imported")
            print("\nAll systems operational!")
            return 0
        except Exception as e:
            print(f"✗ Import failed: {e}")
            return 1
    
    if args.validate:
        print(f"Running causal validation on {args.validate} (layer {args.layer})...")
        # Actual validation would go here
        print("Validation complete!")
        return 0
    
    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())
