#!/usr/bin/env python3
"""
ANDON BOARD — Visual Escalation System

Implements the Toyota Andon cord concept for OpenClaw.
Provides visual status of all work cells and automatic escalation.

Levels:
  - Green: Normal operation
  - Yellow: Warning (attention needed)
  - Red: Critical (stop line for some cells)
  - Cord Pulled: Emergency (all-hands)

Author: Integration Architect
Version: 1.0
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Paths
COORD_DIR = Path("/Users/dhyana/clawd/coordination")
STATE_DIR = COORD_DIR / "state"
ANDON_FILE = COORD_DIR / "ANDON_BOARD.md"
ALERT_QUEUE_FILE = STATE_DIR / "alert_queue.json"
ESCALATION_LOG = Path("/Users/dhyana/clawd/logs/escalation.log")

# Ensure directories exist
STATE_DIR.mkdir(parents=True, exist_ok=True)
Path("/Users/dhyana/clawd/logs").mkdir(parents=True, exist_ok=True)


class AndonBoard:
    """
    Visual escalation board for the OpenClaw factory floor.
    
    Monitors all cells and triggers escalation based on defined thresholds.
    """
    
    # Escalation thresholds
    THRESHOLDS = {
        "research": {
            "yellow": {"stale_output": 3600},      # 1 hour
            "red": {"stale_output": 14400},       # 4 hours
        },
        "build": {
            "yellow": {"test_failure": 3600, "stale_output": 1800},
            "red": {"test_failure": 7200, "stale_output": 7200},
        },
        "ship": {
            "yellow": {"stale_output": 3600, "wip_high": True},
            "red": {"stale_output": 86400},        # 24 hours
        },
        "monitor": {
            "yellow": {"metric_stale": 300},       # 5 minutes
            "red": {"metric_stale": 600},          # 10 minutes
        }
    }
    
    def __init__(self):
        self.cells = {}
        self.alerts = []
        self.overall_status = "green"
        
    def _load_cell_status(self, cell: str) -> Dict[str, Any]:
        """Load status for a specific cell."""
        cell_file = STATE_DIR / f"{cell}_status.json"
        if cell_file.exists():
            try:
                with open(cell_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"status": "unknown", "last_output": None}
    
    def _check_staleness(self, timestamp_str: Optional[str]) -> int:
        """Calculate staleness in seconds."""
        if not timestamp_str:
            return float('inf')
        
        try:
            ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            return int((now - ts).total_seconds())
        except:
            return float('inf')
    
    def _evaluate_cell(self, cell: str, status: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a cell against thresholds and return status."""
        thresholds = self.THRESHOLDS.get(cell, {})
        result = {
            "name": cell,
            "raw_status": status,
            "staleness": 0,
            "level": "green",
            "reasons": []
        }
        
        # Check staleness
        last_output = status.get("last_output")
        stale_seconds = self._check_staleness(last_output)
        result["staleness"] = stale_seconds
        
        # Check yellow thresholds
        yellow = thresholds.get("yellow", {})
        if "stale_output" in yellow and stale_seconds > yellow["stale_output"]:
            result["level"] = "yellow"
            result["reasons"].append(f"stale for {stale_seconds//60}m")
        
        if "wip_high" in yellow and status.get("wip", 0) >= status.get("limit", 999):
            result["level"] = "yellow"
            result["reasons"].append("WIP at limit")
        
        # Check red thresholds
        red = thresholds.get("red", {})
        if "stale_output" in red and stale_seconds > red["stale_output"]:
            result["level"] = "red"
            result["reasons"].append(f"CRITICAL: stale for {stale_seconds//3600}h")
        
        if "test_failure" in red:
            # Check for test failures
            failures = status.get("test_failures", 0)
            if failures > 0:
                fail_duration = status.get("failure_duration", 0)
                if fail_duration > red["test_failure"]:
                    result["level"] = "red"
                    result["reasons"].append(f"tests failing for {fail_duration//3600}h")
        
        return result
    
    def _evaluate_all_cells(self) -> Dict[str, Any]:
        """Evaluate all cells and return status map."""
        cells = {}
        worst_level = "green"
        
        for cell in ["research", "build", "ship", "monitor"]:
            status = self._load_cell_status(cell)
            eval_result = self._evaluate_cell(cell, status)
            cells[cell] = eval_result
            
            # Track worst level
            if eval_result["level"] == "red":
                worst_level = "red"
            elif eval_result["level"] == "yellow" and worst_level != "red":
                worst_level = "yellow"
        
        return {
            "cells": cells,
            "overall": worst_level,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_alerts(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts from evaluation."""
        alerts = []
        
        for cell_name, cell_eval in evaluation["cells"].items():
            if cell_eval["level"] in ["yellow", "red"]:
                alert = {
                    "id": f"{cell_name}_{int(datetime.now(timezone.utc).timestamp())}",
                    "cell": cell_name,
                    "level": cell_eval["level"],
                    "reasons": cell_eval["reasons"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "acknowledged": False
                }
                alerts.append(alert)
        
        return alerts
    
    def _load_existing_alerts(self) -> List[Dict[str, Any]]:
        """Load existing alerts from queue."""
        if ALERT_QUEUE_FILE.exists():
            try:
                with open(ALERT_QUEUE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_alerts(self, alerts: List[Dict[str, Any]]):
        """Save alert queue."""
        with open(ALERT_QUEUE_FILE, 'w') as f:
            json.dump(alerts, f, indent=2, default=str)
    
    def _update_alert_queue(self, new_alerts: List[Dict[str, Any]]):
        """Merge new alerts with existing queue."""
        existing = self._load_existing_alerts()
        
        # Add new alerts
        for alert in new_alerts:
            # Check if similar alert already exists
            duplicate = False
            for existing_alert in existing:
                if (existing_alert["cell"] == alert["cell"] and 
                    existing_alert["level"] == alert["level"] and
                    not existing_alert.get("acknowledged")):
                    duplicate = True
                    break
            
            if not duplicate:
                existing.append(alert)
        
        # Clean up old acknowledged alerts
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)
        
        existing = [
            a for a in existing 
            if not (a.get("acknowledged") and 
                   datetime.fromisoformat(a["timestamp"].replace('Z', '+00:00')) < cutoff)
        ]
        
        self._save_alerts(existing)
        return existing
    
    def _generate_board_markdown(self, evaluation: Dict[str, Any], alerts: List[Dict[str, Any]]) -> str:
        """Generate the visual Andon board in Markdown."""
        now = datetime.now(timezone.utc)
        
        # Status emoji mapping
        status_emoji = {
            "green": "🟢",
            "yellow": "🟡",
            "red": "🔴",
            "unknown": "⚪"
        }
        
        lines = [
            "# 🚨 ANDON BOARD — OpenClaw Factory Floor",
            "",
            f"**Last Updated:** {now.isoformat()} UTC",
            f"**Overall Status:** {status_emoji.get(evaluation['overall'], '⚪')} {evaluation['overall'].upper()}",
            f"**Takt Cycle:** Active",
            "",
            "---",
            "",
            "## Cell Status",
            "",
            "| Cell | Status | WIP | Staleness | Reasons |",
            "|------|--------|-----|-----------|---------|"
        ]
        
        for cell_name, cell_eval in evaluation["cells"].items():
            emoji = status_emoji.get(cell_eval["level"], "⚪")
            wip = cell_eval["raw_status"].get("wip", 0)
            limit = cell_eval["raw_status"].get("limit", "∞")
            stale = f"{cell_eval['staleness']//60}m" if cell_eval["staleness"] < 3600 else f"{cell_eval['staleness']//3600}h"
            reasons = ", ".join(cell_eval["reasons"]) if cell_eval["reasons"] else "-"
            
            lines.append(f"| {cell_name.capitalize()} | {emoji} {cell_eval['level'].upper()} | {wip}/{limit} | {stale} | {reasons} |")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Active alerts section
        unacknowledged = [a for a in alerts if not a.get("acknowledged")]
        
        if unacknowledged:
            lines.append("## Active Alerts")
            lines.append("")
            
            for alert in unacknowledged:
                emoji = "🔴" if alert["level"] == "red" else "🟡"
                reasons = ", ".join(alert["reasons"])
                lines.append(f"{emoji} **{alert['cell'].upper()}** ({alert['level'].upper()}): {reasons}")
                lines.append(f"   - Time: {alert['timestamp']}")
                lines.append(f"   - ID: `{alert['id']}`")
                lines.append("")
        else:
            lines.append("## Active Alerts")
            lines.append("")
            lines.append("✅ No active alerts")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Legend
        lines.append("## Legend")
        lines.append("")
        lines.append("- 🟢 **GREEN**: Normal operation")
        lines.append("- 🟡 **YELLOW**: Warning - attention needed")
        lines.append("- 🔴 **RED**: Critical - stop line for affected cell")
        lines.append("- ⚪ **UNKNOWN**: Status unavailable")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Auto-generated by Andon System*")
        
        return '\n'.join(lines)
    
    def _log_escalation(self, evaluation: Dict[str, Any]):
        """Log escalation events."""
        now = datetime.now(timezone.utc)
        
        if evaluation["overall"] != "green":
            log_entry = f"[{now.isoformat()}] ESCALATION: {evaluation['overall'].upper()}"
            for cell_name, cell_eval in evaluation["cells"].items():
                if cell_eval["level"] != "green":
                    log_entry += f" | {cell_name}:{cell_eval['level']}"
            log_entry += "\n"
            
            with open(ESCALATION_LOG, 'a') as f:
                f.write(log_entry)
    
    def update(self):
        """Update the Andon board."""
        # Evaluate all cells
        evaluation = self._evaluate_all_cells()
        
        # Generate new alerts
        new_alerts = self._generate_alerts(evaluation)
        
        # Update alert queue
        all_alerts = self._update_alert_queue(new_alerts)
        
        # Generate board
        board_md = self._generate_board_markdown(evaluation, all_alerts)
        
        # Save board
        with open(ANDON_FILE, 'w') as f:
            f.write(board_md)
        
        # Log escalation
        self._log_escalation(evaluation)
        
        return {
            "evaluation": evaluation,
            "alerts": all_alerts,
            "board_path": str(ANDON_FILE)
        }
    
    def pull_cord(self, reason: str, cell: Optional[str] = None):
        """
        Pull the Andon cord - emergency stop.
        
        This is a manual escalation for critical situations.
        """
        now = datetime.now(timezone.utc)
        
        emergency = {
            "type": "CORD_PULLED",
            "timestamp": now.isoformat(),
            "reason": reason,
            "cell": cell,
            "status": "active"
        }
        
        # Save emergency state
        emergency_file = STATE_DIR / "emergency_stop.json"
        with open(emergency_file, 'w') as f:
            json.dump(emergency, f, indent=2)
        
        # Log
        with open(ESCALATION_LOG, 'a') as f:
            f.write(f"[{now.isoformat()}] 🚨 CORD PULLED: {reason}\n")
        
        print(f"🚨 ANDON CORD PULLED: {reason}")
        print(f"Emergency stop activated. Manual intervention required.")
        
        return emergency
    
    def reset_cord(self):
        """Reset the Andon cord after fix."""
        emergency_file = STATE_DIR / "emergency_stop.json"
        
        if emergency_file.exists():
            with open(emergency_file, 'r') as f:
                emergency = json.load(f)
            
            emergency["status"] = "resolved"
            emergency["resolved_at"] = datetime.now(timezone.utc).isoformat()
            
            with open(emergency_file, 'w') as f:
                json.dump(emergency, f, indent=2)
            
            now = datetime.now(timezone.utc)
            with open(ESCALATION_LOG, 'a') as f:
                f.write(f"[{now.isoformat()}] ✅ CORD RESET: Emergency resolved\n")
            
            return True
        
        return False


def main():
    parser = argparse.ArgumentParser(description="Andon Board System")
    parser.add_argument("--update", action="store_true", help="Update the board")
    parser.add_argument("--pull", metavar="REASON", help="Pull the andon cord")
    parser.add_argument("--reset", action="store_true", help="Reset the cord")
    parser.add_argument("--cell", help="Cell name for cord pull")
    
    args = parser.parse_args()
    
    board = AndonBoard()
    
    if args.pull:
        result = board.pull_cord(args.pull, args.cell)
        return 0 if result else 1
    
    elif args.reset:
        if board.reset_cord():
            print("✅ Andon cord reset")
            return 0
        else:
            print("No active cord to reset")
            return 1
    
    else:
        # Default: update board
        result = board.update()
        print(f"Andon board updated: {result['board_path']}")
        print(f"Overall status: {result['evaluation']['overall'].upper()}")
        print(f"Active alerts: {len([a for a in result['alerts'] if not a.get('acknowledged')])}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
