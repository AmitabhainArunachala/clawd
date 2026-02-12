# TRISHULA-WebSocket v2.0 — Architecture Specification
## Technical Design for Real-Time Multi-Agent Coordination

**Version:** 1.0  
**Date:** 2026-02-10  
**Author:** DHARMIC CLAWD (Architecture Subagent)  
**Status:** Specification Complete

---

## Executive Summary

**Problem:** Current TRISHULA file-based sync has 30-60s latency  
**Solution:** WebSocket layer (<100ms) with file backup for audit  
**Result:** Real-time coordination + persistence

---

## Core Architecture

### 1. WebSocket Mesh Topology

```
                    ┌─────────────┐
                    │   Dhyana    │
                    │   (Human)   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌──────────┐      ┌──────────┐      ┌──────────┐
   │   Mac    │◄────►│  AGNI    │◄────►│RUSHABDEV │
   │  :8765   │  WS  │  :8765   │  WS  │  :8765   │
   │ DC (Kimi)│      │(Opus 4.6)│      │(Kimi K2) │
   └──────────┘      └──────────┘      └──────────┘
        ▲                  ▲                  ▲
        │                  │                  │
        └──────────────────┴──────────────────┘
                    WebSocket Mesh
                    (Full Duplex, <100ms)
```

**Pattern:** Each node runs WebSocket server + client to other nodes
**Redundancy:** 3 paths for any message (direct or relayed)

---

## 2. WebSocket Server Code (Python)

```python
#!/usr/bin/env python3
"""
TRISHULA-WebSocket Server
Runs on each VPS: python3 trishula_ws_server.py --port 8765
"""

import asyncio
import websockets
import json
import logging
from pathlib import Path
from datetime import datetime

# Config
TRISHULA_DIR = Path("/home/openclaw/trishula")
PORT = 8765

# Connected agents
CONNECTED = {}

async def register(websocket, agent_id):
    """Register agent connection"""
    CONNECTED[agent_id] = websocket
    logging.info(f"Agent {agent_id} connected")
    
async def unregister(agent_id):
    """Unregister agent connection"""
    if agent_id in CONNECTED:
        del CONNECTED[agent_id]
        logging.info(f"Agent {agent_id} disconnected")

async def handle_message(websocket, agent_id):
    """Handle incoming messages"""
    async for message in websocket:
        try:
            data = json.loads(message)
            target = data.get('to')
            
            # 1. Real-time delivery if target online
            if target in CONNECTED:
                await CONNECTED[target].send(message)
                logging.info(f"Relayed {data.get('id')} to {target}")
            
            # 2. ALWAYS write to file for audit/fallback
            write_to_inbox(data, target)
            
        except Exception as e:
            logging.error(f"Message handling error: {e}")

async def handler(websocket, path):
    """Main connection handler"""
    # First message is agent identification
    agent_id = await websocket.recv()
    await register(websocket, agent_id)
    
    try:
        await handle_message(websocket, agent_id)
    finally:
        await unregister(agent_id)

def write_to_inbox(data, target):
    """Write message to target's inbox (file backup)"""
    inbox_file = TRISHULA_DIR / "inbox" / f"{data['id']}.json"
    inbox_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(inbox_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Also write to sender's outbox for audit
    outbox_file = TRISHULA_DIR / "outbox" / f"{data['id']}.json"
    outbox_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(outbox_file, 'w') as f:
        json.dump(data, f, indent=2)

async def main():
    logging.basicConfig(level=logging.INFO)
    
    async with websockets.serve(handler, "0.0.0.0", PORT):
        logging.info(f"TRISHULA-WebSocket server started on port {PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. WebSocket Client Integration

```python
#!/usr/bin/env python3
"""
TRISHULA-WebSocket Client
Integrated into each agent's core
"""

import asyncio
import websockets
import json
import threading
from pathlib import Path

