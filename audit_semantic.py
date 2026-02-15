#!/usr/bin/env python3
"""
P9 Semantic Search Audit Script
Tests performance, integration, and edge cases
"""
import sqlite3
import json
import tempfile
import os
import time
import hashlib
from pathlib import Path

# Generate test documents of various sizes
def generate_test_docs(count=100):
    """Generate test documents with varied content"""
    topics = [
        "machine learning neural networks deep learning artificial intelligence",
        "python programming software development coding best practices",
        "database design sql indexing query optimization performance",
        "web development javascript frontend react vue angular",
        "devops kubernetes docker containers deployment ci cd",
        "data science analytics visualization statistics pandas numpy",
        "security encryption authentication authorization oauth jwt",
        "cloud computing aws azure gcp serverless lambda functions",
    ]
    
    docs = []
    for i in range(count):
        topic = topics[i % len(topics)]
        # Vary document size
        size = (i % 5) + 1  # 1-5 paragraphs
        content = f"Document {i}: {topic}\n\n" + (topic * 50 + "\n\n") * size
        docs.append((content, f"doc_{i}.txt"))
    return docs

def create_test_db_with_docs(docs):
    """Create a test database with the documents schema"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create documents table (like p9_index.py does)
    cursor.execute("""
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            content_hash TEXT NOT NULL,
            content TEXT NOT NULL,
            title TEXT,
            metadata TEXT,
            file_size INTEGER,
            modified_time TEXT,
            indexed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create FTS5 table
    cursor.execute("""
        CREATE VIRTUAL TABLE documents_fts USING fts5(
            content,
            title,
            path,
            content=documents,
            content_rowid=id
        )
    """)
    
    # Insert documents
    for i, (content, filename) in enumerate(docs):
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        path = f"/test/{filename}"
        cursor.execute("""
            INSERT INTO documents (path, content_hash, content, title, metadata, file_size, modified_time)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (path, content_hash, content, f"Document {i}", "test", len(content)))
        
        # Insert into FTS
        cursor.execute("""
            INSERT INTO documents_fts(rowid, content, title, path)
            VALUES (?, ?, ?, ?)
        """, (i+1, content, f"Document {i}", path))
    
    conn.commit()
    conn.close()
    return db_path

def test_performance():
    """Test indexing and search performance"""
    print("="*70)
    print("P9 SEMANTIC SEARCH PERFORMANCE TEST")
    print("="*70)
    
    # Create test data
    print("\n[1] Creating test database with 100 documents...")
    docs = generate_test_docs(100)
    db_path = create_test_db_with_docs(docs)
    print(f"    ✓ Database created: {db_path}")
    
    try:
        import sys
        sys.path.insert(0, '/Users/dhyana/clawd')
        from p9_semantic import SemanticIndexer, SemanticSearcher
        
        # Test indexing performance
        print("\n[2] Testing vector indexing performance...")
        indexer = SemanticIndexer(db_path)
        indexer.connect()
        indexer.init_vector_schema()
        
        start_time = time.time()
        indexer.index_all()
        index_time = time.time() - start_time
        
        stats = indexer.get_stats()
        print(f"    ✓ Indexed {stats['vector_indexed']} documents in {index_time:.2f}s")
        print(f"    ✓ Average: {index_time/stats['vector_indexed']*1000:.1f}ms per document")
        indexer.close()
        
        # Test search performance
        print("\n[3] Testing search performance...")
        searcher = SemanticSearcher(db_path)
        searcher.connect()
        
        queries = [
            "neural networks",
            "python best practices",
            "database optimization",
            "cloud infrastructure",
            "security vulnerabilities",
        ]
        
        total_time = 0
        for query in queries:
            start = time.time()
            results = searcher.search(query, top_k=10)
            elapsed = time.time() - start
            total_time += elapsed
            print(f"    '{query[:30]}...' - {elapsed*1000:.1f}ms ({len(results)} results)")
        
        avg_search_time = total_time / len(queries)
        print(f"\n    ✓ Average search time: {avg_search_time*1000:.1f}ms")
        
        if avg_search_time * 1000 < 100:
            print("    ✓ PASS: Search under 100ms target")
        else:
            print("    ⚠ SLOW: Search exceeds 100ms target")
        
        # Test hybrid search
        print("\n[4] Testing hybrid search performance...")
        start = time.time()
        results = searcher.hybrid_search("machine learning deployment", top_k=10)
        hybrid_time = time.time() - start
        print(f"    ✓ Hybrid search: {hybrid_time*1000:.1f}ms ({len(results)} results)")
        
        searcher.close()
        
        # Test missing embeddings handling
        print("\n[5] Testing missing embeddings handling...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete one vector
        cursor.execute("DELETE FROM document_vectors WHERE document_id = 1")
        conn.commit()
        conn.close()
        
        # Try search - should handle gracefully
        searcher = SemanticSearcher(db_path)
        searcher.connect()
        results = searcher.search("test query", top_k=10)
        print(f"    ✓ Search works with missing embeddings ({len(results)} results)")
        searcher.close()
        
        print("\n" + "="*70)
        print("PERFORMANCE TEST COMPLETE")
        print("="*70)
        
    finally:
        os.unlink(db_path)
        print(f"\n✓ Cleaned up test database")

def test_schema_compatibility():
    """Test schema compatibility issues"""
    print("\n" + "="*70)
    print("SCHEMA COMPATIBILITY TEST")
    print("="*70)
    
    # Check if p9_semantic works with different schemas
    import sys
    sys.path.insert(0, '/Users/dhyana/clawd')
    
    db_path = "/Users/dhyana/DHARMIC_GODEL_CLAW/integrations/dharmic-agora/p9_mesh/p9_memory.db"
    
    print(f"\n[1] Checking P9 memory database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"    Tables: {tables}")
    
    # Check for documents table
    if 'documents' in tables:
        print("    ✓ Found 'documents' table")
    else:
        print("    ✗ MISSING 'documents' table - p9_semantic expects this!")
    
    if 'cartographer_index' in tables:
        print("    ✓ Found 'cartographer_index' table")
        cursor.execute("PRAGMA table_info(cartographer_index)")
        cols = [r[1] for r in cursor.fetchall()]
        print(f"    Columns: {cols}")
        if 'content' not in cols:
            print("    ✗ CRITICAL: No 'content' column in cartographer_index!")
            print("    ✗ Semantic search CANNOT work without content column")
    
    conn.close()

if __name__ == "__main__":
    test_performance()
    test_schema_compatibility()
