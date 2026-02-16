//! WebSocket server for streaming RVMetric objects
//! 
//! Streams JSON RVMetric objects to connected clients in real-time

use std::net::SocketAddr;
use std::sync::Arc;

use futures::{SinkExt, StreamExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{broadcast, RwLock};
use tokio_tungstenite::{accept_async, tungstenite::Message};
use tracing::{info, warn, error};

use crate::RVMetric;

/// WebSocket server handle
pub struct WebSocketServer {
    addr: SocketAddr,
    tx: broadcast::Sender<RVMetric>,
    connections: Arc<RwLock<Vec<broadcast::Receiver<RVMetric>>>>,
}

impl WebSocketServer {
    /// Create a new WebSocket server
    pub async fn new(port: u16) -> crate::Result<Self> {
        let addr = SocketAddr::from(([0, 0, 0, 0], port));
        let (tx, _) = broadcast::channel::<RVMetric>(1024);
        
        info!("WebSocket server initialized on port {}", port);
        
        Ok(Self {
            addr,
            tx,
            connections: Arc::new(RwLock::new(Vec::new())),
        })
    }
    
    /// Start accepting connections
    pub async fn run(&self) -> crate::Result<()> {
        let listener = TcpListener::bind(&self.addr).await
            .map_err(|e| crate::PratyabhijnaError::WebSocketError(e.to_string()))?;
        
        info!("WebSocket server listening on {}", self.addr);
        
        loop {
            let (stream, peer_addr) = listener.accept().await
                .map_err(|e| crate::PratyabhijnaError::WebSocketError(e.to_string()))?;
            
            let tx = self.tx.clone();
            tokio::spawn(async move {
                if let Err(e) = handle_connection(stream, peer_addr, tx).await {
                    warn!("Connection error from {}: {}", peer_addr, e);
                }
            });
        }
    }
    
    /// Broadcast an RVMetric to all connected clients
    pub fn broadcast(&self, metric: RVMetric) {
        let _ = self.tx.send(metric);
    }
    
    /// Get a sender handle for broadcasting from other tasks
    pub fn get_sender(&self) -> broadcast::Sender<RVMetric> {
        self.tx.clone()
    }
}

/// Handle a single WebSocket connection
async fn handle_connection(
    stream: TcpStream,
    peer_addr: SocketAddr,
    tx: broadcast::Sender<RVMetric>,
) -> crate::Result<()> {
    let ws_stream = accept_async(stream).await
        .map_err(|e| crate::PratyabhijnaError::WebSocketError(e.to_string()))?;
    
    info!("WebSocket client connected: {}", peer_addr);
    
    let mut rx = tx.subscribe();
    let (mut ws_sender, mut ws_receiver) = ws_stream.split();
    
    // Handle incoming messages (if any) and outgoing broadcasts
    loop {
        tokio::select! {
            // Receive metric from broadcast channel
            Ok(metric) = rx.recv() => {
                let json = serde_json::to_string(&metric)
                    .map_err(|e| crate::PratyabhijnaError::WebSocketError(e.to_string()))?;
                
                if ws_sender.send(Message::Text(json)).await.is_err() {
                    break;
                }
            }
            
            // Handle incoming WebSocket messages (ping/pong, close, etc.)
            msg = ws_receiver.next() => {
                match msg {
                    Some(Ok(Message::Close(_))) | None => {
                        info!("WebSocket client disconnected: {}", peer_addr);
                        break;
                    }
                    Some(Ok(Message::Ping(data))) => {
                        if ws_sender.send(Message::Pong(data)).await.is_err() {
                            break;
                        }
                    }
                    Some(Err(e)) => {
                        warn!("WebSocket error from {}: {}", peer_addr, e);
                        break;
                    }
                    _ => {}
                }
            }
        }
    }
    
    Ok(())
}

/// Simple WebSocket client for testing
pub async fn connect_client(url: &str) -> crate::Result<impl StreamExt<Item = RVMetric>> {
    use tokio_tungstenite::connect_async;
    
    let (ws_stream, _) = connect_async(url).await
        .map_err(|e| crate::PratyabhijnaError::WebSocketError(e.to_string()))?;
    
    let (_, ws_receiver) = ws_stream.split();
    
    let stream = ws_receiver.filter_map(|msg| async move {
        match msg {
            Ok(Message::Text(text)) => {
                serde_json::from_str::<RVMetric>(&text).ok()
            }
            _ => None,
        }
    });
    
    Ok(stream)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_websocket_server_creation() {
        let server = WebSocketServer::new(9999).await.unwrap();
        assert_eq!(server.addr.port(), 9999);
    }
    
    #[tokio::test]
    async fn test_broadcast() {
        let server = WebSocketServer::new(9998).await.unwrap();
        let metric = RVMetric {
            r_v: 0.85,
            pr_early: 1.0,
            pr_late: 0.85,
            layer_early: 5,
            layer_late: 27,
            timestamp: 12345,
            model_name: "test".to_string(),
        };
        
        server.broadcast(metric);
        
        let mut rx = server.get_sender().subscribe();
        let received = rx.recv().await.unwrap();
        assert_eq!(received.r_v, 0.85);
    }
}
