//! Kaizen Agent System - Example Usage
//!
//! This example demonstrates the Kaizen Agent System with 3 agents
//! processing tasks while tracking waste according to TPS principles.

use kaizen_agent::*;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::watch;
use tokio::time::{interval, MissedTickBehavior};

#[tokio::main]
async fn main() {
    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║         Kaizen Agent System - TPS Implementation             ║");
    println!("║                                                              ║");
    println!("║  Principles: JIT (Just-In-Time) | Jidoka | Muda (Waste)      ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");
    
    // ====================================================================
    // Setup: Create Kanban board with WIP limit
    // ====================================================================
    // WIP (Work In Progress) limit prevents inventory waste by restricting
    // how many tasks can be active at once. This exposes bottlenecks
    // and encourages flow.
    let wip_limit = 3;
    let kanban: Arc<dyn Kanban> = SimpleKanban::new(wip_limit);
    
    println!("📋 Kanban board created with WIP limit: {}", wip_limit);
    println!();
    
    // ====================================================================
    // Setup: Create 3 agents with different capabilities
    // ====================================================================
    // Agents have different complexity limits, simulating a heterogeneous
    // workforce. This demonstrates the Jidoka principle: agents have
    // autonomy and won't take tasks beyond their capability.
    let agents: Vec<Arc<dyn Agent>> = vec![
        Arc::new(SimpleAgent::new("Agent-Alpha", 5)),    // Can handle complexity 1-5
        Arc::new(SimpleAgent::new("Agent-Beta", 3)),     // Can handle complexity 1-3
        Arc::new(SimpleAgent::new("Agent-Gamma", 4)),    // Can handle complexity 1-4
    ];
    
    println!("🤖 Agents created:");
    for agent in &agents {
        println!("   • {} (max complexity: {})", agent.id(), agent.max_complexity());
    }
    println!();
    
    // ====================================================================
    // Setup: Create tasks with varying complexity
    // ====================================================================
    // Tasks represent the "value" flowing through the system.
    // Complexity simulates different types of work.
    let tasks: Vec<Box<dyn Task>> = vec![
        Box::new(SimpleTask::new(1, "Simple data validation", 1)),
        Box::new(SimpleTask::new(2, "User authentication", 2)),
        Box::new(SimpleTask::new(3, "Complex report generation", 5)),
        Box::new(SimpleTask::new(4, "Email notification", 1)),
        Box::new(SimpleTask::new(5, "Database migration", 4)),
        Box::new(SimpleTask::new(6, "API integration", 3)),
        Box::new(SimpleTask::new(7, "Log analysis", 2)),
        Box::new(SimpleTask::new(8, "Payment processing", 3)),
        Box::new(SimpleTask::new(9, "High complexity ML task", 5)),
        Box::new(SimpleTask::new(10, "Simple health check", 1)),
        // One task that will fail (demonstrates defect tracking)
        Box::new(SimpleTask::new(11, "Buggy legacy code", 2).with_failure()),
        Box::new(SimpleTask::new(12, "Cache refresh", 1)),
    ];
    
    println!("📦 {} tasks queued:", tasks.len());
    for task in &tasks {
        println!("   • Task {}: {} (complexity: {})", 
            task.id(), task.description(), task.complexity());
    }
    println!();
    
    // Enqueue all tasks
    for task in tasks {
        kanban.enqueue(task).await;
    }
    
    // ====================================================================
    // Start agent workers
    // ====================================================================
    let (shutdown_tx, shutdown_rx) = watch::channel(false);
    let mut handles = vec![];
    
    for agent in agents {
        let kanban_clone = Arc::clone(&kanban);
        let shutdown_clone = shutdown_rx.clone();
        
        let handle = tokio::spawn(async move {
            run_agent_worker(agent, kanban_clone, shutdown_clone).await;
        });
        handles.push(handle);
    }
    
    // ====================================================================
    // Metrics reporter (runs in parallel)
    // ====================================================================
    // Continuous monitoring is essential for Kaizen (continuous improvement).
    // Metrics reveal waste patterns that guide improvement efforts.
    let kanban_metrics = Arc::clone(&kanban);
    let metrics_handle = tokio::spawn(async move {
        let mut interval = interval(Duration::from_secs(1));
        interval.set_missed_tick_behavior(MissedTickBehavior::Skip);
        
        for i in 0..15 {
            interval.tick().await;
            
            let m = kanban_metrics.metrics().await;
            println!("\n📊 Metrics snapshot {}/15:", i + 1);
            println!("   Completed: {} | Failed: {} | In Progress: {} | Backlog: {}",
                m.completed, m.failed, m.in_progress, m.backlog);
            println!("   Throughput: {:.2} tasks/min | Avg cycle time: {:?}",
                m.throughput, m.avg_cycle_time);
            
            // Show waste breakdown (Kaizen: identify and eliminate waste)
            let w = &m.total_waste;
            println!("   Waste breakdown:");
            println!("      • Motion:       {:?}", w.motion);
            println!("      • Waiting:      {:?}", w.waiting);
            println!("      • Defects:      {:?}", w.defects);
            println!("      • Overprocess:  {:?}", w.overprocessing);
            println!("      • Transport:    {:?}", w.transport);
            println!("      • Inventory:    {:?}", w.inventory);
            println!("      • Overprod:     {:?}", w.overproduction);
            println!("      ─────────────────────────");
            println!("      Total waste:    {:?}", w.total());
        }
    });
    
    // Wait for metrics to finish (15 seconds)
    let _ = metrics_handle.await;
    
    // Signal shutdown
    let _ = shutdown_tx.send(true);
    
    // Wait for all agents to finish
    for handle in handles {
        let _ = handle.await;
    }
    
    // ====================================================================
    // Final report
    // ====================================================================
    println!("\n");
    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║                    FINAL KAIZEN REPORT                       ║");
    println!("╚══════════════════════════════════════════════════════════════╝");
    
    let final_metrics = kanban.metrics().await;
    println!("\n✅ Completed tasks: {}", final_metrics.completed);
    println!("❌ Failed tasks: {}", final_metrics.failed);
    println!("⚡ Throughput: {:.2} tasks/minute", final_metrics.throughput);
    println!("⏱️  Average cycle time: {:?}", final_metrics.avg_cycle_time);
    println!("💎 Value-added time: {:?}", final_metrics.value_added_time);
    
    let w = final_metrics.total_waste;
    println!("\n🗑️  Total Waste Breakdown (Muda):");
    println!("   ┌─────────────────────────────────────────┐");
    println!("   │ Overproduction:  {:>20?} │", w.overproduction);
    println!("   │ Waiting:         {:>20?} │", w.waiting);
    println!("   │ Transport:       {:>20?} │", w.transport);
    println!("   │ Overprocessing:  {:>20?} │", w.overprocessing);
    println!("   │ Inventory:       {:>20?} │", w.inventory);
    println!("   │ Motion:          {:>20?} │", w.motion);
    println!("   │ Defects:         {:>20?} │", w.defects);
    println!("   ├─────────────────────────────────────────┤");
    println!("   │ TOTAL WASTE:     {:>20?} │", w.total());
    println!("   └─────────────────────────────────────────┘");
    
    println!("\n📈 Kaizen Recommendations:");
    if w.defects > Duration::ZERO {
        println!("   1. Implement better quality checks to reduce defect waste");
    }
    if w.waiting > w.motion {
        println!("   2. Balance workload better to reduce waiting time");
    }
    if w.motion > Duration::from_millis(100) {
        println!("   3. Reduce agent setup overhead (motion waste)");
    }
    println!("   4. Review WIP limit - adjust based on throughput data");
    
    println!("\n🏁 System shutdown complete. Arigatou gozaimasu!");
}
