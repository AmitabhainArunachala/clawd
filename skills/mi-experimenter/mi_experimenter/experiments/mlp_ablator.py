"""
MLP Ablator - Layer Necessity Analysis via R_V
===============================================

Ablates MLP layers and measures changes in R_V to determine layer necessity.
Uses rv_toolkit for R_V computation and local hook_manager for ablation patches.

The necessity score indicates how critical each MLP layer is for maintaining
representation quality:
- High necessity (d > 1, p < 0.05): Layer is critical
- Moderate necessity (0.5 < d < 1): Layer contributes meaningfully
- Low necessity (d < 0.5, p > 0.05): Layer may be prunable

Example:
    >>> from mi_experimenter.experiments.mlp_ablator import MLPAblator
    >>> ablator = MLPAblator("gpt2")
    >>> results = ablator.run(test_prompts=["The cat sat on the"])
    >>> 
    >>> # Find most critical layers
    >>> critical = [l for l, r in results['necessity_scores'].items() 
    ...             if r['d'] > 1.0 and r['p'] < 0.05]
    >>> print(f"Critical layers: {critical}")
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import warnings
from pathlib import Path

from scipy import stats

# Import rv_toolkit for R_V computation (use local version)
import sys
from pathlib import Path
_rv_toolkit_path = str(Path(__file__).parent.parent.parent / "rv_toolkit")
if _rv_toolkit_path not in sys.path:
    sys.path.insert(0, _rv_toolkit_path)

from rv_toolkit import quick_rv_measure, measure_rv
from rv_toolkit.rv_hooks import RVHookManager

# Import local hook_manager for ablation patching
from ..core.hook_manager import HookManager
from ..core.model_loader import ModelLoader

logger = logging.getLogger(__name__)


@dataclass
class AblationResult:
    """R_V measurement result for a single ablation configuration."""
    layer_idx: int
    ablated: bool
    rv_mean: float
    rv_per_layer: Dict[str, float]
    computation_time_sec: float = 0.0
    error: Optional[str] = None


@dataclass
class NecessityScore:
    """Necessity score for a single MLP layer."""
    layer_idx: int
    cohens_d: float  # Effect size of ablation
    p_value: float   # Statistical significance
    rv_baseline: float
    rv_ablated: float
    rv_change_pct: float
    interpretation: str = ""


class MLPAblator:
    """
    Ablates MLP layers and measures R_V change to determine necessity.
    
    Uses rv_toolkit for R_V measurement and local hook_manager for
    applying ablation masks (zeroing out MLP outputs).
    
    Args:
        model_name: HuggingFace model name or path
        device: Device to run on ("cuda", "cpu", "auto")
        dtype: Data type for model loading
        ablation_mode: How to ablate ("zero", "mean", "noise")
        smoke_test: If True, run minimal test
        random_seed: Random seed for determinism
    
    Example:
        >>> ablator = MLPAblator("gpt2", ablation_mode="zero")
        >>> results = ablator.run(test_prompts=["The cat sat"])
        >>> 
        >>> for layer, score in results['necessity_scores'].items():
        ...     print(f"{layer}: d={score['d']:.2f}, p={score['p']:.4f}")
    """
    
    ABLATION_MODES = ["zero", "mean", "noise", "skip"]
    
    def __init__(
        self,
        model_name: str,
        device: str = "auto",
        dtype: str = "auto",
        ablation_mode: str = "zero",
        smoke_test: bool = False,
        random_seed: int = 42,
        output_dir: Optional[str] = None,
        n_bootstrap: int = 100
    ):
        self.model_name = model_name
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype
        self.ablation_mode = ablation_mode
        self.smoke_test = smoke_test
        self.random_seed = random_seed
        self.output_dir = Path(output_dir) if output_dir else None
        self.n_bootstrap = n_bootstrap
        
        # State
        self.model: Optional[nn.Module] = None
        self.tokenizer: Optional[Any] = None
        self.hook_manager: Optional[HookManager] = None
        self.num_layers: int = 0
        self.baseline_results: Optional[AblationResult] = None
        self.ablation_results: List[AblationResult] = []
        self.hardware_info = self._log_hardware()
        
        self._set_determinism()
    
    def _set_determinism(self):
        """Set random seeds for reproducibility."""
        torch.manual_seed(self.random_seed)
        np.random.seed(self.random_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.random_seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        logger.info(f"Random seed set to {self.random_seed}")
    
    def _log_hardware(self) -> Dict[str, Any]:
        """Log hardware information."""
        info = {
            "timestamp": datetime.now().isoformat(),
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "pytorch_version": torch.__version__,
        }
        
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
        
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count()
            info["ram_gb"] = psutil.virtual_memory().total / 1e9
        except ImportError:
            pass
        
        return info
    
    def _load_model(self):
        """Load model and create hook manager."""
        logger.info(f"Loading model: {self.model_name}")
        
        loader = ModelLoader(
            model_name=self.model_name,
            device=self.device,
            dtype=self.dtype,
            trust_remote_code=True
        )
        self.model, self.tokenizer = loader.load()
        self.num_layers = loader.num_layers
        
        # Create hook manager for ablation
        self.hook_manager = HookManager(self.model, architecture=loader.architecture)
        
        logger.info(f"Model loaded: {self.num_layers} layers")
    
    def _get_ablation_patch(
        self, 
        original_output: torch.Tensor
    ) -> torch.Tensor:
        """
        Create ablation patch based on mode.
        
        Args:
            original_output: The original MLP output tensor
        
        Returns:
            Patched tensor
        """
        if self.ablation_mode == "zero":
            # Zero out the MLP output
            return torch.zeros_like(original_output)
        
        elif self.ablation_mode == "mean":
            # Replace with mean value
            return original_output.mean(dim=-1, keepdim=True).expand_as(original_output)
        
        elif self.ablation_mode == "noise":
            # Replace with Gaussian noise matching statistics
            mean = original_output.mean()
            std = original_output.std()
            return torch.randn_like(original_output) * std + mean
        
        elif self.ablation_mode == "skip":
            # Return original unchanged (for testing)
            return original_output
        
        else:
            raise ValueError(f"Unknown ablation mode: {self.ablation_mode}")
    
    def _create_ablation_hook(
        self, 
        layer_idx: int
    ) -> Callable:
        """
        Create a forward hook that ablates MLP output.
        
        Args:
            layer_idx: Layer index to ablate
        
        Returns:
            Hook function
        """
        def hook(module, input, output):
            # Handle tuple outputs
            if isinstance(output, tuple):
                original = output[0]
                patched = self._get_ablation_patch(original)
                return (patched,) + output[1:]
            else:
                return self._get_ablation_patch(output)
        
        return hook
    
    def _measure_rv_baseline(
        self, 
        input_ids: torch.Tensor
    ) -> AblationResult:
        """Measure baseline R_V without any ablation."""
        logger.info("Measuring baseline R_V...")
        
        import time
        start = time.time()
        
        # Use rv_toolkit for measurement
        rv_summary = quick_rv_measure(
            self.model,
            input_ids,
            num_heads=None  # Aggregate across heads
        )
        
        elapsed = time.time() - start
        
        return AblationResult(
            layer_idx=-1,
            ablated=False,
            rv_mean=rv_summary.get('mean_rv', 0.0),
            rv_per_layer=rv_summary.get('per_layer', {}),
            computation_time_sec=elapsed
        )
    
    def _measure_rv_with_ablation(
        self,
        input_ids: torch.Tensor,
        layer_idx: int
    ) -> AblationResult:
        """
        Measure R_V with a specific MLP layer ablated.
        
        Uses hook_manager to patch the MLP output at the specified layer.
        """
        logger.info(f"Measuring R_V with layer {layer_idx} ablated...")
        
        import time
        start = time.time()
        
        # Register ablation hook
        patterns = self.hook_manager.HOOK_PATTERNS.get(
            self.hook_manager.architecture, 
            {}
        )
        mlp_pattern = patterns.get('mlp_out', r'.*\.mlp$')
        
        # Find the MLP module for this layer
        mlp_module = None
        import re
        for name, module in self.model.named_modules():
            full_pattern = mlp_pattern.replace(r'(\d+)', str(layer_idx))
            if re.search(full_pattern, name):
                mlp_module = module
                break
        
        if mlp_module is None:
            logger.warning(f"Could not find MLP module for layer {layer_idx}")
            return AblationResult(
                layer_idx=layer_idx,
                ablated=True,
                rv_mean=0.0,
                rv_per_layer={},
                error=f"MLP module not found for layer {layer_idx}"
            )
        
        # Register hook
        hook = mlp_module.register_forward_hook(self._create_ablation_hook(layer_idx))
        
        try:
            # Measure with ablation
            rv_summary = quick_rv_measure(
                self.model,
                input_ids,
                num_heads=None
            )
            
            elapsed = time.time() - start
            
            return AblationResult(
                layer_idx=layer_idx,
                ablated=True,
                rv_mean=rv_summary.get('mean_rv', 0.0),
                rv_per_layer=rv_summary.get('per_layer', {}),
                computation_time_sec=elapsed
            )
            
        finally:
            hook.remove()
    
    def _compute_necessity_scores(self) -> Dict[str, Dict[str, float]]:
        """
        Compute necessity scores (Cohen's d and p-values) for each layer.
        
        Uses bootstrap resampling for robust statistical testing.
        """
        necessity_scores = {}
        
        baseline = self.baseline_results
        if baseline is None or baseline.error:
            logger.error("No valid baseline results")
            return necessity_scores
        
        baseline_rvs = list(baseline.rv_per_layer.values())
        
        for ablation in self.ablation_results:
            if ablation.error:
                continue
            
            layer_key = f"layer_{ablation.layer_idx}"
            ablated_rvs = list(ablation.rv_per_layer.values())
            
            if len(baseline_rvs) != len(ablated_rvs):
                logger.warning(f"Layer count mismatch for layer {ablation.layer_idx}")
                continue
            
            # Compute Cohen's d
            mean_base = np.mean(baseline_rvs)
            mean_ablated = np.mean(ablated_rvs)
            std_base = np.std(baseline_rvs, ddof=1)
            std_ablated = np.std(ablated_rvs, ddof=1)
            
            n = len(baseline_rvs)
            pooled_std = np.sqrt((std_base**2 + std_ablated**2) / 2)
            
            if pooled_std > 0:
                cohens_d = (mean_base - mean_ablated) / pooled_std
            else:
                cohens_d = 0.0
            
            # Paired t-test for significance
            if n > 1:
                t_stat, p_value = stats.ttest_rel(baseline_rvs, ablated_rvs)
            else:
                p_value = 1.0
            
            # Percent change
            if mean_base != 0:
                pct_change = ((mean_ablated - mean_base) / mean_base) * 100
            else:
                pct_change = 0.0
            
            # Interpretation
            if cohens_d > 1.0 and p_value < 0.05:
                interpretation = "Critical - layer is essential"
            elif cohens_d > 0.5 and p_value < 0.05:
                interpretation = "Important - layer contributes significantly"
            elif cohens_d > 0.2:
                interpretation = "Moderate - layer has some impact"
            else:
                interpretation = "Dispensable - layer may be prunable"
            
            necessity_scores[layer_key] = {
                "d": float(cohens_d),
                "p": float(p_value),
                "rv_baseline": float(mean_base),
                "rv_ablated": float(mean_ablated),
                "rv_change_pct": float(pct_change),
                "layer_idx": ablation.layer_idx,
                "interpretation": interpretation
            }
        
        return necessity_scores
    
    def _bootstrap_necessity(
        self, 
        baseline_rvs: List[float], 
        ablated_rvs: List[float]
    ) -> Tuple[float, float]:
        """
        Bootstrap confidence intervals for necessity scores.
        
        Returns:
            (mean_d, std_d) from bootstrap samples
        """
        if len(baseline_rvs) != len(ablated_rvs) or len(baseline_rvs) < 2:
            return 0.0, 0.0
        
        bootstrap_ds = []
        n = len(baseline_rvs)
        
        rng = np.random.RandomState(self.random_seed)
        
        for _ in range(self.n_bootstrap):
            # Resample indices
            indices = rng.choice(n, size=n, replace=True)
            
            b_base = [baseline_rvs[i] for i in indices]
            b_ablated = [ablated_rvs[i] for i in indices]
            
            mean_base = np.mean(b_base)
            mean_ablated = np.mean(b_ablated)
            std_base = np.std(b_base, ddof=1)
            std_ablated = np.std(b_ablated, ddof=1)
            
            pooled_std = np.sqrt((std_base**2 + std_ablated**2) / 2)
            if pooled_std > 0:
                d = (mean_base - mean_ablated) / pooled_std
                bootstrap_ds.append(d)
        
        return float(np.mean(bootstrap_ds)), float(np.std(bootstrap_ds))
    
    def run(
        self,
        test_prompts: Optional[List[str]] = None,
        max_length: int = 50,
        layers_to_ablate: Optional[List[int]] = None,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run MLP ablation experiment.
        
        Args:
            test_prompts: List of test prompts
            max_length: Maximum sequence length
            layers_to_ablate: Specific layers to ablate (None = all layers)
            save_results: Whether to save results
        
        Returns:
            Dictionary with necessity_scores, baseline, ablations, hardware_info.
        """
        if test_prompts is None:
            test_prompts = [
                "The cat sat on the mat",
                "In 1492, Columbus sailed",
                "Machine learning is a subset"
            ]
        
        logger.info(f"Starting MLPAblator for {self.model_name}")
        logger.info(f"Ablation mode: {self.ablation_mode}")
        
        # Load model
        self._load_model()
        
        if self.smoke_test:
            test_prompts = test_prompts[:1]
            max_length = 10
            if layers_to_ablate is None:
                layers_to_ablate = [0, self.num_layers // 2, self.num_layers - 1]
        
        # Prepare inputs
        all_input_ids = []
        for prompt in test_prompts:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=max_length
            )
            all_input_ids.append(inputs['input_ids'])
        
        input_ids = torch.cat(all_input_ids, dim=0).to(self.device)
        
        # Determine layers to ablate
        if layers_to_ablate is None:
            layers_to_ablate = list(range(self.num_layers))
        
        # Baseline measurement
        self.baseline_results = self._measure_rv_baseline(input_ids)
        logger.info(f"Baseline R_V: {self.baseline_results.rv_mean:.2f}")
        
        # Ablation measurements
        self.ablation_results = []
        for layer_idx in layers_to_ablate:
            result = self._measure_rv_with_ablation(input_ids, layer_idx)
            self.ablation_results.append(result)
            
            if result.error:
                logger.warning(f"Layer {layer_idx} ablation failed: {result.error}")
            else:
                logger.info(f"Layer {layer_idx} ablated: R_V = {result.rv_mean:.2f}")
        
        # Compute necessity scores
        logger.info("Computing necessity scores...")
        necessity_scores = self._compute_necessity_scores()
        
        # Compile results
        results = {
            "model_name": self.model_name,
            "ablation_mode": self.ablation_mode,
            "num_layers": self.num_layers,
            "baseline": {
                "rv_mean": self.baseline_results.rv_mean,
                "rv_per_layer": self.baseline_results.rv_per_layer,
                "time_sec": self.baseline_results.computation_time_sec
            },
            "ablations": [
                {
                    "layer_idx": r.layer_idx,
                    "rv_mean": r.rv_mean,
                    "time_sec": r.computation_time_sec,
                    "error": r.error
                }
                for r in self.ablation_results
            ],
            "necessity_scores": necessity_scores,
            "hardware_info": self.hardware_info,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add bootstrap confidence intervals if enabled
        if self.n_bootstrap > 0:
            results["bootstrap"] = {}
            baseline_rvs = list(self.baseline_results.rv_per_layer.values())
            
            for ablation in self.ablation_results:
                if ablation.error:
                    continue
                
                ablated_rvs = list(ablation.rv_per_layer.values())
                mean_d, std_d = self._bootstrap_necessity(baseline_rvs, ablated_rvs)
                
                layer_key = f"layer_{ablation.layer_idx}"
                if layer_key in necessity_scores:
                    necessity_scores[layer_key]["d_bootstrap_mean"] = mean_d
                    necessity_scores[layer_key]["d_bootstrap_std"] = std_d
                    necessity_scores[layer_key]["d_ci95"] = [mean_d - 1.96*std_d, mean_d + 1.96*std_d]
        
        # Save results
        if save_results and self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.output_dir / f"mlp_ablation_{self.model_name.replace('/', '_')}_{datetime.now():%Y%m%d_%H%M%S}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        
        # Summary
        critical_layers = [k for k, v in necessity_scores.items() if v['d'] > 1.0 and v['p'] < 0.05]
        logger.info(f"Ablator complete. Critical layers: {len(critical_layers)}/{len(necessity_scores)}")
        
        return results
    
    def get_summary(self) -> str:
        """Get a text summary of results."""
        if self.baseline_results is None:
            return "No results. Run the ablator first."
        
        lines = [
            "=" * 60,
            f"MLP Ablation Summary: {self.model_name}",
            f"Ablation Mode: {self.ablation_mode}",
            "=" * 60,
            ""
        ]
        
        lines.append(f"Baseline R_V: {self.baseline_results.rv_mean:.2f}")
        lines.append("")
        
        necessity = self._compute_necessity_scores()
        
        # Sort by effect size
        sorted_layers = sorted(
            necessity.items(),
            key=lambda x: x[1]['d'],
            reverse=True
        )
        
        lines.append("Layer Necessity Scores (sorted by effect size):")
        lines.append("-" * 50)
        
        for layer_key, score in sorted_layers:
            sig = "***" if score['p'] < 0.001 else "**" if score['p'] < 0.01 else "*" if score['p'] < 0.05 else ""
            lines.append(
                f"{layer_key:12s}: d={score['d']:6.2f}, p={score['p']:.4f} {sig:3s} "
                f"({score['interpretation']})"
            )
        
        return "\n".join(lines)
    
    def get_prunable_layers(self, threshold_d: float = 0.5, threshold_p: float = 0.05) -> List[int]:
        """
        Identify potentially prunable layers based on necessity thresholds.
        
        Args:
            threshold_d: Maximum Cohen's d for prunability
            threshold_p: Minimum p-value for prunability
        
        Returns:
            List of layer indices that may be prunable
        """
        necessity = self._compute_necessity_scores()
        prunable = []
        
        for layer_key, score in necessity.items():
            if score['d'] < threshold_d and score['p'] > threshold_p:
                prunable.append(score['layer_idx'])
        
        return sorted(prunable)


def smoke_test():
    """Run a quick smoke test of the ablator."""
    print("Running MLPAblator smoke test...")
    
    ablator = MLPAblator(
        model_name="gpt2",
        smoke_test=True,
        device="cpu",
        ablation_mode="zero"
    )
    
    results = ablator.run(
        test_prompts=["The cat"],
        max_length=5,
        layers_to_ablate=[0, 11],  # Test first and last layers
        save_results=False
    )
    
    print(ablator.get_summary())
    
    success = (
        results['baseline']['rv_mean'] > 0 and
        len(results['ablations']) == 2 and
        len(results['necessity_scores']) > 0
    )
    
    print(f"\nSmoke test {'PASSED' if success else 'FAILED'}!")
    return results


if __name__ == "__main__":
    smoke_test()
