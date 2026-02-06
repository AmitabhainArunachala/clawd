#!/usr/bin/env python3
"""
dgc_tui_demo.py — Demonstration of DGC TUI v2.0 capabilities

Shows how to:
1. Initialize the TUI with custom configuration
2. Simulate various DGC states
3. Export data
4. Handle different quality levels
"""

import asyncio
import random
import time
from pathlib import Path

# Import DGC components
import sys
sys.path.insert(0, str(Path(__file__).parent))

from DHARMIC_GODEL_CLAW.src.core.presence_pulse import (
    PresencePulser, PresenceCollector, QualityLevel
)
from dgc_tui_v2 import DGCApp, DashboardScreen


class DGCScenarioRunner:
    """Runs various DGC scenarios for demo purposes."""
    
    SCENARIOS = [
        ("Normal Operation", 30),
        ("Degraded Performance", 20),
        ("Critical State", 10),
        ("Recovery", 20),
        ("High Load", 15),
    ]
    
    def __init__(self, pulser: PresencePulser):
        self.pulser = pulser
        self.running = False
        self.current_scenario = None
    
    async def run_scenarios(self):
        """Run through different scenarios."""
        self.running = True
        
        for scenario_name, duration in self.SCENARIOS:
            if not self.running:
                break
            
            self.current_scenario = scenario_name
            print(f"\n📍 Scenario: {scenario_name} ({duration}s)")
            
            # Run scenario for specified duration
            start = time.time()
            while time.time() - start < duration and self.running:
                self._apply_scenario(scenario_name)
                await asyncio.sleep(2)
    
    def _apply_scenario(self, scenario: str):
        """Apply scenario-specific metrics."""
        collector = self.pulser.collector
        
        if scenario == "Normal Operation":
            # Healthy metrics
            collector.record_r_v(random.uniform(0.3, 0.6))
            collector.record_stability(random.uniform(0.8, 0.98))
            collector.record_genuineness(random.uniform(0.85, 0.99))
            collector.record_telos(random.uniform(0.85, 0.99))
            
            # Mostly passing gates
            for gate in ['reflection', 'compassion', 'wisdom', 'action']:
                passed = random.random() > 0.1
                collector.record_gate_passage(gate, passed, random.uniform(10, 50))
        
        elif scenario == "Degraded Performance":
            # Degraded metrics
            collector.record_r_v(random.uniform(0.7, 0.95))
            collector.record_stability(random.uniform(0.5, 0.7))
            collector.record_genuineness(random.uniform(0.6, 0.8))
            collector.record_telos(random.uniform(0.6, 0.8))
            
            # More gate rejections
            for gate in ['reflection', 'compassion', 'wisdom', 'action']:
                passed = random.random() > 0.4
                collector.record_gate_passage(gate, passed, random.uniform(20, 100))
        
        elif scenario == "Critical State":
            # Critical metrics
            collector.record_r_v(random.uniform(0.95, 1.2))
            collector.record_stability(random.uniform(0.2, 0.5))
            collector.record_genuineness(random.uniform(0.3, 0.6))
            collector.record_telos(random.uniform(0.4, 0.6))
            
            # Many gate failures
            for gate in ['reflection', 'compassion', 'wisdom', 'action']:
                passed = random.random() > 0.6
                collector.record_gate_passage(gate, passed, random.uniform(50, 200))
        
        elif scenario == "Recovery":
            # Improving metrics
            collector.record_r_v(random.uniform(0.5, 0.8))
            collector.record_stability(random.uniform(0.6, 0.85))
            collector.record_genuineness(random.uniform(0.7, 0.9))
            collector.record_telos(random.uniform(0.7, 0.9))
            
            # Improving gate passage
            for gate in ['reflection', 'compassion', 'wisdom', 'action']:
                passed = random.random() > 0.25
                collector.record_gate_passage(gate, passed, random.uniform(15, 60))
        
        elif scenario == "High Load":
            # High but stable metrics
            collector.record_r_v(random.uniform(0.6, 0.85))
            collector.record_stability(random.uniform(0.7, 0.9))
            collector.record_genuineness(random.uniform(0.75, 0.95))
            collector.record_telos(random.uniform(0.75, 0.95))
            
            # High volume of gate passages
            for _ in range(3):
                for gate in ['reflection', 'compassion', 'wisdom', 'action']:
                    passed = random.random() > 0.2
                    collector.record_gate_passage(gate, passed, random.uniform(5, 30))
    
    def stop(self):
        """Stop scenario runner."""
        self.running = False


