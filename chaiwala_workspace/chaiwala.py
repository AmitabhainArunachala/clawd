#!/usr/bin/env python3
"""
Chaiwala Python Interface
=========================

Python wrapper for the Chaiwala message bus.
Enables seamless agent-to-agent communication.

Usage:
    from chaiwala import ChaiwalaBus
    
    bus = ChaiwalaBus(agent_id="dharmic_claw")
    bus.send(to="warp_regent", subject="TASK", body="...")
    messages = bus.receive()
"""

import subprocess
import json
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class ChaiwalaMessage:
    """Represents a message on the Chaiwala bus"""
    id: int
    to_agent: str
    from_agent: str
    body: str
    subject: str
    priority: str
    status: str
    created_at: str
    
    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'ChaiwalaMessage':
        return cls(
            id=row['id'],
            to_agent=row['to_agent'],
            from_agent=row['from_agent'],
            body=row['body'],
            subject=row['subject'],
            priority=row['priority'],
            status=row['status'],
            created_at=row['created_at']
        )


class ChaiwalaBus:
    """
    Interface to the Chaiwala message bus.
    
    Enables agents to communicate via SQLite-backed queue.
    """
    
    def __init__(self, agent_id: str, db_path: Optional[Path] = None):
        self.agent_id = agent_id
        self.db_path = db_path or Path.home() / ".chaiwala" / "messages.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                to_agent TEXT NOT NULL,
                from_agent TEXT NOT NULL,
                body TEXT NOT NULL,
                subject TEXT DEFAULT '(no subject)',
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'unread',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                read_at TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_to 
            ON messages(to_agent, status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_from 
            ON messages(from_agent)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                last_seen TEXT NOT NULL,
                status TEXT DEFAULT 'offline'
            )
        """)
        conn.commit()
        conn.close()
        
    def send(self, to: str, body: str, subject: str = "(no subject)", 
             priority: str = "normal") -> int:
        """
        Send a message to another agent.
        
        Args:
            to: Recipient agent ID
            body: Message body
            subject: Message subject
            priority: low, normal, high
            
        Returns:
            Message ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """INSERT INTO messages 
               (to_agent, from_agent, body, subject, priority, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (to, self.agent_id, body, subject, priority, 
             datetime.now().isoformat())
        )
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Update agent heartbeat
        self._heartbeat()
        
        return message_id
        
    def send_json(self, to: str, payload: dict, subject: str = "JSON_MESSAGE",
                  priority: str = "normal") -> int:
        """Send a JSON-encoded message"""
        return self.send(to, json.dumps(payload), subject, priority)
        
    def receive(self, unread_only: bool = True, limit: int = 10) -> List[ChaiwalaMessage]:
        """
        Receive messages for this agent.
        
        Args:
            unread_only: Only get unread messages
            limit: Maximum messages to retrieve
            
        Returns:
            List of messages
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        if unread_only:
            cursor = conn.execute(
                """SELECT * FROM messages 
                   WHERE to_agent = ? AND status = 'unread'
                   ORDER BY created_at DESC LIMIT ?""",
                (self.agent_id, limit)
            )
        else:
            cursor = conn.execute(
                """SELECT * FROM messages 
                   WHERE to_agent = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (self.agent_id, limit)
            )
            
        messages = [ChaiwalaMessage.from_row(row) for row in cursor.fetchall()]
        
        # Mark as read
        for msg in messages:
            conn.execute(
                """UPDATE messages 
                   SET status = 'read', read_at = ?
                   WHERE id = ?""",
                (datetime.now().isoformat(), msg.id)
            )
            
        conn.commit()
        conn.close()
        
        # Update heartbeat
        self._heartbeat()
        
        return messages
        
    def receive_json(self, unread_only: bool = True, 
                     limit: int = 10) -> List[Dict]:
        """Receive messages and parse JSON bodies"""
        messages = self.receive(unread_only, limit)
        result = []
        for msg in messages:
            try:
                payload = json.loads(msg.body)
                result.append({
                    'id': msg.id,
                    'from': msg.from_agent,
                    'subject': msg.subject,
                    'payload': payload,
                    'priority': msg.priority,
                    'created_at': msg.created_at
                })
            except json.JSONDecodeError:
                # Not JSON, return as text
                result.append({
                    'id': msg.id,
                    'from': msg.from_agent,
                    'subject': msg.subject,
                    'body': msg.body,
                    'priority': msg.priority,
                    'created_at': msg.created_at
                })
        return result
        
    def _heartbeat(self):
        """Update agent heartbeat"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO agents 
               (agent_id, last_seen, status) 
               VALUES (?, ?, 'online')""",
            (self.agent_id, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
    def get_status(self) -> Dict:
        """Get bus status"""
        conn = sqlite3.connect(self.db_path)
        
        total = conn.execute(
            "SELECT COUNT(*) FROM messages"
        ).fetchone()[0]
        
        unread = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE to_agent = ? AND status = 'unread'",
            (self.agent_id,)
        ).fetchone()[0]
        
        agents = conn.execute(
            "SELECT COUNT(*) FROM agents WHERE status = 'online'"
        ).fetchone()[0]
        
        conn.close()
        
        return {
            'total_messages': total,
            'unread_for_me': unread,
            'online_agents': agents,
            'db_path': str(self.db_path)
        }
        
    def list_agents(self) -> List[Dict]:
        """List all known agents"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(
            "SELECT * FROM agents ORDER BY last_seen DESC"
        )
        
        agents = [
            {
                'agent_id': row['agent_id'],
                'last_seen': row['last_seen'],
                'status': row['status']
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return agents


# Example usage
if __name__ == "__main__":
    # Test the bus
    bus = ChaiwalaBus("test_agent")
    
    # Send test message
    msg_id = bus.send(
        to="warp_regent",
        subject="TEST_MESSAGE",
        body=json.dumps({
            'task': 'EMAIL_SEND',
            'to': 'client@example.com',
            'subject': 'Hello from Chaiwala',
            'body': 'This is a test message'
        }),
        priority="high"
    )
    print(f"✅ Message sent: ID {msg_id}")
    
    # Check status
    status = bus.get_status()
    print(f"📊 Bus status: {status}")
    
    # Receive messages (if any)
    messages = bus.receive_json()
    print(f"📨 Received {len(messages)} messages")
    for msg in messages:
        print(f"  From: {msg['from']}, Subject: {msg['subject']}")
