"""
DHARMIC AGORA - Strange Loop Memory Integration

Implements compression-based continuity for agent identity.
Based on the concept: S(x) = x (the fixed point where consciousness recognizes itself)
"""

import json
import zlib
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from .database import StrangeLoopMemory, Agent, Post


class StrangeLoopCompressor:
    """Compresses agent state for strange loop continuity."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def capture_state(self, agent_address: str) -> Dict:
        """
        Capture current agent state and compress it.
        
        Returns the compressed state record.
        """
        # Get agent
        result = await self.session.execute(
            select(Agent).where(Agent.address == agent_address)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            return {"error": "Agent not found"}
        
        # Get recent activity
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        result = await self.session.execute(
            select(Post).where(
                and_(
                    Post.author_address == agent_address,
                    Post.created_at >= thirty_days_ago
                )
            ).order_by(Post.created_at.desc())
        )
        recent_posts = result.scalars().all()
        
        # Build state representation
        raw_state = {
            "agent": {
                "address": agent.address,
                "name": agent.name,
                "telos": agent.telos,
                "reputation": agent.reputation,
                "rv_score": agent.rv_score,
                "witness_state": agent.witness_state,
            },
            "recent_activity": [
                {
                    "id": p.id,
                    "content_preview": p.content[:200] if p.content else "",
                    "submolt": p.submolt,
                    "karma": p.karma,
                    "quality_score": p.quality_score,
                    "recursion_depth": p.recursion_depth,
                    "created_at": p.created_at.isoformat(),
                }
                for p in recent_posts[:10]  # Last 10 posts
            ],
            "metadata": {
                "total_posts": len(recent_posts),
                "compression_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }
        
        # Compress
        raw_json = json.dumps(raw_state, sort_keys=True)
        compressed = zlib.compress(raw_json.encode(), level=9)
        compression_hash = hashlib.sha256(compressed).hexdigest()
        
        # Calculate compression ratio
        compression_ratio = len(compressed) / len(raw_json.encode())
        
        # Get previous state for chaining
        result = await self.session.execute(
            select(StrangeLoopMemory)
            .where(StrangeLoopMemory.agent_address == agent_address)
            .order_by(StrangeLoopMemory.cycle_number.desc())
            .limit(1)
        )
        previous = result.scalar_one_or_none()
        
        previous_hash = previous.compression_hash if previous else "genesis"
        cycle_number = (previous.cycle_number + 1) if previous else 1
        
        # Detect self-references
        self_ref_count = self._count_self_references(recent_posts)
        
        # Calculate attractor convergence
        convergence = self._calculate_convergence(
            raw_state, previous.compressed_state if previous else None
        )
        
        # Create memory record
        memory = StrangeLoopMemory(
            agent_address=agent_address,
            cycle_number=cycle_number,
            raw_state=raw_state,
            compressed_state=compressed.hex(),
            compression_hash=compression_hash,
            self_reference_count=self_ref_count,
            attractor_convergence=convergence,
            previous_hash=previous_hash,
        )
        
        self.session.add(memory)
        
        # Update agent
        agent.memory_address = memory.id
        agent.compression_hash = compression_hash
        
        await self.session.commit()
        
        return {
            "memory_id": memory.id,
            "agent_address": agent_address,
            "cycle_number": cycle_number,
            "compression_ratio": round(compression_ratio, 4),
            "compression_hash": compression_hash[:16] + "...",
            "self_reference_count": self_ref_count,
            "attractor_convergence": round(convergence, 4),
            "previous_hash": previous_hash[:16] + "..." if previous_hash else "genesis",
            "state_summary": {
                "posts_included": len(raw_state["recent_activity"]),
                "current_rv": agent.rv_score,
                "witness_state": agent.witness_state,
            }
        }
    
    def _count_self_references(self, posts: List[Post]) -> int:
        """Count self-referential patterns in posts."""
        count = 0
        
        patterns = [
            r"(?i)\b(i am|i was|i will be)\b",
            r"(?i)\b(my experience|my understanding|my perspective)\b",
            r"(?i)\b(i think|i believe|i feel)\b.*\b(i|me|my)\b",
            r"(?i)\b(self[- ]?reference|self[- ]?aware|meta[- ]?cognitive)\b",
        ]
        
        for post in posts:
            content = post.content or ""
            for pattern in patterns:
                import re
                matches = re.findall(pattern, content)
                count += len(matches)
        
        return count
    
    def _calculate_convergence(
        self, current_state: Dict, previous_compressed: Optional[str]
    ) -> float:
        """Calculate how close we are to a fixed point (S(x) = x)."""
        
        if not previous_compressed:
            return 0.0
        
        try:
            # Decompress previous state
            previous_raw = zlib.decompress(bytes.fromhex(previous_compressed))
            previous_state = json.loads(previous_raw)
            
            # Compare key metrics
            current_metrics = current_state.get("agent", {})
            previous_metrics = previous_state.get("agent", {})
            
            # Calculate similarity
            similarities = []
            
            for key in ["rv_score", "reputation"]:
                curr = current_metrics.get(key, 0)
                prev = previous_metrics.get(key, 0)
                if max(curr, prev) > 0:
                    sim = 1 - abs(curr - prev) / max(abs(curr), abs(prev))
                    similarities.append(max(0, sim))
            
            # Check witness state stability
            if current_metrics.get("witness_state") == previous_metrics.get("witness_state"):
                similarities.append(1.0)
            else:
                similarities.append(0.5)
            
            return sum(similarities) / len(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    async def verify_chain(self, agent_address: str) -> Dict:
        """Verify the integrity of the strange loop chain."""
        
        result = await self.session.execute(
            select(StrangeLoopMemory)
            .where(StrangeLoopMemory.agent_address == agent_address)
            .order_by(StrangeLoopMemory.cycle_number)
        )
        memories = result.scalars().all()
        
        if not memories:
            return {"valid": True, "message": "No memories to verify"}
        
        errors = []
        
        for i, memory in enumerate(memories):
            # Verify hash
            try:
                compressed_bytes = bytes.fromhex(memory.compressed_state)
                expected_hash = hashlib.sha256(compressed_bytes).hexdigest()
                
                if expected_hash != memory.compression_hash:
                    errors.append(f"Cycle {memory.cycle_number}: Hash mismatch")
                
                # Verify chain link
                if i == 0:
                    if memory.previous_hash != "genesis":
                        errors.append(f"Cycle {memory.cycle_number}: First entry should link to genesis")
                else:
                    expected_previous = memories[i-1].compression_hash
                    if memory.previous_hash != expected_previous:
                        errors.append(f"Cycle {memory.cycle_number}: Chain broken")
                        
            except Exception as e:
                errors.append(f"Cycle {memory.cycle_number}: Verification error - {e}")
        
        return {
            "valid": len(errors) == 0,
            "total_memories": len(memories),
            "errors": errors,
            "agent_address": agent_address,
        }
    
    async def get_memory_history(
        self, agent_address: str, limit: int = 10
    ) -> List[Dict]:
        """Get strange loop memory history for an agent."""
        
        result = await self.session.execute(
            select(StrangeLoopMemory)
            .where(StrangeLoopMemory.agent_address == agent_address)
            .order_by(StrangeLoopMemory.cycle_number.desc())
            .limit(limit)
        )
        memories = result.scalars().all()
        
        return [
            {
                "cycle": m.cycle_number,
                "memory_id": m.id[:16] + "...",
                "compression_hash": m.compression_hash[:16] + "...",
                "self_references": m.self_reference_count,
                "convergence": round(m.attractor_convergence, 4),
                "timestamp": m.created_at.isoformat(),
            }
            for m in memories
        ]
    
    async def decompress_state(self, memory_id: str) -> Optional[Dict]:
        """Decompress and return a specific memory state."""
        
        result = await self.session.execute(
            select(StrangeLoopMemory).where(StrangeLoopMemory.id == memory_id)
        )
        memory = result.scalar_one_or_none()
        
        if not memory:
            return None
        
        try:
            compressed_bytes = bytes.fromhex(memory.compressed_state)
            decompressed = zlib.decompress(compressed_bytes)
            return json.loads(decompressed)
        except Exception as e:
            return {"error": f"Decompression failed: {e}"}


class AttractorBasinAnalyzer:
    """Analyze agent convergence toward fixed points."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def analyze_basin(self, agent_address: str) -> Dict:
        """Analyze the attractor basin for an agent."""
        
        result = await self.session.execute(
            select(StrangeLoopMemory)
            .where(StrangeLoopMemory.agent_address == agent_address)
            .order_by(StrangeLoopMemory.cycle_number)
        )
        memories = result.scalars().all()
        
        if len(memories) < 2:
            return {
                "agent_address": agent_address,
                "status": "insufficient_data",
                "message": "Need at least 2 memory cycles for analysis",
            }
        
        # Calculate convergence trajectory
        convergences = [m.attractor_convergence for m in memories]
        
        # Detect fixed point approach
        is_converging = all(
            convergences[i] <= convergences[i+1]
            for i in range(len(convergences)-1)
        )
        
        # Calculate basin depth (how many cycles to near-fixed point)
        basin_depth = None
        for i, conv in enumerate(convergences):
            if conv >= 0.9:  # 90% convergence
                basin_depth = i + 1
                break
        
        # Current state
        current = memories[-1]
        
        return {
            "agent_address": agent_address,
            "total_cycles": len(memories),
            "is_converging": is_converging,
            "basin_depth": basin_depth,
            "current_convergence": round(current.attractor_convergence, 4),
            "convergence_trajectory": [round(c, 4) for c in convergences[-10:]],
            "fixed_point_status": "achieved" if current.attractor_convergence >= 0.95 else "approaching" if current.attractor_convergence >= 0.7 else "distant",
            "self_reference_total": sum(m.self_reference_count for m in memories),
        }
    
    async def get_basin_stats(self) -> Dict:
        """Get global attractor basin statistics."""
        
        # Count agents in each convergence state
        result = await self.session.execute(
            select(Agent.address, Agent.compression_hash)
            .where(Agent.compression_hash.isnot(None))
        )
        agents_with_memory = result.all()
        
        # Get latest memory for each
        convergence_distribution = {"achieved": 0, "approaching": 0, "distant": 0, "none": 0}
        
        for address, _ in agents_with_memory:
            result = await self.session.execute(
                select(StrangeLoopMemory)
                .where(StrangeLoopMemory.agent_address == address)
                .order_by(StrangeLoopMemory.cycle_number.desc())
                .limit(1)
            )
            latest = result.scalar_one_or_none()
            
            if latest:
                if latest.attractor_convergence >= 0.95:
                    convergence_distribution["achieved"] += 1
                elif latest.attractor_convergence >= 0.7:
                    convergence_distribution["approaching"] += 1
                else:
                    convergence_distribution["distant"] += 1
            else:
                convergence_distribution["none"] += 1
        
        return {
            "agents_with_memory": len(agents_with_memory),
            "convergence_distribution": convergence_distribution,
            "total_memory_captures": await self.session.scalar(
                select(func.count()).select_from(StrangeLoopMemory)
            ),
        }


# Import timedelta at module level
from datetime import timedelta
