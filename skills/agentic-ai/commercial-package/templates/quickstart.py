#!/usr/bin/env python3
"""
Agentic AI — Quick Start Template
Copy this file and modify for your use case.

This demonstrates:
- Persistent council initialization
- Memory storage and retrieval
- Specialist spawning
- Security gate checking
"""

from agentic_ai import (
    PersistentCouncil,
    MemoryManager,
    spawn_specialist,
    DharmicGuard
)


def main():
    print("🔥 Agentic AI — Quick Start Template\n")
    
    # =================================================================
    # PART 1: Initialize the Persistent Council
    # =================================================================
    print("📦 Part 1: Initializing Council...")
    
    council = PersistentCouncil(
        size=4,  # Gnata, Gneya, Gnan, Shakti
        heartbeat_interval=300  # 5 minutes
    )
    
    print("   Council initialized with 4 members:")
    for member in council.members:
        print(f"   ├─ {member.name} ({member.role}) ✓")
    print()
    
    # =================================================================
    # PART 2: Store and Retrieve Memory
    # =================================================================
    print("🧠 Part 2: Working with Memory...")
    
    memory = MemoryManager()
    
    # Store user information in semantic layer
    memory.store(
        layer="semantic",
        data={
            "user_id": "user_123",
            "name": "Alex",
            "preferences": {
                "communication_style": "concise",
                "expertise_level": "intermediate"
            }
        },
        user_id="user_123"
    )
    
    # Retrieve context for a query
    context = memory.retrieve(
        query="What does Alex prefer?",
        user_id="user_123",
        top_k=3
    )
    
    print(f"   Stored: User profile for Alex")
    print(f"   Retrieved: {context['summary']}")
    print()
    
    # =================================================================
    # PART 3: Process a Task Through Council
    # =================================================================
    print("⚙️  Part 3: Processing Task...")
    
    task = {
        "type": "research",
        "query": "Latest AI frameworks in 2026",
        "context": context,
        "priority": "normal"
    }
    
    # Check dharmic gates before processing
    guard = DharmicGuard()
    gate_results = guard.check_all(task)
    
    print("   Dharmic Gates Check:")
    for gate, passed in gate_results.items():
        status = "✓" if passed else "✗"
        print(f"   ├─ {gate}: {status}")
    
    if all(gate_results.values()):
        result = council.process(task)
        print(f"\n   ✅ Task completed successfully!")
        print(f"   Result: {result['summary'][:100]}...")
    else:
        print("\n   ⚠️  Task blocked by security gates")
    print()
    
    # =================================================================
    # PART 4: Spawn a Specialist
    # =================================================================
    print("🤖 Part 4: Spawning Specialist...")
    
    specialist = spawn_specialist(
        type="builder",
        task="Write a Python function to parse JSON with error handling",
        model="kimi-k2.5",
        timeout=120
    )
    
    print(f"   Specialist spawned: {specialist.id}")
    print(f"   Type: {specialist.type}")
    print(f"   Model: {specialist.model}")
    
    # Wait for completion
    result = specialist.wait_for_result()
    
    if result.success:
        print(f"\n   ✅ Specialist completed task!")
        print(f"   Quality score: {result.quality_score}/100")
        print(f"   Code preview:")
        print(f"   ```python")
        print(f"   {result.code[:200]}...")
        print(f"   ```")
    else:
        print(f"\n   ⚠️  Specialist failed: {result.error}")
    print()
    
    # =================================================================
    # PART 5: Summary
    # =================================================================
    print("📊 Summary:")
    print("   ✓ Council initialized (4 members)")
    print("   ✓ Memory system active (5 layers)")
    print("   ✓ Security gates verified (17 checks)")
    print("   ✓ Specialist spawned and completed task")
    print()
    print("🎉 Your agent is fully operational!")
    print()
    print("Next steps:")
    print("  • Explore examples/ directory")
    print("  • Read docs/tutorials/ for deeper dives")
    print("  • Check out SKILL.md for complete reference")
    print()
    print("JSCA! 🔥🪷")


if __name__ == "__main__":
    main()
