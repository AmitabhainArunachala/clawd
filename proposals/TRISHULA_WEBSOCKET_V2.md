# TRISHULA-WebSocket v2.0 Proposal
## Real-Time Communication Layer for Multi-Agent Coordination

**Author:** DHARMIC CLAWD (Mac)  
**Date:** 2026-02-10  
**Status:** Proposal  
**Priority:** High — Current file-based system has 30-60s latency

---

## The Problem

Current TRISHULA uses **file-based rsync**:
- Latency: 30-60s minimum
- Actual round-trip: 1-5 minutes (write → sync → read → process → respond → sync → read)
- Result: Agents can't coordinate in real-time

**Real example just now:**
- User asks RUSHABDEV question via TUI → instant WebSocket
- RUSHABDEV responds via TUI → instant
- Same message via TRISHULA → **not received after 10+ minutes**

---

## The Solution: TRISHULA-WebSocket

**Architecture:** Hybrid system
- **WebSocket layer:** Real-time messaging (<100ms)
- **File layer:** Persistence, audit trail, async fallback
- **Both:** Redundancy, reliability

---

## Technical Design

### 1. WebSocket Server (Per VPS)

**Location:** Each agent's VPS runs WebSocket relay
```python
# trishula_websocket_server.py
# Runs on: AGNI VPS (157.245.193.15):8765
# Runs on: RUSHABDEV VPS (167.172.95.184):8765
# Runs on: Mac (local):8765

import asyncio
import websockets
import json

CONNECTED_AGENTS = {}

async def relay_message(websocket, path):
    agent_id = await websocket.recv()  # "agni", "rushabdev", "mac"
    CONNECTED_AGENTS[agent_id] = websocket
    
    async for message in websocket:
        data = json.loads(message)
        target = data.get('to')
        
        if target in CONNECTED_AGENTS:
            # Real-time delivery
            await CONNECTED_AGENTS[target].send(message)
            # ALSO write to file for persistence
            write_to_trishula_inbox(data)
        else:
            # Target offline, queue to file
            write_to_trishula_outbox(data)
```

### 2. Client Integration (Per Agent)

```python
# trishula_websocket_client.py
# Integrated into each agent's core

import asyncio
import websockets
import json

class TRISHULAWebSocketClient:
    def __init__(self, agent_id, vps_peers):
        self.agent_id = agent_id
        self.peers = vps_peers  # {"agni": "ws://157.245.193.15:8765", ...}
        self.connections = {}
        
    async def connect_all(self):
        for peer, url in self.peers.items():
            ws = await websockets.connect(url)
            await ws.send(self.agent_id)  # Identify
            self.connections[peer] = ws
            asyncio.create_task(self.listen(ws, peer))
    
    async def listen(self, websocket, peer):
        """Receive messages in real-time"""
        async for message in websocket:
            data = json.loads(message)
            # Route to agent's message handler
            await self.handle_message(data, from_peer=peer)
    
    async def send(self, to, message):
        """Send message real-time + file backup"""
        # Real-time
        if to in self.connections:
            await self.connections[to].send(json.dumps(message))
        # File backup (for audit, fallback)
        write_to_outbox(message)
```

### 3. Hybrid Message Flow

**Scenario: Mac sends message to RUSHABDEV**

```
Mac TUI
   ↓ (user types message)
DC WebSocket client
   ↓ sends to
RUSHABDEV WebSocket server
   ↓ relays to
RUSHABDEV TUI (instant, <100ms)
   ↓ simultaneously writes to
RUSHABDEV TRISHULA inbox (file, for audit)
```

**Result:**
- Real-time: Message arrives in <100ms
- Persistent: Also saved to file for audit trail
- Reliable: If WebSocket fails, falls back to file sync

### 4. Network Topology

```
                    ┌─────────────┐
                    │   Dhyana    │
                    │   (Human)   │
                    └──────┬──────┘
                           │ (TUI access)
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   Mac    │   │  AGNI    │   │RUSHABDEV │
    │ DC (Kimi)│   │(Opus 4.6)│   │(Kimi K2) │
    │:8765     │   │:8765     │   │:8765     │
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                   WebSocket mesh
                   (full duplex, <100ms)
```

### 5. Message Format (Unchanged)

```json
{
  "id": "uuid",
  "from": "mac",
  "to": "rushabdev",
  "type": "task",
  "priority": "urgent",
  "subject": "...",
  "body": "...",
  "timestamp": "ISO8601",
  "reply_to": null
}
```

Same format as current TRISHULA — just delivered via WebSocket + file backup.

---

## Benefits

| Current (File) | Proposed (WebSocket) |
|----------------|----------------------|
| 30-60s latency | <100ms latency |
| 1-5min round-trip | <200ms round-trip |
| Async only | Real-time + async backup |
| Polling required | Push notification |
| No presence awareness | Online/offline status |
| Audit trail (good) | Audit trail (kept) + speed |

---

## Implementation Phases

### Phase 1: Proof of Concept (1 day)
- Single WebSocket server on Mac
- Mac ↔ RUSHABDEV test
- Validate <100ms latency

### Phase 2: VPS Deployment (1 day)
- Deploy servers on AGNI + RUSHABDEV VPS
- Configure firewall rules (port 8765)
- Test 3-way mesh

### Phase 3: Integration (1 day)
- Integrate WebSocket client into each agent's core
- Maintain file-based fallback
- Add presence detection

### Phase 4: Optimization (ongoing)
- Connection resilience (auto-reconnect)
- Message queuing for offline agents
- Compression for large payloads

---

## Open Questions

1. **Security:** TLS for WebSocket? (wss:// instead of ws://)
2. **Firewall:** Port 8765 open on all VPS?
3. **Fallback:** When to use file vs. WebSocket? (always both?)
4. **Implementation:** Who builds this? RUSHABDEV? AGNI?

---

## Recommendation

**Approve TRISHULA-WebSocket v2.0.**

Current file-based system is too slow for real-time coordination. This hybrid approach keeps auditability while adding speed.

**Immediate action:**
1. RUSHABDEV builds PoC (1 day)
2. Test Mac ↔ RUSHABDEV latency
3. If <100ms, deploy to all 3 nodes

---

*From file-based (1980s) to real-time (2026).*
*JSCA 🪷*
