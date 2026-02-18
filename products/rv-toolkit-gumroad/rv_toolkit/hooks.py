"""
Hook utilities for capturing transformer activations.

Context managers for safely capturing V-projection activations during forward passes.
"""

import torch
from contextlib import contextmanager


@contextmanager
def capture_v_projection(model, layer_idx):
    """
    Capture the output of self_attn.v_proj at a specific layer.

    Args:
        model: Transformer model
        layer_idx: Layer index (0-indexed)

    Yields:
        Context manager that returns a storage dict with 'v' key
    
    Example:
        with capture_v_projection(model, 5) as storage:
            model(**inputs)
        v_tensor = storage.get('v')  # shape [batch, seq_len, hidden]
    """
    storage = {'v': None}
    
    def hook_fn(module, inp, out):
        storage['v'] = out.detach()
        return out
    
    # Get the target layer's v_proj
    try:
        layer = model.model.layers[layer_idx].self_attn
    except AttributeError:
        # Try different model architectures
        try:
            layer = model.transformer.layers[layer_idx].self_attn
        except AttributeError:
            try:
                layer = model.layers[layer_idx].self_attn
            except AttributeError:
                raise ValueError(f"Could not find layer {layer_idx} in model architecture")
    
    handle = layer.v_proj.register_forward_hook(hook_fn)
    
    try:
        yield storage
    finally:
        handle.remove()


@contextmanager 
def capture_v_at_layer(model, layer_idx, storage_list):
    """
    Capture V-projection at a layer and append to provided list.
    
    Args:
        model: Transformer model
        layer_idx: Layer index (0-indexed)
        storage_list: List to append captured tensor to
        
    Yields:
        Context manager for clean hook registration
        
    Note:
        Appends tensor of shape [batch, seq_len, hidden]
    """
    def hook_fn(module, inp, out):
        storage_list.append(out.detach())
        return out
    
    try:
        layer = model.model.layers[layer_idx].self_attn
    except AttributeError:
        try:
            layer = model.transformer.layers[layer_idx].self_attn
        except AttributeError:
            try:
                layer = model.layers[layer_idx].self_attn
            except AttributeError:
                raise ValueError(f"Could not find layer {layer_idx} in model architecture")
    
    handle = layer.v_proj.register_forward_hook(hook_fn)
    
    try:
        yield
    finally:
        handle.remove()


def capture_activation(model, layer_idx, module_path='self_attn.v_proj'):
    """
    Generalized activation capture for any module.
    
    Args:
        model: Transformer model
        layer_idx: Layer index (0-indexed)
        module_path: Path to module within layer (e.g., 'self_attn.v_proj')
        
    Returns:
        Context manager yielding storage dict
    """
    storage = {'activation': None}
    
    def hook_fn(module, inp, out):
        storage['activation'] = out.detach()
        return out
    
    # Navigate to target module
    try:
        layer = model.model.layers[layer_idx]
    except AttributeError:
        try:
            layer = model.transformer.layers[layer_idx]
        except AttributeError:
            try:
                layer = model.layers[layer_idx]
            except AttributeError:
                raise ValueError(f"Could not find layer {layer_idx} in model architecture")
    
    module = layer
    for part in module_path.split('.'):
        module = getattr(module, part)
    
    handle = module.register_forward_hook(hook_fn)
    
    try:
        yield storage
    finally:
        handle.remove()


def safe_register_hook(model, module_path, hook_fn):
    """
    Safely register a hook on a module identified by path.
    
    Args:
        model: PyTorch model
        module_path: Dot-separated path to module (e.g., 'model.layers.27.self_attn.v_proj')
        hook_fn: Hook function with signature hook_fn(module, inp, out)
        
    Returns:
        Hook handle for removal
    """
    module = model
    for part in module_path.split('.'):
        module = getattr(module, part)
    
    return module.register_forward_hook(hook_fn)


def get_layer_count(model):
    """Get number of layers in model."""
    try:
        return len(model.model.layers)
    except AttributeError:
        try:
            return len(model.transformer.layers)
        except AttributeError:
            try:
                return len(model.layers)
            except AttributeError:
                # Try config
                try:
                    return model.config.num_hidden_layers
                except AttributeError:
                    return None