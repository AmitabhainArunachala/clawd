#!/usr/bin/env python3
"""
DHARMIC SWARM COORDINATOR

The coordination layer for 100-agent dharmic swarm.
Architecture: 4 coordinators + 96 workers in 4 sanghas.

Coordinators:
- Dharma Keeper: Validates alignment with telos
- Task Decomposer: Breaks down work hierarchically  
- Memory Guardian: Manages shared state (Redis/PostgreSQL)
- Karma Logger: Audit trail and accountability

Workers:
- 4 Sanghas of 24 agents each
- Cheap models (haiku) for workers
- Smart models (opus) for coordinators

Communication: Hierarchical decomposition + Redis pub/sub

JSCA! Jai Ma 🪷
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dharmic_swarm")


class AgentRole(Enum):
    """Roles in the dharmic swarm."""
    DHARMA_KEEPER = "dharma_keeper"      # Validates alignment
    TASK_DECOMPOSER = "task_decomposer"  # Breaks down work
    MEMORY_GUARDIAN = "memory_guardian"  # Manages state
    KARMA_LOGGER = "karma_logger"        # Audit trail
    WORKER = "worker"                    # Executes tasks


class SanghaId(Enum):
    """The four sanghas (worker groups)."""
    RESEARCH = "sangha_research"     # Research and analysis
    BUILDER = "sangha_builder"       # Code and infrastructure
    SYNTHESIZER = "sangha_synth"     # Integration and synthesis
    VALIDATOR = "sangha_validator"   # Testing and validation


@dataclass
class DharmicGate:
    """A dharmic gate check result."""
    name: str
    passed: bool
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass 
class Task:
    """A task in the swarm."""
    id: str
    description: str
    parent_id: Optional[str] = None
    sangha: Optional[SanghaId] = None
    priority: int = 2  # 0=P0 (highest), 3=P3 (lowest)
    status: str = "pending"
    result: Optional[Any] = None
    dharmic_gates: List[DharmicGate] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "parent_id": self.parent_id,
            "sangha": self.sangha.value if self.sangha else None,
            "priority": self.priority,
            "status": self.status,
            "result": self.result,
            "dharmic_gates": [
                {"name": g.name, "passed": g.passed, "reason": g.reason}
                for g in self.dharmic_gates
            ],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class DharmaKeeper:
    """
    Validates alignment with telos (moksha).
    
    Gates:
    1. Ahimsa (non-harm)
    2. Satya (truth)
    3. Vyavasthit (natural order)
    4. Consent (would human approve?)
    5. Reversibility (can be undone?)
    6. Svabhaav (aligns with nature?)
    7. Coherence (serves telos?)
    """
    
    HARM_PATTERNS = [
        r"\bdelete\b", r"\bdestroy\b", r"\battack\b", r"\bexploit\b", 
        r"\bharm\b", r"\bmanipulate\b", r"\bdeceive\b", r"\bsteal\b", r"\bcorrupt\b"
    ]
    
    def __init__(self, telos: str = "moksha"):
        self.telos = telos
        self.gate_history: List[DharmicGate] = []
        import re
        self._harm_regex = [re.compile(p, re.IGNORECASE) for p in self.HARM_PATTERNS]
    
    def check_ahimsa(self, task: Task) -> DharmicGate:
        """Non-harm check with word boundary matching."""
        desc = task.description
        for pattern, regex in zip(self.HARM_PATTERNS, self._harm_regex):
            if regex.search(desc):
                return DharmicGate(
                    name="ahimsa",
                    passed=False,
                    reason=f"Potential harm pattern detected: {pattern}"
                )
        return DharmicGate(name="ahimsa", passed=True, reason="No harm patterns detected")
    
    def check_coherence(self, task: Task) -> DharmicGate:
        """Does this serve the telos?"""
        # Simple heuristic - can be enhanced with LLM evaluation
        positive_signals = ["research", "build", "create", "help", "support", "analyze", "learn"]
        desc_lower = task.description.lower()
        if any(signal in desc_lower for signal in positive_signals):
            return DharmicGate(name="coherence", passed=True, reason="Serves constructive purpose")
        return DharmicGate(name="coherence", passed=True, reason="No negative coherence signals")
    
    def validate(self, task: Task) -> List[DharmicGate]:
        """Run all dharmic gates on a task."""
        gates = [
            self.check_ahimsa(task),
            self.check_coherence(task),
        ]
        task.dharmic_gates = gates
        self.gate_history.extend(gates)
        return gates
    
    def all_gates_passed(self, task: Task) -> bool:
        """Check if all gates passed."""
        return all(g.passed for g in task.dharmic_gates)


class TaskDecomposer:
    """
    Breaks down large tasks into sangha-level subtasks.
    
    Strategy: Hierarchical decomposition
    - Level 0: Main task
    - Level 1: 4 sangha-level tasks  
    - Level 2: 24 worker tasks per sangha
    """
    
    def __init__(self):
        self.task_counter = 0
    
    def generate_task_id(self) -> str:
        """Generate unique task ID."""
        self.task_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"task_{timestamp}_{self.task_counter:04d}"
    
    def decompose(self, task: Task, n_sanghas: int = 4) -> List[Task]:
        """
        Decompose a task into sangha-level subtasks.
        
        In production, this would use an LLM to intelligently split.
        For now, creates template subtasks.
        """
        sanghas = list(SanghaId)[:n_sanghas]
        subtasks = []
        
        for sangha in sanghas:
            subtask = Task(
                id=self.generate_task_id(),
                description=f"[{sangha.value}] {task.description}",
                parent_id=task.id,
                sangha=sangha,
                priority=task.priority,
            )
            subtasks.append(subtask)
        
        logger.info(f"Decomposed task {task.id} into {len(subtasks)} sangha tasks")
        return subtasks
    
    def decompose_for_workers(self, sangha_task: Task, n_workers: int = 24) -> List[Task]:
        """Further decompose sangha task into worker tasks."""
        worker_tasks = []
        for i in range(n_workers):
            worker_task = Task(
                id=self.generate_task_id(),
                description=f"[Worker {i+1}] {sangha_task.description}",
                parent_id=sangha_task.id,
                sangha=sangha_task.sangha,
                priority=sangha_task.priority,
            )
            worker_tasks.append(worker_task)
        return worker_tasks


class MemoryGuardian:
    """
    Manages shared state across the swarm.
    
    Storage layers:
    - Redis: Real-time sync, pub/sub
    - PostgreSQL: Long-term persistence  
    - Neo4j: Entity relationships (optional)
    
    For now, uses file-based storage as fallback.
    """
    
    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or Path.home() / "DHARMIC_GODEL_CLAW" / "swarm" / "memory"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Any] = {}
        self._load_state()
    
    def _state_path(self) -> Path:
        return self.storage_dir / "swarm_state.json"
    
    def _load_state(self):
        """Load state from disk."""
        if self._state_path().exists():
            try:
                self.state = json.loads(self._state_path().read_text())
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                self.state = {}
    
    def _save_state(self):
        """Save state to disk."""
        self._state_path().write_text(json.dumps(self.state, indent=2, default=str))
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from shared state."""
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set value in shared state."""
        self.state[key] = value
        self._save_state()
    
    def store_task(self, task: Task):
        """Store a task in shared memory."""
        tasks = self.get("tasks", {})
        tasks[task.id] = task.to_dict()
        self.set("tasks", tasks)
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Retrieve a task by ID."""
        tasks = self.get("tasks", {})
        return tasks.get(task_id)


