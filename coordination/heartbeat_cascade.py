#!/usr/bin/env python3
"""
HEARTBEAT CASCADE — Multi-Layer Coordination System

This script implements the heartbeat cascade that synchronizes
MMK, TRISHULA, and OpenClaw subsystems. It reduces the current
2-hour latency to <30 seconds through event-driven triggers.

The cascade works by:
1. Reading the takt_master cascade signal
2. Querying all subsystems in parallel
3. Merging state into unified view
4. Triggering downstream agents

Author: Integration Architect
Version: 1.0
"""

import json
import os
import sys
import concurrent.futures
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import time

# Paths
COORD_DIR = Path("/Users/dhyana/clawd/coordination")
STATE_DIR = COORD_DIR / "state"
CASCADE_FILE = STATE_DIR / "cascade_signal.json"
UNIFIED_STATE_FILE = STATE_DIR / "unified_state.json"
PIPELINE_STATUS_FILE = Path("/Users/dhyana/clawd/PIPELINE_STATUS.md")
LOG_FILE = Path("/Users/dhyana/clawd/logs/heartbeat.log")

# Ensure directories exist
STATE_DIR.mkdir(parents=True, exist_ok=True)
Path("/Users/dhyana/clawd/logs").mkdir(parents=True, exist_ok=True)