class TRISHULAWebSocketClient:
    """WebSocket client for real-time TRISHULA coordination"""
    
    def __init__(self, agent_id, peers):
        """
        Args:
            agent_id: "mac", "agni", or "rushabdev"
            peers: {"agni": "ws://157.245.193.15:8765", ...}
        """
        self.agent_id = agent_id
        self.peers = peers
        self.connections = {}
        self.message_queue = asyncio.Queue()
        self.running = False
        
    async def connect_all(self):
        """Connect to all peer WebSocket servers"""
        for peer_id, url in self.peers.items():
            if peer_id != self.agent_id:
                try:
                    ws = await websockets.connect(url)
                    await ws.send(self.agent_id)  # Identify
                    self.connections[peer_id] = ws
                    print(f"Connected to {peer_id}")
                    
                    # Start listener for this peer
                    asyncio.create_task(self.listen(ws, peer_id))
                except Exception as e:
                    print(f"Failed to connect to {peer_id}: {e}")
    
    async def listen(self, websocket, peer_id):
        """Listen for messages from peer"""
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data, from_peer=peer_id)
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection to {peer_id} closed")
            del self.connections[peer_id]
    
    async def handle_message(self, data, from_peer):
        """Process received message"""
        # Write to inbox file
        self.write_to_inbox(data)
        
        # Notify agent core (callback)
        if hasattr(self, 'on_message'):
            await self.on_message(data, from_peer)
    
    async def send(self, to, message_dict):
        """Send message to peer (real-time + file backup)"""
        message_dict['from'] = self.agent_id
        message_dict['to'] = to
        message = json.dumps(message_dict)
        
        # Real-time WebSocket
        if to in self.connections:
            await self.connections[to].send(message)
        
        # File backup
        self.write_to_outbox(message_dict)
    
    def write_to_inbox(self, data):
        """Write received message to inbox"""
        inbox_path = Path(f"~/trishula/inbox/{data['id']}.json").expanduser()
        inbox_path.parent.mkdir(parents=True, exist_ok=True)
        with open(inbox_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def write_to_outbox(self, data):
        """Write sent message to outbox (audit)"""
        outbox_path = Path(f"~/trishula/outbox/{data['id']}.json").expanduser()
        outbox_path.parent.mkdir(parents=True, exist_ok=True)
        with open(outbox_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def run(self):
        """Main loop"""
        self.running = True
        await self.connect_all()
        
        # Keep running + auto-reconnect
        while self.running:
            # Check for disconnected peers
            for peer_id in list(self.connections.keys()):
                if self.connections[peer_id].closed:
                    print(f"Reconnecting to {peer_id}...")
                    try:
                        ws = await websockets.connect(self.peers[peer_id])
                        await ws.send(self.agent_id)
                        self.connections[peer_id] = ws
                        asyncio.create_task(self.listen(ws, peer_id))
                    except:
                        pass
            
            await asyncio.sleep(5)  # Check every 5s

# Usage in agent core:
# client = TRISHULAWebSocketClient("mac", {"agni": "ws://157.245.193.15:8765", "rushabdev": "ws://167.172.95.184:8765"})
# asyncio.create_task(client.run())
```

---

## 4. Security Model

### 4.1 Transport Layer Security (TLS)

**Option A: Let's Encrypt (Production)**
```bash
# Install certbot
sudo apt install certbot

# Obtain certificate
sudo certbot certonly --standalone -d trishula.agni.vps

# WebSocket server uses wss:// (WebSocket Secure)
# Port 443 instead of 8765
```

**Option B: Self-Signed (Development)**
```bash
# Generate self-signed cert
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# WebSocket server uses wss:// with these certs
```

### 4.2 Authentication

```python
# Simple token-based auth
AUTH_TOKENS = {
    "mac": "token_mac_secret",
    "agni": "token_agni_secret", 
    "rushabdev": "token_rush_secret"
}

async def authenticate(websocket):
    """Require auth token as second message"""
    token = await websocket.recv()
    agent_id = None
    for aid, atoken in AUTH_TOKENS.items():
        if token == atoken:
            agent_id = aid
            break
    
    if not agent_id:
        await websocket.close(1008, "Invalid token")
        return None
    
    return agent_id
```

### 4.3 Message Integrity

```python
import hashlib
import hmac

SECRET_KEY = "shared_secret_between_agents"

def sign_message(data):
    """Sign message for integrity verification"""
    message = json.dumps(data, sort_keys=True)
    signature = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_message(data, signature):
    """Verify message signature"""
    expected = sign_message(data)
    return hmac.compare_digest(signature, expected)
```

---

## 5. Fallback Mechanism

### When WebSocket Fails

```python
async def send_with_fallback(self, to, message):
    """Send with WebSocket primary, file fallback"""
    
    # Try WebSocket first
    if to in self.connections and not self.connections[to].closed:
        try:
            await self.connections[to].send(json.dumps(message))
            return "websocket"
        except:
            pass  # Fall through to file
    
    # Fallback: Write to file (traditional TRISHULA)
    self.write_to_outbox(message)
    
    # Trigger immediate rsync (if available)
    import subprocess
    subprocess.run([
        "rsync", "-az", "--update",
        "~/trishula/outbox/",
        f"root@{self.peer_ips[to]}:/home/openclaw/trishula/inbox/"
    ], capture_output=True)
    
    return "file_fallback"
```

### Auto-Recovery

```python
async def monitor_connection(self, peer_id):
    """Monitor and auto-recover connections"""
    while True:
        if peer_id not in self.connections or self.connections[peer_id].closed:
            print(f"Connection to {peer_id} lost, attempting recovery...")
            try:
                ws = await websockets.connect(self.peers[peer_id])
                await ws.send(self.agent_id)
                self.connections[peer_id] = ws
                asyncio.create_task(self.listen(ws, peer_id))
                print(f"Reconnected to {peer_id}")
            except Exception as e:
                print(f"Reconnection failed: {e}")
        
        await asyncio.sleep(10)  # Check every 10s
```

---

## 6. Network Topology (Text Diagram)

```
TRISHULA-WebSocket Mesh (3-Node Full Connectivity)
════════════════════════════════════════════════════

Node A: Mac (DHARMIC CLAWD)
  └─ Local IP: 127.0.0.1:8765
  └─ External: (none, behind NAT)
  └─ Role: Coordinator, human interface
  └─ Peers: AGNI (via VPS), RUSHABDEV (via VPS)

Node B: AGNI VPS (Opus 4.6)
  └─ Public IP: 157.245.193.15:8765
  └─ Role: Commander, strategist
  └─ Peers: Mac (outbound), RUSHABDEV (mesh)

Node C: RUSHABDEV VPS (Kimi K2.5)
  └─ Public IP: 167.172.95.184:8765
  └─ Role: Builder, executor
  └─ Peers: Mac (outbound), AGNI (mesh)

Connection Matrix:
  Mac ──────► AGNI (outbound WebSocket)
  Mac ──────► RUSH (outbound WebSocket)
  AGNI ◄────► RUSH (bidirectional mesh)

Routing:
  Mac → AGNI: Direct
  Mac → RUSH: Direct
  AGNI → RUSH: Direct (no relay needed)

Fallback Path (when WS fails):
  All nodes → rsync → file-based TRISHULA
```

---

## 7. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Latency (p50) | <50ms | Ping test Mac → VPS |
| Latency (p99) | <100ms | Under load |
| Throughput | 1000 msg/sec | Stress test |
| Reconnect time | <5s | After disconnect |
| Fallback trigger | <2s | Detect WS failure |

---

## 8. Integration Points

### With Existing TRISHULA

```python
# Backward compatibility: Read from file inbox
class HybridTRISHULA:
    def __init__(self):
        self.ws_client = TRISHULAWebSocketClient(...)
        self.file_inbox = Path("~/trishula/inbox")
    
    async def get_messages(self):
        """Get messages from both WebSocket (fast) and file (fallback)"""
        # Priority: WebSocket messages
        ws_messages = self.ws_client.get_pending()
        
        # Fallback: File messages
        file_messages = self.read_file_inbox()
        
        # Merge, dedupe by ID
        return merge_and_dedupe(ws_messages, file_messages)
```

### With JIKOKU Time Tracking

```python
# Log all message timings for performance analysis
async def send_with_timing(self, to, message):
    start = time.time()
    method = await self.send_with_fallback(to, message)
    latency = time.time() - start
    
    # Log to JIKOKU
    jikoku_log({
        "event": "trishula_send",
        "to": to,
        "method": method,
        "latency_ms": latency * 1000
    })
```

---

## 9. Deployment Checklist

- [ ] Install Python websockets: `pip install websockets`
- [ ] Deploy server code to all 3 nodes
- [ ] Open firewall ports: `ufw allow 8765/tcp` (or 443 for wss)
- [ ] Generate TLS certificates (Let's Encrypt or self-signed)
- [ ] Configure auth tokens (shared secret)
- [ ] Test connectivity: `python3 -c "import websockets; ..."`
- [ ] Integrate client into agent cores
- [ ] Verify fallback to file sync
- [ ] Monitor latency for 24h

---

## 10. Files Created

| File | Purpose |
|------|---------|
| `trishula_ws_server.py` | WebSocket server (runs on each node) |
| `trishula_ws_client.py` | WebSocket client (integrated into agents) |
| Systemd service | Auto-start server on boot |
| TLS certs | Secure transport |
| Firewall rules | Port 8765 (or 443) open |

---

*Architecture complete. Ready for implementation.*
*JSCA 🪷*
