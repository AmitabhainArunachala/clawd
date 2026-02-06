"""
R_V Causal Validator - ORCHESTRATION LAYER
============================================

Wrapper around rv_toolkit that orchestrates 4-control activation patching
experiments with cross-architecture support and statistical validation.

This module does NOT reimplement core computation - it wraps:
- rv_toolkit.patching.ActivationPatcher
- rv_toolkit.metrics.compute_participation_ratio  
- rv_toolkit.compute_rv

Responsibilities:
- Experiment orchestration (n_pairs, controls, randomization)
- Hardware logging & determinism setup
- Statistical testing (Cohen's d, p-values, transfer efficiency)
- Result aggregation and persistence

Example:
    >>> from mi_experimenter import RVCausalValidator
    >>> validator = RVCausalValidator(
    ...     model_name="mistralai/Mistral-7B-v0.1",
    ...     target_layer=27,
    ...     controls=["random", "shuffled", "wrong_layer", "orthogonal"],
    ...     n_pairs=45
    ... )
    >>> results = validator.run()
    >>> print(f"Cohen's d: {results['cohens_d']:.3f}")
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from scipy import stats
import json
import logging

# Import from rv_toolkit (foundation layer)
try:
    from rv_toolkit import compute_rv
    from rv_toolkit.patching import ActivationPatcher
    from rv_toolkit.metrics import compute_participation_ratio
    from rv_toolkit.model_loader import load_model as rv_load_model
    from rv_toolkit.prompts import load_prompt_bank, generate_pairs
    RV_AVAILABLE = True
except ImportError:
    RV_AVAILABLE = False
    # Fallback stubs for type checking
    compute_rv = None
    ActivationPatcher = None
    compute_participation_ratio = None
    rv_load_model = None
    load_prompt_bank = None
    generate_pairs = None

logger = logging.getLogger(__name__)


@dataclass
class HardwareInfo:
    """Hardware configuration logging for reproducibility."""
    gpu_model: str = "unknown"
    cuda_version: str = "unknown"
    cuda_available: bool = False
    device_name: str = "cpu"
    precision: str = "float32"
    num_gpus: int = 0
    gpu_memory_gb: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gpu_model": self.gpu_model,
            "cuda_version": self.cuda_version,
            "cuda_available": self.cuda_available,
            "device_name": self.device_name,
            "precision": self.precision,
            "num_gpus": self.num_gpus,
            "gpu_memory_gb": self.gpu_memory_gb,
        }


@dataclass 
class ValidationConfig:
    """Configuration for R_V causal validation."""
    model_name: str
    target_layer: int = 27
    early_layer: int = 5
    wrong_layer: int = 21
    window_size: int = 16
    n_pairs: int = 45
    controls: List[str] = field(default_factory=lambda: ["random", "shuffled", "wrong_layer", "orthogonal"])
    device: str = "auto"
    dtype: str = "auto"
    random_seed: int = 42
    max_length: int = 512
    smoke_test: bool = False
    save_results: bool = True
    output_dir: str = "./results"
    
    def __post_init__(self):
        if self.smoke_test:
            self.n_pairs = 3
            self.model_name = "gpt2"


@dataclass
class ValidationResults:
    """Results from R_V causal validation."""
    # Main statistics
    cohens_d: float = 0.0
    p_value: float = 1.0
    transfer_efficiency: float = 0.0
    controls_passed: Dict[str, bool] = field(default_factory=dict)
    
    # Detailed metrics
    n_pairs: int = 0
    rv_recursive_mean: float = 0.0
    rv_baseline_mean: float = 0.0
    rv_patched_mean: float = 0.0
    
    # Control results
    control_deltas: Dict[str, float] = field(default_factory=dict)
    control_p_values: Dict[str, float] = field(default_factory=dict)
    
    # Hardware & config
    hardware_info: Optional[HardwareInfo] = None
    config: Optional[ValidationConfig] = None
    
    # Raw data
    raw_data: Optional[pd.DataFrame] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cohens_d": self.cohens_d,
            "p_value": self.p_value,
            "transfer_efficiency": self.transfer_efficiency,
            "controls_passed": self.controls_passed,
            "n_pairs": self.n_pairs,
            "rv_recursive_mean": self.rv_recursive_mean,
            "rv_baseline_mean": self.rv_baseline_mean,
            "rv_patched_mean": self.rv_patched_mean,
            "control_deltas": self.control_deltas,
            "control_p_values": self.control_p_values,
            "hardware_info": self.hardware_info.to_dict() if self.hardware_info else None,
            "timestamp": self.timestamp,
        }
    
    def summary(self) -> str:
        """Generate a text summary of results."""
        lines = [
            "=" * 70,
            "R_V CAUSAL VALIDATION RESULTS",
            "=" * 70,
            f"Model: {self.config.model_name if self.config else 'unknown'}",
            f"Target Layer: {self.config.target_layer if self.config else 'unknown'}",
            f"N pairs: {self.n_pairs}",
            "",
            "Main Effect:",
            f"  Cohen's d: {self.cohens_d:.3f}",
            f"  p-value: {self.p_value:.6f}",
            f"  Transfer efficiency: {self.transfer_efficiency:.1f}%",
            "",
            "Controls Passed:",
        ]
        for control, passed in self.controls_passed.items():
            lines.append(f"  {control}: {'✓' if passed else '✗'}")
        
        all_passed = all(self.controls_passed.values()) if self.controls_passed else False
        status = "VALIDATED ✓" if all_passed and self.p_value < 0.001 else "NOT VALIDATED ✗"
        lines.extend([
            "",
            f"Overall: {status}",
            "=" * 70,
        ])
        return "\n".join(lines)


class RVCausalValidator:
    """
    R_V Causal Validator - ORCHESTRATION LAYER
    
    Wraps rv_toolkit.patching.ActivationPatcher to run 4-control
    activation patching experiments with proper statistical testing.
    
    This class does NOT implement:
    - Activation patching (uses rv_toolkit)
    - PR/R_V computation (uses rv_toolkit)
    - Model loading (uses rv_toolkit)
    
    This class DOES implement:
    - Experiment orchestration (pairing, controls, sequencing)
    - Statistical aggregation (Cohen's d, transfer efficiency)
    - Hardware logging & determinism
    - Result persistence
    
    Args:
        model_name: HuggingFace model name (e.g., "mistralai/Mistral-7B-v0.1")
        target_layer: Layer to patch (default: 27 for Mistral-7B)
        controls: List of control types to run (default: all 4)
        n_pairs: Number of prompt pairs to test (default: 45)
        **kwargs: Additional configuration options
    
    Example:
        >>> validator = RVCausalValidator(
        ...     "mistralai/Mistral-7B-v0.1",
        ...     target_layer=27,
        ...     n_pairs=45
        ... )
        >>> results = validator.run()
    """
    
    def __init__(
        self,
        model_name: str,
        target_layer: int = 27,
        controls: Optional[List[str]] = None,
        n_pairs: int = 45,
        **kwargs
    ):
        if not RV_AVAILABLE:
            raise ImportError(
                "rv_toolkit not available. "
                "Install from: ~/clawd/rv_toolkit/"
            )
        
        self.config = ValidationConfig(
            model_name=model_name,
            target_layer=target_layer,
            controls=controls or ["random", "shuffled", "wrong_layer", "orthogonal"],
            n_pairs=n_pairs,
            **kwargs
        )
        
        self.model = None
        self.tokenizer = None
        self.patcher = None
        self.hardware_info = None
        
        # Setup determinism
        self._setup_determinism()
        
    def _setup_determinism(self):
        """Enable deterministic behavior for reproducibility."""
        torch.manual_seed(self.config.random_seed)
        np.random.seed(self.config.random_seed)
        
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.config.random_seed)
            torch.use_deterministic_algorithms(True, warn_only=True)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            
    def _log_hardware(self) -> HardwareInfo:
        """Log hardware configuration."""
        info = HardwareInfo()
        
        info.cuda_available = torch.cuda.is_available()
        if info.cuda_available:
            info.cuda_version = torch.version.cuda or "unknown"
            info.num_gpus = torch.cuda.device_count()
            info.gpu_model = torch.cuda.get_device_name(0)
            info.device_name = f"cuda:0 ({info.gpu_model})"
            
            try:
                props = torch.cuda.get_device_properties(0)
                info.gpu_memory_gb = props.total_memory / (1024**3)
            except:
                pass
        else:
            info.device_name = "cpu"
        
        if self.model is not None:
            dtype_map = {
                torch.float16: "float16",
                torch.bfloat16: "bfloat16", 
                torch.float32: "float32",
            }
            info.precision = dtype_map.get(next(self.model.parameters()).dtype, "unknown")
        
        self.hardware_info = info
        return info
    
    def _load_model(self):
        """Load model using rv_toolkit."""
        logger.info(f"Loading model via rv_toolkit: {self.config.model_name}")
        
        self.model, self.tokenizer = rv_load_model(
            self.config.model_name,
            device=self.config.device,
            dtype=self.config.dtype,
        )
        
        # Initialize patcher from rv_toolkit
        self.patcher = ActivationPatcher(self.model, self.tokenizer)
        self._log_hardware()
        
        logger.info(f"Model loaded: {self.hardware_info.gpu_model}")
        
    def _compute_rv_metrics(self, v_tensor: torch.Tensor) -> Tuple[float, float]:
        """
        Compute R_V metrics using rv_toolkit.
        
        Wraps rv_toolkit.metrics.compute_participation_ratio
        """
        if v_tensor is None or compute_participation_ratio is None:
            return np.nan, np.nan
        
        # Remove batch dimension if present
        if v_tensor.dim() == 3:
            v_tensor = v_tensor[0]
        
        T, D = v_tensor.shape
        W = min(self.config.window_size, T)
        
        if W < 2:
            return np.nan, np.nan
        
        v_window = v_tensor[-W:, :].float()
        
        # Use rv_toolkit for PR computation
        try:
            pr = compute_participation_ratio(v_window)
            
            # Compute effective rank (SVD-based)
            U, S, Vt = torch.linalg.svd(v_window.T, full_matrices=False)
            S_np = S.cpu().numpy()
            eff_rank = np.sum(S_np / (S_np[0] + 1e-10))
            
            return float(eff_rank), float(pr)
        except Exception as e:
            logger.warning(f"R_V computation failed: {e}")
            return np.nan, np.nan
    
    def _get_v_activations(self, text: str, layers: List[int]) -> Dict[int, torch.Tensor]:
        """
        Get V activations using rv_toolkit.ActivationPatcher.
        """
        if self.patcher is None:
            raise RuntimeError("Patcher not initialized")
        
        # Use rv_toolkit patcher to capture activations
        hook_points = [f"blocks.{layer}.hook_v_proj" for layer in layers]
        
        activations = self.patcher.capture(
            text=text,
            hook_points=hook_points,
            max_length=self.config.max_length
        )
        
        # Convert to layer-indexed dict
        result = {}
        for layer in layers:
            hook_point = f"blocks.{layer}.hook_v_proj"
            if hook_point in activations:
                result[layer] = activations[hook_point]
        
        return result
    
    def _create_control_patch(
        self, 
        source_v: torch.Tensor, 
        control_type: str,
        wrong_layer_v: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Create control patch of specified type."""
        if source_v is None:
            return None
        
        if control_type == "random":
            rand_v = torch.randn_like(source_v)
            norm_ratio = source_v.norm() / (rand_v.norm() + 1e-10)
            return rand_v * norm_ratio
        
        elif control_type == "shuffled":
            perm = torch.randperm(source_v.shape[0])
            return source_v[perm, :]
        
        elif control_type == "wrong_layer":
            if wrong_layer_v is not None:
                return wrong_layer_v
            else:
                return self._create_control_patch(source_v, "random")
        
        elif control_type == "orthogonal":
            mean_dir = source_v.mean(dim=0, keepdim=True)
            mean_dir = mean_dir / (mean_dir.norm() + 1e-10)
            projections = (source_v * mean_dir).sum(dim=-1, keepdim=True)
            orthogonal_v = source_v - projections * mean_dir
            norm_ratio = source_v.norm() / (orthogonal_v.norm() + 1e-10)
            return orthogonal_v * norm_ratio
        
        else:
            raise ValueError(f"Unknown control type: {control_type}")
    
    def _run_patched_forward(
        self,
        baseline_text: str,
        patch_v: torch.Tensor,
        target_layer: int,
        early_layer: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Run patched forward using rv_toolkit.ActivationPatcher.
        """
        if self.patcher is None or patch_v is None:
            return None, None
        
        # Use rv_toolkit patcher
        v_early, v_target = self.patcher.patch_and_capture(
            target_text=baseline_text,
            patch_value=patch_v,
            patch_layer=target_layer,
            capture_layer=early_layer,
            component="v_proj",
            window_size=self.config.window_size,
            max_length=self.config.max_length
        )
        
        return v_early, v_target
    
    def _generate_prompt_pairs(self) -> List[Tuple[str, str, str, str]]:
        """Generate prompt pairs using rv_toolkit or built-in."""
        if self.config.smoke_test:
            # Use built-in smoke test prompts
            prompts = {
                "rec1": {"text": "Consider a fractal where each level contains self-similar patterns recursively.", "group": "L5_refined"},
                "rec2": {"text": "To solve this recursively, define the base case then build up.", "group": "L4_full"},
                "rec3": {"text": "Recursion is self-reference creating infinite depth in finite space.", "group": "L3_deeper"},
                "base1": {"text": "The weather today is sunny with a few clouds.", "group": "long_control"},
                "base2": {"text": "Paris is the capital of France known for the Eiffel Tower.", "group": "baseline_creative"},
                "base3": {"text": "Calculate rectangle area by multiplying length by width.", "group": "baseline_math"},
            }
            return [
                (prompts["rec1"]["text"], prompts["base1"]["text"], "L5_refined", "long_control"),
                (prompts["rec2"]["text"], prompts["base2"]["text"], "L4_full", "baseline_creative"),
                (prompts["rec3"]["text"], prompts["base3"]["text"], "L3_deeper", "baseline_math"),
            ][:self.config.n_pairs]
        
        # Use rv_toolkit prompt loading if available
        if load_prompt_bank is not None and generate_pairs is not None:
            prompt_bank = load_prompt_bank()
            pairs = generate_pairs(
                prompt_bank, 
                n_pairs=self.config.n_pairs,
                random_seed=self.config.random_seed
            )
            return pairs
        
        # Fallback to smoke prompts
        return self._generate_prompt_pairs()
    
    def _compute_cohens_d(self, values: np.ndarray) -> float:
        """Compute Cohen's d for one-sample t-test against 0."""
        if len(values) == 0 or np.std(values) == 0:
            return 0.0
        return float(np.mean(values) / np.std(values))
    
    def run(self) -> ValidationResults:
        """
        Run the full R_V causal validation experiment.
        
        Returns:
            ValidationResults with cohens_d, p_value, transfer_efficiency, controls_passed
        """
        logger.info("=" * 70)
        logger.info("R_V CAUSAL VALIDATION - ORCHESTRATION LAYER")
        logger.info("=" * 70)
        
        if not RV_AVAILABLE:
            raise RuntimeError("rv_toolkit required but not available")
        
        # Load model via rv_toolkit
        if self.model is None:
            self._load_model()
        
        logger.info(f"Target layer: {self.config.target_layer}")
        logger.info(f"Early layer: {self.config.early_layer}")
        logger.info(f"Window size: {self.config.window_size}")
        logger.info(f"N pairs: {self.config.n_pairs}")
        logger.info(f"Controls: {self.config.controls}")
        
        # Generate prompt pairs
        pairs = self._generate_prompt_pairs()
        logger.info(f"Testing {len(pairs)} pairs...")
        
        results_list = []
        
        for idx, (rec_text, base_text, rec_group, base_group) in enumerate(pairs):
            logger.info(f"Processing pair {idx+1}/{len(pairs)}...")
            
            try:
                # 1. Get V activations from recursive text
                rec_vs = self._get_v_activations(rec_text, 
                    [self.config.early_layer, self.config.target_layer])
                v_early_rec = rec_vs.get(self.config.early_layer)
                v_target_rec = rec_vs.get(self.config.target_layer)
                
                # 2. Get V activations from baseline text
                base_vs = self._get_v_activations(base_text,
                    [self.config.early_layer, self.config.target_layer])
                v_early_base = base_vs.get(self.config.early_layer)
                v_target_base = base_vs.get(self.config.target_layer)
                
                # 3. Get wrong layer activations for control
                v_wrong = None
                if "wrong_layer" in self.config.controls:
                    wrong_vs = self._get_v_activations(rec_text, [self.config.wrong_layer])
                    v_wrong = wrong_vs.get(self.config.wrong_layer)
                
                # Compute metrics
                _, pr5_rec = self._compute_rv_metrics(v_early_rec)
                _, pr27_rec = self._compute_rv_metrics(v_target_rec)
                _, pr5_base = self._compute_rv_metrics(v_early_base)
                _, pr27_base = self._compute_rv_metrics(v_target_base)
                
                # 4. MAIN: Patch with recursive V
                v5_patch_main, v27_patch_main = self._run_patched_forward(
                    base_text, 
                    v_target_rec[0] if v_target_rec is not None else None,
                    self.config.target_layer, 
                    self.config.early_layer
                )
                _, pr27_patch = self._compute_rv_metrics(v27_patch_main)
                
                # Calculate R_V ratios
                rv_rec = pr27_rec / pr5_rec if pr5_rec > 0 else np.nan
                rv_base = pr27_base / pr5_base if pr5_base > 0 else np.nan
                rv_patch = pr27_patch / pr5_base if pr5_base > 0 else np.nan
                
                result = {
                    'pair_idx': idx,
                    'rec_group': rec_group,
                    'base_group': base_group,
                    'RV_recursive': rv_rec,
                    'RV_baseline': rv_base,
                    'RV_patch_main': rv_patch,
                    'delta_main': rv_patch - rv_base,
                }
                
                # 5. Run controls
                for control in self.config.controls:
                    patch_control = self._create_control_patch(
                        v_target_rec[0] if v_target_rec is not None else None,
                        control,
                        v_wrong[0] if v_wrong is not None else None
                    )
                    
                    v5_ctrl, v27_ctrl = self._run_patched_forward(
                        base_text, patch_control,
                        self.config.target_layer, 
                        self.config.early_layer
                    )
                    
                    _, pr27_ctrl = self._compute_rv_metrics(v27_ctrl)
                    rv_ctrl = pr27_ctrl / pr5_base if pr5_base > 0 else np.nan
                    
                    result[f'RV_patch_{control}'] = rv_ctrl
                    result[f'delta_{control}'] = rv_ctrl - rv_base
                
                results_list.append(result)
                
            except Exception as e:
                logger.warning(f"Error on pair {idx}: {e}")
                continue
        
        # Create DataFrame
        df = pd.DataFrame(results_list)
        
        if len(df) == 0:
            raise RuntimeError("No valid results collected")
        
        # Compute main statistics
        main_deltas = df['delta_main'].dropna().values
        cohens_d = self._compute_cohens_d(main_deltas)
        _, p_value = stats.ttest_1samp(main_deltas, 0, alternative='less')
        
        # Compute transfer efficiency
        rv_rec_mean = df['RV_recursive'].mean()
        rv_base_mean = df['RV_baseline'].mean()
        rv_patch_mean = df['RV_patch_main'].mean()
        
        gap = rv_base_mean - rv_rec_mean
        if gap != 0:
            transfer_efficiency = ((rv_patch_mean - rv_base_mean) / gap) * 100
        else:
            transfer_efficiency = 0.0
        
        # Test controls
        controls_passed = {}
        control_deltas = {}
        control_p_values = {}
        
        for control in self.config.controls:
            if f'delta_{control}' in df.columns:
                ctrl_deltas = df[f'delta_{control}'].dropna().values
                control_deltas[control] = float(np.mean(ctrl_deltas))
                
                if len(main_deltas) == len(ctrl_deltas) and len(main_deltas) > 1:
                    _, p_ctrl = stats.ttest_rel(main_deltas, ctrl_deltas)
                    control_p_values[control] = float(p_ctrl)
                    controls_passed[control] = np.mean(main_deltas) < np.mean(ctrl_deltas)
                else:
                    control_p_values[control] = 1.0
                    controls_passed[control] = False
        
        # Create results
        results = ValidationResults(
            cohens_d=cohens_d,
            p_value=float(p_value),
            transfer_efficiency=abs(transfer_efficiency),
            controls_passed=controls_passed,
            n_pairs=len(df),
            rv_recursive_mean=float(rv_rec_mean),
            rv_baseline_mean=float(rv_base_mean),
            rv_patched_mean=float(rv_patch_mean),
            control_deltas=control_deltas,
            control_p_values=control_p_values,
            hardware_info=self.hardware_info,
            config=self.config,
            raw_data=df,
        )
        
        # Save results
        if self.config.save_results:
            self._save_results(results, df)
        
        logger.info(results.summary())
        
        return results
    
    def _save_results(self, results: ValidationResults, df: pd.DataFrame):
        """Save results to disk."""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = self.config.model_name.replace("/", "_")
        
        # Save CSV
        csv_path = output_dir / f"rv_validation_{model_name}_L{self.config.target_layer}_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Results saved to: {csv_path}")
        
        # Save JSON summary
        json_path = output_dir / f"rv_validation_{model_name}_L{self.config.target_layer}_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(results.to_dict(), f, indent=2, default=str)
        logger.info(f"Summary saved to: {json_path}")


def smoke_test():
    """Run smoke test with GPT-2 and minimal pairs."""
    print("=" * 70)
    print("R_V CAUSAL VALIDATOR - SMOKE TEST (ORCHESTRATION LAYER)")
    print("=" * 70)
    print("Testing with GPT-2, n=3 pairs, 2 controls")
    print()
    
    if not RV_AVAILABLE:
        print("⚠️  rv_toolkit not available - install first")
        return None
    
    validator = RVCausalValidator(
        model_name="gpt2",
        target_layer=6,
        controls=["random", "shuffled"],
        n_pairs=3,
        smoke_test=True,
        save_results=True,
        output_dir="./smoke_test_results"
    )
    
    results = validator.run()
    
    print()
    print("=" * 70)
    print("SMOKE TEST COMPLETE")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    smoke_test()
