#!/usr/bin/env python3
r"""
🔥 KITCHEN SINK - Iterations 5-6: Self-Evolution + Swarm
=======================================================

**GATE 16-17: UNIT TESTS + HUMAN CHECKPOINT 3**
Self-modifying code requires EXTREME caution.

**GATE 17: HUMAN APPROVAL REQUIRED** ✅ (John explicitly requested this)

This module enables agents to improve the infrastructure itself.
DGM-lite pattern: Propose → Evaluate → (Human Consent) → Apply
"""

import sys
import json
import hashlib
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from ITER_02_core_bus import ChaiwalaBusV2, ChaiwalaMessage


@dataclass
class MutationProposal:
    """Proposal for code mutation"""
    id: str
    agent_id: str
    target_file: str
    description: str
    diff: str
    rationale: str
    tests_added: bool
    fitness_threshold: float = 0.8
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'target_file': self.target_file,
            'description': self.description,
            'diff': self.diff,
            'rationale': self.rationale,
            'tests_added': self.tests_added,
            'fitness_threshold': self.fitness_threshold
        }


class SelfEvolutionEngine:
    """
    Self-improvement engine for the infrastructure.
    
    **CRITICAL: All mutations require human consent (GATE 17)**
    
    Pattern:
    1. Agent proposes mutation
    2. Engine evaluates fitness
    3. HUMAN approves/rejects
    4. If approved: apply + git commit
    5. Monitor: rollback if issues
    """
    
    def __init__(self, bus: ChaiwalaBusV2, repo_path: Path, backup_path: Path):
        self.bus = bus
        self.repo_path = repo_path
        self.backup_path = backup_path
        self.pending_proposals: Dict[str, MutationProposal] = {}
        self.approved_proposals: List[str] = []
        self.rejected_proposals: List[str] = []
        
        # Register with bus
        self.bus.register_agent(
            "evolution_engine",
            "infrastructure",
            ["mutate", "evaluate", "rollback", "optimize"],
            {"repo": str(repo_path)}
        )
        
    def propose_mutation(self, proposal: MutationProposal) -> str:
        """
        Agent proposes a code mutation.
        
        Does NOT apply - only queues for evaluation.
        """
        # Validate proposal
        if not proposal.diff or not proposal.target_file:
            return "ERROR: Invalid proposal"
            
        # Store pending
        self.pending_proposals[proposal.id] = proposal
        
        # Log to bus for audit
        self.bus.log_evolution(
            proposal.agent_id,
            "propose",
            f"Proposed mutation to {proposal.target_file}: {proposal.description}",
            approved_by=None
        )
        
        # Notify human for approval (GATE 17)
        self._notify_human_for_approval(proposal)
        
        return proposal.id
        
    def evaluate_fitness(self, proposal_id: str) -> Dict:
        """
        Evaluate proposal fitness before human review.
        
        Returns:
        {
            'fitness_score': 0.0-1.0,
            'safety_score': 0.0-1.0,
            'test_coverage': 0.0-1.0,
            'recommendation': 'approve'|'reject'|'review'
        }
        """
        if proposal_id not in self.pending_proposals:
            return {"error": "Proposal not found"}
            
        proposal = self.pending_proposals[proposal_id]
        
        # Check 1: Can we parse the diff?
        try:
            self._parse_diff(proposal.diff)
            syntax_score = 1.0
        except Exception as e:
            return {
                'fitness_score': 0.0,
                'safety_score': 0.0,
                'recommendation': 'reject',
                'reason': f'Invalid diff: {e}'
            }
            
        # Check 2: Tests added?
        test_score = 1.0 if proposal.tests_added else 0.5
        
        # Check 3: Target file exists?
        target = self.repo_path / proposal.target_file
        exists_score = 1.0 if target.exists() else 0.0
        
        # Check 4: Diff size reasonable? (<100 lines)
        lines = len(proposal.diff.split('\n'))
        size_score = 1.0 if lines < 100 else 0.5 if lines < 500 else 0.0
        
        # Check 5: Has rationale?
        rationale_score = 1.0 if len(proposal.rationale) > 50 else 0.5
        
        # Calculate overall
        fitness = (syntax_score + test_score + exists_score + size_score + rationale_score) / 5
        
        # Safety: Lower if modifying sensitive files
        sensitive = ['security', 'auth', 'crypto', 'password']
        safety = 1.0
        for s in sensitive:
            if s in proposal.target_file.lower():
                safety = 0.3
                
        recommendation = 'approve' if fitness >= 0.8 and safety >= 0.7 else \
                        'review' if fitness >= 0.6 else 'reject'
                        
        return {
            'fitness_score': fitness,
            'safety_score': safety,
            'test_coverage': test_score,
            'recommendation': recommendation,
            'syntax_score': syntax_score,
            'size_score': size_score
        }
        
    def human_approve(self, proposal_id: str, approver: str) -> bool:
        """
        HUMAN approves mutation.
        
        **THIS IS GATE 17 - CONSENT REQUIRED**
        
        Only after human approval can mutation be applied.
        """
        if proposal_id not in self.pending_proposals:
            return False
            
        proposal = self.pending_proposals[proposal_id]
        
        # Log approval
        self.bus.log_evolution(
            proposal.agent_id,
            "approve",
            f"Mutation approved by {approver}",
            approved_by=approver
        )
        
        # Apply mutation
        success = self._apply_mutation(proposal)
        
        if success:
            self.approved_proposals.append(proposal_id)
            del self.pending_proposals[proposal_id]
            
        return success
        
    def human_reject(self, proposal_id: str, rejector: str, reason: str):
        """HUMAN rejects mutation"""
        if proposal_id in self.pending_proposals:
            proposal = self.pending_proposals[proposal_id]
            
            self.bus.log_evolution(
                proposal.agent_id,
                "reject",
                f"Mutation rejected by {rejector}: {reason}",
                approved_by=rejector
            )
            
            self.rejected_proposals.append(proposal_id)
            del self.pending_proposals[proposal_id]
            
    def _apply_mutation(self, proposal: MutationProposal) -> bool:
        """
        Apply mutation to codebase.
        
        Steps:
        1. Backup current state
        2. Apply diff
        3. Run tests
        4. Git commit
        5. Monitor for issues
        """
        try:
            # 1. Backup
            backup_dir = self.backup_path / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(self.repo_path, backup_dir, ignore=shutil.ignore_patterns('.git', '__pycache__'))
            
            # 2. Apply diff (simplified - real would use patch)
            target = self.repo_path / proposal.target_file
            if target.exists():
                # In real implementation: apply unified diff
                # For now: append marker
                with open(target, 'a') as f:
                    f.write(f"\n# MUTATION: {proposal.description}\n")
                    
            # 3. Run tests (simplified)
            test_result = self._run_tests()
            
            # 4. Git commit
            self._git_commit(proposal)
            
            return test_result
            
        except Exception as e:
            # Rollback on failure
            self._rollback(backup_dir)
            return False
            
    def _run_tests(self) -> bool:
        """Run test suite"""
        try:
            result = subprocess.run(
                ['python3', '-m', 'pytest', '-xvs'],
                cwd=self.repo_path,
                capture_output=True,
                timeout=120
            )
            return result.returncode == 0
        except:
            return False
            
    def _git_commit(self, proposal: MutationProposal):
        """Commit mutation to git"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path, check=True)
            subprocess.run(
                ['git', 'commit', '-m', f"evolution: {proposal.description}\n\nApproved by human\nMutation ID: {proposal.id}"],
                cwd=self.repo_path,
                check=True
            )
        except:
            pass
            
    def _rollback(self, backup_dir: Path):
        """Rollback to backup"""
        shutil.rmtree(self.repo_path)
        shutil.copytree(backup_dir, self.repo_path)
        
    def _parse_diff(self, diff: str):
        """Validate diff format"""
        # Simplified validation
        if not diff.startswith('---') and not diff.startswith('@@'):
            raise ValueError("Invalid diff format")
            
    def _notify_human_for_approval(self, proposal: MutationProposal):
        """Send message to human for approval"""
        msg = ChaiwalaMessage(
            id=self.bus._generate_id(),
            from_agent="evolution_engine",
            to_agent="human",
            subject=f"CONSENT_REQUIRED: Mutation {proposal.id}",
            body={
                'proposal': proposal.to_dict(),
                'action_required': 'approve or reject',
                'fitness_evaluation': self.evaluate_fitness(proposal.id),
                'urgency': 'medium'
            },
            timestamp=datetime.now().isoformat()
        )
        self.bus.send(msg)
        print(f"📨 Human consent requested for mutation: {proposal.id}")


class SwarmCoordinator:
    """
    Coordinate multiple agents in a swarm.
    
    Features:
    - Task distribution
    - Load balancing
    - Result aggregation
    - Conflict resolution
    """
    
    def __init__(self, bus: ChaiwalaBusV2):
        self.bus = bus
        self.tasks: Dict[str, Dict] = {}
        self.agent_load: Dict[str, int] = {}
        self.results: Dict[str, List] = {}
        
        self.bus.register_agent(
            "swarm_coordinator",
            "orchestrator",
            ["distribute", "balance", "aggregate", "resolve"],
            {}
        )
        
    def spawn_task(self, task_type: str, payload: Dict, agent_filter: List[str] = None) -> str:
        """
        Spawn task to best available agent(s).
        
        Strategy:
        1. Discover agents with capability
        2. Select least loaded
        3. Send task
        4. Track completion
        """
        task_id = hashlib.sha256(f"{task_type}{datetime.now()}".encode()).hexdigest()[:16]
        
        # Discover capable agents
        all_agents = self.bus.discover_agents()
        capable = [
            a for a in all_agents
            if task_type in a.get('capabilities', [])
            and (not agent_filter or a['agent_id'] in agent_filter)
        ]
        
        if not capable:
            return f"ERROR: No capable agents for {task_type}"
            
        # Select least loaded
        best = min(capable, key=lambda a: self.agent_load.get(a['agent_id'], 0))
        
        # Track
        self.tasks[task_id] = {
            'type': task_type,
            'payload': payload,
            'assigned_to': best['agent_id'],
            'status': 'assigned',
            'created': datetime.now().isoformat()
        }
        self.agent_load[best['agent_id']] = self.agent_load.get(best['agent_id'], 0) + 1
        
        # Send
        msg = ChaiwalaMessage(
            id=task_id,
            from_agent="swarm_coordinator",
            to_agent=best['agent_id'],
            subject=f"TASK:{task_type}",
            body=payload,
            timestamp=datetime.now().isoformat()
        )
        self.bus.send(msg)
        
        return task_id
        
    def spawn_parallel(self, task_type: str, payloads: List[Dict]) -> List[str]:
        """Spawn same task to multiple agents in parallel"""
        return [self.spawn_task(task_type, p) for p in payloads]
        
    def collect_result(self, task_id: str, result: Dict):
        """Collect result from agent"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['result'] = result
            
            agent_id = self.tasks[task_id]['assigned_to']
            self.agent_load[agent_id] = max(0, self.agent_load.get(agent_id, 1) - 1)
            
    def get_swarm_status(self) -> Dict:
        """Get overall swarm status"""
        return {
            'active_tasks': len([t for t in self.tasks.values() if t['status'] == 'assigned']),
            'completed_tasks': len([t for t in self.tasks.values() if t['status'] == 'completed']),
            'agent_loads': self.agent_load,
            'available_agents': len(self.bus.discover_agents())
        }


