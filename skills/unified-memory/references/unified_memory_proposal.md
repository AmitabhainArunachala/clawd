# Unified Memory Architecture Proposal
## SQLite-Based Memory System with Strange Loops, Canonical Form, and Mem0 Layer

**Status:** Design Proposal  
**Date:** 2026-02-05  
**Target:** Replace/Enhance memory-system-v2 with unified architecture

---

## Executive Summary

Current memory-system-v2 uses file-based JSON indexing with bash/jq. While fast (<20ms), it lacks:
- Semantic embeddings for true similarity search
- Self-referential memory (strange loops)
- Graph relationships between memories
- Scalability beyond ~10K entries

This proposal introduces a **three-layer unified memory system** using SQLite with vector extensions:

1. **Canonical Layer** - Normalized, structured memory storage
2. **Strange Loop Layer** - Self-referential, emergent memory properties
3. **Mem0 Layer** - Vector embeddings for semantic retrieval

---

## Core Concepts

### 1. Canonical Memory (canonical_memory.py)
**Purpose:** Standardized, normalized memory format ensuring consistency across all memory operations.

**Key Features:**
- Schema-enforced memory structure
- Type normalization (learning/decision/insight/event/interaction)
- Entity extraction and linking
- Deduplication via content hashing
- Temporal versioning

**Schema:**
```python
@dataclass
class CanonicalMemory:
    id: str                    # UUID v4
    timestamp: datetime        # UTC
    memory_type: MemoryType    # Enum: LEARNING, DECISION, INSIGHT, EVENT, INTERACTION
    importance: int           # 1-10 scale
    content: str              # Normalized text
    content_hash: str         # SHA256 for dedup
    tags: List[str]           # Normalized tags
    entities: EntityGraph     # Extracted people, projects, skills
    context: str              # Situational context
    source: MemorySource      # Origin (user, agent, system, external)
    embedding_id: Optional[str]  # Reference to Mem0 layer
    loop_refs: List[str]      # Strange loop references
    created_at: datetime
    updated_at: datetime
    access_count: int         # For importance decay/boost
    last_accessed: datetime
```

### 2. Strange Loop Memory (strange_loop_memory.py)
**Purpose:** Self-referential memory system where memories can reference other memories, creating emergent properties and higher-order insights.

**Key Features:**
- Memory-to-memory references (graph edges)
- Pattern emergence detection
- Self-observation capabilities (memories about memories)
- Recursive importance propagation
- Contradiction detection

**Concepts:**
- **Direct Reference:** Memory A mentions Memory B
- **Emergent Pattern:** Cluster of related memories reveals new insight
- **Meta-Memory:** Memory about the memory system itself
- **Strange Loop:** Memory that indirectly references itself through a chain

**Strange Loop Detection:**
```python
class StrangeLoopDetector:
    """Detects circular references and emergent patterns in memory graph."""
    
    def detect_loops(self, memory_id: str) -> List[List[str]]:
        """Find all cyclic paths starting from memory_id."""
        
    def find_emergent_insights(self) -> List[CanonicalMemory]:
        """Analyze memory clusters to generate new insights."""
        
    def propagate_importance(self, source_id: str, delta: int):
        """Recursively adjust importance through reference chains."""
```

### 3. Mem0 Layer (mem0_layer.py)
**Purpose:** Vector embedding storage and semantic search, inspired by mem0.ai's approach to AI memory.

**Key Features:**
- Text embedding generation (local or API)
- Vector similarity search
- Context-aware retrieval
- Memory decay and reinforcement
- Multi-modal support (text, code, image descriptions)

**Implementation:**
```python
class Mem0Layer:
    """Vector memory with semantic search capabilities."""
    
    def __init__(self, embedding_model: str = "local"):
        self.embedder = self._load_embedder(embedding_model)
        
    def embed(self, memory: CanonicalMemory) -> np.ndarray:
        """Generate embedding for memory content."""
        
    def search_similar(
        self, 
        query: str, 
        top_k: int = 10,
        threshold: float = 0.7
    ) -> List[SearchResult]:
        """Semantic similarity search."""
        
    def get_context_memories(
        self, 
        current_context: str,
        recent_memories: List[str],
        max_results: int = 5
    ) -> List[CanonicalMemory]:
        """Retrieve memories relevant to current working context."""
```

---

## Unified SQLite Schema

### Tables

