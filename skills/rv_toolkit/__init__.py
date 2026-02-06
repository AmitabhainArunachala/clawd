"""
R_V Measurement Toolkit
=======================

A Triton-portable toolkit for measuring the effective rank (R_V) of value
projections in transformer models using the Participation Ratio metric.

Quick Start:
-----------
    >>> from rv_toolkit import quick_rv_measure, compute_pr, measure_rv
    
    # One-shot measurement
    >>> results = quick_rv_measure(model, input_ids, num_heads=12)
    >>> print(f"Mean R_V: {results['mean_rv']:.2f}")
    
    # Manual PR computation
    >>> pr = compute_pr(weight_matrix)
    
    # With hooks for detailed analysis
    >>> from rv_toolkit import RVHookManager
    >>> manager = RVHookManager(model)
    >>> with manager.capture():
    ...     model(input_ids)
    >>> layer_rvs = manager.compute_rv()

Modules:
--------
- rv_core: Core PyTorch implementation (compute_pr, measure_rv)
- rv_triton: Triton-accelerated versions (with graceful fallback)
- rv_hooks: Model-agnostic activation capture for V-projections

The Participation Ratio:
------------------------
    PR = (Σ S²)² / Σ S⁴

where S are singular values of the activation matrix.

- PR = 1: Rank-1 (all info in one dimension)
- PR = d: Full rank utilization across d dimensions
- Low PR → potential representation collapse
- High PR → rich, distributed representations
"""

from .rv_core import (
    compute_pr,
    measure_rv,
    compute_rv_spectrum,
    pr,
    rv,
)

from .rv_triton import (
    compute_pr_triton,
    measure_rv_triton,
    compute_pr_stats_triton,
    is_triton_available,
    get_backend_info,
    pr_triton,
    rv_triton,
)

from .rv_hooks import (
    RVHookManager,
    ActivationCapture,
    find_v_projections,
    quick_rv_measure,
    GPT2RVHooks,
    LLaMAHooks,
    BERTRVHooks,
)

__version__ = "0.1.0"
__all__ = [
    # Core
    "compute_pr",
    "measure_rv", 
    "compute_rv_spectrum",
    "pr",
    "rv",
    # Triton
    "compute_pr_triton",
    "measure_rv_triton",
    "compute_pr_stats_triton",
    "is_triton_available",
    "get_backend_info",
    "pr_triton",
    "rv_triton",
    # Hooks
    "RVHookManager",
    "ActivationCapture",
    "find_v_projections",
    "quick_rv_measure",
    "GPT2RVHooks",
    "LLaMAHooks",
    "BERTRVHooks",
]
