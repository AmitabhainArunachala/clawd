//! Kaizen Agent System - MVP Implementation
//! 
//! This module implements a minimal viable Kaizen (改善) Agent System based on
//! Toyota Production System (TPS) principles. The system emphasizes continuous
//! improvement through waste elimination and flow optimization.
//!
//! ## TPS Principles Applied:
//! 
//! 1. **Just-In-Time (JIT)** - Tasks are pulled only when capacity is available
//! 2. **Jidoka** - Autonomous agents with built-in quality checks
//! 3. **Muda (Waste)** - Seven types of waste tracked and minimized
//! 4. **Kanban** - Visual workflow management with WIP limits
//! 5. **Kaizen** - Continuous improvement through metrics
//!
//! ## The Seven Wastes (Muda):
//! - Overproduction: Doing more than needed
//! - Waiting: Idle time between tasks
//! - Transport: Unnecessary movement of work
//! - Overprocessing: Excessive refinement
//! - Inventory: Backlog of unstarted work
//! - Motion: Unnecessary agent activity
//! - Defects: Rework due to errors

use async_trait::async_trait;
use std::collections::VecDeque;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::{mpsc, Mutex, RwLock};

// ============================================================================
// CORE TRAITS
// ============================================================================

/// A Task represents a unit of work to be processed by an Agent.
/// In TPS terms, this is the "value" that flows through the system.
pub trait Task: Send + Sync + 'static {
    /// Unique identifier for this task
    fn id(&self) -> u64;
    
    /// Human-readable description
    fn description(&self) -> &str;
    
    /// Estimated complexity (affects processing time simulation)
    fn complexity(&self) -> u32;
    
    /// Process the task. Returns Ok(()) on success, Err on failure.
    /// This is where the actual value-adding work happens.
    fn execute(&self) -> Result<(), TaskError>;
}

/// Errors that can occur during task execution
#[derive(Debug, Clone)]
pub enum TaskError {
    /// Defect detected - requires rework (muda: defects)
    Defect(String),
    /// Task cannot be processed
    Invalid(String),
    /// Processing was interrupted
    Interrupted,
}

impl std::fmt::Display for TaskError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TaskError::Defect(msg) => write!(f, "Defect: {}", msg),
            TaskError::Invalid(msg) => write!(f, "Invalid: {}", msg),
            TaskError::Interrupted => write!(f, "Interrupted"),
        }
    }
}

impl std::error::Error for TaskError {}

/// An Agent is an autonomous worker that pulls tasks from a Kanban board.
/// Implements the Jidoka principle: agents have autonomy and stop on defects.
pub trait Agent: Send + Sync + 'static {
    /// Unique identifier for this agent
    fn id(&self) -> &str;
    
    /// Agent capability - what complexity levels can this agent handle?
    fn max_complexity(&self) -> u32;
    
    /// Process a single task.
    /// Returns the time taken and any waste generated during processing.
    fn process_task(&self, task: &dyn Task) -> (Duration, WasteLog);
}

/// Kanban board manages the flow of work through different stages.
/// Implements pull-based workflow with WIP (Work In Progress) limits.
#[async_trait]
pub trait Kanban: Send + Sync + 'static {
    /// Add a new task to the backlog (Todo column)
    async fn enqueue(&self, task: Box<dyn Task>);
    
    /// Pull the next available task (Just-In-Time)
    async fn pull(&self) -> Option<Box<dyn Task>>;
    
    /// Mark a task as completed
    async fn complete(&self, task_id: u64, waste: WasteLog, duration: Duration);
    
    /// Get current metrics snapshot
    async fn metrics(&self) -> MetricsSnapshot;
}

// ============================================================================
// WASTE TRACKING (MUDA)
// ============================================================================

/// The seven types of waste in TPS (Muda)
#[derive(Debug, Clone, Copy, Default)]
pub struct WasteLog {
    /// Overproduction: Doing more work than required
    pub overproduction: Duration,
    /// Waiting: Time spent waiting for resources/inputs
    pub waiting: Duration,
    /// Transport: Time spent moving/handling work unnecessarily
    pub transport: Duration,
    /// Overprocessing: Excessive refinement beyond requirements
    pub overprocessing: Duration,
    /// Inventory: Time work sits idle in queues
    pub inventory: Duration,
    /// Motion: Unnecessary agent activity
    pub motion: Duration,
    /// Defects: Time spent on rework
    pub defects: Duration,
}

impl WasteLog {
    pub fn new() -> Self {
        Self::default()
    }
    
