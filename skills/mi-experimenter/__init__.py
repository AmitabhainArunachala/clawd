"""MI-Experimenter: Mechanistic Interpretability Experimental Framework
====================================================================

Experimental toolkit for running mechanistic interpretability experiments
with integrated R_V measurement, automated logging, and publication-ready analysis.

This is the main entry point for the skill.

Currently implemented:
- Core: ModelLoader, HookManager, ActivationCache
- Experiments: RVCausalValidator, CrossArchitectureSuite
- Integration: R_V computation via rv_toolkit

Example:
    >>> from mi_experimenter import RVCausalValidator
    >>> validator = RVCausalValidator(
    ...     model_name="mistralai/Mistral-7B-v0.1",
    ...     target_layer=27,
    ...     controls=["random", "shuffled", "wrong_layer", "orthogonal"],
    ...     n_pairs=45
    ... )
    >>> results = validator.run()
    >>> print(f"Cohen's d: {results['cohens_d']:.3f}")
"""

__version__ = "0.1.0"
__author__ = "AIKAGRYA Research Team"

# Handle imports with fallback for editable install issues
import sys
from pathlib import Path

# Add self to path if needed (for editable install issues)
_skill_root = Path(__file__).parent
if str(_skill_root) not in sys.path:
    sys.path.insert(0, str(_skill_root))

# Core imports
try:
    from core.model_loader import ModelLoader, load_model
    from core.hook_manager import HookManager, ActivationCache
except ImportError:
    from .core.model_loader import ModelLoader, load_model
    from .core.hook_manager import HookManager, ActivationCache

# Experiment classes
try:
    from experiments.rv_causal_validator import RVCausalValidator
    from experiments.cross_arch_suite import CrossArchitectureSuite
    from experiments.mlp_ablator import MLPAblator
except ImportError:
    from .experiments.rv_causal_validator import RVCausalValidator
    from .experiments.cross_arch_suite import CrossArchitectureSuite
    from .experiments.mlp_ablator import MLPAblator

# R_V Integration (from rv_toolkit)
try:
    from rv_toolkit.metrics import compute_participation_ratio as compute_pr, compute_rv as measure_rv
    from rv_toolkit.patching import ActivationPatcher
    from rv_toolkit import compute_rv, get_prompt_pairs
    RV_AVAILABLE = True
except ImportError as e:
    RV_AVAILABLE = False
    import warnings
    warnings.warn(f"rv_toolkit not available: {e}. Install from ~/mech-interp-latent-lab-phase1/rv_toolkit")

__all__ = [
    # Core
    "ModelLoader",
    "load_model", 
    "HookManager",
    "ActivationCache",
    # Experiments
    "RVCausalValidator",
    "CrossArchitectureSuite",
    "MLPAblator",
]

# Add R_V exports if available
if RV_AVAILABLE:
    __all__.extend(["compute_pr", "measure_rv", "compute_rv", "ActivationPatcher", "get_prompt_pairs"])
