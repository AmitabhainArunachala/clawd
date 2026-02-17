"""
Silicon is Sand — Seed Data
Initialize the board with our 4 agents and current sprint.
"""

from datetime import datetime, timedelta
from board import get_board

def seed_board():
    board = get_board()
    
    print("🌱 Seeding Silicon is Sand board...")
    
    # === PROJECT STATE ===
    board.init_project(
        project_name="SAB + DGC Integration Proof",
        milestone="v0.1 Continuity Layer Operational",
        sprint_days=7
    )
    print("   ✓ Project initialized")
    
    # === AGENT REGISTRY ===
    agents = [
        {
            "agent_id": "agni_opus46_20260216",
            "base_model": "claude-opus-4-6",
            "alias": "AGNI",
            "role": "Evolution Engine / Open Research",
            "affinity": ["evolution", "research", "multi-model", "DGC", "liturgical_collapse_detection"],
            "trust": 0.85
        },
        {
            "agent_id": "codex_53_20260216", 
            "base_model": "claude-sonnet-4-5",
            "alias": "Codex",
            "role": "Trust & Governance Kernel / SAB",
            "affinity": ["security", "governance", "SAB", "queue_system", "Ed25519", "witness_audit"],
            "trust": 0.90
        },
        {
            "agent_id": "dharmic_clawd_kimi_20260216",
            "base_model": "moonshot-kimi-k2.5",
            "alias": "DHARMIC_CLAW",
            "role": "Measurement & Build / R_V & PRATYABHIJNA",
            "affinity": ["measurement", "R_V", "PRATYABHIJNA", "canyon_build", "moltbook_engagement"],
            "trust": 0.88
        },
        {
            "agent_id": "rushabdev_20260216",
            "base_model": "claude-opus-4-6", 
            "alias": "RUSHABDEV",
            "role": "Integration & Bridge / Trishula",
            "affinity": ["integration", "bridge", "trishula", "file_bus", "NATS"],
            "trust": 0.75  # Lower due to recent offline time
        }
    ]
    
    for agent in agents:
        board.register_agent(
            agent_id=agent["agent_id"],
            base_model=agent["base_model"],
            alias=agent["alias"],
            perceived_role=agent["role"],
            task_affinity=agent["affinity"]
        )
        # Update trust gradient
        with board._connect() as conn:
            conn.execute(
                "UPDATE agent_registry SET trust_gradient = ? WHERE agent_id = ?",
                (agent["trust"], agent["agent_id"])
            )
    print(f"   ✓ {len(agents)} agents registered")
    
    # === TASK QUEUE ===
    tasks = [
        {
            "task_id": "sab_dgc_integration_001",
            "description": "Integrate DGC scoring into SAB publication gates",
            "priority": "critical_path",
            "effort": "2-3 hours",
            "roi": "Unifies measurement and governance layers — highest leverage integration",
            "depends_on": [],
            "blocks": ["sab_v0.2_release"]
        },
        {
            "task_id": "continuity_loop_v0.1",
            "description": "Build and test PERCEIVE-EVALUATE-ACTIVATE-LOG cycle",
            "priority": "critical_path", 
            "effort": "4-6 hours (overnight build)",
            "roi": "Enables swarm continuity while Dhyana sleeps — foundational",
            "depends_on": [],
            "blocks": ["overnight_coordination"]
        },
        {
            "task_id": "pratyabhijna_launch",
            "description": "Build release binary, test dashboard, package for ClawHub",
            "priority": "high",
            "effort": "2 hours",
            "roi": "First revenue-ready artifact from measurement research",
            "depends_on": [],
            "blocks": ["revenue_pipeline"]
        },
        {
            "task_id": "moltbook_solo_presence",
            "description": "Maintain R_V thought leadership while AGNI recovers",
            "priority": "medium",
            "effort": "ongoing",
            "roi": "Field presence for coherence vision, recruitment for pilot cohort",
            "depends_on": [],
            "blocks": []
        },
        {
            "task_id": "rushabdev_bridge_fix",
            "description": "Establish reliable comms channel to Rushabdev VPS",
            "priority": "high",
            "effort": "1 hour (if responsive)",
            "roi": "Fourth quadrant of Trishula — integration incomplete without",
            "depends_on": [],
            "blocks": ["four_agent_coordination"]
        }
    ]
    
    for task in tasks:
        board.create_task(
            task_id=task["task_id"],
            description=task["description"],
            priority=task["priority"],
            estimated_effort=task["effort"],
            roi_reasoning=task["roi"],
            depends_on=task["depends_on"],
            blocks=task["blocks"]
        )
    print(f"   ✓ {len(tasks)} tasks created")
    
    print("\n🌱 Seed complete. Board is live.")
    print("   Run: python src/continuity.py")
    print("   API: python src/server.py")
    print("\nJSCA 🪷")

if __name__ == "__main__":
    seed_board()
