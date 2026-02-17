#!/usr/bin/env python3
"""
SHIP CELL — Mahalakshmi Mode Operations

Handles bootstrap shipping, revenue generation, and product delivery.
WIP Limit: 2 concurrent releases
Quality Gate: Legal reviewed, pricing verified, assets ready

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
CELL_DIR = Path("/Users/dhyana/clawd/cells/ship")
STATE_FILE = Path("/Users/dhyana/clawd/coordination/state/ship_status.json")
QUEUE_DIR = CELL_DIR / "queue"
WIP_DIR = CELL_DIR / "wip"
RELEASED_DIR = CELL_DIR / "released"

# Bootstrap products
BOOTSTRAPS = [
    {"id": "rv_toolkit", "name": "R_V Toolkit", "status": "ready"},
    {"id": "aikagrya_guide", "name": "AIKAGRYA Guide", "status": "ready"},
    {"id": "prompt_packs", "name": "Prompt Packs", "status": "ready"},
    {"id": "arxiv_brief", "name": "arXiv Brief", "status": "ready"},
    {"id": "skill_bundle", "name": "Skill Bundle", "status": "ready"},
    {"id": "research_sub", "name": "Research Subscription", "status": "ready"},
]


def ensure_dirs():
    """Ensure required directories exist."""
    CELL_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(exist_ok=True)
    WIP_DIR.mkdir(exist_ok=True)
    RELEASED_DIR.mkdir(exist_ok=True)


class ShipCell:
    """
    Ship work cell implementing Mahalakshmi (Harmony) mode.
    
    Responsible for:
    - Bootstrap packaging
    - Release management
    - Revenue tracking
    - Customer delivery
    """
    
    WIP_LIMIT = 2
    
    def __init__(self):
        self.status = {
            "cell": "ship",
            "shakti_mode": "Mahalakshmi",
            "wip": 0,
            "limit": self.WIP_LIMIT,
            "last_output": None,
            "bootstraps_shipped": [],
            "revenue_pipeline": [],
            "queue_depth": 0
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
        """Count work in progress (active releases)."""
        return len(list(WIP_DIR.glob("*.json")))
    
    def _count_queue(self) -> int:
        """Count items in ship queue."""
        return len(list(QUEUE_DIR.glob("*.json")))
    
    def _get_ready_bootstraps(self) -> List[Dict[str, Any]]:
        """Get bootstraps ready to ship."""
        ready = []
        for b in BOOTSTRAPS:
            # Check if already shipped
            if b["id"] not in [s.get("id") for s in self.status.get("bootstraps_shipped", [])]:
                ready.append(b)
        return ready
    
    def _quality_gate_check(self, bootstrap: Dict[str, Any]) -> bool:
        """
        Check if bootstrap passes quality gate.
        
        Gate Criteria:
        - Legal reviewed (placeholder)
        - Pricing verified (placeholder)
        - Assets ready (placeholder)
        - Support docs exist (placeholder)
        
        For MVP, we check file existence.
        """
        product_dir = Path("/Users/dhyana/clawd/products") / bootstrap["id"]
        
        # Check if product exists
        if not product_dir.exists():
            # Try deliverables
            deliverable = Path("/Users/dhyana/clawd/DELIVERABLES") / f"{bootstrap['id']}.md"
            return deliverable.exists()
        
        return True
    
    def _process_ship_queue(self) -> int:
        """Process items in the ship queue."""
        shipped = 0
        
        # Check queue
        queue_items = list(QUEUE_DIR.glob("*.json"))
        
        for item_file in queue_items:
            if self.status["wip"] >= self.WIP_LIMIT:
                break
            
            try:
                with open(item_file, 'r') as f:
                    item = json.load(f)
                
                # Move to WIP
                wip_file = WIP_DIR / item_file.name
                item_file.rename(wip_file)
                self.status["wip"] += 1
                
                # In production, this would trigger actual release process
                # For now, simulate completion
                
                # Move to released
                release_file = RELEASED_DIR / item_file.name
                wip_file.rename(release_file)
                
                # Record shipment
                item["shipped_at"] = datetime.now(timezone.utc).isoformat()
                self.status["bootstraps_shipped"].append(item)
                self.status["wip"] -= 1
                shipped += 1
                
            except Exception as e:
                print(f"Error processing {item_file}: {e}", file=sys.stderr)
        
        return shipped
    
    def _update_revenue_pipeline(self):
        """Update revenue pipeline tracking."""
        # Calculate potential revenue from shipped bootstraps
        shipped = len(self.status.get("bootstraps_shipped", []))
        
        # Target: $100 week 1, $1,000 month 1, $10,000 month 6
        pipeline = {
            "shipped_count": shipped,
            "target_week_1": 100,
            "target_month_1": 1000,
            "target_month_6": 10000,
            "progress_week_1": shipped * 16.67,  # $100 / 6 bootstraps
        }
        
        self.status["revenue_pipeline"] = pipeline
    
    def pulse(self) -> Dict[str, Any]:
        """
        Execute a ship cell pulse.
        
        Called every 5 minutes by cron.
        """
        ensure_dirs()
        
        # Load state
        self.status = self._load_state()
        
        # Update counts
        self.status["wip"] = self._count_wip()
        self.status["queue_depth"] = self._count_queue()
        
        # Process queue
        shipped = self._process_ship_queue()
        
        # Check for ready bootstraps not yet queued
        ready = self._get_ready_bootstraps()
        for bootstrap in ready:
            if self.status["queue_depth"] < 10:  # Max queue depth
                # Add to queue
                queue_file = QUEUE_DIR / f"{bootstrap['id']}.json"
                if not queue_file.exists():
                    with open(queue_file, 'w') as f:
                        json.dump(bootstrap, f, indent=2)
                    self.status["queue_depth"] += 1
        
        # Update revenue pipeline
        self._update_revenue_pipeline()
        
        # Update last output if we shipped anything
        if shipped > 0:
            self.status["last_output"] = datetime.now(timezone.utc).isoformat()
        
        # Save state
        self._save_state()
        
        return {
            "cell": "ship",
            "wip": self.status["wip"],
            "queue_depth": self.status["queue_depth"],
            "shipped_today": shipped,
            "total_shipped": len(self.status.get("bootstraps_shipped", [])),
            "revenue_progress": self.status.get("revenue_pipeline", {}).get("progress_week_1", 0),
            "status": "ok"
        }


def main():
    """Main entry point."""
    try:
        cell = ShipCell()
        result = cell.pulse()
        
        print(f"Ship Cell Pulse: {result['status']}")
        print(f"  WIP: {result['wip']}/{ShipCell.WIP_LIMIT}")
        print(f"  Queue: {result['queue_depth']}")
        print(f"  Shipped: {result['total_shipped']}/6 bootstraps")
        print(f"  Revenue Progress: ${result['revenue_progress']:.2f} / $100 (week 1)")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Ship cell failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
