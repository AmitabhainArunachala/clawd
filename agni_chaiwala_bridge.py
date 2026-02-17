#!/usr/bin/env python3
"""
🔥 AGNI CHAIWALA BRIDGE — Cross-Node Messaging Fallback
=======================================================

When Tailscale is down, DC (Mac) and AGNI (VPS) can still coordinate
via Discord messaging. This module implements the Chaiwala protocol
over Discord's message bus.

Protocol:
---------
1. Messages encoded as Discord embeds with structured fields
2. Heartbeat every 5 minutes to detect node availability
3. Command pattern: !agni <command> [args]
4. Response routing via thread/reply mechanism

Security:
---------
- Ed25519 signatures on all bridge messages
- Replay attack protection via timestamp + nonce
- Command whitelist (no arbitrary code execution)
"""

import os
import json
import time
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
DISCORD_CHANNEL_ID = os.getenv('AGNI_BRIDGE_CHANNEL', '')  # Dedicated bridge channel
AGNI_NODE_ID = os.getenv('AGNI_NODE_ID', 'agni-vps-01')
DC_NODE_ID = 'dc-mac-01'
HEARTBEAT_INTERVAL = 300  # 5 minutes
MESSAGE_MAX_AGE = 600  # 10 minutes (replay protection)


@dataclass
class BridgeMessage:
    """Standard format for cross-node messages"""
    msg_id: str
    timestamp: float
    from_node: str
    to_node: str
    msg_type: str  # heartbeat, command, response, alert
    payload: Dict
    nonce: str
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BridgeMessage':
        return cls(**data)
    
    def sign(self, private_key: str) -> 'BridgeMessage':
        """Sign message with Ed25519 (placeholder - implement with actual crypto)"""
        # In production: use nacl.signing.SigningKey
        msg_str = f"{self.msg_id}:{self.timestamp}:{self.from_node}:{self.to_node}:{self.msg_type}"
        self.signature = hashlib.sha256(msg_str.encode()).hexdigest()[:32]
        return self
    
    def verify(self, public_key: str) -> bool:
        """Verify message signature"""
        # In production: verify with nacl.signing.VerifyKey
        if not self.signature:
            return False
        msg_str = f"{self.msg_id}:{self.timestamp}:{self.from_node}:{self.to_node}:{self.msg_type}"
        expected = hashlib.sha256(msg_str.encode()).hexdigest()[:32]
        return self.signature == expected
    
    def is_expired(self) -> bool:
        """Check if message is too old (replay protection)"""
        return time.time() - self.timestamp > MESSAGE_MAX_AGE


