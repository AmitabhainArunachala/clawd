"""
Silicon is Sand — Shared Board Database Layer
Fast, simple, stigmergic.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "shared_board.db"

class SharedBoard:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        with self._connect() as conn:
            if schema_path.exists():
                conn.executescript(schema_path.read_text())
    
    # === AGENT REGISTRY ===
    
    def register_agent(self, agent_id: str, base_model: str, alias: str, 
                       task_affinity: List[str], perceived_role: str = ""):
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agent_registry 
                (agent_id, base_model, alias, perceived_role, task_affinity, status, trust_gradient)
                VALUES (?, ?, ?, ?, ?, 'idle', 0.5)
            """, (agent_id, base_model, alias, perceived_role, json.dumps(task_affinity)))
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM agent_registry WHERE agent_id = ?", (agent_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def get_all_agents(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM agent_registry").fetchall()
            return [dict(row) for row in rows]
    
    def update_agent_status(self, agent_id: str, status: str, current_task: Optional[str] = None):
        with self._connect() as conn:
            conn.execute("""
                UPDATE agent_registry 
                SET status = ?, current_task = ?, last_output_timestamp = ?
                WHERE agent_id = ?
            """, (status, current_task, datetime.utcnow().isoformat(), agent_id))
    
    def log_agent_output(self, agent_id: str, summary: str, artifact_path: Optional[str] = None):
        """Log agent output and update their last_output fields"""
        output_id = f"{agent_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        with self._connect() as conn:
            # Insert output log
            conn.execute("""
                INSERT INTO output_log (output_id, agent_id, summary, artifact_path)
                VALUES (?, ?, ?, ?)
            """, (output_id, agent_id, summary, artifact_path))
            # Update agent last_output fields
            conn.execute("""
                UPDATE agent_registry 
                SET last_output_timestamp = ?, last_output_summary = ?
                WHERE agent_id = ?
            """, (datetime.utcnow().isoformat(), summary, agent_id))
    
    # === PROJECT STATE ===
    
    def init_project(self, project_name: str, milestone: str, sprint_days: int = 7):
        sprint_end = (datetime.now() + timedelta(days=sprint_days)).date()
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO project_state (id, project_name, current_milestone, sprint_end, components, dependencies, decision_queue)
                VALUES (1, ?, ?, ?, '{}', '[]', '[]')
            """, (project_name, milestone, sprint_end))
    
    def get_project_state(self) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM project_state WHERE id = 1").fetchone()
            return dict(row) if row else None
    
    def update_project_components(self, components: Dict):
        with self._connect() as conn:
            conn.execute(
                "UPDATE project_state SET components = ? WHERE id = 1",
                (json.dumps(components),)
            )
    
    def add_to_decision_queue(self, question: str, priority: str, waiting_for: str):
        with self._connect() as conn:
            state = self.get_project_state()
            if state:
                queue = json.loads(state.get('decision_queue', '[]'))
                queue.append({
                    'question': question,
                    'priority': priority,
                    'waiting_for': waiting_for,
                    'timestamp': datetime.utcnow().isoformat()
                })
                conn.execute(
                    "UPDATE project_state SET decision_queue = ? WHERE id = 1",
                    (json.dumps(queue),)
                )
    
    # === TASK QUEUE ===
    
    def create_task(self, task_id: str, description: str, priority: str = 'medium',
                    estimated_effort: str = "unknown", roi_reasoning: str = "",
                    depends_on: Optional[List[str]] = None, blocks: Optional[List[str]] = None):
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO task_queue (task_id, description, priority, estimated_effort, roi_reasoning, depends_on, blocks, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (task_id, description, priority, estimated_effort, roi_reasoning,
                  json.dumps(depends_on or []), json.dumps(blocks or [])))
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get tasks ordered by priority (critical_path > high > medium > low)"""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM task_queue 
                WHERE status = 'pending'
                ORDER BY CASE priority
                    WHEN 'critical_path' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END
            """).fetchall()
            return [dict(row) for row in rows]
    
    def claim_task(self, task_id: str, agent_id: str):
        with self._connect() as conn:
            conn.execute("""
                UPDATE task_queue SET status = 'in_progress', assigned_to = ?
                WHERE task_id = ?
            """, (agent_id, task_id))
    
    def complete_task(self, task_id: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE task_queue SET status = 'completed' WHERE task_id = ?",
                (task_id,)
            )
    
    # === OUTPUT LOG ===
    
    def get_recent_outputs(self, since_minutes: int = 30) -> List[Dict]:
        cutoff = (datetime.utcnow() - timedelta(minutes=since_minutes)).isoformat()
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM output_log 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            """, (cutoff,)).fetchall()
            return [dict(row) for row in rows]
    
    # === WITNESS LOG ===
    
    def log_witness(self, cycle_number: int, perceived: Dict, evaluated: Dict, activated: Dict):
        witness_id = f"witness_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{cycle_number}"
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO witness_log (witness_id, cycle_number, perceived, evaluated, activated)
                VALUES (?, ?, ?, ?, ?)
            """, (witness_id, cycle_number, json.dumps(perceived), 
                  json.dumps(evaluated), json.dumps(activated)))
        return witness_id
    
    def get_recent_witnesses(self, limit: int = 10) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM witness_log 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

# Singleton instance
_board = None

def get_board() -> SharedBoard:
    global _board
    if _board is None:
        _board = SharedBoard()
    return _board
