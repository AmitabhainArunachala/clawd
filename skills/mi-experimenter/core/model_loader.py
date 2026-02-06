"""
Core Model Loader - Multi-Architecture Transformer Loading
==========================================================

Handles loading of various transformer architectures with automatic
detection and configuration for mechanistic interpretability experiments.

Supported Architectures:
- GPT-2 (and variants: GPT-Neo, GPT-J)
- LLaMA (1 & 2, including CodeLlama)
- Mistral (7B, 8x7B)
- Qwen (7B, 14B, 72B)
- Phi (2, 3)
- Gemma (2B, 7B, 9B)
- BERT/RoBERTa (for encoder experiments)

Example:
    >>> from mi_experimenter.core.model_loader import load_model
    >>> model, tokenizer = load_model("mistralai/Mistral-7B-v0.1", device="cuda")
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
from typing import Optional, Tuple, Dict, Any, Literal
import logging

logger = logging.getLogger(__name__)

# Architecture type mapping
ARCHITECTURE_TYPES = {
    # GPT-2 family
    "gpt2": "gpt2",
    "gpt2-medium": "gpt2",
    "gpt2-large": "gpt2",
    "gpt2-xl": "gpt2",
    "gpt-neo": "gpt2",
    "gpt-j": "gpt2",
    
    # LLaMA family
    "llama": "llama",
    "llama2": "llama",
    "codellama": "llama",
    
    # Mistral family
    "mistral": "mistral",
    "mixtral": "mistral-moe",
    
    # Qwen family
    "qwen": "qwen",
    "qwen2": "qwen",
    
    # Phi family
    "phi": "phi",
    "phi3": "phi",
    
    # Gemma family
    "gemma": "gemma",
    "gemma2": "gemma",
}


class ModelLoader:
    """
    Handles loading and configuration of transformer models for MI experiments.
    
    Args:
        model_name: HuggingFace model name or path
        device: Device to load model on ("cuda", "cpu", "auto")
        dtype: Data type ("float16", "bfloat16", "float32", "auto")
        trust_remote_code: Whether to trust remote code for custom architectures
        use_flash_attention: Whether to use flash attention if available
    """
    
    def __init__(
        self,
        model_name: str,
        device: str = "auto",
        dtype: str = "auto",
        trust_remote_code: bool = True,
        use_flash_attention: bool = True,
    ):
        self.model_name = model_name
        self.device = self._resolve_device(device)
        self.dtype = self._resolve_dtype(dtype)
        self.trust_remote_code = trust_remote_code
        self.use_flash_attention = use_flash_attention
        
        self.model = None
        self.tokenizer = None
        self.config = None
        self.architecture = None
        
    def _resolve_device(self, device: str) -> str:
        """Resolve device string to actual device."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def _resolve_dtype(self, dtype: str) -> torch.dtype:
        """Resolve dtype string to torch dtype."""
        if dtype == "auto":
            if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
                return torch.bfloat16
            elif torch.cuda.is_available():
                return torch.float16
            else:
                return torch.float32
        
        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        return dtype_map.get(dtype, torch.float32)
    
    def _detect_architecture(self, config: AutoConfig) -> str:
        """Detect architecture type from config."""
        model_type = getattr(config, "model_type", "").lower()
        
        # Check architecture mappings
        for key, arch in ARCHITECTURE_TYPES.items():
            if key in model_type:
                return arch
        
        # Fallback to model type
        return model_type
    
    def _get_model_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for model loading based on architecture."""
        kwargs = {
            "trust_remote_code": self.trust_remote_code,
            "torch_dtype": self.dtype,
        }
        
        # Add flash attention if requested and available
        if self.use_flash_attention:
            # Try different attention implementations
            try:
                # For newer transformers
                kwargs["attn_implementation"] = "flash_attention_2"
            except:
                pass
        
        return kwargs
    
    def load(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """
        Load the model and tokenizer.
        
        Returns:
            Tuple of (model, tokenizer)
        """
        logger.info(f"Loading model: {self.model_name}")
        logger.info(f"Device: {self.device}, Dtype: {self.dtype}")
        
        # Load tokenizer first
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=self.trust_remote_code
        )
        
        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load config for architecture detection
        self.config = AutoConfig.from_pretrained(
            self.model_name,
            trust_remote_code=self.trust_remote_code
        )
        self.architecture = self._detect_architecture(self.config)
        logger.info(f"Detected architecture: {self.architecture}")
        
        # Load model
        model_kwargs = self._get_model_kwargs()
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
        except Exception as e:
            logger.warning(f"Failed with flash attention: {e}")
            logger.warning("Retrying without flash attention...")
            model_kwargs.pop("attn_implementation", None)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
        
        # Move to device
        self.model = self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"Model loaded successfully")
        logger.info(f"Parameters: {sum(p.numel() for p in self.model.parameters()) / 1e6:.1f}M")
        
        return self.model, self.tokenizer
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        return {
            "model_name": self.model_name,
            "architecture": self.architecture,
            "num_layers": getattr(self.config, "num_hidden_layers", None),
            "num_heads": getattr(self.config, "num_attention_heads", None),
            "hidden_size": getattr(self.config, "hidden_size", None),
            "vocab_size": getattr(self.config, "vocab_size", None),
            "num_parameters": sum(p.numel() for p in self.model.parameters()),
            "device": self.device,
            "dtype": str(self.dtype),
        }
    
    @property
    def num_layers(self) -> int:
        """Get number of layers in the model."""
        if self.config is None:
            raise RuntimeError("Model not loaded")
        return getattr(self.config, "num_hidden_layers", 0)
    
    @property
    def num_heads(self) -> int:
        """Get number of attention heads."""
        if self.config is None:
            raise RuntimeError("Model not loaded")
        return getattr(self.config, "num_attention_heads", 0)
    
    @property
    def hidden_size(self) -> int:
        """Get hidden dimension size."""
        if self.config is None:
            raise RuntimeError("Model not loaded")
        return getattr(self.config, "hidden_size", 0)


def load_model(
    model_name: str,
    device: str = "auto",
    dtype: str = "auto",
    trust_remote_code: bool = True,
    **kwargs
) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """
    Convenience function to load a model and tokenizer.
    
    Args:
        model_name: HuggingFace model name or path
        device: Device to load on ("cuda", "cpu", "auto")
        dtype: Data type ("float16", "bfloat16", "float32", "auto")
        trust_remote_code: Whether to trust remote code
        **kwargs: Additional arguments passed to ModelLoader
    
    Returns:
        Tuple of (model, tokenizer)
    
    Example:
        >>> model, tokenizer = load_model("mistralai/Mistral-7B-v0.1", device="cuda")
    """
    loader = ModelLoader(
        model_name=model_name,
        device=device,
        dtype=dtype,
        trust_remote_code=trust_remote_code,
        **kwargs
    )
    return loader.load()