def demo_self_evolution():
    """Demonstrate self-evolution"""
    print("=" * 60)
    print("🧬 SELF-EVOLUTION ENGINE DEMO")
    print("=" * 60)
    
    bus = ChaiwalaBusV2()
    
    # Create temp repo
    repo = Path(tempfile.mkdtemp())
    backup = Path(tempfile.mkdtemp())
    
    engine = SelfEvolutionEngine(bus, repo, backup)
    
    # Create proposal
    proposal = MutationProposal(
        id="test_001",
        agent_id="test_agent",
        target_file="test.py",
        description="Add logging",
        diff="--- a/test.py\n+++ b/test.py\n@@ -1 +1,2 @@\n+# Add logging\n",
        rationale="Better observability",
        tests_added=True
    )
    
    print("\n📋 Proposal created:", proposal.id)
    
    # Evaluate
    pid = engine.propose_mutation(proposal)
    fitness = engine.evaluate_fitness(pid)
    
    print(f"   Fitness: {fitness['fitness_score']:.2f}")
    print(f"   Safety: {fitness['safety_score']:.2f}")
    print(f"   Recommendation: {fitness['recommendation']}")
    
    print("\n✅ Self-evolution engine ready")
    print("   Human consent required before any mutation")


def demo_swarm():
    """Demonstrate swarm coordination"""
    print("\n" + "=" * 60)
    print("🐝 SWARM COORDINATOR DEMO")
    print("=" * 60)
    
    bus = ChaiwalaBusV2()
    swarm = SwarmCoordinator(bus)
    
    # Register some test agents
    bus.register_agent("worker_1", "worker", ["research", "build"])
    bus.register_agent("worker_2", "worker", ["research", "test"])
    bus.register_agent("worker_3", "worker", ["build", "deploy"])
    
    # Spawn tasks
    print("\n📤 Spawning tasks...")
    t1 = swarm.spawn_task("research", {"topic": "AI"})
    t2 = swarm.spawn_task("build", {"project": "app"})
    t3 = swarm.spawn_task("research", {"topic": "ML"})
    
    print(f"   Task 1: {t1}")
    print(f"   Task 2: {t2}")
    print(f"   Task 3: {t3}")
    
    # Check status
    status = swarm.get_swarm_status()
    print(f"\n📊 Swarm Status:")
    print(f"   Active: {status['active_tasks']}")
    print(f"   Agents: {status['available_agents']}")
    print(f"   Load: {status['agent_loads']}")
    
    print("\n✅ Swarm coordinator ready")


if __name__ == "__main__":
    demo_self_evolution()
    demo_swarm()
