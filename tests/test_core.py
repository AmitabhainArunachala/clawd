"""
Unit tests for OACP core module.
"""

from __future__ import annotations

import pytest

from oacp.core import AgentIdentity, Attestation


class TestAgentIdentity:
    """Tests for AgentIdentity class."""
    
    def test_create_basic_identity(self):
        """Test creating a basic identity."""
        identity = AgentIdentity.create("agent-001")
        assert identity.agent_id == "agent-001"
        assert identity.public_key is None
        assert identity.created_at != ""
        assert identity.metadata == {}
    
    def test_create_with_metadata(self):
        """Test creating identity with metadata."""
        meta = {"role": "test", "team": "alpha"}
        identity = AgentIdentity.create("agent-002", metadata=meta)
        assert identity.metadata == meta
    
    def test_create_invalid_agent_id(self):
        """Test that empty agent_id raises error."""
        with pytest.raises(ValueError):
            AgentIdentity.create("")
        
        with pytest.raises(ValueError):
            AgentIdentity.create(None)  # type: ignore
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        identity = AgentIdentity.create("agent-003", metadata={"key": "value"})
        data = identity.to_dict()
        
        assert data["agent_id"] == "agent-003"
        assert data["metadata"] == {"key": "value"}
        assert "created_at" in data
    
    def test_frozen_dataclass(self):
        """Test that identity is immutable."""
        identity = AgentIdentity.create("agent-004")
        
        with pytest.raises(AttributeError):
            identity.agent_id = "new-id"


class TestAttestation:
    """Tests for Attestation class."""
    
    def test_create_attestation(self):
        """Test creating an attestation."""
        identity = AgentIdentity.create("agent-001")
        attestation = Attestation(
            identity=identity,
            evidence="test_evidence_123",
            verifier="test_verifier"
        )
        
        assert attestation.identity.agent_id == "agent-001"
        assert attestation.evidence == "test_evidence_123"
        assert attestation.verifier == "test_verifier"
        assert attestation.timestamp != ""
    
    def test_verify_placeholder(self):
        """Test that verify() returns True (placeholder)."""
        identity = AgentIdentity.create("agent-001")
        attestation = Attestation(
            identity=identity,
            evidence="test_evidence"
        )
        
        # Currently returns True as placeholder
        assert attestation.verify() is True
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        identity = AgentIdentity.create("agent-001", metadata={"env": "test"})
        attestation = Attestation(
            identity=identity,
            evidence="evidence_data",
            verifier="verifier_1"
        )
        
        data = attestation.to_dict()
        assert data["evidence"] == "evidence_data"
        assert data["verifier"] == "verifier_1"
        assert data["identity"]["agent_id"] == "agent-001"
