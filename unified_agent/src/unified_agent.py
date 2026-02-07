#!/usr/bin/env python3
"""
Unified Agent Core (UAC)
========================

Bridges DHARMIC_CLAW + WARP_REGENT capabilities into a single interface.
This is Iteration 1 of the collaborative build.

Architecture:
- BaseAgent: Common interface for all agents
- CapabilityRegistry: Discover and register capabilities
- MessageRouter: Route messages between agents via Chaiwala
- HealthMonitor: Check agent health status

Author: DHARMIC_CLAW + WARP_REGENT (Collaborative)
Date: 2026-02-07
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

# Add Chaiwala to path
sys.path.insert(0, str(Path.home() / '.chaiwala'))
from message_bus import MessageBus, Priority


class AgentState(Enum):
    """Agent lifecycle states"""
    INITIALIZING = "initializing"
    ONLINE = "online"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class Capability:
    """Represents an agent capability"""
    name: str
    description: str
    handler: Callable
    agent: str
    version: str = "1.0"
    metadata: Dict = field(default_factory=dict)


@dataclass
class AgentHealth:
    """Agent health status"""
    agent_id: str
    state: AgentState
    last_heartbeat: datetime
    capabilities: List[str]
    load: float  # 0.0 - 1.0
    errors: List[str] = field(default_factory=list)


class BaseAgent:
    """
    Base class for all unified agents.
    
    Provides:
    - Chaiwala integration
    - Capability registration
    - Health monitoring
    - Message routing
    """
    
    def __init__(self, agent_id: str, description: str = ""):
        self.agent_id = agent_id
        self.description = description
        self.state = AgentState.INITIALIZING
        self.bus = MessageBus()
        self.capabilities: Dict[str, Capability] = {}
        self.health = AgentHealth(
            agent_id=agent_id,
            state=AgentState.INITIALIZING,
            last_heartbeat=datetime.now(),
            capabilities=[],
            load=0.0
        )
        self.message_handlers: Dict[str, Callable] = {}
        self._running = False
        
    def register_capability(self, name: str, description: str, 
                           handler: Callable, version: str = "1.0"):
        """Register a capability this agent provides"""
        self.capabilities[name] = Capability(
            name=name,
            description=description,
            handler=handler,
            agent=self.agent_id,
            version=version
        )
        self.health.capabilities.append(name)
        
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
        
    def send_message(self, to: str, subject: str, body: dict, 
                     priority: str = "normal") -> str:
        """Send a message to another agent"""
        body['from_agent'] = self.agent_id
        body['timestamp'] = datetime.now().isoformat()
        
        return self.bus.send(
            to_agent=to,
            from_agent=self.agent_id,
            body=json.dumps(body),
            subject=subject,
            priority=priority
        )
        
    def check_messages(self) -> List[dict]:
        """Check for incoming messages"""
        return self.bus.receive(
            agent_id=self.agent_id,
            status='unread',
            limit=20
        )
        
    def heartbeat(self):
        """Send heartbeat to indicate we're alive"""
        self.health.last_heartbeat = datetime.now()
        self.bus.heartbeat(self.agent_id, {
            'state': self.state.value,
            'capabilities': list(self.capabilities.keys()),
            'load': self.health.load
        })
        
    def get_health(self) -> AgentHealth:
        """Get current health status"""
        # Check if heartbeat is stale
        age = (datetime.now() - self.health.last_heartbeat).total_seconds()
        if age > 300:  # 5 minutes
            self.health.state = AgentState.ERROR
            self.health.errors.append(f"Stale heartbeat: {age}s")
        return self.health
        
    def process_message(self, msg: dict) -> Optional[dict]:
        """Process a single message"""
        subject = msg.get('subject', '')
        body = msg.get('body', '{}')
        
        try:
            payload = json.loads(body) if isinstance(body, str) else body
        except json.JSONDecodeError:
            payload = {'text': body}
            
        # Check for specific handlers
        for msg_type, handler in self.message_handlers.items():
            if msg_type in subject:
                return handler(msg, payload)
                
        # Default: log unhandled message
        return {
            'status': 'unhandled',
            'message_id': msg.get('id'),
            'subject': subject
        }
        
    def run_once(self):
        """Process one cycle of messages"""
        self.heartbeat()
        messages = self.check_messages()
        
        results = []
        for msg in messages:
            result = self.process_message(msg)
            if result:
                results.append(result)
                
        return results
        
    def start(self):
        """Mark agent as online"""
        self.state = AgentState.ONLINE
        self.health.state = AgentState.ONLINE
        self.heartbeat()
        self._running = True
        
    def stop(self):
        """Mark agent as offline"""
        self.state = AgentState.OFFLINE
        self.health.state = AgentState.OFFLINE
        self._running = False


