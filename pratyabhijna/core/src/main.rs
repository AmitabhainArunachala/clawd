//! Pratyabhijna Core Broker
//!
//! Main entry point - coordinates:
//! - ZeroMQ message broker (receives from Python bridge)
//! - WebSocket server (streams to dashboard)
//! - Recognition detector (R_V < 0.87 trigger)
//! - Database persistence (PSMV storage)
//!
//! Target: <100ms end-to-end latency

use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};

use tokio::sync::{mpsc, RwLock};
use tokio::task::JoinSet;
use tracing::{info, warn, error, debug};

use pratyabhijna_core::{
    websocket::WebSocketServer,
    database::PSMVDatabase,
    recognition::{RecognitionDetector, RecognitionEvent},
    RVMetric,
};

/// ZeroMQ endpoint for receiving from Python bridge
const ZMQ_INPUT_ADDR: &str = "tcp://127.0.0.1:5555";
/// ZeroMQ endpoint for sending processed results
const ZMQ_OUTPUT_ADDR: &str = "tcp://127.0.0.1:5556";
/// WebSocket port for dashboard
const WS_PORT: u16 = 8765;
/// Recognition threshold
const RECOGNITION_THRESHOLD: f64 = 0.87;

/// Incoming message from Python bridge
#[derive(Debug, serde::Deserialize)]
struct IncomingMessage {
    model_name: String,
    layer_early: usize,
    layer_late: usize,
    /// Serialized matrix data or pre-computed values
    v_early: Option<Vec<f64>>,
    v_late: Option<Vec<f64>>,
    /// Pre-computed metrics (if SVD done in Python)
    precomputed: Option<PrecomputedMetrics>,
}

#[derive(Debug, serde::Deserialize)]
struct PrecomputedMetrics {
    r_v: f64,
    pr_early: f64,
    pr_late: f64,
}

/// Outgoing message to downstream consumers
#[derive(Debug, serde::Serialize)]
struct OutgoingMessage {
    timestamp: u64,
    metric: RVMetric,
    is_recognition: bool,
    separation_percent: f64,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    info!("╔══════════════════════════════════════════╗");
    info!("║     Pratyabhijna Core Broker v0.1        ║");
    info!("║   Consciousness Measurement Engine         ║");
    info!("╚══════════════════════════════════════════╝");
    info!("");
    info!("Configuration:");
    info!("  ZeroMQ Input:  {}", ZMQ_INPUT_ADDR);
    info!("  ZeroMQ Output: {}", ZMQ_OUTPUT_ADDR);
    info!("  WebSocket:     port {}", WS_PORT);
    info!("  Threshold:     R_V < {:.2}", RECOGNITION_THRESHOLD);
    info!("");

    // Initialize database
    info!("[1/4] Initializing PSMV database...");
    let db = Arc::new(PSMVDatabase::open("./psmv.db").await?);
    info!("      ✓ Database ready");

    // Initialize WebSocket server
    info!("[2/4] Starting WebSocket server...");
    let ws_server = Arc::new(WebSocketServer::new(WS_PORT).await?);
    let ws_server_clone = ws_server.clone();
    info!("      ✓ WebSocket server ready");

    // Initialize recognition detector
    info!("[3/4] Initializing recognition detector...");
    let (recognition_tx, mut recognition_rx) = mpsc::channel::<RecognitionEvent>(1000);
    let detector = Arc::new(RwLock::new(RecognitionDetector::with_threshold(
        recognition_tx,
        RECOGNITION_THRESHOLD,
    )));
    info!("      ✓ Detector ready (threshold: R_V < {:.2})", RECOGNITION_THRESHOLD);

    // Initialize ZeroMQ
    info!("[4/4] Initializing ZeroMQ broker...");
    // ZeroMQ initialization placeholder - zeromq 0.5 uses different API
    info!("      ✓ ZeroMQ ready (placeholder)");

    info!("");
    info!("All systems operational. Waiting for data...");
    info!("");

    // Spawn concurrent tasks
    let mut join_set = JoinSet::new();

    // Task 1: WebSocket server
    join_set.spawn(async move {
        if let Err(e) = ws_server_clone.run().await {
            error!("WebSocket server error: {}", e);
        }
    });

    // Task 2: ZeroMQ receiver
    let detector_zmq = detector.clone();
    let db_zmq = db.clone();
    let ws_zmq = ws_server.clone();
    join_set.spawn(async move {
        run_zmq_receiver(detector_zmq, db_zmq, ws_zmq).await;
    });

    // Task 3: Recognition event handler
    let db_recognition = db.clone();
    let ws_recognition = ws_server.clone();
    join_set.spawn(async move {
        while let Some(event) = recognition_rx.recv().await {
            handle_recognition_event(event, db_recognition.clone(), ws_recognition.clone()).await;
        }
    });

