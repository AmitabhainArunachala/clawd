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
        attestation = Attestation(
            hash="a" * 64,  # SHA256 hex hash
            timestamp=1234567890.0,
            config={"timeout": 30},
            metrics={"cpu_time": 0.5}
        )
        
        assert attestation.hash == "a" * 64
        assert attestation.timestamp == 1234567890.0
        assert attestation.config == {"timeout": 30}
        assert attestation.metrics == {"cpu_time": 0.5}
        assert attestation.signature is None
    
    def test_verify_valid_hash(self):
        """Test that verify() returns True for valid hash."""
        import time
        attestation = Attestation(
            hash="a" * 64,  # Valid 64-char hex
            timestamp=time.time(),  # Current time
            config={},
            metrics={}
        )
        
        assert attestation.verify() is True
    
    def test_verify_invalid_hash(self):
        """Test that verify() returns False for invalid hash."""
        attestation = Attestation(
            hash="invalid_hash",  # Invalid
            timestamp=1234567890.0,
            config={},
            metrics={}
        )
        
        assert attestation.verify() is False
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        attestation = Attestation(
            hash="b" * 64,
            timestamp=1234567890.0,
            config={"env": "test"},
            metrics={"cpu": 0.5},
            signature="sig_123"
        )
        
        data = attestation.to_dict()
        assert data["hash"] == "b" * 64
        assert data["timestamp"] == 1234567890.0
        assert data["config"] == {"env": "test"}
        assert data["metrics"] == {"cpu": 0.5}
        assert data["signature"] == "sig_123"
