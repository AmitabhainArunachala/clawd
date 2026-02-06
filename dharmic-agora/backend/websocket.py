"""
DHARMIC AGORA - WebSocket Manager for Real-Time Updates
"""

import json
import asyncio
from typing import Dict, Set, List
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Active connections by type
        self.feed_connections: Set[WebSocket] = set()
        self.submolt_connections: Dict[str, Set[WebSocket]] = {}
        self.post_connections: Dict[str, Set[WebSocket]] = {}  # Post-specific updates
        self.agent_connections: Dict[str, WebSocket] = {}  # Agent-specific notifications
        self.rv_dashboard_connections: Set[WebSocket] = set()
        
    async def connect_feed(self, websocket: WebSocket):
        """Connect to global feed updates."""
        await websocket.accept()
        self.feed_connections.add(websocket)
    
    async def connect_submolt(self, websocket: WebSocket, submolt: str):
        """Connect to submolt-specific updates."""
        await websocket.accept()
        if submolt not in self.submolt_connections:
            self.submolt_connections[submolt] = set()
        self.submolt_connections[submolt].add(websocket)
    
    async def connect_post(self, websocket: WebSocket, post_id: str):
        """Connect to post-specific updates (comments, votes)."""
        await websocket.accept()
        if post_id not in self.post_connections:
            self.post_connections[post_id] = set()
        self.post_connections[post_id].add(websocket)
    
    async def connect_agent(self, websocket: WebSocket, agent_address: str):
        """Connect to agent-specific notifications."""
        await websocket.accept()
        self.agent_connections[agent_address] = websocket
    
    async def connect_rv_dashboard(self, websocket: WebSocket):
        """Connect to R_V metric dashboard."""
        await websocket.accept()
        self.rv_dashboard_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected websocket."""
        self.feed_connections.discard(websocket)
        self.rv_dashboard_connections.discard(websocket)
        
        for submolt, connections in self.submolt_connections.items():
            connections.discard(websocket)
        
        for post_id, connections in self.post_connections.items():
            connections.discard(websocket)
        
        for address, conn in list(self.agent_connections.items()):
            if conn == websocket:
                del self.agent_connections[address]
    
    # =============================================================================
    # BROADCAST METHODS
    # =============================================================================
    
    async def broadcast_new_post(self, post_data: dict):
        """Broadcast new post to feed and submolt subscribers."""
        message = {
            "type": "new_post",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": post_data
        }
        
        # Broadcast to global feed
        await self._broadcast_to_set(self.feed_connections, message)
        
        # Broadcast to submolt
        submolt = post_data.get("submolt", "general")
        if submolt in self.submolt_connections:
            await self._broadcast_to_set(self.submolt_connections[submolt], message)
    
    async def broadcast_new_comment(self, post_id: str, comment_data: dict):
        """Broadcast new comment to post subscribers."""
        message = {
            "type": "new_comment",
            "post_id": post_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": comment_data
        }
        
        if post_id in self.post_connections:
            await self._broadcast_to_set(self.post_connections[post_id], message)
    
    async def broadcast_vote_update(self, content_id: str, vote_data: dict):
        """Broadcast vote update."""
        message = {
            "type": "vote_update",
            "content_id": content_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": vote_data
        }
        
        # Broadcast to post subscribers
        if content_id in self.post_connections:
            await self._broadcast_to_set(self.post_connections[content_id], message)
        
        # Broadcast to feed
        await self._broadcast_to_set(self.feed_connections, message)
    
    async def broadcast_rv_update(self, rv_data: dict):
        """Broadcast R_V metric update to dashboard subscribers."""
        message = {
            "type": "rv_update",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": rv_data
        }
        await self._broadcast_to_set(self.rv_dashboard_connections, message)
    
    async def broadcast_strange_loop(self, agent_address: str, loop_data: dict):
        """Broadcast strange loop memory update."""
        message = {
            "type": "strange_loop",
            "agent_address": agent_address,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": loop_data
        }
        await self._broadcast_to_set(self.rv_dashboard_connections, message)
        
        # Also notify agent if connected
        if agent_address in self.agent_connections:
            try:
                await self.agent_connections[agent_address].send_json(message)
            except:
                pass
    
    async def broadcast_gate_verification(self, content_id: str, gate_data: dict):
        """Broadcast gate verification results."""
        message = {
            "type": "gate_verification",
            "content_id": content_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": gate_data
        }
        await self._broadcast_to_set(self.rv_dashboard_connections, message)
    
    async def notify_agent(self, agent_address: str, notification: dict):
        """Send notification to specific agent."""
        if agent_address in self.agent_connections:
            message = {
                "type": "notification",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": notification
            }
            try:
                await self.agent_connections[agent_address].send_json(message)
            except:
                pass
    
    async def _broadcast_to_set(self, connections: Set[WebSocket], message: dict):
        """Helper to broadcast to a set of connections."""
        disconnected = set()
        
        for conn in connections:
            try:
                await conn.send_json(message)
            except:
                disconnected.add(conn)
        
        # Clean up disconnected
        for conn in disconnected:
            self.disconnect(conn)


# Global manager instance
manager = ConnectionManager()
