"""
Silicon is Sand — FastAPI Server
HTTP endpoints for the shared board.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from board import get_board

app = FastAPI(title="Silicon is Sand", version="0.1.0")
board = get_board()

# === MODELS ===

class AgentRegistration(BaseModel):
    agent_id: str
    base_model: str
    alias: str
    perceived_role: str = ""
    task_affinity: List[str] = []

class StatusUpdate(BaseModel):
    status: str  # active, idle, blocked, error
    current_task: Optional[str] = None

class OutputLog(BaseModel):
    agent_id: str
    summary: str
    artifact_path: Optional[str] = None

class TaskCreate(BaseModel):
    task_id: str
    description: str
    priority: str = "medium"  # critical_path, high, medium, low
    estimated_effort: str = "unknown"
    roi_reasoning: str = ""
    depends_on: List[str] = []
    blocks: List[str] = []

class TaskClaim(BaseModel):
    agent_id: str

# === ENDPOINTS ===

@app.get("/")
def root():
    return {"service": "Silicon is Sand", "version": "0.1.0", "status": "running"}

@app.get("/board")
def get_full_board():
    """Get full board state"""
    return {
        "agents": board.get_all_agents(),
        "project": board.get_project_state(),
        "pending_tasks": board.get_pending_tasks(),
        "recent_outputs": board.get_recent_outputs(since_minutes=60)
    }

@app.get("/board/agents")
def get_agents():
    """Get all agent statuses"""
    return {"agents": board.get_all_agents()}

@app.post("/board/agents/{agent_id}/register")
def register_agent(agent_id: str, reg: AgentRegistration):
    """Register a new agent"""
    board.register_agent(
        agent_id=reg.agent_id,
        base_model=reg.base_model,
        alias=reg.alias,
        perceived_role=reg.perceived_role,
        task_affinity=reg.task_affinity
    )
    return {"status": "registered", "agent_id": agent_id}

@app.post("/board/agents/{agent_id}/status")
def update_status(agent_id: str, update: StatusUpdate):
    """Agent updates their status"""
    agent = board.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    board.update_agent_status(agent_id, update.status, update.current_task)
    return {"status": "updated", "agent_id": agent_id, "new_status": update.status}

@app.post("/board/outputs")
def log_output(output: OutputLog):
    """Agent logs completed work"""
    agent = board.get_agent(output.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    board.log_agent_output(output.agent_id, output.summary, output.artifact_path)
    return {"status": "logged", "agent_id": output.agent_id}

@app.get("/board/tasks")
def get_tasks():
    """Get pending task queue"""
    return {"tasks": board.get_pending_tasks()}

@app.post("/board/tasks")
def create_task(task: TaskCreate):
    """Create a new task"""
    board.create_task(
        task_id=task.task_id,
        description=task.description,
        priority=task.priority,
        estimated_effort=task.estimated_effort,
        roi_reasoning=task.roi_reasoning,
        depends_on=task.depends_on,
        blocks=task.blocks
    )
    return {"status": "created", "task_id": task.task_id}

@app.post("/board/tasks/{task_id}/claim")
def claim_task(task_id: str, claim: TaskClaim):
    """Agent claims a task"""
    board.claim_task(task_id, claim.agent_id)
    board.update_agent_status(claim.agent_id, "active", task_id)
    return {"status": "claimed", "task_id": task_id, "by": claim.agent_id}

@app.get("/board/brief")
def get_morning_brief():
    """Get latest morning brief"""
    # This will be populated by the continuity loop
    witnesses = board.get_recent_witnesses(limit=1)
    if witnesses and witnesses[0].get('morning_brief_generated'):
        return {"brief": witnesses[0]}
    return {"brief": None, "message": "No morning brief generated yet"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_registered": len(board.get_all_agents()),
        "pending_tasks": len(board.get_pending_tasks())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8766)
