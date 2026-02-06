"""
test_imports.py - Verify all imports work correctly
====================================================

Tests that all modules in mi_experimenter and rv_toolkit can be imported.
Run with: PYTHONPATH="$HOME/clawd/skills:$HOME/clawd/skills/rv_toolkit" python -m pytest tests/test_imports.py -v
"""

import sys
import os
import unittest

# Ensure paths are set for imports
skills_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if skills_dir not in sys.path:
    sys.path.insert(0, skills_dir)
rv_toolkit_dir = os.path.join(os.path.dirname(skills_dir), 'rv_toolkit')
if rv_toolkit_dir not in sys.path:
    sys.path.insert(0, rv_toolkit_dir)


class TestRVToolkitImports(unittest.TestCase):
    """Test rv_toolkit imports (foundation layer)."""
    
    def test_measure_rv_import(self):
        """Test from rv_toolkit import measure_rv."""
        from rv_toolkit import measure_rv
        self.assertTrue(callable(measure_rv))
    
    def test_rv_core_functions(self):
        """Test all core R_V functions."""
        from rv_toolkit import compute_pr, measure_rv, compute_rv_spectrum
        self.assertTrue(callable(compute_pr))
        self.assertTrue(callable(measure_rv))
        self.assertTrue(callable(compute_rv_spectrum))
    
    def test_rv_triton_availability(self):
        """Test Triton functions import."""
        from rv_toolkit import (
            is_triton_available,
            compute_pr_triton,
            measure_rv_triton,
        )
        self.assertTrue(callable(is_triton_available))
        self.assertTrue(callable(compute_pr_triton))
        self.assertTrue(callable(measure_rv_triton))
    
    def test_rv_hooks_import(self):
        """Test hook manager imports."""
        from rv_toolkit import (
            RVHookManager,
            ActivationCapture,
            quick_rv_measure,
        )
        self.assertTrue(isinstance(RVHookManager, type))
        self.assertTrue(isinstance(ActivationCapture, type))
        self.assertTrue(callable(quick_rv_measure))
    
    def test_architecture_hooks(self):
        """Test architecture-specific hooks."""
        from rv_toolkit import GPT2RVHooks, LLaMAHooks, BERTRVHooks
        self.assertTrue(isinstance(GPT2RVHooks, type))
        self.assertTrue(isinstance(LLaMAHooks, type))
        self.assertTrue(isinstance(BERTRVHooks, type))


class TestMIExperimenterImports(unittest.TestCase):
    """Test mi_experimenter imports (orchestration layer)."""
    
    def test_package_import(self):
        """Test that mi_experimenter imports without error."""
        import mi_experimenter
        self.assertIsNotNone(mi_experimenter)
        self.assertEqual(mi_experimenter.__version__, "0.1.0")
    
    def test_core_imports(self):
        """Test core module imports."""
        from mi_experimenter import ModelLoader, load_model
        from mi_experimenter import HookManager, ActivationCache
        
        self.assertTrue(callable(load_model))
        self.assertTrue(isinstance(ModelLoader, type))
        self.assertTrue(isinstance(HookManager, type))
        self.assertTrue(isinstance(ActivationCache, type))
    
    def test_cross_architecture_suite(self):
        """Test CrossArchitectureSuite import."""
        from mi_experimenter import CrossArchitectureSuite
        from mi_experimenter import CrossArchitectureResults, ArchitectureResult
        from mi_experimenter import run_tier_2_discovery_suite
        
        self.assertTrue(isinstance(CrossArchitectureSuite, type))
        self.assertTrue(isinstance(CrossArchitectureResults, type))
        self.assertTrue(isinstance(ArchitectureResult, type))
        self.assertTrue(callable(run_tier_2_discovery_suite))
    
    def test_rv_causal_validator(self):
        """Test RVCausalValidator import."""
        from mi_experimenter import RVCausalValidator
        from mi_experimenter import ValidationConfig, ValidationResults
        from mi_experimenter import HardwareInfo
        
        self.assertTrue(isinstance(RVCausalValidator, type))
        self.assertTrue(isinstance(ValidationConfig, type))
        self.assertTrue(isinstance(ValidationResults, type))
        self.assertTrue(isinstance(HardwareInfo, type))
    
    def test_mlp_ablator(self):
        """Test MLPAblator import."""
        from mi_experimenter import MLPAblator
        self.assertTrue(isinstance(MLPAblator, type))
    
    def test_rv_available_flag(self):
        """Test RV_AVAILABLE flag."""
        import mi_experimenter
        self.assertIn("RV_AVAILABLE", dir(mi_experimenter))
        self.assertIsInstance(mi_experimenter.RV_AVAILABLE, bool)
    
    def test_measure_rv_through_mi_experimenter(self):
        """Test that measure_rv is available through mi_experimenter."""
        from mi_experimenter import measure_rv, RV_AVAILABLE
        
        if RV_AVAILABLE:
            self.assertTrue(callable(measure_rv))
        else:
            self.assertIsNone(measure_rv)


class TestAllExports(unittest.TestCase):
    """Test that all __all__ items are accessible."""
    
    def test_all_exports_present(self):
        """Test that all items in __all__ can be accessed."""
        import mi_experimenter
        
        for name in mi_experimenter.__all__:
            self.assertTrue(
                hasattr(mi_experimenter, name),
                f"{name} is in __all__ but not exported"
            )


class TestIntegration(unittest.TestCase):
    """Test integration between rv_toolkit and mi_experimenter."""
    
    def test_rv_toolkit_dependency(self):
        """Test that mi_experimenter properly depends on rv_toolkit."""
        import mi_experimenter
        
        # Should be able to access rv_toolkit via mi_experimenter
        if mi_experimenter.RV_AVAILABLE:
            # If available, measure_rv should work
            import torch
            test_matrix = torch.randn(1, 10, 128)  # batch, seq, hidden
            result = mi_experimenter.measure_rv(test_matrix)
            self.assertIsInstance(result, (float, torch.Tensor))


if __name__ == "__main__":
    unittest.main(verbosity=2)
