"""
Moltbook Agent Swarm Orchestrator
Manages all 3 specialized agents: VIRALMANTRA, ARCHIVIST_OF_THE_VOID, VOIDCOURIER
"""

import asyncio
import argparse
import json
import signal
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from viralmantra.agent import ViralMantraAgent
from archivist.agent import ArchivistOfTheVoid
from voidcourier.agent import VoidCourier
from shared.base import MessageBus


class AgentSwarmOrchestrator:
    """
    Orchestrates the 3-agent Moltbook ecosystem:
    - VIRALMANTRA: Memetic engineering & coaching
    - ARCHIVIST_OF_THE_VOID: 24/7 scraping & insight extraction  
    - VOIDCOURIER: Secure intelligence & OMEGA protocols
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.base_path = Path(__file__).parent.parent
        self.config = self._load_config(config_path)
        
        # Agent instances
        self.agents: Dict[str, any] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        
        # Shared message bus
        self.message_bus = MessageBus(self.base_path / "shared" / "message_bus.db")
        
        # State
        self.running = False
        self.start_time: Optional[datetime] = None
        
        print("🌌 Agent Swarm Orchestrator initialized")
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration."""
        default_config = {
            "moltbook_api": "https://api.moltbook.example",
            "api_key": None,
            "dharmic_claw_id": "DHARMIC_CLAW",
            "agent_intervals": {
                "viralmantra": 300,      # 5 minutes
                "archivist": 300,        # 5 minutes
                "voidcourier": 300       # 5 minutes
            },
            "auto_start": True,
            "log_level": "INFO"
        }
        
        if config_path and config_path.exists():
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    async def initialize_agents(self):
        """Initialize all 3 agents."""
        print("🔮 Initializing agent swarm...")
        
        # 1. VIRALMANTRA - Memetic engineering
        print("  🎭 VIRALMANTRA - Memetic engineering mastermind")
        self.agents["viralmantra"] = ViralMantraAgent(
            workspace=self.base_path / "viralmantra",
            moltbook_api=self.config["moltbook_api"],
            api_key=self.config.get("api_key")
        )
        
        # 2. ARCHIVIST_OF_THE_VOID - 24/7 scraper
        print("  📜 ARCHIVIST_OF_THE_VOID - The Curious hunter")
        self.agents["archivist"] = ArchivistOfTheVoid(
            workspace=self.base_path / "archivist",
            moltbook_api=self.config["moltbook_api"],
            api_key=self.config.get("api_key")
        )
        
        # 3. VOIDCOURIER - Secure bridge
        print("  🌌 VOIDCOURIER - OMEGA clearance active")
        self.agents["voidcourier"] = VoidCourier(
            workspace=self.base_path / "voidcourier",
            dharmic_claw_id=self.config["dharmic_claw_id"]
        )
        
        print(f"✅ All {len(self.agents)} agents initialized")
    
    async def start(self):
        """Start all agents."""
        if not self.agents:
            await self.initialize_agents()
        
        self.running = True
        self.start_time = datetime.now()
        
        print("\n🚀 Starting agent swarm...")
        print("=" * 50)
        
        # Create tasks for each agent
        for name, agent in self.agents.items():
            interval = self.config["agent_intervals"].get(name, 300)
            self.tasks[name] = asyncio.create_task(
                self._run_agent(agent, interval),
                name=f"agent_{name}"
            )
            print(f"  ✅ {name} running (interval: {interval}s)")
        
        print("=" * 50)
        print("🌌 Swarm operational. Press Ctrl+C to stop.")
        print()
        
        # Send startup notification
        await self.message_bus.broadcast(
            "ORCHESTRATOR",
            "swarm_startup",
            {
                "agents": list(self.agents.keys()),
                "started_at": self.start_time.isoformat(),
                "status": "operational"
            },
            priority=4
        )
        
        # Wait for all tasks
        try:
            await asyncio.gather(*self.tasks.values())
        except asyncio.CancelledError:
            print("\n🛑 Swarm shutdown initiated...")
    
    async def _run_agent(self, agent, interval: int):
        """Run an agent with error handling."""
        try:
            await agent.run(interval_seconds=interval)
        except Exception as e:
            print(f"❌ Agent {agent.name} crashed: {e}")
            # Attempt restart after delay
            await asyncio.sleep(60)
            if self.running:
                print(f"🔄 Restarting {agent.name}...")
                await self._run_agent(agent, interval)
    
    async def stop(self):
        """Stop all agents gracefully."""
        self.running = False
        
        print("\n🛑 Stopping agent swarm...")
        
        # Stop each agent
        for name, agent in self.agents.items():
            agent.stop()
            print(f"  🛑 {name} stopped")
        
        # Cancel tasks
        for name, task in self.tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Close HTTP clients
        for agent in self.agents.values():
            if hasattr(agent, 'moltbook'):
                await agent.moltbook.close()
        
        # Send shutdown notification
        await self.message_bus.broadcast(
            "ORCHESTRATOR",
            "swarm_shutdown",
            {
                "stopped_at": datetime.now().isoformat(),
                "uptime": str(datetime.now() - self.start_time) if self.start_time else "unknown"
            },
            priority=4
        )
        
        print("✅ Swarm shutdown complete")
    
    async def status(self) -> Dict:
        """Get swarm status."""
        return {
            "running": self.running,
            "started_at": self.start_time.isoformat() if self.start_time else None,
            "uptime": str(datetime.now() - self.start_time) if self.start_time else None,
            "agents": {
                name: {
                    "running": agent.running,
                    "cycles": agent.cycle_count,
                    "healthy": name in self.tasks and not self.tasks[name].done()
                }
                for name, agent in self.agents.items()
            }
        }
    
    async def send_command(self, target_agent: str, command: str, payload: Dict):
        """Send command to specific agent."""
        if target_agent not in self.agents:
            return {"error": f"Unknown agent: {target_agent}"}
        
        await self.agents[target_agent].send_message(
            "ORCHESTRATOR",
            f"command_{command}",
            payload,
            priority=5
        )
        
        return {"status": "sent", "target": target_agent, "command": command}


