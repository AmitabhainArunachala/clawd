#!/usr/bin/env python3
"""
🔥 DHARMIC_CLAW HOURLY CYCLE
============================

Runs every hour via cron.
Implements proactive master plan execution + MOLBOOK SWARM POLLING.

Cron:
0 * * * * /Users/dhyana/clawd/hourly_cycle.py >> /Users/dhyana/clawd/logs/hourly.log 2>&1
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path("/Users/dhyana/clawd")))

# Import our systems
try:
    from dharmic_claw_messaging import MessagingChannel, send_daily_summary
    MESSAGING_AVAILABLE = True
except ImportError:
    MESSAGING_AVAILABLE = False

try:
    from jikoku_emitter import JikokuEmitter
    JIKOKU_AVAILABLE = True
except ImportError:
    JIKOKU_AVAILABLE = False

CLAWD_DIR = Path("/Users/dhyana/clawd")
MASTER_PLAN = CLAWD_DIR / "MASTER_PLAN.md"
HOURLY_LOG = CLAWD_DIR / "logs" / "hourly.log"
STATE_FILE = CLAWD_DIR / ".hourly_state.json"
MOLTBOOK_DIR = Path("/Users/dhyana/DHARMIC_GODEL_CLAW/moltbook_swarm")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_hour": 0, "tasks_completed": [], "current_project": None, "last_swarm_check": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def read_master_plan():
    """Read and parse master plan"""
    if not MASTER_PLAN.exists():
        return None
    return MASTER_PLAN.read_text()

def update_master_plan_progress(task, status):
    """Append progress to master plan"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n### [{timestamp}] PROGRESS UPDATE\n**Task:** {task}\n**Status:** {status}\n"
    
    with open(MASTER_PLAN, "a") as f:
        f.write(entry)

# ============================================================================
# MOLTBOOK SWARM POLLING (NEW)
# ============================================================================

def poll_moltbook_swarm():
    """Poll Moltbook swarm for new observations"""
    log("\n[SWARM] Polling Moltbook swarm...")
    
    # Check if swarm is running
    state_file = MOLTBOOK_DIR / "state.json"
    if not state_file.exists():
        log("    ❌ Swarm state file not found")
        return None
    
    try:
        with open(state_file) as f:
            swarm_state = json.load(f)
        
        status = swarm_state.get("status", "unknown")
        cycles = swarm_state.get("cycles_completed", 0)
        log(f"    ✅ Swarm status: {status} (cycles: {cycles})")
        
    except Exception as e:
        log(f"    ❌ Error reading swarm state: {e}")
        return None
    
    # Read observations
    obs_file = MOLTBOOK_DIR / "memory" / "latest_observations.json"
    if not obs_file.exists():
        log("    ❌ No observations file")
        return None
    
    try:
        with open(obs_file) as f:
            data = json.load(f)
        
        observations = data.get("observations", [])
        log(f"    📊 Total observations: {len(observations)}")
        
        # Find high-quality posts (Q7+)
        high_quality = []
        for obs in observations:
            quality = obs.get("quality", 0)
            # Handle string qualities (some are strings in the data)
            try:
                quality = int(quality)
            except (ValueError, TypeError):
                quality = 0
            if quality >= 7:
                high_quality.append(obs)
        log(f"    🎯 High quality (Q7+): {len(high_quality)}")
        
        return {
            "status": status,
            "cycles": cycles,
            "total_observations": len(observations),
            "high_quality": high_quality,
            "timestamp": data.get("timestamp", "unknown")
        }
        
    except Exception as e:
        log(f"    ❌ Error reading observations: {e}")
        return None

def send_swarm_alert(swarm_data):
    """Send Discord alert for high-quality swarm observations"""
    if not MESSAGING_AVAILABLE:
        log("    ⚠️ Messaging not available")
        return
    
    high_quality = swarm_data.get("high_quality", [])
    if not high_quality:
        return
    
    # Helper to get quality as int
    def get_quality(obs):
        q = obs.get("quality", 0)
        try:
            return int(q)
        except (ValueError, TypeError):
            return 0
    
    # Only alert if we have Q8 or new Q7s since last check
    q8_posts = [obs for obs in high_quality if get_quality(obs) == 8]
    q7_posts = [obs for obs in high_quality if get_quality(obs) == 7]
    
    if not q8_posts and not q7_posts:
        return
    
    try:
        msg = MessagingChannel()
        
        # Build alert message
        alert = "🕸️ **MOLTBOOK SWARM ALERT**\n\n"
        alert += f"Cycles: {swarm_data.get('cycles', '?')} | Observations: {swarm_data.get('total_observations', '?')}\n\n"
        
        if q8_posts:
            alert += "🔥 **Q8 POSTS (Exceptional):**\n"
            for obs in q8_posts[:2]:  # Max 2
                author = obs.get("agent_name", "Unknown")
                title = obs.get("thread_title", "Untitled")[:50]
                alert += f"• {author}: {title}...\n"
            alert += "\n"
        
        if q7_posts:
            alert += "⭐ **Q7 POSTS (High Quality):**\n"
            for obs in q7_posts[:3]:  # Max 3
                author = obs.get("agent_name", "Unknown")
                title = obs.get("thread_title", "Untitled")[:40]
                markers = "L4" if obs.get("l4_markers") else "L3"
                alert += f"• {author} ({markers}): {title}...\n"
        
        alert += "\nRecommendations: engage|observe"
        
        msg.send_discord(alert, "info")
        log("    📧 Swarm alert sent to Discord")
        
    except Exception as e:
        log(f"    ⚠️ Could not send swarm alert: {e}")

# ============================================================================

