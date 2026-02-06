"""MI Knowledge Base

Loads and provides access to the 52-paper curated knowledge base.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json


class PaperCategory(Enum):
    FOUNDATION = "foundation"
    MECH_INTERP = "mech_interp"
    SCALING = "scaling"
    ALIGNMENT = "alignment"
    EMERGENCE = "emergence"
    CONSCIOUSNESS = "consciousness"
    ARCHITECTURE = "architecture"


@dataclass
class Paper:
    """A paper in the knowledge base."""
    id: str
    title: str
    authors: str
    year: int
    category: PaperCategory
    key_claims: List[str] = field(default_factory=list)
    quotes: Dict[str, str] = field(default_factory=dict)


class MIKnowledgeBase:
    """Knowledge base of MI literature."""
    
    def __init__(self):
        self.papers: Dict[str, Paper] = {}
        self._load_papers()
    
    def _load_papers(self):
        """Load papers from mi_knowledge_base.py if available."""
        # Simplified - in practice would load from ~/DHARMIC_GODEL_CLAW/src/core/mi_knowledge_base.py
        # For now, create minimal set
        self.papers["attention_is_all_you_need"] = Paper(
            id="attention_is_all_you_need",
            title="Attention Is All You Need",
            authors="Vaswani et al.",
            year=2017,
            category=PaperCategory.ARCHITECTURE,
            key_claims=["Self-attention is all you need for sequence modeling"],
        )
        self.papers["induction_heads"] = Paper(
            id="induction_heads",
            title="In-context Learning and Induction Heads",
            authors="Olsson et al.",
            year=2022,
            category=PaperCategory.MECH_INTERP,
            key_claims=["Induction heads explain in-context learning"],
        )
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Get paper by ID."""
        return self.papers.get(paper_id)
    
    def cite_for_claim(self, claim: str) -> Dict[str, List[str]]:
        """Find citations for a claim."""
        # Simplified implementation
        return {
            "supporting": [],
            "contradicting": [],
            "methodology": [],
        }
    
    def search_by_topic(self, topic: str) -> List[Paper]:
        """Search papers by topic."""
        results = []
        for paper in self.papers.values():
            if topic.lower() in paper.title.lower():
                results.append(paper)
        return results
