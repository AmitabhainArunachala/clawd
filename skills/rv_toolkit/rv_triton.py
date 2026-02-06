"""
R_V Measurement Toolkit - Triton Kernel Implementation
======================================================

This module provides Triton-accelerated kernels for computing participation
ratio components. Falls back gracefully to PyTorch when Triton is unavailable.

Triton Advantage:
-----------------
For large-scale R_V measurement across many layers/heads, Triton kernels can
significantly accelerate the computation by:
1. Fusing the S² and S⁴ computations
2. Efficient parallel reduction
3. Avoiding intermediate tensor allocations

Note: The SVD computation itself is NOT implemented in Triton (CUDA SVD is complex).
These kernels accelerate the post-SVD PR computation.
"""

import torch
from typing import Optional, Tuple

# Try to import Triton
try:
    import triton
    import triton.language as tl
    TRITON_AVAILABLE = True
except ImportError:
    TRITON_AVAILABLE = False
    triton = None
    tl = None


# ============================================================================
# Triton Kernels (when available)
# ============================================================================

if TRITON_AVAILABLE:
    
    @triton.jit
    def _pr_from_sv_kernel(
        sv_ptr,           # Pointer to singular values
        output_ptr,       # Pointer to output PR values
        n_elements,       # Number of singular values per matrix
        n_matrices,       # Number of matrices (batch size)
        BLOCK_SIZE: tl.constexpr,
    ):
        """
        Triton kernel to compute PR from pre-computed singular values.
        
        PR = (Σ S²)² / Σ S⁴
        
        Each program instance handles one matrix in the batch.
        """
        # Which matrix this program handles
        matrix_idx = tl.program_id(0)
        
        if matrix_idx >= n_matrices:
            return
        
        # Base offset for this matrix's singular values
        base_offset = matrix_idx * n_elements
        
        # Accumulate sums
        sum_s2 = 0.0
        sum_s4 = 0.0
        
        # Process in blocks
        for block_start in range(0, n_elements, BLOCK_SIZE):
            offsets = block_start + tl.arange(0, BLOCK_SIZE)
            mask = offsets < n_elements
            
            # Load singular values
            sv = tl.load(sv_ptr + base_offset + offsets, mask=mask, other=0.0)
            
            # Compute S² and S⁴
            sv_squared = sv * sv
            sv_fourth = sv_squared * sv_squared
            
            # Accumulate
            sum_s2 += tl.sum(sv_squared, axis=0)
            sum_s4 += tl.sum(sv_fourth, axis=0)
        
        # Compute PR with numerical stability
        pr = (sum_s2 * sum_s2) / (sum_s4 + 1e-10)
        
        # Store result
        tl.store(output_ptr + matrix_idx, pr)
    
    
    @triton.jit
    def _pr_stats_kernel(
        sv_ptr,           # Pointer to singular values
        pr_ptr,           # Output: PR values
        entropy_ptr,      # Output: Spectral entropy
        n_elements,       # Number of singular values per matrix
        n_matrices,       # Number of matrices
        BLOCK_SIZE: tl.constexpr,
    ):
        """
        Extended kernel computing both PR and spectral entropy in one pass.
        """
        matrix_idx = tl.program_id(0)
        
        if matrix_idx >= n_matrices:
            return
        
        base_offset = matrix_idx * n_elements
        
        # First pass: compute total for normalization
        total_s2 = 0.0
        for block_start in range(0, n_elements, BLOCK_SIZE):
            offsets = block_start + tl.arange(0, BLOCK_SIZE)
            mask = offsets < n_elements
            sv = tl.load(sv_ptr + base_offset + offsets, mask=mask, other=0.0)
            sv_squared = sv * sv
            total_s2 += tl.sum(sv_squared, axis=0)
        
        # Second pass: compute PR and entropy
        sum_s2 = 0.0
        sum_s4 = 0.0
        entropy = 0.0
        
        for block_start in range(0, n_elements, BLOCK_SIZE):
            offsets = block_start + tl.arange(0, BLOCK_SIZE)
            mask = offsets < n_elements
            sv = tl.load(sv_ptr + base_offset + offsets, mask=mask, other=0.0)
            
            sv_squared = sv * sv
            sv_fourth = sv_squared * sv_squared
            
            sum_s2 += tl.sum(sv_squared, axis=0)
            sum_s4 += tl.sum(sv_fourth, axis=0)
            
            # Normalized probabilities for entropy
            p = sv_squared / (total_s2 + 1e-10)
            # Entropy contribution (handle p=0 case)
            log_p = tl.where(p > 1e-10, tl.log(p), 0.0)
            entropy -= tl.sum(p * log_p, axis=0)
        
        # Store results
        pr = (sum_s2 * sum_s2) / (sum_s4 + 1e-10)
        tl.store(pr_ptr + matrix_idx, pr)
        tl.store(entropy_ptr + matrix_idx, entropy)


# ============================================================================
# Public API (with fallbacks)
# ============================================================================

