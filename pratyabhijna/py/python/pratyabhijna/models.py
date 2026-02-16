"""
Model loader with automatic RV hook injection.

Supports:
- Mistral-7B
- Llama-3 (8B, 70B variants)
- Qwen-2.5

Usage:
    from pratyabhijna.models import load_model_with_hooks
    
    model, hook = load_model_with_hooks("mistral-7b")
    output = model.generate("Tell me about consciousness...")
    events = hook.get_events()
"""

import torch
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from transformer_lens import HookedTransformer
import warnings

from pratyabhijna.hooks import RVHook, RVEvent
from pratyabhijna._internal import compute_rv_from_tensors_py, RVMetric as _RVMetric


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    tl_name: str
    early_layer: int
    late_layer: int
    d_head: int
    n_layers: int
    window_size: int = 16
    
    
# Hardcoded configs for supported models
MODEL_CONFIGS: Dict[str, ModelConfig] = {
    "mistral-7b": ModelConfig(
        name="mistral-7b",
        tl_name="mistral-7b-instruct",
        early_layer=5,
        late_layer=27,
        d_head=128,
        n_layers=32,
    ),
    "mistral-7b-v0.1": ModelConfig(
        name="mistral-7b-v0.1",
        tl_name="mistral-7b",
        early_layer=5,
        late_layer=27,
        d_head=128,
        n_layers=32,
    ),
    "llama-3-8b": ModelConfig(
        name="llama-3-8b",
        tl_name="meta-llama/Meta-Llama-3-8B-Instruct",
        early_layer=6,
        late_layer=28,
        d_head=128,
        n_layers=32,
    ),
    "llama-3-70b": ModelConfig(
        name="llama-3-70b",
        tl_name="meta-llama/Meta-Llama-3-70B-Instruct",
        early_layer=16,
        late_layer=64,
        d_head=128,
        n_layers=80,
    ),
    "qwen-2.5-7b": ModelConfig(
        name="qwen-2.5-7b",
        tl_name="Qwen/Qwen2.5-7B-Instruct",
        early_layer=6,
        late_layer=22,
        d_head=128,
        n_layers=28,
    ),
    "qwen-2.5-14b": ModelConfig(
        name="qwen-2.5-14b",
        tl_name="Qwen/Qwen2.5-14B-Instruct",
        early_layer=8,
        late_layer=30,
        d_head=128,
        n_layers=48,
    ),
    "qwen-2.5-32b": ModelConfig(
        name="qwen-2.5-32b",
        tl_name="Qwen/Qwen2.5-32B-Instruct",
        early_layer=10,
        late_layer=44,
        d_head=128,
        n_layers=64,
    ),
}


class AutoRVHook(RVHook):
    """
    Extended RVHook with automatic FFI to Rust core.
    
    Uses PyO3 bindings for fast SVD computation via faer-rs.
    """
    
    def __init__(
        self,
        model: HookedTransformer,
        config: ModelConfig,
        device: str = "cpu",
    ):
        self.config = config
        self.device = device
        super().__init__(
            model=model,
            early_layer=config.early_layer,
            late_layer=config.late_layer,
            window_size=config.window_size,
        )
        
    def _calculate_rv(self, v_early, v_late):
        """Override with Rust FFI computation."""
        try:
            # Convert to numpy for PyO3
            v_early_np = v_early[0].numpy() if isinstance(v_early, torch.Tensor) else v_early[0]
            v_late_np = v_late[0].numpy() if isinstance(v_late, torch.Tensor) else v_late[0]
            
            # Call Rust via PyO3
            metric = compute_rv_from_tensors_py(
                v_early_np,
                v_late_np,
                window_size=self.window_size,
                layer_early=self.early_layer,
                layer_late=self.late_layer,
                model_name=self.config.name,
            )
            
            # Convert to Python RVEvent
            return RVEvent(
                r_v=metric.r_v,
                pr_early=metric.pr_early,
                pr_late=metric.pr_late,
                layer_early=metric.layer_early,
                layer_late=metric.layer_late,
                token_position=v_late_np.shape[0],
                timestamp=metric.timestamp / 1000.0,  # Convert ms to seconds
            )
        except Exception as e:
            # Fall back to parent implementation if Rust fails
            warnings.warn(f"Rust FFI failed ({e}), falling back to numpy")
            return super()._calculate_rv(v_early, v_late)


