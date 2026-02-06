"""
Search query and result types for unified memory indexer.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchQuery:
    """A search query against the unified index."""
    query: str
    sources: List[str] = field(default_factory=lambda: ['all'])
    min_relevance: float = 0.0
    limit: int = 10
    hybrid: bool = True
    
    def __post_init__(self):
        if isinstance(self.sources, str):
            self.sources = [self.sources]


@dataclass
class SearchResult:
    """A single search result from the unified index."""
    id: str
    document_id: str
    title: str
    content: str
    source: str
    path: str
    score: float
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'document_id': self.document_id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'path': self.path,
            'score': self.score,
            'start_line': self.start_line,
            'end_line': self.end_line
        }