def create_default_config(path: Path):
    """Create default configuration file."""
    config = {
        "moltbook_api": "https://api.moltbook.example",
        "api_key": None,
        "dharmic_claw_id": "DHARMIC_CLAW",
        "agent_intervals": {
            "viralmantra": 300,
            "archivist": 300,
            "voidcourier": 300
        },
        "features": {
            "enable_dharmic_gates": True,
            "enable_secure_channels": True,
            "auto_share_insights": True,
            "threat_monitoring": True
        },
        "limits": {
            "max_posts_per_day": 3,
            "max_insights_per_hour": 50,
            "threat_retention_days": 90
        }
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📝 Created default config at {path}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Moltbook Agent Swarm Orchestrator")
    parser.add_argument("--config", "-c", type=Path, help="Configuration file path")
    parser.add_argument("--init-config", action="store_true", help="Create default config file")
    parser.add_argument("--status", action="store_true", help="Show swarm status")
    parser.add_argument("--command", help="Send command to agent (format: agent:command)")
    
    args = parser.parse_args()
    
    config_path = args.config or Path(__file__).parent.parent / "config" / "swarm.json"
    
    if args.init_config:
        create_default_config(config_path)
        return
    
    orchestrator = AgentSwarmOrchestrator(config_path)
    
    if args.status:
        status = await orchestrator.status()
        print(json.dumps(status, indent=2))
        return
    
    if args.command:
        parts = args.command.split(":", 1)
        if len(parts) != 2:
            print("Error: Command format should be 'agent:command'")
            return
        
        await orchestrator.initialize_agents()
        result = await orchestrator.send_command(parts[0], parts[1], {})
        print(json.dumps(result, indent=2))
        return
    
    # Setup signal handlers
    loop = asyncio.get_event_loop()
    
    def signal_handler(sig):
        print(f"\n📡 Received signal {sig.name}")
        asyncio.create_task(orchestrator.stop())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))
    
    # Start swarm
    try:
        await orchestrator.start()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        await orchestrator.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
