"""
test_rv_causal.py - Unit tests for R_V causal validation
=========================================================

Tests the R_V computation and validator behavior.
"""

import unittest
import torch
import numpy as np


class TestRVComputation(unittest.TestCase):
    """Test R_V computation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        try:
            from rv_toolkit.rv_core import compute_pr, measure_rv
            self.compute_pr = compute_pr
            self.measure_rv = measure_rv
            self.RV_AVAILABLE = True
        except ImportError:
            self.RV_AVAILABLE = False
    
    def test_pr_full_rank(self):
        """Test PR of full-rank identity matrix."""
        if not self.RV_AVAILABLE:
            self.skipTest("rv_toolkit not available")
        
        # Identity matrix should have PR ≈ dimension
        dim = 50
        eye = torch.eye(dim)
        pr = self.compute_pr(eye)
        
        # Should be close to full rank
        self.assertGreater(pr.item(), dim * 0.9)
        self.assertLessEqual(pr.item(), dim)
    
    def test_pr_rank_one(self):
        """Test PR of rank-1 matrix."""
        if not self.RV_AVAILABLE:
            self.skipTest("rv_toolkit not available")
        
        # Outer product of two vectors = rank-1
        v1 = torch.randn(100)
        v2 = torch.randn(50)
        rank_one = torch.outer(v1, v2)
        pr = self.compute_pr(rank_one)
        
        # Should be close to 1
        self.assertLess(pr.item(), 2.0)
        self.assertGreater(pr.item(), 0.5)
    
    def test_pr_random_matrix(self):
        """Test PR of random matrix (full effective rank)."""
        if not self.RV_AVAILABLE:
            self.skipTest("rv_toolkit not available")
        
        # Random matrix should have high PR
        torch.manual_seed(42)
        random_mat = torch.randn(100, 50)
        pr = self.compute_pr(random_mat)
        
        # Should be substantial (roughly 40-50 for 100x50)
        self.assertGreater(pr.item(), 30)
        self.assertLess(pr.item(), 60)
    
    def test_measure_rv_hidden_states(self):
        """Test measure_rv on transformer-like hidden states."""
        if not self.RV_AVAILABLE:
            self.skipTest("rv_toolkit not available")
        
        # Simulate hidden states: (batch=4, seq_len=10, hidden_dim=128)
        torch.manual_seed(42)
        hidden = torch.randn(4, 10, 128)
        
        rv = self.measure_rv(hidden)
        
        # Should return a scalar
        self.assertTrue(isinstance(rv, torch.Tensor))
        self.assertEqual(rv.ndim, 0)  # scalar
        
        # Should be reasonable (not extreme)
        self.assertGreater(rv.item(), 1)
        self.assertLess(rv.item(), 128)
    
    def test_measure_rv_per_head(self):
        """Test measure_rv with per-head analysis."""
        if not self.RV_AVAILABLE:
            self.skipTest("rv_toolkit not available")
        
        # Simulate 12-head attention: (batch=2, seq=8, hidden=768)
        torch.manual_seed(42)
        hidden = torch.randn(2, 8, 768)
        
        mean_rv, per_head_rv = self.measure_rv(
            hidden, per_head=True, num_heads=12
        )
        
        # Should return mean and per-head values
        self.assertTrue(isinstance(mean_rv, torch.Tensor))
        self.assertEqual(per_head_rv.shape, (12,))
        
        # Mean should be average of per-head
        expected_mean = per_head_rv.mean()
        self.assertAlmostEqual(mean_rv.item(), expected_mean.item(), places=5)
    
    def test_pr_determinism(self):
        """Test that PR computation is deterministic with same seed."""
        if not self.RV_AVAILABLE:
            self.skipTest("rv_toolkit not available")
        
        torch.manual_seed(42)
        mat1 = torch.randn(50, 50)
        pr1 = self.compute_pr(mat1)
        
        torch.manual_seed(42)
        mat2 = torch.randn(50, 50)
        pr2 = self.compute_pr(mat2)
        
        # Should be identical
        self.assertAlmostEqual(pr1.item(), pr2.item(), places=6)


class TestCausalValidatorAPI(unittest.TestCase):
    """Test the causal validator API (placeholder for actual implementation)."""
    
    def test_validator_placeholder(self):
        """Placeholder test for RVCausalValidator."""
        # This test documents the expected API
        # When implemented, it should:
        # 1. Accept model, target_layer, controls, n_pairs
        # 2. Run causal validation with 4 controls
        # 3. Return effect size, p-value, transfer efficiency
        
        expected_api = {
            "model": "str or ModelLoader",
            "target_layer": "int",
            "controls": "List[str] - ['random', 'shuffled', 'wrong_layer', 'orthogonal']",
            "n_pairs": "int - number of causal pairs",
        }
        
        expected_results = {
            "d": "Cohen's d effect size",
            "p": "p-value",
            "transfer_efficiency": "float",
            "control_results": "Dict[str, Any]"
        }
        
        # Just verify the API spec is documented
        self.assertIn("model", expected_api)
        self.assertIn("d", expected_results)


class TestControlTypes(unittest.TestCase):
    """Test the various control types for causal validation."""
    
    def test_random_control(self):
        """Test random activation control."""
        # Random activations should have no causal effect
        # This tests that we can generate truly random tensors
        torch.manual_seed(42)
        random_act = torch.randn(1, 10, 128)
        
        # Should be different from another random sample
        torch.manual_seed(43)
        random_act2 = torch.randn(1, 10, 128)
        
        self.assertFalse(torch.allclose(random_act, random_act2))
    
    def test_shuffled_control(self):
        """Test shuffled activation control."""
        # Shuffled should preserve distribution but destroy structure
        torch.manual_seed(42)
        original = torch.randn(1, 10, 128)
        
        # Shuffle along sequence dimension
        indices = torch.randperm(10)
        shuffled = original[:, indices, :]
        
        # Values should be the same set, but order different
        self.assertFalse(torch.allclose(original, shuffled))
        self.assertTrue(torch.allclose(original.sum(), shuffled.sum()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
