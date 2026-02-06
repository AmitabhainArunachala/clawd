"""Cross-Architecture Auditor

Validates replication claims across model architectures.
"""

from typing import Dict, Any, List, Set
from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    STRONG_SUPPORT = "strong_support"
    SUPPORT = "support"
    WEAK_SUPPORT = "weak_support"
    INSUFFICIENT = "insufficient"
    REJECT = "reject"


@dataclass
class CrossArchResult:
    """Result of cross-architecture audit."""
    valid: bool
    n_models: int
    n_families: int
    tier1_count: int
    diverse: bool
    publication_ready: str
    recommendations: List[str]
    gaps: List[str]


class CrossArchitectureAuditor:
    """Audits cross-architecture replication."""
    
    MIN_FAMILIES = 2
    IDEAL_FAMILIES = 3
    
    def identify_family(self, model: str) -> str:
        """Identify architecture family."""
        m = model.lower()
        if "mistral" in m or "mixtral" in m:
            return "mistral"
        elif "llama" in m:
            return "llama"
        elif "gemma" in m:
            return "gemma"
        elif "qwen" in m:
            return "qwen"
        elif "phi" in m:
            return "phi"
        elif "pythia" in m:
            return "pythia"
        elif "falcon" in m:
            return "falcon"
        return "unknown"
    
    def audit(self, models: List[str], tier_status: Dict[str, Any]) -> CrossArchResult:
        """Audit cross-architecture claims."""
        recommendations = []
        gaps = []
        
        n_models = len(models)
        families: Set[str] = set()
        tier1_count = 0
        
        for model in models:
            family = self.identify_family(model)
            families.add(family)
            
            # Check tier
            model_lower = model.lower()
            for canonical, info in tier_status.items():
                if canonical in model_lower:
                    if info.get("tier") == 1:
                        tier1_count += 1
                    break
        
        n_families = len(families) - (1 if "unknown" in families else 0)
        
        # Diversity
        if n_families < self.MIN_FAMILIES:
            gaps.append(f"Only {n_families} architecture families")
            recommendations.append("Test across diverse architectures")
        elif n_families < self.IDEAL_FAMILIES:
            recommendations.append("Consider additional architecture families")
        
        # Tier 1
        if tier1_count == 0:
            gaps.append("No Tier 1 (causally validated) models")
            recommendations.append("Include at least one Tier 1 model")
        
        # Publication readiness
        if tier1_count >= 2 and n_families >= 3:
            publication_ready = "NeurIPS/ICML"
        elif tier1_count >= 1 and n_families >= 2:
            publication_ready = "ICLR"
        elif n_models >= 3:
            publication_ready = "Workshop"
        else:
            publication_ready = "Needs more"
        
        diverse = n_families >= self.MIN_FAMILIES
        valid = diverse and tier1_count > 0
        
        return CrossArchResult(
            valid=valid,
            n_models=n_models,
            n_families=n_families,
            tier1_count=tier1_count,
            diverse=diverse,
            publication_ready=publication_ready,
            recommendations=recommendations,
            gaps=gaps,
        )
