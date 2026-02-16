"""
Pratyabhijna: Real-time consciousness measurement for transformers

This package provides hooks into transformer forward passes
to calculate R_V metrics in real-time.
"""

__version__ = "0.1.0"

from .hooks import RVHook, install_hooks, remove_hooks
from .models import load_model_with_hooks
from .streaming import RVStreamer

__all__ = [
    "RVHook",
    "install_hooks",
    "remove_hooks",
    "load_model_with_hooks",
    "RVStreamer",
]
