"""Agent identity management for OACP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AgentIdentity:
    """Represents an agent's cryptographic identity.
    
    Attributes:
        agent_id: Unique identifier for the agent
        public_key: Agent's public key for verification
        created_at: Timestamp when identity was created
        metadata: Optional additional identity metadata
    """
    
    agent_id: str
    public_key: Optional[str] = None
    created_at: str = ""
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Set default timestamp if not provided."""
        if not self.created_at:
            object.__setattr__(
                self, 
                'created_at', 
                datetime.now().isoformat()
            )
    
    @classmethod
    def create(
        cls, 
        agent_id: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentIdentity:
        """Create a new agent identity.

        Args:
            agent_id: Unique identifier for the agent
            metadata: Optional metadata dictionary

        Returns:
            New AgentIdentity instance

        Raises:
            ValueError: If agent_id is empty or None
        """
        if not agent_id:
            raise ValueError("agent_id cannot be empty or None")
        
        return cls(
            agent_id=agent_id,
            metadata=metadata or {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert identity to dictionary."""
        return {
            "agent_id": self.agent_id,
            "public_key": self.public_key,
            "created_at": self.created_at,
            "metadata": self.metadata or {}
        }
