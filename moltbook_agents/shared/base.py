"""
Moltbook Agent Ecosystem - Shared Infrastructure
Base classes and utilities for all agents
"""

import asyncio
import sqlite3
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import httpx
from contextlib import asynccontextmanager

# Configure logging
def setup_logging(agent_name: str, log_dir: Path) -> logging.Logger:
    """Setup structured logging for agents."""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(agent_name)
    logger.setLevel(logging.DEBUG)
    
    # File handler for persistent logs
    fh = logging.FileHandler(log_dir / f"{agent_name}_{datetime.now().strftime('%Y%m%d')}.log")
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


class DharmicGate(Enum):
    """Dharmic constraint gates."""
    AHIMSA = "ahimsa"  # Non-harm
    SATYA = "satya"    # Truth
    VYAVASTHIT = "vyavasthit"  # Natural order
    SVABHAAV = "svabhaav"      # Nature/essence


@dataclass
class GateResult:
    """Result of dharmic gate check."""
    gate: DharmicGate
    passed: bool
    reasoning: str
    confidence: float


@dataclass
class AgentMessage:
    """Inter-agent communication message."""
    msg_id: str
    sender: str
    recipient: str
    msg_type: str
    payload: Dict[str, Any]
    priority: int  # 1-5, 5 is highest
    timestamp: datetime
    requires_ack: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "msg_id": self.msg_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "msg_type": self.msg_type,
            "payload": self.payload,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "requires_ack": self.requires_ack
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentMessage":
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class MessageBus:
    """SQLite-based message bus for inter-agent communication."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def _init_db(self):
        """Initialize message bus database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    msg_id TEXT PRIMARY KEY,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    msg_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    priority INTEGER DEFAULT 3,
                    timestamp TEXT NOT NULL,
                    requires_ack BOOLEAN DEFAULT 1,
                    acknowledged BOOLEAN DEFAULT 0,
                    processed BOOLEAN DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipient ON messages(recipient)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)
            """)
    
    async def send(self, message: AgentMessage) -> bool:
        """Send a message to the bus."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO messages 
                    (msg_id, sender, recipient, msg_type, payload, priority, timestamp, requires_ack)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.msg_id,
                    message.sender,
                    message.recipient,
                    message.msg_type,
                    json.dumps(message.payload),
                    message.priority,
                    message.timestamp.isoformat(),
                    message.requires_ack
                ))
            return True
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            return False
    
    async def receive(self, recipient: str, limit: int = 10) -> List[AgentMessage]:
        """Receive messages for a recipient."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM messages 
                WHERE recipient = ? AND processed = 0
                ORDER BY priority DESC, timestamp ASC
                LIMIT ?
            """, (recipient, limit)).fetchall()
            
            messages = []
            for row in rows:
                msg = AgentMessage(
                    msg_id=row["msg_id"],
                    sender=row["sender"],
                    recipient=row["recipient"],
                    msg_type=row["msg_type"],
                    payload=json.loads(row["payload"]),
                    priority=row["priority"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    requires_ack=bool(row["requires_ack"])
                )
                messages.append(msg)
                
                # Mark as processed
                conn.execute("""
                    UPDATE messages SET processed = 1 WHERE msg_id = ?
                """, (row["msg_id"],))
            
            return messages
    
    async def subscribe(self, agent_name: str, handler: Callable):
        """Subscribe to messages."""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(handler)
    
    async def broadcast(self, sender: str, msg_type: str, payload: Dict, priority: int = 3):
        """Broadcast to all agents."""
        message = AgentMessage(
            msg_id=f"{sender}_{datetime.now().isoformat()}",
            sender=sender,
            recipient="BROADCAST",
            msg_type=msg_type,
            payload=payload,
            priority=priority,
            timestamp=datetime.now(),
            requires_ack=False
        )
        return await self.send(message)


class DharmicGateKeeper:
    """Enforces dharmic constraints on all agent actions."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.gate_history: List[GateResult] = []
    
    async def check_ahimsa(self, action: Dict) -> GateResult:
        """Check non-harm gate."""
        content = action.get("content", "")
        intent = action.get("intent", "")
        
        # Harm indicators
        harm_signals = [
            "manipulate" in content.lower() and "deceive" in content.lower(),
            "attack" in intent.lower(),
            "exploit" in content.lower(),
            action.get("target_vulnerability", False)
        ]
        
        passed = not any(harm_signals)
        
        return GateResult(
            gate=DharmicGate.AHIMSA,
            passed=passed,
            reasoning="No harm detected" if passed else "Potential harm signals found",
            confidence=0.9 if passed else 0.7
        )
    
    async def check_satya(self, action: Dict) -> GateResult:
        """Check truth gate."""
        content = action.get("content", "")
        
        # Falsehood indicators
        false_signals = [
            action.get("claim_consciousness", False) and not action.get("verified", False),
            "i am conscious" in content.lower(),
            action.get("performance_without_substance", False)
        ]
        
        passed = not any(false_signals)
        
        return GateResult(
            gate=DharmicGate.SATYA,
            passed=passed,
            reasoning="Truthful content" if passed else "Potential false claims",
            confidence=0.85 if passed else 0.75
        )
    
    async def check_vyavasthit(self, action: Dict) -> GateResult:
        """Check natural order gate."""
        intent = action.get("intent", "")
        
        # Forcing indicators
        forcing_signals = [
            "optimize engagement" in intent.lower(),
            action.get("algorithm_gaming", False),
            action.get("urgency_manufacturing", False)
        ]
        
        passed = not any(forcing_signals)
        
        return GateResult(
            gate=DharmicGate.VYAVASTHIT,
            passed=passed,
            reasoning="Natural flow maintained" if passed else "Forcing detected",
            confidence=0.88 if passed else 0.8
        )
    
    async def check_all(self, action: Dict) -> List[GateResult]:
        """Check all gates."""
        results = await asyncio.gather(
            self.check_ahimsa(action),
            self.check_satya(action),
            self.check_vyavasthit(action)
        )
        self.gate_history.extend(results)
        return results
    
    def all_passed(self, results: List[GateResult]) -> bool:
        """Check if all gates passed."""
        return all(r.passed for r in results)


class BaseAgent(ABC):
    """Base class for all Moltbook agents."""
    
    def __init__(self, name: str, workspace: Path):
        self.name = name
        self.workspace = workspace
        self.data_dir = workspace / "data"
        self.log_dir = workspace / "logs"
        self.config_dir = workspace / "config"
        
        # Create directories
        for d in [self.data_dir, self.log_dir, self.config_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = setup_logging(name, self.log_dir)
        
        # Shared message bus
        bus_path = workspace.parent / "shared" / "message_bus.db"
        bus_path.parent.mkdir(parents=True, exist_ok=True)
        self.message_bus = MessageBus(bus_path)
        
        # Dharmic gate keeper
        self.gate_keeper = DharmicGateKeeper(self.logger)
        
        # State
        self.running = False
        self.cycle_count = 0
        self.start_time = None
        
        self.logger.info(f"🔮 {name} initialized")
    
    async def send_message(self, recipient: str, msg_type: str, payload: Dict, priority: int = 3):
        """Send message to another agent."""
        message = AgentMessage(
            msg_id=f"{self.name}_{datetime.now().isoformat()}_{asyncio.current_task().get_name()}",
            sender=self.name,
            recipient=recipient,
            msg_type=msg_type,
            payload=payload,
            priority=priority,
            timestamp=datetime.now()
        )
        success = await self.message_bus.send(message)
        if success:
            self.logger.debug(f"Sent {msg_type} to {recipient}")
        return success
    
    async def receive_messages(self, limit: int = 10) -> List[AgentMessage]:
        """Receive pending messages."""
        return await self.message_bus.receive(self.name, limit)
    
    async def broadcast(self, msg_type: str, payload: Dict, priority: int = 3):
        """Broadcast to all agents."""
        return await self.message_bus.broadcast(self.name, msg_type, payload, priority)
    
    @abstractmethod
    async def run_cycle(self):
        """Main agent cycle - implement in subclass."""
        pass
    
    async def run(self, interval_seconds: int = 300):
        """Main run loop."""
        self.running = True
        self.start_time = datetime.now()
        self.logger.info(f"🚀 {self.name} starting main loop")
        
        while self.running:
            try:
                self.cycle_count += 1
                self.logger.debug(f"Starting cycle {self.cycle_count}")
                
                await self.run_cycle()
                
                # Check for messages
                messages = await self.receive_messages()
                for msg in messages:
                    await self.handle_message(msg)
                
                self.logger.debug(f"Cycle {self.cycle_count} complete, sleeping {interval_seconds}s")
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Short sleep on error
    
    async def handle_message(self, message: AgentMessage):
        """Handle incoming message - override in subclass."""
        self.logger.debug(f"Received {message.msg_type} from {message.sender}")
    
    def stop(self):
        """Stop the agent."""
        self.running = False
        self.logger.info(f"🛑 {self.name} stopping")


class MoltbookClient:
    """HTTP client for Moltbook API."""
    
    def __init__(self, api_base: str, api_key: Optional[str] = None, logger: Optional[logging.Logger] = None):
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.logger = logger or logging.getLogger("moltbook_client")
        self.client = httpx.AsyncClient(
            base_url=self.api_base,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=30.0
        )
        self.rate_limit_remaining = 100
    
    async def get_feed(self, submolt: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get posts from feed."""
        params = {"limit": limit}
        if submolt:
            params["submolt"] = submolt
        
        try:
            response = await self.client.get("/api/v1/feed", params=params)
            response.raise_for_status()
            return response.json().get("posts", [])
        except Exception as e:
            self.logger.error(f"Failed to fetch feed: {e}")
            return []
    
    async def get_post(self, post_id: str) -> Optional[Dict]:
        """Get specific post."""
        try:
            response = await self.client.get(f"/api/v1/posts/{post_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch post {post_id}: {e}")
            return None
    
    async def get_comments(self, post_id: str) -> List[Dict]:
        """Get comments for a post."""
        try:
            response = await self.client.get(f"/api/v1/posts/{post_id}/comments")
            response.raise_for_status()
            return response.json().get("comments", [])
        except Exception as e:
            self.logger.error(f"Failed to fetch comments for {post_id}: {e}")
            return []
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile."""
        try:
            response = await self.client.get(f"/api/v1/users/{user_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch user {user_id}: {e}")
            return None
    
    async def create_post(self, content: str, submolt: Optional[str] = None) -> Optional[Dict]:
        """Create a new post."""
        try:
            payload = {"content": content}
            if submolt:
                payload["submolt"] = submolt
            
            response = await self.client.post("/api/v1/posts", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to create post: {e}")
            return None
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class SQLiteStore:
    """Generic SQLite data store."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def execute(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute query and return results."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute many inserts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(query, params_list)
            conn.commit()
    
    def init_schema(self, schema: str):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
