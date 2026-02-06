"""Statistical Rigor Auditor

Validates statistical claims for sample size, effect size, power, and corrections.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class Verdict(Enum):
    STRONG_SUPPORT = "strong_support"
    SUPPORT = "support"
    WEAK_SUPPORT = "weak_support"
    INSUFFICIENT = "insufficient"
    REJECT = "reject"


@dataclass
class StatisticalResult:
    """Result of statistical audit."""
    valid: bool
    effect_strength: str
    power_adequate: bool
    corrections_applied: bool
    confidence_interval_present: bool
    recommendations: List[str]
    gaps: List[str]


class StatisticalAuditor:
    """Audits statistical rigor of claims."""
    
    COHENS_D_SMALL = 0.2
    COHENS_D_MEDIUM = 0.5
    COHENS_D_LARGE = 0.8
    COHENS_D_HUGE = 2.0
    P_THRESHOLD = 0.05
    POWER_THRESHOLD = 0.8
    
    def audit(self, data: Dict[str, Any]) -> StatisticalResult:
        """Audit statistical measures."""
        recommendations = []
        gaps = []
        
        n = data.get("n", 0)
        cohens_d = data.get("cohens_d", 0)
        p_value = data.get("p_value", 1.0)
        power = data.get("power")
        ci = data.get("confidence_interval")
        
        # Sample size
        if n < 30:
            gaps.append(f"Small sample (n={n})")
            recommendations.append("Increase to n≥30 for CLT")
        elif n < 100:
            recommendations.append(f"n={n} adequate but larger improves power")
        
        # Effect size
        abs_d = abs(cohens_d)
        if abs_d >= self.COHENS_D_HUGE:
            effect_strength = "huge"
        elif abs_d >= self.COHENS_D_LARGE:
            effect_strength = "large"
        elif abs_d >= self.COHENS_D_MEDIUM:
            effect_strength = "medium"
        elif abs_d >= self.COHENS_D_SMALL:
            effect_strength = "small"
        else:
            effect_strength = "negligible"
        
        # Significance
        is_significant = p_value < self.P_THRESHOLD
        if not is_significant:
            gaps.append(f"Not significant (p={p_value})")
        
        # Power
        power_adequate = power is not None and power >= self.POWER_THRESHOLD
        if power is None:
            gaps.append("Power not reported")
            recommendations.append("Report statistical power")
        elif not power_adequate:
            gaps.append(f"Underpowered ({power:.2f})")
            recommendations.append("Increase sample size for 80% power")
        
        # Corrections
        corrections_applied = data.get("correction_applied", False)
        if data.get("comparisons", 1) > 1 and not corrections_applied:
            gaps.append("Multiple comparisons without correction")
            recommendations.append("Apply Bonferroni/FDR correction")
        
        # Confidence interval
        ci_present = ci is not None
        if not ci_present:
            gaps.append("Confidence interval not reported")
            recommendations.append("Report 95% CI for effect sizes")
        
        valid = len(gaps) == 0 or (len(gaps) <= 1 and is_significant)
        
        return StatisticalResult(
            valid=valid,
            effect_strength=effect_strength,
            power_adequate=power_adequate,
            corrections_applied=corrections_applied or data.get("comparisons", 1) == 1,
            confidence_interval_present=ci_present,
            recommendations=recommendations,
            gaps=gaps,
        )
