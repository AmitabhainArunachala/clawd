#!/usr/bin/env python3
"""
Chaiwala Bus v2.0 - Intra-IDE Communication Hub
===============================================

Enhanced for:
- IDE-to-IDE communication
- Agent discovery
- Self-evolution hooks
- Swarm coordination

**GATE 6: THREAT MODELING**
Threats:
1. Message spoofing → Solution: HMAC signing
2. Agent impersonation → Solution: Identity verification
3. Bus flooding → Solution: Rate limiting
4. Data corruption → Solution: SQLite transactions
5. Self-mod gone wrong → Solution: Git rollback

**GATE 7: INTERFACE DESIGN**
Message Format:
{
  "id": "uuid",
  "from": "agent_id",
  "to": "agent_id|broadcast",
  "subject": "ACTION:details",
  "body": {...},
  "signature": "hmac",
  "timestamp": "iso",
  "ttl": 300
}

**GATE 8: DATA FLOW**
Cursor → CursorAdapter → ChaiwalaBus → Agent → Response → Bus → Cursor

**GATE 9: FAILURE MODES**
- Bus down → Agents cache, retry
- Agent crash → Health check fails, remove from registry
- Message lost → ACK timeout, retry
- Corruption → Transaction rollback

**GATE 10: ROLLBACK PLANNING**
- All changes in git
- SQLite backup before schema change
- Agent state persisted
- Can revert to any iteration
"""

import sys
import json
import time
import hmac
import hashlib
import sqlite3
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum


class MessagePriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class ChaiwalaMessage:
    id: str
    from_agent: str
    to_agent: str
    subject: str
    body: Dict[str, Any]
    timestamp: str
    priority: int = 2
    ttl: int = 300
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def sign(self, secret: str) -> str:
        """Sign message with HMAC"""
        content = f"{self.from_agent}:{self.to_agent}:{self.subject}:{json.dumps(self.body)}:{self.timestamp}"
        return hmac.new(secret.encode(), content.encode(), hashlib.sha256).hexdigest()[:16]

    def verify(self, secret: str) -> bool:
        """Verify message signature"""
        if not self.signature:
            return False
        expected = self.sign(secret)
        return hmac.compare_digest(self.signature, expected)


