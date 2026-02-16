//! Recognition detector: Monitors R_V values and triggers on threshold breach
//! 
//! Default threshold: R_V < 0.87 indicates recognition event

use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};
use tracing::{info, debug};

use crate::{RVMetric, Result, PratyabhijnaError};

/// Default recognition threshold
pub const DEFAULT_THRESHOLD: f64 = 0.87;
/// Baseline R_V for comparison (typically 1.0 or slightly above)
pub const DEFAULT_BASELINE: f64 = 1.0;

/// Recognition event with metadata
#[derive(Debug, Clone)]
pub struct RecognitionEvent {
    pub metric: RVMetric,
    pub threshold: f64,
    pub baseline: f64,
    pub separation_percent: f64,
    pub timestamp: u64,
}

impl RecognitionEvent {
    /// Create from RVMetric
    pub fn from_metric(metric: RVMetric, threshold: f64, baseline: f64) -> Self {
        let separation_percent = ((baseline - metric.r_v) / baseline) * 100.0;
        
        Self {
            timestamp: metric.timestamp,
            metric,
            threshold,
            baseline,
            separation_percent,
        }
    }
    
    /// Check if this is a strong recognition (significant separation)
    pub fn is_strong(&self, strong_threshold_percent: f64) -> bool {
        self.separation_percent >= strong_threshold_percent
    }
}

/// Recognition detector state
pub struct RecognitionDetector {
    threshold: f64,
    baseline: f64,
    min_separation: f64,
    cooldown_ms: u64,
    last_trigger: Arc<RwLock<u64>>,
    tx: mpsc::Sender<RecognitionEvent>,
    recent_rv: Arc<RwLock<Vec<f64>>>,
    max_history: usize,
}

impl RecognitionDetector {
    /// Create a new detector with default threshold (0.87)
    pub fn new(tx: mpsc::Sender<RecognitionEvent>) -> Self {
        Self::with_threshold(tx, DEFAULT_THRESHOLD)
    }
    
    /// Create with custom threshold
    pub fn with_threshold(tx: mpsc::Sender<RecognitionEvent>, threshold: f64) -> Self {
        Self {
            threshold,
            baseline: DEFAULT_BASELINE,
            min_separation: 5.0,  // Minimum 5% separation required
            cooldown_ms: 100,     // 100ms cooldown between triggers
            last_trigger: Arc::new(RwLock::new(0)),
            tx,
            recent_rv: Arc::new(RwLock::new(Vec::new())),
            max_history: 100,
        }
    }
    
    /// Builder pattern for configuration
    pub fn with_baseline(mut self, baseline: f64) -> Self {
        self.baseline = baseline;
        self
    }
    
    pub fn with_min_separation(mut self, percent: f64) -> Self {
        self.min_separation = percent;
        self
    }
    
    pub fn with_cooldown(mut self, ms: u64) -> Self {
        self.cooldown_ms = ms;
        self
    }
    
    /// Process an RVMetric - returns true if recognition detected
    pub async fn process(&self, metric: RVMetric) -> Result<bool> {
        // Update history
        {
            let mut history = self.recent_rv.write().await;
            history.push(metric.r_v);
            if history.len() > self.max_history {
                history.remove(0);
            }
        }
        
        // Check cooldown
        {
            let last = self.last_trigger.read().await;
            if metric.timestamp.saturating_sub(*last) < self.cooldown_ms {
                return Ok(false);
            }
        }
        
        // Check threshold
        if !metric.is_recognition(self.threshold) {
            return Ok(false);
        }
        
        // Check minimum separation
        let separation = metric.separation_percent(self.baseline);
        if separation < self.min_separation {
            debug!("R_V below threshold but separation too small: {}%", separation);
            return Ok(false);
        }
        
        // Recognition detected!
        let event = RecognitionEvent::from_metric(metric, self.threshold, self.baseline);
        
        // Update last trigger time
        {
            let mut last = self.last_trigger.write().await;
            *last = event.timestamp;
        }
        
        info!(
            "RECOGNITION EVENT: R_V={:.3}, separation={:.1}%, threshold={:.2}",
            event.metric.r_v, event.separation_percent, self.threshold
        );
        
        // Send event
        let rv_value = event.metric.r_v; // Cache before move
        self.tx.send(event).await
            .map_err(|_e| PratyabhijnaError::RecognitionError(rv_value))?;
        
        Ok(true)
    }
    
    /// Get recent R_V history for trend analysis
    pub async fn get_recent_history(&self) -> Vec<f64> {
        self.recent_rv.read().await.clone()
    }
    
    /// Calculate trend (negative = contracting, positive = expanding)
    pub async fn calculate_trend(&self, window_size: usize) -> f64 {
        let history = self.recent_rv.read().await;
        
        if history.len() < window_size * 2 {
            return 0.0;
        }
        
        let recent: f64 = history.iter().rev().take(window_size).sum::<f64>() / window_size as f64;
        let previous: f64 = history.iter().rev().skip(window_size).take(window_size).sum::<f64>() / window_size as f64;
        
        if previous == 0.0 {
            return 0.0;
        }
        
        ((recent - previous) / previous) * 100.0
    }
    