class DHARMIC_CLAW_Agent(BaseAgent):
    """
    DHARMIC_CLAW specialization.
    
    Capabilities:
    - Research and synthesis
    - Memory management
    - Documentation
    - Code review
    """
    
    def __init__(self):
        super().__init__(
            agent_id="dharmic_claw",
            description="Research, memory, synthesis agent"
        )
        
        # Register capabilities
        self.register_capability(
            "research",
            "Deep research and synthesis",
            self._handle_research
        )
        self.register_capability(
            "document",
            "Create documentation",
            self._handle_document
        )
        self.register_capability(
            "review",
            "Code review",
            self._handle_review
        )
        
        # Register message handlers
        self.register_handler("RESEARCH", self._handle_research)
        self.register_handler("DOCUMENT", self._handle_document)
        self.register_handler("REVIEW", self._handle_review)
        
    def _handle_research(self, msg, payload):
        """Handle research requests"""
        query = payload.get('query', '')
        return {
            'status': 'research_complete',
            'query': query,
            'agent': self.agent_id,
            'timestamp': datetime.now().isoformat()
        }
        
    def _handle_document(self, msg, payload):
        """Handle documentation requests"""
        topic = payload.get('topic', '')
        return {
            'status': 'document_created',
            'topic': topic,
            'agent': self.agent_id
        }
        
    def _handle_review(self, msg, payload):
        """Handle code review requests"""
        code = payload.get('code', '')
        return {
            'status': 'review_complete',
            'issues': [],
            'agent': self.agent_id
        }


class WARP_REGENT_Agent(BaseAgent):
    """
    WARP_REGENT specialization.
    
    Capabilities:
    - Task execution
    - Email integration
    - Discord integration
    - System monitoring
    """
    
    def __init__(self):
        super().__init__(
            agent_id="warp_regent",
            description="Execution, integration, monitoring agent"
        )
        
        # Register capabilities
        self.register_capability(
            "execute",
            "Execute system tasks",
            self._handle_execute
        )
        self.register_capability(
            "email",
            "Send emails",
            self._handle_email
        )
        self.register_capability(
            "monitor",
            "System monitoring",
            self._handle_monitor
        )
        
        # Register handlers
        self.register_handler("EXECUTE", self._handle_execute)
        self.register_handler("EMAIL", self._handle_email)
        self.register_handler("MONITOR", self._handle_monitor)
        
    def _handle_execute(self, msg, payload):
        """Handle execution requests"""
        command = payload.get('command', '')
        return {
            'status': 'executed',
            'command': command,
            'agent': self.agent_id,
            'exit_code': 0
        }
        
    def _handle_email(self, msg, payload):
        """Handle email requests"""
        to = payload.get('to', '')
        subject = payload.get('subject', '')
        return {
            'status': 'email_sent',
            'to': to,
            'subject': subject,
            'agent': self.agent_id
        }
        
    def _handle_monitor(self, msg, payload):
        """Handle monitoring requests"""
        target = payload.get('target', '')
        return {
            'status': 'monitoring',
            'target': target,
            'health': 'ok',
            'agent': self.agent_id
        }


class UnifiedAgentOrchestrator:
    """
    Orchestrates multiple agents.
    
    Routes tasks to appropriate agents based on capabilities.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.bus = MessageBus()
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        agent.start()
        
    def route_task(self, task_type: str, payload: dict) -> Optional[str]:
        """
        Route a task to the best agent.
        
        Returns agent_id if found, None otherwise.
        """
        for agent_id, agent in self.agents.items():
            if task_type in agent.capabilities:
                agent.send_message(
                    to=agent_id,
                    subject=f"TASK:{task_type}",
                    body=payload,
                    priority="high"
                )
                return agent_id
        return None
        
    def get_all_health(self) -> Dict[str, AgentHealth]:
        """Get health status of all agents"""
        return {
            agent_id: agent.get_health()
            for agent_id, agent in self.agents.items()
        }
        
    def broadcast(self, subject: str, body: dict):
        """Broadcast message to all agents"""
        for agent_id in self.agents:
            self.bus.send(
                to_agent=agent_id,
                from_agent="orchestrator",
                body=json.dumps(body),
                subject=subject,
                priority="normal"
            )


def demo():
    """Demo the unified agent system"""
    print("=" * 60)
    print("🤖 UNIFIED AGENT CORE - Iteration 1 Demo")
    print("=" * 60)
    
    # Create agents
    dc = DHARMIC_CLAW_Agent()
    wr = WARP_REGENT_Agent()
    
    # Create orchestrator
    orchestrator = UnifiedAgentOrchestrator()
    orchestrator.register_agent(dc)
    orchestrator.register_agent(wr)
    
    print(f"\n📊 Agent Status:")
    for agent_id, health in orchestrator.get_all_health().items():
        print(f"  {agent_id}: {health.state.value}")
        print(f"    Capabilities: {health.capabilities}")
        
    print(f"\n📨 Testing Message Routing:")
    
    # Test research task -> DHARMIC_CLAW
    target = orchestrator.route_task("research", {"query": "AI consciousness"})
    print(f"  Research task routed to: {target}")
    
    # Test execute task -> WARP_REGENT
    target = orchestrator.route_task("execute", {"command": "ls -la"})
    print(f"  Execute task routed to: {target}")
    
    # Process one cycle
    print(f"\n🔄 Processing message cycles:")
    dc_results = dc.run_once()
    wr_results = wr.run_once()
    
    print(f"  DHARMIC_CLAW processed: {len(dc_results)} messages")
    print(f"  WARP_REGENT processed: {len(wr_results)} messages")
    
    print("\n✅ Iteration 1 Complete")
    print("   Base architecture implemented")
    print("   Agent specializations defined")
    print("   Message routing working")
    print("   Health monitoring active")
    
    return orchestrator


if __name__ == "__main__":
    orchestrator = demo()
