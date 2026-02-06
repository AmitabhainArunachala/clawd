"""
R_V Measurement Toolkit - Model Hooks for Activation Capture
============================================================

This module provides model-agnostic hooks for capturing V-projection activations
from transformer models. Works with HuggingFace Transformers, custom models,
and any PyTorch module that exposes V-projections.

Supported Architectures:
------------------------
- HuggingFace: GPT-2, LLaMA, Mistral, Phi, BERT, RoBERTa, T5, etc.
- Custom transformers with standard naming conventions
- Any model where you can specify the layer path manually

Usage Pattern:
--------------
1. Create a hook manager
2. Attach to model
3. Run forward pass
4. Collect R_V measurements
5. Detach hooks

Example:
    >>> from rv_hooks import RVHookManager
    >>> manager = RVHookManager(model)
    >>> manager.attach()
    >>> output = model(input_ids)
    >>> rv_results = manager.compute_rv()
    >>> manager.detach()
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager
import re

from .rv_core import compute_pr, measure_rv


@dataclass
class ActivationCapture:
    """Container for captured activations with metadata."""
    name: str
    layer_idx: int
    activations: List[torch.Tensor] = field(default_factory=list)
    
    def append(self, tensor: torch.Tensor):
        """Append activation, detaching from graph."""
        self.activations.append(tensor.detach().cpu())
    
    def get_stacked(self) -> torch.Tensor:
        """Get all activations stacked along batch dimension."""
        if not self.activations:
            raise ValueError(f"No activations captured for {self.name}")
        return torch.cat(self.activations, dim=0)
    
    def clear(self):
        """Clear stored activations."""
        self.activations.clear()


class RVHookManager:
    """
    Manager for attaching hooks to capture V-projection activations.
    
    This class automatically detects and hooks into V-projection layers
    across various transformer architectures.
    
    Args:
        model: The transformer model to hook into.
        layer_pattern: Regex pattern to match V-projection layer names.
                      If None, uses auto-detection for common architectures.
        capture_input: If True, capture layer inputs; if False, capture outputs.
        device: Device to store captured activations ('cpu' recommended for memory).
    
    Example:
        >>> manager = RVHookManager(model)
        >>> with manager.capture():
        ...     outputs = model(input_ids)
        >>> rv_per_layer = manager.compute_rv()
        >>> print(f"Mean R_V: {sum(rv_per_layer.values()) / len(rv_per_layer):.2f}")
    """
    
    # Common patterns for V-projection layers across architectures
    V_PATTERNS = [
        # HuggingFace GPT-2, GPT-Neo, GPT-J
        r".*\.attn\.c_attn$",           # GPT-2 (combined QKV)
        r".*\.attn\.v_proj$",           # Some variants
        # LLaMA, Mistral, Phi
        r".*\.self_attn\.v_proj$",
        r".*\.attention\.v_proj$",
        # BERT, RoBERTa
        r".*\.attention\.self\.value$",
        # T5
        r".*\.SelfAttention\.v$",
        r".*\.EncDecAttention\.v$",
        # Generic patterns
        r".*v_proj$",
        r".*value$",
        r".*\.v$",
    ]
    
    def __init__(
        self,
        model: nn.Module,
        layer_pattern: Optional[str] = None,
        capture_input: bool = False,
        device: str = "cpu"
    ):
        self.model = model
        self.custom_pattern = layer_pattern
        self.capture_input = capture_input
        self.device = device
        
        self._hooks: List[torch.utils.hooks.RemovableHandle] = []
        self._captures: Dict[str, ActivationCapture] = {}
        self._layer_modules: Dict[str, nn.Module] = {}
        
        # Detect architecture and find V-projection layers
        self._detect_layers()
    
    def _detect_layers(self):
        """Detect V-projection layers in the model."""
        self._layer_modules.clear()
        
        patterns = [self.custom_pattern] if self.custom_pattern else self.V_PATTERNS
        
        for name, module in self.model.named_modules():
            for pattern in patterns:
                if pattern and re.match(pattern, name):
                    # Extract layer index from name
                    layer_idx = self._extract_layer_idx(name)
                    self._layer_modules[name] = module
                    self._captures[name] = ActivationCapture(
                        name=name,
                        layer_idx=layer_idx
                    )
                    break
        
        if not self._layer_modules:
            raise ValueError(
                f"No V-projection layers found. "
                f"Searched patterns: {patterns}. "
                f"Available modules: {[n for n, _ in self.model.named_modules() if 'attn' in n.lower() or 'attention' in n.lower()][:10]}"
            )
    
    def _extract_layer_idx(self, name: str) -> int:
        """Extract layer index from module name."""
        # Look for numbers in the name (e.g., "layer.5.attention" -> 5)
        numbers = re.findall(r'\.(\d+)\.', name)
        if numbers:
            return int(numbers[0])
        return -1
    
    def _create_hook(self, name: str) -> Callable:
        """Create a hook function for the given layer."""
        capture = self._captures[name]
        
        def hook(module, input, output):
            if self.capture_input:
                # Input is a tuple
                tensor = input[0] if isinstance(input, tuple) else input
            else:
                tensor = output
            
            # Handle combined QKV projections (split to get V)
            if "c_attn" in name and not self.capture_input:
                # GPT-2 style: output is [Q, K, V] concatenated
                # V is the last third
                hidden_size = tensor.shape[-1] // 3
                tensor = tensor[..., 2 * hidden_size:]
            
            capture.append(tensor)
        
        return hook
    
    def attach(self):
        """Attach hooks to all detected V-projection layers."""
        self.detach()  # Remove any existing hooks
        
        for name, module in self._layer_modules.items():
            hook = self._create_hook(name)
            handle = module.register_forward_hook(hook)
            self._hooks.append(handle)
    
    def detach(self):
        """Remove all hooks."""
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()
    
    def clear(self):
        """Clear all captured activations."""
        for capture in self._captures.values():
            capture.clear()
    
    @contextmanager
    def capture(self, clear_before: bool = True, clear_after: bool = False):
        """
        Context manager for capturing activations.
        
        Args:
            clear_before: Clear existing captures before starting.
            clear_after: Clear captures after exiting context.
        
        Example:
            >>> with manager.capture():
            ...     model(input_ids)
            >>> rv = manager.compute_rv()
        """
        if clear_before:
            self.clear()
        
        self.attach()
        try:
            yield self
        finally:
            self.detach()
            if clear_after:
                self.clear()
    
    def get_activations(self, layer_name: Optional[str] = None) -> Dict[str, torch.Tensor]:
        """
        Get captured activations.
        
        Args:
            layer_name: Specific layer to get, or None for all layers.
        
        Returns:
            Dict mapping layer names to stacked activation tensors.
        """
        if layer_name:
            return {layer_name: self._captures[layer_name].get_stacked()}
        
        return {
            name: capture.get_stacked()
            for name, capture in self._captures.items()
            if capture.activations
        }
    
    def compute_rv(
        self,
        per_head: bool = False,
        num_heads: Optional[int] = None
    ) -> Dict[str, Union[float, Tuple[float, torch.Tensor]]]:
        """
        Compute R_V for all captured layers.
        
        Args:
            per_head: If True, compute per-head R_V (requires num_heads).
            num_heads: Number of attention heads for per-head analysis.
        
        Returns:
            Dict mapping layer names to R_V values.
            If per_head=True, values are (mean_rv, per_head_tensor) tuples.
        """
        results = {}
        
        for name, capture in self._captures.items():
            if not capture.activations:
                continue
            
            activations = capture.get_stacked()
            
            if per_head and num_heads:
                rv_mean, rv_heads = measure_rv(
                    activations,
                    per_head=True,
                    num_heads=num_heads
                )
                results[name] = (rv_mean.item(), rv_heads)
            else:
                rv = measure_rv(activations)
                results[name] = rv.item() if rv.dim() == 0 else rv.mean().item()
        
        return results
    
    def compute_rv_summary(
        self,
        num_heads: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compute comprehensive R_V summary statistics.
        
        Returns:
            Dict with summary statistics including:
            - mean_rv: Average R_V across all layers
            - min_rv: Minimum R_V (potential bottleneck)
            - max_rv: Maximum R_V
            - per_layer: Dict of per-layer R_V values
            - per_head (if num_heads provided): Per-head breakdown
        """
        layer_rvs = self.compute_rv(per_head=False)
        
        if not layer_rvs:
            raise ValueError("No activations captured. Run a forward pass first.")
        
        rv_values = list(layer_rvs.values())
        
        summary = {
            "mean_rv": sum(rv_values) / len(rv_values),
            "min_rv": min(rv_values),
            "max_rv": max(rv_values),
            "std_rv": torch.tensor(rv_values).std().item(),
            "num_layers": len(rv_values),
            "per_layer": layer_rvs,
            "bottleneck_layer": min(layer_rvs, key=layer_rvs.get),
        }
        
        # Per-head analysis if requested
        if num_heads:
            head_results = self.compute_rv(per_head=True, num_heads=num_heads)
            head_rvs = []
            for name, (mean_rv, heads) in head_results.items():
                head_rvs.append(heads)
            
            if head_rvs:
                all_heads = torch.stack(head_rvs)  # (num_layers, num_heads)
                summary["per_head"] = {
                    "mean_per_head": all_heads.mean(dim=0).tolist(),
                    "min_head_idx": all_heads.mean(dim=0).argmin().item(),
                    "max_head_idx": all_heads.mean(dim=0).argmax().item(),
                }
        
        return summary
    
    @property
    def layer_names(self) -> List[str]:
        """List of detected V-projection layer names."""
        return list(self._layer_modules.keys())
    
    @property
    def num_layers(self) -> int:
        """Number of detected V-projection layers."""
        return len(self._layer_modules)


