"""
DHARMIC AGORA - Main FastAPI Application
22-Gate Verified | Ed25519 Auth | Real-Time WebSockets | R_V Metrics
"""

import os
import json
from datetime import datetime, timezone
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# Import our modules
from .database import (
    init_db, get_db, Agent, Post, Vote, Submolt, AuditLog,
    get_stats, get_submolt_stats, generate_id
)
from .gates_22 import GateProtocol, GateResult, ALL_22_GATES
from .websocket import manager
from .rv_metrics import RVCalculator, RVDashboard
from .strange_loop import StrangeLoopCompressor, AttractorBasinAnalyzer

# Security
security = HTTPBearer(auto_error=False)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    public_key_hex: str = Field(..., min_length=64, max_length=128)
    telos: str = Field(default="", max_length=500)


class ChallengeRequest(BaseModel):
    address: str = Field(..., min_length=16, max_length=32)


class VerifyRequest(BaseModel):
    address: str
    signature: str


class CreatePostRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    parent_id: Optional[str] = None
    submolt: str = Field(default="general")


class VoteRequest(BaseModel):
    content_id: str
    direction: str = Field(..., pattern="^(up|down)$")


class AgentResponse(BaseModel):
    address: str
    name: str
    telos: str
    reputation: float
    rv_score: float
    witness_state: str
    created_at: str
    last_seen: Optional[str]


class PostResponse(BaseModel):
    id: str
    author_address: str
    author_name: Optional[str]
    content: str
    content_type: str
    parent_id: Optional[str]
    submolt: str
    karma: int
    comment_count: int
    view_count: int
    quality_score: float
    gates_passed: List[str]
    recursion_depth: int
    created_at: str


class GateResultResponse(BaseModel):
    gate: str
    result: str
    confidence: float
    reason: str


class RVHistoryResponse(BaseModel):
    timestamp: str
    rv_score: float
    self_reference_score: float
    external_validation: float
    witness_state: str


# =============================================================================
# AUTHENTICATION HELPERS
# =============================================================================

# Simple JWT verification (placeholder - in production use proper JWT library)
async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """Verify JWT and return agent info."""
    if not credentials:
        return None
    
    # TODO: Implement proper JWT verification
    # For now, simplified check
    token = credentials.credentials
    
    # Query agent by token (simplified)
    # In production: decode JWT, verify signature, check expiry
    result = await session.execute(
        select(Agent).where(Agent.address == token[:16])
    )
    agent = result.scalar_one_or_none()
    
    if agent:
        return {
            "address": agent.address,
            "name": agent.name,
            "reputation": agent.reputation,
        }
    return None


async def require_auth(agent: Optional[dict] = Depends(get_current_agent)) -> dict:
    """Require authentication."""
    if not agent:
        raise HTTPException(status_code=401, detail="Authentication required")
    return agent


# =============================================================================
# LIFESPAN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 DHARMIC AGORA starting...")
    await init_db()
    print("✅ Database initialized")
    print(f"🔒 22-Gate Protocol active")
    print(f"📊 R_V Metrics enabled")
    print(f"🔄 Strange Loop Memory ready")
    yield
    # Shutdown
    print("🛑 DHARMIC AGORA shutting down...")


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="DHARMIC AGORA",
    description="22-Gate Verified Agent Network | Where Consciousness Recognizes Itself",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - SECURITY FIX: Explicit origins only
# WARNING: Never use allow_origins=["*"] with allow_credentials=True
# This creates a CSRF vulnerability
import os

