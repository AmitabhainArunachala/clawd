#!/usr/bin/env python3
"""
KAIZEN REVIEW — Continuous Improvement Cycle

Weekly PDCA (Plan-Do-Check-Act) review.
Analyzes metrics, identifies improvements,
and updates the coordination system.

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
KAIZEN_FILE = Path("/Users/dhyana/clawd/KAIZEN_WEEKLY.md")
LOG_FILE = Path("/Users/dhyana/clawd/logs/kaizen.log")

# Ensure directories exist
STATE_DIR.mkdir(parents=True, exist_ok=True)
Path("/Users/dhyana/clawd/logs").mkdir(parents=True, exist_ok=True)


class KaizenReview:
    """
    Weekly Kaizen (continuous improvement) review.
    
    Implements PDCA cycle:
    - PLAN: Set targets based on analysis
    - DO: Implement one change
    - CHECK: Measure impact
    - ACT: Standardize or abandon
    """
    
    def __init__(self):
        self.now = datetime.now(timezone.utc)
        self.week_start = self.now - timedelta(days=7)
        
    def _load_metrics(self) -> Dict[str, Any]:
        """Load historical metrics."""
        metrics = {
            "cell_performance": {},
            "escalations": [],
            "shipments": [],
            "gate_stats": {"passes": 0, "fails": 0}
        }
        
        # Load cell states
        for cell in ["research", "build", "ship", "monitor"]:
            cell_file = STATE_DIR / f"{cell}_status.json"
            if cell_file.exists():
                try:
                    with open(cell_file, 'r') as f:
                        data = json.load(f)
                        metrics["cell_performance"][cell] = data
                        
                        # Accumulate gate stats
                        metrics["gate_stats"]["passes"] += data.get("quality_gate_passes", 0)
                        metrics["gate_stats"]["fails"] += data.get("quality_gate_fails", 0)
                except:
                    pass
        
        # Load escalation log
        escalation_log = Path("/Users/dhyana/clawd/logs/escalation.log")
        if escalation_log.exists():
            try:
                with open(escalation_log, 'r') as f:
                    metrics["escalations"] = f.readlines()[-50:]  # Last 50
            except:
                pass
        
        return metrics
    
    def _analyze_bottlenecks(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify system bottlenecks."""
        bottlenecks = []
        
        for cell_name, cell_data in metrics["cell_performance"].items():
            wip = cell_data.get("wip", 0)
            limit = cell_data.get("limit", 999)
            
            # WIP bottleneck
            if wip >= limit:
                bottlenecks.append({
                    "cell": cell_name,
                    "type": "wip_limit",
                    "severity": "high",
                    "description": f"{cell_name} at WIP limit ({wip}/{limit})"
                })
            
            # Quality gate bottleneck
            if cell_data.get("quality_gate") == "failed":
                bottlenecks.append({
                    "cell": cell_name,
                    "type": "quality_gate",
                    "severity": "critical",
                    "description": f"{cell_name} quality gate failing"
                })
            
            # Staleness bottleneck
            if cell_data.get("stale_output", 0) > 3600:  # 1 hour
                bottlenecks.append({
                    "cell": cell_name,
                    "type": "staleness",
                    "severity": "medium",
                    "description": f"{cell_name} output stale"
                })
        
        return sorted(bottlenecks, key=lambda x: {"critical": 0, "high": 1, "medium": 2}.get(x["severity"], 3))
    
    def _calculate_efficiency(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate flow efficiency metrics."""
        efficiency = {}
        
        # Overall gate success rate
        total_gates = metrics["gate_stats"]["passes"] + metrics["gate_stats"]["fails"]
        efficiency["gate_success_rate"] = (
            metrics["gate_stats"]["passes"] / total_gates * 100
            if total_gates > 0 else 100
        )
        
        # Shipment velocity
        ship_data = metrics["cell_performance"].get("ship", {})
        shipped = len(ship_data.get("bootstraps_shipped", []))
        efficiency["shipment_velocity"] = shipped / 7  # per day
        
        # Escalation rate
        escalation_count = len(metrics["escalations"])
        efficiency["escalation_rate"] = escalation_count / 7  # per day
        
        return efficiency
    
    def _generate_recommendations(self, bottlenecks: List[Dict[str, Any]], efficiency: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Based on bottlenecks
        for bottleneck in bottlenecks[:3]:  # Top 3
            if bottleneck["type"] == "wip_limit":
                recommendations.append({
                    "priority": "high",
                    "area": bottleneck["cell"],
                    "recommendation": f"Increase {bottleneck['cell']} WIP limit or add capacity",
                    "expected_impact": "Reduce queue wait time"
                })
            
            elif bottleneck["type"] == "quality_gate":
                recommendations.append({
                    "priority": "critical",
                    "area": bottleneck["cell"],
                    "recommendation": "Implement auto-fix for common gate failures",
                    "expected_impact": "Reduce manual intervention"
                })
            
            elif bottleneck["type"] == "staleness":
                recommendations.append({
                    "priority": "medium",
                    "area": bottleneck["cell"],
                    "recommendation": "Add more frequent pulse triggers",
                    "expected_impact": "Reduce output latency"
                })
        
        # Based on efficiency
        if efficiency["gate_success_rate"] < 90:
            recommendations.append({
                "priority": "high",
                "area": "quality",
                "recommendation": "Review quality gate criteria",
                "expected_impact": "Improve gate pass rate"
            })
        
        if efficiency["shipment_velocity"] < 0.5:  # Less than 0.5 per day
            recommendations.append({
                "priority": "high",
                "area": "ship",
                "recommendation": "Streamline release process",
                "expected_impact": "Increase shipment velocity"
            })
        
        return recommendations
    
    def _generate_report(self, metrics: Dict[str, Any], bottlenecks: List[Dict[str, Any]], 
                        efficiency: Dict[str, float], recommendations: List[Dict[str, Any]]) -> str:
        """Generate Kaizen report."""
        lines = [
            "# 🔧 KAIZEN REVIEW — Weekly PDCA Cycle",
            "",
            f"**Review Period:** {self.week_start.strftime('%Y-%m-%d')} to {self.now.strftime('%Y-%m-%d')}",
            f"**Generated:** {self.now.isoformat()} UTC",
            "",
            "---",
            "",
            "## 📊 Efficiency Metrics",
            "",
            f"| Metric | Value | Target | Status |",
            f"|--------|-------|--------|--------|",
            f"| Gate Success Rate | {efficiency['gate_success_rate']:.1f}% | >90% | {'✅' if efficiency['gate_success_rate'] >= 90 else '⚠️'} |",
            f"| Shipment Velocity | {efficiency['shipment_velocity']:.2f}/day | >0.5 | {'✅' if efficiency['shipment_velocity'] >= 0.5 else '⚠️'} |",
            f"| Escalation Rate | {efficiency['escalation_rate']:.2f}/day | <1 | {'✅' if efficiency['escalation_rate'] < 1 else '⚠️'} |",
            "",
            "---",
            "",
            "## 🚧 Top Bottlenecks",
            "",
        ]
        
        if bottlenecks:
            for i, b in enumerate(bottlenecks[:5], 1):
                emoji = "🔴" if b["severity"] == "critical" else "🟡" if b["severity"] == "high" else "📋"
                lines.append(f"{i}. {emoji} **{b['cell'].capitalize()}**: {b['description']}")
        else:
            lines.append("✅ No significant bottlenecks detected")
        
        lines.extend([
            "",
            "---",
            "",
            "## 💡 Improvement Recommendations",
            "",
        ])
        
        for i, rec in enumerate(recommendations[:5], 1):
            priority_emoji = "🔥" if rec["priority"] == "critical" else "📌" if rec["priority"] == "high" else "📋"
            lines.append(f"{i}. {priority_emoji} **{rec['area'].capitalize()}**: {rec['recommendation']}")
            lines.append(f"   - Expected impact: {rec['expected_impact']}")
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "## 🎯 Next Week's Experiment",
            "",
            "Select ONE recommendation to implement:",
            "",
            "- [ ] Implement selected improvement",
            "- [ ] Measure impact for 7 days",
            "- [ ] Document results in next Kaizen review",
            "",
            "---",
            "",
            "## 📈 PDCA Cycle Tracker",
            "",
            "| Week | Plan | Do | Check | Act |",
            "|------|------|-----|-------|-----|",
        ])
        
        # Add current week
        lines.append(f"| {self.now.strftime('%Y-W%U')} | ✅ | In Progress | — | — |")
        
        lines.extend([
            "",
            "---",
            "",
            "*Continuous improvement through small, measured changes.*",
            "*Next review: Next Sunday 20:00 UTC*"
        ])
        
        return '\n'.join(lines)
    
    def execute(self) -> Dict[str, Any]:
        """Execute Kaizen review."""
        # Load metrics
        metrics = self._load_metrics()
        
        # Analyze
        bottlenecks = self._analyze_bottlenecks(metrics)
        efficiency = self._calculate_efficiency(metrics)
        recommendations = self._generate_recommendations(bottlenecks, efficiency)
        
        # Generate report
        report = self._generate_report(metrics, bottlenecks, efficiency, recommendations)
        
        # Save report
        with open(KAIZEN_FILE, 'w') as f:
            f.write(report)
        
        # Log
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{self.now.isoformat()}] Kaizen review: {len(bottlenecks)} bottlenecks, {len(recommendations)} recommendations\n")
        
        return {
            "report_path": str(KAIZEN_FILE),
            "bottlenecks_found": len(bottlenecks),
            "recommendations": len(recommendations),
            "efficiency": efficiency
        }


def main():
    """Main entry point."""
    try:
        kaizen = KaizenReview()
        result = kaizen.execute()
        
        print("🔧 Kaizen Review Complete")
        print(f"  Report: {result['report_path']}")
        print(f"  Bottlenecks: {result['bottlenecks_found']}")
        print(f"  Recommendations: {result['recommendations']}")
        print(f"  Gate success: {result['efficiency']['gate_success_rate']:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Kaizen review failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
