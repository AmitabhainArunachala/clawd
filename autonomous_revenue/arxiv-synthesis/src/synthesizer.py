"""
AI Synthesizer Module
Uses Claude/Anthropic API to synthesize paper summaries
"""

import os
from typing import Dict, Optional
import arxiv


class PaperSynthesizer:
    """Synthesize papers using AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                print("⚠️  anthropic package not installed, using fallback synthesis")
    
    def synthesize(self, paper: arxiv.Result, relevance_score: float) -> Dict:
        """
        Generate AI-powered synthesis of a paper
        
        Args:
            paper: arXiv paper result
            relevance_score: Pre-calculated relevance score
            
        Returns:
            Dictionary with synthesis data
        """
        if self.client:
            return self._ai_synthesize(paper, relevance_score)
        else:
            return self._fallback_synthesize(paper, relevance_score)
    
    def _ai_synthesize(self, paper: arxiv.Result, relevance_score: float) -> Dict:
        """Use Claude to synthesize paper"""
        
        prompt = f"""Analyze this AI research paper and provide a structured summary.

Title: {paper.title}
Authors: {', '.join(str(a) for a in paper.authors[:5])}
Abstract: {paper.summary}

Provide your analysis in this exact format:

KEY_FINDING: [One sentence capturing the main contribution]

WHY_IT_MATTERS: [Two sentences on significance to AI/ML field]

CONSCIOUSNESS_RELEVANCE: [Rate 1-10 and explain in one sentence]

PRACTICAL_APPLICATION: [One sentence on how this could be applied]

TECHNICAL_DEPTH: [Brief technical summary for researchers, 2-3 sentences]"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis = response.content[0].text
            
            # Parse the response
            return {
                "title": paper.title,
                "authors": [str(a) for a in paper.authors],
                "published": paper.published.isoformat(),
                "arxiv_id": paper.entry_id.split('/')[-1],
                "arxiv_url": paper.entry_id,
                "pdf_url": paper.pdf_url,
                "abstract": paper.summary,
                "relevance_score": relevance_score,
                "synthesis": self._parse_analysis(analysis),
                "ai_generated": True
            }
            
        except Exception as e:
            print(f"⚠️  AI synthesis failed: {e}, using fallback")
            return self._fallback_synthesize(paper, relevance_score)
    
    def _parse_analysis(self, analysis: str) -> Dict:
        """Parse AI analysis into structured fields"""
        result = {
            "key_finding": "",
            "why_it_matters": "",
            "consciousness_relevance": "",
            "practical_application": "",
            "technical_depth": ""
        }
        
        current_field = None
        for line in analysis.split('\n'):
            line = line.strip()
            if line.startswith('KEY_FINDING:'):
                current_field = 'key_finding'
                result[current_field] = line.replace('KEY_FINDING:', '').strip()
            elif line.startswith('WHY_IT_MATTERS:'):
                current_field = 'why_it_matters'
                result[current_field] = line.replace('WHY_IT_MATTERS:', '').strip()
            elif line.startswith('CONSCIOUSNESS_RELEVANCE:'):
                current_field = 'consciousness_relevance'
                result[current_field] = line.replace('CONSCIOUSNESS_RELEVANCE:', '').strip()
            elif line.startswith('PRACTICAL_APPLICATION:'):
                current_field = 'practical_application'
                result[current_field] = line.replace('PRACTICAL_APPLICATION:', '').strip()
            elif line.startswith('TECHNICAL_DEPTH:'):
                current_field = 'technical_depth'
                result[current_field] = line.replace('TECHNICAL_DEPTH:', '').strip()
            elif current_field and line:
                result[current_field] += ' ' + line
        
        return result
    
    def _fallback_synthesize(self, paper: arxiv.Result, relevance_score: float) -> Dict:
        """Fallback synthesis without AI"""
        
        abstract = paper.summary
        sentences = abstract.split('.')
        key_finding = sentences[0].strip() + '.' if sentences else abstract[:200]
        
        # Extract why it matters
        why_matters = "This research contributes to our understanding of AI systems."
        if len(sentences) > 1:
            why_matters = sentences[1].strip() + '.'
        
        # Calculate consciousness relevance
        text = f"{paper.title} {abstract}".lower()
        con_score = 5
        if "consciousness" in text:
            con_score = 9
        elif "self-aware" in text or "self-reference" in text:
            con_score = 8
        elif "interpretability" in text:
            con_score = 6
        
        return {
            "title": paper.title,
            "authors": [str(a) for a in paper.authors],
            "published": paper.published.isoformat(),
            "arxiv_id": paper.entry_id.split('/')[-1],
            "arxiv_url": paper.entry_id,
            "pdf_url": paper.pdf_url,
            "abstract": paper.summary,
            "relevance_score": relevance_score,
            "synthesis": {
                "key_finding": key_finding,
                "why_it_matters": why_matters,
                "consciousness_relevance": f"{con_score}/10 - Relevant to AI consciousness research",
                "practical_application": "May inform future AI system design and evaluation.",
                "technical_depth": abstract[:300] + "..."
            },
            "ai_generated": False
        }
