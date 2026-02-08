#!/usr/bin/env python3
"""
MASSIVE CONTEXT INDEXING SPRINT
Indexes entire filesystem into unified_memory.db
"""

import os
import sys
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import sqlite_vec

# Configuration
DB_PATH = os.path.expanduser("~/.openclaw/unified_memory.db")

def init_database():
    """Initialize database with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    
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
    
    # Chunks table with vector support
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            content TEXT NOT NULL,
            start_line INTEGER,
            end_line INTEGER,
            embedding BLOB
        )
    """)
    
    # FTS5 for full-text search
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
    
    # Vector table using sqlite-vec
    try:
        conn.execute("SELECT vec_version()")
        print("✅ sqlite-vec extension loaded")
    except:
        print("⚠️ sqlite-vec extension not available")
    
    conn.commit()
    conn.close()

def compute_sha256(filepath):
    """Compute SHA256 hash of file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return None

def chunk_content(content, chunk_size=400, overlap=80):
    """Split content into overlapping chunks"""
    words = content.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
        if end == len(words):
            break
    
    return chunks

def is_text_file(filepath):
    """Check if file is text (not binary)"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return False
            # Try to decode as utf-8
            chunk.decode('utf-8')
            return True
    except:
        return False

def index_directory(source_name, dir_path, file_extensions=None, exclude_patterns=None):
    """Index all files in a directory"""
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    try:
        sqlite_vec.load(conn)
    except:
        pass
    
    dir_path = os.path.expanduser(dir_path)
    
    if not os.path.exists(dir_path):
        print(f"❌ Directory not found: {dir_path}")
        conn.close()
        return 0, 0
    
    # Default text extensions
    text_extensions = {'.md', '.py', '.txt', '.json', '.yaml', '.yml', '.sh', '.js', '.html', '.css', '.rs', '.go', '.ts', '.jsx', '.tsx', '.ipynb'}
    
    # Collect all files
    files_to_index = []
    for root, dirs, files in os.walk(dir_path):
        # Skip excluded directories
        if exclude_patterns:
            dirs[:] = [d for d in dirs if not any(pat in d.lower() for pat in exclude_patterns)]
        
        for filename in files:
            if filename.startswith('.'):
                continue
            
            filepath = os.path.join(root, filename)
            
            # Skip obvious binary/large files
            try:
                size = os.path.getsize(filepath)
                if size > 10 * 1024 * 1024:  # Skip files > 10MB
                    continue
                if size == 0:
                    continue
            except:
                continue
            
            # Check extension
            if file_extensions:
                if not any(filename.endswith(ext) for ext in file_extensions):
                    continue
            else:
                # Default to text extensions
                if not any(filename.endswith(ext) for ext in text_extensions):
                    continue
            
            files_to_index.append(filepath)
    
    print(f"📁 Found {len(files_to_index)} files to index in {source_name}")
    
    doc_count = 0
    chunk_count = 0
    
    # Index with progress bar
    for filepath in tqdm(files_to_index, desc=f"Indexing {source_name}"):
        try:
            # Quick binary check
            if not is_text_file(filepath):
                continue
            
            # Get file content
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if len(content) < 50:  # Skip tiny files
                continue
            
            if len(content) > 5 * 1024 * 1024:  # Skip files > 5MB text
                continue
            
            # Compute hash
            file_hash = compute_sha256(filepath)
            
            # Check if already indexed
            cursor = conn.execute(
                "SELECT id FROM documents WHERE path = ? AND sha256 = ?",
                (filepath, file_hash)
            )
            if cursor.fetchone():
                continue  # Already indexed
            
            # Create document ID
            doc_id = f"{source_name}_{hashlib.md5(filepath.encode()).hexdigest()[:16]}"
            
            # Extract title from first line or filename
            title = os.path.basename(filepath)
            first_line = content.split('\n')[0][:100]
            if first_line.startswith('#'):
                title = first_line.lstrip('# ').strip()
            
            # Insert document
            conn.execute(
                """INSERT OR REPLACE INTO documents 
                   (id, source, path, title, content, sha256, indexed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (doc_id, source_name, filepath, title, content, file_hash, datetime.now())
            )
            
            # Chunk content
            chunks = chunk_content(content)
            
            # Insert chunks
            for i, chunk_text in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                conn.execute(
                    """INSERT OR REPLACE INTO chunks
                       (id, document_id, content, start_line, end_line)
                       VALUES (?, ?, ?, ?, ?)""",
                    (chunk_id, doc_id, chunk_text, i*320, min((i+1)*400, len(content.split())))
                )
                chunk_count += 1
            
            doc_count += 1
            
        except Exception as e:
            # Skip files that can't be read
            continue
    
    # Update source tracking
    conn.execute(
        """INSERT OR REPLACE INTO sources 
           (name, path, document_count, chunk_count, last_sync)
           VALUES (?, ?, ?, ?, ?)""",
        (source_name, dir_path, doc_count, chunk_count, datetime.now())
    )
    
    conn.commit()
    conn.close()
    
    return doc_count, chunk_count

def get_index_stats():
    """Get current index statistics"""
    conn = sqlite3.connect(DB_PATH)
    
    # Total documents
    cursor = conn.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]
    
    # Total chunks
    cursor = conn.execute("SELECT COUNT(*) FROM chunks")
    total_chunks = cursor.fetchone()[0]
    
    # By source
    cursor = conn.execute("SELECT source, COUNT(*) FROM documents GROUP BY source")
    by_source = cursor.fetchall()
    
    # Sources table
    cursor = conn.execute("SELECT name, document_count, last_sync FROM sources")
    sources_info = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_docs': total_docs,
        'total_chunks': total_chunks,
        'by_source': by_source,
        'sources_info': sources_info
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Massive Context Indexing")
    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--index', metavar='SOURCE:PATH', help='Index directory (format: source_name:/path/to/dir)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--all', action='store_true', help='Index all primary workspaces')
    
    args = parser.parse_args()
    
    if args.init:
        print("🔧 Initializing database...")
        init_database()
        print("✅ Database initialized")
    
    elif args.index:
        source, path = args.index.split(':', 1)
        print(f"🚀 Indexing {source} from {path}")
        docs, chunks = index_directory(source, path)
        print(f"✅ Indexed {docs} documents, {chunks} chunks")
    
    elif args.stats:
        stats = get_index_stats()
        print("\n📊 INDEX STATISTICS")
        print("="*50)
        print(f"Total documents: {stats['total_docs']:,}")
        print(f"Total chunks: {stats['total_chunks']:,}")
        print("\nBy source:")
        for source, count in stats['by_source']:
            print(f"  - {source}: {count:,}")
        print("\nSources tracking:")
        for name, count, last_sync in stats['sources_info']:
            print(f"  - {name}: {count:,} docs (last sync: {last_sync})")
    
    elif args.all:
        print("🚀 MASSIVE CONTEXT INDEXING SPRINT")
        print("="*50)
        
        init_database()
        
        targets = [
            ("clawd", "~/clawd", ['.md', '.py', '.txt', '.json', '.yaml', '.yml', '.sh']),
            ("dgc", "~/DHARMIC_GODEL_CLAW", ['.md', '.py', '.txt', '.json']),
            ("mech_interp", "~/mech-interp-latent-lab-phase1", ['.md', '.py', '.txt', '.json', '.ipynb']),
            ("psmv_full", "~/Persistent-Semantic-Memory-Vault", ['.md', '.txt']),
            ("recognition", "~/RECOGNITION_LAB", ['.md', '.py', '.txt']),
        ]
        
        total_docs = 0
        total_chunks = 0
        
        for source_name, path, extensions in targets:
            print(f"\n📁 Indexing {source_name}...")
            docs, chunks = index_directory(source_name, path, extensions, ['.git', 'node_modules', '__pycache__', '.venv', 'venv'])
            print(f"✅ {source_name}: {docs} docs, {chunks} chunks")
            total_docs += docs
            total_chunks += chunks
        
        print("\n" + "="*50)
        print(f"🎉 SPRINT COMPLETE")
        print(f"   Total documents: {total_docs:,}")
        print(f"   Total chunks: {total_chunks:,}")
        
        # Show final stats
        stats = get_index_stats()
        print(f"\n📊 DATABASE TOTALS:")
        print(f"   {stats['total_docs']:,} documents")
        print(f"   {stats['total_chunks']:,} chunks")
    
    else:
        parser.print_help()