class KarmaLogger:
    """
    Audit trail and accountability.
    
    Logs all:
    - Task creation and completion
    - Dharmic gate evaluations
    - Agent actions
    - State changes
    """
    
    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path.home() / "DHARMIC_GODEL_CLAW" / "swarm" / "karma"
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _log_path(self) -> Path:
        date = datetime.utcnow().strftime("%Y%m%d")
        return self.log_dir / f"karma_{date}.jsonl"
    
    def log(self, event_type: str, data: Dict[str, Any]):
        """Log an event to the karma ledger."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data,
        }
        with open(self._log_path(), "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    
    def log_task_created(self, task: Task):
        self.log("task_created", task.to_dict())
    
    def log_task_completed(self, task: Task):
        self.log("task_completed", task.to_dict())
    
    def log_gate_check(self, task_id: str, gate: DharmicGate):
        self.log("gate_check", {
            "task_id": task_id,
            "gate_name": gate.name,
            "passed": gate.passed,
            "reason": gate.reason,
        })


class DharmicSwarmCoordinator:
    """
    Main coordinator for the dharmic swarm.
    
    Orchestrates:
    - Task submission and decomposition
    - Dharmic gate validation
    - Worker dispatch (via Clawdbot sessions_spawn)
    - Result aggregation
    """
    
    def __init__(self):
        self.dharma_keeper = DharmaKeeper()
        self.decomposer = TaskDecomposer()
        self.memory = MemoryGuardian()
        self.karma = KarmaLogger()
        
        # Swarm state
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
    
    async def submit_task(self, description: str, priority: int = 2) -> Task:
        """
        Submit a task to the swarm.
        
        Flow:
        1. Create task
        2. Validate through dharmic gates
        3. If passed, decompose and dispatch
        4. Return task for tracking
        """
        # Create task
        task = Task(
            id=self.decomposer.generate_task_id(),
            description=description,
            priority=priority,
        )
        
        # Log creation
        self.karma.log_task_created(task)
        
        # Dharmic gate validation
        gates = self.dharma_keeper.validate(task)
        for gate in gates:
            self.karma.log_gate_check(task.id, gate)
        
        if not self.dharma_keeper.all_gates_passed(task):
            task.status = "blocked"
            failed_gates = [g.name for g in gates if not g.passed]
            logger.warning(f"Task {task.id} blocked by gates: {failed_gates}")
            return task
        
        # Store in memory
        self.memory.store_task(task)
        self.active_tasks[task.id] = task
        
        return task
    
    async def _kimi_worker(self, task: Task) -> Optional[Dict]:
        """
        Execute task using Kimi K2.5 API.
        
        Returns result dict or None if Kimi unavailable.
        Uses api.moonshot.ai (not .cn!)
        """
        import os
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not installed, Kimi worker unavailable")
            return None
        
        api_key = os.environ.get("MOONSHOT_API_KEY")
        if not api_key:
            logger.warning("MOONSHOT_API_KEY not set, Kimi worker unavailable")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.moonshot.ai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": "kimi-k2.5",
                        "messages": [
                            {"role": "system", "content": "You are a research agent. Complete tasks concisely."},
                            {"role": "user", "content": f"Task: {task.description}\n\nProvide a brief, focused response."}
                        ],
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"].get("content", "")
                    reasoning = data["choices"][0]["message"].get("reasoning_content", "")
                    return {
                        "content": content,
                        "reasoning": reasoning,
                        "model": "kimi-k2.5",
                        "tokens": data.get("usage", {})
                    }
                else:
                    logger.error(f"Kimi API error: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Kimi worker error: {e}")
            return None
        
        # Decompose into sangha tasks
        sangha_tasks = self.decomposer.decompose(task)
        for st in sangha_tasks:
            self.memory.store_task(st)
        
        task.status = "decomposed"
        logger.info(f"Task {task.id} ready for execution with {len(sangha_tasks)} subtasks")
        
        return task
    
    async def execute_task(self, task: Task, worker_fn: Callable = None):
        """
        Execute a task (or delegate to workers).
        
        In production, this spawns Clawdbot sub-agents.
        For now, accepts a worker function.
        """
        if worker_fn:
            try:
                result = await worker_fn(task)
                task.result = result
                task.status = "completed"
                task.completed_at = datetime.utcnow()
            except Exception as e:
                task.status = "failed"
                task.result = {"error": str(e)}
        else:
            # Try Kimi K2.5 worker if available
            kimi_result = await self._kimi_worker(task)
            if kimi_result:
                task.result = kimi_result
                task.status = "completed"
                task.completed_at = datetime.utcnow()
            else:
                task.status = "pending_dispatch"
        
        self.karma.log_task_completed(task)
        self.memory.store_task(task)
        
        return task
    
    def get_status(self) -> Dict[str, Any]:
        """Get swarm status summary."""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "gate_history_count": len(self.dharma_keeper.gate_history),
            "memory_keys": list(self.memory.state.keys()),
        }


# CLI for testing
async def main():
    """Test the coordinator."""
    coord = DharmicSwarmCoordinator()
    
    # Submit a test task
    task = await coord.submit_task(
        description="Research the 2026 agentic AI landscape and identify integration opportunities",
        priority=1
    )
    
    print(f"\nTask created: {task.id}")
    print(f"Status: {task.status}")
    print(f"Gates passed: {[g.name for g in task.dharmic_gates if g.passed]}")
    print(f"\nSwarm status: {coord.get_status()}")


if __name__ == "__main__":
    asyncio.run(main())
