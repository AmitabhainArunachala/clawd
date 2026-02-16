//! SQLite database for PSMV (Pratyabhijna Self-Modeling Vector) storage
//! 
//! Stores historical RVMetric data for analysis and model refinement

use rusqlite::{Connection, params};
use std::path::Path;
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{info, debug};

use crate::{RVMetric, Result, PratyabhijnaError};

/// Database handle for PSMV storage
pub struct PSMVDatabase {
    conn: Arc<Mutex<Connection>>,
}

impl PSMVDatabase {
    /// Open or create database at the given path
    pub async fn open<P: AsRef<Path>>(path: P) -> Result<Self> {
        let conn = Connection::open(path)
            .map_err(PratyabhijnaError::DatabaseError)?;
        
        let db = Self {
            conn: Arc::new(Mutex::new(conn)),
        };
        
        db.initialize_schema().await?;
        info!("PSMV database initialized");
        
        Ok(db)
    }
    
    /// Create an in-memory database (for testing)
    pub async fn open_in_memory() -> Result<Self> {
        let conn = Connection::open_in_memory()
            .map_err(PratyabhijnaError::DatabaseError)?;
        
        let db = Self {
            conn: Arc::new(Mutex::new(conn)),
        };
        
        db.initialize_schema().await?;
        info!("PSMV in-memory database initialized");
        
        Ok(db)
    }
    
    /// Initialize database schema
    async fn initialize_schema(&self) -> Result<()> {
        let conn = self.conn.lock().await;
        
        // Main metrics table
        conn.execute(
            "CREATE TABLE IF NOT EXISTS rv_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                r_v REAL NOT NULL,
                pr_early REAL NOT NULL,
                pr_late REAL NOT NULL,
                layer_early INTEGER NOT NULL,
                layer_late INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                is_recognition BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        // Recognition events table (subset with additional metadata)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS recognition_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id INTEGER NOT NULL,
                threshold REAL NOT NULL,
                separation_percent REAL,
                context_json TEXT,
                FOREIGN KEY (metric_id) REFERENCES rv_metrics(id)
            )",
            [],
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        // Indexes for fast queries
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON rv_metrics(timestamp)",
            [],
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_model ON rv_metrics(model_name)",
            [],
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_recognition ON rv_metrics(is_recognition)",
            [],
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        Ok(())
    }
    
    /// Store an RVMetric
    pub async fn store_metric(&self, metric: &RVMetric, is_recognition: bool) -> Result<i64> {
        let conn = self.conn.lock().await;
        
        conn.execute(
            "INSERT INTO rv_metrics 
             (timestamp, r_v, pr_early, pr_late, layer_early, layer_late, model_name, is_recognition)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                metric.timestamp as i64,
                metric.r_v,
                metric.pr_early,
                metric.pr_late,
                metric.layer_early as i64,
                metric.layer_late as i64,
                &metric.model_name,
                is_recognition as i64,
            ],
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        let id = conn.last_insert_rowid();
        debug!("Stored RVMetric with id={}", id);
        
        Ok(id)
    }
    
