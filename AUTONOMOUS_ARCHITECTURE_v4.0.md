# OpenClaw Autonomous Operation Architecture v4.0
## DHARMIC CLAW — Maximal Efficacy Design

**Date:** 2026-02-17  
**Architect:** Infrastructure Subagent  
**Classification:** Production Architecture Document  

---

## EXECUTIVE SUMMARY

This document presents a comprehensive architecture for maximizing DHARMIC CLAW's autonomous operation efficacy. The design treats statelessness as a feature, not a bug—enabling resilient, fault-tolerant operation that degrades gracefully while maintaining continuous forward momentum.

### Key Design Principles

1. **Multi-Modal Triggers**: Never rely on single triggering mechanism
2. **State Externalization**: All state lives on disk; agent sessions are ephemeral workers
3. **Continuity Through Continuation**: Work persists via structured state files, not session persistence
4. **Graceful Degradation**: System continues operating even if components fail
5. **Observable Everything**: If it can't be monitored, it doesn't exist

---

## 1. CURRENT STATE ANALYSIS

### Existing Infrastructure (Working)

| Component | Status | Notes |
|-----------|--------|-------|
| `dharmic_claw_heartbeat.py` | ✅ Active | Runs every 15min via cron |
| `hourly_cycle.py` | ✅ Active | Hourly proactive execution |
| `crontab_dharmic_claw.txt` | ⚠️ Partial | Config exists, needs validation |
| State persistence | ✅ Working | `.dharmic_claw_state.json` |
| JIKOKU logging | ✅ Active | Temporal tracking functional |
| Git auto-commit | ✅ Working | Self-healing version control |

### Critical Constraints (Non-Negotiable)

1. **Stateless Sessions**: Agent context resets between messages
2. **External Trigger Required**: Cannot self-awaken; needs cron/webhook/manual trigger
3. **No Subagent Persistence**: Spawned subagents die with parent session
4. **Resource Bound**: Runs on MacBook Pro with finite compute

### Current Failure Modes

```
1. Cron job silent failure → No alerting
2. Agent session timeout → Work lost mid-task
3. Git corruption → No recovery mechanism
4. State file corruption → Cold start required
5. No health dashboard → Blind to system status
```

---

## 2. TRIGGERING ARCHITECTURE

### 2.1 Three-Tier Trigger System

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIGGER PYRAMID                          │
├─────────────────────────────────────────────────────────────┤
│  TIER 1: Temporal (Reliable Baseline)                       │
│  ├── Cron (every 15min) → Heartbeat                         │
│  ├── LaunchAgent (user session) → GUI triggers              │
│  └── Watchdog (every 5min) → Health checks                  │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: Event-Based (Responsive)                           │
│  ├── File system watchers (fswatch) → On change             │
│  ├── Webhook server (localhost) → External events           │
│  ├── MQTT subscriber (optional) → IoT triggers              │
│  └── Git hook post-commit → Auto-advance                    │
├─────────────────────────────────────────────────────────────┤
│  TIER 3: Manual (Human Override)                            │
│  ├── CLI command (`openclaw trigger <task>`)                │
│  ├── Telegram bot command                                   │
│  ├── Web dashboard button                                   │
│  └── Voice trigger (Siri Shortcuts)                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Recommended: Hybrid LaunchAgent + Cron Approach

**Why LaunchAgent over pure cron:**
- ✅ Runs only when user logged in (respects human presence)
- ✅ Can trigger on file changes (WatchPaths)
- ✅ Better error logging (StandardErrorPath)
- ✅ Native macOS integration
- ✅ Can run GUI scripts (if needed)

**Why keep cron as backup:**
- ✅ Works even if LaunchAgent fails
- ✅ Simple, universal, battle-tested
- ✅ Can be monitored via system logs

### 2.3 LaunchAgent Configuration

