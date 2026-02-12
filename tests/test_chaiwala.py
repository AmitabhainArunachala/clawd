"""
Unit tests for Chaiwala message bus.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# Import with proper path handling
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "chaiwala_workspace"))

from chaiwala import (
    ChaiwalaBus,
    ChaiwalaMessage,
    ChaiwalaError,
    DatabaseError,
    MessageError,
)


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        os.unlink(db_path)


@pytest.fixture
def bus(temp_db_path: Path) -> ChaiwalaBus:
    """Create a test bus instance."""
    return ChaiwalaBus("test_agent", db_path=temp_db_path)


@pytest.fixture
def second_bus(temp_db_path: Path) -> ChaiwalaBus:
    """Create a second test bus instance for cross-agent testing."""
    return ChaiwalaBus("second_agent", db_path=temp_db_path)


class TestChaiwalaMessage:
    """Tests for ChaiwalaMessage dataclass."""
    
    def test_message_creation(self):
        """Test creating a ChaiwalaMessage."""
        msg = ChaiwalaMessage(
            id=1,
            to_agent="recipient",
            from_agent="sender",
            body="test body",
            subject="test subject",
            priority="normal",
            status="unread",
            created_at="2026-02-12T00:00:00"
        )
        assert msg.id == 1
        assert msg.to_agent == "recipient"
        assert msg.from_agent == "sender"
    
    def test_message_from_row(self):
        """Test creating message from sqlite Row."""
        # Create a mock row
        class MockRow:
            def __getitem__(self, key):
                data = {
                    "id": 1,
                    "to_agent": "recipient",
                    "from_agent": "sender",
                    "body": "body",
                    "subject": "subject",
                    "priority": "high",
                    "status": "unread",
                    "created_at": "2026-02-12T00:00:00"
                }
                return data[key]
        
        row = MockRow()
        msg = ChaiwalaMessage.from_row(row)
        assert msg.id == 1
        assert msg.priority == "high"


class TestChaiwalaBusInitialization:
    """Tests for ChaiwalaBus initialization."""
    
    def test_bus_creation(self, temp_db_path: Path):
        """Test creating a bus instance."""
        bus = ChaiwalaBus("agent_1", db_path=temp_db_path)
        assert bus.agent_id == "agent_1"
        assert bus.db_path == temp_db_path
    
    def test_default_db_path(self):
        """Test that default db path is in home directory."""
        bus = ChaiwalaBus("test_agent")
        expected = Path.home() / ".chaiwala" / "messages.db"
        assert bus.db_path == expected
    
    def test_db_directory_created(self, temp_db_path: Path):
        """Test that database directory is created."""
        nested_path = temp_db_path.parent / "nested" / "deep" / "test.db"
        bus = ChaiwalaBus("agent_1", db_path=nested_path)
        assert nested_path.parent.exists()
    
    def test_invalid_db_path(self):
        """Test handling of invalid database path."""
        with pytest.raises(DatabaseError):
            # Use a path that can't be created (root directory on Unix)
            ChaiwalaBus("agent_1", db_path=Path("/nonexistent/path/test.db"))


class TestChaiwalaBusSend:
    """Tests for sending messages."""
    
    def test_send_basic_message(self, bus: ChaiwalaBus):
        """Test sending a basic message."""
        msg_id = bus.send("recipient", "Hello!")
        assert isinstance(msg_id, int)
        assert msg_id > 0
    
    def test_send_with_subject(self, bus: ChaiwalaBus):
        """Test sending with custom subject."""
        msg_id = bus.send("recipient", "Hello!", subject="TEST")
        assert msg_id > 0
    
    def test_send_with_priority(self, bus: ChaiwalaBus):
        """Test sending with different priorities."""
        for priority in ["low", "normal", "high"]:
            msg_id = bus.send("recipient", "Hello!", priority=priority)
            assert msg_id > 0
    
    def test_send_invalid_priority(self, bus: ChaiwalaBus):
        """Test sending with invalid priority raises error."""
        with pytest.raises(ValueError):
            bus.send("recipient", "Hello!", priority="invalid")
    
    def test_send_json_message(self, bus: ChaiwalaBus):
        """Test sending JSON message."""
        payload = {"key": "value", "number": 42}
        msg_id = bus.send_json("recipient", payload)
        assert msg_id > 0
    
    def test_send_json_invalid_payload(self, bus: ChaiwalaBus):
        """Test sending invalid JSON raises error."""
        # Objects that can't be JSON serialized
        with pytest.raises(MessageError):
            bus.send_json("recipient", {"func": lambda x: x})


class TestChaiwalaBusReceive:
    """Tests for receiving messages."""
    
    def test_receive_empty(self, bus: ChaiwalaBus):
        """Test receiving when no messages."""
        messages = bus.receive()
        assert messages == []
    
    def test_receive_message(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test receiving a sent message."""
        # Send message from second_bus to bus
        second_bus.send("test_agent", "Hello there!")
        
        # Receive with bus
        messages = bus.receive()
        assert len(messages) == 1
        assert messages[0].body == "Hello there!"
        assert messages[0].from_agent == "second_agent"
    
    def test_receive_only_unread(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test that unread_only=True only gets unread messages."""
        # Send and receive message
        second_bus.send("test_agent", "First message")
        bus.receive()  # Marks as read
        
        # Second message
        second_bus.send("test_agent", "Second message")
        
        # Should only get second message
        messages = bus.receive(unread_only=True)
        assert len(messages) == 1
        assert messages[0].body == "Second message"
    
    def test_receive_limit(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test receive limit parameter."""
        # Send multiple messages
        for i in range(5):
            second_bus.send("test_agent", f"Message {i}")
        
        messages = bus.receive(limit=3)
        assert len(messages) == 3
    
    def test_receive_json(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test receiving JSON messages."""
        payload = {"task": "test", "data": [1, 2, 3]}
        second_bus.send_json("test_agent", payload)
        
        messages = bus.receive_json()
        assert len(messages) == 1
        assert "payload" in messages[0]
        assert messages[0]["payload"] == payload
    
    def test_receive_json_non_json(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test receiving non-JSON message via receive_json."""
        second_bus.send("test_agent", "Plain text message")
        
        messages = bus.receive_json()
        assert len(messages) == 1
        assert "body" in messages[0]
        assert messages[0]["body"] == "Plain text message"


class TestChaiwalaBusStatus:
    """Tests for bus status methods."""
    
    def test_get_status(self, bus: ChaiwalaBus):
        """Test getting bus status."""
        status = bus.get_status()
        assert "total_messages" in status
        assert "unread_for_me" in status
        assert "online_agents" in status
        assert "db_path" in status
    
    def test_status_after_send(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test status updates after sending."""
        initial_total = bus.get_status()["total_messages"]
        
        second_bus.send("test_agent", "Test")
        
        new_status = bus.get_status()
        assert new_status["total_messages"] == initial_total + 1
        assert new_status["unread_for_me"] == 1
    
    def test_list_agents(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test listing agents."""
        # Send message to trigger heartbeat
        bus.send("second_agent", "Hello")
        
        agents = bus.list_agents()
        assert len(agents) >= 1
        assert any(a["agent_id"] == "test_agent" for a in agents)
    
    def test_list_agents_with_filter(self, bus: ChaiwalaBus):
        """Test listing agents with status filter."""
        # Trigger heartbeat
        bus.send("test_agent", "Self message")
        
        online_agents = bus.list_agents(status_filter="online")
        assert all(a["status"] == "online" for a in online_agents)


class TestChaiwalaBusDelete:
    """Tests for message deletion."""
    
    def test_delete_message(self, bus: ChaiwalaBus, second_bus: ChaiwalaBus):
        """Test deleting a message."""
        # Send and receive message
        second_bus.send("test_agent", "To be deleted")
        messages = bus.receive()
        msg_id = messages[0].id
        
        # Delete
        result = bus.delete_message(msg_id)
        assert result is True
        
        # Verify deletion
        status = bus.get_status()
        assert status["total_messages"] == 0
    
    def test_delete_nonexistent(self, bus: ChaiwalaBus):
        """Test deleting non-existent message."""
        result = bus.delete_message(99999)
        assert result is False


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_database_error_on_init(self):
        """Test DatabaseError on bad database path."""
        with pytest.raises(DatabaseError):
            ChaiwalaBus("test", db_path=Path("/nonexistent/path/db.sqlite"))
