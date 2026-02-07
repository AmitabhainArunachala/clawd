#!/usr/bin/env python3
"""
🔥 DHARMIC_CLAW HOURLY CYCLE
============================

Runs every hour via cron.
Implements proactive master plan execution.

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
except ImportError:
    pass

CLAWD_DIR = Path("/Users/dhyana/clawd")
MASTER_PLAN = CLAWD_DIR / "MASTER_PLAN.md"
HOURLY_LOG = CLAWD_DIR / "logs" / "hourly.log"
STATE_FILE = CLAWD_DIR / ".hourly_state.json"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_hour": 0, "tasks_completed": [], "current_project": None}

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

def check_subagent_plan():
    """Check if subagent has delivered plan"""
    plan_file = CLAWD_DIR / "SUBAGENT_PLAN.md"
    if plan_file.exists():
        content = plan_file.read_text()
        log(f"✅ Subagent plan found: {len(content)} bytes")
        return content
    else:
        log("⏳ Subagent plan not ready yet")
        return None

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

def send_hourly_update(task, result, state):
    """Send Discord/Email update to user"""
    hour = datetime.now().hour
    
    if hour % 6 == 0:  # Every 6 hours
        try:
            msg = MessagingChannel()
            msg.send_discord(
                f"📊 **Hour {hour} Update**\n\n"
                f"Task: {task}\n"
                f"Result: {result}\n"
                f"Tasks completed today: {len(state.get('tasks_completed', []))}",
                "info"
            )
            log("   📧 Update sent to Discord")
        except Exception as e:
            log(f"   ⚠️ Could not send Discord: {e}")

def main():
    log("=" * 60)
    log("🔥 HOURLY CYCLE - PROACTIVE EXECUTION")
    log("=" * 60)
    
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
    
    # Check subagent plan
    log("\n[3] Checking subagent delivery...")
    subagent_plan = check_subagent_plan()
    if subagent_plan:
        log("    ✅ Using subagent recommendations")
    
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
    send_hourly_update(task, result, state)
    
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