    /// Total waste time
    pub fn total(&self) -> Duration {
        self.overproduction + self.waiting + self.transport + 
        self.overprocessing + self.inventory + self.motion + self.defects
    }
    
    /// Create a waste log for waiting time
    pub fn waiting(duration: Duration) -> Self {
        let mut log = Self::new();
        log.waiting = duration;
        log
    }
    
    /// Create a waste log for defects/rework
    pub fn defects(duration: Duration) -> Self {
        let mut log = Self::new();
        log.defects = duration;
        log
    }
}

impl std::ops::Add for WasteLog {
    type Output = Self;
    
    fn add(self, rhs: Self) -> Self::Output {
        WasteLog {
            overproduction: self.overproduction + rhs.overproduction,
            waiting: self.waiting + rhs.waiting,
            transport: self.transport + rhs.transport,
            overprocessing: self.overprocessing + rhs.overprocessing,
            inventory: self.inventory + rhs.inventory,
            motion: self.motion + rhs.motion,
            defects: self.defects + rhs.defects,
        }
    }
}

impl std::iter::Sum for WasteLog {
    fn sum<I: Iterator<Item = Self>>(iter: I) -> Self {
        iter.fold(WasteLog::new(), |a, b| a + b)
    }
}

// ============================================================================
// METRICS
// ============================================================================

/// Real-time metrics snapshot for system monitoring
#[derive(Debug, Clone)]
pub struct MetricsSnapshot {
    /// Tasks completed successfully
    pub completed: u64,
    /// Tasks that failed (defects)
    pub failed: u64,
    /// Tasks currently in progress
    pub in_progress: u64,
    /// Tasks waiting in backlog
    pub backlog: usize,
    /// Total value-added time (actual processing)
    pub value_added_time: Duration,
    /// Total waste time by category
    pub total_waste: WasteLog,
    /// Average cycle time (time from start to completion)
    pub avg_cycle_time: Duration,
    /// Throughput: tasks per minute
    pub throughput: f64,
}

impl Default for MetricsSnapshot {
    fn default() -> Self {
        Self {
            completed: 0,
            failed: 0,
            in_progress: 0,
            backlog: 0,
            value_added_time: Duration::ZERO,
            total_waste: WasteLog::new(),
            avg_cycle_time: Duration::ZERO,
            throughput: 0.0,
        }
    }
}

/// Internal metrics tracking (thread-safe)
struct Metrics {
    completed: AtomicU64,
    failed: AtomicU64,
    in_progress: AtomicU64,
    total_value_time_ms: AtomicU64,
    total_waste_ms: Mutex<WasteLog>,
    cycle_times_ms: Mutex<Vec<u64>>,
    start_time: Instant,
}

impl Metrics {
    fn new() -> Self {
        Self {
            completed: AtomicU64::new(0),
            failed: AtomicU64::new(0),
            in_progress: AtomicU64::new(0),
            total_value_time_ms: AtomicU64::new(0),
            total_waste_ms: Mutex::new(WasteLog::new()),
            cycle_times_ms: Mutex::new(Vec::new()),
            start_time: Instant::now(),
        }
    }
    
    async fn record_completion(&self, cycle_time_ms: u64, value_time_ms: u64, waste: WasteLog) {
        self.completed.fetch_add(1, Ordering::SeqCst);
        self.in_progress.fetch_sub(1, Ordering::SeqCst);
        self.total_value_time_ms.fetch_add(value_time_ms, Ordering::SeqCst);
        
        let mut waste_guard = self.total_waste_ms.lock().await;
        *waste_guard = waste_guard.clone() + waste;
        
        let mut cycle_guard = self.cycle_times_ms.lock().await;
        cycle_guard.push(cycle_time_ms);
    }
    
    async fn record_failure(&self) {
        self.failed.fetch_add(1, Ordering::SeqCst);
        self.in_progress.fetch_sub(1, Ordering::SeqCst);
    }
    
    async fn snapshot(&self, backlog_size: usize) -> MetricsSnapshot {
        let completed = self.completed.load(Ordering::SeqCst);
        let failed = self.failed.load(Ordering::SeqCst);
        let in_progress = self.in_progress.load(Ordering::SeqCst);
        let value_time_ms = self.total_value_time_ms.load(Ordering::SeqCst);
        let waste = self.total_waste_ms.lock().await.clone();
        let cycle_times = self.cycle_times_ms.lock().await.clone();
        
        let elapsed_minutes = self.start_time.elapsed().as_secs_f64() / 60.0;
        let throughput = if elapsed_minutes > 0.0 {
            completed as f64 / elapsed_minutes
        } else {
            0.0
        };
        
        let avg_cycle_ms = if !cycle_times.is_empty() {
            cycle_times.iter().sum::<u64>() / cycle_times.len() as u64
        } else {
            0
        };
        
        MetricsSnapshot {
            completed,
            failed,
            in_progress,
            backlog: backlog_size,
            value_added_time: Duration::from_millis(value_time_ms),
            total_waste: waste,
            avg_cycle_time: Duration::from_millis(avg_cycle_ms),
            throughput,
        }
    }
}

