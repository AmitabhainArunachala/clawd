#!/usr/bin/env python3
"""
🕐 JIKOKU EMITTER — Temporal Span Generator
===========================================

Generates OpenTelemetry-style spans for temporal auditing.
Appends to JIKOKU_LOG.jsonl (append-only, like blockchain)

Usage:
  from jikoku_emitter import JikokuEmitter
  
  jk = JikokuEmitter()
  jk.emit_boot()
  jk.emit_task_start("Discord setup", "infrastructure", 15)
  # ... do work ...
  jk.emit_task_end(task_id, value_generated, artifacts, commits)
  jk.emit_session_summary(tasks, categories, muda, kaizen)
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

CLAWD_DIR = Path("/Users/dhyana/clawd")
JIKOKU_LOG = Path("/Users/dhyana/.openclaw/workspace/JIKOKU_LOG.jsonl")

class JikokuEmitter:
    """Emit JIKOKU temporal spans for self-auditing"""
    
    def __init__(self, agent_name="DHARMIC_CLAW"):
        self.agent = agent_name
        self.session_id = str(uuid.uuid4())[:8]
        self.boot_time = datetime.now(timezone.utc)
        self.tasks = {}
        self.current_task = None
        
        # Ensure log file exists
        JIKOKU_LOG.parent.mkdir(parents=True, exist_ok=True)
        if not JIKOKU_LOG.exists():
            self._write({
                "schema_version": "1.0",
                "created": self._now(),
                "system": "JIKOKU",
                "agent": self.agent
            })
    
    def _now(self):
        """ISO timestamp in UTC"""
        return datetime.now(timezone.utc).isoformat()
    
    def _write(self, data):
        """Append to JIKOKU_LOG.jsonl (append-only)"""
        with open(JIKOKU_LOG, "a") as f:
            f.write(json.dumps(data, separators=(',', ':')) + "\n")
    
    def emit_boot(self, files_read=None):
        """Emit BOOT span at session start"""
        duration_ms = int((datetime.now(timezone.utc) - self.boot_time).total_seconds() * 1000)
        
        span = {
            "timestamp": self._now(),
            "span_type": "BOOT",
            "session_id": self.session_id,
            "agent": self.agent,
            "boot_files_read": files_read or [],
            "duration_ms": duration_ms
        }
        self._write(span)
        return span
    
    def emit_task_start(self, task_name, category, estimated_min):
        """Emit TASK_START span"""
        task_id = str(uuid.uuid4())[:8]
        
        span = {
            "timestamp": self._now(),
            "span_type": "TASK_START",
            "task_id": task_id,
            "task_name": task_name,
            "category": category,  # code, research, comms, admin, meta, value, necessary, muda
            "estimated_duration_min": estimated_min
        }
        self._write(span)
        
        self.tasks[task_id] = {
            "name": task_name,
            "category": category,
            "start": datetime.now(timezone.utc),
            "estimated": estimated_min
        }
        self.current_task = task_id
        
        return task_id
    
    def emit_task_end(self, task_id, value_generated, artifacts=None, git_commits=None):
        """Emit TASK_END span"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        end_time = datetime.now(timezone.utc)
        duration = (end_time - task["start"]).total_seconds() / 60
        
        span = {
            "timestamp": self._now(),
            "span_type": "TASK_END",
            "task_id": task_id,
            "actual_duration_min": round(duration, 1),
            "value_generated": value_generated,
            "artifacts": artifacts or [],
            "git_commits": git_commits or []
        }
        self._write(span)
        
        self.current_task = None
        return span
    
    def emit_session_summary(self, categories=None, muda_detected=None, kaizen_opportunities=None):
        """Emit SESSION_SUMMARY span"""
        end_time = datetime.now(timezone.utc)
        total_duration = (end_time - self.boot_time).total_seconds() / 60
        
        # Calculate value-added ratio
        value_time = 0
        necessary_time = 0
        muda_time = 0
        
        for task_id, task in self.tasks.items():
            cat = task["category"]
            duration = task.get("actual_duration", task["estimated"])
            
            if cat in ["code", "research", "writing", "comms"]:
                value_time += duration
            elif cat in ["debug", "fix", "wait", "necessary"]:
                necessary_time += duration
            elif cat in ["admin", "meta", "muda"]:
                muda_time += duration
        
        total_accounted = value_time + necessary_time + muda_time
        if total_accounted > 0:
            value_ratio = (value_time / total_accounted) * 100
        else:
            value_ratio = 0
        
        span = {
            "timestamp": self._now(),
            "span_type": "SESSION_SUMMARY",
            "session_id": self.session_id,
            "total_duration_min": round(total_duration, 1),
            "tasks_completed": len(self.tasks),
            "categories": categories or {},
            "value_added_ratio": round(value_ratio, 1),
            "muda_detected": muda_detected or [],
            "kaizen_opportunities": kaizen_opportunities or []
        }
        self._write(span)
        
        # Alert if below threshold
        if value_ratio < 50:
            print(f"🚨 THEATER ALERT: value_added_ratio = {value_ratio:.1f}%")
        elif value_ratio < 80:
            print(f"⚠️  KAIZEN NEEDED: value_added_ratio = {value_ratio:.1f}%")
        
        return span
    
    def get_stats(self):
        """Get current session stats"""
        return {
            "session_id": self.session_id,
            "tasks": len(self.tasks),
            "current_task": self.current_task,
            "runtime_min": round((datetime.now(timezone.utc) - self.boot_time).total_seconds() / 60, 1)
        }

# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🕐 Testing JIKOKU Emitter...")
        
        jk = JikokuEmitter()
        
        # Boot
        jk.emit_boot(["CONSTITUTION.md", "SOUL.md", "jikoku_skill.md"])
        print("✅ BOOT emitted")
        
        # Task 1
        tid1 = jk.emit_task_start("Test task", "code", 5)
        print(f"✅ TASK_START: {tid1}")
        
        import time
        time.sleep(1)
        
        jk.emit_task_end(tid1, "Test completed", ["test.txt"], ["abc1234"])
        print("✅ TASK_END emitted")
        
        # Summary
        jk.emit_session_summary(
            categories={"code": 1},
            muda_detected=["test_muda"],
            kaizen_opportunities=["improve_test"]
        )
        print("✅ SESSION_SUMMARY emitted")
        
        print(f"\n📊 Stats: {jk.get_stats()}")
        print(f"📁 Log: {JIKOKU_LOG}")
        
        # Show last 3 lines
        if JIKOKU_LOG.exists():
            lines = JIKOKU_LOG.read_text().strip().split('\n')
            print(f"\n📝 Last entries:")
            for line in lines[-3:]:
                data = json.loads(line)
                print(f"   [{data.get('span_type', 'UNKNOWN')}] {data.get('timestamp', '')}")
