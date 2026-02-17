#!/usr/bin/env python3
"""
RESEARCH CELL — Maheshwari Mode Operations

Handles R_V paper work, AIKAGRYA insights, and arXiv ingestion.
WIP Limit: 3 concurrent projects
Quality Gate: Cited, actionable, non-duplicate

Author: Integration Architect
Version: 1.0
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Paths
CELL_DIR = Path("/Users/dhyana/clawd/cells/research")
STATE_FILE = Path("/Users/dhyana/clawd/coordination/state/research_status.json")
INPUT_DIR = CELL_DIR / "inputs"
WIP_DIR = CELL_DIR / "wip"
OUTPUT_DIR = CELL_DIR / "outputs"
ARCHIVE_DIR = CELL_DIR / "archive"

# Ensure directories exist
for d in [CELL_DIR, INPUT_DIR, WIP_DIR, OUTPUT_DIR, ARCHIVE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class ResearchCell:
    """
    Research work cell implementing Maheshwari (Vision) mode.
    
    Responsible for:
    - arXiv paper ingestion
    - R_V paper development
    - AIKAGRYA insight capture
    - Citation management
    """
    
    WIP_LIMIT = 3
    
    def __init__(self):
        self.status = {
            "cell": "research",
            "shakti_mode": "Maheshwari",
            "wip": 0,
            "limit": self.WIP_LIMIT,
            "last_output": None,
            "active_projects": [],
            "quality_gate_passes": 0,
            "quality_gate_fails": 0
        }
    
    def _load_state(self) -> Dict[str, Any]:
        """Load current cell state."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self.status
    
    def _save_state(self):
        """Save cell state."""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.status, f, indent=2, default=str)
    
    def _count_wip(self) -> int:
        """Count work in progress."""
        return len(list(WIP_DIR.glob("*.md")))
    
    def _get_active_projects(self) -> List[Dict[str, Any]]:
        """Get list of active projects."""
        projects = []
        for f in WIP_DIR.glob("*.json"):
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                    projects.append(data)
            except:
                pass
        return projects
    
    def _check_arxiv_feed(self):
        """Check for new arXiv papers."""
        # Placeholder for arXiv RSS integration
        # In production, this would parse https://rss.arxiv.org/rss/atom-ph
        return []
    
    def _check_insight_queue(self):
        """Check for captured insights awaiting processing."""
        insights = []
        for f in INPUT_DIR.glob("insight_*.json"):
            try:
                with open(f, 'r') as fp:
                    data = json.load(f)
                    insights.append({"file": f, "data": data})
            except:
                pass
        return insights
    
    def _process_insight(self, insight: Dict[str, Any]) -> bool:
        """
        Process a captured insight through the quality gate.
        
        Gate Criteria:
        - Has source/reference
        - Is actionable
        - Not a duplicate
        """
        data = insight["data"]
        
        # Check 1: Has source
        if not data.get("source"):
            return False
        
        # Check 2: Is actionable
        if not data.get("actionable", False):
            return False
        
        # Check 3: Not duplicate (simple check)
        insight_text = data.get("text", "")
        for existing in OUTPUT_DIR.glob("*.md"):
            with open(existing, 'r') as f:
                if insight_text[:100] in f.read():
                    return False  # Duplicate
        
        return True
    
    def _archive_completed(self):
        """Move completed projects to archive."""
        # Find projects marked complete
        for f in WIP_DIR.glob("*.json"):
            try:
                with open(f, 'r') as fp:
                    data = json.load(fp)
                    if data.get("status") == "completed":
                        # Move to archive
                        target = ARCHIVE_DIR / f.name
                        f.rename(target)
                        
                        # Also move associated markdown
                        md_file = WIP_DIR / f.stem.replace("_meta", "") + ".md"
                        if md_file.exists():
                            md_file.rename(ARCHIVE_DIR / md_file.name)
            except:
                pass
    
    def pulse(self) -> Dict[str, Any]:
        """
        Execute a research cell pulse.
        
        Called every 15 minutes by cron.
        """
        # Load current state
        self.status = self._load_state()
        
        # Update WIP count
        self.status["wip"] = self._count_wip()
        self.status["active_projects"] = self._get_active_projects()
        
        # Check inputs
        new_papers = self._check_arxiv_feed()
        insights = self._check_insight_queue()
        
        # Process insights if WIP allows
        processed = 0
        for insight in insights:
            if self.status["wip"] >= self.WIP_LIMIT:
                break
            
            if self._process_insight(insight):
                # Move to WIP
                target = WIP_DIR / insight["file"].name
                insight["file"].rename(target)
                self.status["wip"] += 1
                self.status["quality_gate_passes"] += 1
                processed += 1
            else:
                self.status["quality_gate_fails"] += 1
        
        # Archive completed
        self._archive_completed()
        
        # Update last output timestamp if anything was processed
        if processed > 0:
            self.status["last_output"] = datetime.now(timezone.utc).isoformat()
        
        # Save state
        self._save_state()
        
        return {
            "cell": "research",
            "wip": self.status["wip"],
            "processed_insights": processed,
            "new_papers": len(new_papers),
            "status": "ok"
        }


def main():
    """Main entry point."""
    try:
        cell = ResearchCell()
        result = cell.pulse()
        
        print(f"Research Cell Pulse: {result['status']}")
        print(f"  WIP: {result['wip']}/{ResearchCell.WIP_LIMIT}")
        print(f"  Processed: {result['processed_insights']} insights")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Research cell failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