// ============================================================================
// WORK QUEUE (Kanban Implementation)
// ============================================================================

/// A simple Kanban board with WIP limits and pull-based workflow.
/// 
/// # TPS Principle: Just-In-Time
/// Tasks are only pulled when an agent has capacity. This prevents
/// overproduction and keeps work flowing smoothly.
/// 
/// # TPS Principle: WIP Limits
/// Limiting work in progress exposes bottlenecks and reduces inventory waste.
pub struct SimpleKanban {
    /// Tasks waiting to be pulled (Todo column)
    backlog: Mutex<VecDeque<Box<dyn Task>>>,
    /// Tasks currently being worked on (In Progress column)
    in_progress: RwLock<Vec<u64>>, // Just track IDs
    /// Completed tasks with their metrics (Done column)
    completed: Mutex<Vec<(u64, WasteLog, Duration)>>,
    /// Maximum work in progress (WIP limit)
    wip_limit: usize,
    /// Channel for task distribution (reserved for future use)
    _tx: mpsc::Sender<Box<dyn Task>>,
    rx: Mutex<mpsc::Receiver<Box<dyn Task>>>,
    /// Metrics tracking
    metrics: Arc<Metrics>,
}

impl SimpleKanban {
    /// Create a new Kanban board with specified WIP limit
    pub fn new(wip_limit: usize) -> Arc<Self> {
        let (tx, rx) = mpsc::channel(100);
        Arc::new(Self {
            backlog: Mutex::new(VecDeque::new()),
            in_progress: RwLock::new(Vec::new()),
            completed: Mutex::new(Vec::new()),
            wip_limit,
            _tx: tx,
            rx: Mutex::new(rx),
            metrics: Arc::new(Metrics::new()),
        })
    }
    
    /// Start the work distribution loop
    pub async fn run(self: Arc<Self>) {
        let rx = self.rx.lock().await;
        // The receiver is held; in production, you'd spawn a task here
        drop(rx);
    }
    
    /// Get current WIP count
    async fn current_wip(&self) -> usize {
        self.in_progress.read().await.len()
    }
    
    /// Check if we can accept more work
    async fn can_pull(&self) -> bool {
        self.current_wip().await < self.wip_limit
    }
}

#[async_trait::async_trait]
impl Kanban for SimpleKanban {
    async fn enqueue(&self, task: Box<dyn Task>) {
        let mut backlog = self.backlog.lock().await;
        backlog.push_back(task);
    }
    
    async fn pull(&self) -> Option<Box<dyn Task>> {
        // Check WIP limit (TPS: limit work in progress)
        if !self.can_pull().await {
            return None;
        }
        
        let mut backlog = self.backlog.lock().await;
        if let Some(task) = backlog.pop_front() {
            // Track that this task is now in progress
            let mut in_progress = self.in_progress.write().await;
            in_progress.push(task.id());
            self.metrics.in_progress.fetch_add(1, Ordering::SeqCst);
            Some(task)
        } else {
            None
        }
    }
    
    async fn complete(&self, task_id: u64, waste: WasteLog, duration: Duration) {
        // Remove from in-progress
        let mut in_progress = self.in_progress.write().await;
        if let Some(pos) = in_progress.iter().position(|&id| id == task_id) {
            in_progress.remove(pos);
        }
        
        // Add to completed
        let mut completed = self.completed.lock().await;
        completed.push((task_id, waste.clone(), duration));
        
        // Update metrics
        self.metrics.record_completion(
            duration.as_millis() as u64,
            duration.saturating_sub(waste.total()).as_millis() as u64,
            waste,
        ).await;
    }
    
    async fn metrics(&self) -> MetricsSnapshot {
        let backlog_size = self.backlog.lock().await.len();
        self.metrics.snapshot(backlog_size).await
    }
}

// ============================================================================
// SIMPLE IMPLEMENTATIONS
// ============================================================================

/// A basic task implementation for testing
pub struct SimpleTask {
    id: u64,
    description: String,
    complexity: u32,
    should_fail: bool,
}

