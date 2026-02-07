#!/usr/bin/env python3
"""
🔥 DHARMIC_CLAW AUTONOMOUS HEARTBEAT
====================================

Runs every 15 minutes via cron.
Proactive agent that works without user input.

Cron entry:
*/15 * * * * /Users/dhyana/clawd/dharmic_claw_heartbeat.py >> /Users/dhyana/clawd/logs/heartbeat.log 2>&1
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add dharmic_claw to path
sys.path.insert(0, str(Path("/Users/dhyana/clawd")))

# Import messaging
try:
    from dharmic_claw_messaging import MessagingChannel, send_warp_regent_alert, send_git_commit_alert
    MESSAGING_AVAILABLE = True
except ImportError:
    MESSAGING_AVAILABLE = False
    print("[WARN] Messaging module not available")

# Import JIKOKU
try:
    from jikoku_emitter import JikokuEmitter
    JIKOKU_AVAILABLE = True
except ImportError:
    JIKOKU_AVAILABLE = False
    print("[WARN] JIKOKU emitter not available")

# Paths
CLAWD_DIR = Path("/Users/dhyana/clawd")
LOG_DIR = CLAWD_DIR / "logs"
STATE_FILE = CLAWD_DIR / ".dharmic_claw_state.json"
AUDIT_FILE = CLAWD_DIR / "YOLO_META_AUDIT.md"
CHAIWALA_DB = Path.home() / ".chaiwala" / "messages.db"

# Ensure dirs
LOG_DIR.mkdir(exist_ok=True)

def log(msg):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    
def audit_log(action, status, details=""):
    """Log to audit file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n### [{timestamp}] {action}\n**Status:** {status}\n"
    if details:
        entry += f"**Details:** {details}\n"
    
    with open(AUDIT_FILE, "a") as f:
        f.write(entry)