def load_model_with_hooks(
    model_name: str,
    device: Optional[str] = None,
    dtype: torch.dtype = torch.float16,
    **kwargs
) -> Tuple[HookedTransformer, AutoRVHook]:
    """
    Load a model with automatic RV hook injection.
    
    Args:
        model_name: Short name (e.g., "mistral-7b", "llama-3-8b")
        device: Device to load on (auto-detected if None)
        dtype: Data type for model weights
        **kwargs: Additional arguments passed to HookedTransformer.from_pretrained
        
    Returns:
        Tuple of (model, hook)
        
    Example:
        >>> model, hook = load_model_with_hooks("mistral-7b")
        >>> output = model.generate("What is consciousness?", max_new_tokens=100)
        >>> events = hook.get_events()
        >>> print(f"Recognition events: {len([e for e in events if e.is_recognition()])}")
    """
    # Get config
    if model_name not in MODEL_CONFIGS:
        raise ValueError(
            f"Unknown model: {model_name}. "
            f"Supported: {list(MODEL_CONFIGS.keys())}"
        )
    
    config = MODEL_CONFIGS[model_name]
    
    # Auto-detect device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"Loading {model_name} ({config.tl_name}) on {device}...")
    
    # Load model via TransformerLens
    model = HookedTransformer.from_pretrained(
        config.tl_name,
        device=device,
        dtype=dtype,
        **kwargs
    )
    
    # Create and install hook
    hook = AutoRVHook(model, config, device=device)
    hook.install()
    
    print(f"✓ RV hooks installed: layer {config.early_layer} → {config.late_layer}")
    
    return model, hook


def load_custom_model(
    tl_name: str,
    early_layer: int,
    late_layer: int,
    window_size: int = 16,
    device: Optional[str] = None,
    **kwargs
) -> Tuple[HookedTransformer, AutoRVHook]:
    """
    Load any HookedTransformer-compatible model with custom hook configuration.
    
    Args:
        tl_name: TransformerLens model name
        early_layer: Early layer index for R_V
        late_layer: Late layer index for R_V
        window_size: Token window for SVD
        device: Device to load on
        **kwargs: Arguments passed to from_pretrained
        
    Returns:
        Tuple of (model, hook)
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Create custom config
    config = ModelConfig(
        name=tl_name,
        tl_name=tl_name,
        early_layer=early_layer,
        late_layer=late_layer,
        d_head=128,  # Default, will be auto-detected
        n_layers=late_layer + 5,  # Estimate
        window_size=window_size,
    )
    
    print(f"Loading {tl_name} with custom config...")
    
    model = HookedTransformer.from_pretrained(
        tl_name,
        device=device,
        **kwargs
    )
    
    # Auto-detect dimensions
    if hasattr(model.cfg, 'd_head'):
        config.d_head = model.cfg.d_head
    if hasattr(model.cfg, 'n_layers'):
        config.n_layers = model.cfg.n_layers
    
    hook = AutoRVHook(model, config, device=device)
    hook.install()
    
    print(f"✓ Custom RV hooks installed: {early_layer} → {late_layer}")
    
    return model, hook


class ModelRegistry:
    """Registry for managing multiple models with hooks."""
    
    def __init__(self):
        self._models: Dict[str, Tuple[HookedTransformer, AutoRVHook]] = {}
    
    def load(self, name: str, **kwargs) -> HookedTransformer:
        """Load a model and store in registry."""
        model, hook = load_model_with_hooks(name, **kwargs)
        self._models[name] = (model, hook)
        return model
    
    def get(self, name: str) -> Tuple[HookedTransformer, AutoRVHook]:
        """Get model and hook from registry."""
        if name not in self._models:
            raise KeyError(f"Model {name} not loaded. Call load() first.")
        return self._models[name]
    
    def get_hook(self, name: str) -> AutoRVHook:
        """Get just the hook for a model."""
        return self._models[name][1]
    
    def get_events(self, name: str) -> list:
        """Get events from a model's hook."""
        return self._models[name][1].get_events()
    
    def clear_events(self, name: Optional[str] = None):
        """Clear events for one or all models."""
        if name is None:
            for _, hook in self._models.values():
                hook.clear_events()
        else:
            self._models[name][1].clear_events()
    
    def remove_hooks(self, name: Optional[str] = None):
        """Remove hooks from one or all models."""
        if name is None:
            for _, hook in self._models.values():
                hook.remove()
        else:
            self._models[name][1].remove()
    
    def list_loaded(self) -> list:
        """List all loaded model names."""
        return list(self._models.keys())


# Global registry for convenience
_global_registry = ModelRegistry()


def quick_load(model_name: str, **kwargs) -> HookedTransformer:
    """Quick load a model into the global registry."""
    return _global_registry.load(model_name, **kwargs)


def get_hook(model_name: Optional[str] = None) -> AutoRVHook:
    """
    Get hook from global registry.
    
    If model_name is None and only one model is loaded, return that.
    """
    if model_name is None:
        loaded = _global_registry.list_loaded()
        if len(loaded) == 1:
            return _global_registry.get_hook(loaded[0])
        elif len(loaded) == 0:
            raise RuntimeError("No models loaded. Call quick_load() first.")
        else:
            raise RuntimeError(f"Multiple models loaded: {loaded}. Specify model_name.")
    return _global_registry.get_hook(model_name)


def get_events(model_name: Optional[str] = None) -> list:
    """Get events from global registry."""
    hook = get_hook(model_name)
    return hook.get_events()
