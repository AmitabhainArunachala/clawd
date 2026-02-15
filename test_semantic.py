#!/usr/bin/env python3
"""
Quick test for P9 Semantic Search functionality
"""
import sqlite3
import json
import tempfile
import os
from pathlib import Path

# Test documents about different topics
TEST_DOCS = [
    ("The quick brown fox jumps over the lazy dog", "animals"),
    ("Machine learning models require large amounts of training data", "ai"),
    ("Python is a versatile programming language for data science", "programming"),
    ("Neural networks can learn complex patterns from data", "ai"),
    ("Cats and dogs are popular pets around the world", "animals"),
    ("The syntax of Python is clean and readable", "programming"),
    ("Deep learning is a subset of machine learning", "ai"),
    ("Birds can fly high in the sky", "animals"),
]

def create_test_db():
    """Create a test database with sample documents"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create documents table
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
    
    # Insert test documents
    import hashlib
    for i, (content, category) in enumerate(TEST_DOCS):
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        path = f"/test/doc_{i}.txt"
        cursor.execute("""
            INSERT INTO documents (path, content_hash, content, title, metadata, file_size, modified_time)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (path, content_hash, content, f"Document {i}", category, len(content)))
        
        # Insert into FTS
        cursor.execute("""
            INSERT INTO documents_fts(rowid, content, title, path)
            VALUES (?, ?, ?, ?)
        """, (i+1, content, f"Document {i}", path))
    
    conn.commit()
    conn.close()
    
    return db_path

def test_semantic_search():
    """Test semantic search functionality"""
    print("="*60)
    print("P9 Semantic Search - Quick Test")
    print("="*60)
    
    # Create test database
    db_path = create_test_db()
    print(f"\n✓ Created test database: {db_path}")
    
    try:
        # Import and test
        from p9_semantic import SemanticIndexer, SemanticSearcher
        
        # Test 1: Initialize vector schema
        print("\n[Test 1] Initialize vector schema...")
        indexer = SemanticIndexer(db_path)
        indexer.connect()
        indexer.init_vector_schema()
        print("✓ Vector schema initialized")
        
        # Test 2: Index documents
        print("\n[Test 2] Index documents with embeddings...")
        indexer.index_all()
        
        stats = indexer.get_stats()
        print(f"✓ Indexed {stats['vector_indexed']}/{stats['total_documents']} documents")
        indexer.close()
        
        # Test 3: Semantic search
        print("\n[Test 3] Semantic search...")
        searcher = SemanticSearcher(db_path)
        searcher.connect()
        
        queries = [
            "artificial intelligence",
            "coding",
            "pets",
        ]
        
        for query in queries:
            print(f"\n  Query: '{query}'")
            results = searcher.search(query, top_k=3)
            for i, r in enumerate(results, 1):
                print(f"    {i}. {r['title']} (similarity: {r['similarity']:.3f})")
                print(f"       Content: {r['title'][:60]}...")
                
        # Test 4: Hybrid search
        print("\n[Test 4] Hybrid search...")
        results = searcher.hybrid_search("Python programming", top_k=3)
        for i, r in enumerate(results, 1):
            print(f"    {i}. {r['title']} (hybrid: {r.get('hybrid_score', 0):.3f})")
            
        searcher.close()
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)
        
    finally:
        # Cleanup
        os.unlink(db_path)
        print(f"\n✓ Cleaned up test database")

if __name__ == "__main__":
    test_semantic_search()
