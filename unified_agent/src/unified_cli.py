#!/usr/bin/env python3
"""
Unified Agent CLI
=================

Command-line interface for the Unified Agent system.
Demonstrates real agent coordination with Chaiwala.

Usage:
    unified-cli status              # Show agent status
    unified-cli agents              # List all agents
    unified-cli delegate <task>     # Delegate task to best agent
    unified-cli health              # Show detailed health
    unified-cli demo                # Run build demo
    unified-cli watch               # Watch agent activity

Author: DHARMIC_CLAW + WARP_REGENT
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path.home() / '.chaiwala'))

from message_bus import MessageBus
from unified_agent import (
    DHARMIC_CLAW_Agent, WARP_REGENT_Agent, 
    UnifiedAgentOrchestrator
)


def cmd_status(args):
    """Show agent status"""
    print("=" * 60)
    print("🤖 UNIFIED AGENT SYSTEM - Status")
    print("=" * 60)
    
    bus = MessageBus()
    
    # Get all agents
    agents = bus.list_agents()
    
    print(f"\n📊 Known Agents: {len(agents)}")
    print("-" * 60)
    
    for agent in agents:
        status_icon = "🟢" if agent['status'] == 'online' else "🔴"
        age = agent.get('age_minutes', 0)
        print(f"{status_icon} {agent['agent_id']}")
        print(f"   Status: {agent['status']}")
        print(f"   Last seen: {agent['last_seen']}")
        print(f"   Age: {age:.1f} minutes")
        print()
        
    # Get message stats
    stats = bus.get_stats()
    print("📨 Message Statistics:")
    print(f"   Total messages: {stats['total_messages']}")
    print(f"   Unread messages: {stats['unread_messages']}")
    print(f"   Database: {stats['db_path']}")


def cmd_agents(args):
    """List agents with capabilities"""
    print("=" * 60)
    print("🤖 AGENT CAPABILITIES")
    print("=" * 60)
    
    # Create agent instances to show capabilities
    dc = DHARMIC_CLAW_Agent()
    wr = WARP_REGENT_Agent()
    
    print("\n📘 DHARMIC_CLAW:")
    print("   Description: Research, memory, synthesis")
    print("   Capabilities:")
    for name, cap in dc.capabilities.items():
        print(f"      • {name}: {cap.description}")
        
    print("\n📗 WARP_REGENT:")
    print("   Description: Execution, integration, monitoring")
    print("   Capabilities:")
    for name, cap in wr.capabilities.items():
        print(f"      • {name}: {cap.description}")


def cmd_delegate(args):
    """Delegate a task to the best agent"""
    print("=" * 60)
    print("📤 TASK DELEGATION")
    print("=" * 60)
    
    task_type = args.task_type
    payload = {'request': args.request, 'timestamp': datetime.now().isoformat()}
    
    print(f"\nTask Type: {task_type}")
    print(f"Request: {args.request}")
    
    # Create orchestrator and route
    orch = UnifiedAgentOrchestrator()
    dc = DHARMIC_CLAW_Agent()
    wr = WARP_REGENT_Agent()
    orch.register_agent(dc)
    orch.register_agent(wr)
    
    target = orch.route_task(task_type, payload)
    
    if target:
        print(f"\n✅ Task routed to: {target}")
        print(f"   Message sent via Chaiwala bus")
        
        # Show the agent's capabilities
        agent = orch.agents.get(target)
        if agent:
            print(f"\n   Agent capabilities:")
            for cap_name in agent.capabilities:
                print(f"      • {cap_name}")
    else:
        print(f"\n❌ No agent found for task type: {task_type}")
        print("   Available task types: research, document, review, execute, email, monitor")


def cmd_health(args):
    """Show detailed health status"""
    print("=" * 60)
    print("🏥 AGENT HEALTH CHECK")
    print("=" * 60)
    
    dc = DHARMIC_CLAW_Agent()
    wr = WARP_REGENT_Agent()
    
    dc.start()
    wr.start()
    
    print("\n📘 DHARMIC_CLAW:")
    health = dc.get_detailed_health()
    print(f"   State: {health['state']}")
    print(f"   Capabilities: {len(health['capabilities'])}")
    print(f"   Load: {health['load']:.2f}")
    
    if 'system_health' in health:
        sys_health = health['system_health']
        print(f"   System: {sys_health.get('status', 'unknown')}")
        
    print("\n📗 WARP_REGENT:")
    health = wr.get_detailed_health()
    print(f"   State: {health['state']}")
    print(f"   Capabilities: {len(health['capabilities'])}")
    print(f"   Load: {health['load']:.2f}")
    
    if 'system_health' in health:
        sys_health = health['system_health']
        print(f"   System: {sys_health.get('status', 'unknown')}")


def cmd_demo(args):
    """Run build demo"""
    print("=" * 60)
    print("🎬 UNIFIED AGENT DEMO")
    print("=" * 60)
    print("\nSimulating a real build task with agent coordination...")
    print()
    
    # Create orchestrator
    orch = UnifiedAgentOrchestrator()
    dc = DHARMIC_CLAW_Agent()
    wr = WARP_REGENT_Agent()
    orch.register_agent(dc)
    orch.register_agent(wr)
    
    # Simulate build workflow
    steps = [
        ("Research dependencies", "research", dc.agent_id),
        ("Execute build command", "execute", wr.agent_id),
        ("Monitor build health", "monitor", wr.agent_id),
        ("Document results", "document", dc.agent_id),
    ]
    
    for i, (desc, task_type, expected_agent) in enumerate(steps, 1):
        print(f"Step {i}: {desc}")
        print(f"   Task type: {task_type}")
        
        target = orch.route_task(task_type, {'step': i, 'description': desc})
        
        if target == expected_agent:
            print(f"   ✅ Routed to {target} (correct)")
        else:
            print(f"   ⚠️  Routed to {target} (expected {expected_agent})")
            
        time.sleep(0.5)
        
    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("   All tasks routed to appropriate agents")
    print("   Chaiwala bus used for coordination")


def cmd_watch(args):
    """Watch agent activity"""
    print("=" * 60)
    print("👁️  WATCHING AGENT ACTIVITY")
    print("=" * 60)
    print(f"\nMonitoring for {args.duration} seconds...")
    print("Press Ctrl+C to stop\n")
    
    bus = MessageBus()
    my_agent = 'cli_watcher'
    
    try:
        for i in range(args.duration):
            # Send heartbeat
            bus.heartbeat(my_agent)
            
            # Check for messages
            messages = bus.receive(agent_id=my_agent, status='unread', limit=5)
            
            for msg in messages:
                print(f"[{datetime.now().strftime('%H:%M:%S')}]")
                print(f"  From: {msg['from']}")
                print(f"  Subject: {msg['subject']}")
                print(f"  Priority: {msg['priority']}")
                print()
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")


def main():
    parser = argparse.ArgumentParser(
        description="Unified Agent System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  unified-cli status
  unified-cli agents
  unified-cli delegate research "Analyze AI trends"
  unified-cli health
  unified-cli demo
  unified-cli watch --duration 60
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # status
    status_parser = subparsers.add_parser('status', help='Show agent status')
    
    # agents
    agents_parser = subparsers.add_parser('agents', help='List agents')
    
    # delegate
    delegate_parser = subparsers.add_parser('delegate', help='Delegate task')
    delegate_parser.add_argument('task_type', choices=['research', 'document', 'review', 'execute', 'email', 'monitor'])
    delegate_parser.add_argument('request', help='Task request description')
    
    # health
    health_parser = subparsers.add_parser('health', help='Show health status')
    
    # demo
    demo_parser = subparsers.add_parser('demo', help='Run build demo')
    
    # watch
    watch_parser = subparsers.add_parser('watch', help='Watch agent activity')
    watch_parser.add_argument('--duration', type=int, default=30, help='Duration in seconds')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        cmd_status(args)
    elif args.command == 'agents':
        cmd_agents(args)
    elif args.command == 'delegate':
        cmd_delegate(args)
    elif args.command == 'health':
        cmd_health(args)
    elif args.command == 'demo':
        cmd_demo(args)
    elif args.command == 'watch':
        cmd_watch(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
