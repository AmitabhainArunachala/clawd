"""
Source-specific indexers for PSMV, conversations, and code.
"""

import os
import re
from pathlib import Path
from typing import Iterator, Dict, Any, List
from datetime import datetime

from .index import Document, UnifiedIndex


class BaseIndexer:
    """Base class for source-specific indexers."""
    
    def __init__(self, unified_index: UnifiedIndex):
        self.unified_index = unified_index
    
    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 80) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens (approximated as words/1.3)
            overlap: Number of tokens to overlap between chunks
            
        Returns:
            List of chunk dicts with content and line numbers
        """
        lines = text.split('\n')
        chunks = []
        
        current_chunk = []
        current_start = 0
        current_tokens = 0
        
        for i, line in enumerate(lines):
            line_tokens = len(line.split()) / 1.3  # Rough token estimate
            
            if current_tokens + line_tokens > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'content': '\n'.join(current_chunk),
                    'start_line': current_start + 1,
                    'end_line': i
                })
                
                # Start new chunk with overlap
                overlap_lines = int(overlap / (chunk_size / len(current_chunk))) if current_chunk else 0
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                current_start = i - len(current_chunk)
                current_tokens = sum(len(l.split()) for l in current_chunk) / 1.3
            
            current_chunk.append(line)
            current_tokens += line_tokens
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'start_line': current_start + 1,
                'end_line': len(lines)
            })
        
        return chunks


class PSMVIndexer(BaseIndexer):
    """Indexer for Persistent Semantic Memory Vault."""
    
    def __init__(self, index: UnifiedIndex, vault_path: str):
        super().__init__(index)
        self.vault_path = Path(vault_path)
    
    def index(self, force: bool = False) -> int:
        """
        Index all files in PSMV.
        
        Args:
            force: If True, re-index all files. If False, only new/changed files.
            
        Returns:
            Number of documents indexed
        """
        count = 0
        
        # Find all markdown files in vault
        md_files = list(self.vault_path.rglob("*.md"))
        
        for file_path in md_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                sha256 = self.unified_index.compute_sha256(content)
                
                # Check if already indexed and unchanged
                if not force:
                    # Would check against existing index here
                    pass
                
                # Extract title from first heading
                title = self._extract_title(content) or file_path.name
                
                # Create document
                doc = Document(
                    id=f"psmv:{file_path.relative_to(self.vault_path)}",
                    source="psmv",
                    path=str(file_path),
                    title=title,
                    content=content,
                    sha256=sha256,
                    indexed_at=datetime.now(),
                    metadata={
                        "filename": file_path.name,
                        "relative_path": str(file_path.relative_to(self.vault_path))
                    }
                )
                
                # Chunk and index
                chunks = self.chunk_text(content)
                self.unified_index.add_document(doc, chunks)
                count += 1
                
                if count % 100 == 0:
                    print(f"Indexed {count} PSMV documents...")
                    
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
        
        return count
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        # Look for first # heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""


class ConversationIndexer(BaseIndexer):
    """Indexer for session transcripts."""
    
    def __init__(self, index: UnifiedIndex, sessions_path: str):
        super().__init__(index)
        self.sessions_path = Path(sessions_path)
    
    def index(self, force: bool = False) -> int:
        """Index all session transcripts."""
        count = 0
        
        # Find session files
        session_files = list(self.sessions_path.glob("*.jsonl"))
        
        for file_path in session_files:
            try:
                # Parse JSONL
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                sha256 = self.unified_index.compute_sha256(content)
                
                # Extract conversation content
                lines = content.strip().split('\n')
                conversation_text = self._parse_jsonl(lines)
                
                doc = Document(
                    id=f"conversation:{file_path.name}",
                    source="conversation",
                    path=str(file_path),
                    title=f"Session: {file_path.stem}",
                    content=conversation_text,
                    sha256=sha256,
                    indexed_at=datetime.now(),
                    metadata={
                        "filename": file_path.name,
                        "message_count": len(lines)
                    }
                )
                
                chunks = self.chunk_text(conversation_text)
                self.unified_index.add_document(doc, chunks)
                count += 1
                
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
        
        return count
    
    def _parse_jsonl(self, lines: List[str]) -> str:
        """Parse JSONL and extract conversation text."""
        import json
        texts = []
        for line in lines:
            try:
                data = json.loads(line)
                if 'content' in data:
                    texts.append(data['content'])
                elif 'message' in data:
                    texts.append(data['message'])
            except:
                pass
        return '\n'.join(texts)


class CodeIndexer(BaseIndexer):
    """Indexer for code repositories."""
    
    CODE_EXTENSIONS = {'.py', '.js', '.ts', '.rs', '.go', '.java', '.cpp', '.c', '.h', '.rb'}
    
    def __init__(self, index: UnifiedIndex, code_paths: List[str]):
        super().__init__(index)
        self.code_paths = [Path(p) for p in code_paths]
    
    def index(self, force: bool = False) -> int:
        """Index all code files."""
        count = 0
        
        for base_path in self.code_paths:
            if not base_path.exists():
                continue
            
            for ext in self.CODE_EXTENSIONS:
                for file_path in base_path.rglob(f"*{ext}"):
                    try:
                        # Skip common exclude patterns
                        if any(part.startswith('.') for part in file_path.parts):
                            continue
                        if 'node_modules' in str(file_path) or '__pycache__' in str(file_path):
                            continue
                        
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        if len(content) > 100000:  # Skip huge files
                            continue
                        
                        sha256 = self.unified_index.compute_sha256(content)
                        
                        doc = Document(
                            id=f"code:{file_path}",
                            source="code",
                            path=str(file_path),
                            title=file_path.name,
                            content=content,
                            sha256=sha256,
                            indexed_at=datetime.now(),
                            metadata={
                                "language": file_path.suffix,
                                "size": len(content)
                            }
                        )
                        
                        chunks = self.chunk_text(content, chunk_size=300)  # Smaller chunks for code
                        self.unified_index.add_document(doc, chunks)
                        count += 1
                        
                    except Exception as e:
                        pass  # Silently skip problematic files
        
        return count