```xml
<!-- com.dharmic-claw.heartbeat.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dharmic-claw.heartbeat</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/dhyana/clawd/orchestrator/trigger.py</string>
        <string>--mode</string>
        <string>heartbeat</string>
    </array>
    
    <!-- Run every 15 minutes -->
    <key>StartInterval</key>
    <integer>900</integer>
    
    <!-- Also trigger on file changes -->
    <key>WatchPaths</key>
    <array>
        <string>/Users/dhyana/clawd/memory/</string>
        <string>/Users/dhyana/clawd/.trigger</string>
    </array>
    
    <!-- Logging -->
    <key>StandardOutPath</key>
    <string>/Users/dhyana/clawd/logs/launchagent.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/dhyana/clawd/logs/launchagent.err.log</string>
    
    <!-- Environment -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>CLAWD_DIR</key>
        <string>/Users/dhyana/clawd</string>
        <key>PYTHONPATH</key>
        <string>/Users/dhyana/clawd</string>
    </dict>
    
    <!-- Keep alive if crashes -->
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <!-- Throttle restarts -->
    <key>ThrottleInterval</key>
    <integer>60</integer>
</dict>
</plist>
```

### 2.4 Event-Based Triggers (File Watcher)

```python
# orchestrator/fswatch_bridge.py
"""
Uses macOS fswatch to trigger agent on file changes.
More responsive than polling; complements cron schedule.
"""

import subprocess
import sys
from pathlib import Path

WATCHED_PATHS = [
    "/Users/dhyana/clawd/memory/*.md",
    "/Users/dhyana/clawd/.trigger",
    "/Users/dhyana/clawd/TOP_10_PROJECTS.md",
]

def main():
    """Run fswatch and trigger agent on changes"""
    cmd = ["fswatch", "-o"] + WATCHED_PATHS
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    for line in process.stdout:
        # File changed - trigger agent
        trigger_agent("file_change", line.strip())

def trigger_agent(event_type, context):
    """Trigger agent session with context"""
    subprocess.run([
        sys.executable,
        "/Users/dhyana/clawd/orchestrator/trigger.py",
        "--mode", "event",
        "--event-type", event_type,
        "--context", context
    ])

if __name__ == "__main__":
    main()
```

---

## 3. STATE MANAGEMENT ARCHITECTURE

### 3.1 State Hierarchy

```
/Users/dhyana/clawd/
├── state/
│   ├── current_session.json       # Ephemeral: current work unit
│   ├── work_queue.json            # Persistent: pending tasks
│   ├── continuity_log.jsonl       # Persistent: all session transitions
│   ├── project_state/             # Per-project checkpoints
│   │   ├── rv_paper.json
│   │   ├── dgc_tests.json
│   │   └── witness_mvp.json
│   └── recovery/                  # Auto-generated recovery points
│       ├── latest.json
│       └── daily/
├── memory/                        # Already exists: daily notes
├── logs/                          # Already exists: operation logs
└── .trigger                       # Touch to force trigger
```

### 3.2 Session State Schema

```json
{
  "session_id": "uuid-v4",
  "started_at": "2026-02-17T07:00:00Z",
  "triggered_by": "cron|event|manual",
  "agent_mode": "heartbeat|deep_work|reactive",
  
  "current_work": {
    "project": "rv_paper",
    "task": "write_methods_section",
    "started_at": "2026-02-17T07:05:00Z",
    "estimated_duration_min": 30,
    "checkpoint": {
      "file": "/Users/dhyana/clawd/state/current_session.json",
      "last_saved": "2026-02-17T07:10:00Z"
    }
  },
  
  "completed_this_session": [
    {"task": "check_git_status", "completed_at": "2026-02-17T07:02:00Z"}
  ],
  
  "blockers": [],
  
  "next_session": {
    "recommended_task": "continue_methods_section",
    "priority": "high",
    "context": "Completed literature review para; next: methodology"
  }
}
```

### 3.3 Work Queue System

