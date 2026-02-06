"""Report Generator

Generates formatted audit reports.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    STRONG_SUPPORT = "strong_support"
    SUPPORT = "support"
    WEAK_SUPPORT = "weak_support"
    INSUFFICIENT = "insufficient"
    REJECT = "reject"


@dataclass
class AuditReport:
    """Formatted audit report."""
    claim: str
    verdict: Verdict
    evidence: Dict[str, Any]
    gaps: List[str]
    recommendations: List[str]
    confidence: float
    
    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# Audit Report: {self.claim[:50]}",
            "",
            f"**Verdict:** {self.verdict.value.upper()}",
            f"**Confidence:** {self.confidence*100:.1f}%",
            "",
            "## Gaps",
        ]
        for gap in self.gaps:
            lines.append(f"- ⚠️ {gap}")
        
        lines.extend(["", "## Recommendations"])
        for rec in self.recommendations:
            lines.append(f"- 💡 {rec}")
        
        return "\n".join(lines)


class ReportGenerator:
    """Generates audit reports."""
    
    def generate(
        self,
        claim: str,
        verdict: Verdict,
        evidence: Dict[str, Any],
        gaps: List[str],
        recommendations: List[str],
        confidence: float,
    ) -> AuditReport:
        """Generate a report."""
        return AuditReport(
            claim=claim,
            verdict=verdict,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            confidence=confidence,
        )
