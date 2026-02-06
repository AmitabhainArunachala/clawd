"""
Cross-Architecture R_V Measurement Suite
========================================

Orchestrates R_V measurements across multiple model architectures using
rv_toolkit for computation, with meta-analysis including heterogeneity
assessment (I²) and forest plot data generation.

Example:
    >>> from mi_experimenter.experiments.cross_arch_suite import CrossArchitectureSuite
    >>> suite = CrossArchitectureSuite(["gpt2", "mistralai/Mistral-7B-v0.1"])
    >>> results = suite.run(test_prompts=["The cat sat on the"])
    >>> print(f"I² (heterogeneity): {results['heterogeneity']['i_squared']:.2f}%")
"""

# Ensure local rv_toolkit is used
import sys
from pathlib import Path
_rv_toolkit_path = str(Path(__file__).parent.parent.parent / "rv_toolkit")
if _rv_toolkit_path not in sys.path:
    sys.path.insert(0, _rv_toolkit_path)

import torch
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
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

# Import rv_toolkit with proper path setup
import sys
from pathlib import Path
_rv_root = Path(__file__).parent.parent.parent.parent / "mech-interp-latent-lab-phase1" / "rv_toolkit"
if str(_rv_root) not in sys.path:
    sys.path.insert(0, str(_rv_root))

from rv_toolkit import compute_rv
# measure_rv is same as compute_rv in current version
measure_rv = compute_rv
# RVHookManager may not exist in current version - using activation hooks directly

# Import local model loader
# Fix relative import for standalone usage
try:
    from ..core.model_loader import ModelLoader
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.model_loader import ModelLoader

logger = logging.getLogger(__name__)


@dataclass
class ModelRVResult:
    """R_V measurement results for a single model."""
    model_name: str
    architecture: str
    rv_mean: float
    rv_per_layer: Dict[str, float]
    bottleneck_layer: Optional[str] = None
    num_layers: int = 0
    num_heads: int = 0
    hidden_size: int = 0
    num_params: int = 0
    computation_time_sec: float = 0.0
    error: Optional[str] = None