```python
# orchestrator/work_queue.py
"""
Priority queue for autonomous work.
Persists across sessions; agent pulls from here.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json
from pathlib import Path

@dataclass
class WorkItem:
    id: str
    project: str
    task: str
    priority: int  # 1-10, lower = higher priority
    estimated_minutes: int
    created_at: str
    depends_on: Optional[str] = None
    context: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

class WorkQueue:
    QUEUE_FILE = Path("/Users/dhyana/clawd/state/work_queue.json")
    
    def __init__(self):
        self.items = []
        self.load()
    
    def load(self):
        if self.QUEUE_FILE.exists():
            data = json.loads(self.QUEUE_FILE.read_text())
            self.items = [WorkItem.from_dict(i) for i in data]
    
    def save(self):
        self.QUEUE_FILE.write_text(
            json.dumps([i.to_dict() for i in self.items], indent=2)
        )
    
    def add(self, item: WorkItem):
        self.items.append(item)
        self.items.sort(key=lambda x: (x.priority, x.created_at))
        self.save()
    
    def pop_next(self) -> Optional[WorkItem]:
        """Get highest priority item, checking dependencies"""
        for item in self.items:
            if item.depends_on is None or self.is_complete(item.depends_on):
                self.items.remove(item)
                self.save()
                return item
        return None
    
    def is_complete(self, task_id: str) -> bool:
        # Check completion log
        log_file = Path("/Users/dhyana/clawd/state/completion_log.jsonl")
        if not log_file.exists():
            return False
        
        for line in log_file.read_text().strip().split("\n"):
            if line:
                entry = json.loads(line)
                if entry.get("task_id") == task_id:
                    return True
        return False
    
    def complete(self, item: WorkItem, result: str):
        """Mark item complete and log it"""
        log_file = Path("/Users/dhyana/clawd/state/completion_log.jsonl")
        entry = {
            "task_id": item.id,
            "completed_at": datetime.utcnow().isoformat(),
            "result": result
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
```

---

## 4. CONTINUITY MECHANISM

### 4.1 The Continuation Pattern

Since sessions are stateless, we use **continuation-passing style**:

```python
# How agent maintains continuity across sessions

def run_autonomous_session(trigger_mode: str):
    """
    Each session:
    1. Load state from disk (not memory)
    2. Execute one work unit
    3. Save continuation state
    4. Exit cleanly
    """
    
    # 1. Load where we left off
    state = load_session_state()
    queue = WorkQueue()
    
    # 2. Decide what to do
    if state.current_work and not state.current_work.get("completed"):
        # Continue previous work
        task = state.current_work
    else:
        # Pull new work from queue
        task = queue.pop_next()
    
    if not task:
        logger.info("HEARTBEAT_OK: No work to do")
        return
    
    # 3. Execute with checkpointing
    try:
        result = execute_with_checkpoints(task)
        queue.complete(task, result)
        
        # 4. Prepare next session
        next_task = queue.peek_next()
        save_continuation_state(next_task)
        
    except SessionTimeoutWarning:
        # Save exact position for continuation
        save_emergency_checkpoint(task)
        raise
```

### 4.2 Checkpoint Every 2 Minutes

```python
# orchestrator/checkpoint.py
"""
Automatic checkpointing during long operations.
Ensures minimal work loss on session interruption.
"""

import signal
import sys
from contextlib import contextmanager
from datetime import datetime

class CheckpointManager:
    CHECKPOINT_INTERVAL = 120  # seconds
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.last_checkpoint = datetime.utcnow()
        self.state = {}
        
        # Handle graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Save checkpoint on shutdown signal"""
        self._save_emergency_checkpoint()
        sys.exit(0)
    
    def checkpoint(self, data: dict):
        """Save progress checkpoint"""
        elapsed = (datetime.utcnow() - self.last_checkpoint).total_seconds()
        
        if elapsed >= self.CHECKPOINT_INTERVAL:
            self._write_checkpoint(data)
            self.last_checkpoint = datetime.utcnow()
    
    def _write_checkpoint(self, data: dict):
        checkpoint = {
            "task_id": self.task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        # Write atomic (temp + rename)
        temp = f"/Users/dhyana/clawd/state/checkpoints/{self.task_id}.tmp"
        final = f"/Users/dhyana/clawd/state/checkpoints/{self.task_id}.json"
        
        with open(temp, "w") as f:
            json.dump(checkpoint, f)
        
        os.rename(temp, final)
    
    def _save_emergency_checkpoint(self):
        """Called on signal - minimal safe write"""
        self._write_checkpoint({
            "emergency": True,
            "signal_caught": True,
            "partial_state": self.state
        })

# Usage in agent code:
@contextmanager
def resumable_task(task_id: str):
    checkpoint = CheckpointManager(task_id)
    try:
        yield checkpoint
    finally:
        checkpoint._save_emergency_checkpoint()

# In agent:
with resumable_task("write_methods_section") as cp:
    for paragraph in sections:
        write_paragraph(paragraph)
        cp.checkpoint({"completed_paras": completed})
```