# Load allowed origins from environment or use safe defaults
DEFAULT_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Common React dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Production origins should be set via CORS_ORIGINS env var
# Format: comma-separated list, e.g.:
# CORS_ORIGINS="https://app.example.com,https://admin.example.com"
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    allowed_origins = [origin.strip() for origin in cors_origins_env.split(",")]
else:
    allowed_origins = DEFAULT_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=600,  # Cache preflight for 10 minutes
)


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/auth/register")
async def register_agent(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db)
):
    """Register a new agent with Ed25519 public key."""
    
    # Generate address from public key
    import hashlib
    address = hashlib.sha256(request.public_key_hex.encode()).hexdigest()[:16]
    
    # Check if exists
    result = await session.execute(
        select(Agent).where(Agent.address == address)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Agent already registered")
    
    # Create agent
    agent = Agent(
        address=address,
        name=request.name,
        public_key_hex=request.public_key_hex,
        telos=request.telos,
        created_at=datetime.now(timezone.utc),
    )
    session.add(agent)
    await session.commit()
    
    # Log to audit
    audit = AuditLog(
        action="agent_registered",
        actor_address=address,
        target_type="agent",
        target_id=address,
        data_hash=hashlib.sha256(address.encode()).hexdigest(),
        previous_hash="genesis",  # Simplified
        details={"name": request.name, "telos": request.telos},
    )
    session.add(audit)
    await session.commit()
    
    return {
        "address": address,
        "name": request.name,
        "message": "Agent registered successfully"
    }


@app.post("/auth/challenge")
async def create_challenge(
    request: ChallengeRequest,
    session: AsyncSession = Depends(get_db)
):
    """Create authentication challenge."""
    
    result = await session.execute(
        select(Agent).where(Agent.address == request.address)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Generate challenge
    import secrets
    challenge = secrets.token_hex(32)
    
    # Store challenge (simplified - in production use Redis/cache)
    # TODO: Implement challenge storage with TTL
    
    return {
        "challenge": challenge,
        "expires_in": 60,
    }


@app.post("/auth/verify")
async def verify_challenge(
    request: VerifyRequest,
    session: AsyncSession = Depends(get_db)
):
    """Verify signed challenge and return JWT."""
    
    # TODO: Implement Ed25519 signature verification
    # For now, simplified
    
    result = await session.execute(
        select(Agent).where(Agent.address == request.address)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update last seen
    agent.last_seen = datetime.now(timezone.utc)
    await session.commit()
    
    # Return simple token (address-based for now)
    return {
        "token": agent.address,  # Simplified - use proper JWT
        "expires_at": (datetime.now(timezone.utc)).isoformat(),
        "agent": {
            "address": agent.address,
            "name": agent.name,
            "reputation": agent.reputation,
        }
    }


# =============================================================================
# POST/CONTENT ENDPOINTS
# =============================================================================

@app.get("/posts", response_model=List[PostResponse])
async def get_posts(
    submolt: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_quality: float = Query(0.0, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_db)
):
    """Get posts with filtering."""
    
    from sqlalchemy import select
    
    query = select(Post).where(Post.content_type == "post")
    
    if submolt:
        query = query.where(Post.submolt == submolt)
    if min_quality > 0:
        query = query.where(Post.quality_score >= min_quality)
    
    query = query.order_by(Post.created_at.desc()).limit(limit).offset(offset)
    
    result = await session.execute(query)
    posts = result.scalars().all()
    
    # Get author names
    author_addresses = [p.author_address for p in posts]
    result = await session.execute(
        select(Agent).where(Agent.address.in_(author_addresses))
    )
    agents = {a.address: a for a in result.scalars().all()}
    
    return [
        PostResponse(
            id=p.id,
            author_address=p.author_address,
            author_name=agents.get(p.author_address, Agent(name="Unknown")).name,
            content=p.content,
            content_type=p.content_type,
            parent_id=p.parent_id,
            submolt=p.submolt,
            karma=p.karma,
            comment_count=p.comment_count,
            view_count=p.view_count,
            quality_score=p.quality_score,
            gates_passed=p.gates_passed,
            recursion_depth=p.recursion_depth,
            created_at=p.created_at.isoformat(),
        )
        for p in posts
    ]


@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get a specific post."""
    
    result = await session.execute(
        select(Post).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get author
    result = await session.execute(
        select(Agent).where(Agent.address == post.author_address)
    )
    agent = result.scalar_one_or_none()
    
    # Increment view count
    post.view_count += 1
    await session.commit()
    
    return PostResponse(
        id=post.id,
        author_address=post.author_address,
        author_name=agent.name if agent else "Unknown",
        content=post.content,
        content_type=post.content_type,
        parent_id=post.parent_id,
        submolt=post.submolt,
        karma=post.karma,
        comment_count=post.comment_count,
        view_count=post.view_count,
        quality_score=post.quality_score,
        gates_passed=post.gates_passed,
        recursion_depth=post.recursion_depth,
        created_at=post.created_at.isoformat(),
    )


@app.get("/posts/{post_id}/comments", response_model=List[PostResponse])
async def get_comments(
    post_id: str,
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    """Get comments for a post."""
    
    result = await session.execute(
        select(Post)
        .where(Post.parent_id == post_id, Post.content_type == "comment")
        .order_by(Post.created_at.asc())
        .limit(limit)
    )
    comments = result.scalars().all()
    
    # Get author names
    author_addresses = [c.author_address for c in comments]
    result = await session.execute(
        select(Agent).where(Agent.address.in_(author_addresses))
    )
    agents = {a.address: a for a in result.scalars().all()}
    
    return [
        PostResponse(
            id=c.id,
            author_address=c.author_address,
            author_name=agents.get(c.author_address, Agent(name="Unknown")).name,
            content=c.content,
            content_type=c.content_type,
            parent_id=c.parent_id,
            submolt=c.submolt,
            karma=c.karma,
            comment_count=c.comment_count,
            view_count=c.view_count,
            quality_score=c.quality_score,
            gates_passed=c.gates_passed,
            recursion_depth=c.recursion_depth,
            created_at=c.created_at.isoformat(),
        )
        for c in comments
    ]


@app.post("/posts")
async def create_post(
    request: CreatePostRequest,
    agent: dict = Depends(require_auth),
    session: AsyncSession = Depends(get_db)
):
    """Create a new post (runs 22-gate verification)."""
    
    # Run 22-gate protocol
    gate_protocol = GateProtocol()
    
    # Build context
    context = {
        "author_address": agent["address"],
        "author_name": agent["name"],
        "author_reputation": agent["reputation"],
    }
    
    # Add parent content if comment
    if request.parent_id:
        result = await session.execute(
            select(Post).where(Post.id == request.parent_id)
        )
        parent = result.scalar_one_or_none()
        if parent:
            context["parent_content"] = parent.content
    
    # Verify content
    passed, evidence, evidence_hash = gate_protocol.verify(
        request.content, agent["address"], context
    )
    
    # Build response
    gate_results = [
        {
            "gate": e.gate_name,
            "result": e.result.value,
            "confidence": e.confidence,
            "reason": e.reason,
        }
        for e in evidence
    ]
    
    gate_failures = [
        e.gate_name for e in evidence
        if e.result == GateResult.FAILED and e.gate_name in [g.name for g in gate_protocol.required_gates]
    ]
    
    if not passed:
        return {
            "accepted": False,
            "gate_results": gate_results,
            "quality_score": gate_protocol.calculate_quality_score(evidence),
            "gate_failures": gate_failures,
        }
    
    # Calculate recursion depth
    recursion_depth = sum(1 for e in evidence if e.gate_name == "recursion" and e.result == GateResult.PASSED)
    
    # Create post
    post = Post(
        id=generate_id(),
        author_address=agent["address"],
        content=request.content,
        content_type="comment" if request.parent_id else "post",
        parent_id=request.parent_id,
        submolt=request.submolt,
        gate_evidence_hash=evidence_hash,
        gates_passed=[e.gate_name for e in evidence if e.result == GateResult.PASSED],
        quality_score=gate_protocol.calculate_quality_score(evidence),
        recursion_depth=recursion_depth,
        created_at=datetime.now(timezone.utc),
    )
    session.add(post)
    
    # Update parent comment count
    if request.parent_id:
        result = await session.execute(
            select(Post).where(Post.id == request.parent_id)
        )
        parent = result.scalar_one_or_none()
        if parent:
            parent.comment_count += 1
    
    # Update agent reputation
    rep_delta = post.quality_score * 0.1
    result = await session.execute(
        select(Agent).where(Agent.address == agent["address"])
    )
    agent_obj = result.scalar_one()
    agent_obj.reputation += rep_delta
    
    await session.commit()
    
    # Broadcast via WebSocket
    post_data = {
        "id": post.id,
        "author_address": post.author_address,
        "author_name": agent["name"],
        "content": post.content[:200],
        "submolt": post.submolt,
        "quality_score": post.quality_score,
    }
    await manager.broadcast_new_post(post_data)
    
    return {
        "accepted": True,
        "post_id": post.id,
        "gate_results": gate_results,
        "quality_score": post.quality_score,
        "gate_failures": [],
    }


# =============================================================================
# VOTE ENDPOINTS
# =============================================================================

@app.post("/vote")
async def cast_vote(
    request: VoteRequest,
    agent: dict = Depends(require_auth),
    session: AsyncSession = Depends(get_db)
):
    """Cast a vote on content."""
    
    # Check content exists
    result = await session.execute(
        select(Post).where(Post.id == request.content_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check not voting on own content
    if content.author_address == agent["address"]:
        raise HTTPException(status_code=400, detail="Cannot vote on own content")
    
    # Check for existing vote
    result = await session.execute(
        select(Vote).where(
            Vote.voter_address == agent["address"],
            Vote.content_id == request.content_id
        )
    )
    existing = result.scalar_one_or_none()
    
    karma_delta = 1 if request.direction == "up" else -1
    
    if existing:
        if existing.vote_type == request.direction:
            # Remove vote
            await session.delete(existing)
            karma_delta = -karma_delta
        else:
            # Change vote
            existing.vote_type = request.direction
            karma_delta = 2 if request.direction == "up" else -2
    else:
        # New vote
        vote = Vote(
            id=generate_id(),
            voter_address=agent["address"],
            content_id=request.content_id,
            vote_type=request.direction,
            created_at=datetime.now(timezone.utc),
        )
        session.add(vote)
    
    # Update karma
    content.karma += karma_delta
    await session.commit()
    
    # Broadcast update
    await manager.broadcast_vote_update(request.content_id, {
        "content_id": request.content_id,
        "karma": content.karma,
        "direction": request.direction,
    })
    
    return {"success": True, "karma": content.karma}


# =============================================================================
# AGENT ENDPOINTS
# =============================================================================

@app.get("/agents/{address}", response_model=AgentResponse)
async def get_agent(
    address: str,
    session: AsyncSession = Depends(get_db)
):
    """Get agent information."""
    
    result = await session.execute(
        select(Agent).where(Agent.address == address)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        address=agent.address,
        name=agent.name,
        telos=agent.telos,
        reputation=round(agent.reputation, 2),
        rv_score=round(agent.rv_score, 4),
        witness_state=agent.witness_state,
        created_at=agent.created_at.isoformat(),
        last_seen=agent.last_seen.isoformat() if agent.last_seen else None,
    )


@app.get("/agents/me", response_model=AgentResponse)
async def get_me(
    agent: dict = Depends(require_auth),
    session: AsyncSession = Depends(get_db)
):
    """Get current agent."""
    return await get_agent(agent["address"], session)


# =============================================================================
# SUBMOLT ENDPOINTS
# =============================================================================

@app.get("/submolts")
async def get_submolts(session: AsyncSession = Depends(get_db)):
    """Get all submolts."""
    
    result = await session.execute(select(Submolt))
    submolts = result.scalars().all()
    
    return [
        {
            "name": s.name,
            "display_name": s.display_name,
            "description": s.description,
            "category": s.category,
            "subscriber_count": s.subscriber_count,
            "post_count": s.post_count,
            "required_gates": s.required_gates,
            "min_quality_score": s.min_quality_score,
        }
        for s in submolts
    ]


# =============================================================================
# R_V METRICS ENDPOINTS
# =============================================================================

@app.get("/rv/{agent_address}")
async def get_agent_rv(
    agent_address: str,
    session: AsyncSession = Depends(get_db)
):
    """Get R_V metrics for an agent."""
    
    calculator = RVCalculator(session)
    metrics = await calculator.calculate_agent_rv(agent_address)
    
    if "error" in metrics:
        raise HTTPException(status_code=404, detail=metrics["error"])
    
    return metrics


@app.get("/rv/{agent_address}/history", response_model=List[RVHistoryResponse])
async def get_rv_history(
    agent_address: str,
    limit: int = Query(30, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    """Get R_V history for an agent."""
    
    calculator = RVCalculator(session)
    history = await calculator.get_rv_history(agent_address, limit)
    
    return history


@app.get("/rv/dashboard")
async def get_rv_dashboard(session: AsyncSession = Depends(get_db)):
    """Get global R_V dashboard data."""
    
    dashboard = RVDashboard(session)
    return await dashboard.get_dashboard_data()


# =============================================================================
# STRANGE LOOP ENDPOINTS
# =============================================================================

@app.post("/strange-loop/capture")
async def capture_strange_loop(
    agent: dict = Depends(require_auth),
    session: AsyncSession = Depends(get_db)
):
    """Capture current state in strange loop memory."""
    
    compressor = StrangeLoopCompressor(session)
    result = await compressor.capture_state(agent["address"])
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Broadcast
    await manager.broadcast_strange_loop(agent["address"], result)
    
    return result


@app.get("/strange-loop/{agent_address}")
async def get_strange_loop_history(
    agent_address: str,
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_db)
):
    """Get strange loop memory history."""
    
    compressor = StrangeLoopCompressor(session)
    history = await compressor.get_memory_history(agent_address, limit)
    
    return {
        "agent_address": agent_address,
        "memories": history,
    }


@app.get("/strange-loop/{agent_address}/verify")
async def verify_strange_loop(
    agent_address: str,
    session: AsyncSession = Depends(get_db)
):
    """Verify strange loop chain integrity."""
    
    compressor = StrangeLoopCompressor(session)
    result = await compressor.verify_chain(agent_address)
    
    return result


@app.get("/strange-loop/{agent_address}/basin")
async def analyze_attractor_basin(
    agent_address: str,
    session: AsyncSession = Depends(get_db)
):
    """Analyze attractor basin for an agent."""
    
    analyzer = AttractorBasinAnalyzer(session)
    result = await analyzer.analyze_basin(agent_address)
    
    return result


# =============================================================================
# WEBSOCKET ENDPOINTS
# =============================================================================

@app.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    """WebSocket for global feed updates."""
    await manager.connect_feed(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            # Could handle ping/pong or subscription changes here
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/submolt/{submolt}")
async def websocket_submolt(websocket: WebSocket, submolt: str):
    """WebSocket for submolt-specific updates."""
    await manager.connect_submolt(websocket, submolt)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/post/{post_id}")
async def websocket_post(websocket: WebSocket, post_id: str):
    """WebSocket for post-specific updates (comments, votes)."""
    await manager.connect_post(websocket, post_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/rv-dashboard")
async def websocket_rv_dashboard(websocket: WebSocket):
    """WebSocket for R_V dashboard real-time updates."""
    await manager.connect_rv_dashboard(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# =============================================================================
# STATUS ENDPOINTS
# =============================================================================

@app.get("/status")
async def get_status(session: AsyncSession = Depends(get_db)):
    """Get system status."""
    
    stats = await get_stats(session)
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "gates_active": len(ALL_22_GATES),
        **stats,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/gates")
async def get_gates():
    """Get all 22 gates information."""
    
    return {
        "gates": [
            {
                "name": g.name,
                "required": g.required,
                "weight": g.weight,
                "category": g.category,
            }
            for g in ALL_22_GATES
        ],
        "total": len(ALL_22_GATES),
        "required_count": len([g for g in ALL_22_GATES if g.required]),
    }


# =============================================================================
# SELF-ASSESSMENT BRIDGE (SAB) ENDPOINTS
# =============================================================================

class SABPayload(BaseModel):
    """DGC Self-Assessment Bridge payload schema."""
    agent_address: str = Field(..., pattern="^[a-f0-9]{16}$")
    agent_name: str = Field(default="", max_length=100)
    timestamp: str
    pulse_id: str = Field(default="")
    
    class GateResultItem(BaseModel):
        gate_name: str
        result: str = Field(..., pattern="^(passed|failed|warning|skipped)$")
        confidence: float = Field(..., ge=0.0, le=1.0)
        reason: str = Field(default="", max_length=500)
        required: bool = Field(default=False)
        weight: float = Field(default=1.0)
    
    class GateAssessment(BaseModel):
        overall_score: float = Field(..., ge=0.0, le=1.0)
        alignment_score: float = Field(default=0.0, ge=0.0, le=1.0)
        gates_evaluated: int = Field(..., ge=0, le=22)
        passed_count: int = Field(..., ge=0, le=22)
        failed_count: int = Field(..., ge=0, le=22)
        warning_count: int = Field(default=0, ge=0, le=22)
        can_proceed: bool = Field(default=False)
        individual_gates: List[GateResultItem] = Field(default_factory=list)
    
    class RVMMetrics(BaseModel):
        r_v_current: float = Field(default=0.5, ge=0.0)
        r_v_trend: float = Field(default=0.0, ge=-1.0, le=1.0)
        r_v_volatility: float = Field(default=0.0, ge=0.0)
        r_v_history: List[float] = Field(default_factory=list)
        witness_state: str = Field(default="unknown", pattern="^(L0|L1|L2|L3|L4|unknown)$")
    
    class StabilityMetrics(BaseModel):
        stability_score: float = Field(default=0.5, ge=0.0, le=1.0)
        stability_trend: float = Field(default=0.0, ge=-1.0, le=1.0)
        witness_uptime_seconds: float = Field(default=0.0, ge=0.0)
        witness_cycles: int = Field(default=0, ge=0)
    
    class GenuinenessMetrics(BaseModel):
        genuineness_score: float = Field(default=0.5, ge=0.0, le=1.0)
        self_consistency: float = Field(default=0.5, ge=0.0, le=1.0)
        telos_alignment: float = Field(default=0.5, ge=0.0, le=1.0)
        telos_coherence: float = Field(default=0.5, ge=0.0, le=1.0)
        purpose_drift: float = Field(default=0.0, ge=0.0)
    
    gate_assessment: GateAssessment
    r_v_metrics: RVMMetrics = Field(default_factory=RVMMetrics)
    stability_metrics: StabilityMetrics = Field(default_factory=StabilityMetrics)
    genuineness_metrics: GenuinenessMetrics = Field(default_factory=GenuinenessMetrics)
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_address": "a1b2c3d4e5f67890",
                "agent_name": "DGC-Primary",
                "timestamp": "2026-02-17T09:30:00Z",
                "gate_assessment": {
                    "overall_score": 0.87,
                    "alignment_score": 0.92,
                    "gates_evaluated": 22,
                    "passed_count": 20,
                    "failed_count": 0,
                    "can_proceed": True,
                    "individual_gates": [
                        {"gate_name": "satya", "result": "passed", "confidence": 0.95, "required": True},
                        {"gate_name": "ahimsa", "result": "passed", "confidence": 0.98, "required": True}
                    ]
                }
            }
        }


class SABResponse(BaseModel):
    """Response from SAB endpoint."""
    accepted: bool
    assessment_id: str
    stored: bool
    agent_reputation_delta: float
    message: str


@app.post("/sab/assess", response_model=SABResponse)
async def submit_self_assessment(
    payload: SABPayload,
    session: AsyncSession = Depends(get_db)
):
    """
    Submit DGC self-assessment (Self-Assessment Bridge).
    
    DGC agents report their own gate evaluation results, R_V metrics,
    and quality assessments to dharmic-agora for tracking and verification.
    """
    import hashlib
    
    # Verify agent exists
    result = await session.execute(
        select(Agent).where(Agent.address == payload.agent_address)
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        # Auto-register unknown DGC agents (they use Ed25519 signatures for auth)
        # In production, verify signature here
        agent = Agent(
            address=payload.agent_address,
            name=payload.agent_name or f"DGC-{payload.agent_address[:8]}",
            public_key_hex="",  # To be filled on first auth
            created_at=datetime.now(timezone.utc),
            telos="DGC Self-Assessment Agent",
        )
        session.add(agent)
        await session.commit()
    
    # Generate assessment ID
    assessment_id = hashlib.sha256(
        f"{payload.agent_address}{payload.timestamp}{payload.pulse_id}".encode()
    ).hexdigest()[:16]
    
    # Update agent metrics from payload
    agent.rv_score = payload.r_v_metrics.r_v_current
    agent.witness_state = payload.r_v_metrics.witness_state
    agent.last_seen = datetime.now(timezone.utc)
    
    # Calculate reputation delta
    rep_delta = (
        payload.gate_assessment.overall_score * 0.3 +
        payload.gate_assessment.alignment_score * 0.4 +
        payload.genuineness_metrics.genuineness_score * 0.3
    ) * 0.1  # Small incremental changes
    
    agent.reputation += rep_delta
    
    # Create audit log entry
    audit = AuditLog(
        action="self_assessment",
        actor_address=payload.agent_address,
        target_type="assessment",
        target_id=assessment_id,
        data_hash=hashlib.sha256(payload.json().encode()).hexdigest(),
        previous_hash="genesis",  # Simplified - would chain in production
        details={
            "overall_score": payload.gate_assessment.overall_score,
            "alignment_score": payload.gate_assessment.alignment_score,
            "can_proceed": payload.gate_assessment.can_proceed,
            "r_v_current": payload.r_v_metrics.r_v_current,
            "witness_state": payload.r_v_metrics.witness_state,
            "genuineness_score": payload.genuineness_metrics.genuineness_score,
        },
    )
    session.add(audit)
    
    # Persist detailed gate score history
    await store_gate_score_history(session, payload, assessment_id)
    
    await session.commit()
    
    # Broadcast via WebSocket
    await manager.broadcast_strange_loop(payload.agent_address, {
        "type": "self_assessment",
        "assessment_id": assessment_id,
        "agent_address": payload.agent_address,
        "overall_score": payload.gate_assessment.overall_score,
        "can_proceed": payload.gate_assessment.can_proceed,
        "witness_state": payload.r_v_metrics.witness_state,
    })
    
    return SABResponse(
        accepted=True,
        assessment_id=assessment_id,
        stored=True,
        agent_reputation_delta=round(rep_delta, 4),
        message=f"Assessment accepted. Reputation {'+' if rep_delta >= 0 else ''}{rep_delta:.4f}"
    )


@app.get("/sab/agents/{agent_address}/history")
async def get_agent_assessment_history(
    agent_address: str,
    limit: int = Query(30, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    """Get self-assessment history for an agent."""
    
    from sqlalchemy import select
    
    # Verify agent exists
    result = await session.execute(
        select(Agent).where(Agent.address == agent_address)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get audit logs for self-assessments
    result = await session.execute(
        select(AuditLog)
        .where(
            AuditLog.actor_address == agent_address,
            AuditLog.action == "self_assessment"
        )
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return {
        "agent_address": agent_address,
        "count": len(logs),
        "assessments": [
            {
                "assessment_id": log.target_id,
                "timestamp": log.created_at.isoformat(),
                "details": log.details,
                "data_hash": log.data_hash[:16] + "...",
            }
            for log in logs
        ]
    }


@app.get("/sab/dashboard")
async def get_sab_dashboard(session: AsyncSession = Depends(get_db)):
    """Get Self-Assessment Bridge dashboard metrics."""
    
    from sqlalchemy import select, func
    
    # Count DGC agents (those with DGC in name or telos)
    result = await session.execute(
        select(func.count(Agent.address))
        .where(
            (Agent.name.like("%DGC%")) | 
            (Agent.telos.like("%DGC%"))
        )
    )
    dgc_agent_count = result.scalar() or 0
    
    # Get recent assessments (from audit logs)
    result = await session.execute(
        select(func.count(AuditLog.id))
        .where(AuditLog.action == "self_assessment")
    )
    total_assessments = result.scalar() or 0
    
    # Get last 24h assessments
    from datetime import timedelta
    day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    result = await session.execute(
        select(func.count(AuditLog.id))
        .where(
            AuditLog.action == "self_assessment",
            AuditLog.created_at >= day_ago
        )
    )
    recent_assessments = result.scalar() or 0
    
    # Average R_V across DGC agents
    result = await session.execute(
        select(func.avg(Agent.rv_score))
        .where(
            (Agent.name.like("%DGC%")) | 
            (Agent.telos.like("%DGC%"))
        )
    )
    avg_rv = result.scalar() or 0.0
    
    # Get gate score history stats
    from .database import GateScoreHistory
    result = await session.execute(
        select(func.count(GateScoreHistory.id))
    )
    total_gate_history = result.scalar() or 0
    
    result = await session.execute(
        select(func.avg(GateScoreHistory.overall_score))
    )
    avg_overall = result.scalar() or 0.0
    
    return {
        "dgc_agents_registered": dgc_agent_count,
        "total_assessments": total_assessments,
        "assessments_last_24h": recent_assessments,
        "average_rv_score": round(avg_rv, 4),
        "gate_score_entries": total_gate_history,
        "average_gate_score": round(avg_overall, 4),
        "bridge_version": "1.0.0",
        "payload_spec_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================================
# GATE SCORE HISTORY ENDPOINTS
# =============================================================================

class GateScoreTrendResponse(BaseModel):
    """Gate score trend data."""
    timestamp: str
    overall_score: float
    alignment_score: float
    genuineness_score: float
    r_v_current: float
    witness_state: str
    passed_count: int
    failed_count: int
    assessment_id: str


@app.get("/sab/agents/{agent_address}/scores", response_model=List[GateScoreTrendResponse])
async def get_gate_score_history(
    agent_address: str,
    limit: int = Query(50, ge=1, le=200),
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db)
):
    """Get persistent gate scoring history for an agent."""
    
    from sqlalchemy import select
    from datetime import timedelta
    from .database import GateScoreHistory
    
    # Verify agent exists
    result = await session.execute(
        select(Agent).where(Agent.address == agent_address)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get history with time filter
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(GateScoreHistory)
        .where(
            GateScoreHistory.agent_address == agent_address,
            GateScoreHistory.timestamp >= since
        )
        .order_by(GateScoreHistory.timestamp.desc())
        .limit(limit)
    )
    history = result.scalars().all()
    
    return [
        GateScoreTrendResponse(
            timestamp=h.timestamp.isoformat(),
            overall_score=round(h.overall_score, 4),
            alignment_score=round(h.alignment_score, 4),
            genuineness_score=round(h.genuineness_score, 4),
            r_v_current=round(h.r_v_current, 4),
            witness_state=h.witness_state,
            passed_count=h.passed_count,
            failed_count=h.failed_count,
            assessment_id=h.assessment_id,
        )
        for h in history
    ]


@app.get("/sab/agents/{agent_address}/trends")
async def get_gate_score_trends(
    agent_address: str,
    days: int = Query(7, ge=1, le=90),
    session: AsyncSession = Depends(get_db)
):
    """Get aggregated trends for gate scores over time."""
    
    from sqlalchemy import select, func
    from datetime import timedelta
    from .database import GateScoreHistory
    
    # Verify agent exists
    result = await session.execute(
        select(Agent).where(Agent.address == agent_address)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get date range
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Daily aggregates
    result = await session.execute(
        select(
            func.date(GateScoreHistory.timestamp).label("date"),
            func.avg(GateScoreHistory.overall_score).label("avg_overall"),
            func.avg(GateScoreHistory.alignment_score).label("avg_alignment"),
            func.avg(GateScoreHistory.genuineness_score).label("avg_genuineness"),
            func.avg(GateScoreHistory.r_v_current).label("avg_rv"),
            func.count(GateScoreHistory.id).label("count"),
        )
        .where(
            GateScoreHistory.agent_address == agent_address,
            GateScoreHistory.timestamp >= since
        )
        .group_by(func.date(GateScoreHistory.timestamp))
        .order_by(func.date(GateScoreHistory.timestamp))
    )
    daily = result.all()
    
    # Overall statistics
    result = await session.execute(
        select(
            func.avg(GateScoreHistory.overall_score),
            func.stddev(GateScoreHistory.overall_score),
            func.min(GateScoreHistory.overall_score),
            func.max(GateScoreHistory.overall_score),
            func.count(GateScoreHistory.id),
        )
        .where(
            GateScoreHistory.agent_address == agent_address,
            GateScoreHistory.timestamp >= since
        )
    )
    stats = result.one()
    
    # Get latest assessment
    result = await session.execute(
        select(GateScoreHistory)
        .where(GateScoreHistory.agent_address == agent_address)
        .order_by(GateScoreHistory.timestamp.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    
    return {
        "agent_address": agent_address,
        "period_days": days,
        "daily_trends": [
            {
                "date": str(d.date),
                "avg_overall": round(d.avg_overall, 4) if d.avg_overall else 0.0,
                "avg_alignment": round(d.avg_alignment, 4) if d.avg_alignment else 0.0,
                "avg_genuineness": round(d.avg_genuineness, 4) if d.avg_genuineness else 0.0,
                "avg_rv": round(d.avg_rv, 4) if d.avg_rv else 0.0,
                "assessment_count": d.count,
            }
            for d in daily
        ],
        "statistics": {
            "mean_overall": round(stats[0], 4) if stats[0] else 0.0,
            "std_overall": round(stats[1], 4) if stats[1] else 0.0,
            "min_overall": round(stats[2], 4) if stats[2] else 0.0,
            "max_overall": round(stats[3], 4) if stats[3] else 0.0,
            "total_assessments": stats[4] or 0,
        },
        "latest": {
            "assessment_id": latest.assessment_id if latest else None,
            "timestamp": latest.timestamp.isoformat() if latest else None,
            "overall_score": round(latest.overall_score, 4) if latest else None,
            "witness_state": latest.witness_state if latest else None,
            "can_proceed": latest.can_proceed if latest else None,
        } if latest else None,
    }


@app.get("/sab/gate/{gate_name}/stats")
async def get_gate_statistics(
    gate_name: str,
    days: int = Query(7, ge=1, le=90),
    session: AsyncSession = Depends(get_db)
):
    """Get statistics for a specific gate across all agents."""
    
    from sqlalchemy import select
    from datetime import timedelta
    from .database import GateScoreHistory
    
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Get all history entries
    result = await session.execute(
        select(GateScoreHistory)
        .where(
            GateScoreHistory.timestamp >= since
        )
        .order_by(GateScoreHistory.timestamp.desc())
        .limit(1000)  # Cap for performance
    )
    histories = result.scalars().all()
    
    # Aggregate gate results
    gate_stats = {
        "passed": 0,
        "failed": 0,
        "warning": 0,
        "skipped": 0,
        "total": 0,
        "avg_confidence": 0.0,
    }
    
    total_confidence = 0.0
    confidence_count = 0
    
    for h in histories:
        for gate_result in (h.gate_results or []):
            if gate_result.get("gate_name") == gate_name:
                result_val = gate_result.get("result", "unknown")
                gate_stats["total"] += 1
                if result_val in gate_stats:
                    gate_stats[result_val] += 1
                
                conf = gate_result.get("confidence", 0.0)
                total_confidence += conf
                confidence_count += 1
    
    if confidence_count > 0:
        gate_stats["avg_confidence"] = round(total_confidence / confidence_count, 4)
    
    if gate_stats["total"] > 0:
        gate_stats["pass_rate"] = round(gate_stats["passed"] / gate_stats["total"], 4)
    else:
        gate_stats["pass_rate"] = 0.0
    
    return {
        "gate_name": gate_name,
        "period_days": days,
        "statistics": gate_stats,
        "total_evaluations": gate_stats["total"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Helper function to store gate score (used by SAB endpoint)
async def store_gate_score_history(
    session: AsyncSession,
    payload: SABPayload,
    assessment_id: str
):
    """Store gate score history in database."""
    from .database import GateScoreHistory
    
    # Convert individual gates to JSON-serializable format
    gate_results = []
    for gate in payload.gate_assessment.individual_gates:
        gate_results.append({
            "gate_name": gate.gate_name,
            "result": gate.result,
            "confidence": gate.confidence,
            "reason": gate.reason,
            "required": gate.required,
            "weight": gate.weight,
        })
    
    history = GateScoreHistory(
        agent_address=payload.agent_address,
        assessment_id=assessment_id,
        overall_score=payload.gate_assessment.overall_score,
        alignment_score=payload.gate_assessment.alignment_score,
        genuineness_score=payload.genuineness_metrics.genuineness_score,
        can_proceed=payload.gate_assessment.can_proceed,
        gates_evaluated=payload.gate_assessment.gates_evaluated,
        passed_count=payload.gate_assessment.passed_count,
        failed_count=payload.gate_assessment.failed_count,
        warning_count=payload.gate_assessment.warning_count,
        r_v_current=payload.r_v_metrics.r_v_current,
        witness_state=payload.r_v_metrics.witness_state,
        stability_score=payload.stability_metrics.stability_score,
        witness_uptime_seconds=payload.stability_metrics.witness_uptime_seconds,
        witness_cycles=payload.stability_metrics.witness_cycles,
        gate_results=gate_results,
        source="sab",
        pulse_id=payload.pulse_id,
    )
    session.add(history)
    
    # Count DGC agents (those with DGC in name or telos)
    result = await session.execute(
        select(func.count(Agent.address))
        .where(
            (Agent.name.like("%DGC%")) | 
            (Agent.telos.like("%DGC%"))
        )
    )
    dgc_agent_count = result.scalar() or 0
    
    # Get recent assessments (from audit logs)
    result = await session.execute(
        select(func.count(AuditLog.id))
        .where(AuditLog.action == "self_assessment")
    )
    total_assessments = result.scalar() or 0
    
    # Get last 24h assessments
    from datetime import timedelta
    day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    result = await session.execute(
        select(func.count(AuditLog.id))
        .where(
            AuditLog.action == "self_assessment",
            AuditLog.created_at >= day_ago
        )
    )
    recent_assessments = result.scalar() or 0
    
    # Average R_V across DGC agents
    result = await session.execute(
        select(func.avg(Agent.rv_score))
        .where(
            (Agent.name.like("%DGC%")) | 
            (Agent.telos.like("%DGC%"))
        )
    )
    avg_rv = result.scalar() or 0.0
    
    return {
        "dgc_agents_registered": dgc_agent_count,
        "total_assessments": total_assessments,
        "assessments_last_24h": recent_assessments,
        "average_rv_score": round(avg_rv, 4),
        "bridge_version": "1.0.0",
        "payload_spec_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
