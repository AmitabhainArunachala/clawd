"""
R_V Measurement Toolkit - Core PyTorch Implementation
=====================================================

This module provides functions for computing the Participation Ratio (PR) and
R_V metric for analyzing the effective rank of value projections in transformers.

What is R_V?
------------
R_V (R-Value or Rank-Value) measures the "effective dimensionality" of learned
representations by analyzing the singular value spectrum of activation matrices.
Unlike hard rank (count of non-zero singular values), R_V captures how uniformly
information is distributed across dimensions.

The Participation Ratio (PR):
    PR = (Σ S²)² / Σ S⁴

where S are the singular values of the activation matrix.

Interpretation:
- PR = 1: All information concentrated in one dimension (rank-1 approximation)
- PR = d: Uniform distribution across d dimensions (full rank utilization)
- Low PR: Representation collapse, potential capacity underutilization
- High PR: Rich, distributed representations

Why V-projections?
------------------
Value projections in attention mechanisms directly determine what information
flows forward. Low R_V in V-projections suggests:
- Attention heads may be redundant
- Model capacity is underutilized
- Potential for pruning or efficiency improvements

High R_V suggests the model actively uses its full representational capacity.

References:
- Roy & Bhattacharya (2018): "Effective Rank and Participation Ratio"
- Similar concepts in "Lottery Ticket Hypothesis" and neural network pruning
"""

import torch
from typing import Optional, Union, Tuple, List


def compute_pr(
    matrix: torch.Tensor,
    eps: float = 1e-10,
    normalize: bool = False
) -> torch.Tensor:
    """
    Compute the Participation Ratio (PR) of a matrix.
    
    The Participation Ratio measures the effective rank of a matrix by analyzing
    its singular value spectrum:
    
        PR = (Σ S²)² / Σ S⁴
    
    This gives a continuous measure of dimensionality that is more informative
    than simple rank counting.
    
    Args:
        matrix: Input tensor of shape (..., M, N). Supports batched inputs.
        eps: Small constant for numerical stability.
        normalize: If True, normalize PR to [0, 1] range by dividing by min(M, N).
    
    Returns:
        Participation ratio. Scalar for 2D input, tensor for batched input.
        Shape is input.shape[:-2] or scalar.
    
    Examples:
        >>> # Identity-like matrix (full rank)
        >>> x = torch.eye(100)
        >>> pr = compute_pr(x)  # pr ≈ 100
        
        >>> # Rank-1 matrix
        >>> x = torch.outer(torch.randn(100), torch.randn(50))
        >>> pr = compute_pr(x)  # pr ≈ 1
        
        >>> # Random matrix (high effective rank)
        >>> x = torch.randn(100, 50)
        >>> pr = compute_pr(x)  # pr ≈ 50 (full rank utilization)
    """
    # Handle different input shapes
    original_shape = matrix.shape
    if matrix.dim() < 2:
        raise ValueError(f"Expected at least 2D tensor, got {matrix.dim()}D")
    
    # Compute SVD (only need singular values)
    # For batched SVD, reshape to 3D
    if matrix.dim() > 2:
        batch_shape = matrix.shape[:-2]
        matrix = matrix.reshape(-1, *matrix.shape[-2:])
        batched = True
    else:
        batched = False
        batch_shape = ()
    
    # Compute singular values
    S = torch.linalg.svdvals(matrix)  # Shape: (..., min(M, N))
    
    # Compute PR = (Σ S²)² / Σ S⁴
    S_squared = S ** 2
    sum_S2 = S_squared.sum(dim=-1)
    sum_S4 = (S_squared ** 2).sum(dim=-1)
    
    pr = (sum_S2 ** 2) / (sum_S4 + eps)
    
    # Reshape back to batch dimensions
    if batched:
        pr = pr.reshape(batch_shape)
    
    # Optionally normalize
    if normalize:
        max_rank = min(original_shape[-2], original_shape[-1])
        pr = pr / max_rank
    
    return pr