---

## 5. GRACEFUL DEGRADATION

### 5.1 Failure Mode Matrix

| Component Failure | Impact | Fallback Behavior |
|-------------------|--------|-------------------|
| Cron job fails | No triggers | LaunchAgent continues; manual trigger via file touch |
| LaunchAgent crashes | No file watching | Cron provides baseline; auto-restart via KeepAlive |
| State file corrupt | Cold start | Recovery from `recovery/latest.json` backup |
| Git unavailable | No version control | Continue with local state; alert user |
| Network down | No external APIs | Queue tasks locally; retry with exponential backoff |
| LLM unavailable | Cannot reason | Log error; retry in 15min; escalate if persistent |
| Disk full | Cannot write | Alert immediately; pause non-critical operations |

### 5.2 Degradation Chain

```
NORMAL OPERATION:
  Full agent → Full tools → Git backup → External APIs
       ↓
DEGRADED (Component Failure):
  Full agent → Reduced tools → Local state only → Retry later
       ↓
MINIMAL (Multiple Failures):
  Monitoring only → Log to file → Alert human
       ↓
RECOVERY (Human intervention):
  Diagnostic mode → Manual trigger → Full restore
```

### 5.3 Circuit Breaker Pattern

```python
# orchestrator/circuit_breaker.py
"""
Prevents cascade failures by temporarily disabling failing components.
"""

import time
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocked
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 300  # 5 minutes
    
    def __post_init__(self):
        self.state_file = Path(f"/Users/dhyana/clawd/state/circuits/{self.name}.json")
        self._load_state()
    
    def _load_state(self):
        if self.state_file.exists():
            data = json.loads(self.state_file.read_text())
            self.state = CircuitState(data["state"])
            self.failures = data["failures"]
            self.last_failure = data["last_failure"]
        else:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.last_failure = 0
    
    def _save_state(self):
        self.state_file.write_text(json.dumps({
            "state": self.state.value,
            "failures": self.failures,
            "last_failure": self.last_failure
        }))
    
    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self._save_state()
                return True
            return False
        
        return True  # HALF_OPEN - allow test
    
    def record_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED
        self._save_state()
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
        
        self._save_state()

# Usage:
discord_circuit = CircuitBreaker("discord_api", failure_threshold=3)

if discord_circuit.can_execute():
    try:
        send_discord_message(msg)
        discord_circuit.record_success()
    except Exception:
        discord_circuit.record_failure()
        # Fallback to log file
        log_to_file(msg)
```

---

## 6. MONITORING & ALERTING

### 6.1 Health Dashboard (File-Based)

```json
// /Users/dhyana/clawd/state/health.json
{
  "generated_at": "2026-02-17T07:00:00Z",
  "overall_status": "healthy|degraded|critical",
  
  "components": {
    "cron": {
      "status": "ok",
      "last_execution": "2026-02-17T06:45:00Z",
      "success_rate_24h": 0.98
    },
    "launchagent": {
      "status": "ok", 
      "pid": 12345,
      "uptime_hours": 48
    },
    "git": {
      "status": "ok",
      "last_commit": "2026-02-17T06:30:00Z",
      "uncommitted_files": 2
    },
    "work_queue": {
      "pending_tasks": 5,
      "blocked_tasks": 1,
      "avg_completion_time_min": 23
    }
  },
  
  "alerts": [
    {
      "level": "warning",
      "component": "discord_api",
      "message": "3 failures in last hour",
      "since": "2026-02-17T06:00:00Z"
    }
  ]
}
```

### 6.2 Alerting Levels

```python
# orchestrator/alerting.py

ALERT_CONFIG = {
    "critical": {
        "channels": ["telegram", "discord", "email", "dashboard"],
        "immediate": True,
        "examples": [
            "Disk space < 5%",
            "All triggers failed for > 1 hour",
            "Git corruption detected",
            "State file unreadable"
        ]
    },
    "warning": {
        "channels": ["discord", "dashboard"],
        "immediate": False,
        "examples": [
            "Queue backlog > 10 items",
            "API failure rate > 20%",
            "No commits for 6 hours"
        ]
    },
    "info": {
        "channels": ["dashboard"],
        "immediate": False,
        "examples": [
            "Daily summary",
            "Task completed",
            "New work item added"
        ]
    }
}
```

