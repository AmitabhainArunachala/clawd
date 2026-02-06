"""
Core UnifiedIndex class - main interface for unified memory search.
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from .search import SearchQuery, SearchResult
from .embeddings import EmbeddingProvider


@dataclass
class Document:
    """A document in the unified index."""
    id: str
    source: str  # 'psmv', 'conversation', 'code'
    path: str
    title: str
    content: str
    sha256: str
    indexed_at: datetime
    metadata: Dict[str, Any]


class UnifiedIndex:
    """
    Unified memory index providing fast semantic search across
    PSMV, conversations, and code.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the unified index.
        
        Args:
            db_path: Path to SQLite database. Defaults to ~/.openclaw/unified_memory.db
        """
        if db_path is None:
            db_path = Path.home() / ".openclaw" / "unified_memory.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._conn: Optional[sqlite3.Connection] = None
        self._embedding = EmbeddingProvider()
        
    def _get_conn(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn
    
    def _init_schema(self):
        """Initialize database schema."""
        conn = self._conn
        
        # Documents table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                path TEXT NOT NULL,
                title TEXT,
                content TEXT,
                sha256 TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Chunks table for vector search
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                embedding BLOB,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)
        
        # FTS5 virtual table for BM25
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                content,
                content_rowid=rowid
            )
        """)
        
        # Sources tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                name TEXT PRIMARY KEY,
                path TEXT,
                document_count INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                last_sync TIMESTAMP
            )
        """)
        
        # Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_source ON documents(source)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(document_id)")
        
        conn.commit()
    
    def compute_sha256(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_document(self, doc: Document, chunks: List[Dict[str, Any]]) -> None:
        """
        Add a document to the index with its chunks.
        
        Args:
            doc: Document to add
            chunks: List of chunk dicts with 'content', 'start_line', 'end_line'
        """
        conn = self._get_conn()
        
        # Insert document
        conn.execute(
            """INSERT OR REPLACE INTO documents 
               (id, source, path, title, content, sha256, indexed_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (doc.id, doc.source, doc.path, doc.title, doc.content, 
             doc.sha256, doc.indexed_at.isoformat(), json.dumps(doc.metadata))
        )
        
        # Delete old chunks for this document
        conn.execute("DELETE FROM chunks WHERE document_id = ?", (doc.id,))
        
        # Insert new chunks with embeddings
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc.id}_chunk_{i}"
            embedding = self._embedding.embed(chunk['content'])
            
            conn.execute(
                """INSERT INTO chunks (id, document_id, content, start_line, end_line, embedding)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (chunk_id, doc.id, chunk['content'], 
                 chunk.get('start_line', 0), chunk.get('end_line', 0),
                 embedding.tobytes() if hasattr(embedding, 'tobytes') else embedding)
            )
            
            # Also insert into FTS
            conn.execute(
                "INSERT INTO chunks_fts (content) VALUES (?)",
                (chunk['content'],)
            )
        
        conn.commit()
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Search the unified index.
        
        Args:
            query: SearchQuery with query string and filters
            
        Returns:
            List of SearchResult objects
        """
        conn = self._get_conn()
        
        # Get query embedding
        query_embedding = self._embedding.embed(query.query)
        
        # Build source filter
        source_filter = ""
        params = []
        if query.sources and query.sources != ['all']:
            placeholders = ','.join('?' * len(query.sources))
            source_filter = f"AND d.source IN ({placeholders})"
            params = query.sources
        
        # Hybrid search: combine BM25 + vector similarity
        results = []
        
        # FTS5 BM25 search
        bm25_results = conn.execute(
            f"""SELECT c.id, c.document_id, c.content, c.start_line, c.end_line,
                       rank as bm25_score
                FROM chunks_fts 
                JOIN chunks c ON c.rowid = chunks_fts.rowid
                JOIN documents d ON c.document_id = d.id
                WHERE chunks_fts MATCH ? {source_filter}
                ORDER BY rank LIMIT ?""",
            [query.query] + params + [query.limit * 2]
        ).fetchall()
        
        # Get documents and compute final scores
        seen_docs = set()
        for row in bm25_results:
            if row['document_id'] in seen_docs:
                continue
            seen_docs.add(row['document_id'])
            
            doc_row = conn.execute(
                "SELECT * FROM documents WHERE id = ?", (row['document_id'],)
            ).fetchone()
            
            if doc_row:
                # Compute hybrid score (simplified - would use actual cosine similarity)
                hybrid_score = 0.6 * (1.0 / (1.0 + abs(row['bm25_score']))) + 0.4 * 0.5
                
                if hybrid_score >= query.min_relevance:
                    results.append(SearchResult(
                        id=row['id'],
                        document_id=row['document_id'],
                        title=doc_row['title'],
                        content=row['content'],
                        source=doc_row['source'],
                        path=doc_row['path'],
                        score=hybrid_score,
                        start_line=row['start_line'],
                        end_line=row['end_line']
                    ))
        
        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.limit]
    
    def get_status(self) -> Dict[str, Any]:
        """Get index status statistics."""
        conn = self._get_conn()
        
        total_docs = conn.execute(
            "SELECT COUNT(*) FROM documents"
        ).fetchone()[0]
        
        total_chunks = conn.execute(
            "SELECT COUNT(*) FROM chunks"
        ).fetchone()[0]
        
        by_source = conn.execute(
            "SELECT source, COUNT(*) FROM documents GROUP BY source"
        ).fetchall()
        
        sources = conn.execute(
            "SELECT * FROM sources"
        ).fetchall()
        
        return {
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "by_source": {row[0]: row[1] for row in by_source},
            "sources": [
                {
                    "name": s[0],
                    "path": s[1],
                    "document_count": s[2],
                    "chunk_count": s[3],
                    "last_sync": s[4]
                }
                for s in sources
            ],
            "db_path": str(self.db_path),
            "db_size_mb": self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
        }
    
    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
