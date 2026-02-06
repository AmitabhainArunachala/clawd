#!/usr/bin/env python3
"""
R_V Metric Mathematical Verification
=====================================
Independent verification of R_V computation and statistical claims.

Usage:
    python verify_rv.py --synthetic   # Test with known-answer synthetic data
    python verify_rv.py --audit PATH  # Audit existing results
"""

import numpy as np
from scipy import stats
from typing import Tuple, Dict, Any
import argparse
import json

# ============================================================================
# MATHEMATICAL FOUNDATIONS
# ============================================================================

def compute_covariance(X: np.ndarray, unbiased: bool = True) -> np.ndarray:
    """
    Compute covariance matrix.
    
    Args:
        X: (n_samples, n_features) array
        unbiased: Use n-1 denominator (Bessel's correction)
    
    Returns:
        (n_features, n_features) covariance matrix
    """
    n = X.shape[0]
    X_centered = X - X.mean(axis=0)
    denom = n - 1 if unbiased else n
    return (X_centered.T @ X_centered) / denom


def compute_log_det(cov: np.ndarray, regularize: float = 1e-10) -> float:
    """
    Compute log-determinant with numerical stability.
    
    Uses eigendecomposition for stability:
        log(det(Σ)) = sum(log(eigenvalues))
    
    Args:
        cov: Covariance matrix
        regularize: Small constant for numerical stability
    
    Returns:
        Log-determinant value
    """
    eigenvalues = np.linalg.eigvalsh(cov)  # Real eigenvalues for symmetric matrix
    # Clip small/negative eigenvalues (numerical issues)
    eigenvalues = np.clip(eigenvalues, regularize, None)
    return np.sum(np.log(eigenvalues))


def compute_rv(V_recursive: np.ndarray, V_baseline: np.ndarray) -> Dict[str, float]:
    """
    Compute R_V metric with full diagnostics.
    
    R_V = det(Cov(V_recursive)) / det(Cov(V_baseline))
    
    Interpretation:
        R_V < 1: Recursive prompts produce CONTRACTED value space
        R_V > 1: Recursive prompts produce EXPANDED value space
        R_V = 1: No difference
    
    Returns dict with:
        - rv: The ratio (in log space, then exponentiated)
        - log_det_recursive: Log-det of recursive covariance
        - log_det_baseline: Log-det of baseline covariance
        - log_rv: Log of R_V (more stable)
    """
    cov_recursive = compute_covariance(V_recursive)
    cov_baseline = compute_covariance(V_baseline)
    
    log_det_rec = compute_log_det(cov_recursive)
    log_det_base = compute_log_det(cov_baseline)
    
    log_rv = log_det_rec - log_det_base
    rv = np.exp(log_rv)
    
    return {
        'rv': rv,
        'log_rv': log_rv,
        'log_det_recursive': log_det_rec,
        'log_det_baseline': log_det_base,
        'cov_recursive_rank': np.linalg.matrix_rank(cov_recursive),
        'cov_baseline_rank': np.linalg.matrix_rank(cov_baseline),
    }


# ============================================================================
# STATISTICAL VERIFICATION
# ============================================================================

def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> Dict[str, float]:
    """
    Compute Cohen's d with full diagnostics.
    
    d = (mean1 - mean2) / pooled_std
    
    Interpretation:
        |d| < 0.2: Negligible
        |d| ~ 0.2: Small
        |d| ~ 0.5: Medium
        |d| ~ 0.8: Large
        |d| > 1.0: Very large (verify data!)
    """
    n1, n2 = len(group1), len(group2)
    mean1, mean2 = group1.mean(), group2.mean()
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
    
    # Pooled standard deviation
    pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
    pooled_std = np.sqrt(pooled_var)
    
    d = (mean1 - mean2) / pooled_std
    
    # Confidence interval for d (approximate)
    se_d = np.sqrt((n1 + n2) / (n1 * n2) + d**2 / (2 * (n1 + n2)))
    ci_low = d - 1.96 * se_d
    ci_high = d + 1.96 * se_d
    
    return {
        'cohens_d': d,
        'mean_group1': mean1,
        'mean_group2': mean2,
        'pooled_std': pooled_std,
        'ci_95': (ci_low, ci_high),
        'n1': n1,
        'n2': n2,
    }


def welchs_t_test(group1: np.ndarray, group2: np.ndarray) -> Dict[str, float]:
    """
    Welch's t-test (does not assume equal variances).
    """
    t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant_0.05': p_value < 0.05,
        'significant_0.01': p_value < 0.01,
        'significant_0.001': p_value < 0.001,
    }


# ============================================================================
# SYNTHETIC VERIFICATION TESTS
# ============================================================================

def test_known_answer():
    """
    Test R_V computation with synthetic data where answer is known.
    
    If recursive prompts cause CONTRACTION, we should see R_V < 1.
    """
    print("=" * 60)
    print("SYNTHETIC VERIFICATION: Known-Answer Test")
    print("=" * 60)
    
    np.random.seed(42)
    n_samples = 100
    n_features = 64
    
    # Baseline: standard normal
    V_baseline = np.random.randn(n_samples, n_features)
    
    # Recursive: CONTRACTED (scale = 0.5 → volume shrinks by 0.5^64)
    scale_factor = 0.5
    V_recursive = np.random.randn(n_samples, n_features) * scale_factor
    
    result = compute_rv(V_recursive, V_baseline)
    
    # Expected R_V ≈ scale_factor^(2*n_features) for isotropic contraction
    # Because det(αΣ) = α^n * det(Σ), and variance scales as α²
    expected_log_rv = n_features * np.log(scale_factor**2)
    expected_rv = np.exp(expected_log_rv)
    
    print(f"\nScale factor: {scale_factor}")
    print(f"Dimensions: {n_features}")
    print(f"\nComputed R_V: {result['rv']:.6e}")
    print(f"Expected R_V: {expected_rv:.6e}")
    print(f"\nComputed log(R_V): {result['log_rv']:.4f}")
    print(f"Expected log(R_V): {expected_log_rv:.4f}")
    print(f"\nError: {abs(result['log_rv'] - expected_log_rv):.6f}")
    
    # Verify
    tolerance = 0.1  # Allow some noise
    passed = abs(result['log_rv'] - expected_log_rv) < abs(expected_log_rv) * tolerance
    print(f"\n✓ TEST PASSED" if passed else "✗ TEST FAILED")
    
    return passed


