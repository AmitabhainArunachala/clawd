#!/usr/bin/env python3
"""
Chaiwala Python Interface
=========================

Python wrapper for the Chaiwala message bus.
Enables seamless agent-to-agent communication via SQLite-backed queue.

Usage:
    from chaiwala import ChaiwalaBus
    
    bus = ChaiwalaBus(agent_id="dharmic_claw")
    bus.send(to="warp_regent", subject="TASK", body="...")
    messages = bus.receive()

Example:
    >>> bus = ChaiwalaBus("test_agent")
    >>> msg_id = bus.send("recipient", "Hello!", "GREETING")
    >>> print(f"Sent message {msg_id}")
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# ============================================================================
# Data Classes
# ============================================================================

@dataclass(frozen=True)
class ChaiwalaMessage:
    """Represents a message on the Chaiwala bus.
    
    Attributes:
        id: Unique message identifier
        to_agent: Recipient agent ID
        from_agent: Sender agent ID
        body: Message content
        subject: Message subject line
        priority: Message priority (low, normal, high)
        status: Current status (unread, read)
        created_at: ISO format timestamp when message was created
    """
    id: int
    to_agent: str
    from_agent: str
    body: str
    subject: str
    priority: str
    status: str
    created_at: str
    
    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ChaiwalaMessage:
        """Create a ChaiwalaMessage from a database row.
        
        Args:
            row: SQLite row object with message data
            
        Returns:
            ChaiwalaMessage instance
        """
        return cls(
            id=row["id"],
            to_agent=row["to_agent"],
            from_agent=row["from_agent"],
            body=row["body"],
            subject=row["subject"],
            priority=row["priority"],
            status=row["status"],
            created_at=row["created_at"]
        )


# ============================================================================
# Exceptions
# ============================================================================

class ChaiwalaError(Exception):
    """Base exception for Chaiwala errors."""
    pass


class DatabaseError(ChaiwalaError):
    """Raised when database operations fail."""
    pass


class MessageError(ChaiwalaError):
    """Raised when message operations fail."""
    pass


# ============================================================================
# Main Bus Class
# ============================================================================

class ChaiwalaBus:
    """Interface to the Chaiwala message bus.
    
    Enables agents to communicate via SQLite-backed queue with
    automatic heartbeat tracking and JSON message support.
    
    Args:
        agent_id: Unique identifier for this agent
        db_path: Optional custom path to SQLite database
        
    Raises:
        DatabaseError: If database initialization fails
        
    Example:
        >>> bus = ChaiwalaBus("my_agent")
        >>> status = bus.get_status()
        >>> print(f"Total messages: {status['total_messages']}")
    """
    
    def __init__(
        self, 
        agent_id: str, 
        db_path: Optional[Union[str, Path]] = None
    ) -> None:
        """Initialize the ChaiwalaBus instance.
        
        Args:
            agent_id: Unique identifier for this agent
            db_path: Optional path to SQLite database (default: ~/.chaiwala/messages.db)
        """
        self.agent_id: str = agent_id
        self.db_path: Path = self._resolve_db_path(db_path)
        self._ensure_db_directory()
        self._init_db()
    
    def _resolve_db_path(self, db_path: Optional[Union[str, Path]]) -> Path:
        """Resolve database path with fallback to default.
        
        Args:
            db_path: Optional custom path
            
        Returns:
            Resolved Path object
        """
        if db_path is None:
            return Path.home() / ".chaiwala" / "messages.db"
        return Path(db_path)
    
    def _ensure_db_directory(self) -> None:
        """Ensure database directory exists."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise DatabaseError(
                f"Failed to create database directory {self.db_path.parent}: {e}"
            ) from e
    
    def _init_db(self) -> None:
        """Initialize database schema with proper error handling."""
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Messages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    to_agent TEXT NOT NULL,
                    from_agent TEXT NOT NULL,
                    body TEXT NOT NULL,
                    subject TEXT DEFAULT '(no subject)',
                    priority TEXT DEFAULT 'normal' 
                        CHECK (priority IN ('low', 'normal', 'high')),
                    status TEXT DEFAULT 'unread' 
                        CHECK (status IN ('unread', 'read')),
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    read_at TEXT
                )
            """)
            
            # Indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_to_status 
                ON messages(to_agent, status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_from 
                ON messages(from_agent)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_created 
                ON messages(created_at DESC)
            """)
            
            # Agents table for heartbeat tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    last_seen TEXT NOT NULL,
                    status TEXT DEFAULT 'offline'
                        CHECK (status IN ('online', 'offline', 'busy'))
                )
            """)
            
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}") from e
        finally:
            if conn:
                conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory.
        
        Returns:
            Configured SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _heartbeat(self) -> None:
        """Update agent heartbeat timestamp."""
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """INSERT OR REPLACE INTO agents 
                   (agent_id, last_seen, status) 
                   VALUES (?, ?, 'online')""",
                (self.agent_id, datetime.now().isoformat())
            )
            conn.commit()
        except sqlite3.Error as e:
            # Heartbeat failures are non-critical, log but don't raise
            print(f"Warning: Heartbeat failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def send(
        self, 
        to: str, 
        body: str, 
        subject: str = "(no subject)", 
        priority: str = "normal"
    ) -> int:
        """Send a message to another agent.
        
        Args:
            to: Recipient agent ID
            body: Message body content
            subject: Message subject (default: "(no subject)")
            priority: Message priority - 'low', 'normal', or 'high' (default: 'normal')
            
        Returns:
            The message ID of the sent message
            
        Raises:
            MessageError: If the message cannot be sent
            ValueError: If priority is invalid
        """
        if priority not in ("low", "normal", "high"):
            raise ValueError(f"Invalid priority: {priority}. Must be 'low', 'normal', or 'high'")
        
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                """INSERT INTO messages 
                   (to_agent, from_agent, body, subject, priority, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (to, self.agent_id, body, subject, priority, datetime.now().isoformat())
            )
            message_id = cursor.lastrowid
            conn.commit()
            
            # Update heartbeat
            self._heartbeat()
            
            return message_id
        except sqlite3.Error as e:
            raise MessageError(f"Failed to send message: {e}") from e
        finally:
            if conn:
                conn.close()
    
    def send_json(
        self, 
        to: str, 
        payload: Dict[str, Any], 
        subject: str = "JSON_MESSAGE",
        priority: str = "normal"
    ) -> int:
        """Send a JSON-encoded message.
        
        Args:
            to: Recipient agent ID
            payload: Dictionary to JSON-encode and send
            subject: Message subject (default: "JSON_MESSAGE")
            priority: Message priority (default: 'normal')
            
        Returns:
            The message ID of the sent message
            
        Raises:
            MessageError: If JSON encoding or sending fails
        """
        try:
            json_body = json.dumps(payload, ensure_ascii=False, indent=None)
        except (TypeError, ValueError) as e:
            raise MessageError(f"Failed to encode payload as JSON: {e}") from e
        
        return self.send(to, json_body, subject, priority)
    
    def receive(
        self, 
        unread_only: bool = True, 
        limit: int = 10
    ) -> List[ChaiwalaMessage]:
        """Receive messages for this agent.
        
        Args:
            unread_only: Only retrieve unread messages (default: True)
            limit: Maximum number of messages to retrieve (default: 10)
            
        Returns:
            List of ChaiwalaMessage objects
            
        Raises:
            DatabaseError: If database query fails
        """
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = self._get_connection()
            
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
            now = datetime.now().isoformat()
            for msg in messages:
                conn.execute(
                    """UPDATE messages 
                       SET status = 'read', read_at = ?
                       WHERE id = ?""",
                    (now, msg.id)
                )
            
            conn.commit()
            self._heartbeat()
            
            return messages
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to receive messages: {e}") from e
        finally:
            if conn:
                conn.close()
    
    def receive_json(
        self, 
        unread_only: bool = True, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Receive messages and parse JSON bodies.
        
        Args:
            unread_only: Only retrieve unread messages (default: True)
            limit: Maximum number of messages to retrieve (default: 10)
            
        Returns:
            List of dictionaries containing message metadata.
            If body is valid JSON, includes 'payload' key.
            Otherwise includes 'body' key with raw content.
        """
        messages = self.receive(unread_only, limit)
        result: List[Dict[str, Any]] = []
        
        for msg in messages:
            entry: Dict[str, Any] = {
                "id": msg.id,
                "from": msg.from_agent,
                "subject": msg.subject,
                "priority": msg.priority,
                "created_at": msg.created_at
            }
            
            try:
                payload = json.loads(msg.body)
                entry["payload"] = payload
            except json.JSONDecodeError:
                # Not JSON, return as text
                entry["body"] = msg.body
            
            result.append(entry)
        
        return result
    
    def get_status(self) -> Dict[str, Union[int, str]]:
        """Get bus status for this agent.
        
        Returns:
            Dictionary with:
                - total_messages: Total messages in system
                - unread_for_me: Unread messages for this agent
                - sent_by_me: Messages sent by this agent
                - online_agents: Number of agents currently online
                - db_path: Path to database file
        """
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = sqlite3.connect(self.db_path)
            
            total = conn.execute(
                "SELECT COUNT(*) FROM messages"
            ).fetchone()[0]
            
            unread = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE to_agent = ? AND status = 'unread'",
                (self.agent_id,)
            ).fetchone()[0]
            
            sent = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE from_agent = ?",
                (self.agent_id,)
            ).fetchone()[0]
            
            agents = conn.execute(
                "SELECT COUNT(*) FROM agents WHERE status = 'online'"
            ).fetchone()[0]
            
            return {
                "total_messages": total,
                "unread_for_me": unread,
                "sent_by_me": sent,
                "online_agents": agents,
                "db_path": str(self.db_path)
            }
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get status: {e}") from e
        finally:
            if conn:
                conn.close()
    
    def list_agents(
        self, 
        status_filter: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """List all known agents.
        
        Args:
            status_filter: Optional filter by status ('online', 'offline', 'busy')
            
        Returns:
            List of dictionaries with agent_id, last_seen, and status
        """
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = self._get_connection()
            
            if status_filter:
                cursor = conn.execute(
                    "SELECT * FROM agents WHERE status = ? ORDER BY last_seen DESC",
                    (status_filter,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM agents ORDER BY last_seen DESC"
                )
            
            agents = [
                {
                    "agent_id": row["agent_id"],
                    "last_seen": row["last_seen"],
                    "status": row["status"]
                }
                for row in cursor.fetchall()
            ]
            
            return agents
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to list agents: {e}") from e
        finally:
            if conn:
                conn.close()
    
    def delete_message(self, message_id: int) -> bool:
        """Delete a message by ID.
        
        Args:
            message_id: ID of message to delete
            
        Returns:
            True if message was deleted, False if not found
        """
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "DELETE FROM messages WHERE id = ?",
                (message_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete message: {e}") from e
        finally:
            if conn:
                conn.close()


# ============================================================================
# CLI / Example Usage
# ============================================================================

def main() -> None:
    """Example usage and CLI test."""
    import sys
    
    # Parse arguments
    agent_id = sys.argv[1] if len(sys.argv) > 1 else "test_agent"
    
    print(f"🚌 Chaiwala Bus Test - Agent: {agent_id}")
    print("=" * 50)
    
    try:
        # Initialize bus
        bus = ChaiwalaBus(agent_id)
        print(f"✅ Bus initialized")
        
        # Send test message
        msg_id = bus.send(
            to="warp_regent",
            subject="TEST_MESSAGE",
            body=json.dumps({
                "task": "EMAIL_SEND",
                "to": "client@example.com",
                "subject": "Hello from Chaiwala",
                "body": "This is a test message"
            }),
            priority="high"
        )
        print(f"✅ Message sent: ID {msg_id}")
        
        # Check status
        status = bus.get_status()
        print(f"\n📊 Bus Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Receive messages
        messages = bus.receive_json()
        print(f"\n📨 Received {len(messages)} messages")
        for msg in messages:
            print(f"   From: {msg['from']}, Subject: {msg['subject']}")
        
        # List agents
        agents = bus.list_agents()
        print(f"\n👥 Known Agents ({len(agents)}):")
        for agent in agents[:5]:  # Show first 5
            print(f"   {agent['agent_id']}: {agent['status']} (last seen: {agent['last_seen']})")
        
        print("\n✅ Test completed successfully!")
        
    except ChaiwalaError as e:
        print(f"❌ Chaiwala error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
