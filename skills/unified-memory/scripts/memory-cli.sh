#!/usr/bin/env python3
"""
Unified Memory CLI - Three-layer memory system interface.

Usage:
    ./memory-cli.sh capture --type insight --importance 9 --content "..."
    ./memory-cli.sh search "knowledge architecture"
    ./memory-cli.sh insights
    ./memory-cli.sh stats
"""

import argparse
import sys
from pathlib import Path

# Add skill to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "unified_memory"))

from unified_memory import MemoryManager, CanonicalMemory, MemoryType, MemorySource


def cmd_capture(args):
    """Capture a new memory."""
    mm = MemoryManager()
    
    memory = CanonicalMemory(
        content=args.content,
        memory_type=MemoryType(args.type),
        importance=args.importance,
        context=args.context,
        tags=args.tags.split(",") if args.tags else [],
        source=MemorySource(args.source)
    )
    
    try:
        memory_id = mm.capture(memory, related_to=args.related)
        print(f"✓ Captured: {memory_id}")
        return 0
    except ValueError as e:
        print(f"✗ Error: {e}")
        return 1


def cmd_search(args):
    """Search memories."""
    mm = MemoryManager()
    
    results = mm.search(
        query=args.query,
        search_type=args.search_type,
        limit=args.limit,
        min_importance=args.min_importance
    )
    
    print(f"Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        m = result.memory
        sim_str = f" [sim:{result.similarity:.2f}]" if result.similarity else ""
        print(f"{i}. [{m.memory_type.value}] {m.content[:60]}...{sim_str}")
        print(f"   ID: {m.id} | Importance: {m.importance} | Tags: {', '.join(m.tags[:3])}")
        print()
    
    return 0


def cmd_related(args):
    """Get related memories."""
    mm = MemoryManager()
    
    related = mm.get_related(args.memory_id, max_hops=args.hops)
    
    print(f"Related memories (up to {args.hops} hops):\n")
    for mem_id, strength in related[:args.limit]:
        memory = mm._row_to_memory(
            mm._get_row(mem_id)  # This won't work directly, need to fix
        )
        print(f"  {mem_id[:8]}... (strength: {strength:.2f})")
    
    return 0


def cmd_insights(args):
    """Find emergent insights."""
    mm = MemoryManager()
    
    insights = mm.find_insights()
    
    print(f"Found {len(insights)} insights:\n")
    for insight in insights:
        print(f"[{insight['type'].upper()}] {insight['insight']}")
        if 'count' in insight:
            print(f"  Count: {insight['count']}")
        print()
    
    return 0


def cmd_stats(args):
    """Show memory statistics."""
    mm = MemoryManager()
    
    stats = mm.get_stats()
    
    print("Memory System Statistics")
    print("=" * 40)
    print(f"Total memories: {stats['total_memories']}")
    print(f"References: {stats['total_references']}")
    print(f"Reference density: {stats['reference_density']:.2f}")
    print(f"Database: {stats['db_path']}")
    print()
    print("By type:")
    for mem_type, count in stats['by_type'].items():
        print(f"  {mem_type}: {count}")
    
    return 0


def cmd_bridge(args):
    """Bridge with memory-system-v2."""
    import json
    from pathlib import Path
    
    # Read v2 memories
    v2_path = Path.home() / "clawd" / "memory"
    v2_index = v2_path / "index" / "memory-index.json"
    
    if not v2_index.exists():
        print("No memory-system-v2 found")
        return 1
    
    mm = MemoryManager()
    
    with open(v2_index) as f:
        index = json.load(f)
    
    imported = 0
    for mem in index.get("memories", []):
        try:
            memory = CanonicalMemory(
                content=mem["content"],
                memory_type=MemoryType(mem["type"]),
                importance=mem["importance"],
                context=mem.get("context", ""),
                tags=mem.get("tags", []),
                source=MemorySource.SYSTEM
            )
            mm.capture(memory)
            imported += 1
        except ValueError:
            pass  # Duplicate
    
    print(f"✓ Imported {imported} memories from v2")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Unified Memory CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Capture
    capture_cmd = subparsers.add_parser("capture", help="Capture a memory")
    capture_cmd.add_argument("--type", required=True, choices=[t.value for t in MemoryType])
    capture_cmd.add_argument("--importance", type=int, required=True)
    capture_cmd.add_argument("--content", required=True)
    capture_cmd.add_argument("--context")
    capture_cmd.add_argument("--tags")
    capture_cmd.add_argument("--source", default="agent", choices=[s.value for s in MemorySource])
    capture_cmd.add_argument("--related", nargs="*", help="Related memory IDs")
    capture_cmd.set_defaults(func=cmd_capture)
    
    # Search
    search_cmd = subparsers.add_parser("search", help="Search memories")
    search_cmd.add_argument("query")
    search_cmd.add_argument("--search-type", dest="search_type", choices=["text", "semantic", "hybrid"], default="hybrid")
    search_cmd.add_argument("--limit", type=int, default=10)
    search_cmd.add_argument("--min-importance", type=int, default=1)
    search_cmd.set_defaults(func=cmd_search)
    
    # Related
    related_cmd = subparsers.add_parser("related", help="Get related memories")
    related_cmd.add_argument("memory_id")
    related_cmd.add_argument("--hops", type=int, default=2)
    related_cmd.add_argument("--limit", type=int, default=10)
    related_cmd.set_defaults(func=cmd_related)
    
    # Insights
    insights_cmd = subparsers.add_parser("insights", help="Find emergent insights")
    insights_cmd.set_defaults(func=cmd_insights)
    
    # Stats
    stats_cmd = subparsers.add_parser("stats", help="Show statistics")
    stats_cmd.set_defaults(func=cmd_stats)
    
    # Bridge
    bridge_cmd = subparsers.add_parser("bridge", help="Bridge with memory-system-v2")
    bridge_cmd.set_defaults(func=cmd_bridge)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
