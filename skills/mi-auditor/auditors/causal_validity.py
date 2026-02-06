"""Causal Validity Auditor

Validates causal claims through control checks and intervention analysis.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    STRONG_SUPPORT = "strong_support"
    SUPPORT = "support"
    WEAK_SUPPORT = "weak_support"
    INSUFFICIENT = "insufficient"
    REJECT = "reject"


@dataclass
class CausalResult:
    """Result of causal audit."""
    valid: bool
    n_controls: int
    controls_sufficient: bool
    effect_size_adequate: bool
    transfer_measured: bool
    baseline_present: bool
    recommendations: List[str]
    gaps: List[str]


class CausalAuditor:
    """Audits causal validity of experiments."""
    
    REQUIRED_CONTROLS = 4
    MIN_EFFECT_SIZE = 0.8
    
    def audit(self, experiment: Dict[str, Any]) -> CausalResult:
        """Audit causal experiment."""
        recommendations = []
        gaps = []
        
        n_controls = experiment.get("n_controls", 0)
        intervention = experiment.get("intervention_result", {})
        baseline = experiment.get("baseline")
        
        # Controls
        controls_sufficient = n_controls >= self.REQUIRED_CONTROLS
        if not controls_sufficient:
            gaps.append(f"Only {n_controls}/{self.REQUIRED_CONTROLS} controls")
            recommendations.append("Add random, shuffled, wrong-layer, orthogonal controls")
        
        # Effect size
        cohens_d = intervention.get("cohens_d", 0)
        effect_size_adequate = abs(cohens_d) >= self.MIN_EFFECT_SIZE if cohens_d else False
        if not effect_size_adequate:
            gaps.append(f"Small effect size (d={cohens_d})")
            recommendations.append("Effect size should be large (d>0.8)")
        
        # Transfer efficiency
        transfer = intervention.get("transfer_efficiency")
        transfer_measured = transfer is not None
        if not transfer_measured:
            gaps.append("Transfer efficiency not measured")
            recommendations.append("Measure transfer efficiency")
        
        # Baseline
        baseline_present = baseline is not None
        if not baseline_present:
            gaps.append("No baseline")
            recommendations.append("Include baseline measurement")
        
        valid = controls_sufficient and effect_size_adequate and baseline_present
        
        return CausalResult(
            valid=valid,
            n_controls=n_controls,
            controls_sufficient=controls_sufficient,
            effect_size_adequate=effect_size_adequate,
            transfer_measured=transfer_measured,
            baseline_present=baseline_present,
            recommendations=recommendations,
            gaps=gaps,
        )