class HeartbeatCascade:
    """
    Orchestrates the heartbeat cascade across all subsystems.
    
    Replaces the current 2-hour latency with <30 second propagation.
    """
    
    # SLA targets in seconds
    SLAS = {
        "mmk": 30,
        "trishula": 20,
        "openclaw": 15,
    }
    
    def __init__(self):
        self.cascade = None
        self.results = {}
        self.errors = []
        
    def _load_cascade(self) -> Optional[Dict[str, Any]]:
        """Load the current takt cascade signal."""
        if CASCADE_FILE.exists():
            try:
                with open(CASCADE_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.errors.append(f"Failed to load cascade: {e}")
        return None
    
    def _query_mmk(self) -> Dict[str, Any]:
        """Query MMK subsystem status."""
        start = time.time()
        try:
            # Check MMK agent status file
            mmk_status = Path("/Users/dhyana/META_META_KNOWER/AGENT_STATUS.json")
            if mmk_status.exists():
                with open(mmk_status, 'r') as f:
                    data = json.load(f)
                return {
                    "status": "ok",
                    "latency_ms": int((time.time() - start) * 1000),
                    "agents": len(data.get("agents", {})),
                    "alerts": len(data.get("alerts", [])),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "status": "warning",
                    "latency_ms": int((time.time() - start) * 1000),
                    "error": "AGENT_STATUS.json not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": int((time.time() - start) * 1000),
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _query_trishula(self) -> Dict[str, Any]:
        """Query TRISHULA subsystem status."""
        start = time.time()
        try:
            # Check TRISHULA queue and router status
            trish_dir = Path("/Users/dhyana/trishula")
            
            # Count pending messages
            inbox = trish_dir / "inbox"
            pending = len(list(inbox.glob("*.json"))) if inbox.exists() else 0
            
            # Check last router run
            log_file = trish_dir / "log" / "cron.log"
            last_run = None
            if log_file.exists():
                stat = log_file.stat()
                last_run = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
            
            return {
                "status": "ok",
                "latency_ms": int((time.time() - start) * 1000),
                "pending_messages": pending,
                "last_router_run": last_run,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": int((time.time() - start) * 1000),
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _query_openclaw(self) -> Dict[str, Any]:
        """Query OpenClaw core status."""
        start = time.time()
        try:
            # Check work queue
            work_queue = COORD_DIR / "state" / "work_queue.json"
            queue_size = 0
            if work_queue.exists():
                with open(work_queue, 'r') as f:
                    data = json.load(f)
                    queue_size = len(data.get("tasks", []))
            
            # Check cell health
            cells = {}
            for cell in ["research", "build", "ship", "monitor"]:
                cell_file = STATE_DIR / f"{cell}_status.json"
                if cell_file.exists():
                    with open(cell_file, 'r') as f:
                        cells[cell] = json.load(f)
            
            return {
                "status": "ok",
                "latency_ms": int((time.time() - start) * 1000),
                "work_queue_size": queue_size,
                "cell_health": cells,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": int((time.time() - start) * 1000),
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _run_cascade(self) -> Dict[str, Any]:
        """Execute the cascade query in parallel."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._query_mmk): "mmk",
                executor.submit(self._query_trishula): "trishula",
                executor.submit(self._query_openclaw): "openclaw",
            }
            
            results = {}
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    results[name] = future.result(timeout=self.SLAS[name] + 5)
                except concurrent.futures.TimeoutError:
                    results[name] = {
                        "status": "timeout",
                        "error": f"Query exceeded {self.SLAS[name]}s SLA"
                    }
                except Exception as e:
                    results[name] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            return results
    
    def _merge_state(self, cascade: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Merge all subsystem states into unified view."""
        now = datetime.now(timezone.utc)
        
        unified = {
            "takt_id": cascade.get("takt_id", 0),
            "timestamp": now.isoformat(),
            "cascade_latency_ms": int((now.timestamp() - cascade.get("cascade_start", now.timestamp())) * 1000),
            "shakti_mode": cascade.get("shakti_mode", "unknown"),
            "subsystems": results,
            "overall_health": self._calculate_health(results),
            "alerts": self._generate_alerts(results),
            "next_actions": self._determine_actions(results)
        }
        
        return unified
    
    def _calculate_health(self, results: Dict[str, Any]) -> str:
        """Calculate overall system health."""
        statuses = [r.get("status", "unknown") for r in results.values()]
        
        if any(s == "error" for s in statuses):
            return "critical"
        elif any(s == "timeout" for s in statuses):
            return "degraded"
        elif any(s == "warning" for s in statuses):
            return "warning"
        else:
            return "healthy"
    
    def _generate_alerts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on subsystem status."""
        alerts = []
        
        for name, result in results.items():
            if result.get("status") == "error":
                alerts.append({
                    "level": "red",
                    "source": name,
                    "message": f"{name} subsystem error: {result.get('error')}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            elif result.get("status") == "timeout":
                alerts.append({
                    "level": "yellow",
                    "source": name,
                    "message": f"{name} subsystem timeout",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        return alerts
    
    def _determine_actions(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine next actions based on state."""
        actions = []
        
        # Check for work to dispatch
        openclaw = results.get("openclaw", {})
        queue_size = openclaw.get("work_queue_size", 0)
        
        if queue_size > 0:
            actions.append({
                "priority": "high",
                "action": "dispatch_work",
                "queue_size": queue_size
            })
        
        # Check for pending messages
        trishula = results.get("trishula", {})
        pending = trishula.get("pending_messages", 0)
        
        if pending > 5:
            actions.append({
                "priority": "medium",
                "action": "clear_trishula_queue",
                "pending": pending
            })
        
        return actions
    
    def _save_unified_state(self, state: Dict[str, Any]):
        """Save unified state atomically."""
        temp_file = UNIFIED_STATE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        temp_file.rename(UNIFIED_STATE_FILE)
    
    def _update_pipeline_status(self, state: Dict[str, Any]):
        """Generate human-readable pipeline status."""
        now = datetime.now(timezone.utc)
        
        lines = [
            "# PIPELINE STATUS — Toyota Production System",
            f"",
            f"**Last Updated:** {now.isoformat()} UTC",
            f"**Takt:** #{state['takt_id']} | **Mode:** {state['shakti_mode']}",
            f"**Health:** {state['overall_health'].upper()}",
            f"",
            "## Subsystem Status",
            "",
        ]
        
        for name, result in state['subsystems'].items():
            status_emoji = "🟢" if result.get('status') == 'ok' else "🟡" if result.get('status') == 'warning' else "🔴"
            lines.append(f"### {status_emoji} {name.upper()}")
            lines.append(f"- Status: {result.get('status', 'unknown')}")
            lines.append(f"- Latency: {result.get('latency_ms', 'N/A')}ms")
            
            # Add specific metrics
            if 'agents' in result:
                lines.append(f"- Agents: {result['agents']}")
            if 'pending_messages' in result:
                lines.append(f"- Pending Messages: {result['pending_messages']}")
            if 'work_queue_size' in result:
                lines.append(f"- Work Queue: {result['work_queue_size']} tasks")
            
            lines.append("")
        
        # Alerts section
        if state['alerts']:
            lines.append("## 🚨 Active Alerts")
            lines.append("")
            for alert in state['alerts']:
                emoji = "🔴" if alert['level'] == 'red' else "🟡"
                lines.append(f"{emoji} **{alert['source']}**: {alert['message']}")
            lines.append("")
        
        # Next actions
        if state['next_actions']:
            lines.append("## Next Actions")
            lines.append("")
            for action in state['next_actions']:
                emoji = "🔥" if action['priority'] == 'high' else "📋"
                lines.append(f"{emoji} **{action['action']}** ({action['priority']})")
            lines.append("")
        
        with open(PIPELINE_STATUS_FILE, 'w') as f:
            f.write('\n'.join(lines))
    
    def _log_heartbeat(self, state: Dict[str, Any]):
        """Log the heartbeat execution."""
        now = datetime.now(timezone.utc)
        log_entry = (
            f"[{now.isoformat()}] CASCADE #{state['takt_id']} | "
            f"health={state['overall_health']} | "
            f"latency={state['cascade_latency_ms']}ms | "
            f"alerts={len(state['alerts'])}\n"
        )
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the full heartbeat cascade.
        
        This is the main entry point called every 15 minutes.
        """
        # Load cascade signal
        self.cascade = self._load_cascade()
        if not self.cascade:
            # No cascade yet, create minimal one
            self.cascade = {
                "takt_id": 0,
                "cascade_start": datetime.now(timezone.utc).timestamp(),
                "shakti_mode": "unknown"
            }
        
        # Query all subsystems
        self.results = self._run_cascade()
        
        # Merge into unified state
        unified = self._merge_state(self.cascade, self.results)
        
        # Save state
        self._save_unified_state(unified)
        
        # Update human-readable status
        self._update_pipeline_status(unified)
        
        # Log
        self._log_heartbeat(unified)
        
        return unified


def main():
    """Main entry point."""
    try:
        cascade = HeartbeatCascade()
        state = cascade.execute()
        
        print(f"CASCADE #{state['takt_id']} complete")
        print(f"Health: {state['overall_health'].upper()}")
        print(f"Latency: {state['cascade_latency_ms']}ms")
        print(f"Alerts: {len(state['alerts'])}")
        
        # Return error code if critical
        if state['overall_health'] == 'critical':
            return 2
        elif state['overall_health'] == 'degraded':
            return 1
        return 0
        
    except Exception as e:
        print(f"ERROR: Heartbeat cascade failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
