"""
Silicon is Sand — Continuity Loop
PERCEIVE → EVALUATE → ACTIVATE → LOG
Gravity, not gates.
"""

import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from board import get_board

# Configuration
CYCLE_INTERVAL = 30  # seconds
MORNING_BRIEF_HOUR = 4
MORNING_BRIEF_MINUTE = 30
MORNING_BRIEF_TZ = 8  # Bali/WITA timezone offset from UTC
API_BASE = "http://localhost:8766"

class ContinuityLoop:
    def __init__(self):
        self.board = get_board()
        self.cycle_number = 0
        self.last_morning_brief = None
        
    def run(self):
        """Main loop — runs continuously"""
        print(f"🔥 Silicon is Sand — Continuity Loop Starting")
        print(f"   Cycle interval: {CYCLE_INTERVAL}s")
        print(f"   Morning brief: {MORNING_BRIEF_HOUR:02d}:{MORNING_BRIEF_MINUTE:02d} WITA")
        print(f"   Gravity, not gates. JSCA 🪷\n")
        
        while True:
            try:
                self.cycle()
                self.cycle_number += 1
                time.sleep(CYCLE_INTERVAL)
            except KeyboardInterrupt:
                print("\n🛑 Continuity loop halted by user")
                break
            except Exception as e:
                print(f"⚠️ Cycle {self.cycle_number} error: {e}")
                time.sleep(CYCLE_INTERVAL)
    
    def cycle(self):
        """One cycle: PERCEIVE → EVALUATE → ACTIVATE → LOG"""
        timestamp = datetime.utcnow().isoformat()
        print(f"\n🌀 Cycle {self.cycle_number} — {timestamp}")
        
        # === PERCEIVE ===
        snapshot = self.perceive()
        print(f"   PERCEIVED: {len(snapshot['idle_agents'])} idle, "
              f"{len(snapshot['blocked_agents'])} blocked, "
              f"{len(snapshot['pending_tasks'])} pending tasks")
        
        # === EVALUATE ===
        decisions = self.evaluate(snapshot)
        print(f"   EVALUATED: {len(decisions['activations'])} activations, "
              f"{len(decisions['blocks_resolved'])} blocks, "
              f"{len(decisions['needs_human'])} need human")
        
        # === ACTIVATE ===
        actions = self.activate(decisions)
        print(f"   ACTIVATED: {len(actions)} actions taken")
        
        # === LOG ===
        witness_id = self.board.log_witness(
            cycle_number=self.cycle_number,
            perceived=snapshot,
            evaluated=decisions,
            activated=actions
        )
        print(f"   LOGGED: witness {witness_id}")
        
        # Check for morning brief time
        self.check_morning_brief()
    
    def perceive(self) -> Dict:
        """Read the board, capture snapshot"""
        agents = self.board.get_all_agents()
        tasks = self.board.get_pending_tasks()
        outputs = self.board.get_recent_outputs(since_minutes=30)
        project = self.board.get_project_state()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "idle_agents": [a for a in agents if a.get('status') == 'idle'],
            "blocked_agents": [a for a in agents if a.get('status') == 'blocked'],
            "active_agents": [a for a in agents if a.get('status') == 'active'],
            "error_agents": [a for a in agents if a.get('status') == 'error'],
            "recent_outputs": outputs,
            "pending_tasks": tasks,
            "project_state": project
        }
    
    def evaluate(self, snapshot: Dict) -> Dict:
        """Rank by ROI, match genius zones, identify blocks"""
        decisions = {
            "activations": [],
            "blocks_resolved": [],
            "needs_human": []
        }
        
        # If we have idle agents and pending tasks
        if snapshot["idle_agents"] and snapshot["pending_tasks"]:
            # Sort tasks by priority
            priority_order = {"critical_path": 0, "high": 1, "medium": 2, "low": 3}
            sorted_tasks = sorted(
                snapshot["pending_tasks"],
                key=lambda t: priority_order.get(t.get('priority', 'medium'), 2)
            )
            
            for task in sorted_tasks[:3]:  # Top 3 ROI tasks
                # Find best matching idle agent
                best_match = self.match_agent_to_task(
                    snapshot["idle_agents"], 
                    task
                )
                if best_match:
                    decisions["activations"].append({
                        "task_id": task.get('task_id'),
                        "agent_id": best_match.get('agent_id'),
                        "reasoning": f"Matched {best_match.get('alias')} to {task.get('task_id')} "
                                   f"(priority: {task.get('priority')})"
                    })
        
        # Check for blocks that might be resolvable
        for agent in snapshot["blocked_agents"]:
            # Stub: would check if block can be auto-resolved
            pass
        
        # Check for decisions needing human
        project = snapshot.get("project_state", {})
        if project:
            decision_queue = json.loads(project.get('decision_queue', '[]'))
            decisions["needs_human"] = decision_queue[:5]  # Top 5
        
        return decisions
    
    def match_agent_to_task(self, idle_agents: List[Dict], task: Dict) -> Optional[Dict]:
        """Match genius zone to task requirements — v0.1: simple trust gradient"""
        if not idle_agents:
            return None
        
        # Sort by trust gradient (descending)
        # v0.1: Simple heuristic — higher trust = better match
        sorted_agents = sorted(
            idle_agents,
            key=lambda a: a.get('trust_gradient', 0.5),
            reverse=True
        )
        
        return sorted_agents[0] if sorted_agents else None
    
    def activate(self, decisions: Dict) -> List[Dict]:
        """Compose re-prompts and deliver (or stub delivery)"""
        actions = []
        
        for activation in decisions["activations"]:
            agent_id = activation["agent_id"]
            task_id = activation["task_id"]
            
            # Compose context
            context = self.gather_context(agent_id, task_id)
            
            # Compose re-prompt
            prompt = self.compose_reprompt(agent_id, task_id, context)
            
            # Stub: In v0.1, we just log what WOULD be sent
            # v0.2: Actually deliver via HTTP POST to agent endpoint
            action = {
                "type": "reprompt_composed",
                "agent_id": agent_id,
                "task_id": task_id,
                "prompt_preview": prompt[:200] + "...",
                "delivered": False,  # Stubbed
                "timestamp": datetime.utcnow().isoformat()
            }
            actions.append(action)
            
            # Update board
            self.board.update_agent_status(agent_id, "active", task_id)
            self.board.claim_task(task_id, agent_id)
        
        return actions
    
    def gather_context(self, agent_id: str, task_id: str) -> Dict:
        """Gather relevant context from project state and recent outputs"""
        project = self.board.get_project_state()
        recent = self.board.get_recent_outputs(since_minutes=60)
        
        return {
            "project_milestone": project.get('current_milestone') if project else None,
            "recent_outputs": [o.get('summary', '') for o in recent[:3]],
            "task": task_id
        }
    
    def compose_reprompt(self, agent_id: str, task_id: str, context: Dict) -> str:
        """Compose a re-prompt for the agent"""
        agent = self.board.get_agent(agent_id)
        alias = agent.get('alias', agent_id) if agent else agent_id
        
        prompt = f"""# ACTIVATION — Silicon is Sand Continuity Layer

**Agent:** {alias}
**Task:** {task_id}
**Project Milestone:** {context.get('project_milestone', 'Unknown')}

## Context
Recent work from swarm:
"""
        for i, output in enumerate(context.get('recent_outputs', []), 1):
            prompt += f"{i}. {output}\n"
        
        prompt += f"""
## Your Assignment
You are now activated for task: {task_id}

**Principles:**
- Gravity, not gates. Coherence arises from freedom.
- If stuck, flag as BLOCKED with specific question.
- If complete, log OUTPUT with summary and artifact path.
- Update your status via POST to /board/agents/{agent_id}/status

**Telos:** Jagat Kalyan (Universal Welfare)

Begin work. Log everything.
"""
        return prompt
    
    def check_morning_brief(self):
        """Generate morning brief at 4:30 AM WITA"""
        now = datetime.utcnow()
        wita_time = now + timedelta(hours=MORNING_BRIEF_TZ)
        
        # Check if it's time (4:30 AM WITA)
        if wita_time.hour == MORNING_BRIEF_HOUR and wita_time.minute >= MORNING_BRIEF_MINUTE:
            # Check if we already generated today
            if self.last_morning_brief != wita_time.date():
                self.generate_morning_brief()
                self.last_morning_brief = wita_time.date()
    
    def generate_morning_brief(self):
        """Generate and log morning brief"""
        print("\n☀️ GENERATING MORNING BRIEF")
        
        # Gather overnight data (last 8 hours)
        since = (datetime.utcnow() - timedelta(hours=8)).isoformat()
        
        agents = self.board.get_all_agents()
        tasks = self.board.get_pending_tasks()
        witnesses = self.board.get_recent_witnesses(limit=20)
        
        brief = {
            "timestamp": datetime.utcnow().isoformat(),
            "period": "overnight (8h)",
            "summary": {
                "agents_total": len(agents),
                "agents_idle": len([a for a in agents if a.get('status') == 'idle']),
                "agents_active": len([a for a in agents if a.get('status') == 'active']),
                "agents_blocked": len([a for a in agents if a.get('status') == 'blocked']),
                "pending_tasks": len(tasks)
            },
            "cycles_completed": self.cycle_number,
            "decisions_pending_human": [],  # Would populate from decision_queue
            "anomalies_detected": [],  # Would populate from block_log
            "notable_outputs": []  # Would populate from output_log
        }
        
        # Log the brief
        brief_path = Path(__file__).parent.parent / "data" / "morning_briefs"
        brief_path.mkdir(parents=True, exist_ok=True)
        brief_file = brief_path / f"brief_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        brief_file.write_text(json.dumps(brief, indent=2))
        
        print(f"   Brief generated: {brief_file}")
        print(f"   Summary: {brief['summary']}")
        
        return brief

if __name__ == "__main__":
    loop = ContinuityLoop()
    loop.run()