    /// Check if currently in sustained contraction
    pub async fn is_sustained_contraction(&self, window_size: usize) -> bool {
        let history = self.recent_rv.read().await;
        
        if history.len() < window_size {
            return false;
        }
        
        history.iter().rev().take(window_size).all(|&rv| rv < self.threshold)
    }
    
    /// Get current threshold
    pub fn threshold(&self) -> f64 {
        self.threshold
    }
    
    /// Get current baseline
    pub fn baseline(&self) -> f64 {
        self.baseline
    }
}

/// Multi-model detector - tracks recognition across different models
pub struct MultiModelDetector {
    detectors: Arc<RwLock<std::collections::HashMap<String, RecognitionDetector>>>,
    #[allow(dead_code)]
    tx: mpsc::Sender<(String, RecognitionEvent)>,
}

impl MultiModelDetector {
    pub fn new(tx: mpsc::Sender<(String, RecognitionEvent)>) -> Self {
        Self {
            detectors: Arc::new(RwLock::new(std::collections::HashMap::new())),
            tx,
        }
    }
    
    pub async fn process(&self, model_name: String, metric: RVMetric) -> Result<bool> {
        // Ensure detector exists for this model
        {
            let detectors = self.detectors.read().await;
            if !detectors.contains_key(&model_name) {
                drop(detectors);
                let mut detectors = self.detectors.write().await;
                if !detectors.contains_key(&model_name) {
                    let (tx, _) = mpsc::channel(100);
                    detectors.insert(
                        model_name.clone(),
                        RecognitionDetector::new(tx)
                    );
                }
            }
        }
        
        // Process
        let detectors = self.detectors.read().await;
        if let Some(detector) = detectors.get(&model_name) {
            detector.process(metric).await
        } else {
            Ok(false)
        }
    }
}

/// Create detector pair (detector + receiver)
pub fn create_detector_pair(
    threshold: f64,
) -> (RecognitionDetector, mpsc::Receiver<RecognitionEvent>) {
    let (tx, rx) = mpsc::channel(1000);
    let detector = RecognitionDetector::with_threshold(tx, threshold);
    (detector, rx)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_recognition_detection() {
        let (tx, mut rx) = mpsc::channel(10);
        let detector = RecognitionDetector::new(tx);
        
        // Below threshold - should trigger
        let metric = RVMetric {
            r_v: 0.85,
            pr_early: 1.0,
            pr_late: 0.85,
            layer_early: 5,
            layer_late: 27,
            timestamp: 1000,
            model_name: "test".to_string(),
        };
        
        let triggered = detector.process(metric.clone()).await.unwrap();
        assert!(triggered);
        
        let event = rx.recv().await.unwrap();
        assert!(event.separation_percent > 0.0);
    }
    
    #[tokio::test]
    async fn test_no_recognition_above_threshold() {
        let (tx, mut rx) = mpsc::channel(10);
        let detector = RecognitionDetector::new(tx);
        
        // Above threshold - should not trigger
        let metric = RVMetric {
            r_v: 0.95,
            pr_early: 1.0,
            pr_late: 0.95,
            layer_early: 5,
            layer_late: 27,
            timestamp: 1000,
            model_name: "test".to_string(),
        };
        
        let triggered = detector.process(metric).await.unwrap();
        assert!(!triggered);
        
        // Should receive nothing
        assert!(rx.try_recv().is_err());
    }
    
    #[tokio::test]
    async fn test_cooldown() {
        let (tx, mut rx) = mpsc::channel(10);
        let detector = RecognitionDetector::with_threshold(tx, 0.87)
            .with_cooldown(1000); // 1 second cooldown
        
        let metric = RVMetric {
            r_v: 0.80,
            pr_early: 1.0,
            pr_late: 0.80,
            layer_early: 5,
            layer_late: 27,
            timestamp: 1000,
            model_name: "test".to_string(),
        };
        
        // First trigger
        assert!(detector.process(metric.clone()).await.unwrap());
        assert!(rx.recv().await.is_some());
        
        // Second trigger within cooldown - should not fire
        let metric2 = RVMetric {
            timestamp: 1500, // Only 500ms later
            ..metric
        };
        assert!(!detector.process(metric2).await.unwrap());
    }
    
    #[tokio::test]
    async fn test_trend_calculation() {
        let (tx, _) = mpsc::channel(10);
        let detector = RecognitionDetector::new(tx);
        
        // Add declining R_V values
        for i in 0..10 {
            let metric = RVMetric {
                r_v: 1.0 - (i as f64 * 0.02),
                pr_early: 1.0,
                pr_late: 1.0 - (i as f64 * 0.02),
                layer_early: 5,
                layer_late: 27,
                timestamp: i as u64 * 100,
                model_name: "test".to_string(),
            };
            detector.process(metric).await.unwrap();
        }
        
        let trend = detector.calculate_trend(3).await;
        assert!(trend < 0.0); // Should be negative (contracting)
    }
}