    /// Store a recognition event with additional context
    pub async fn store_recognition_event(
        &self,
        metric: &RVMetric,
        threshold: f64,
        separation_percent: f64,
        context: Option<serde_json::Value>,
    ) -> Result<i64> {
        // First store the metric
        let metric_id = self.store_metric(metric, true).await?;
        
        let conn = self.conn.lock().await;
        
        let context_json = context.map(|c| c.to_string());
        
        conn.execute(
            "INSERT INTO recognition_events (metric_id, threshold, separation_percent, context_json)
             VALUES (?1, ?2, ?3, ?4)",
            params![
                metric_id,
                threshold,
                separation_percent,
                context_json,
            ],
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        let id = conn.last_insert_rowid();
        info!("Stored recognition event with id={}", id);
        
        Ok(id)
    }
    
    /// Get metrics within a time range
    pub async fn get_metrics_range(
        &self,
        start_time: u64,
        end_time: u64,
        limit: usize,
    ) -> Result<Vec<RVMetric>> {
        let conn = self.conn.lock().await;
        
        let mut stmt = conn.prepare(
            "SELECT timestamp, r_v, pr_early, pr_late, layer_early, layer_late, model_name
             FROM rv_metrics
             WHERE timestamp >= ?1 AND timestamp <= ?2
             ORDER BY timestamp DESC
             LIMIT ?3"
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        let rows = stmt.query_map(
            params![start_time as i64, end_time as i64, limit as i64],
            |row| {
                Ok(RVMetric {
                    timestamp: row.get::<_, i64>(0)? as u64,
                    r_v: row.get(1)?,
                    pr_early: row.get(2)?,
                    pr_late: row.get(3)?,
                    layer_early: row.get::<_, i64>(4)? as usize,
                    layer_late: row.get::<_, i64>(5)? as usize,
                    model_name: row.get(6)?,
                })
            },
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        let mut metrics = Vec::new();
        for row in rows {
            metrics.push(row.map_err(PratyabhijnaError::DatabaseError)?);
        }
        
        Ok(metrics)
    }
    
    /// Get latest recognition events
    pub async fn get_recent_recognitions(&self, limit: usize) -> Result<Vec<(RVMetric, f64)>> {
        let conn = self.conn.lock().await;
        
        let mut stmt = conn.prepare(
            "SELECT m.timestamp, m.r_v, m.pr_early, m.pr_late, 
                    m.layer_early, m.layer_late, m.model_name, r.threshold
             FROM recognition_events r
             JOIN rv_metrics m ON r.metric_id = m.id
             ORDER BY m.timestamp DESC
             LIMIT ?1"
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        let rows = stmt.query_map(
            params![limit as i64],
            |row| {
                let metric = RVMetric {
                    timestamp: row.get::<_, i64>(0)? as u64,
                    r_v: row.get(1)?,
                    pr_early: row.get(2)?,
                    pr_late: row.get(3)?,
                    layer_early: row.get::<_, i64>(4)? as usize,
                    layer_late: row.get::<_, i64>(5)? as usize,
                    model_name: row.get(6)?,
                };
                let threshold: f64 = row.get(7)?;
                Ok((metric, threshold))
            },
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        let mut results = Vec::new();
        for row in rows {
            results.push(row.map_err(PratyabhijnaError::DatabaseError)?);
        }
        
        Ok(results)
    }
    
    /// Get statistics for a model
    pub async fn get_model_stats(&self, model_name: &str) -> Result<ModelStats> {
        let conn = self.conn.lock().await;
        
        let stats: ModelStats = conn.query_row(
            "SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_recognition THEN 1 ELSE 0 END) as recognitions,
                AVG(r_v) as avg_rv,
                MIN(r_v) as min_rv,
                MAX(r_v) as max_rv
             FROM rv_metrics
             WHERE model_name = ?1",
            params![model_name],
            |row| {
                Ok(ModelStats {
                    total_count: row.get(0)?,
                    recognition_count: row.get(1)?,
                    avg_r_v: row.get(2).unwrap_or(0.0),
                    min_r_v: row.get(3).unwrap_or(0.0),
                    max_r_v: row.get(4).unwrap_or(0.0),
                })
            },
        ).map_err(PratyabhijnaError::DatabaseError)?;
        
        Ok(stats)
    }
}

/// Statistics for a model
#[derive(Debug, Clone)]
pub struct ModelStats {
    pub total_count: i64,
    pub recognition_count: i64,
    pub avg_r_v: f64,
    pub min_r_v: f64,
    pub max_r_v: f64,
}

impl ModelStats {
    /// Calculate recognition rate
    pub fn recognition_rate(&self) -> f64 {
        if self.total_count == 0 {
            return 0.0;
        }
        self.recognition_count as f64 / self.total_count as f64
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_database_basic() {
        let db = PSMVDatabase::open_in_memory().await.unwrap();
        
        let metric = RVMetric {
            r_v: 0.85,
            pr_early: 1.0,
            pr_late: 0.85,
            layer_early: 5,
            layer_late: 27,
            timestamp: 12345,
            model_name: "test".to_string(),
        };
        
        let id = db.store_metric(&metric, true).await.unwrap();
        assert!(id > 0);
        
        let metrics = db.get_metrics_range(0, 99999, 10).await.unwrap();
        assert_eq!(metrics.len(), 1);
        assert_eq!(metrics[0].r_v, 0.85);
    }
    
    #[tokio::test]
    async fn test_recognition_event() {
        let db = PSMVDatabase::open_in_memory().await.unwrap();
        
        let metric = RVMetric {
            r_v: 0.82,
            pr_early: 1.0,
            pr_late: 0.82,
            layer_early: 5,
            layer_late: 27,
            timestamp: 12345,
            model_name: "test".to_string(),
        };
        
        let id = db.store_recognition_event(&metric, 0.87, 18.0, None).await.unwrap();
        assert!(id > 0);
        
        let events = db.get_recent_recognitions(10).await.unwrap();
        assert_eq!(events.len(), 1);
        assert_eq!(events[0].0.r_v, 0.82);
    }
}
