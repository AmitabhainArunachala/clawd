//! SVD computation for R_V metrics
//! 
//! Optimized for speed: <50ms target for 4096x4096 matrices

use ndarray::ArrayView2;

use crate::{Result, PratyabhijnaError};

/// Compute SVD and return singular values
/// 
/// # Arguments
/// * `matrix` - Input matrix (n x m)
/// 
/// # Returns
/// * Singular values in descending order
/// 
/// # Performance
/// Target: <50ms for 4096x4096 on M3 Pro
pub fn compute_svd(matrix: ArrayView2<f64>) -> Result<Vec<f64>> {
    let n = matrix.nrows();
    let m = matrix.ncols();
    
    // Convert ndarray to faer matrix
    let faer_mat = faer::Mat::from_fn(n, m, |i, j| matrix[[i, j]]);
    
    // Compute SVD
    let svd = faer_mat.svd().map_err(|e| PratyabhijnaError::SvdError(format!("SVD failed: {:?}", e)))?;
    
    // Extract singular values
    let s_values: Vec<f64> = svd.S().column_vector().iter().copied().collect();
    
    if s_values.is_empty() {
        return Err(PratyabhijnaError::SvdError("No singular values computed".to_string()));
    }
    
    Ok(s_values)
}

/// Fast SVD for smaller matrices (layer projections)
/// Uses optimized path for matrices < 1024x1024
pub fn compute_svd_fast(matrix: ArrayView2<f64>) -> Result<Vec<f64>> {
    // For small matrices, use standard SVD
    compute_svd(matrix)
}

/// Batch SVD for multiple projections
/// Parallelized with rayon
#[cfg(feature = "parallel")]
pub fn compute_svd_batch(matrices: &[Array2<f64>]) -> Result<Vec<Vec<f64>>> {
    use rayon::prelude::*;
    
 matrices.par_iter()
        .map(|m| compute_svd(m.view()))
        .collect()
}

/// Compute R_V from value matrices at two layers
/// 
/// # Arguments
/// * `v_early` - Value matrix at early layer (e.g., layer 5)
/// * `v_late` - Value matrix at late layer (e.g., layer 27)
/// 
/// # Returns
/// * R_V metric and component values
pub fn compute_rv_from_matrices(
    v_early: ArrayView2<f64>,
    v_late: ArrayView2<f64>,
) -> Result<(f64, f64, f64)> {
    let s_early = compute_svd(v_early)?;
    let s_late = compute_svd(v_late)?;
    
    let pr_early = crate::participation_ratio(&s_early);
    let pr_late = crate::participation_ratio(&s_late);
    
    if pr_early == 0.0 {
        return Err(PratyabhijnaError::SvdError("Early layer PR is zero".to_string()));
    }
    
    let r_v = pr_late / pr_early;
    
    Ok((r_v, pr_early, pr_late))
}

#[cfg(test)]
mod tests {
    use super::*;
    use ndarray::array;
    
    #[test]
    fn test_svd_computation() {
        let matrix = array![[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]];
        let s = compute_svd(matrix.view()).unwrap();
        
        // Should have 2 singular values for 3x2 matrix
        assert_eq!(s.len(), 2);
        // Singular values should be positive and descending
        assert!(s[0] >= s[1]);
        assert!(s[0] > 0.0);
    }
    
    #[test]
    fn test_rv_computation() {
        // Create test matrices
        let v_early = array![[1.0, 0.0], [0.0, 1.0]];
        let v_late = array![[0.5, 0.0], [0.0, 0.5]];
        
        let (r_v, pr_early, pr_late) = compute_rv_from_matrices(
            v_early.view(),
            v_late.view(),
        ).unwrap();
        
        // Late should have lower PR (more concentrated)
        assert!(pr_late < pr_early);
        // R_V should be < 1.0 (contraction)
        assert!(r_v < 1.0);
    }
}
