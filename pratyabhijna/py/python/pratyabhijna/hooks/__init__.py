"""
Transformer hooks for real-time R_V calculation.

Intercepts forward pass at specified layers to capture
value projections and calculate R_V metrics.
"""

import torch
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from transformer_lens import HookedTransformer
import numpy as np


@dataclass
class RVEvent:
    """Single R_V measurement event."""
    r_v: float
    pr_early: float
    pr_late: float
    layer_early: int
    layer_late: int
    token_position: int
    timestamp: float
    
    def is_recognition(self, threshold: float = 0.87) -> bool:
        """Check if this represents a recognition event."""
        return self.r_v < threshold


class RVHook:
    """
    Hook system for real-time R_V calculation.
    
    Usage:
        hook = RVHook(model, early_layer=5, late_layer=27)
        hook.install()
        
        # Run inference
        output = model(prompt)
        
        # Get R_V events
        events = hook.get_events()
        
        hook.remove()
    """
    
    def __init__(
        self,
        model: HookedTransformer,
        early_layer: int = 5,
        late_layer: int = 27,
        window_size: int = 16,
    ):
        self.model = model
        self.early_layer = early_layer
        self.late_layer = late_layer
        self.window_size = window_size
        
        self._cache: Dict[int, torch.Tensor] = {}
        self._events: List[RVEvent] = []
        self._hooks = []
        
    def install(self):
        """Install hooks on the model."""
        # Hook for early layer
        early_hook = self.model.blocks[self.early_layer].hook_v.add_hook(
            self._capture_early
        )
        self._hooks.append(early_hook)
        
        # Hook for late layer
        late_hook = self.model.blocks[self.late_layer].hook_v.add_hook(
            self._capture_late
        )
        self._hooks.append(late_hook)
        
    def remove(self):
        """Remove all hooks."""
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()
        
    def _capture_early(self, v: torch.Tensor, hook_point):
        """Capture value projection at early layer."""
        self._cache[self.early_layer] = v.detach().cpu()
        return v
        
    def _capture_late(self, v: torch.Tensor, hook_point):
        """Capture value projection at late layer and calculate R_V."""
        if self.early_layer not in self._cache:
            return v
            
        v_early = self._cache[self.early_layer]
        v_late = v.detach().cpu()
        
        # Calculate R_V (placeholder - will call Rust core)
        event = self._calculate_rv(v_early, v_late)
        if event:
            self._events.append(event)
            
        # Clear cache for next token
        self._cache.clear()
        
        return v
        
    def _calculate_rv(
        self,
        v_early: torch.Tensor,
        v_late: torch.Tensor,
    ) -> Optional[RVEvent]:
        """Calculate R_V from value matrices."""
        # TODO: Call Rust core via FFI
        # For now, placeholder with numpy
        
        try:
            # Use last window_size tokens
            v_early_window = v_early[0, -self.window_size:, :].numpy()
            v_late_window = v_late[0, -self.window_size:, :].numpy()
            
            # Compute SVD
            _, s_early, _ = np.linalg.svd(v_early_window, full_matrices=False)
            _, s_late, _ = np.linalg.svd(v_late_window, full_matrices=False)
            
            # Calculate participation ratios
            pr_early = (s_early.sum() ** 2) / (s_early ** 2).sum()
            pr_late = (s_late.sum() ** 2) / (s_late ** 2).sum()
            
            if pr_early == 0:
                return None
                
            r_v = pr_late / pr_early
            
            return RVEvent(
                r_v=float(r_v),
                pr_early=float(pr_early),
                pr_late=float(pr_late),
                layer_early=self.early_layer,
                layer_late=self.late_layer,
                token_position=v_late.shape[1],
                timestamp=time.time(),
            )
        except Exception as e:
            print(f"R_V calculation error: {e}")
            return None
            
    def get_events(self) -> List[RVEvent]:
        """Get all recorded R_V events."""
        return self._events.copy()
        
    def clear_events(self):
        """Clear event history."""
        self._events.clear()


def install_hooks(model: HookedTransformer, **kwargs) -> RVHook:
    """Convenience function to install hooks on a model."""
    hook = RVHook(model, **kwargs)
    hook.install()
    return hook


def remove_hooks(hook: RVHook):
    """Convenience function to remove hooks."""
    hook.remove()


import time