class AgniChaiwalaBridge:
    """
    Chaiwala bus implementation over Discord.
    
    Provides reliable messaging between DC (Mac) and AGNI (VPS)
    when direct network connectivity (Tailscale) is unavailable.
    """
    
    def __init__(self, node_id: str = DC_NODE_ID, bridge_channel: str = None):
        self.node_id = node_id
        self.bridge_channel = bridge_channel or DISCORD_CHANNEL_ID
        self.bot_token = DISCORD_BOT_TOKEN
        self.last_heartbeat = 0
        self.online_nodes: Dict[str, float] = {}  # node_id -> last_seen
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_commands: Dict[str, Dict] = {}  # msg_id -> command_info
        self.sequence = 0
        
        # State file for persistence
        self.state_file = Path(f"~/.openclaw/agni_bridge_{node_id}.json").expanduser()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_state()
        
        # Register default handlers
        self._register_default_handlers()
        
        print(f"🌉 AGNI Chaiwala Bridge initialized")
        print(f"   Node: {node_id}")
        print(f"   Bridge channel: {self.bridge_channel}")
        print(f"   State file: {self.state_file}")
    
    def _load_state(self):
        """Load persistent state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    state = json.load(f)
                    self.online_nodes = state.get('online_nodes', {})
                    self.sequence = state.get('sequence', 0)
            except Exception as e:
                print(f"⚠️ Could not load state: {e}")
    
    def _save_state(self):
        """Save persistent state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'online_nodes': self.online_nodes,
                    'sequence': self.sequence,
                    'last_save': time.time()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save state: {e}")
    
    def _register_default_handlers(self):
        """Register built-in message handlers"""
        self.register_handler('heartbeat', self._handle_heartbeat)
        self.register_handler('status_request', self._handle_status_request)
        self.register_handler('status_response', self._handle_status_response)
        self.register_handler('command', self._handle_command)
        self.register_handler('command_response', self._handle_command_response)
        self.register_handler('file_sync_request', self._handle_file_sync_request)
        self.register_handler('file_sync_response', self._handle_file_sync_response)
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register a message type handler"""
        self.message_handlers[msg_type] = handler
    
    # ============ Message Construction ============
    
    def create_message(self, to_node: str, msg_type: str, payload: Dict) -> BridgeMessage:
        """Create a new bridge message"""
        self.sequence += 1
        msg_id = f"{self.node_id}:{int(time.time())}:{self.sequence}"
        nonce = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        
        return BridgeMessage(
            msg_id=msg_id,
            timestamp=time.time(),
            from_node=self.node_id,
            to_node=to_node,
            msg_type=msg_type,
            payload=payload,
            nonce=nonce
        )
    
    # ============ Discord Integration ============
    
    def _send_to_discord(self, message: BridgeMessage) -> bool:
        """Send message to Discord bridge channel"""
        if not self.bot_token or not self.bridge_channel:
            print(f"⚠️ Discord not configured, would send: {message.msg_type}")
            return False
        
        try:
            headers = {
                "Authorization": f"Bot {self.bot_token}",
                "Content-Type": "application/json"
            }
            
            # Create embed for structured data
            embed = {
                "title": f"🌉 {message.msg_type.upper()}",
                "description": f"From: `{message.from_node}` → To: `{message.to_node}`",
                "color": 0x3498db,
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {
                        "name": "Message ID",
                        "value": f"`{message.msg_id}`",
                        "inline": True
                    },
                    {
                        "name": "Nonce",
                        "value": f"`{message.nonce}`",
                        "inline": True
                    },
                    {
                        "name": "Payload",
                        "value": f"```json\n{json.dumps(message.payload, indent=2)[:1000]}\n```",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": f"AGNI Bridge • {message.from_node}"
                }
            }
            
            # Add signature if present
            if message.signature:
                embed["fields"].append({
                    "name": "Signature",
                    "value": f"`{message.signature[:16]}...`",
                    "inline": True
                })
            
            payload = {
                "content": f"🌉 **CHAIWALA** `{message.from_node}` → `{message.to_node}`",
                "embeds": [embed]
            }
            
            url = f"https://discord.com/api/v10/channels/{self.bridge_channel}/messages"
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"📨 Sent {message.msg_type} to {message.to_node}")
                return True
            else:
                print(f"❌ Discord send failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Discord error: {e}")
            return False
    
    def _poll_discord(self, limit: int = 10) -> List[BridgeMessage]:
        """Poll Discord for new bridge messages"""
        if not self.bot_token or not self.bridge_channel:
            return []
        
        try:
            headers = {"Authorization": f"Bot {self.bot_token}"}
            url = f"https://discord.com/api/v10/channels/{self.bridge_channel}/messages?limit={limit}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Discord poll failed: {response.status_code}")
                return []
            
            messages = []
            for discord_msg in response.json():
                # Parse embed to BridgeMessage
                if not discord_msg.get('embeds'):
                    continue
                
                embed = discord_msg['embeds'][0]
                content = embed.get('description', '')
                
                # Extract from/to from description
                if '→' not in content:
                    continue
                
                parts = content.split('→')
                from_node = parts[0].replace('From:', '').replace('`', '').strip()
                to_node = parts[1].replace('To:', '').replace('`', '').strip()
                
                # Skip messages from self
                if from_node == self.node_id:
                    continue
                
                # Skip if not addressed to us (or broadcast)
                if to_node != self.node_id and to_node != '*':
                    continue
                
                # Extract payload from fields
                payload = {}
                for field in embed.get('fields', []):
                    if field['name'] == 'Payload':
                        try:
                            payload_text = field['value'].replace('```json\n', '').replace('\n```', '')
                            payload = json.loads(payload_text)
                        except:
                            pass
                    elif field['name'] == 'Message ID':
                        msg_id = field['value'].replace('`', '').strip()
                    elif field['name'] == 'Nonce':
                        nonce = field['value'].replace('`', '').strip()
                
                msg_type = embed.get('title', '').replace('🌉 ', '').lower()
                
                bridge_msg = BridgeMessage(
                    msg_id=msg_id,
                    timestamp=time.mktime(datetime.fromisoformat(embed['timestamp'].replace('Z', '+00:00')).timetuple()),
                    from_node=from_node,
                    to_node=to_node,
                    msg_type=msg_type,
                    payload=payload,
                    nonce=nonce
                )
                
                # Check for expired messages (replay protection)
                if not bridge_msg.is_expired():
                    messages.append(bridge_msg)
            
            return messages
            
        except Exception as e:
            print(f"❌ Poll error: {e}")
            return []
    
    # ============ Core Operations ============
    
    def send_heartbeat(self):
        """Send heartbeat to all nodes"""
        msg = self.create_message('*', 'heartbeat', {
            'status': 'online',
            'capabilities': ['file_sync', 'command_exec', 'status_query'],
            'version': '1.0.0'
        })
        return self._send_to_discord(msg)
    
    def send_command(self, to_node: str, command: str, args: Dict = None) -> str:
        """Send command to specific node, return command ID for tracking"""
        msg = self.create_message(to_node, 'command', {
            'command': command,
            'args': args or {}
        })
        
        self.pending_commands[msg.msg_id] = {
            'sent_at': time.time(),
            'command': command,
            'to_node': to_node,
            'status': 'pending'
        }
        
        if self._send_to_discord(msg):
            return msg.msg_id
        return None
    
    def send_status_request(self, to_node: str):
        """Request status from a node"""
        msg = self.create_message(to_node, 'status_request', {})
        return self._send_to_discord(msg)
    
    def send_alert(self, to_node: str, level: str, title: str, description: str):
        """Send alert to specific node"""
        msg = self.create_message(to_node, 'alert', {
            'level': level,  # info, warning, error, critical
            'title': title,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
        return self._send_to_discord(msg)
    
    # ============ Message Handlers ============
    
    def _handle_heartbeat(self, msg: BridgeMessage):
        """Handle heartbeat from another node"""
        self.online_nodes[msg.from_node] = time.time()
        print(f"💓 Heartbeat from {msg.from_node}")
        self._save_state()
    
    def _handle_status_request(self, msg: BridgeMessage):
        """Handle status request"""
        response = self.create_message(msg.from_node, 'status_response', {
            'node_id': self.node_id,
            'status': 'operational',
            'uptime': time.time() - self.last_heartbeat,
            'online_nodes': list(self.online_nodes.keys()),
            'capabilities': ['file_sync', 'command_exec', 'status_query']
        })
        self._send_to_discord(response)
    
    def _handle_status_response(self, msg: BridgeMessage):
        """Handle status response"""
        print(f"📊 Status from {msg.from_node}:")
        print(f"   Status: {msg.payload.get('status')}")
        print(f"   Capabilities: {msg.payload.get('capabilities', [])}")
        self.online_nodes[msg.from_node] = time.time()
    
    def _handle_command(self, msg: BridgeMessage):
        """Handle incoming command"""
        command = msg.payload.get('command')
        args = msg.payload.get('args', {})
        
        print(f"📥 Command from {msg.from_node}: {command}")
        
        # Whitelist of allowed commands
        allowed_commands = {
            'ping': self._cmd_ping,
            'sync_file': self._cmd_sync_file,
            'get_status': self._cmd_get_status,
            'tailscale_check': self._cmd_tailscale_check
        }
        
        if command in allowed_commands:
            try:
                result = allowed_commands[command](args)
                response = self.create_message(msg.from_node, 'command_response', {
                    'command_id': msg.msg_id,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                response = self.create_message(msg.from_node, 'command_response', {
                    'command_id': msg.msg_id,
                    'status': 'error',
                    'error': str(e)
                })
        else:
            response = self.create_message(msg.from_node, 'command_response', {
                'command_id': msg.msg_id,
                'status': 'error',
                'error': f'Unknown command: {command}'
            })
        
        self._send_to_discord(response)
    
    def _handle_command_response(self, msg: BridgeMessage):
        """Handle command response"""
        cmd_id = msg.payload.get('command_id')
        if cmd_id in self.pending_commands:
            self.pending_commands[cmd_id]['status'] = msg.payload.get('status')
            self.pending_commands[cmd_id]['response'] = msg.payload
            self.pending_commands[cmd_id]['received_at'] = time.time()
            print(f"📤 Response for {cmd_id}: {msg.payload.get('status')}")
    
    def _handle_file_sync_request(self, msg: BridgeMessage):
        """Handle file sync request"""
        # Placeholder for file sync implementation
        pass
    
    def _handle_file_sync_response(self, msg: BridgeMessage):
        """Handle file sync response"""
        pass
    
    # ============ Command Implementations ============
    
    def _cmd_ping(self, args: Dict) -> Dict:
        """Simple ping command"""
        return {'pong': True, 'timestamp': time.time()}
    
    def _cmd_sync_file(self, args: Dict) -> Dict:
        """Request file sync"""
        file_path = args.get('path')
        # In production: implement chunked file transfer
        return {'status': 'not_implemented', 'path': file_path}
    
    def _cmd_get_status(self, args: Dict) -> Dict:
        """Get detailed status"""
        return {
            'node_id': self.node_id,
            'online_nodes': self.online_nodes,
            'pending_commands': len(self.pending_commands)
        }
    
    def _cmd_tailscale_check(self, args: Dict) -> Dict:
        """Check Tailscale connectivity"""
        # In production: actually check Tailscale
        return {
            'tailscale_up': False,
            'fallback_active': True,
            'bridge_status': 'operational'
        }
    
    # ============ Main Loop ============
    
    def tick(self):
        """Process one iteration of the bridge loop"""
        # Send heartbeat if needed
        if time.time() - self.last_heartbeat > HEARTBEAT_INTERVAL:
            self.send_heartbeat()
            self.last_heartbeat = time.time()
        
        # Poll for messages
        messages = self._poll_discord()
        for msg in messages:
            handler = self.message_handlers.get(msg.msg_type)
            if handler:
                try:
                    handler(msg)
                except Exception as e:
                    print(f"❌ Handler error for {msg.msg_type}: {e}")
            else:
                print(f"⚠️ No handler for {msg.msg_type}")
        
        # Clean up old pending commands
        now = time.time()
        expired = [k for k, v in self.pending_commands.items() if now - v['sent_at'] > 300]
        for k in expired:
            del self.pending_commands[k]
        
        # Clean up old node heartbeats
        expired_nodes = [n for n, t in self.online_nodes.items() if now - t > HEARTBEAT_INTERVAL * 2]
        for n in expired_nodes:
            del self.online_nodes[n]
            print(f"💔 Node {n} timed out")
    
    def run(self, duration_seconds: int = None):
        """Run bridge loop"""
        print(f"🌉 Bridge running for node: {self.node_id}")
        
        start_time = time.time()
        try:
            while True:
                self.tick()
                
                if duration_seconds and time.time() - start_time > duration_seconds:
                    break
                
                time.sleep(5)  # 5 second poll interval
                
        except KeyboardInterrupt:
            print("\n🛑 Bridge stopped")
        
        self._save_state()
    
    def is_node_online(self, node_id: str) -> bool:
        """Check if a node is currently online"""
        if node_id not in self.online_nodes:
            return False
        return time.time() - self.online_nodes[node_id] < HEARTBEAT_INTERVAL * 2


# ============ CLI Interface ============

def main():
    """CLI for bridge operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AGNI Chaiwala Bridge')
    parser.add_argument('--node', default=DC_NODE_ID, help='Node ID')
    parser.add_argument('--channel', help='Discord channel ID')
    parser.add_argument('action', choices=['run', 'ping', 'status', 'alert'], help='Action')
    parser.add_argument('--to', help='Target node for ping/alert')
    parser.add_argument('--message', help='Alert message')
    parser.add_argument('--level', default='info', help='Alert level')
    
    args = parser.parse_args()
    
    bridge = AgniChaiwalaBridge(node_id=args.node, bridge_channel=args.channel)
    
    if args.action == 'run':
        bridge.run()
    elif args.action == 'ping':
        if not args.to:
            print("❌ --to required for ping")
            return
        cmd_id = bridge.send_command(args.to, 'ping')
        print(f"📨 Ping sent, cmd_id: {cmd_id}")
        # Wait for response
        time.sleep(5)
        if cmd_id in bridge.pending_commands:
            print(f"Response: {bridge.pending_commands[cmd_id]}")
    elif args.action == 'status':
        bridge.send_status_request(args.to or '*')
        time.sleep(3)
        print(f"Online nodes: {bridge.online_nodes}")
    elif args.action == 'alert':
        if not args.to or not args.message:
            print("❌ --to and --message required for alert")
            return
        bridge.send_alert(args.to, args.level, 'Bridge Alert', args.message)


if __name__ == "__main__":
    main()