### 6.3 Self-Monitoring Script

```python
# orchestrator/health_check.py
"""
Runs every 5 minutes; updates health dashboard.
Part of the watchdog system.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def check_cron_health():
    """Check if cron jobs are running"""
    log_file = Path("/Users/dhyana/clawd/logs/heartbeat.log")
    
    if not log_file.exists():
        return {"status": "unknown", "error": "No log file"}
    
    # Check last entry timestamp
    lines = log_file.read_text().strip().split("\n")
    if not lines:
        return {"status": "unknown", "error": "Empty log"}
    
    # Parse last timestamp (format: [2026-02-17 07:00:00] message)
    last_line = lines[-1]
    # Extract timestamp...
    
    last_run = parse_timestamp(last_line)
    minutes_since = (datetime.utcnow() - last_run).total_seconds() / 60
    
    if minutes_since > 20:  # Should run every 15 min
        return {
            "status": "failing",
            "minutes_since_last_run": minutes_since,
            "last_run": last_run.isoformat()
        }
    
    return {
        "status": "ok",
        "minutes_since_last_run": minutes_since
    }

def check_git_health():
    """Check git status"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd="/Users/dhyana/clawd",
        capture_output=True,
        text=True
    )
    
    uncommitted = len([l for l in result.stdout.split("\n") if l.strip()])
    
    # Get last commit time
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct"],
        capture_output=True,
        text=True
    )
    last_commit_ts = int(result.stdout.strip())
    last_commit = datetime.fromtimestamp(last_commit_ts)
    hours_since_commit = (datetime.utcnow() - last_commit).total_seconds() / 3600
    
    return {
        "status": "ok" if uncommitted < 10 else "warning",
        "uncommitted_files": uncommitted,
        "hours_since_commit": hours_since_commit
    }

def generate_health_report():
    """Generate comprehensive health report"""
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "components": {
            "cron": check_cron_health(),
            "git": check_git_health(),
            # Add more checks...
        }
    }
    
    # Determine overall status
    statuses = [c["status"] for c in report["components"].values()]
    if "failing" in statuses:
        report["overall_status"] = "critical"
    elif "warning" in statuses:
        report["overall_status"] = "degraded"
    else:
        report["overall_status"] = "healthy"
    
    # Save to file
    Path("/Users/dhyana/clawd/state/health.json").write_text(
        json.dumps(report, indent=2)
    )
    
    return report
```

---

## 7. IMPLEMENTATION PLAN

### Phase 1: Foundation (Week 1)

**Day 1-2: Infrastructure Setup**
```bash
# Create directory structure
mkdir -p /Users/dhyana/clawd/{orchestrator,state/{checkpoints,circuits,recovery},logs}

# Install LaunchAgent
cp orchestrator/com.dharmic-claw.heartbeat.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.dharmic-claw.heartbeat.plist

# Validate cron
crontab -l | grep dharmic_claw
```

**Day 3-4: State System**
- Implement work_queue.py
- Implement checkpoint.py
- Create state schemas
- Add state validation

**Day 5-7: Integration**
- Refactor heartbeat.py to use new queue
- Add checkpointing to existing tasks
- Test continuity across sessions

### Phase 2: Resilience (Week 2)

**Day 8-10: Monitoring**
- Implement health_check.py
- Create health dashboard
- Set up alerting thresholds
- Add circuit breakers

**Day 11-12: Event System**
- Implement fswatch_bridge.py
- Add webhook listener
- Create .trigger file mechanism

**Day 13-14: Testing**
- Simulate component failures
- Test degradation paths
- Validate recovery procedures

### Phase 3: Optimization (Week 3)

**Day 15-17: Intelligence**
- Smart task prioritization
- Dynamic schedule adjustment
- Work time estimation

**Day 18-21: Documentation**
- Runbooks for common failures
- Architecture diagrams
- Monitoring dashboards

---

## 8. CONFIGURATION FILES

