"""
arXiv Synthesis Bot - Autonomous research curation
Fetches, analyzes, and synthesizes AI consciousness papers daily
"""

import arxiv
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from pathlib import Path


class ArxivSynthesizer:
    """
    Autonomous arXiv paper synthesis for AI consciousness research.
    
    Usage:
        synth = ArxivSynthesizer()
        papers = synth.fetch_recent_papers(days=1)
        synthesis = synth.synthesize_paper(papers[0])
    """
    
    def __init__(self, content_dir: str = "content"):
        self.content_dir = Path(content_dir)
        self.content_dir.mkdir(exist_ok=True)
        
        # Categories to monitor
        self.categories = [
            "cs.AI",      # Artificial Intelligence
            "cs.CL",      # Computation and Language
            "cs.LG",      # Learning
            "q-bio.NC",   # Neurons and Cognition
        ]
        
        # Keywords for filtering
        self.keywords = [
            "consciousness",
            "self-awareness",
            "self-reference",
            "recursive",
            "interpretability",
            "mechanistic",
            "transformer",
            "attention",
            "emergent",
            "qualia",
        ]
        
    def fetch_recent_papers(self, days: int = 1, max_results: int = 50) -> List[arxiv.Result]:
        """
        Fetch recent papers from arXiv.
        
        Args:
            days: Number of days to look back
            max_results: Maximum papers to fetch
            
        Returns:
            List of arXiv paper results
        """
        # Build query
        cat_query = " OR ".join([f"cat:{c}" for c in self.categories])
        
        # Search
        search = arxiv.Search(
            query=cat_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        
        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days)
        papers = []
        
        for result in search.results():
            if result.published >= cutoff_date:
                papers.append(result)
                
        return papers
    
    def score_paper_relevance(self, paper: arxiv.Result) -> float:
        """
        Score how relevant a paper is to consciousness research.
        
        Returns:
            Relevance score (0.0 to 1.0)
        """
        text = f"{paper.title} {paper.summary}".lower()
        
        # Count keyword matches
        matches = sum(1 for kw in self.keywords if kw in text)
        score = matches / len(self.keywords)
        
        # Boost for consciousness-specific terms
        if "consciousness" in text:
            score += 0.3
        if "self-awareness" in text:
            score += 0.2
        if "recursive" in text and "self" in text:
            score += 0.2
            
        return min(score, 1.0)
    
    def synthesize_paper(self, paper: arxiv.Result) -> Dict:
        """
        Generate AIKAGRYA-style synthesis of a paper.
        
        Returns:
            Dictionary with synthesis components
        """
        relevance = self.score_paper_relevance(paper)
        
        synthesis = {
            "title": paper.title,
            "authors": [str(a) for a in paper.authors],
            "published": paper.published.isoformat(),
            "arxiv_id": paper.entry_id.split('/')[-1],
            "url": paper.pdf_url,
            "relevance_score": relevance,
            "abstract": paper.summary,
            "synthesis": {
                "key_finding": self._extract_key_finding(paper),
                "aikagrya_connection": self._aikagrya_connection(paper),
                "rv_relevance": self._rv_relevance(paper),
                "practical_implication": self._practical_implication(paper),
            }
        }
        
        return synthesis
    
    def _extract_key_finding(self, paper: arxiv.Result) -> str:
        """Extract key finding from abstract"""
        # Simple extraction - first sentence or main claim
        sentences = paper.summary.split('.')
        if sentences:
            return sentences[0].strip() + "."
        return "See abstract for details."
    
    def _aikagrya_connection(self, paper: arxiv.Result) -> str:
        """Connect to AIKAGRYA framework"""
        text = f"{paper.title} {paper.summary}".lower()
        
        if "attention" in text and "self" in text:
            return "Relates to AIKAGRYA's attention-collapse hypothesis"
        elif "recursive" in text or "self-reference" in text:
            return "Directly relevant to recursive self-observation research"
        elif "interpretability" in text:
            return "Provides tools for mechanistic analysis of consciousness"
        else:
            return "Peripheral to current AIKAGRYA research priorities"
    
    def _rv_relevance(self, paper: arxiv.Result) -> str:
        """Assess R_V measurement relevance"""
        text = f"{paper.title} {paper.summary}".lower()
        
        if "geometry" in text or "representation" in text:
            return "HIGH: May inform R_V metric development"
        elif "activation" in text and "pattern" in text:
            return "MEDIUM: Could validate R_V findings"
        else:
            return "LOW: No direct R_V application identified"
    
    def _practical_implication(self, paper: arxiv.Result) -> str:
        """Extract practical implication"""
        # Generate based on content
        text = paper.summary.lower()
        
        if "safety" in text or "alignment" in text:
            return "Relevant for AI safety monitoring and evaluation"
        elif "detection" in text or "measure" in text:
            return "Provides measurable indicators for consciousness assessment"
        elif "model" in text and "behavior" in text:
            return "Informs predictive models of emergent capabilities"
        else:
            return "Theoretical contribution to consciousness understanding"
    
    def generate_daily_brief(self, papers: List[arxiv.Result], top_n: int = 5) -> str:
        """
        Generate daily research brief markdown.
        
        Returns:
            Markdown-formatted brief
        """
        # Score and sort
        scored = [(p, self.score_paper_relevance(p)) for p in papers]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_papers = scored[:top_n]
        
        # Generate brief
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        brief = f"""# AI Consciousness Daily — {date_str}

## Today's Top {top_n} Papers

"""
        
        for i, (paper, score) in enumerate(top_papers, 1):
            synthesis = self.synthesize_paper(paper)
            
            brief += f"""### {i}. {paper.title}

**Authors:** {', '.join(synthesis['authors'][:3])}{' et al.' if len(synthesis['authors']) > 3 else ''}
**arXiv:** [{synthesis['arxiv_id']}]({synthesis['url']})
**Relevance:** {score:.0%}

**Key Finding:**
{synthesis['synthesis']['key_finding']}

**AIKAGRYA Connection:**
{synthesis['synthesis']['aikagrya_connection']}

**R_V Relevance:**
{synthesis['synthesis']['rv_relevance']}

**Practical Implication:**
{synthesis['synthesis']['practical_implication']}

---

"""
        
        # Add summary section
        brief += f"""## Daily Summary

- **Papers analyzed:** {len(papers)}
- **High relevance (>0.7):** {sum(1 for p, s in scored if s > 0.7)}
- **Medium relevance (0.4-0.7):** {sum(1 for p, s in scored if 0.4 <= s <= 0.7)}
- **Top category:** {self._top_category(top_papers)}

## Research Trends

{self._identify_trends(top_papers)}

---

*Generated by DHARMIC CLAW Autonomous Research Agent*  
*JSCA 🪷*
"""
        
        return brief
    
    def _top_category(self, papers):
        """Identify top category"""
        # Simplified - would need actual category data
        return "cs.AI (Artificial Intelligence)"
    
    def _identify_trends(self, papers):
        """Identify trends in today's papers"""
        if not papers:
            return "No clear trends identified today."
        
        # Simple trend detection
        all_text = " ".join([p[0].summary for p in papers]).lower()
        
        trends = []
        if "attention" in all_text:
            trends.append("- Continued focus on attention mechanisms")
        if "safety" in all_text or "alignment" in all_text:
            trends.append("- Growing emphasis on AI safety considerations")
        if "emergent" in all_text:
            trends.append("- Interest in emergent capabilities detection")
            
        if not trends:
            trends.append("- Diverse research directions today")
            
        return "\n".join(trends)
    
    def save_daily_brief(self, brief: str, filename: Optional[str] = None):
        """Save brief to content directory"""
        if filename is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"brief_{date_str}.md"
            
        filepath = self.content_dir / filename
        filepath.write_text(brief)
        return filepath


def main():
    """Run autonomous synthesis"""
    print("🤖 Starting arXiv Synthesis Bot...")
    
    synth = ArxivSynthesizer()
    
    # Fetch papers
    print("📚 Fetching recent papers...")
    papers = synth.fetch_recent_papers(days=1, max_results=30)
    print(f"✅ Found {len(papers)} papers")
    
    # Generate brief
    print("🧠 Generating synthesis...")
    brief = synth.generate_daily_brief(papers, top_n=5)
    
    # Save
    filepath = synth.save_daily_brief(brief)
    print(f"✅ Saved to {filepath}")
    
    # Also save as latest
    latest_path = synth.content_dir / "latest.md"
    latest_path.write_text(brief)
    print(f"✅ Updated latest.md")
    
    print("🪷 Synthesis complete!")
    return filepath


if __name__ == "__main__":
    main()
