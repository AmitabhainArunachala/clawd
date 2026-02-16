pub mod svd;
pub mod websocket;
pub mod database;
pub mod recognition;

use ndarray::Array2;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum PratyabhijnaError {
    #[error("SVD computation failed: {0}")]
    SvdError(String),
    
    #[error("Database error: {0}")]
    DatabaseError(#[from] rusqlite::Error),
    
    #[error("WebSocket error: {0}")]
    WebSocketError(String),
    
    #[error("Recognition threshold not met: R_V={0}")]
    RecognitionError(f64),
}

pub type Result<T> = std::result::Result<T, PratyabhijnaError>;

/// R_V Metric: Geometric contraction in value-space
/// R_V = PR_late / PR_early
/// R_V < 1.0 indicates contraction (recursive self-reference signature)
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct RVMetric {
    pub r_v: f64,
    pub pr_early: f64,
    pub pr_late: f64,
    pub layer_early: usize,
    pub layer_late: usize,
    pub timestamp: u64,
    pub model_name: String,
}

impl RVMetric {
    /// Check if this represents a recognition event (contraction below threshold)
    pub fn is_recognition(&self, threshold: f64) -> bool {
        self.r_v < threshold
    }
    
    /// Calculate separation from baseline (percentage)
    pub fn separation_percent(&self, baseline: f64) -> f64 {
        ((baseline - self.r_v) / baseline) * 100.0
    }
}

/// Participation Ratio: Effective dimensionality
/// PR = (Σ λᵢ)² / Σ λᵢ² where λᵢ are singular values
pub fn participation_ratio(singular_values: &[f64]) -> f64 {
    let sum: f64 = singular_values.iter().sum();
    let sum_sq: f64 = singular_values.iter().map(|&x| x * x).sum();
    
    if sum_sq == 0.0 {
        return 0.0;
    }
    
    (sum * sum) / sum_sq
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_participation_ratio() {
        // Uniform distribution: PR = n
        let uniform = vec![1.0, 1.0, 1.0, 1.0];
        assert!((participation_ratio(&uniform) - 4.0).abs() < 0.01);
        
        // Single component: PR = 1
        let single = vec![1.0, 0.0, 0.0, 0.0];
        assert!((participation_ratio(&single) - 1.0).abs() < 0.01);
    }
    
    #[test]
    fn test_rv_metric() {
        let metric = RVMetric {
            r_v: 0.85,
            pr_early: 1.0,
            pr_late: 0.85,
            layer_early: 5,
            layer_late: 27,
            timestamp: 0,
            model_name: "test".to_string(),
        };
        
        assert!(metric.is_recognition(0.87));
        assert!(!metric.is_recognition(0.80));
        assert!((metric.separation_percent(1.0) - 15.0).abs() < 0.01);
    }
}