### 8.1 Complete Crontab

```bash
# DHARMIC CLAW Autonomous Operation Schedule
# Add via: crontab -e

# Environment
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
CLAWD_DIR=/Users/dhyana/clawd
PYTHONPATH=/Users/dhyana/clawd

# Primary heartbeat (every 15 minutes)
*/15 * * * * cd $CLAWD_DIR && python3 orchestrator/trigger.py --mode heartbeat >> logs/cron_heartbeat.log 2>&1

# Work queue processing (every 30 minutes, during work hours)
*/30 4-23 * * * cd $CLAWD_DIR && python3 orchestrator/trigger.py --mode work >> logs/cron_work.log 2>&1

# Health check (every 5 minutes)
*/5 * * * * cd $CLAWD_DIR && python3 orchestrator/health_check.py >> logs/health.log 2>&1

# Daily deep work (03:00 - night cycle)
0 3 * * * cd $CLAWD_DIR && python3 orchestrator/trigger.py --mode deep_work >> logs/night_cycle.log 2>&1

# Daily summary (06:00)
0 6 * * * cd $CLAWD_DIR && python3 orchestrator/trigger.py --mode summary >> logs/daily_summary.log 2>&1

# Git maintenance (daily at 02:00)
0 2 * * * cd $CLAWD_DIR && git gc >> logs/git_gc.log 2>&1

# State backup (every 6 hours)
0 */6 * * * cd $CLAWD_DIR && cp -r state/ backups/state_$(date +\%Y\%m\%d_\%H\%M)/
```

### 8.2 LaunchAgent Full Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dharmic-claw.heartbeat</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/dhyana/clawd/orchestrator/trigger.py</string>
        <string>--mode</string>
        <string>heartbeat</string>
    </array>
    
    <!-- Run every 15 minutes -->
    <key>StartInterval</key>
    <integer>900</integer>
    
    <!-- File watching triggers -->
    <key>WatchPaths</key>
    <array>
        <string>/Users/dhyana/clawd/.trigger</string>
        <string>/Users/dhyana/clawd/TOP_10_PROJECTS.md</string>
        <string>/Users/dhyana/clawd/INTERVENTION.md</string>
    </array>
    
    <!-- Queue directory watching -->
    <key>QueueDirectories</key>
    <array>
        <string>/Users/dhyana/clawd/state/inbox/</string>
    </array>
    
    <!-- Run on network connectivity changes -->
    <key>WatchPaths</key>
    <array>
        <string>/private/var/run/resolv.conf</string>
    </array>
    
    <!-- Standard I/O -->
    <key>StandardOutPath</key>
    <string>/Users/dhyana/clawd/logs/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/dhyana/clawd/logs/launchd.err.log</string>
    
    <!-- Environment -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>CLAWD_DIR</key>
        <string>/Users/dhyana/clawd</string>
        <key>PYTHONPATH</key>
        <string>/Users/dhyana/clawd</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    
    <!-- Restart behavior -->
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>
    
    <key>ThrottleInterval</key>
    <integer>60</integer>
    
    <!-- Resource limits -->
    <key>HardResourceLimits</key>
    <dict>
        <key>CPU</key>
        <integer>300</integer>
    </dict>
    
    <!-- Only run when user is logged in -->
    <key>LimitLoadToSessionType</key>
    <string>Aqua</string>
