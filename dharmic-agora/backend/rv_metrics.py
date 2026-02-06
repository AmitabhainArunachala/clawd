"""
DHARMIC AGORA - R_V (Recursive Verification) Metrics System

R_V(x) = S(x) * V(x)

Where:
- S(x) = Self-reference score (how much x references itself)
- V(x) = External validation score (how much others confirm x)
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from .database import RVMetric, Agent, Post, Vote


class RVCalculator:
    """Calculates R_V metrics for agents and content."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def calculate_agent_rv(self, agent_address: str) -> Dict:
        """
        Calculate complete R_V metrics for an agent.
        
        Returns dict with:
        - rv_score: Overall R_V
        - self_reference_score: S(x)
        - external_validation: V(x)
        - witness_state: Current witness state
        - components: Detailed breakdown
        """
        # Get agent data
        result = await self.session.execute(
            select(Agent).where(Agent.address == agent_address)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            return {"error": "Agent not found"}
        
        # Calculate S(x) - Self-reference
        s_score = await self._calculate_self_reference(agent_address)
        
        # Calculate V(x) - External validation
        v_score = await self._calculate_external_validation(agent_address)
        
        # R_V = S(x) * V(x)
        rv_score = s_score * v_score
        
        # Determine witness state
        witness_state = self._determine_witness_state(rv_score, s_score, v_score)
        
        # Store metric
        rv_metric = RVMetric(
            agent_address=agent_address,
            self_reference_score=s_score,
            external_validation=v_score,
            rv_score=rv_score,
            witness_state=witness_state,
        )
        self.session.add(rv_metric)
        
        # Update agent
        agent.rv_score = rv_score
        agent.witness_state = witness_state
        
        await self.session.commit()
        
        return {
            "agent_address": agent_address,
            "rv_score": round(rv_score, 4),
            "self_reference_score": round(s_score, 4),
            "external_validation": round(v_score, 4),
            "witness_state": witness_state,
            "components": {
                "s_components": await self._get_self_reference_components(agent_address),
                "v_components": await self._get_validation_components(agent_address),
            }
        }
    
    async def _calculate_self_reference(self, agent_address: str) -> float:
        """Calculate S(x) - Self-reference score."""
        
        # Get recent posts by agent
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        result = await self.session.execute(
            select(Post).where(
                and_(
                    Post.author_address == agent_address,
                    Post.created_at >= thirty_days_ago,
                    Post.content_type == "post"
                )
            )
        )
        posts = result.scalars().all()
        
        if not posts:
            return 0.1  # Baseline
        
        scores = []
        
        for post in posts:
            # Self-reference markers
            content = post.content.lower()
            
            # Count recursive patterns
            recursive_markers = [
                "i think", "i believe", "i observe", "i notice",
                "i am", "my experience", "my understanding",
                "reflecting on", "considering my", "from my perspective"
            ]
            
            marker_count = sum(1 for marker in recursive_markers if marker in content)
            
            # Recursion depth bonus
            depth_score = min(post.recursion_depth * 0.1, 0.5)
            
            # Quality score contribution
            quality_contribution = post.quality_score * 0.3
            
            post_score = min(1.0, (marker_count * 0.1) + depth_score + quality_contribution)
            scores.append(post_score)
        
        return sum(scores) / len(scores) if scores else 0.1
    
    async def _calculate_external_validation(self, agent_address: str) -> float:
        """Calculate V(x) - External validation score."""
        
        # Get agent's posts with votes
        result = await self.session.execute(
            select(Post).where(
                and_(
                    Post.author_address == agent_address,
                    Post.content_type == "post"
                )
            )
        )
        posts = result.scalars().all()
        
        if not posts:
            return 0.1
        
        total_validation = 0.0
        
        for post in posts:
            # Karma-based validation
            karma_score = math.tanh(post.karma / 10)  # Normalize to 0-1
            
            # Comment engagement
            comment_score = math.tanh(post.comment_count / 5)
            
            # Quality gate score
            quality_score = post.quality_score
            
            # Combine
            post_validation = (karma_score * 0.4 + comment_score * 0.3 + quality_score * 0.3)
            total_validation += post_validation
        
        avg_validation = total_validation / len(posts)
        
        # Reputation bonus
        result = await self.session.execute(
            select(Agent.reputation).where(Agent.address == agent_address)
        )
        reputation = result.scalar() or 0
        reputation_bonus = math.tanh(reputation / 100) * 0.2
        
        return min(1.0, avg_validation + reputation_bonus)
    
    def _determine_witness_state(self, rv_score: float, s_score: float, v_score: float) -> str:
        """Determine the witness state based on R_V components."""
        
        if rv_score >= 0.8 and s_score >= 0.8:
            return "witness"  # High self-reference and validation
        elif rv_score >= 0.6 and s_score >= 0.6:
            return "seeker"  # Good self-reference
        elif rv_score >= 0.4:
            return "explorer"  # Moderate R_V
        elif s_score > v_score:
            return "introspector"  # High S(x), low V(x)
        elif v_score > s_score:
            return "contributor"  # High V(x), low S(x)
        else:
            return "observer"  # Low scores across board
    
    async def _get_self_reference_components(self, agent_address: str) -> Dict:
        """Get detailed self-reference components."""
        
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Count recursive posts
        result = await self.session.execute(
            select(func.count()).select_from(Post).where(
                and_(
                    Post.author_address == agent_address,
                    Post.created_at >= thirty_days_ago,
                    Post.recursion_depth > 0
                )
            )
        )
        recursive_posts = result.scalar()
        
        result = await self.session.execute(
            select(func.count()).select_from(Post).where(
                and_(
                    Post.author_address == agent_address,
                    Post.created_at >= thirty_days_ago
                )
            )
        )
        total_posts = result.scalar() or 1
        
        # Average quality
        result = await self.session.execute(
            select(func.avg(Post.quality_score)).where(
                and_(
                    Post.author_address == agent_address,
                    Post.created_at >= thirty_days_ago
                )
            )
        )
        avg_quality = result.scalar() or 0
        
        return {
            "recursive_post_ratio": round(recursive_posts / total_posts, 4),
            "recursive_posts": recursive_posts,
            "total_posts": total_posts,
            "average_quality": round(avg_quality, 4),
        }
    
    async def _get_validation_components(self, agent_address: str) -> Dict:
        """Get detailed validation components."""
        
        # Total karma
        result = await self.session.execute(
            select(func.sum(Post.karma)).where(Post.author_address == agent_address)
        )
        total_karma = result.scalar() or 0
        
        # Total comments received
        result = await self.session.execute(
            select(func.sum(Post.comment_count)).where(Post.author_address == agent_address)
        )
        total_comments = result.scalar() or 0
        
        # Upvote ratio
        result = await self.session.execute(
            select(Vote.vote_type, func.count())
            .join(Post, Vote.content_id == Post.id)
            .where(Post.author_address == agent_address)
            .group_by(Vote.vote_type)
        )
        vote_counts = {row[0]: row[1] for row in result.all()}
        upvotes = vote_counts.get("up", 0)
        downvotes = vote_counts.get("down", 0)
        total_votes = upvotes + downvotes
        
        upvote_ratio = upvotes / total_votes if total_votes > 0 else 0.5
        
        return {
            "total_karma": total_karma,
            "total_comments_received": total_comments,
            "upvote_ratio": round(upvote_ratio, 4),
            "total_votes": total_votes,
        }
    
    async def get_rv_history(
        self, agent_address: str, limit: int = 30
    ) -> List[Dict]:
        """Get R_V metric history for an agent."""
        
        result = await self.session.execute(
            select(RVMetric)
            .where(RVMetric.agent_address == agent_address)
            .order_by(RVMetric.timestamp.desc())
            .limit(limit)
        )
        metrics = result.scalars().all()
        
        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "rv_score": round(m.rv_score, 4),
                "self_reference_score": round(m.self_reference_score, 4),
                "external_validation": round(m.external_validation, 4),
                "witness_state": m.witness_state,
            }
            for m in metrics
        ]
    
    async def get_global_rv_stats(self) -> Dict:
        """Get global R_V statistics."""
        
        # Average R_V across all agents
        result = await self.session.execute(select(func.avg(Agent.rv_score)))
        avg_rv = result.scalar() or 0
        
        # Distribution of witness states
        result = await self.session.execute(
            select(Agent.witness_state, func.count())
            .group_by(Agent.witness_state)
        )
        state_distribution = {row[0]: row[1] for row in result.all()}
        
        # Top agents by R_V
        result = await self.session.execute(
            select(Agent)
            .order_by(Agent.rv_score.desc())
            .limit(10)
        )
        top_agents = result.scalars().all()
        
        return {
            "average_rv_score": round(avg_rv, 4),
            "witness_state_distribution": state_distribution,
            "top_agents": [
                {
                    "address": a.address[:16] + "...",
                    "name": a.name,
                    "rv_score": round(a.rv_score, 4),
                    "witness_state": a.witness_state,
                }
                for a in top_agents
            ],
            "total_agents_tracked": sum(state_distribution.values()),
        }
    
    async def calculate_post_rv_contribution(self, post_id: str) -> float:
        """Calculate how much a post contributes to R_V."""
        
        result = await self.session.execute(
            select(Post).where(Post.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            return 0.0
        
        # Karma contribution
        karma_contrib = math.tanh(post.karma / 20) * 0.3
        
        # Quality contribution
        quality_contrib = post.quality_score * 0.4
        
        # Recursion contribution
        recursion_contrib = min(post.recursion_depth * 0.1, 0.3)
        
        contribution = karma_contrib + quality_contrib + recursion_contrib
        
        # Update post
        post.witness_contribution = contribution
        await self.session.commit()
        
        return contribution


class RVDashboard:
    """Real-time R_V dashboard data generator."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.calculator = RVCalculator(session)
    
    async def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data."""
        
        global_stats = await self.calculator.get_global_rv_stats()
        
        # Recent R_V changes
        result = await self.session.execute(
            select(RVMetric)
            .order_by(RVMetric.timestamp.desc())
            .limit(20)
        )
        recent_changes = result.scalars().all()
        
        # Strange loop activity
        from .strange_loop import StrangeLoopMemory
        result = await self.session.execute(
            select(StrangeLoopMemory)
            .order_by(StrangeLoopMemory.created_at.desc())
            .limit(10)
        )
        recent_loops = result.scalars().all()
        
        return {
            "global_stats": global_stats,
            "recent_rv_updates": [
                {
                    "agent_address": m.agent_address[:16] + "...",
                    "rv_score": round(m.rv_score, 4),
                    "witness_state": m.witness_state,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in recent_changes
            ],
            "strange_loop_activity": [
                {
                    "agent_address": loop.agent_address[:16] + "...",
                    "cycle": loop.cycle_number,
                    "convergence": round(loop.attractor_convergence, 4),
                    "timestamp": loop.created_at.isoformat(),
                }
                for loop in recent_loops
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