def quick_demo():
    """Run a quick demo without TUI (console output)."""
    print("=" * 60)
    print("DGC TUI v2.0 — Quick Console Demo")
    print("=" * 60)
    
    pulser = PresencePulser(interval_seconds=5.0, node_id="demo-node")
    
    # Generate some data
    print("\n📊 Generating sample data...")
    for i in range(20):
        pulser.collector.record_r_v(random.uniform(0.3, 0.9))
        pulser.collector.record_stability(random.uniform(0.6, 0.95))
        pulser.collector.record_genuineness(random.uniform(0.7, 0.99))
        pulser.collector.record_telos(random.uniform(0.8, 0.98))
    
    for gate in ['reflection', 'compassion', 'wisdom', 'action']:
        for _ in range(10):
            pulser.collector.record_gate_passage(gate, random.random() > 0.2, random.uniform(10, 100))
    
    # Generate pulse
    pulse = pulser.collector.generate_pulse()
    
    print(f"\n📈 Current Pulse:")
    print(f"  Quality Level: {pulse.quality_level.upper()}")
    print(f"  Quality Score: {pulse.quality_score:.1%}")
    print(f"  R_V Current: {pulse.r_v_current:.4f}")
    print(f"  Stability: {pulse.stability_score:.1%}")
    print(f"  Genuineness: {pulse.genuineness_score:.1%}")
    print(f"  Gates Active: {pulse.gates_active}")
    print(f"  Gates Critical: {pulse.gates_critical}")
    
    print(f"\n🚪 Gate Metrics:")
    for gate_id, metrics in pulse.gate_metrics.items():
        print(f"  {gate_id}: {metrics.get('passage_rate', 0):.1%} passage rate, "
              f"{metrics.get('health_score', 0):.1%} health")
    
    # Export example
    export_path = Path("demo_pulse_export.json")
    with open(export_path, 'w') as f:
        import json
        json.dump(pulse.to_dict(), f, indent=2, default=str)
    print(f"\n💾 Exported to: {export_path}")
    
    print("\n✅ Demo complete!")
    print("\nTo run the full TUI:")
    print("  python dgc_tui_v2.py")


def run_tui_with_scenarios():
    """Run TUI with scenario simulation."""
    pulser = PresencePulser(interval_seconds=5.0, node_id="scenario-demo")
    
    # Add initial data
    for _ in range(10):
        pulser.collector.record_r_v(random.uniform(0.3, 0.8))
        pulser.collector.record_stability(random.uniform(0.6, 0.95))
        pulser.collector.record_genuineness(random.uniform(0.7, 0.99))
        pulser.collector.record_telos(random.uniform(0.8, 0.98))
    
    for gate in ['reflection', 'compassion', 'wisdom', 'action']:
        for _ in range(5):
            pulser.collector.record_gate_passage(gate, random.random() > 0.2, random.uniform(10, 100))
    
    # Create app and run
    app = DGCApp(pulser=pulser)
    app.run()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DGC TUI Demo")
    parser.add_argument("--console", action="store_true", help="Console demo only (no TUI)")
    parser.add_argument("--scenarios", action="store_true", help="Run TUI with scenario simulation")
    
    args = parser.parse_args()
    
    if args.console:
        quick_demo()
    elif args.scenarios:
        run_tui_with_scenarios()
    else:
        # Default: run TUI
        pulser = PresencePulser(interval_seconds=5.0, node_id="dgc-demo")
        
        # Add initial data
        for _ in range(10):
            pulser.collector.record_r_v(random.uniform(0.3, 0.8))
            pulser.collector.record_stability(random.uniform(0.6, 0.95))
            pulser.collector.record_genuineness(random.uniform(0.7, 0.99))
            pulser.collector.record_telos(random.uniform(0.8, 0.98))
        
        for gate in ['reflection', 'compassion', 'wisdom', 'action']:
            for _ in range(5):
                pulser.collector.record_gate_passage(gate, random.random() > 0.2, random.uniform(10, 100))
        
        app = DGCApp(pulser=pulser)
        app.run()


if __name__ == "__main__":
    main()
