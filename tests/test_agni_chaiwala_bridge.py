#!/usr/bin/env python3
"""
Tests for AGNI Chaiwala Bridge
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from agni_chaiwala_bridge import (
    BridgeMessage, 
    AgniChaiwalaBridge,
    DC_NODE_ID,
    AGNI_NODE_ID
)


class TestBridgeMessage:
    """Test BridgeMessage dataclass"""
    
    def test_message_creation(self):
        """Test creating a bridge message"""
        msg = BridgeMessage(
            msg_id="test:123:1",
            timestamp=time.time(),
            from_node="dc-mac-01",
            to_node="agni-vps-01",
            msg_type="heartbeat",
            payload={"status": "online"},
            nonce="abc123"
        )
        
        assert msg.from_node == "dc-mac-01"
        assert msg.to_node == "agni-vps-01"
        assert msg.msg_type == "heartbeat"
    
    def test_message_serialization(self):
        """Test message to/from dict"""
        original = BridgeMessage(
            msg_id="test:123:1",
            timestamp=time.time(),
            from_node="dc-mac-01",
            to_node="agni-vps-01",
            msg_type="test",
            payload={"key": "value"},
            nonce="nonce123"
        )
        
        data = original.to_dict()
        restored = BridgeMessage.from_dict(data)
        
        assert restored.msg_id == original.msg_id
        assert restored.payload == original.payload
    
    def test_message_signature(self):
        """Test message signing"""
        msg = BridgeMessage(
            msg_id="test:123:1",
            timestamp=time.time(),
            from_node="dc-mac-01",
            to_node="agni-vps-01",
            msg_type="test",
            payload={},
            nonce="nonce"
        )
        
        # Sign with placeholder crypto
        msg.sign("private_key")
        assert msg.signature is not None
        
        # Verify
        assert msg.verify("public_key") is True
    
    def test_message_expiration(self):
        """Test message expiration for replay protection"""
        # Old message
        old_msg = BridgeMessage(
            msg_id="old:1:1",
            timestamp=time.time() - 1000,  # 1000 seconds ago
            from_node="test",
            to_node="test",
            msg_type="test",
            payload={},
            nonce="nonce"
        )
        assert old_msg.is_expired() is True
        
        # New message
        new_msg = BridgeMessage(
            msg_id="new:1:1",
            timestamp=time.time(),
            from_node="test",
            to_node="test",
            msg_type="test",
            payload={},
            nonce="nonce"
        )
        assert new_msg.is_expired() is False


class TestAgniChaiwalaBridge:
    """Test bridge functionality"""
    
    @pytest.fixture
    def bridge(self, tmp_path):
        """Create test bridge with temp state"""
        with patch.dict('os.environ', {'DISCORD_BOT_TOKEN': '', 'AGNI_BRIDGE_CHANNEL': ''}):
            bridge = AgniChaiwalaBridge(node_id="test-node")
            bridge.state_file = tmp_path / "test_state.json"
            return bridge
    
    def test_bridge_initialization(self, bridge):
        """Test bridge setup"""
        assert bridge.node_id == "test-node"
        assert bridge.online_nodes == {}
        assert bridge.sequence == 0
    
    def test_create_message(self, bridge):
        """Test message creation"""
        msg = bridge.create_message("agni-vps-01", "test", {"key": "value"})
        
        assert msg.from_node == "test-node"
        assert msg.to_node == "agni-vps-01"
        assert msg.msg_type == "test"
        assert msg.payload == {"key": "value"}
        assert msg.nonce is not None
        assert bridge.sequence == 1
    
    def test_state_persistence(self, bridge):
        """Test saving and loading state"""
        bridge.online_nodes = {"agni-vps-01": time.time()}
        bridge.sequence = 42
        bridge._save_state()
        
        # Create new bridge instance
        bridge2 = AgniChaiwalaBridge(node_id="test-node")
        bridge2.state_file = bridge.state_file
        bridge2._load_state()
        
        assert "agni-vps-01" in bridge2.online_nodes
        assert bridge2.sequence == 42
    
    def test_heartbeat_sends_message(self, bridge):
        """Test heartbeat generation"""
        with patch.object(bridge, '_send_to_discord') as mock_send:
            mock_send.return_value = True
            result = bridge.send_heartbeat()
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check message was created correctly
            call_args = mock_send.call_args[0][0]
            assert call_args.msg_type == "heartbeat"
            assert call_args.to_node == "*"
    
    def test_command_with_tracking(self, bridge):
        """Test sending command with tracking"""
        with patch.object(bridge, '_send_to_discord') as mock_send:
            mock_send.return_value = True
            cmd_id = bridge.send_command("agni-vps-01", "ping", {})
            
            assert cmd_id is not None
            assert cmd_id in bridge.pending_commands
            assert bridge.pending_commands[cmd_id]['status'] == 'pending'
    
    def test_node_online_detection(self, bridge):
        """Test detecting online nodes"""
        # Node just checked in
        bridge.online_nodes["agni-vps-01"] = time.time()
        assert bridge.is_node_online("agni-vps-01") is True
        
        # Node hasn't checked in for a while
        bridge.online_nodes["old-node"] = time.time() - 1000
        assert bridge.is_node_online("old-node") is False
    
    def test_handle_heartbeat(self, bridge):
        """Test processing incoming heartbeat"""
        msg = BridgeMessage(
            msg_id="h:1:1",
            timestamp=time.time(),
            from_node="agni-vps-01",
            to_node="*",
            msg_type="heartbeat",
            payload={"status": "online"},
            nonce="nonce"
        )
        
        bridge._handle_heartbeat(msg)
        
        assert "agni-vps-01" in bridge.online_nodes
        assert bridge.is_node_online("agni-vps-01")
    
    def test_handle_status_response(self, bridge):
        """Test processing status response"""
        msg = BridgeMessage(
            msg_id="sr:1:1",
            timestamp=time.time(),
            from_node="agni-vps-01",
            to_node="dc-mac-01",
            msg_type="status_response",
            payload={
                "node_id": "agni-vps-01",
                "status": "operational",
                "capabilities": ["file_sync"]
            },
            nonce="nonce"
        )
        
        bridge._handle_status_response(msg)
        
        assert "agni-vps-01" in bridge.online_nodes
    
    def test_command_whitelist(self, bridge):
        """Test only whitelisted commands are executed"""
        # Valid command
        valid_msg = BridgeMessage(
            msg_id="cmd:1:1",
            timestamp=time.time(),
            from_node="agni-vps-01",
            to_node="dc-mac-01",
            msg_type="command",
            payload={"command": "ping", "args": {}},
            nonce="nonce"
        )
        
        with patch.object(bridge, '_send_to_discord') as mock_send:
            bridge._handle_command(valid_msg)
            
            # Should send response
            mock_send.assert_called_once()
            response = mock_send.call_args[0][0]
            assert response.payload.get('status') == 'success'
        
        # Invalid command
        invalid_msg = BridgeMessage(
            msg_id="cmd:2:1",
            timestamp=time.time(),
            from_node="agni-vps-01",
            to_node="dc-mac-01",
            msg_type="command",
            payload={"command": "rm_rf_root", "args": {}},
            nonce="nonce"
        )
        
        with patch.object(bridge, '_send_to_discord') as mock_send:
            bridge._handle_command(invalid_msg)
            
            response = mock_send.call_args[0][0]
            assert response.payload.get('status') == 'error'
    
    def test_replay_protection(self, bridge):
        """Test old messages are rejected"""
        old_msg = BridgeMessage(
            msg_id="old:1:1",
            timestamp=time.time() - 1000,  # Very old
            from_node="agni-vps-01",
            to_node="dc-mac-01",
            msg_type="command",
            payload={"command": "ping"},
            nonce="nonce"
        )
        
        assert old_msg.is_expired() is True


class TestDiscordIntegration:
    """Test Discord API integration (mocked)"""
    
    @pytest.fixture
    def bridge(self):
        """Create bridge with mocked Discord"""
        with patch.dict('os.environ', {
            'DISCORD_BOT_TOKEN': 'test_token',
            'AGNI_BRIDGE_CHANNEL': '123456'
        }):
            return AgniChaiwalaBridge(node_id="test-node")
    
    @patch('requests.post')
    def test_send_to_discord(self, mock_post, bridge):
        """Test sending message to Discord"""
        mock_post.return_value = Mock(status_code=200)
        
        msg = bridge.create_message("agni-vps-01", "test", {"key": "value"})
        result = bridge._send_to_discord(msg)
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verify payload structure
        call_args = mock_post.call_args
        assert 'json' in call_args[1] or call_args[1].get('json')
    
    @patch('requests.get')
    def test_poll_discord(self, mock_get, bridge):
        """Test polling Discord for messages"""
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: [
                {
                    "id": "msg1",
                    "embeds": [{
                        "title": "🌉 heartbeat",
                        "description": "From: `agni-vps-01` → To: `*`,",
                        "timestamp": "2026-02-17T10:00:00Z",
                        "fields": [
                            {"name": "Message ID", "value": "`agni:123:1`"},
                            {"name": "Nonce", "value": "`abc123`"},
                            {"name": "Payload", "value": "```json\n{\"status\": \"online\"}\n```"}
                        ]
                    }]
                }
            ]
        )
        
        messages = bridge._poll_discord()
        
        assert len(messages) == 1
        assert messages[0].from_node == "agni-vps-01"
        assert messages[0].msg_type == "heartbeat"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])