```sql
-- Core memory table (Canonical Layer)
CREATE TABLE memories (
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
    last_accessed DATETIME,
    FOREIGN KEY (embedding_id) REFERENCES embeddings(id)
);

-- Full-text search virtual table
CREATE VIRTUAL TABLE memories_fts USING fts5(
    content,
    context,
    tags,
    content_rowid=id
);

-- Tags (normalized)
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 0
);

CREATE TABLE memory_tags (
    memory_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (memory_id, tag_id)
);

-- Entities (people, projects, skills)
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- person, project, skill, organization
    normalized_name TEXT UNIQUE NOT NULL
);

CREATE TABLE memory_entities (
    memory_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
    role TEXT,  -- subject, object, mentioned
    PRIMARY KEY (memory_id, entity_id)
);

-- Strange Loop: Memory references (graph edges)
CREATE TABLE memory_references (
    source_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    target_id TEXT REFERENCES memories(id) ON DELETE CASCADE,
    reference_type TEXT NOT NULL,  -- related, contradicts, supports, supersedes
    strength REAL DEFAULT 1.0,     -- 0.0 to 1.0
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_id, target_id)
);

-- Mem0 Layer: Vector embeddings
CREATE TABLE embeddings (
    id TEXT PRIMARY KEY,
    memory_id TEXT UNIQUE REFERENCES memories(id) ON DELETE CASCADE,
    vector BLOB NOT NULL,          -- Serialized numpy array or SQLite vec extension
    model_version TEXT NOT NULL,   -- Embedding model used
    dimensions INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Virtual table for vector search (using sqlite-vec extension)
CREATE VIRTUAL TABLE vec_memories USING vec0(
    embedding_id TEXT PRIMARY KEY,
    vector FLOAT[384]  -- Dimension depends on embedding model
);

-- Memory decay and reinforcement tracking
CREATE TABLE memory_vitals (
    memory_id TEXT PRIMARY KEY REFERENCES memories(id) ON DELETE CASCADE,
    base_importance INTEGER NOT NULL,
    current_importance REAL NOT NULL,
    decay_rate REAL DEFAULT 0.01,     -- Daily decay
    last_reinforced DATETIME,
    reinforcement_count INTEGER DEFAULT 0
);

-- Access patterns for optimization
CREATE TABLE access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT REFERENCES memories(id),
    access_type TEXT NOT NULL,        -- search, recall, suggestion
    query_context TEXT,
    accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Consolidation tracking
CREATE TABLE consolidation_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    window_type TEXT NOT NULL,        -- daily, weekly, monthly
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    memory_count INTEGER,
    insights_generated INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_memories_timestamp ON memories(timestamp);
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_importance ON memories(importance DESC);
CREATE INDEX idx_memories_source ON memories(source);
CREATE INDEX idx_memories_hash ON memories(content_hash);

-- Strange Loop indexes
CREATE INDEX idx_refs_source ON memory_references(source_id);
CREATE INDEX idx_refs_target ON memory_references(target_id);
CREATE INDEX idx_refs_type ON memory_references(reference_type);

-- Mem0 indexes (vector search handled by virtual table)
CREATE INDEX idx_embeddings_model ON embeddings(model_version);

-- Access pattern indexes
CREATE INDEX idx_access_log_memory ON access_log(memory_id);
CREATE INDEX idx_access_log_time ON access_log(accessed_at);
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     UNIFIED MEMORY SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   STRANGE    │    │   CANONICAL  │    │     MEM0     │      │
│  │    LOOP      │◄──►│    MEMORY    │◄──►│    LAYER     │      │
│  │   LAYER      │    │    LAYER     │    │   (Vector)   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         ▲                   ▲                   ▲               │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                    ┌────────┴────────┐                         │
│                    │  MEMORY MANAGER │                         │
│                    │   (Orchestrator)│                         │
│                    └────────┬────────┘                         │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐              │
│         ▼                   ▼                   ▼              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   SQLite     │    │   Embedding  │    │   Entity     │      │
│  │   Storage    │    │    Model     │    │  Extractor   │      │
│  │  (+vec ext)  │    │ (local/API)  │    │   (spacy/    │      │
│  └──────────────┘    └──────────────┘    │    LLM)      │      │
│                                           └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
│  capture() │ search() │ recall() │ consolidate() │ reflect()    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation: Python Modules

### 1. `unified_memory/__init__.py`

```python
"""Unified Memory System - Three-layer memory architecture."""

from .canonical_memory import CanonicalMemory, MemoryType, MemorySource
from .strange_loop_memory import StrangeLoopLayer, ReferenceType
from .mem0_layer import Mem0Layer, EmbeddingModel
from .memory_manager import MemoryManager

__version__ = "3.0.0"
__all__ = [
    "MemoryManager",
    "CanonicalMemory", 
    "MemoryType",
    "MemorySource",
    "StrangeLoopLayer",
    "ReferenceType",
    "Mem0Layer",
    "EmbeddingModel",
]
```

### 2. `unified_memory/canonical_memory.py`

```python
"""Canonical Memory Layer - Normalized, structured memory storage."""

import hashlib
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import json


class MemoryType(Enum):
    LEARNING = "learning"
    DECISION = "decision"
    INSIGHT = "insight"
    EVENT = "event"
    INTERACTION = "interaction"
    META = "meta"  # Memory about memories