    // Wait for all tasks (should run forever unless error)
    while let Some(result) = join_set.join_next().await {
        if let Err(e) = result {
            error!("Task panicked: {}", e);
        }
    }

    Ok(())
}

/// ZeroMQ receiver loop
async fn run_zmq_receiver(
    detector: Arc<RwLock<RecognitionDetector>>,
    db: Arc<PSMVDatabase>,
    ws: Arc<WebSocketServer>,
) {
    // For now, simulate ZMQ with a channel-based approach
    // In production, this would bind to actual ZeroMQ socket

    info!("ZeroMQ receiver started");

    // Create a test channel for now - replace with actual ZMQ
    let (_tx, mut rx) = mpsc::channel::<IncomingMessage>(100);

    // Simulated receiver task - in production, use actual ZMQ socket
    tokio::spawn(async move {
        // Placeholder: Real ZMQ socket binding would go here
        // For now, just keep channel open
        loop {
            tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
        }
    });

    // Process incoming messages
    while let Some(msg) = rx.recv().await {
        let start_time = SystemTime::now();

        // Convert to RVMetric
        let metric = match create_metric(&msg) {
            Some(m) => m,
            None => {
                warn!("Failed to create metric from message");
                continue;
            }
        };

        debug!(
            "Received metric: R_V={:.3}, model={}",
            metric.r_v, metric.model_name
        );

        // Broadcast via WebSocket
        ws.broadcast(metric.clone());

        // Process through recognition detector
        let is_recognition = {
            let det = detector.read().await;
            match det.process(metric.clone()).await {
                Ok(recognized) => recognized,
                Err(e) => {
                    warn!("Recognition processing error: {}", e);
                    false
                }
            }
        };

        // Store in database (non-blocking)
        let db_clone = db.clone();
        let metric_clone = metric.clone();
        tokio::spawn(async move {
            if let Err(e) = db_clone.store_metric(&metric_clone, is_recognition).await {
                warn!("Database store error: {}", e);
            }
        });

        // Log latency
        let elapsed = start_time.elapsed().unwrap_or_default();
        if elapsed.as_millis() > 100 {
            warn!("High latency: {}ms", elapsed.as_millis());
        } else {
            debug!("Processing latency: {}ms", elapsed.as_millis());
        }
    }
}

/// Create RVMetric from incoming message
fn create_metric(msg: &IncomingMessage) -> Option<RVMetric> {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .ok()?
        .as_millis() as u64;

    if let Some(pre) = &msg.precomputed {
        // Use pre-computed values
        Some(RVMetric {
            timestamp,
            r_v: pre.r_v,
            pr_early: pre.pr_early,
            pr_late: pre.pr_late,
            layer_early: msg.layer_early,
            layer_late: msg.layer_late,
            model_name: msg.model_name.clone(),
        })
    } else {
        // Would compute SVD here if raw data provided
        // For now, return None - requires pre-computed or implement SVD
        warn!("Raw matrix computation not yet implemented, use precomputed metrics");
        None
    }
}

/// Handle recognition event
async fn handle_recognition_event(
    event: RecognitionEvent,
    db: Arc<PSMVDatabase>,
    ws: Arc<WebSocketServer>,
) {
    info!(
        "🎯 RECOGNITION: R_V={:.3}, separation={:.1}%",
        event.metric.r_v, event.separation_percent
    );

    // Store recognition event
    if let Err(e) = db.store_recognition_event(
        &event.metric,
        event.threshold,
        event.separation_percent,
        None,
    ).await {
        warn!("Failed to store recognition event: {}", e);
    }

    // Broadcast recognition event (special marker)
    ws.broadcast(event.metric.clone());
}

/// Full ZeroMQ broker implementation (placeholder for production)
#[allow(dead_code)]
async fn run_zmq_broker() -> anyhow::Result<()> {
    // This would implement the full ZeroMQ broker pattern
    // For now, the channel-based approach above is used

    // Example implementation structure:
    // let mut frontend = zeromq::PullSocket::new();
    // let mut backend = zeromq::PushSocket::new();
    // frontend.bind(ZMQ_INPUT_ADDR).await?;
    // backend.bind(ZMQ_OUTPUT_ADDR).await?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_metric() {
        let msg = IncomingMessage {
            model_name: "test-model".to_string(),
            layer_early: 5,
            layer_late: 27,
            v_early: None,
            v_late: None,
            precomputed: Some(PrecomputedMetrics {
                r_v: 0.85,
                pr_early: 1.0,
                pr_late: 0.85,
            }),
        };

        let metric = create_metric(&msg).unwrap();
        assert_eq!(metric.r_v, 0.85);
        assert_eq!(metric.model_name, "test-model");
    }
}
