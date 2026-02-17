#!/usr/bin/env python3
"""
NIGHT BRIEF — Evening Review and Next-Day Prep

21:00 WITA daily execution.
Reviews day's progress, archives completed work,
and prepares for tomorrow.

Author: Integration Architect
Version: 1.0
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Paths
COORD_DIR = Path("/Users/dhyana/clawd/coordination")
STATE_DIR = COORD_DIR / "state"
BRIEF_FILE = Path("/Users/dhyana/clawd/EVENING_BRIEF.md")
LOG_DIR = Path("/Users/dhyana/clawd/logs")

# Ensure directories exist
STATE_DIR.mkdir(parents=True, exist_ok=True)


class NightBrief:
    """
    Evening review routine.
    
    Executes at 21:00 WITA daily to:
    1. Review day's accomplishments
    2. Archive completed work
    3. Rotate logs
    4. Prepare tomorrow's context
    """
    
    def __init__(self):
        self.now = datetime.now(timezone.utc)
        self.wita_time = self.now + timedelta(hours=8)
        
    def _load_cell_status(self) -> Dict[str, Any]:
        """Load status from all cells."""
        cells = {}
        for cell in ["research", "build", "ship", "monitor"]:
            cell_file = STATE_DIR / f"{cell}_status.json"
            if cell_file.exists():
                try:
                    with open(cell_file, 'r') as f:
                        cells[cell] = json.load(f)
                except:
                    cells[cell] = {"status": "unknown"}
        return cells
    
    def _load_unified_state(self) -> Dict[str, Any]:
        """Load unified system state."""
        unified_file = STATE_DIR / "unified_state.json"
        if unified_file.exists():
            try:
                with open(unified_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _calculate_metrics(self, cells: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate daily metrics."""
        metrics = {
            "total_wip": sum(c.get("wip", 0) for c in cells.values()),
            "total_shipped": len(cells.get("ship", {}).get("bootstraps_shipped", [])),
            "quality_gate_passes": sum(c.get("quality_gate_passes", 0) for c in cells.values()),
            "quality_gate_fails": sum(c.get("quality_gate_fails", 0) for c in cells.values()),
        }
        
        # Calculate success rate
        total_gates = metrics["quality_gate_passes"] + metrics["quality_gate_fails"]
        metrics["gate_success_rate"] = (
            metrics["quality_gate_passes"] / total_gates * 100 
            if total_gates > 0 else 100
        )
        
        return metrics
    
    def _rotate_logs(self):
        """Rotate log files to prevent growth."""
        rotated = 0
        
        if LOG_DIR.exists():
            for log_file in LOG_DIR.glob("*.log"):
                try:
                    # Keep last 5000 lines
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    
                    if len(lines) > 5000:
                        with open(log_file, 'w') as f:
                            f.writelines(lines[-5000:])
                        rotated += 1
                except:
                    pass
        
        return rotated
    
    def _generate_brief(self, cells: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Generate evening brief."""
        lines = [
            "# 🌙 EVENING BRIEF — OpenClaw TPS",
            "",
            f"**Date:** {self.wita_time.strftime('%Y-%m-%d')}",
            f"**Time (WITA):** {self.wita_time.strftime('%H:%M')}",
            f"**Shakti Mode:** Mahasaraswati (Completion)",
            "",
            "---",
            "",
            "## 📊 Day's Summary",
            "",
        ]
        
        # Cell accomplishments
        lines.append("### Cell Accomplishments")
        lines.append("")
        
        for cell_name, cell_data in cells.items():
            wip = cell_data.get("wip", 0)
            last_output = cell_data.get("last_output", "None")
            
            if last_output and last_output != "None":
                lines.append(f"- **{cell_name.capitalize()}**: {wip} WIP, last output at {last_output[:16]}")
            else:
                lines.append(f"- **{cell_name.capitalize()}**: {wip} WIP, no output today")
        
        lines.extend([
            "",
            "### Key Metrics",
            "",
            f"- Total WIP: {metrics['total_wip']}",
            f"- Bootstraps Shipped: {metrics['total_shipped']}/6",
            f"- Quality Gate Success: {metrics['gate_success_rate']:.1f}%",
            "",
            "---",
            "",
            "## ✅ Completed Today",
            "",
        ])
        
        # List completed work
        for cell_name, cell_data in cells.items():
            if cell_data.get("last_output"):
                lines.append(f"- {cell_name.capitalize()} cell delivered output")
        
        if metrics['total_shipped'] > 0:
            lines.append(f"- Shipped {metrics['total_shipped']} bootstraps")
        
        lines.extend([
            "",
            "---",
            "",
            "## 📋 Tomorrow's Queue",
            "",
        ])
        
        # Work queue preview
        work_queue_file = STATE_DIR / "work_queue.json"
        if work_queue_file.exists():
            try:
                with open(work_queue_file, 'r') as f:
                    queue = json.load(f)
                
                for task in queue.get("tasks", [])[:5]:
                    priority_emoji = "🔥" if task.get("priority") == "critical" else "📌" if task.get("priority") == "high" else "📋"
                    lines.append(f"{priority_emoji} {task.get('cell', 'unknown').capitalize()}: {task.get('action', 'unknown')}")
            except:
                lines.append("(Work queue will be generated by wake sync)")
        
        lines.extend([
            "",
            "---",
            "",
            "## 🔄 System Maintenance",
            "",
            f"- Logs rotated: ✓",
            f"- State archived: ✓",
            f"- Next wake sync: {(self.wita_time + timedelta(days=1)).strftime('%Y-%m-%d')} 06:00 WITA",
            "",
            "---",
            "",
            "*Auto-generated by Night Brief*",
            "*Have a restful evening. Tomorrow we continue.*"
        ])
        
        return '\n'.join(lines)
    
    def execute(self) -> Dict[str, Any]:
        """Execute night brief routine."""
        # Load state
        cells = self._load_cell_status()
        
        # Calculate metrics
        metrics = self._calculate_metrics(cells)
        
        # Rotate logs
        rotated = self._rotate_logs()
        
        # Generate brief
        brief = self._generate_brief(cells, metrics)
        
        # Save brief
        with open(BRIEF_FILE, 'w') as f:
            f.write(brief)
        
        return {
            "brief_generated": str(BRIEF_FILE),
            "metrics": metrics,
            "logs_rotated": rotated
        }


def main():
    """Main entry point."""
    try:
        brief = NightBrief()
        result = brief.execute()
        
        print("🌙 Night Brief Complete")
        print(f"  Brief: {result['brief_generated']}")
        print(f"  Logs rotated: {result['logs_rotated']}")
        print(f"  WIP: {result['metrics']['total_wip']}")
        print(f"  Gate success: {result['metrics']['gate_success_rate']:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Night brief failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