class MemorySource(Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    EXTERNAL = "external"
    INFERRED = "inferred"


@dataclass
class EntityGraph:
    """Extracted entities from memory content."""
    people: List[str]
    projects: List[str]
    skills: List[str]
    organizations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "EntityGraph":
        return cls(**data)


@dataclass  
class CanonicalMemory:
    """Standardized memory format."""
    
    content: str
    memory_type: MemoryType
    importance: int
    context: Optional[str] = None
    tags: List[str] = None
    entities: Optional[EntityGraph] = None
    source: MemorySource = MemorySource.AGENT
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    embedding_id: Optional[str] = None
    loop_refs: List[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.tags is None:
            self.tags = []
        if self.loop_refs is None:
            self.loop_refs = []
        if self.entities is None:
            self.entities = EntityGraph([], [], [], [])
    
    @property
    def content_hash(self) -> str:
        """Generate content hash for deduplication."""
        normalized = f"{self.memory_type.value}:{self.content.lower().strip()}"
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]
    
    def normalize_tags(self) -> List[str]:
        """Normalize tags to lowercase, alphanumeric."""
        normalized = []
        for tag in self.tags:
            clean = ''.join(c.lower() for c in tag if c.isalnum() or c == '-')
            if clean:
                normalized.append(clean)
        return list(set(normalized))  # Deduplicate
    
    def to_db_dict(self) -> Dict[str, Any]:
        """Convert to database-compatible dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "memory_type": self.memory_type.value,
            "importance": self.importance,
            "content": self.content,
            "content_hash": self.content_hash,
            "context": self.context,
            "source": self.source.value,
            "embedding_id": self.embedding_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
        }
    
    @classmethod
    def from_db_row(cls, row: sqlite3.Row, tags: List[str] = None) -> "CanonicalMemory":
        """Reconstruct from database row."""
        return cls(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            memory_type=MemoryType(row["memory_type"]),
            importance=row["importance"],
            content=row["content"],
            context=row["context"],
            tags=tags or [],
            source=MemorySource(row["source"]),
            embedding_id=row["embedding_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            access_count=row["access_count"],
            last_accessed=datetime.fromisoformat(row["last_accessed"]) if row["last_accessed"] else None,
        )


class CanonicalStore:
    """SQLite-backed storage for canonical memories."""
    
    def __init__(self, db_path: str = "memory/unified_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA_SQL)  # Defined in schema module
    
    def capture(self, memory: CanonicalMemory) -> str:
        """Store a new memory. Returns memory ID."""
        with sqlite3.connect(self.db_path) as conn:
            # Check for duplicates
            cursor = conn.execute(
                "SELECT id FROM memories WHERE content_hash = ?",
                (memory.content_hash,)
            )
            if cursor.fetchone():
                raise DuplicateMemoryError(f"Memory with similar content exists")
            
            # Insert memory
            conn.execute(
                """INSERT INTO memories 
                   (id, timestamp, memory_type, importance, content, content_hash,
                    context, source, embedding_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(memory.to_db_dict().values())[:11]
            )
            
            # Insert tags
            for tag in memory.normalize_tags():
                conn.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                    (tag,)
                )
                conn.execute(
                    """INSERT INTO memory_tags (memory_id, tag_id)
                       SELECT ?, id FROM tags WHERE name = ?""",
                    (memory.id, tag)
                )
            
            conn.commit()
        
        return memory.id
    
    def get_by_id(self, memory_id: str) -> Optional[CanonicalMemory]:
        """Retrieve memory by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM memories WHERE id = ?",
                (memory_id,)
            ).fetchone()
            
            if not row:
                return None
            
            tags = self._get_tags_for_memory(conn, memory_id)
            return CanonicalMemory.from_db_row(row, tags)
    
    def search_text(
        self, 
        query: str, 
        memory_type: Optional[MemoryType] = None,
        min_importance: int = 1,
        limit: int = 20
    ) -> List[CanonicalMemory]:
        """Full-text search using SQLite FTS."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            sql = """
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ?
                AND m.importance >= ?
            """
            params = [query, min_importance]
            
            if memory_type:
                sql += " AND m.memory_type = ?"
                params.append(memory_type.value)
            
            sql += " ORDER BY m.importance DESC, rank LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(sql, params).fetchall()
            
            results = []
            for row in rows:
                tags = self._get_tags_for_memory(conn, row["id"])
                results.append(CanonicalMemory.from_db_row(row, tags))
            
            return results
    
    def update_access(self, memory_id: str):
        """Update access count and timestamp."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE memories 
                   SET access_count = access_count + 1,
                       last_accessed = ?
                   WHERE id = ?""",
                (datetime.utcnow().isoformat(), memory_id)
            )
            conn.commit()
```

### 3. `unified_memory/mem0_layer.py`

```python
"""Mem0 Layer - Vector embeddings for semantic memory search."""

import numpy as np
import sqlite3
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json


class EmbeddingModel:
    """Abstract embedding model interface."""
    
    def embed(self, text: str) -> np.ndarray:
        raise NotImplementedError
    
    @property
    def dimensions(self) -> int:
        raise NotImplementedError


class LocalEmbeddingModel(EmbeddingModel):
    """Local embedding using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self._dims = self.model.get_sentence_embedding_dimension()
    
    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)
    
    @property
    def dimensions(self) -> int:
        return self._dims