impl SimpleTask {
    pub fn new(id: u64, description: impl Into<String>, complexity: u32) -> Self {
        Self {
            id,
            description: description.into(),
            complexity,
            should_fail: false,
        }
    }
    
    pub fn with_failure(mut self) -> Self {
        self.should_fail = true;
        self
    }
}

impl Task for SimpleTask {
    fn id(&self) -> u64 {
        self.id
    }
    
    fn description(&self) -> &str {
        &self.description
    }
    
    fn complexity(&self) -> u32 {
        self.complexity
    }
    
    fn execute(&self) -> Result<(), TaskError> {
        if self.should_fail {
            return Err(TaskError::Defect("Simulated defect".to_string()));
        }
        
        // Simulate value-adding work
        // In real use, this would do actual processing
        let work_time = self.complexity as u64 * 10; // 10ms per complexity unit
        std::thread::sleep(Duration::from_millis(work_time));
        
        Ok(())
    }
}

/// A basic agent implementation
pub struct SimpleAgent {
    id: String,
    max_complexity: u32,
    base_processing_time_ms: u64,
}

impl SimpleAgent {
    pub fn new(id: impl Into<String>, max_complexity: u32) -> Self {
        Self {
            id: id.into(),
            max_complexity,
            base_processing_time_ms: 50, // Base overhead per task
        }
    }
}

impl Agent for SimpleAgent {
    fn id(&self) -> &str {
        &self.id
    }
    
    fn max_complexity(&self) -> u32 {
        self.max_complexity
    }
    
    fn process_task(&self, task: &dyn Task) -> (Duration, WasteLog) {
        let start = Instant::now();
        let mut waste = WasteLog::new();
        
        // Simulate motion waste: agent setup time
        let motion_time = Duration::from_millis(self.base_processing_time_ms);
        std::thread::sleep(motion_time);
        waste.motion = motion_time;
        
        // Check if agent can handle this complexity (Jidoka: built-in quality check)
        if task.complexity() > self.max_complexity {
            let wait_time = Duration::from_millis(20);
            waste.waiting = wait_time;
            return (start.elapsed(), waste);
        }
        
        // Execute the task (value-adding time)
        let exec_start = Instant::now();
        match task.execute() {
            Ok(()) => {
                // Success - minimal waste
            }
            Err(TaskError::Defect(_)) => {
                // Defect detected - add rework waste
                let defect_time = Duration::from_millis(task.complexity() as u64 * 5);
                waste.defects = defect_time;
            }
            Err(_) => {
                // Other errors
                waste.overprocessing = Duration::from_millis(10);
            }
        }
        
        let total_time = start.elapsed();
        
        // Calculate waiting time as any non-value-add, non-motion time
        // In a real system, this would be tracked separately
        let tracked_time = waste.total() + exec_start.elapsed();
        if total_time > tracked_time {
            waste.waiting = waste.waiting + (total_time - tracked_time);
        }
        
        (total_time, waste)
    }
}

// ============================================================================
// WORKER LOOP
// ============================================================================

/// Run an agent worker that continuously pulls and processes tasks.
/// 
/// # TPS Principle: Pull System
/// Agents pull work only when they have capacity (Just-In-Time).
/// 
/// # TPS Principle: Jidoka (Autonomation)
/// Agents work autonomously and stop on defects (simulated here).
pub async fn run_agent_worker(
    agent: Arc<dyn Agent>,
    kanban: Arc<dyn Kanban>,
    shutdown: tokio::sync::watch::Receiver<bool>,
) {
    let shutdown = shutdown;
    
    loop {
        // Check for shutdown signal
        if *shutdown.borrow() {
            break;
        }
        
        // Pull next task (Just-In-Time: only take work when ready)
        if let Some(task) = kanban.pull().await {
            let task_id = task.id();
            let task_desc = task.description().to_string();
            
            println!("[{}] Processing task {}: {}", agent.id(), task_id, task_desc);
            
            // Process the task
            let (duration, waste) = agent.process_task(task.as_ref());
            
            // Report completion with waste metrics
            kanban.complete(task_id, waste.clone(), duration).await;
            
            println!(
                "[{}] Completed task {} in {:?} (waste: {:?})",
                agent.id(), task_id, duration, waste.total()
            );
        } else {
            // No work available - small yield to prevent busy waiting
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
    }
    
    println!("[{}] Shutting down", agent.id());
}

// ============================================================================
// EXPORTS
// ============================================================================

pub use std::time::Duration as StdDuration;