class CrossArchitectureSuite:
    """
    Orchestrates R_V measurements across multiple model architectures.
    
    Uses rv_toolkit for all R_V computation, then performs meta-analysis
    including effect sizes, heterogeneity (I²), and forest plot data.
    
    Args:
        model_names: List of HuggingFace model names or paths
        device: Device to run on ("cuda", "cpu", "auto")
        dtype: Data type for model loading
        smoke_test: If True, run minimal test with small batch
        random_seed: Random seed for determinism
    
    Example:
        >>> suite = CrossArchitectureSuite(
        ...     ["gpt2", "gpt2-medium", "mistralai/Mistral-7B-v0.1"],
        ...     smoke_test=False
        ... )
        >>> results = suite.run(test_prompts=["The cat sat on the"])
        >>> print(f"Heterogeneity I²: {results['heterogeneity']['i_squared']:.2f}%")
    """
    
    def __init__(
        self,
        model_names: List[str],
        device: str = "auto",
        dtype: str = "auto",
        smoke_test: bool = False,
        random_seed: int = 42,
        output_dir: Optional[str] = None
    ):
        self.model_names = model_names
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype
        self.smoke_test = smoke_test
        self.random_seed = random_seed
        self.output_dir = Path(output_dir) if output_dir else None
        
        self.model_results: List[ModelRVResult] = []
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
            info["gpu_count"] = torch.cuda.device_count()
            info["gpu_names"] = [torch.cuda.get_device_name(i) 
                                  for i in range(torch.cuda.device_count())]
            info["gpu_memory_gb"] = [
                torch.cuda.get_device_properties(i).total_memory / 1e9 
                for i in range(torch.cuda.device_count())
            ]
        
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count()
            info["ram_gb"] = psutil.virtual_memory().total / 1e9
        except ImportError:
            pass
        
        return info
    
    def _measure_single_model(
        self,
        model_name: str,
        test_prompts: List[str],
        max_length: int = 50
    ) -> ModelRVResult:
        """Measure R_V for a single model using rv_toolkit."""
        import time
        start_time = time.time()
        
        logger.info(f"Loading model: {model_name}")
        
        try:
            # Load model
            loader = ModelLoader(
                model_name=model_name,
                device=self.device,
                dtype=self.dtype,
                trust_remote_code=True
            )
            model, tokenizer = loader.load()
            
            # Prepare test inputs
            if self.smoke_test:
                test_prompts = test_prompts[:1]
                max_length = 10
            
            all_input_ids = []
            for prompt in test_prompts:
                inputs = tokenizer(
                    prompt, 
                    return_tensors="pt", 
                    truncation=True, 
                    max_length=max_length
                )
                all_input_ids.append(inputs['input_ids'])
            
            input_ids = torch.cat(all_input_ids, dim=0).to(self.device)
            
            # Use rv_toolkit for R_V measurement
            num_heads = loader.num_heads if loader.num_heads > 0 else None
            rv_summary = quick_rv_measure(
                model, 
                input_ids, 
                num_heads=num_heads
            )
            
            rv_per_layer = rv_summary.get('per_layer', {})
            rv_mean = rv_summary.get('mean_rv', 0.0)
            bottleneck_layer = rv_summary.get('bottleneck_layer')
            
            computation_time = time.time() - start_time
            model_info = loader.get_model_info()
            
            return ModelRVResult(
                model_name=model_name,
                architecture=loader.architecture,
                rv_mean=rv_mean,
                rv_per_layer=rv_per_layer,
                bottleneck_layer=bottleneck_layer,
                num_layers=loader.num_layers,
                num_heads=loader.num_heads,
                hidden_size=loader.hidden_size,
                num_params=model_info.get('num_parameters', 0),
                computation_time_sec=computation_time
            )
            
        except Exception as e:
            logger.error(f"Failed to measure {model_name}: {e}")
            return ModelRVResult(
                model_name=model_name,
                architecture="unknown",
                rv_mean=0.0,
                rv_per_layer={},
                error=str(e)
            )
    
    def _compute_effect_sizes(self) -> Dict[str, Dict[str, float]]:
        """Compute Cohen's d effect sizes between model pairs."""
        effect_sizes = {}
        valid_results = [r for r in self.model_results if r.error is None]
        
        for i, model_a in enumerate(valid_results):
            for j, model_b in enumerate(valid_results):
                if i >= j:
                    continue
                
                common_layers = set(model_a.rv_per_layer.keys()) & set(model_b.rv_per_layer.keys())
                if not common_layers:
                    continue
                
                values_a = [model_a.rv_per_layer[l] for l in common_layers]
                values_b = [model_b.rv_per_layer[l] for l in common_layers]
                
                mean_a, mean_b = np.mean(values_a), np.mean(values_b)
                std_a, std_b = np.std(values_a, ddof=1), np.std(values_b, ddof=1)
                n_a, n_b = len(values_a), len(values_b)
                
                pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2))
                cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0.0
                
                comparison_key = f"{model_a.model_name}_vs_{model_b.model_name}"
                effect_sizes[comparison_key] = {
                    "cohens_d": float(cohens_d),
                    "mean_diff": float(mean_a - mean_b),
                    "mean_a": float(mean_a),
                    "mean_b": float(mean_b),
                    "pooled_std": float(pooled_std)
                }
        
        return effect_sizes
    
    def _compute_heterogeneity(self) -> Dict[str, Any]:
        """
        Compute Cochran's Q and I² heterogeneity statistics.
        
        I² interpretation:
        - 0-25%: Low heterogeneity
        - 25-50%: Moderate heterogeneity
        - 50-75%: Substantial heterogeneity
        - 75-100%: Considerable heterogeneity
        """
        valid_results = [r for r in self.model_results if r.error is None]
        
        if len(valid_results) < 2:
            return {"i_squared": 0.0, "interpretation": "Insufficient data"}
        
        # Collect all per-layer R_V values
        all_values = []
        for result in valid_results:
            for rv_value in result.rv_per_layer.values():
                if np.isfinite(rv_value):
                    all_values.append(rv_value)
        
        if len(all_values) < 2:
            return {"i_squared": 0.0, "interpretation": "No valid values"}
        
        values_array = np.array(all_values)
        
        # Simple fixed-effect mean
        mean_rv = np.mean(values_array)
        
        # Cochran's Q statistic
        q_statistic = np.sum((values_array - mean_rv) ** 2)
        df = len(all_values) - 1
        
        # I² statistic
        if q_statistic > 0:
            i_squared = max(0, (q_statistic - df) / q_statistic) * 100
        else:
            i_squared = 0.0
        
        # Chi-square p-value
        p_value = 1 - stats.chi2.cdf(q_statistic, df) if df > 0 else 1.0
        
        # Interpretation
        if i_squared < 25:
            interpretation = "Low heterogeneity"
        elif i_squared < 50:
            interpretation = "Moderate heterogeneity"
        elif i_squared < 75:
            interpretation = "Substantial heterogeneity"
        else:
            interpretation = "Considerable heterogeneity"
        
        return {
            "i_squared": float(i_squared),
            "q_statistic": float(q_statistic),
            "df": int(df),
            "p_value": float(p_value),
            "mean_rv": float(mean_rv),
            "n_layers": len(all_values),
            "interpretation": interpretation
        }
    
    def _generate_forest_data(self) -> Dict[str, Any]:
        """Generate data for forest plot visualization."""
        valid_results = [r for r in self.model_results if r.error is None]
        
        forest_data = {
            "models": [],
            "rv_values": [],
            "ci_lower": [],
            "ci_upper": [],
            "bottlenecks": {}
        }
        
        for result in valid_results:
            rv_values = [v for v in result.rv_per_layer.values() if np.isfinite(v)]
            
            if rv_values:
                mean_rv = np.mean(rv_values)
                std_rv = np.std(rv_values, ddof=1)
                n = len(rv_values)
                sem = std_rv / np.sqrt(n)
                t_value = stats.t.ppf(0.975, n - 1) if n > 1 else 1.96
                
                forest_data["models"].append(result.model_name)
                forest_data["rv_values"].append(float(mean_rv))
                forest_data["ci_lower"].append(float(mean_rv - t_value * sem))
                forest_data["ci_upper"].append(float(mean_rv + t_value * sem))
            
            if result.bottleneck_layer:
                forest_data["bottlenecks"][result.model_name] = {
                    "layer": result.bottleneck_layer,
                    "rv": result.rv_per_layer.get(result.bottleneck_layer, 0)
                }
        
        # Per-layer data across models
        all_layers = set()
        for result in valid_results:
            all_layers.update(result.rv_per_layer.keys())
        
        forest_data["layer_comparison"] = []
        for layer in sorted(all_layers):
            layer_values = [
                result.rv_per_layer[layer] 
                for result in valid_results 
                if layer in result.rv_per_layer and np.isfinite(result.rv_per_layer[layer])
            ]
            if layer_values:
                forest_data["layer_comparison"].append({
                    "layer": layer,
                    "mean": float(np.mean(layer_values)),
                    "std": float(np.std(layer_values, ddof=1)),
                    "min": float(np.min(layer_values)),
                    "max": float(np.max(layer_values)),
                    "n": len(layer_values)
                })
        
        return forest_data
    
    def run(
        self,
        test_prompts: Optional[List[str]] = None,
        max_length: int = 50,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run the cross-architecture R_V measurement suite.
        
        Args:
            test_prompts: List of test prompts. Uses defaults if None.
            max_length: Maximum sequence length.
            save_results: Whether to save results to output_dir.
        
        Returns:
            Dictionary with model_results, effect_sizes, heterogeneity, forest_data.
        """
        if test_prompts is None:
            test_prompts = [
                "The cat sat on the",
                "In 1492, Christopher Columbus",
                "The theory of relativity states that",
                "Machine learning algorithms work by"
            ]
        
        logger.info(f"Starting CrossArchitectureSuite for {len(self.model_names)} models")
        logger.info(f"Smoke test: {self.smoke_test}")
        
        # Measure each model using rv_toolkit
        self.model_results = []
        for model_name in self.model_names:
            result = self._measure_single_model(model_name, test_prompts, max_length)
            self.model_results.append(result)
            
            if result.error:
                logger.warning(f"Model {model_name} failed: {result.error}")
            else:
                logger.info(f"{model_name}: mean R_V = {result.rv_mean:.2f}")
        
        # Meta-analysis
        effect_sizes = self._compute_effect_sizes()
        heterogeneity = self._compute_heterogeneity()
        forest_data = self._generate_forest_data()
        
        results = {
            "model_results": [
                {
                    "model_name": r.model_name,
                    "architecture": r.architecture,
                    "rv_mean": r.rv_mean,
                    "rv_per_layer": r.rv_per_layer,
                    "bottleneck_layer": r.bottleneck_layer,
                    "num_layers": r.num_layers,
                    "num_params": r.num_params,
                    "error": r.error
                }
                for r in self.model_results
            ],
            "effect_sizes": effect_sizes,
            "heterogeneity": heterogeneity,
            "forest_data": forest_data,
            "hardware_info": self.hardware_info,
            "timestamp": datetime.now().isoformat()
        }
        
        if save_results and self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.output_dir / f"cross_arch_{datetime.now():%Y%m%d_%H%M%S}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        
        logger.info(f"Complete. I² = {heterogeneity['i_squared']:.2f}%")
        
        return results
    
    def get_summary(self) -> str:
        """Get a text summary of results."""
        if not self.model_results:
            return "No results. Run the suite first."
        
        lines = ["=" * 60, "Cross-Architecture R_V Summary", "=" * 60, ""]
        
        for result in self.model_results:
            lines.append(f"Model: {result.model_name}")
            if result.error:
                lines.append(f"  ERROR: {result.error}")
            else:
                lines.append(f"  Mean R_V: {result.rv_mean:.2f}")
                lines.append(f"  Bottleneck: {result.bottleneck_layer}")
                lines.append(f"  Layers: {result.num_layers}, Params: {result.num_params / 1e6:.1f}M")
            lines.append("")
        
        return "\n".join(lines)


def smoke_test():
    """Run a quick smoke test."""
    print("Running CrossArchitectureSuite smoke test...")
    
    suite = CrossArchitectureSuite(
        model_names=["gpt2"],
        smoke_test=True,
        device="cpu"
    )
    
    results = suite.run(
        test_prompts=["The cat"],
        max_length=5,
        save_results=False
    )
    
    print(suite.get_summary())
    print(f"\nHeterogeneity: {results['heterogeneity']['i_squared']:.2f}%")
    print("\nSmoke test PASSED!" if not any(r.get('error') for r in results['model_results']) else "FAILED!")
    
    return results


if __name__ == "__main__":
    smoke_test()