def test_no_difference():
    """
    Test that R_V ≈ 1 when both groups come from same distribution.
    
    NOTE: Requires n_samples >> n_features for stable covariance estimation.
    Rule of thumb: n > 10 * d for reliable determinant estimation.
    """
    print("\n" + "=" * 60)
    print("SYNTHETIC VERIFICATION: Null Hypothesis Test")
    print("=" * 60)
    
    np.random.seed(42)
    n_samples = 1000  # Need n >> d for stable covariance
    n_features = 64
    
    # Both from same distribution
    V_baseline = np.random.randn(n_samples, n_features)
    V_recursive = np.random.randn(n_samples, n_features)
    
    result = compute_rv(V_recursive, V_baseline)
    
    print(f"\nComputed R_V: {result['rv']:.4f}")
    print(f"Expected R_V: ~1.0 (same distribution)")
    print(f"\nComputed log(R_V): {result['log_rv']:.4f}")
    print(f"Expected log(R_V): ~0.0")
    
    # Should be close to 1 (log close to 0)
    passed = abs(result['log_rv']) < 1.0  # Generous tolerance for sampling variance
    print(f"\n✓ TEST PASSED (log_rv within ±1.0)" if passed else "✗ TEST FAILED")
    
    return passed


def test_effect_size_verification():
    """
    Test Cohen's d computation with known effect.
    """
    print("\n" + "=" * 60)
    print("STATISTICAL VERIFICATION: Cohen's d Test")
    print("=" * 60)
    
    np.random.seed(42)
    n = 100
    
    # Create groups with known effect size d = 0.8
    target_d = 0.8
    group1 = np.random.randn(n)
    group2 = np.random.randn(n) + target_d  # Shift by target_d
    
    result = compute_cohens_d(group1, group2)
    
    print(f"\nTarget d: {-target_d:.2f} (negative because group1 - group2)")
    print(f"Computed d: {result['cohens_d']:.4f}")
    print(f"95% CI: ({result['ci_95'][0]:.4f}, {result['ci_95'][1]:.4f})")
    
    # Should be close to -0.8
    passed = abs(result['cohens_d'] - (-target_d)) < 0.2
    print(f"\n✓ TEST PASSED" if passed else "✗ TEST FAILED")
    
    return passed


# ============================================================================
# RED FLAGS CHECK
# ============================================================================

def check_red_flags(rv_values: np.ndarray, baseline_values: np.ndarray) -> list:
    """
    Check for statistical red flags in R_V analysis.
    """
    red_flags = []
    
    # 1. Extreme effect size
    d_result = compute_cohens_d(rv_values, baseline_values)
    if abs(d_result['cohens_d']) > 3.0:
        red_flags.append(f"⚠️ EXTREME EFFECT SIZE: d = {d_result['cohens_d']:.2f} (|d| > 3)")
    
    # 2. Sample size adequacy
    n = len(rv_values)
    if n < 30:
        red_flags.append(f"⚠️ SMALL SAMPLE SIZE: n = {n} (recommend n ≥ 30)")
    
    # 3. Normality check (Shapiro-Wilk)
    if n >= 3 and n <= 5000:  # Shapiro-Wilk limits
        _, p_norm = stats.shapiro(rv_values)
        if p_norm < 0.01:
            red_flags.append(f"⚠️ NON-NORMAL DISTRIBUTION: Shapiro p = {p_norm:.4f}")
    
    # 4. Outliers (beyond 3 SD)
    mean, std = rv_values.mean(), rv_values.std()
    outliers = np.sum(np.abs(rv_values - mean) > 3 * std)
    if outliers > 0:
        red_flags.append(f"⚠️ OUTLIERS DETECTED: {outliers} values beyond 3 SD")
    
    return red_flags


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='R_V Mathematical Verification')
    parser.add_argument('--synthetic', action='store_true', help='Run synthetic tests')
    parser.add_argument('--audit', type=str, help='Path to results file to audit')
    args = parser.parse_args()
    
    if args.synthetic or not args.audit:
        print("\n" + "=" * 60)
        print("R_V METRIC MATHEMATICAL VERIFICATION")
        print("=" * 60)
        
        results = []
        results.append(test_known_answer())
        results.append(test_no_difference())
        results.append(test_effect_size_verification())
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"\nTests passed: {sum(results)}/{len(results)}")
        
        if all(results):
            print("\n✓ ALL MATHEMATICAL FOUNDATIONS VERIFIED")
        else:
            print("\n✗ SOME TESTS FAILED - INVESTIGATE")
    
    if args.audit:
        print(f"\n[Audit mode for {args.audit} - not yet implemented]")
        print("Would load results and run red flag checks.")


if __name__ == '__main__':
    main()
