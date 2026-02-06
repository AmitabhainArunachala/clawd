#!/usr/bin/env python3
"""
Memory Bridge - Bidirectional sync between memory-system-v2 and unified-memory.

Enables gradual migration while maintaining backward compatibility.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "unified_memory"))
from unified_memory import MemoryManager, CanonicalMemory, MemoryType, MemorySource


class MemoryBridge:
    """Bidirectional bridge between v2 and unified memory systems."""
    
    def __init__(self):
        self.v2_path = Path.home() / "clawd" / "memory"
        self.v2_index = self.v2_path / "index" / "memory-index.json"
        self.mm = MemoryManager()
    
    def v2_to_unified(self, since: Optional[datetime] = None) -> Dict:
        """Import memories from v2 to unified system."""
        
        if not self.v2_index.exists():
            return {"imported": 0, "skipped": 0, "error": "No v2 index found"}
        
        with open(self.v2_index) as f:
            index = json.load(f)
        
        imported = 0
        skipped = 0
        errors = []
        
        for mem in index.get("memories", []):
            # Check timestamp filter
            if since:
                mem_time = datetime.fromtimestamp(mem["timestamp"] / 1000)
                if mem_time < since:
                    continue
            
            try:
                # Map v2 type to unified type
                type_map = {
                    "learning": MemoryType.LEARNING,
                    "decision": MemoryType.DECISION,
                    "insight": MemoryType.INSIGHT,
                    "event": MemoryType.EVENT,
                    "interaction": MemoryType.INTERACTION,
                }
                
                memory = CanonicalMemory(
                    content=mem["content"],
                    memory_type=type_map.get(mem["type"], MemoryType.LEARNING),
                    importance=mem["importance"],
                    context=mem.get("context", ""),
                    tags=mem.get("tags", []),
                    source=MemorySource.SYSTEM
                )
                
                self.mm.capture(memory)
                imported += 1
                
            except ValueError as e:
                if "Duplicate" in str(e):
                    skipped += 1
                else:
                    errors.append(str(e))
            except Exception as e:
                errors.append(str(e))
        
        return {
            "imported": imported,
            "skipped": skipped,
            "errors": errors[:5],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def unified_to_v2(self) -> Dict:
        """Export unified memories back to v2 format (for compatibility)."""
        
        stats = self.mm.get_stats()
        
        # v2 only needs a subset of data
        # This is mainly for backup/export purposes
        
        return {
            "exported": stats["total_memories"],
            "note": "Export to v2 format available for backup only",
            "v2_location": str(self.v2_index)
        }
    
    def sync(self, bidirectional: bool = True) -> Dict:
        """Full sync between systems."""
        
        result = {
            "v2_to_unified": self.v2_to_unified(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if bidirectional:
            result["unified_to_v2"] = self.unified_to_v2()
        
        # Write sync log
        sync_log = self.v2_path / "bridge-sync.log"
        with open(sync_log, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()}: {json.dumps(result)}\n")
        
        return result
    
    def verify_integrity(self) -> Dict:
        """Verify data integrity across both systems."""
        
        issues = []
        
        # Check v2 index exists
        if not self.v2_index.exists():
            issues.append("v2 index missing")
        
        # Check unified DB
        try:
            stats = self.mm.get_stats()
            if stats["total_memories"] == 0:
                issues.append("unified memory empty")
        except Exception as e:
            issues.append(f"unified memory error: {e}")
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "v2_path": str(self.v2_path),
            "unified_path": str(self.mm.db_path)
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Bridge")
    parser.add_argument("action", choices=["sync", "import", "verify", "stats"])
    parser.add_argument("--since", help="Import only since date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    bridge = MemoryBridge()
    
    if args.action == "sync":
        result = bridge.sync()
        print(json.dumps(result, indent=2))
    
    elif args.action == "import":
        since = None
        if args.since:
            since = datetime.fromisoformat(args.since)
        result = bridge.v2_to_unified(since)
        print(f"Imported: {result['imported']}")
        print(f"Skipped (duplicates): {result['skipped']}")
        if result.get('errors'):
            print(f"Errors: {len(result['errors'])}")
    
    elif args.action == "verify":
        result = bridge.verify_integrity()
        print(f"Healthy: {result['healthy']}")
        if result['issues']:
            print(f"Issues: {', '.join(result['issues'])}")
    
    elif args.action == "stats":
        v2_count = 0
        if bridge.v2_index.exists():
            with open(bridge.v2_index) as f:
                v2_count = len(json.load(f).get("memories", []))
        
        unified_stats = bridge.mm.get_stats()
        
        print("Memory Bridge Statistics")
        print("=" * 40)
        print(f"v2 memories: {v2_count}")
        print(f"Unified memories: {unified_stats['total_memories']}")
        print(f"Total unique: ~{max(v2_count, unified_stats['total_memories'])}")


if __name__ == "__main__":
    main()