def find_v_projections(model: nn.Module) -> List[str]:
    """
    Utility to find potential V-projection layers in a model.
    
    Useful for debugging or custom pattern creation.
    
    Args:
        model: PyTorch model to inspect.
    
    Returns:
        List of module names that might be V-projections.
    """
    candidates = []
    keywords = ['v_proj', 'value', '_v', '.v', 'c_attn']
    
    for name, module in model.named_modules():
        name_lower = name.lower()
        if any(kw in name_lower for kw in keywords):
            candidates.append(name)
    
    return candidates


def quick_rv_measure(
    model: nn.Module,
    input_ids: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
    num_heads: Optional[int] = None,
    **model_kwargs
) -> Dict[str, Any]:
    """
    Quick one-shot R_V measurement for a model.
    
    Convenience function that handles hook setup, forward pass,
    and computation in one call.
    
    Args:
        model: Transformer model.
        input_ids: Input token IDs.
        attention_mask: Optional attention mask.
        num_heads: Number of attention heads (for per-head analysis).
        **model_kwargs: Additional kwargs passed to model forward.
    
    Returns:
        R_V summary dictionary.
    
    Example:
        >>> results = quick_rv_measure(model, input_ids, num_heads=12)
        >>> print(f"Mean R_V: {results['mean_rv']:.2f}")
        >>> print(f"Bottleneck: {results['bottleneck_layer']}")
    """
    manager = RVHookManager(model)
    
    with manager.capture():
        with torch.no_grad():
            if attention_mask is not None:
                model_kwargs['attention_mask'] = attention_mask
            model(input_ids, **model_kwargs)
    
    return manager.compute_rv_summary(num_heads=num_heads)


# ============================================================================
# Specialized hooks for common architectures
# ============================================================================

class GPT2RVHooks(RVHookManager):
    """Specialized hooks for GPT-2 style models."""
    
    def __init__(self, model: nn.Module, **kwargs):
        # GPT-2 uses combined QKV projection
        super().__init__(model, layer_pattern=r".*\.attn\.c_attn$", **kwargs)


class LLaMAHooks(RVHookManager):
    """Specialized hooks for LLaMA/Mistral style models."""
    
    def __init__(self, model: nn.Module, **kwargs):
        super().__init__(model, layer_pattern=r".*\.self_attn\.v_proj$", **kwargs)


class BERTRVHooks(RVHookManager):
    """Specialized hooks for BERT style models."""
    
    def __init__(self, model: nn.Module, **kwargs):
        super().__init__(model, layer_pattern=r".*\.attention\.self\.value$", **kwargs)
