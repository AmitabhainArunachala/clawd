"""
arXiv Fetcher Module
Handles fetching and scoring papers from arXiv API
"""

import arxiv
from datetime import datetime, timedelta, timezone
from typing import List, Tuple


class ArxivFetcher:
    """Fetch and filter arXiv papers"""
    
    def __init__(self, categories: List[str] = None, keywords: List[str] = None):
        self.categories = categories or ["cs.AI", "cs.CL", "cs.LG", "cs.CV"]
        self.keywords = keywords or [
            "consciousness", "self-awareness", "recursive", "self-reference",
            "interpretability", "mechanistic", "emergence", "emergent",
            "attention mechanism", "transformer", "large language model",
            "alignment", "safety", "agency", "autonomy"
        ]
        
        # Scoring weights
        self.high_value_terms = {
            "consciousness": 3.0,
            "self-aware": 2.5,
            "self-reference": 2.0,
            "recursive": 1.5,
            "interpretability": 1.5,
            "mechanistic": 1.5,
            "emergent": 1.5,
            "agency": 1.5,
            "qualia": 2.0,
            "phenomenal": 1.5,
            "sentience": 2.0,
            "attention collapse": 2.5,
            "inner monologue": 1.5,
            "chain of thought": 1.0,
        }
    
    def fetch_recent_papers(self, days: int = 1, max_results: int = 50) -> List[arxiv.Result]:
        """
        Fetch recent papers from arXiv
        
        Args:
            days: Number of days to look back
            max_results: Maximum papers to fetch
            
        Returns:
            List of arXiv paper results
        """
        # Build category query
        cat_query = " OR ".join([f"cat:{c}" for c in self.categories])
        
        # Search arXiv
        search = arxiv.Search(
            query=cat_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        
        # Filter by date (timezone-aware)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        papers = []
        
        for result in search.results():
            if result.published >= cutoff_date:
                papers.append(result)
        
        return papers
    
    def score_paper(self, paper: arxiv.Result) -> float:
        """
        Score paper relevance to consciousness research
        
        Args:
            paper: arXiv paper result
            
        Returns:
            Relevance score (0.0 to 1.0+)
        """
        text = f"{paper.title} {paper.summary}".lower()
        score = 0.0
        
        # Score based on high-value terms
        for term, weight in self.high_value_terms.items():
            if term in text:
                score += weight
        
        # General keyword matching
        keyword_matches = sum(1 for kw in self.keywords if kw.lower() in text)
        score += keyword_matches * 0.3
        
        # Normalize to 0-1 range (roughly)
        score = min(score / 10.0, 1.0)
        
        return score
    
    def score_and_rank(self, papers: List[arxiv.Result]) -> List[Tuple[arxiv.Result, float]]:
        """
        Score and rank papers by relevance
        
        Args:
            papers: List of arXiv papers
            
        Returns:
            List of (paper, score) tuples, sorted by score descending
        """
        scored = [(paper, self.score_paper(paper)) for paper in papers]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def fetch_by_query(self, query: str, max_results: int = 20) -> List[arxiv.Result]:
        """
        Fetch papers by custom query
        
        Args:
            query: arXiv search query
            max_results: Maximum results
            
        Returns:
            List of arXiv paper results
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        return list(search.results())
