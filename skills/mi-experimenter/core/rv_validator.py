"""
R_V Causal Validator - Direct import fix.
Exposes RVCausalValidator at package level.
"""

# Re-export from experiments module for easier access
try:
    from ..experiments.rv_causal_validator import RVCausalValidator
    __all__ = ["RVCausalValidator"]
except ImportError:
    # Fallback for direct imports
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from experiments.rv_causal_validator import RVCausalValidator
    __all__ = ["RVCausalValidator"]
