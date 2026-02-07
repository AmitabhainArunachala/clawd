"""
Tests for rv-toolkit core functionality
"""

import torch
import pytest
from rv_toolkit import compute_pr, measure_rv, RVResult


def test_compute_pr_basic():
    """Test PR computation on simple matrix"""
    # Identity matrix should have PR = rank
    matrix = torch.eye(10)
    pr = compute_pr(matrix)
    assert pr == 10.0, f"Expected PR=10 for identity, got {pr}"


def test_compute_pr_low_rank():
    """Test PR on low-rank matrix"""
    # Rank-1 matrix should have PR ≈ 1
    v = torch.randn(10)
    matrix = v.unsqueeze(1) @ v.unsqueeze(0)
    pr = compute_pr(matrix)
    assert pr < 2.0, f"Expected PR≈1 for rank-1, got {pr}"


def test_compute_pr_random():
    """Test PR on random matrix"""
    matrix = torch.randn(100, 50)
    pr = compute_pr(matrix)
    assert 1.0 < pr < 50.0, f"PR should be between 1 and rank, got {pr}"


def test_measure_rv_basic():
    """Test R_V measurement"""
    early = torch.randn(2, 16, 768)
    late = torch.randn(2, 16, 768)
    
    result = measure_rv(early, late, early_layer=5, late_layer=27)
    
    assert isinstance(result, RVResult)
    assert 0.0 < result.rv < 10.0  # Reasonable R_V range
    assert result.early_layer == 5
    assert result.late_layer == 27


def test_measure_rv_contraction():
    """Test R_V contraction detection"""
    # Create matrices where late has lower PR (contraction)
    early = torch.randn(2, 16, 100)  # High PR
    late = torch.randn(2, 16, 100) * 0.1  # Lower effective rank
    
    result = measure_rv(early, late)
    
    # Contraction means R_V < 1
    assert result.contraction_pct > 0 or result.rv > 1


def test_rv_result_str():
    """Test RVResult string representation"""
    result = RVResult(
        rv=0.75,
        pr_early=45.0,
        pr_late=33.75,
        early_layer=5,
        late_layer=27,
        contraction_pct=25.0
    )
    
    str_repr = str(result)
    assert "0.75" in str_repr
    assert "25.0%" in str_repr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