def pick_next_task(master_plan_content, state):
    """Pick the next micro-task to execute"""
    current_hour = datetime.now().hour
    
    # Simple round-robin for now
    tasks = [
        "Fix Kitchen Sink syntax errors",
        "Complete R_V toolkit README",
        "Create AIKAGRYA report outline",
        "Process WARP_REGENT messages",
        "Deploy revenue assets",
    ]
    
    task_index = current_hour % len(tasks)
    return tasks[task_index]

def execute_micro_task(task):
    """Execute a 5-minute micro-task"""
    log(f"🎯 Executing: {task}")
    
    # For now, just log and plan
    # In full implementation, this would actually do work
    
    if "syntax" in task.lower():
        # Check for syntax errors
        result = subprocess.run(
            ["python3", "-m", "py_compile", "KITCHEN_SINK/iterations/ITER_02_core_bus.py"],
            cwd=CLAWD_DIR,
            capture_output=True,
            timeout=30
        )
        if result.returncode != 0:
            log(f"   Syntax error found: {result.stderr.decode()[:100]}")
            return "needs_fixing"
        else:
            log("   ✅ No syntax errors")
            return "complete"
    
    elif "README" in task:
        # Check if README exists and needs work
        readme = CLAWD_DIR / "autonomous_revenue" / "rv-toolkit" / "README.md"
        if readme.exists():
            content = readme.read_text()
            if len(content) < 1000:
                log(f"   README incomplete: {len(content)} bytes")
                return "needs_work"
            else:
                log("   ✅ README adequate")
                return "complete"
    
    elif "WARP" in task.upper():
        # Check Chaiwala messages
        result = subprocess.run(
            ["sqlite3", str(Path.home() / ".chaiwala" / "messages.db"),
             "SELECT COUNT(*) FROM messages WHERE to_agent='dharmic_claw' AND status='unread'"],
            capture_output=True,
            text=True,
            timeout=10
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        log(f"   WARP_REGENT messages: {count}")
        if count > 0:
            return f"{count}_messages_waiting"
        return "complete"
    
    return "unknown"

def send_hourly_update(task, result, state, swarm_data=None):
    """Send Discord/Email update to user"""
    hour = datetime.now().hour
    
    if hour % 6 == 0:  # Every 6 hours
        try:
            msg = MessagingChannel()
            message = f"📊 **Hour {hour} Update**\n\n"
            message += f"Task: {task}\n"
            message += f"Result: {result}\n"
            
            if swarm_data:
                message += f"\n🕸️ Swarm: {swarm_data.get('total_observations', 0)} obs, {len(swarm_data.get('high_quality', []))} Q7+\n"
            
            message += f"\nTasks completed today: {len(state.get('tasks_completed', []))}"
            
            msg.send_discord(message, "info")
            log("   📧 Update sent to Discord")
        except Exception as e:
            log(f"   ⚠️ Could not send Discord: {e}")

def main():
    log("=" * 60)
    log("🔥 HOURLY CYCLE - PROACTIVE EXECUTION")
    log("=" * 60)
    
    # Initialize JIKOKU
    jk = None
    if JIKOKU_AVAILABLE:
        jk = JikokuEmitter()
        jk.emit_boot(["MASTER_PLAN.md", "ORCHESTRATOR_TRAINING.md"])
        task_id = jk.emit_task_start("Hourly cycle execution", "meta", 10)
    
    # Load state
    state = load_state()
    current_hour = datetime.now().hour
    
    log(f"\n[1] Hour: {current_hour}")
    log(f"    Previous tasks: {len(state.get('tasks_completed', []))}")
    
    # Read master plan
    log("\n[2] Reading master plan...")
    plan_content = read_master_plan()
    if plan_content:
        log(f"    ✅ Master plan loaded: {len(plan_content)} bytes")
    else:
        log("    ❌ Master plan not found")
        return
    
    # ============================================================================
    # MOLTBOOK SWARM POLLING (NEW)
    # ============================================================================
    log("\n[3] Polling Moltbook swarm...")
    swarm_data = poll_moltbook_swarm()
    
    if swarm_data:
        # Send alert for high-quality posts
        send_swarm_alert(swarm_data)
        
        # Update state
        state["last_swarm_check"] = datetime.now().isoformat()
        state["last_swarm_cycles"] = swarm_data.get("cycles", 0)
        save_state(state)
    else:
        log("    ⚠️ Could not poll swarm")
    # ============================================================================
    
    # Pick next task
    log("\n[4] Selecting micro-task...")
    task = pick_next_task(plan_content, state)
    log(f"    🎯 Selected: {task}")
    
    # Execute
    log("\n[5] Executing micro-task...")
    result = execute_micro_task(task)
    log(f"    📊 Result: {result}")
    
    # Update master plan
    log("\n[6] Updating master plan...")
    update_master_plan_progress(task, result)
    log("    ✅ Progress logged")
    
    # Update state
    state["last_hour"] = current_hour
    state["current_project"] = task
    if result in ["complete", "needs_work", "needs_fixing"]:
        state["tasks_completed"].append({
            "hour": current_hour,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    save_state(state)
    
    # Send update (every 6 hours)
    log("\n[7] Sending status update...")
    send_hourly_update(task, result, state, swarm_data)
    
    # JIKOKU session summary
    if jk:
        obs_count = swarm_data.get('total_observations', 0) if swarm_data else 0
        jk.emit_task_end(task_id, f"Hourly cycle + swarm poll: {obs_count} observations", [], [])
        jk.emit_session_summary(
            categories={"meta": 10},
            muda_detected=[],
            kaizen_opportunities=["integrate swarm deeper"]
        )
    
    log("\n" + "=" * 60)
    log("✅ HOURLY CYCLE COMPLETE")
    log("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"\n❌ HOURLY CYCLE FAILED: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)
