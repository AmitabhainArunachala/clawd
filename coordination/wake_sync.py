#!/usr/bin/env python3
"""
WAKE SYNC — Morning Brief and Day Preparation

06:00 WITA daily execution.
Synchronizes all systems, generates morning brief,
and prepares the work queue for the day.

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
BRIEF_FILE = Path("/Users/dhyana/clawd/MORNING_BRIEF.md")
WORK_QUEUE_FILE = STATE_DIR / "work_queue.json"

# Ensure directories exist
STATE_DIR.mkdir(parents=True, exist_ok=True)


class WakeSync:
    """
    Morning synchronization routine.
    
    Executes at 06:00 WITA daily to:
    1. Sync with MMK and TRISHULA
    2. Generate morning brief
    3. Prepare work queue
    4. Set daily priorities
    """
    
    def __init__(self):
        self.now = datetime.now(timezone.utc)
        self.wita_time = self.now + timedelta(hours=8)  # WITA = UTC+8
        
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
    
    def _get_shakti_mode(self) -> str:
        """Get current Shakti mode for morning."""
        hour = self.wita_time.hour
        if 6 <= hour < 9:
            return "Maheshwari (Vision)"
        elif 9 <= hour < 12:
            return "Mahakali (Cutting)"
        elif 14 <= hour < 17:
            return "Mahalakshmi (Harmony)"
        elif 19 <= hour < 22:
            return "Mahasaraswati (Completion)"
        return "Rest"
    
    def _generate_brief(self, cells: Dict[str, Any], unified: Dict[str, Any]) -> str:
        """Generate the morning brief markdown."""
        shakti = self._get_shakti_mode()
        
        lines = [
            "# 🌅 MORNING BRIEF — OpenClaw TPS",
            "",
            f"**Date:** {self.wita_time.strftime('%Y-%m-%d')}",
            f"**Time (WITA):** {self.wita_time.strftime('%H:%M')}",
            f"**Shakti Mode:** {shakti}",
            f"**Overall Health:** {unified.get('overall_health', 'unknown').upper()}",
            "",
            "---",
            "",
            "## 📊 Cell Status Overnight",
            "",
        ]
        
        for cell_name, cell_data in cells.items():
            emoji = "🟢" if cell_data.get("quality_gate") == "passed" else "🟡" if cell_data.get("quality_gate") == "warning" else "🔴"
            wip = cell_data.get("wip", 0)
            limit = cell_data.get("limit", "∞")
            lines.append(f"{emoji} **{cell_name.capitalize()}**: {wip}/{limit} WIP")
        
        lines.extend([
            "",
            "---",
            "",
            "## 🎯 Today's Priorities",
            "",
            "### Research (Maheshwari)",
            "- [ ] Process overnight arXiv feed",
            "- [ ] Advance R_V paper section",
            "- [ ] Capture 3+ AIKAGRYA insights",
            "",
            "### Build (Mahakali)",
            "- [ ] Resolve DGC test failures",
            "- [ ] Implement SwarmProposal API fix",
            "- [ ] WITNESS MVP progress",
            "",
            "### Ship (Mahalakshmi)",
            "- [ ] Queue next bootstrap for release",
            "- [ ] Review revenue pipeline",
            "- [ ] Customer outreach",
            "",
            "### Monitor (Mahasaraswati)",
            "- [ ] Review overnight alerts",
            "- [ ] Update Andon board",
            "- [ ] Generate daily metrics",
            "",
            "---",
            "",
            "## 📈 Key Metrics",
            "",
        ])
        
        # Add ship metrics if available
        ship = cells.get("ship", {})
        revenue = ship.get("revenue_pipeline", {})
        lines.append(f"- Bootstraps Shipped: {len(ship.get('bootstraps_shipped', []))}/6")
        lines.append(f"- Week 1 Progress: ${revenue.get('progress_week_1', 0):.2f} / $100")
        lines.append(f"- Work Queue: {sum(c.get('wip', 0) for c in cells.values())} active tasks")
        
        lines.extend([
            "",
            "---",
            "",
            "## 🔄 Today's Takt Schedule",
            "",
            "| Time | Mode | Focus |",
            "|------|------|-------|",
            "| 06:00-09:00 | Maheshwari | Vision, Planning, Research |",
            "| 09:00-12:00 | Mahakali | Deep Work, Coding, Problem Solving |",
            "| 12:00-14:00 | — | Lunch, Rest |",
            "| 14:00-17:00 | Mahalakshmi | Integration, Reviews, Collaboration |",
            "| 17:00-19:00 | — | Transition |",
            "| 19:00-22:00 | Mahasaraswati | Completion, Documentation, Prep |",
            "",
            "---",
            "",
            "*Auto-generated by Wake Sync*",
            f"*Next brief: {(self.wita_time + timedelta(days=1)).strftime('%Y-%m-%d')} 06:00 WITA*"
        ])
        
        return '\n'.join(lines)
    
    def _prepare_work_queue(self, cells: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the day's work queue."""
        queue = {
            "date": self.wita_time.strftime('%Y-%m-%d'),
            "generated_at": self.now.isoformat(),
            "tasks": []
        }
        
        # Research tasks
        research = cells.get("research", {})
        if research.get("wip", 0) < research.get("limit", 3):
            queue["tasks"].append({
                "id": f"research_{self.now.timestamp()}",
                "cell": "research",
                "priority": "high",
                "action": "process_arxiv_feed",
                "estimated_time": "30 min"
            })
        
        # Build tasks
        build = cells.get("build", {})
        if build.get("quality_gate") == "failed":
            queue["tasks"].append({
                "id": f"build_{self.now.timestamp()}",
                "cell": "build",
                "priority": "critical",
                "action": "fix_test_failures",
                "estimated_time": "2 hours"
            })
        
        # Ship tasks
        ship = cells.get("ship", {})
        if ship.get("queue_depth", 0) > 0:
            queue["tasks"].append({
                "id": f"ship_{self.now.timestamp()}",
                "cell": "ship",
                "priority": "medium",
                "action": "process_ship_queue",
                "estimated_time": "1 hour"
            })
        
        return queue
    
    def execute(self) -> Dict[str, Any]:
        """Execute wake sync routine."""
        # Load current state
        cells = self._load_cell_status()
        unified = self._load_unified_state()
        
        # Generate brief
        brief = self._generate_brief(cells, unified)
        
        # Save brief
        with open(BRIEF_FILE, 'w') as f:
            f.write(brief)
        
        # Prepare work queue
        queue = self._prepare_work_queue(cells)
        
        # Save work queue
        with open(WORK_QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=2, default=str)
        
        return {
            "brief_generated": str(BRIEF_FILE),
            "work_queue_tasks": len(queue["tasks"]),
            "shakti_mode": self._get_shakti_mode(),
            "cell_status": {k: v.get("wip", 0) for k, v in cells.items()}
        }


def main():
    """Main entry point."""
    try:
        sync = WakeSync()
        result = sync.execute()
        
        print("🌅 Wake Sync Complete")
        print(f"  Brief: {result['brief_generated']}")
        print(f"  Tasks queued: {result['work_queue_tasks']}")
        print(f"  Mode: {result['shakti_mode']}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Wake sync failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
