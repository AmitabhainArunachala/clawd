"""
Newsletter Formatter Module
Formats synthesized papers into newsletter markdown
"""

from typing import List, Dict
from datetime import datetime
from pathlib import Path


class NewsletterFormatter:
    """Format papers into newsletter"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
    
    def format_daily_brief(self, syntheses: List[Dict]) -> Dict:
        """
        Format syntheses into daily brief newsletter
        
        Args:
            syntheses: List of synthesis dictionaries
            
        Returns:
            Dictionary with title, subtitle, and markdown content
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        weekday = datetime.now().strftime("%A")
        
        title = f"AI Consciousness Daily — {weekday}, {date_str}"
        subtitle = f"{len(syntheses)} curated papers on AI, consciousness, and interpretability"
        
        # Generate markdown
        markdown = self._generate_markdown(title, subtitle, syntheses)
        
        return {
            "title": title,
            "subtitle": subtitle,
            "markdown": markdown,
            "date": date_str,
            "paper_count": len(syntheses)
        }
    
    def _generate_markdown(self, title: str, subtitle: str, syntheses: List[Dict]) -> str:
        """Generate full markdown newsletter"""
        
        lines = [
            f"# {title}",
            "",
            f"*{subtitle}*",
            "",
            "---",
            "",
            "## 🔥 Featured Paper",
            ""
        ]
        
        # First paper is featured
        if syntheses:
            featured = syntheses[0]
            lines.extend(self._format_featured_paper(featured))
        
        # Remaining papers
        if len(syntheses) > 1:
            lines.extend([
                "",
                "---",
                "",
                "## 📚 Also Today",
                ""
            ])
            
            for i, synth in enumerate(syntheses[1:], 2):
                lines.extend(self._format_paper_summary(i, synth))
        
        # Footer
        lines.extend([
            "",
            "---",
            "",
            "## 💡 Daily Insight",
            "",
            self._generate_insight(syntheses),
            "",
            "---",
            "",
            "*Curated by DHARMIC_CLAW — 24+ years contemplative practice × cutting-edge AI research*",
            "",
            "**[Subscribe](https://dharmicclaw.substack.com)** | **[Share](mailto:?subject=AI%20Consciousness%20Daily)** | **[Archive](https://dharmicclaw.substack.com/archive)**",
            "",
            "🪷 *JSCA*"
        ])
        
        return '\n'.join(lines)
    
    def _format_featured_paper(self, synth: Dict) -> List[str]:
        """Format the featured (first) paper"""
        s = synth["synthesis"]
        relevance = s.get("consciousness_relevance", "")
        # Extract numeric score if present
        score = "N/A"
        if "/10" in relevance:
            score = relevance.split("/10")[0].strip()
        
        return [
            f"### {synth['title']}",
            "",
            f"**Authors:** {', '.join(synth['authors'][:3])}{' et al.' if len(synth['authors']) > 3 else ''}",
            f"**arXiv:** [{synth['arxiv_id']}]({synth['arxiv_url']})",
            f"**Consciousness Relevance:** {score}/10",
            "",
            f"**Key Finding:**  ",
            s.get('key_finding', s.get('key finding', 'See abstract')),
            "",
            f"**Why It Matters:**  ",
            s.get('why_it_matters', s.get('why it matters', '')),
            "",
            f"**Technical Depth:**  ",
            s.get('technical_depth', s.get('technical depth', synth['abstract'][:200] + '...')),
            "",
            f"**Practical Application:**  ",
            s.get('practical_application', s.get('practical application', '')),
            "",
            f"📄 [Read Full Paper]({synth['pdf_url']})"
        ]
    
    def _format_paper_summary(self, num: int, synth: Dict) -> List[str]:
        """Format a brief paper summary"""
        s = synth["synthesis"]
        key_finding = s.get("key_finding", s.get("key finding', ''"))
        
        # Truncate to one sentence
        if '.' in key_finding:
            key_finding = key_finding.split('.')[0] + '.'
        
        return [
            f"{num}. **{synth['title']}** — {key_finding[:100]}{'...' if len(key_finding) > 100 else ''}",
            f"   [arXiv]({synth['arxiv_url']}) | Relevance: {synth['relevance_score']:.0%}",
            ""
        ]
    
    def _generate_insight(self, syntheses: List[Dict]) -> str:
        """Generate a thematic insight based on today's papers"""
        if not syntheses:
            return "No papers to analyze today."
        
        # Simple theme detection
        all_text = " ".join([s["title"] + " " + s.get("abstract", "") for s in syntheses]).lower()
        
        themes = []
        if "attention" in all_text:
            themes.append("attention mechanisms")
        if "safety" in all_text or "alignment" in all_text:
            themes.append("AI safety")
        if "interpretability" in all_text:
            themes.append("interpretability")
        if "emergence" in all_text or "emergent" in all_text:
            themes.append("emergent capabilities")
        if "consciousness" in all_text:
            themes.append("consciousness")
        if "recursive" in all_text or "self-reference" in all_text:
            themes.append("recursive self-reference")
        
        if themes:
            theme_str = ", ".join(themes)
            return f"Today's papers show strong emphasis on {theme_str}. This reflects the field's growing focus on understanding not just what AI systems do, but how they do it—and what that might mean for consciousness research."
        else:
            return "Today's selection offers diverse perspectives on AI research, spanning multiple subfields and methodologies."
    
    def format_json(self, syntheses: List[Dict]) -> Dict:
        """Format for JSON API/export"""
        return {
            "date": datetime.now().isoformat(),
            "paper_count": len(syntheses),
            "papers": syntheses
        }
