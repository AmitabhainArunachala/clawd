"""
Hook Manager - Activation Capture and Patching
==============================================

Manages hooks for capturing and patching activations at any layer
and component of a transformer model.

Integrates with TransformerLens-style hook points while maintaining
compatibility with standard HuggingFace models.

Example:
    >>> from mi_experimenter.core.hook_manager import HookManager
    >>> manager = HookManager(model)
    >>> 
    >>> # Capture activations
    >>> with manager.capture_activations(["blocks.15.hook_resid_pre"]):
    ...     output = model(input_ids)
    >>> cache = manager.get_cache()
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager
import re


@dataclass
class ActivationCache:
    """Container for cached activations."""
    activations: Dict[str, List[torch.Tensor]] = field(default_factory=dict)
    
    def add(self, hook_point: str, tensor: torch.Tensor):
        """Add an activation to the cache."""
        if hook_point not in self.activations:
            self.activations[hook_point] = []
        self.activations[hook_point].append(tensor.detach().cpu())
    
    def get(self, hook_point: str) -> torch.Tensor:
        """Get stacked activations for a hook point."""
        if hook_point not in self.activations:
            raise KeyError(f"Hook point '{hook_point}' not in cache")
        return torch.cat(self.activations[hook_point], dim=0)
    
    def get_all(self) -> Dict[str, torch.Tensor]:
        """Get all activations as stacked tensors."""
        return {k: torch.cat(v, dim=0) for k, v in self.activations.items()}
    
    def clear(self):
        """Clear all cached activations."""
        self.activations.clear()
    
    def __contains__(self, hook_point: str) -> bool:
        return hook_point in self.activations
    
    def __getitem__(self, hook_point: str) -> torch.Tensor:
        return self.get(hook_point)


class HookManager:
    """
    Manages forward hooks for activation capture and patching.
    
    Provides TransformerLens-style hook points:
    - resid_pre: Residual stream before attention
    - resid_mid: Residual stream after attention, before MLP
    - resid_post: Residual stream after MLP
    - attn_out: Attention output (before residual add)
    - mlp_out: MLP output (before residual add)
    - v_proj: Value projection
    - q_proj: Query projection
    - k_proj: Key projection
    - o_proj: Output projection
    
    Args:
        model: The transformer model
        architecture: Architecture type ("gpt2", "llama", "mistral", etc.)
    """
    
    # Hook point patterns for different architectures
    HOOK_PATTERNS = {
        "gpt2": {
            "resid_pre": r"transformer\.h\.(\d+)\.ln_1",
            "resid_mid": r"transformer\.h\.(\d+)\.attn",
            "resid_post": r"transformer\.h\.(\d+)\.ln_2",
            "attn_out": r"transformer\.h\.(\d+)\.attn",
            "mlp_out": r"transformer\.h\.(\d+)\.mlp",
            "v_proj": r"transformer\.h\.(\d+)\.attn",
        },
        "llama": {
            "resid_pre": r"model\.layers\.(\d+)\.input_layernorm",
            "resid_mid": r"model\.layers\.(\d+)\.post_attention_layernorm",
            "resid_post": r"model\.layers\.(\d+)$",
            "attn_out": r"model\.layers\.(\d+)\.self_attn",
            "mlp_out": r"model\.layers\.(\d+)\.mlp$",
            "v_proj": r"model\.layers\.(\d+)\.self_attn\.v_proj",
            "q_proj": r"model\.layers\.(\d+)\.self_attn\.q_proj",
            "k_proj": r"model\.layers\.(\d+)\.self_attn\.k_proj",
            "o_proj": r"model\.layers\.(\d+)\.self_attn\.o_proj",
        },
        "mistral": {
            "resid_pre": r"model\.layers\.(\d+)\.input_layernorm",
            "resid_mid": r"model\.layers\.(\d+)\.post_attention_layernorm",
            "resid_post": r"model\.layers\.(\d+)$",
            "attn_out": r"model\.layers\.(\d+)\.self_attn",
            "mlp_out": r"model\.layers\.(\d+)\.mlp$",
            "v_proj": r"model\.layers\.(\d+)\.self_attn\.v_proj",
            "q_proj": r"model\.layers\.(\d+)\.self_attn\.q_proj",
            "k_proj": r"model\.layers\.(\d+)\.self_attn\.k_proj",
            "o_proj": r"model\.layers\.(\d+)\.self_attn\.o_proj",
        },
    }
    
    def __init__(self, model: nn.Module, architecture: str = "auto"):
        self.model = model
        self.architecture = architecture
        self._cache = ActivationCache()
        self._hooks: List[torch.utils.hooks.RemovableHandle] = []
        self._patch_hooks: List[torch.utils.hooks.RemovableHandle] = []
        
        # Auto-detect architecture if needed
        if architecture == "auto":
            self.architecture = self._detect_architecture()
    
    def _detect_architecture(self) -> str:
        """Auto-detect architecture from model structure."""
        model_class = self.model.__class__.__name__.lower()
        
        if "llama" in model_class:
            return "llama"
        elif "mistral" in model_class:
            return "mistral"
        elif "gpt2" in model_class or "gpt" in model_class:
            return "gpt2"
        elif "qwen" in model_class:
            return "qwen"
        elif "phi" in model_class:
            return "phi"
        elif "gemma" in model_class:
            return "gemma"
        
        # Try to infer from module names
        for name, _ in self.model.named_modules():
            if "model.layers" in name:
                return "llama"  # Generic LLaMA-style
            elif "transformer.h" in name:
                return "gpt2"
        
        return "unknown"
    
    def _get_module(self, pattern: str, layer_idx: int) -> Optional[nn.Module]:
        """Get a module matching the pattern and layer index."""
        full_pattern = pattern.replace(r"(\d+)", str(layer_idx))
        
        for name, module in self.model.named_modules():
            if re.search(full_pattern, name):
                return module
        return None
    
    def _create_capture_hook(self, hook_point: str) -> Callable:
        """Create a hook function that captures activations."""
        def hook(module, input, output):
            # Handle different output types
            if isinstance(output, tuple):
                tensor = output[0]
            else:
                tensor = output
            
            # Handle GPT-2 combined QKV
            if "v_proj" in hook_point and self.architecture == "gpt2":
                # Split combined projection
                hidden_size = tensor.shape[-1] // 3
                tensor = tensor[..., 2*hidden_size:]
            
            self._cache.add(hook_point, tensor)
        
        return hook
    
    def _create_patch_hook(self, hook_point: str, patch_value: torch.Tensor) -> Callable:
        """Create a hook function that patches activations."""
        def hook(module, input, output):
            # Handle different output types
            if isinstance(output, tuple):
                original = output[0]
                # Apply patch
                patched = patch_value.to(original.device, dtype=original.dtype)
                new_output = (patched,) + output[1:]
                return new_output
            else:
                return patch_value.to(output.device, dtype=output.dtype)
        
        return hook
    
    @contextmanager
    def capture_activations(self, hook_points: List[str]):
        """
        Context manager to capture activations at specified hook points.
        
        Args:
            hook_points: List of hook point names (e.g., ["blocks.15.hook_resid_pre"])
        
        Example:
            >>> with manager.capture_activations(["blocks.15.hook_resid_pre"]):
            ...     output = model(input_ids)
            >>> cache = manager.get_cache()
        """
        self._cache.clear()
        self._attach_capture_hooks(hook_points)
        
        try:
            yield self
        finally:
            self._remove_hooks()
    
    @contextmanager
    def patch_activations(self, patches: Dict[str, torch.Tensor]):
        """
        Context manager to patch activations at specified hook points.
        
        Args:
            patches: Dict mapping hook points to patch values
        
        Example:
            >>> patches = {"blocks.15.hook_resid_pre": source_activations}
            >>> with manager.patch_activations(patches):
            ...     output = model(target_input)
        """
        self._attach_patch_hooks(patches)
        
        try:
            yield self
        finally:
            self._remove_patch_hooks()
    
    def _attach_capture_hooks(self, hook_points: List[str]):
        """Attach capture hooks for specified hook points."""
        patterns = self.HOOK_PATTERNS.get(self.architecture, {})
        
        for hook_point in hook_points:
            # Parse hook point (e.g., "blocks.15.hook_resid_pre")
            parts = hook_point.split(".")
            if len(parts) >= 2:
                layer_idx = int(parts[1])
                component = parts[2] if len(parts) > 2 else "resid_pre"
                
                pattern = patterns.get(component, component)
                module = self._get_module(pattern, layer_idx)
                
                if module is not None:
                    hook_fn = self._create_capture_hook(hook_point)
                    handle = module.register_forward_hook(hook_fn)
                    self._hooks.append(handle)
    
    def _attach_patch_hooks(self, patches: Dict[str, torch.Tensor]):
        """Attach patch hooks."""
        patterns = self.HOOK_PATTERNS.get(self.architecture, {})
        
        for hook_point, patch_value in patches.items():
            parts = hook_point.split(".")
            if len(parts) >= 2:
                layer_idx = int(parts[1])
                component = parts[2] if len(parts) > 2 else "resid_pre"
                
                pattern = patterns.get(component, component)
                module = self._get_module(pattern, layer_idx)
                
                if module is not None:
                    hook_fn = self._create_patch_hook(hook_point, patch_value)
                    handle = module.register_forward_hook(hook_fn)
                    self._patch_hooks.append(handle)
    
    def _remove_hooks(self):
        """Remove all capture hooks."""
        for hook in self._hooks:
            hook.remove()
        self._hooks.clear()
    
    def _remove_patch_hooks(self):
        """Remove all patch hooks."""
        for hook in self._patch_hooks:
            hook.remove()
        self._patch_hooks.clear()
    
    def get_cache(self) -> ActivationCache:
        """Get the activation cache."""
        return self._cache
    
    def clear_cache(self):
        """Clear the activation cache."""
        self._cache.clear()
    
    def list_available_hook_points(self, max_layer: Optional[int] = None) -> List[str]:
        """
        List available hook points for this model.
        
        Args:
            max_layer: Maximum layer index to include
        
        Returns:
            List of hook point names
        """
        if max_layer is None:
            # Try to infer from model
            max_layer = 32  # Default
        
        hook_points = []
        components = ["resid_pre", "resid_mid", "resid_post", "attn_out", "mlp_out", "v_proj"]
        
        for layer in range(max_layer):
            for component in components:
                hook_points.append(f"blocks.{layer}.hook_{component}")
        
        return hook_points
