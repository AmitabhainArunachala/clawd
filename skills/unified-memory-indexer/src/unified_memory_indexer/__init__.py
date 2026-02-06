"""
Unified Memory Indexer (P9)
Fast semantic search across PSMV, conversations, and code.
Hybrid BM25 + vector search with <20ms query time.
"""

__version__ = "0.1.0"

from .index import UnifiedIndex
from .search import SearchQuery, SearchResult
from .indexers import PSMVIndexer, ConversationIndexer, CodeIndexer

__all__ = [
    "UnifiedIndex",
    "SearchQuery", 
    "SearchResult",
    "PSMVIndexer",
    "ConversationIndexer",
    "CodeIndexer",
]