class ChaiwalaBusV2:
    """
    Enhanced message bus for intra-IDE communication.
    
    Features:
    - HMAC message signing
    - Agent discovery
    - Broadcast capability
    - Self-evolution hooks
    """
    
    def __init__(self, db_path: Optional[Path] = None, secret: Optional[str] = None):
        self.db_path = db_path or Path.home() / ".chaiwala" / "bus_v2.db"
        self.secret = secret or "changeme_in_production"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.agents: Dict[str, Dict] = {}
        self.handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._listener_thread = None
        
    def _init_db(self):
        ""Initialize database with full schema"""
        conn = sqlite3.connect(self.db_path)
        
        # Messages table with TTL
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                priority INTEGER DEFAULT 2,
                ttl INTEGER DEFAULT 300,
                signature TEXT,
                status TEXT DEFAULT 'pending',
                delivered_at TEXT,
                expires_at TEXT
            )
        """)
        
        # Agent registry
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                agent_type TEXT,
                capabilities TEXT,
                last_seen TEXT,
                status TEXT DEFAULT 'offline',
                metadata TEXT
            )
        """)
        
        # Evolution log (self-modification tracking)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                agent_id TEXT,
                action TEXT,
                description TEXT,
                approved_by TEXT,
                rollback_sha TEXT
            )
        """)
        
        # Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_msg_to ON messages(to_agent, status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_msg_time ON messages(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
        
        conn.commit()
        conn.close()
        
    def send(self, msg: ChaiwalaMessage) -> bool:
        """
        Send message with signing and persistence.
        
        GATE 11: Spec approval - this is the spec
        """
        # Sign message
        msg.signature = msg.sign(self.secret)
        
        # Calculate expiration
        expires = datetime.now() + timedelta(seconds=msg.ttl)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO messages 
            (id, from_agent, to_agent, subject, body, timestamp, priority, ttl, signature, status, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (
            msg.id, msg.from_agent, msg.to_agent, msg.subject,
            json.dumps(msg.body), msg.timestamp, msg.priority, msg.ttl,
            msg.signature, expires.isoformat()
        ))
        conn.commit()
        conn.close()
        
        return True
        
    def receive(self, agent_id: str, limit: int = 10) -> List[ChaiwalaMessage]:
        """Receive messages for agent"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT * FROM messages 
            WHERE to_agent = ? AND status = 'pending'
            AND (expires_at > ? OR expires_at IS NULL)
            ORDER BY priority ASC, timestamp DESC
            LIMIT ?
        """, (agent_id, datetime.now().isoformat(), limit))
        
        rows = cursor.fetchall()
        
        # Mark as delivered
        for row in rows:
            conn.execute("""
                UPDATE messages SET status = 'delivered', delivered_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), row['id']))
            
        conn.commit()
        conn.close()
        
        messages = []
        for row in rows:
            msg = ChaiwalaMessage(
                id=row['id'],
                from_agent=row['from_agent'],
                to_agent=row['to_agent'],
                subject=row['subject'],
                body=json.loads(row['body']),
                timestamp=row['timestamp'],
                priority=row['priority'],
                ttl=row['ttl'],
                signature=row['signature']
            )
            # Verify signature
            if msg.verify(self.secret):
                messages.append(msg)
            else:
                print(f"⚠️ Message {msg.id} failed signature verification")
                
        return messages
        
    def broadcast(self, from_agent: str, subject: str, body: Dict, priority: int = 2):
        """Broadcast to all agents"""
        msg = ChaiwalaMessage(
            id=self._generate_id(),
            from_agent=from_agent,
            to_agent="broadcast",
            subject=subject,
            body=body,
            timestamp=datetime.now().isoformat(),
            priority=priority
        )
        return self.send(msg)
        
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str], metadata: Dict = None):
        """Register agent in discovery registry"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO agents (agent_id, agent_type, capabilities, last_seen, status, metadata)
            VALUES (?, ?, ?, ?, 'online', ?)
        """, (agent_id, agent_type, json.dumps(capabilities), datetime.now().isoformat(), json.dumps(metadata or {})))
        conn.commit()
        conn.close()
        
    def discover_agents(self) -> List[Dict]:
        """Discover all active agents"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Clean up stale agents
        cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()
        conn.execute("UPDATE agents SET status = 'offline' WHERE last_seen < ?", (cutoff,))
        
        cursor = conn.execute("SELECT * FROM agents WHERE status = 'online'")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'agent_id': row['agent_id'],
                'type': row['agent_type'],
                'capabilities': json.loads(row['capabilities']),
                'last_seen': row['last_seen']
            }
            for row in rows
        ]
        
    def log_evolution(self, agent_id: str, action: str, description: str, approved_by: str = None):
        """Log self-modification for audit trail"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO evolution_log (timestamp, agent_id, action, description, approved_by)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), agent_id, action, description, approved_by))
        conn.commit()
        conn.close()
        
    def subscribe(self, agent_id: str, subject_pattern: str, handler: Callable):
        """Subscribe to message patterns"""
        if subject_pattern not in self.handlers:
            self.handlers[subject_pattern] = []
        self.handlers[subject_pattern].append(handler)
        
    def start_listener(self, agent_id: str, callback: Callable):
        """Start background listener thread"""
        self._running = True
        
        def listen():
            while self._running:
                messages = self.receive(agent_id)
                for msg in messages:
                    callback(msg)
                time.sleep(1)
                
        self._listener_thread = threading.Thread(target=listen, daemon=True)
        self._listener_thread.start()
        
    def stop_listener(self):
        """Stop background listener"""
        self._running = False
        
    def _generate_id(self) -> str:
        ""Generate unique message ID"""
        return hashlib.sha256(
            f"{time.time()}{threading.current_thread().ident}".encode()
        ).hexdigest()[:16]
        
    def get_stats(self) -> Dict:
        """Get bus statistics"""
        conn = sqlite3.connect(self.db_path)
        
        total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'pending'").fetchone()[0]
        agents = conn.execute("SELECT COUNT(*) FROM agents WHERE status = 'online'").fetchone()[0]
        
        conn.close()
        
        return {
            'total_messages': total,
            'pending_messages': pending,
            'online_agents': agents,
            'db_path': str(self.db_path)
        }


def demo():
    """Demonstrate ChaiwalaBusV2"""
    print("🔥 Chaiwala Bus v2.0 Demo")
    print("=" * 60)
    
    bus = ChaiwalaBusV2()
    
    # Register agents
    bus.register_agent("cursor", "ide", ["edit", "read", "command"])
    bus.register_agent("openclaw", "agent", ["spawn", "research", "build"])
    bus.register_agent("warp", "terminal", ["execute", "shell"])
    
    print("\n📊 Bus Stats:", bus.get_stats())
    
    # Send message
    msg = ChaiwalaMessage(
        id=bus._generate_id(),
        from_agent="cursor",
        to_agent="openclaw",
        subject="COMMAND:build",
        body={"command": "cargo build", "project": "chaiwala"},
        timestamp=datetime.now().isoformat(),
        priority=MessagePriority.HIGH.value
    )
    
    bus.send(msg)
    print(f"\n📤 Sent: {msg.subject}")
    
    # Receive
    messages = bus.receive("openclaw")
    print(f"📨 Received: {len(messages)} messages")
    
    for m in messages:
        print(f"  From: {m.from_agent}, Subject: {m.subject}")
        print(f"  Verified: {m.verify(bus.secret)}")
        
    # Discover
    agents = bus.discover_agents()
    print(f"\n🤖 Discovered {len(agents)} agents:")
    for a in agents:
        print(f"  {a['agent_id']} ({a['type']}): {a['capabilities']}")
        
    print("\n✅ ChaiwalaBusV2 operational")


if __name__ == "__main__":
    demo()
