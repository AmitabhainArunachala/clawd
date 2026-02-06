#!/usr/bin/env python3
"""
Unified Memory System - Three-layer memory architecture.

Canonical + Mem0 (vector) + Strange Loop layers in one interface.
"""

import sqlite3
import json
import hashlib
import uuid
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple, Set
import sys

# Config
DEFAULT_DB_PATH = Path.home() / "clawd" / "memory" / "unified_memory.db"


class MemoryType(Enum):
    LEARNING = "learning"
    DECISION = "decision"
    INSIGHT = "insight"
    EVENT = "event"
    INTERACTION = "interaction"
    META = "meta"


class MemorySource(Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    EXTERNAL = "external"
    INFERRED = "inferred"


class ReferenceType(Enum):
    RELATED = "related"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    DERIVED_FROM = "derived_from"
    META = "meta"


@dataclass
class CanonicalMemory:
    content: str
    memory_type: MemoryType
    importance: int
    context: Optional[str] = None
    tags: List[str] = None
    source: MemorySource = MemorySource.AGENT
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.tags is None:
            self.tags = []
    
    @property
    def content_hash(self) -> str:
        normalized = f"{self.memory_type.value}:{self.content.lower().strip()}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]


@dataclass
class SearchResult:
    memory: CanonicalMemory
    similarity: Optional[float] = None
    score: float = 0.0


# SQL Schema
SCHEMA_SQL = """
-- Core memories table
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    memory_type TEXT NOT NULL,
    importance INTEGER NOT NULL CHECK(importance BETWEEN 1 AND 10),
    content TEXT NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,
    context TEXT,
    source TEXT NOT NULL,
    embedding_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed DATETIME
);

-- Full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content, context, tags,
    content_rowid=id
);

-- Tags
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS memory_tags (
    memory_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (memory_id, tag_id)
);

-- Strange Loop: Memory references
CREATE TABLE IF NOT EXISTS memory_references (
    source_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    target_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    reference_type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_id, target_id)
);

-- Mem0: Vector embeddings
CREATE TABLE IF NOT EXISTS embeddings (
    id TEXT PRIMARY KEY,
    memory_id TEXT UNIQUE REFERENCES memories(id) ON DELETE CASCADE,
    vector BLOB NOT NULL,
    model_version TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Access log
CREATE TABLE IF NOT EXISTS access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT REFERENCES memories(id),
    access_type TEXT NOT NULL,
    query_context TEXT,
    accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance DESC);
CREATE INDEX IF NOT EXISTS idx_refs_source ON memory_references(source_id);
CREATE INDEX IF NOT EXISTS idx_refs_target ON memory_references(target_id);
"""


class SimpleEmbedder:
    """Simple local embedding using TF-IDF-like approach."""
    
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        self.vocab = {}
        self._initialized = False
    
    def _get_vocab(self, texts: List[str]):
        """Build vocabulary from texts."""
        import re
        words = set()
        for text in texts:
            words.update(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
        self.vocab = {w: i for i, w in enumerate(sorted(words))}
        self._initialized = True
    
    def embed(self, text: str) -> np.ndarray:
        """Create simple embedding."""
        import re
        
        # Simple bag-of-words embedding
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        vector = np.zeros(self.dimensions)
        
        for word in words:
            idx = hash(word) % self.dimensions
            vector[idx] += 1
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector


class MemoryManager:
    """Unified memory manager - three layers in one interface."""
    
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedder = SimpleEmbedder()
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA_SQL)
    
    def capture(self, memory: CanonicalMemory, related_to: List[str] = None) -> str:
        """Capture memory across all layers."""
        
        # 1. Store in canonical layer
        with sqlite3.connect(self.db_path) as conn:
            # Check for duplicates
            cursor = conn.execute(
                "SELECT id FROM memories WHERE content_hash = ?",
                (memory.content_hash,)
            )
            if cursor.fetchone():
                raise ValueError(f"Duplicate memory: {memory.content_hash}")
            
            # Insert memory
            conn.execute("""
                INSERT INTO memories 
                (id, timestamp, memory_type, importance, content, content_hash,
                 context, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id, memory.timestamp.isoformat(), memory.memory_type.value,
                memory.importance, memory.content, memory.content_hash,
                memory.context, memory.source.value, memory.timestamp.isoformat(),
                memory.timestamp.isoformat()
            ))
            
            # Insert tags
            for tag in set(t.lower() for t in memory.tags):
                conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                conn.execute("""
                    INSERT INTO memory_tags (memory_id, tag_id)
                    SELECT ?, id FROM tags WHERE name = ?
                """, (memory.id, tag))
            
            conn.commit()
        
        # 2. Generate embedding
        embedding_text = f"{memory.content} {memory.context or ''} {' '.join(memory.tags)}"
        vector = self.embedder.embed(embedding_text)
        
        embedding_id = str(uuid.uuid4())[:16]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO embeddings (id, memory_id, vector, model_version, dimensions)
                VALUES (?, ?, ?, ?, ?)
            """, (embedding_id, memory.id, vector.tobytes(), "simple-v1", self.embedder.dimensions))
            conn.commit()
        
        # 3. Create references (strange loops)
        if related_to:
            with sqlite3.connect(self.db_path) as conn:
                for related_id in related_to:
                    conn.execute("""
                        INSERT OR IGNORE INTO memory_references 
                        (source_id, target_id, reference_type, strength)
                        VALUES (?, ?, ?, ?)
                    """, (memory.id, related_id, ReferenceType.RELATED.value, 1.0))
                conn.commit()
        
        return memory.id
    
    def search(self, query: str, search_type: str = "hybrid", 
               limit: int = 10, min_importance: int = 1) -> List[SearchResult]:
        """Hybrid search across all layers."""
        
        results = {}
        
        # Text search (FTS)
        if search_type in ("text", "hybrid"):
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT m.* FROM memories m
                    JOIN memories_fts fts ON m.id = fts.rowid
                    WHERE memories_fts MATCH ? AND m.importance >= ?
                    ORDER BY m.importance DESC, rank
                    LIMIT ?
                """, (query, min_importance, limit * 2)).fetchall()
                
                for row in rows:
                    memory = self._row_to_memory(row)
                    results[memory.id] = SearchResult(memory=memory, score=0.5)
        
        # Semantic search
        if search_type in ("semantic", "hybrid"):
            query_vec = self.embedder.embed(query)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT e.memory_id, e.vector FROM embeddings e
                    JOIN memories m ON e.memory_id = m.id
                    WHERE m.importance >= ?
                """, (min_importance,)).fetchall()
                
                for row in rows:
                    mem_vec = np.frombuffer(row['vector'], dtype=np.float64)
                    if len(mem_vec) == 0:
                        continue
                    
                    # Cosine similarity
                    similarity = np.dot(query_vec, mem_vec)
                    
                    if similarity > 0.3:  # Threshold
                        mem_row = conn.execute(
                            "SELECT * FROM memories WHERE id = ?", (row['memory_id'],)
                        ).fetchone()
                        
                        if mem_row:
                            memory = self._row_to_memory(mem_row)
                            if memory.id in results:
                                results[memory.id].similarity = similarity
                                results[memory.id].score += similarity * 0.5
                            else:
                                results[memory.id] = SearchResult(
                                    memory=memory, similarity=similarity, score=similarity
                                )
        
        # Sort by score
        sorted_results = sorted(results.values(), key=lambda x: x.score, reverse=True)
        
        # Update access counts
        for result in sorted_results[:limit]:
            self._update_access(result.memory.id)
        
        return sorted_results[:limit]
    
    def get_related(self, memory_id: str, max_hops: int = 2) -> List[Tuple[str, float]]:
        """Get related memories via strange loop references."""
        
        related = {}
        current = {memory_id: 1.0}
        visited = {memory_id}
        
        for hop in range(max_hops):
            next_level = {}
            for node_id, strength in current.items():
                with sqlite3.connect(self.db_path) as conn:
                    rows = conn.execute("""
                        SELECT target_id, strength FROM memory_references WHERE source_id = ?
                        UNION
                        SELECT source_id, strength FROM memory_references WHERE target_id = ?
                    """, (node_id, node_id)).fetchall()
                    
                    for target_id, ref_strength in rows:
                        if target_id not in visited:
                            visited.add(target_id)
                            new_strength = strength * ref_strength
                            next_level[target_id] = new_strength
                            related[target_id] = new_strength
            current = next_level
        
        return sorted(related.items(), key=lambda x: x[1], reverse=True)
    
    def find_insights(self) -> List[Dict]:
        """Find emergent insights from memory patterns."""
        
        insights = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Find dense clusters
            rows = conn.execute("""
                SELECT m1.memory_type, COUNT(*) as count FROM memories m1
                WHERE m1.timestamp >= datetime('now', '-7 days')
                GROUP BY m1.memory_type
                ORDER BY count DESC
            """).fetchall()
            
            for row in rows:
                if row[1] >= 3:
                    insights.append({
                        "type": "cluster",
                        "memory_type": row[0],
                        "count": row[1],
                        "insight": f"Strong activity in {row[0]} ({row[1]} memories)"
                    })
            
            # Find orphans (no connections)
            orphan_count = conn.execute("""
                SELECT COUNT(*) FROM memories m
                LEFT JOIN memory_references r ON m.id = r.source_id OR m.id = r.target_id
                WHERE r.source_id IS NULL
            """).fetchone()[0]
            
            if orphan_count > 0:
                total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
                orphan_pct = orphan_count / max(total, 1)
                if orphan_pct > 0.2:
                    insights.append({
                        "type": "orphans",
                        "count": orphan_count,
                        "percentage": f"{orphan_pct:.1%}",
                        "insight": f"{orphan_count} orphaned memories need connections"
                    })
        
        return insights
    
    def get_stats(self) -> Dict:
        """Get memory system statistics."""
        
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            by_type = conn.execute("""
                SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type
            """).fetchall()
            refs = conn.execute("SELECT COUNT(*) FROM memory_references").fetchone()[0]
            
        return {
            "total_memories": total,
            "by_type": {t: c for t, c in by_type},
            "total_references": refs,
            "reference_density": refs / max(total, 1),
            "db_path": str(self.db_path)
        }
    
    def _row_to_memory(self, row: sqlite3.Row) -> CanonicalMemory:
        """Convert DB row to CanonicalMemory."""
        return CanonicalMemory(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            memory_type=MemoryType(row['memory_type']),
            importance=row['importance'],
            content=row['content'],
            context=row['context'],
            source=MemorySource(row['source'])
        )
    
    def _update_access(self, memory_id: str):
        """Update access statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), memory_id))
            conn.commit()


if __name__ == "__main__":
    # Test
    mm = MemoryManager()
    
    # Capture test memories
    for i in range(5):
        mem = CanonicalMemory(
            content=f"Test memory about AI research {i}",
            memory_type=MemoryType.INSIGHT,
            importance=8,
            tags=["ai", "research", f"test{i}"]
        )
        try:
            mm.capture(mem)
            print(f"✓ Captured: {mem.id[:8]}")
        except ValueError:
            pass
    
    # Search
    results = mm.search("AI research", limit=3)
    print(f"\n✓ Found {len(results)} results")
    
    # Stats
    stats = mm.get_stats()
    print(f"\n✓ Stats: {stats}")
