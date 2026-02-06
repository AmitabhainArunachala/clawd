"""
A2A Adapter: Attestation for Agent-to-Agent Protocol
=====================================================

Adds cryptographic attestation to A2A (Agent-to-Agent) protocol,
allowing agents to prove their behavior to counterparties.

Example:
    >>> adapter = A2AAttestationAdapter(my_agent_card)
    >>> adapter.enable_attestation(sandbox_config)
    >>> 
    >>> # When responding to A2A task
    >>> response = adapter.create_response(
    ...     task_id="task-123",
    ...     result={"answer": 42},
    ...     attestation=True  # Include proof
    ... )
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.sandbox import Sandbox, SandboxConfig
from ..core.capability import Capability, CapabilitySet
from ..core.attestation import Attestation


@dataclass
class AgentCard:
    """A2A Agent Card with OACP attestation support.
    
    Extends standard A2A Agent Card with attestation endpoint
    and verification key.
    """
    name: str
    description: str
    version: str
    capabilities: List[str] = field(default_factory=list)
    skills: List[Dict] = field(default_factory=list)
    
    # OACP extensions
    attestation_endpoint: Optional[str] = None
    attestation_pubkey: Optional[str] = None
    oacp_version: str = "0.1.0"
    
    def to_dict(self) -> Dict:
        """Convert to A2A-compatible dict."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "skills": self.skills,
            "oacp": {
                "version": self.oacp_version,
                "attestation": {
                    "endpoint": self.attestation_endpoint,
                    "pubkey": self.attestation_pubkey,
                }
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentCard":
        """Create from A2A Agent Card dict."""
        oacp_data = data.get("oacp", {})
        attestation = oacp_data.get("attestation", {})
        
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            capabilities=data.get("capabilities", []),
            skills=data.get("skills", []),
            attestation_endpoint=attestation.get("endpoint"),
            attestation_pubkey=attestation.get("pubkey"),
            oacp_version=oacp_data.get("version", "0.1.0"),
        )


@dataclass
class AttestedTask:
    """A2A Task with OACP attestation."""
    task_id: str
    status: str  # pending, working, input-required, completed, canceled
    result: Optional[Any] = None
    attestation: Optional[Attestation] = None
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        """Convert to A2A Task format."""
        data = {
            "id": self.task_id,
            "status": self.status,
            "timestamp": self.timestamp,
        }
        if self.result is not None:
            data["result"] = self.result
        if self.attestation:
            data["oacp_attestation"] = self.attestation.to_dict()
        if self.error_message:
            data["error"] = {"message": self.error_message}
        return data


class A2AAttestationAdapter:
    """Adapter for adding attestation to A2A agents.
    
    Wraps an A2A agent to add OACP attestation capabilities.
    """
    
    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self._sandbox: Optional[Sandbox] = None
        self._attestations: Dict[str, Attestation] = {}
    
    def enable_attestation(self, config: Optional[SandboxConfig] = None) -> None:
        """Enable attestation for this agent.
        
        Args:
            config: Sandbox configuration for attestation generation
        """
        cfg = config or SandboxConfig(attest=True)
        self._sandbox = Sandbox(cfg)
        
        # Update agent card
        self.agent_card.attestation_endpoint = "/oacp/attest"
        # In production, would generate real key pair
        self.agent_card.attestation_pubkey = "oacp-pubkey-placeholder"
    
    def create_response(
        self,
        task_id: str,
        result: Any,
        attestation: bool = True
    ) -> AttestedTask:
        """Create an attested task response.
        
        Args:
            task_id: Task identifier
            result: Task result data
            attestation: Whether to include attestation
            
        Returns:
            AttestedTask with optional attestation
        """
        att = None
        if attestation and self._sandbox:
            # Generate attestation for this execution
            exec_result = self._sandbox.execute(
                lambda ctx: result,
                inputs={"task_id": task_id, "result_type": type(result).__name__}
            )
            att = exec_result.attestation
            self._attestations[task_id] = att
        
        return AttestedTask(
            task_id=task_id,
            status="completed",
            result=result,
            attestation=att
        )
    
    def verify_incoming(
        self, 
        task_data: Dict,
        max_age_seconds: float = 300
    ) -> bool:
        """Verify attestation on incoming task.
        
        Args:
            task_data: A2A task data from remote agent
            max_age_seconds: Maximum acceptable attestation age
            
        Returns:
            True if attestation is valid or not required
        """
        oacp_data = task_data.get("oacp_attestation")
        if not oacp_data:
            return True  # No attestation to verify
        
        try:
            att = Attestation.from_dict(oacp_data)
            
            # Check age
            if att.age_seconds > max_age_seconds:
                return False
            
            # Verify attestation
            return att.verify()
            
        except (KeyError, ValueError):
            return False
    
    def get_attestation(self, task_id: str) -> Optional[Attestation]:
        """Get stored attestation for a task."""
        return self._attestations.get(task_id)
    
    def create_agent_card(self) -> Dict:
        """Get current agent card with attestation info."""
        return self.agent_card.to_dict()