</dict>
</plist>
```

### 8.3 Main Trigger Script

```python
#!/usr/bin/env python3
"""
orchestrator/trigger.py
=======================

Main entry point for all agent triggers.
Routes to appropriate handler based on mode.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add clawd to path
sys.path.insert(0, "/Users/dhyana/clawd")

from orchestrator.work_queue import WorkQueue
from orchestrator.checkpoint import CheckpointManager

def setup_logging(mode: str):
    """Configure logging for this session"""
    log_dir = Path("/Users/dhyana/clawd/logs/sessions")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{mode}_{timestamp}.log"
    
    # Configure root logger
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("orchestrator")

def load_session_state():
    """Load continuation state from previous session"""
    state_file = Path("/Users/dhyana/clawd/state/current_session.json")
    if state_file.exists():
        return json.loads(state_file.read_text())
    return None

def save_session_state(state: dict):
    """Save state for next session"""
    state_file = Path("/Users/dhyana/clawd/state/current_session.json")
    state["saved_at"] = datetime.utcnow().isoformat()
    state_file.write_text(json.dumps(state, indent=2))

def route_heartbeat(logger):
    """Handle heartbeat trigger"""
    logger.info("Processing heartbeat trigger")
    
    # Load previous state
    prev_state = load_session_state()
    
    # Check for work
    queue = WorkQueue()
    next_task = queue.peek_next()
    
    if not next_task:
        logger.info("HEARTBEAT_OK: No pending work")
        return
    
    # If we have work, this should have triggered work mode
    # But handle just in case
    logger.info(f"Found work: {next_task.task}")
    return route_work(logger)

def route_work(logger):
    """Handle work execution trigger"""
    logger.info("Processing work trigger")
    
    queue = WorkQueue()
    task = queue.pop_next()
    
    if not task:
        logger.info("No work available")
        return
    
    # Initialize checkpoint manager
    checkpoint = CheckpointManager(task.id)
    
    try:
        # Route to appropriate skill/handler
        result = execute_task(task, checkpoint, logger)
        
        # Mark complete
        queue.complete(task, result)
        
        # Prepare next
        next_task = queue.peek_next()
        if next_task:
            save_session_state({
                "next_task": next_task.to_dict(),
                "ready_at": datetime.utcnow().isoformat()
            })
        
        logger.info(f"Task completed: {result}")
        
    except Exception as e:
        logger.error(f"Task failed: {e}")
        # Re-queue with backoff
        queue.add(task)  # Will be re-sorted by priority
        raise

def execute_task(task, checkpoint, logger):
    """Execute a work item with checkpointing"""
    # Route to appropriate handler based on task type
    handlers = {
        "research": "skills/academic-deep-research/execute.py",
        "coding": "skills/cosmic-krishna-coder/execute.py",
        "analysis": "skills/mech-interp/execute.py",
        # Add more...
    }
    
    handler = handlers.get(task.task_type, "orchestrator/default_handler.py")
    
    # Execute via subprocess to isolate
    import subprocess
    result = subprocess.run(
        [sys.executable, handler, json.dumps(task.to_dict())],
        capture_output=True,
        text=True,
        timeout=3600  # 1 hour max per task
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Handler failed: {result.stderr}")
    
    return result.stdout

def route_deep_work(logger):
    """Handle deep work session (night cycle)"""
    logger.info("Processing deep work trigger")
    
    # Deep work: extended session for complex tasks
    # Load highest priority complex task
    queue = WorkQueue()
    
    # Filter for complex tasks only
    complex_task = None
    for item in queue.items:
        if item.estimated_minutes > 30:
            complex_task = item
            break
    
    if not complex_task:
        logger.info("No complex tasks available")
        return
    
    # Execute with extended timeout
    logger.info(f"Starting deep work: {complex_task.task}")
    # ... similar to route_work but longer timeout

def route_summary(logger):
    """Generate daily summary"""
    logger.info("Generating daily summary")
    
    # Read completion log
    log_file = Path("/Users/dhyana/clawd/state/completion_log.jsonl")
    
    if not log_file.exists():
        logger.info("No completion log found")
        return
    
    # Parse last 24 hours
    # Generate summary
    # Send notification

def main():
    parser = argparse.ArgumentParser(description="DHARMIC CLAW Orchestrator")
    parser.add_argument("--mode", required=True,
                       choices=["heartbeat", "work", "deep_work", "summary", "health"],
                       help="Trigger mode")
    parser.add_argument("--event-type", help="Event type for event mode")
    parser.add_argument("--context", help="Additional context")
    
    args = parser.parse_args()
    
    logger = setup_logging(args.mode)
    logger.info(f"Trigger received: mode={args.mode}")
    
    # Route to handler
    routers = {
        "heartbeat": route_heartbeat,
        "work": route_work,
        "deep_work": route_deep_work,
        "summary": route_summary,
        "health": lambda l: None,  # Health check handled separately
    }
    
    router = routers.get(args.mode)
    if router:
        try:
            router(logger)
        except Exception as e:
            logger.error(f"Router failed: {e}")
            sys.exit(1)
    else:
        logger.error(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 9. OPERATIONAL RUNBOOKS

### 9.1 Emergency Procedures

```markdown
# Emergency Runbook

## Agent Not Responding

1. Check LaunchAgent status:
   launchctl list | grep dharmic-claw

2. Check cron:
   crontab -l | grep dharmic

3. Manual trigger:
   touch /Users/dhyana/clawd/.trigger

4. If still failing, check logs:
   tail -f /Users/dhyana/clawd/logs/launchd.err.log

## State Corruption

1. Stop all triggers:
   launchctl unload ~/Library/LaunchAgents/com.dharmic-claw.heartbeat.plist

2. Recover from backup:
   cp backups/state_YYYYMMDD_HHMM/* state/

3. Validate:
   python3 orchestrator/validate_state.py

4. Restart:
   launchctl load ~/Library/LaunchAgents/com.dharmic-claw.heartbeat.plist

## Git Corruption

1. Diagnose:
   cd /Users/dhyana/clawd && git status

2. If unrecoverable:
   git reset --hard HEAD
   # OR restore from remote
   git fetch origin
   git reset --hard origin/main

3. Rebuild state from files:
   python3 orchestrator/rebuild_state_from_git.py
```

### 9.2 Monitoring Queries

```bash
# Check system health
cat /Users/dhyana/clawd/state/health.json | jq .

# View recent work
 tail -20 /Users/dhyana/clawd/state/completion_log.jsonl

# Check queue status
python3 -c "from orchestrator.work_queue import WorkQueue; q = WorkQueue(); print(f'Pending: {len(q.items)}')"

# See current session
 cat /Users/dhyana/clawd/state/current_session.json

# Check cron logs
tail -50 /Users/dhyana/clawd/logs/cron_heartbeat.log
```

---

## 10. SUCCESS METRICS

### 10.1 Key Performance Indicators

| Metric | Target | Measurement |
|--------|--------|-------------|
| Trigger reliability | >99% | Successful executions / scheduled triggers |
| Work completion rate | >90% | Completed tasks / queued tasks (weekly) |
| State continuity | 100% | Sessions that successfully resume from checkpoint |
| Alert response time | <5 min | Time from failure detection to human alert |
| Mean recovery time | <10 min | Time to restore service after failure |
| False positive rate | <5% | Unnecessary alerts / total alerts |

### 10.2 Efficacy Measurements

```python
# Efficacy scoring algorithm
def calculate_efficacy_score(days=7):
    """
    Calculate autonomous operation efficacy score.
    0-100 scale, higher is better.
    """
    metrics = {
        # Reliability (40%)
        'trigger_success_rate': get_trigger_success_rate(days),  # 0-1
        
        # Productivity (30%)
        'tasks_completed_per_day': get_completion_rate(days),  # normalized
        
        # Continuity (20%)
        'checkpoint_recovery_rate': get_recovery_rate(days),  # 0-1
        
        # Health (10%)
        'system_health_score': get_health_score(),  # 0-1
    }
    
    weights = {
        'trigger_success_rate': 0.40,
        'tasks_completed_per_day': 0.30,
        'checkpoint_recovery_rate': 0.20,
        'system_health_score': 0.10,
    }
    
    score = sum(metrics[k] * weights[k] for k in metrics) * 100
    return round(score, 1)
```

---

## 11. CONCLUSION

This architecture provides:

1. **Multiple redundant triggers** ensuring the agent runs even if one mechanism fails
2. **Robust state management** enabling seamless continuity across stateless sessions
3. **Automatic checkpointing** minimizing work loss from interruptions
4. **Graceful degradation** allowing operation to continue at reduced capacity
5. **Comprehensive monitoring** providing visibility into system health
6. **Clear recovery procedures** enabling quick restoration from failures

The design treats the stateless nature of OpenClaw agents as an advantage—forcing explicit state management and making the system more resilient to failures.

**Next Steps:**
1. Review and approve architecture
2. Begin Phase 1 implementation
3. Set up monitoring baseline
4. Gradually transition existing automation

---

*Document Version: 4.0*  
*Last Updated: 2026-02-17 07:05 GMT+8*  
*Author: Infrastructure Architecture Subagent*