def compute_pr_triton(
    singular_values: torch.Tensor,
    eps: float = 1e-10
) -> torch.Tensor:
    """
    Compute Participation Ratio from singular values using Triton.
    
    This function expects PRE-COMPUTED singular values. Use torch.linalg.svdvals()
    to compute them first.
    
    Args:
        singular_values: Tensor of shape (batch, k) where k = min(M, N) of
                        original matrices.
        eps: Numerical stability constant.
    
    Returns:
        PR values of shape (batch,)
    
    Note:
        Falls back to PyTorch if Triton is unavailable or inputs are on CPU.
    """
    # Ensure 2D
    if singular_values.dim() == 1:
        singular_values = singular_values.unsqueeze(0)
    
    # Check if we can use Triton
    use_triton = (
        TRITON_AVAILABLE and 
        singular_values.is_cuda and
        singular_values.numel() > 1024  # Only worth it for larger inputs
    )
    
    if use_triton:
        batch_size, n_sv = singular_values.shape
        output = torch.empty(batch_size, device=singular_values.device, dtype=singular_values.dtype)
        
        # Determine block size
        BLOCK_SIZE = min(1024, triton.next_power_of_2(n_sv))
        
        # Launch kernel
        grid = (batch_size,)
        _pr_from_sv_kernel[grid](
            singular_values,
            output,
            n_sv,
            batch_size,
            BLOCK_SIZE=BLOCK_SIZE,
        )
        
        return output
    else:
        # PyTorch fallback
        S2 = singular_values ** 2
        sum_S2 = S2.sum(dim=-1)
        sum_S4 = (S2 ** 2).sum(dim=-1)
        return (sum_S2 ** 2) / (sum_S4 + eps)


def compute_pr_stats_triton(
    singular_values: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Compute both PR and spectral entropy in a single fused kernel.
    
    More efficient than computing separately when both metrics are needed.
    
    Args:
        singular_values: Tensor of shape (batch, k)
    
    Returns:
        Tuple of (pr, entropy) tensors, each of shape (batch,)
    """
    if singular_values.dim() == 1:
        singular_values = singular_values.unsqueeze(0)
    
    use_triton = (
        TRITON_AVAILABLE and 
        singular_values.is_cuda and
        singular_values.numel() > 1024
    )
    
    if use_triton:
        batch_size, n_sv = singular_values.shape
        pr_out = torch.empty(batch_size, device=singular_values.device, dtype=singular_values.dtype)
        entropy_out = torch.empty(batch_size, device=singular_values.device, dtype=singular_values.dtype)
        
        BLOCK_SIZE = min(1024, triton.next_power_of_2(n_sv))
        
        grid = (batch_size,)
        _pr_stats_kernel[grid](
            singular_values,
            pr_out,
            entropy_out,
            n_sv,
            batch_size,
            BLOCK_SIZE=BLOCK_SIZE,
        )
        
        return pr_out, entropy_out
    else:
        # PyTorch fallback
        S2 = singular_values ** 2
        S2_sum = S2.sum(dim=-1, keepdim=True)
        S2_norm = S2 / (S2_sum + 1e-10)
        
        # PR
        sum_S2 = S2.sum(dim=-1)
        sum_S4 = (S2 ** 2).sum(dim=-1)
        pr = (sum_S2 ** 2) / (sum_S4 + 1e-10)
        
        # Entropy
        log_p = torch.where(S2_norm > 1e-10, torch.log(S2_norm), torch.zeros_like(S2_norm))
        entropy = -(S2_norm * log_p).sum(dim=-1)
        
        return pr, entropy


def measure_rv_triton(
    matrix: torch.Tensor,
    eps: float = 1e-10
) -> torch.Tensor:
    """
    Full R_V measurement with Triton acceleration where possible.
    
    Computes SVD (PyTorch/CUDA) then PR (Triton when available).
    
    Args:
        matrix: Input tensor of shape (..., M, N)
        eps: Numerical stability constant.
    
    Returns:
        PR value(s)
    """
    # Reshape for batched SVD
    original_shape = matrix.shape
    if matrix.dim() > 2:
        batch_shape = matrix.shape[:-2]
        matrix = matrix.reshape(-1, *matrix.shape[-2:])
    else:
        batch_shape = ()
        matrix = matrix.unsqueeze(0)
    
    # Compute singular values (this is the expensive part)
    S = torch.linalg.svdvals(matrix)
    
    # Compute PR (Triton-accelerated)
    pr = compute_pr_triton(S, eps=eps)
    
    # Reshape output
    if batch_shape:
        pr = pr.reshape(batch_shape)
    elif pr.numel() == 1:
        pr = pr.squeeze()
    
    return pr


# ============================================================================
# Utility functions
# ============================================================================

def is_triton_available() -> bool:
    """Check if Triton is available for acceleration."""
    return TRITON_AVAILABLE


def get_backend_info() -> dict:
    """Get information about available backends."""
    info = {
        "triton_available": TRITON_AVAILABLE,
        "triton_version": None,
        "cuda_available": torch.cuda.is_available(),
        "recommended_backend": "pytorch"  # default
    }
    
    if TRITON_AVAILABLE:
        info["triton_version"] = triton.__version__
        if torch.cuda.is_available():
            info["recommended_backend"] = "triton"
    
    return info


# Convenience aliases
pr_triton = compute_pr_triton
rv_triton = measure_rv_triton