class APIEmbeddingModel(EmbeddingModel):
    """API-based embedding (OpenAI, etc)."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self._dims = 1536 if "small" in model else 3072
    
    def embed(self, text: str) -> np.ndarray:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return np.array(response.data[0].embedding)
    
    @property
    def dimensions(self) -> int:
        return self._dims


@dataclass
class SearchResult:
    """Semantic search result."""
    memory_id: str
    similarity: float
    memory: Optional["CanonicalMemory"] = None


class Mem0Layer:
    """Vector memory layer with semantic search."""
    
    def __init__(
        self, 
        db_path: str = "memory/unified_memory.db",
        embedding_model: Optional[EmbeddingModel] = None
    ):
        self.db_path = db_path
        self.embedder = embedding_model or LocalEmbeddingModel()
        self._init_vec_table()
    
    def _init_vec_table(self):
        """Initialize vector extension tables."""
        with sqlite3.connect(self.db_path) as conn:
            # Load sqlite-vec extension
            conn.execute("SELECT load_extension('vec0')")
            
            # Create virtual table if not exists
            dims = self.embedder.dimensions
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_memories USING vec0(
                    embedding_id TEXT PRIMARY KEY,
                    vector FLOAT[{dims}]
                )
            """)
    
    def embed_memory(self, memory: "CanonicalMemory") -> str:
        """Generate and store embedding for a memory."""
        # Create embedding text combining content, context, and tags
        embedding_text = self._prepare_embedding_text(memory)
        vector = self.embedder.embed(embedding_text)
        
        embedding_id = hashlib.sha256(
            f"{memory.id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        with sqlite3.connect(self.db_path) as conn:
            # Store in embeddings table
            conn.execute(
                """INSERT INTO embeddings 
                   (id, memory_id, vector, model_version, dimensions)
                   VALUES (?, ?, ?, ?, ?)""",
                (embedding_id, memory.id, vector.tobytes(), 
                 self.embedder.__class__.__name__, self.embedder.dimensions)
            )
            
            # Store in vector search table
            vector_json = json.dumps(vector.tolist())
            conn.execute(
                "INSERT INTO vec_memories (embedding_id, vector) VALUES (?, ?)",
                (embedding_id, vector_json)
            )
            
            conn.commit()
        
        return embedding_id
    
    def _prepare_embedding_text(self, memory: "CanonicalMemory") -> str:
        """Prepare rich text for embedding."""
        parts = [
            memory.content,
            memory.context or "",
            f"Type: {memory.memory_type.value}",
            f"Tags: {', '.join(memory.tags)}"
        ]
        return " | ".join(filter(None, parts))
    
    def search_similar(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.7,
        memory_type: Optional[str] = None
    ) -> List[SearchResult]:
        """Semantic similarity search."""
        query_vector = self.embedder.embed(query)
        vector_json = json.dumps(query_vector.tolist())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Use sqlite-vec for KNN search
            sql = """
                SELECT 
                    vm.embedding_id,
                    distance as similarity
                FROM vec_memories vm
                WHERE vector MATCH ?
                ORDER BY distance
                LIMIT ?
            """
            
            rows = conn.execute(sql, (vector_json, top_k * 2)).fetchall()
            
            results = []
            for row in rows:
                # Get memory_id from embedding_id
                mem_row = conn.execute(
                    "SELECT memory_id FROM embeddings WHERE id = ?",
                    (row["embedding_id"],)
                ).fetchone()
                
                if mem_row and row["similarity"] >= threshold:
                    results.append(SearchResult(
                        memory_id=mem_row["memory_id"],
                        similarity=row["similarity"]
                    ))
            
            return results[:top_k]
    
    def get_context_memories(
        self,
        current_context: str,
        recent_memory_ids: List[str],
        max_results: int = 5
    ) -> List[str]:
        """Retrieve contextually relevant memories."""
        # Combine current context with recent memories for query
        context_parts = [current_context]
        
        # Fetch recent memory contents
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ','.join('?' * len(recent_memory_ids))
            rows = conn.execute(
                f"SELECT content FROM memories WHERE id IN ({placeholders})",
                recent_memory_ids
            ).fetchall()
            context_parts.extend([r[0] for r in rows])
        
        combined_query = " | ".join(context_parts)
        results = self.search_similar(combined_query, top_k=max_results)
        
        return [r.memory_id for r in results]
```

### 4. `unified_memory/strange_loop_memory.py`

```python
"""Strange Loop Memory - Self-referential memory with emergent properties."""

import sqlite3
from typing import List, Optional, Set, Dict, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import networkx as nx


class ReferenceType(Enum):
    """Types of memory references."""
    RELATED = "related"           # General association
    SUPPORTS = "supports"         # Evidence for
    CONTRADICTS = "contradicts"   # Opposes
    SUPERSEDES = "supersedes"     # Replaces
    DERIVED_FROM = "derived_from" # Generated from
    META = "meta"                 # About the memory


@dataclass
class MemoryPath:
    """Path through memory graph."""
    nodes: List[str]
    total_strength: float
    path_type: str  # loop, chain, tree


@dataclass
class EmergentInsight:
    """New insight derived from memory patterns."""
    source_memories: List[str]
    insight_content: str
    confidence: float
    pattern_type: str


class StrangeLoopLayer:
    """
    Self-referential memory layer where memories can reference each other,
    creating emergent properties and higher-order insights.
    """
    
    def __init__(self, db_path: str = "memory/unified_memory.db"):
        self.db_path = db_path
        self._graph: Optional[nx.DiGraph] = None
    
    def add_reference(
        self,
        source_id: str,
        target_id: str,
        ref_type: ReferenceType = ReferenceType.RELATED,
        strength: float = 1.0
    ):
        """Create a reference between two memories."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO memory_references 
                   (source_id, target_id, reference_type, strength, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (source_id, target_id, ref_type.value, strength, datetime.utcnow())
            )
            conn.commit()
        
        # Invalidate cached graph
        self._graph = None
    
    def detect_loops(self, start_id: str, max_depth: int = 5) -> List[MemoryPath]:
        """Find cyclic paths starting from a memory."""
        graph = self._load_graph()
        loops = []
        
        def dfs(current: str, path: List[str], strength: float, depth: int):
            if depth > max_depth:
                return
            
            for neighbor in graph.successors(current):
                edge_strength = graph[current][neighbor].get("strength", 1.0)
                new_strength = strength * edge_strength
                
                if neighbor == start_id and len(path) > 1:
                    # Found a loop
                    loops.append(MemoryPath(
                        nodes=path + [neighbor],
                        total_strength=new_strength,
                        path_type="loop"
                    ))
                elif neighbor not in path:
                    dfs(neighbor, path + [neighbor], new_strength, depth + 1)
        
        dfs(start_id, [start_id], 1.0, 0)
        
        # Sort by strength (stronger loops first)
        loops.sort(key=lambda x: x.total_strength, reverse=True)
        return loops
    
    def find_emergent_insights(self) -> List[EmergentInsight]:
        """
        Analyze memory clusters to generate new insights.
        
        Detects patterns like:
        - Contradictions (memories that oppose each other)
        - Convergences (multiple paths to same conclusion)
        - Chains (sequences of related learnings)
        - Clusters (dense groups of related memories)
        """
        insights = []
        graph = self._load_graph()
        
        # Find contradictions
        contradictions = self._find_contradictions(graph)
        for mem_ids, strength in contradictions:
            insights.append(EmergentInsight(
                source_memories=mem_ids,
                insight_content=f"Contradiction detected between memories",
                confidence=strength,
                pattern_type="contradiction"
            ))
        
        # Find dense clusters
        clusters = self._find_clusters(graph)
        for cluster in clusters:
            if len(cluster) >= 3:
                insights.append(EmergentInsight(
                    source_memories=list(cluster),
                    insight_content=f"Dense knowledge cluster with {len(cluster)} memories",
                    confidence=0.8,
                    pattern_type="cluster"
                ))
        
        # Find convergence points
        convergences = self._find_convergences(graph)
        for target, sources in convergences.items():
            if len(sources) >= 3:
                insights.append(EmergentInsight(
                    source_memories=sources + [target],
                    insight_content=f"Multiple paths converge on shared conclusion",
                    confidence=0.75,
                    pattern_type="convergence"
                ))
        
        return insights
    
    def _find_contradictions(
        self, 
        graph: nx.DiGraph
    ) -> List[Tuple[List[str], float]]:
        """Find pairs of memories that contradict each other."""
        contradictions = []
        
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT source_id, target_id, strength 
                   FROM memory_references 
                   WHERE reference_type = 'contradicts'"""
            ).fetchall()
            
            for source, target, strength in rows:
                contradictions.append(([source, target], strength))
        
        return contradictions
    
    def _find_clusters(self, graph: nx.DiGraph) -> List[Set[str]]:
        """Find densely connected memory clusters."""
        from networkx.algorithms import community
        
        # Convert to undirected for clustering
        undirected = graph.to_undirected()
        
        # Use community detection
        communities = community.greedy_modularity_communities(undirected)
        
        return [set(c) for c in communities]
    
    def _find_convergences(self, graph: nx.DiGraph) -> Dict[str, List[str]]:
        """Find nodes that multiple paths converge on."""
        convergence = defaultdict(list)
        
        for node in graph.nodes():
            predecessors = list(graph.predecessors(node))
            if len(predecessors) > 2:
                convergence[node] = predecessors
        
        return dict(convergence)
    
    def propagate_importance(
        self,
        source_id: str,
        delta: int,
        decay: float = 0.5,
        max_depth: int = 3
    ):
        """
        Propagate importance changes through reference chain.
        
        If a memory becomes more/less important, adjust connected memories.
        """
        graph = self._load_graph()
        visited = {source_id}
        
        def propagate(current: str, current_delta: float, depth: int):
            if depth >= max_depth or abs(current_delta) < 0.1:
                return
            
            for neighbor in graph.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_delta = current_delta * decay
                    
                    # Update importance in database
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            """UPDATE memories 
                               SET importance = MAX(1, MIN(10, importance + ?))
                               WHERE id = ?""",
                            (int(new_delta), neighbor)
                        )
                        conn.commit()
                    
                    propagate(neighbor, new_delta, depth + 1)
        
        propagate(source_id, float(delta), 0)
    
    def get_related_memories(
        self,
        memory_id: str,
        max_hops: int = 2
    ) -> List[Tuple[str, float]]:
        """Get memories related within N hops."""
        graph = self._load_graph()
        
        related = []
        visited = {memory_id}
        current_level = {memory_id: 1.0}
        
        for hop in range(max_hops):
            next_level = {}
            for node, strength in current_level.items():
                for neighbor in graph.successors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        edge_strength = graph[node][neighbor].get("strength", 1.0)
                        new_strength = strength * edge_strength
                        next_level[neighbor] = new_strength
                        related.append((neighbor, new_strength))
            current_level = next_level
        
        # Sort by connection strength
        related.sort(key=lambda x: x[1], reverse=True)
        return related
    
    def create_meta_memory(
        self,
        source_ids: List[str],
        insight: str,
        memory_manager  # Forward reference to MemoryManager
    ) -> str:
        """
        Create a meta-memory (memory about other memories).
        
        This is the "strange loop" - the system remembering itself.
        """
        from .canonical_memory import CanonicalMemory, MemoryType, MemorySource
        
        meta_memory = CanonicalMemory(
            content=f"Meta-insight: {insight}",
            memory_type=MemoryType.META,
            importance=8,  # Meta-memories are generally important
            context=f"Derived from {len(source_ids)} related memories",
            tags=["meta", "emergent", "strange-loop"],
            source=MemorySource.INFERRED,
            loop_refs=source_ids
        )
        
        # Store via memory manager
        memory_id = memory_manager.capture(meta_memory)
        
        # Create references to source memories
        for source_id in source_ids:
            self.add_reference(
                memory_id, 
                source_id, 
                ReferenceType.DERIVED_FROM,
                strength=0.9
            )
        
        return memory_id
    
    def _load_graph(self) -> nx.DiGraph:
        """Load memory references as directed graph."""
        if self._graph is not None:
            return self._graph
        
        graph = nx.DiGraph()
        
        with sqlite3.connect(self.db_path) as conn:
            # Add all memories as nodes
            rows = conn.execute("SELECT id FROM memories").fetchall()
            for (memory_id,) in rows:
                graph.add_node(memory_id)
            
            # Add references as edges
            rows = conn.execute(
                "SELECT source_id, target_id, reference_type, strength FROM memory_references"
            ).fetchall()
            for source, target, ref_type, strength in rows:
                graph.add_edge(source, target, 
                             type=ref_type, strength=strength)
        
        self._graph = graph
        return graph
    
    def analyze_self(self) -> Dict:
        """
        Generate meta-analysis of the memory system itself.
        
        Returns statistics about memory connectivity, patterns, health.
        """
        graph = self._load_graph()
        
        with sqlite3.connect(self.db_path) as conn:
            total_memories = conn.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            
            total_refs = conn.execute(
                "SELECT COUNT(*) FROM memory_references"
            ).fetchone()[0]
            
            orphaned = conn.execute("""
                SELECT COUNT(*) FROM memories m
                LEFT JOIN memory_references r ON m.id = r.source_id OR m.id = r.target_id
                WHERE r.source_id IS NULL
            """).fetchone()[0]
        
        return {
            "total_memories": total_memories,
            "total_references": total_refs,
            "reference_density": total_refs / max(total_memories, 1),
            "orphaned_memories": orphaned,
            "connected_components": nx.number_weakly_connected_components(graph),
            "avg_clustering": nx.average_clustering(graph.to_undirected()),
            "has_cycles": not nx.is_directed_acyclic_graph(graph),
        }