def load_state():
    """Load persistent state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_check": None,
        "current_task": None,
        "tasks_completed": 0,
        "uncommitted_work": [],
        "messages_sent": 0
    }

def save_state(state):
    """Save persistent state"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_git_status():
    """Check for uncommitted work"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=CLAWD_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = [l for l in result.stdout.strip().split("\n") if l]
        return lines
    except Exception as e:
        return [f"Error: {e}"]

def check_chaiwala_messages():
    """Check for messages from WARP_REGENT"""
    try:
        # Use sqlite3 to check messages
        result = subprocess.run(
            ["sqlite3", str(CHAIWALA_DB), 
             "SELECT COUNT(*) FROM messages WHERE to_agent='dharmic_claw' AND status='unread'"],
            capture_output=True,
            text=True,
            timeout=5
        )
        count = int(result.stdout.strip()) if result.stdout.strip() else 0
        return count
    except Exception as e:
        return 0

def check_top_10_projects():
    """Check TOP 10 projects for progress"""
    top_10_file = CLAWD_DIR / "TOP_10_PROJECTS.md"
    if not top_10_file.exists():
        return "No TOP_10 file"
    
    # Read and check for blockers
    content = top_10_file.read_text()
    lines = content.split("\n")
    
    # Find blocked items
    blocked = [l for l in lines if "blocked" in l.lower() or "stuck" in l.lower()]
    return f"{len(blocked)} blocked items" if blocked else "All clear"

def attempt_git_commit():
    """Try to commit any uncommitted work"""
    try:
        # Add all
        subprocess.run(
            ["git", "add", "."],
            cwd=CLAWD_DIR,
            timeout=10,
            capture_output=True
        )
        
        # Commit with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = subprocess.run(
            ["git", "commit", "-m", f"[autonomous] Heartbeat commit {timestamp}"],
            cwd=CLAWD_DIR,
            timeout=10,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return "Committed successfully"
        else:
            return "Nothing to commit"
    except Exception as e:
        return f"Error: {e}"

def self_improvement_check():
    """Check for self-improvement opportunities"""
    # Look for patterns in recent work
    recent_files = list(CLAWD_DIR.glob("*.py")) + list((CLAWD_DIR / "skills").rglob("*.py"))
    
    # Simple heuristics
    issues = []
    
    for f in recent_files[:10]:  # Check 10 most recent
        try:
            content = f.read_text()
            
            # Check for syntax errors
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(f)],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                issues.append(f"Syntax error in {f.name}")
                
        except Exception:
            pass
    
    return issues[:3] if issues else ["No immediate issues found"]

def check_jikoku_temporal_blindness():
    """Check for TEMPORAL_BLINDNESS (no JIKOKU spans > 24h)"""
    jikoku_log = Path("/Users/dhyana/.openclaw/workspace/JIKOKU_LOG.jsonl")
    
    if not jikoku_log.exists():
        return "TEMPORAL_BLINDNESS: No JIKOKU_LOG found"
    
    try:
        # Read last line
        lines = jikoku_log.read_text().strip().split('\n')
        if not lines:
            return "TEMPORAL_BLINDNESS: Empty JIKOKU_LOG"
        
        last_entry = json.loads(lines[-1])
        last_timestamp = last_entry.get('timestamp', '')
        
        if last_timestamp:
            # Parse timestamp
            from datetime import timezone
            last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            hours_since = (now - last_time).total_seconds() / 3600
            
            if hours_since > 24:
                return f"🚨 TEMPORAL_BLINDNESS: No JIKOKU spans for {hours_since:.1f} hours"
            else:
                return f"✅ JIKOKU healthy: Last span {hours_since:.1f} hours ago"
        else:
            return "TEMPORAL_BLINDNESS: No timestamp in last entry"
            
    except Exception as e:
        return f"TEMPORAL_BLINDNESS: Error reading log: {e}"

def main():
    """Main heartbeat function"""
    log("=" * 60)
    log("🔥 DHARMIC_CLAW AUTONOMOUS HEARTBEAT")
    log("=" * 60)
    
    # Load state
    state = load_state()
    state["last_check"] = datetime.now().isoformat()
    
    # 1. Check git status
    log("\n[1] Checking git status...")
    git_status = check_git_status()
    if git_status:
        log(f"   Found {len(git_status)} uncommitted files")
        audit_log("Git Status Check", "ATTENTION", f"{len(git_status)} files uncommitted")
        
        # Try to commit
        commit_result = attempt_git_commit()
        log(f"   Commit attempt: {commit_result}")
        audit_log("Auto-Commit", "ATTEMPTED", commit_result)
    else:
        log("   All clear")
    
    # 2. Check Chaiwala messages
    log("\n[2] Checking Chaiwala messages...")
    msg_count = check_chaiwala_messages()
    if msg_count > 0:
        log(f"   🚨 {msg_count} unread messages from WARP_REGENT!")
        audit_log("Chaiwala Check", "ACTION NEEDED", f"{msg_count} unread messages")
    else:
        log("   No new messages")
    
    # 3. Check TOP 10 projects
    log("\n[3] Checking TOP 10 projects...")
    top10_status = check_top_10_projects()
    log(f"   Status: {top10_status}")
    audit_log("TOP 10 Check", "SCANNED", top10_status)
    
    # 4. Self-improvement check
    log("\n[4] Self-improvement check...")
    issues = self_improvement_check()
    for issue in issues:
        log(f"   - {issue}")
    audit_log("Self-Improvement Scan", "COMPLETED", "; ".join(issues))
    
    # 5. JIKOKU temporal audit (CONSTITUTION Section VI)
    log("\n[5] JIKOKU temporal audit...")
    jikoku_status = check_jikoku_temporal_blindness()
    log(f"   {jikoku_status}")
    audit_log("JIKOKU Audit", "CHECKED", jikoku_status)
    
    # 6. Update state
    state["tasks_completed"] += 1
    save_state(state)
    
    log("\n" + "=" * 60)
    log(f"✅ Heartbeat complete. Total runs: {state['tasks_completed']}")
    log("=" * 60)
    
    # 7. Proactive message if needed
    if msg_count > 0 or len(git_status) > 5:
        log("\n🚨 PROACTIVE: Issues detected, user should be notified")
        audit_log("Proactive Alert", "TRIGGERED", "Issues need user attention")
        
        # Send actual alerts!
        if MESSAGING_AVAILABLE:
            msg = MessagingChannel()
            
            # Alert about WARP_REGENT messages (disabled per user request)
            if msg_count > 0 and os.getenv('NOTIFY_WARP_REGENT', 'false').lower() == 'true':
                log("   📧 Sending WARP_REGENT alert...")
                send_warp_regent_alert(msg_count)
            elif msg_count > 0:
                log(f"   🤐 WARP_REGENT has {msg_count} messages (alerts disabled)")
            
            # Alert about git commits
            if len(git_status) > 0 and state.get("last_commit_alert") != datetime.now().strftime("%Y%m%d"):
                log("   📧 Sending git commit alert...")
                send_git_commit_alert([g.split()[-1] for g in git_status[:5]])
                state["last_commit_alert"] = datetime.now().strftime("%Y%m%d")
        else:
            log("   ⚠️  Messaging not configured, alerts logged only")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"\n❌ Heartbeat failed: {e}")
        audit_log("Heartbeat", "ERROR", str(e))
        sys.exit(1)