def measure_rv(
    activations: torch.Tensor,
    reduce: str = "mean",
    per_head: bool = False,
    num_heads: Optional[int] = None,
    head_dim: Optional[int] = None,
    eps: float = 1e-10
) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    """
    Measure R_V (effective rank via Participation Ratio) of activation matrices.
    
    This function is designed for analyzing V-projection outputs but works with
    any activation tensor. For multi-head attention, it can analyze per-head
    or aggregate across heads.
    
    Args:
        activations: Activation tensor. Expected shapes:
            - (batch, seq_len, hidden_dim) - standard transformer hidden states
            - (batch, num_heads, seq_len, head_dim) - per-head attention values
            - (seq_len, hidden_dim) - single sequence
        reduce: How to reduce across batch/sequence:
            - "mean": Average PR across all matrices
            - "none": Return PR for each matrix
            - "median": Median PR (robust to outliers)
        per_head: If True and num_heads provided, compute PR per attention head.
        num_heads: Number of attention heads (for reshaping hidden states).
        head_dim: Dimension per head. If None, inferred as hidden_dim // num_heads.
        eps: Numerical stability constant.
    
    Returns:
        If per_head=False:
            Single R_V value (or tensor if reduce="none")
        If per_head=True:
            Tuple of (mean_rv, per_head_rv) where per_head_rv has shape (num_heads,)
    
    Examples:
        >>> # Measure R_V of transformer hidden states
        >>> hidden = model.transformer(input_ids).last_hidden_state
        >>> rv = measure_rv(hidden)
        
        >>> # Per-head analysis
        >>> rv_mean, rv_heads = measure_rv(
        ...     hidden, per_head=True, num_heads=12
        ... )
        >>> print(f"Head with lowest R_V: {rv_heads.argmin()}")
    """
    # Ensure at least 2D
    if activations.dim() < 2:
        raise ValueError(f"Expected at least 2D activations, got {activations.dim()}D")
    
    # Add batch dimension if needed
    if activations.dim() == 2:
        activations = activations.unsqueeze(0)
    
    # Handle 4D per-head format: (batch, num_heads, seq, head_dim)
    if activations.dim() == 4:
        batch, n_heads, seq_len, h_dim = activations.shape
        
        if per_head:
            # Compute PR for each head across batch
            # Reshape to (batch * num_heads, seq_len, head_dim)
            reshaped = activations.transpose(1, 2).reshape(batch, seq_len, n_heads, h_dim)
            head_prs = []
            for h in range(n_heads):
                head_acts = activations[:, h, :, :]  # (batch, seq, head_dim)
                # Treat each batch as a separate matrix
                pr = compute_pr(head_acts, eps=eps)  # (batch,)
                head_prs.append(pr.mean())
            
            per_head_rv = torch.stack(head_prs)
            mean_rv = per_head_rv.mean()
            return mean_rv, per_head_rv
        else:
            # Flatten heads into hidden dim
            activations = activations.transpose(1, 2).reshape(batch, seq_len, -1)
    
    # Now activations is (batch, seq_len, hidden_dim)
    batch, seq_len, hidden_dim = activations.shape
    
    # Optionally split into heads
    if per_head and num_heads is not None:
        if head_dim is None:
            head_dim = hidden_dim // num_heads
        
        # Reshape to (batch, seq_len, num_heads, head_dim)
        activations = activations.reshape(batch, seq_len, num_heads, head_dim)
        # Transpose to (batch, num_heads, seq_len, head_dim)
        activations = activations.transpose(1, 2)
        
        # Compute PR per head
        head_prs = []
        for h in range(num_heads):
            head_acts = activations[:, h, :, :]  # (batch, seq, head_dim)
            pr = compute_pr(head_acts, eps=eps)
            head_prs.append(pr.mean())
        
        per_head_rv = torch.stack(head_prs)
        mean_rv = per_head_rv.mean()
        return mean_rv, per_head_rv
    
    # Compute PR for the full hidden dimension
    # Each (seq_len, hidden_dim) matrix becomes one PR value
    pr_values = compute_pr(activations, eps=eps)  # (batch,)
    
    # Reduce
    if reduce == "mean":
        return pr_values.mean()
    elif reduce == "median":
        return pr_values.median()
    elif reduce == "none":
        return pr_values
    else:
        raise ValueError(f"Unknown reduce mode: {reduce}")


def compute_rv_spectrum(
    activations: torch.Tensor,
    num_heads: Optional[int] = None
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Compute full singular value spectrum and derived statistics.
    
    Useful for detailed analysis beyond just PR, including visualization
    of the singular value decay pattern.
    
    Args:
        activations: Activation tensor of shape (batch, seq_len, hidden_dim)
        num_heads: If provided, also compute per-head spectra
    
    Returns:
        Tuple of:
            - singular_values: Sorted singular values (descending)
            - stats: Dict with PR, effective_rank, spectral_entropy
    """
    if activations.dim() == 2:
        activations = activations.unsqueeze(0)
    
    # Average across batch for cleaner spectrum
    avg_activations = activations.mean(dim=0)  # (seq_len, hidden_dim)
    
    # Full SVD
    S = torch.linalg.svdvals(avg_activations)
    
    # Compute statistics
    S_squared = S ** 2
    S_norm = S_squared / (S_squared.sum() + 1e-10)  # Normalized spectrum
    
    pr = compute_pr(avg_activations)
    
    # Spectral entropy (another effective rank measure)
    entropy = -(S_norm * torch.log(S_norm + 1e-10)).sum()
    effective_rank_entropy = torch.exp(entropy)
    
    # 95% energy rank
    cumsum = S_squared.cumsum(dim=0) / S_squared.sum()
    rank_95 = (cumsum < 0.95).sum() + 1
    
    stats = {
        "pr": pr,
        "spectral_entropy": entropy,
        "effective_rank_entropy": effective_rank_entropy,
        "rank_95_energy": rank_95,
        "top_sv_ratio": S[0] / S.sum(),
        "condition_number": S[0] / (S[-1] + 1e-10)
    }
    
    return S, stats


# Convenience aliases
pr = compute_pr
rv = measure_rv