```

### 5. `unified_memory/memory_manager.py`

```python
"""Memory Manager - Orchestrates Canonical, Mem0, and Strange Loop layers."""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from .canonical_memory import CanonicalMemory, CanonicalStore, MemoryType
from .mem0_layer import Mem0Layer, SearchResult
from .strange_loop_memory import StrangeLoopLayer, ReferenceType, EmergentInsight


@dataclass
class SearchContext:
    """Rich search results combining all layers."""
    canonical: CanonicalMemory
    similarity: Optional[float] = None
    related_memories: List[str] = None
    strange_loops: List[Any] = None


class MemoryManager:
    """
    Unified interface to the three-layer memory system.
    
    Orchestrates:
    - Canonical storage (structured data)
    - Mem0 embeddings (semantic search)
    - Strange loops (self-referential insights)
    """
    
    def __init__(self, db_path: str = "memory/unified_memory.db"):
        self.db_path = db_path
        self.canonical = CanonicalStore(db_path)
        self.mem0 = Mem0Layer(db_path)
        self.strange_loop = StrangeLoopLayer(db_path)
    
    def capture(
        self,
        memory: CanonicalMemory,
        related_to: Optional[List[str]] = None,
        generate_embedding: bool = True
    ) -> str:
        """
        Capture a new memory across all layers.
        
        Args:
            memory: The canonical memory to store
            related_to: IDs of related memories (creates strange loops)
            generate_embedding: Whether to create vector embedding
        
        Returns:
            Memory ID
        """
        # 1. Store in canonical layer
        memory_id = self.canonical.capture(memory)
        
        # 2. Generate embedding if requested
        if generate_embedding:
            embedding_id = self.mem0.embed_memory(memory)
            
            # Update memory with embedding reference
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE memories SET embedding_id = ? WHERE id = ?",
                    (embedding_id, memory_id)
                )
                conn.commit()
        
        # 3. Create strange loop references
        if related_to:
            for related_id in related_to:
                self.strange_loop.add_reference(
                    memory_id, 
                    related_id, 
                    ReferenceType.RELATED
                )
        
        # 4. Check for emergent insights
        self._check_emergence(memory_id)
        
        return memory_id
    
    def search(
        self,
        query: str,
        search_type: str = "hybrid",  # text, semantic, hybrid
        memory_type: Optional[MemoryType] = None,
        min_importance: int = 1,
        limit: int = 10
    ) -> List[SearchContext]:
        """
        Multi-layer memory search.
        
        Args:
            query: Search query
            search_type: text (fts), semantic (vector), hybrid (both)
            memory_type: Filter by memory type
            min_importance: Minimum importance score
            limit: Maximum results
        
        Returns:
            List of search contexts with rich metadata
        """
        results = []
        seen_ids = set()
        
        # Text search via FTS
        if search_type in ("text", "hybrid"):
            text_results = self.canonical.search_text(
                query, memory_type, min_importance, limit
            )
            for memory in text_results:
                if memory.id not in seen_ids:
                    seen_ids.add(memory.id)
                    results.append(SearchContext(
                        canonical=memory,
                        related_memories=self._get_related(memory.id),
                        strange_loops=self.strange_loop.detect_loops(memory.id)
                    ))
        
        # Semantic search via Mem0
        if search_type in ("semantic", "hybrid"):
            semantic_results = self.mem0.search_similar(
                query, top_k=limit * 2, threshold=0.6
            )
            for result in semantic_results:
                if result.memory_id not in seen_ids:
                    seen_ids.add(result.memory_id)
                    memory = self.canonical.get_by_id(result.memory_id)
                    if memory and memory.importance >= min_importance:
                        results.append(SearchContext(
                            canonical=memory,
                            similarity=result.similarity,
                            related_memories=self._get_related(memory.id),
                            strange_loops=self.strange_loop.detect_loops(memory.id)
                        ))
        
        # Sort by relevance (hybrid scoring)
        if search_type == "hybrid":
            results.sort(
                key=lambda x: (
                    (x.similarity or 0) * 0.5 + 
                    (x.canonical.importance / 10) * 0.3 +
                    (min(len(x.related_memories or []), 5) / 5) * 0.2
                ),
                reverse=True
            )
        
        return results[:limit]
    
    def recall(
        self,
        memory_id: str,
        include_related: bool = True,
        max_related: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Rich memory recall with context.
        
        Returns memory plus related context from all layers.
        """
        memory = self.canonical.get_by_id(memory_id)
        if not memory:
            return None
        
        # Update access stats
        self.canonical.update_access(memory_id)
        
        result = {
            "memory": memory,
            "loops": self.strange_loop.detect_loops(memory_id),
            "analysis": self.strange_loop.analyze_self()
        }
        
        if include_related:
            related = self.strange_loop.get_related_memories(memory_id)
            result["related"] = [
                {
                    "memory": self.canonical.get_by_id(mem_id),
                    "connection_strength": strength
                }
                for mem_id, strength in related[:max_related]
            ]
        
        return result
    
    def get_context_for_task(
        self,
        task_description: str,
        recent_memory_ids: Optional[List[str]] = None,
        max_memories: int = 5
    ) -> List[CanonicalMemory]:
        """
        Retrieve memories relevant to current task context.
        
        Uses Mem0 semantic search on task + recent memories.
        """
        context_ids = self.mem0.get_context_memories(
            task_description,
            recent_memory_ids or [],
            max_results=max_memories
        )
        
        memories = []
        for mem_id in context_ids:
            memory = self.canonical.get_by_id(mem_id)
            if memory:
                memories.append(memory)
                self.canonical.update_access(mem_id)
        
        return memories
    
    def consolidate(self, days: int = 7) -> Dict[str, Any]:
        """
        Consolidate memories into higher-order summaries.
        
        - Generate weekly summaries
        - Detect emergent insights
        - Create meta-memories
        - Archive old daily logs
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get memories from period
            rows = conn.execute(
                """SELECT id FROM memories 
                   WHERE timestamp >= ? 
                   ORDER BY importance DESC""",
                (cutoff.isoformat(),)
            ).fetchall()
            
            memory_ids = [r[0] for r in rows]
        
        # Find emergent insights
        insights = self.strange_loop.find_emergent_insights()
        
        # Create meta-memories for strong insights
        created_meta = []
        for insight in insights:
            if insight.confidence > 0.8:
                meta_id = self.strange_loop.create_meta_memory(
                    insight.source_memories,
                    insight.insight_content,
                    self
                )
                created_meta.append(meta_id)
        
        return {
            "period_days": days,
            "memories_considered": len(memory_ids),
            "insights_found": len(insights),
            "meta_memories_created": len(created_meta),
            "meta_ids": created_meta
        }
    
    def reflect(self) -> Dict[str, Any]:
        """
        Generate self-reflection on the memory system.
        
        Returns analysis of memory health, patterns, recommendations.
        """
        analysis = self.strange_loop.analyze_self()
        
        with sqlite3.connect(self.db_path) as conn:
            # Memory type distribution
            type_dist = conn.execute(
                """SELECT memory_type, COUNT(*) 
                   FROM memories 
                   GROUP BY memory_type"""
            ).fetchall()
            
            # Importance distribution
            importance_dist = conn.execute(
                """SELECT importance, COUNT(*) 
                   FROM memories 
                   GROUP BY importance"""
            ).fetchall()
            
            # Recent activity
            recent_count = conn.execute(
                """SELECT COUNT(*) FROM memories 
                   WHERE timestamp >= datetime('now', '-7 days')"""
            ).fetchone()[0]
        
        recommendations = []
        
        if analysis["orphaned_memories"] > analysis["total_memories"] * 0.2:
            recommendations.append(
                "Many orphaned memories. Consider adding more cross-references."
            )
        
        if analysis["reference_density"] < 0.5:
            recommendations.append(
                "Low reference density. Memories are too isolated."
            )
        
        if not analysis["has_cycles"]:
            recommendations.append(
                "No strange loops detected yet. System needs more self-reference."
            )
        
        return {
            "analysis": analysis,
            "type_distribution": {t: c for t, c in type_dist},
            "importance_distribution": {i: c for i, c in importance_dist},
            "recent_activity_7d": recent_count,
            "recommendations": recommendations
        }
    
    def _check_emergence(self, memory_id: str):
        """Check if new memory creates emergent patterns."""
        # Check for loops involving this memory
        loops = self.strange_loop.detect_loops(memory_id, max_depth=3)
        
        # If strong loops detected, boost importance
        if loops and loops[0].total_strength > 0.7:
            self.strange_loop.propagate_importance(
                memory_id, 
                delta=1,
                decay=0.5
            )
    
    def _get_related(self, memory_id: str) -> List[str]:
        """Get IDs of related memories."""
        related = self.strange_loop.get_related_memories(memory_id, max_hops=1)
        return [mem_id for mem_id, _ in related]
```

---

## Migration Path from v2

### Phase 1: Dual System (Week 1)
- Keep memory-system-v2 running
- Build unified system in parallel
- Sync daily: v2 JSON → SQLite

### Phase 2: Cutover (Week 2)
- Migrate all historical memories
- Update AGENTS.md to use new API
- Deprecate v2 bash scripts

### Phase 3: Enhancement (Week 3+)
- Enable Mem0 embeddings
- Activate Strange Loops
- Self-reflection routines

### Migration Script

```python
# scripts/migrate_v2_to_v3.py
"""Migrate memory-system-v2 to unified memory v3."""

import json
from datetime import datetime
from unified_memory import MemoryManager, CanonicalMemory, MemoryType

def migrate():
    manager = MemoryManager()
    
    # Load v2 index
    with open("memory/index/memory-index.json") as f:
        index = json.load(f)
    
    for mem in index["memories"]:
        memory = CanonicalMemory(
            content=mem["content"],
            memory_type=MemoryType(mem["type"]),
            importance=mem["importance"],
            context=mem.get("context"),
            tags=mem.get("tags", []),
            timestamp=datetime.fromtimestamp(mem["timestamp"] / 1000)
        )
        
        manager.capture(memory, generate_embedding=False)
    
    print(f"Migrated {len(index['memories'])} memories")

if __name__ == "__main__":
    migrate()
```

---

## Performance Targets

| Operation | v2 (File) | v3 (SQLite) | Target |
|-----------|-----------|-------------|--------|
| Capture | ~50ms | ~30ms | <50ms |
| Text Search | ~20ms | ~15ms | <20ms |
| Semantic Search | N/A | ~100ms | <150ms |
| Related Memories | N/A | ~25ms | <50ms |
| Loop Detection | N/A | ~50ms | <100ms |
| Consolidation | Manual | Automatic | Background |

---

## File Structure

```
clawd/
├── memory/
│   ├── unified_memory.db       # SQLite database
│   ├── daily/                  # Markdown exports (optional)
│   └── v2_backup/             # v2 data archive
│
├── unified_memory/             # Python package
│   ├── __init__.py
│   ├── canonical_memory.py     # Canonical layer
│   ├── mem0_layer.py          # Vector embeddings
│   ├── strange_loop_memory.py # Self-referential
│   ├── memory_manager.py      # Orchestrator
│   ├── schema.sql             # Database schema
│   └── cli.py                 # Command-line interface
│
└── scripts/
    ├── migrate_v2_to_v3.py
    └── memory_consolidation.py
```

---

## Conclusion

This unified architecture provides:

1. **Canonical Layer** - Reliable, structured storage with SQLite
2. **Mem0 Layer** - Semantic search via vector embeddings
3. **Strange Loop Layer** - Self-referential insights and emergence

The system is:
- **Faster** - SQLite beats file-based operations
- **Smarter** - Semantic + text hybrid search
- **Self-aware** - Strange loops enable meta-cognition
- **Scalable** - Handles 100K+ memories efficiently

**Next Steps:**
1. Review and approve design
2. Implement core modules
3. Migration from v2
4. Integration with Clawd ecosystem
