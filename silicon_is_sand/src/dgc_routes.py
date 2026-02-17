"""
Silicon is Sand — DGC Integration Endpoint
POST /board/outputs/{id}/score
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dgc_scorer import scorer

router = APIRouter(prefix="/board/outputs", tags=["dgc"])

# Board will be imported from server to avoid circular imports
# This is set when server.py includes the router
board = None

def set_board(board_instance):
    """Called by server.py to provide the board instance"""
    global board
    board = board_instance

class ScoreResponse(BaseModel):
    output_id: str
    dgc_score: dict
    passed_gate: bool
    gate_message: str

@router.post("/{output_id}/score")
def score_output(output_id: str):
    """Score an existing output with DGC"""
    if board is None:
        raise HTTPException(status_code=500, detail="Board not initialized")
    
    # Get output from board
    with board._connect() as conn:
        row = conn.execute(
            "SELECT * FROM output_log WHERE output_id = ?",
            (output_id,)
        ).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Output not found")
    
    output = dict(row)
    
    # Score it
    score = scorer.score_output(
        output.get("summary", ""),
        output.get("artifact_path")
    )
    
    # Gate check
    passed, message = scorer.gate_check(score)
    
    # Update output with score
    with board._connect() as conn:
        conn.execute(
            "UPDATE output_log SET dgc_score = ? WHERE output_id = ?",
            (score.get("composite"), output_id)
        )
    
    return {
        "output_id": output_id,
        "dgc_score": score,
        "passed_gate": passed,
        "gate_message": message
    }

@router.get("/scores/recent")
def recent_scores(limit: int = 10):
    """Get recently scored outputs"""
    if board is None:
        raise HTTPException(status_code=500, detail="Board not initialized")
    
    with board._connect() as conn:
        rows = conn.execute("""
            SELECT output_id, agent_id, summary, dgc_score, timestamp
            FROM output_log
            WHERE dgc_score IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
    
    return {"scored_outputs": [dict(row) for row in rows]}
