"""Tests for collaboration protocol."""
import pytest
from unittest.mock import MagicMock, patch
from collab_protocol import CollabSession, CollabState, CollabResponder

class TestCollabSession:
    def test_init_creates_session_id(self):
        with patch('collab_protocol.ChaiwalaBus'):
            session = CollabSession("agent_a", "agent_b", "test_session")
            assert session.session_id.startswith("test_session_")
            assert session.state == CollabState.PROPOSED
    
    def test_cannot_begin_iteration_before_acceptance(self):
        with patch('collab_protocol.ChaiwalaBus'):
            session = CollabSession("agent_a", "agent_b", "test")
            with pytest.raises(RuntimeError):
                session.begin_iteration(0, "proposal")
    
    def test_audit_log_records_events(self):
        with patch('collab_protocol.ChaiwalaBus'):
            session = CollabSession("agent_a", "agent_b", "test")
            assert len(session.audit_log) == 1
            assert session.audit_log[0]["event"] == "SESSION_INIT"

class TestCollabProtocolIntegration:
    """These require actual Chaiwala bus - skip in CI."""
    
    @pytest.mark.skip(reason="Requires live Chaiwala bus")
    def test_full_collaboration_flow(self):
        # Would test actual message flow
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
