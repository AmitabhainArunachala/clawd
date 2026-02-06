"""
MI Auditor - Mechanistic Interpretability Claim Auditor

A tool for auditing claims in mechanistic interpretability research,
enforcing rigorous standards for causal validity, statistical rigor,
and cross-architecture validation.

Usage:
    from mi_auditor import MIAuditor
    
    auditor = MIAuditor()
    
    # Audit a statistical claim
    verdict = auditor.audit_statistical(
        claim="R_V effect size is large",
        data={"cohens_d": -3.56, "n": 45, "p_value": 1e-6}
    )
    
    # Audit causal validity
    verdict = auditor.audit_causal(experiment_results)
    
    # Audit cross-architecture claims
    verdict = auditor.audit_cross_arch(models_tested)
    
    # Position claim in literature
    comparison = auditor.position_in_literature(claim)
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import sys
from pathlib import Path

from .knowledge_base import MIKnowledgeBase, PaperCategory
from .report_generator import AuditReport, ReportGenerator, Verdict
from .auditors.statistical_rigor import StatisticalAuditor
from .auditors.causal_validity import CausalAuditor
from .auditors.cross_architecture import CrossArchitectureAuditor
from .auditors.literature_positioning import LiteraturePositioner


class AuditType(Enum):
    STATISTICAL = "statistical"
    CAUSAL = "causal"
    CROSS_ARCH = "cross_arch"
    LITERATURE = "literature"


@dataclass
class AuditResult:
    """Result of an audit."""
    claim: str
    audit_type: AuditType
    verdict: Verdict
    confidence: float  # 0-1
    evidence: Dict[str, Any]
    gaps: List[str]
    recommendations: List[str]
    report: AuditReport = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "audit_type": self.audit_type.value,
            "verdict": self.verdict.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "gaps": self.gaps,
            "recommendations": self.recommendations,
        }
    
    def __str__(self) -> str:
        lines = [
            f"╔═══════════════════════════════════════════════════════════════╗",
            f"║  MI AUDIT RESULT                                              ║",
            f"╠═══════════════════════════════════════════════════════════════╣",
            f"║  CLAIM: {self.claim[:56]:<56} ║",
            f"║  TYPE:  {self.audit_type.value:<56} ║",
            f"║  VERDICT: {self.verdict.value.upper():<54} ║",
            f"║  CONFIDENCE: {self.confidence*100:.1f}%{' ':<51} ║",
            f"╚═══════════════════════════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


class MIAuditor:
    """
    Main auditor class for evaluating mechanistic interpretability claims.
    
    Combines statistical rigor, causal validation, cross-architecture
    replication standards, and literature positioning.
    """
    
    # Tier definitions from ARCHITECTURE_STATUS_CORRECTED.md
    TIER_1_IRONCLAD = ["mistral-7b", "gemma-2-9b", "pythia-2.8b"]
    TIER_2_DISCOVERY = ["mixtral-8x7b", "llama-3-8b", "qwen-7b", "phi-3"]
    TIER_3_PROBLEMATIC = ["gemma-7b-it", "falcon-7b", "stablelm-3b"]
    
    # Statistical thresholds
    COHENS_D_LARGE = 0.8
    COHENS_D_HUGE = 2.0
    P_VALUE_THRESHOLD = 0.05
    POWER_THRESHOLD = 0.8
    
    def __init__(self, load_kb: bool = True):
        """Initialize the auditor with optional knowledge base."""
        self.statistical_auditor = StatisticalAuditor()
        self.causal_auditor = CausalAuditor()
        self.cross_arch_auditor = CrossArchitectureAuditor()
        self.literature_positioner = LiteraturePositioner()
        self.report_generator = ReportGenerator()
        
        self.kb: Optional[MIKnowledgeBase] = None
        if load_kb:
            try:
                self.kb = MIKnowledgeBase()
            except Exception as e:
                print(f"Warning: Could not load knowledge base: {e}")
        
        # Model status from corrected architecture status
        self.model_status = {
            # Tier 1: Causally validated
            "mistral-7b": {
                "tier": 1,
                "status": "ironclad",
                "cohens_d": -3.56,
                "p_value": "<10^-6",
                "transfer": "117.8%",
                "controls_passed": 4,
            },
            "gemma-2-9b": {
                "tier": 1,
                "status": "ironclad",
                "cohens_d": -2.09,
                "p_value": "<10^-23",
                "transfer": "99.5%",
                "controls_passed": 4,
            },
            "pythia-2.8b": {
                "tier": 1,
                "status": "circuit_mapped",
                "cohens_d": -4.51,
                "p_value": "<10^-40",
                "transfer": None,
                "controls_passed": 4,
            },
            # Tier 2: Discovery complete, needs causal validation
            "mixtral-8x7b": {
                "tier": 2,
                "status": "discovery",
                "effect_size": "24.3%",
                "effect": "strongest",
                "next_step": "4-control patching",
            },
            "llama-3-8b": {
                "tier": 2,
                "status": "discovery",
                "effect_size": "11.7%",
                "next_step": "7-phase protocol",
            },
            "qwen-7b": {
                "tier": 2,
                "status": "discovery",
                "effect_size": "9.2%",
                "next_step": "causal validation",
            },
            "phi-3": {
                "tier": 2,
                "status": "discovery",
                "effect_size": "6.9%",
                "next_step": "causal validation",
            },
            # Tier 3: Problematic
            "gemma-7b-it": {
                "tier": 3,
                "status": "problematic",
                "issue": "SVD singularities on math prompts",
                "fix": "Use bfloat16, filter math prompts",
            },
            "falcon-7b": {
                "tier": 3,
                "status": "infrastructure_error",
                "issue": "No space left on device",
            },
            "stablelm-3b": {
                "tier": 3,
                "status": "not_attempted",
            },
        }
    
    def audit_statistical(self, claim: str, data: Dict[str, Any]) -> AuditResult:
        """
        Audit a statistical claim for rigor.
        
        Args:
            claim: The statistical claim being made
            data: Dictionary with statistical measures
                - n: sample size
                - cohens_d: effect size
                - p_value: significance
                - confidence_interval: (lower, upper)
                - power: statistical power
                
        Returns:
            AuditResult with verdict and recommendations
        """
        evidence = {"input_data": data}
        gaps = []
        recommendations = []
        
        # Check for required fields
        n = data.get("n", 0)
        cohens_d = data.get("cohens_d", 0)
        p_value = data.get("p_value", 1.0)
        power = data.get("power", None)
        ci = data.get("confidence_interval", None)
        
        # Sample size assessment
        if n < 30:
            gaps.append(f"Small sample size (n={n})")
            recommendations.append("Increase sample size to at least n=30 for CLT")
        elif n < 100:
            recommendations.append(f"Sample size n={n} is adequate but larger samples improve power")
        
        # Effect size assessment
        effect_strength = "negligible"
        if abs(cohens_d) >= self.COHENS_D_HUGE:
            effect_strength = "huge"
        elif abs(cohens_d) >= self.COHENS_D_LARGE:
            effect_strength = "large"
        elif abs(cohens_d) >= 0.5:
            effect_strength = "medium"
        elif abs(cohens_d) >= 0.2:
            effect_strength = "small"
        
        evidence["effect_strength"] = effect_strength
        
        # Statistical significance
        is_significant = p_value < self.P_VALUE_THRESHOLD
        evidence["is_significant"] = is_significant
        
        if not is_significant:
            gaps.append(f"Not statistically significant (p={p_value})")
            recommendations.append("Collect more data or reduce noise")
        
        # Multiple comparisons check
        if "comparisons" in data:
            comparisons = data["comparisons"]
            if comparisons > 1 and not data.get("correction_applied"):
                gaps.append(f"Multiple comparisons ({comparisons}) without correction")
                recommendations.append("Apply Bonferroni or FDR correction")
        
        # Power analysis
        if power is not None and power < self.POWER_THRESHOLD:
            gaps.append(f"Underpowered study (power={power:.2f})")
            recommendations.append(f"Increase sample size to achieve 80% power")
        elif power is None:
            gaps.append("Power analysis not reported")
            recommendations.append("Report statistical power or conduct power analysis")
        
        # Confidence interval
        if ci is None:
            gaps.append("Confidence interval not reported")
            recommendations.append("Report 95% confidence intervals for effect sizes")
        
        # Determine verdict
        if len(gaps) == 0 and abs(cohens_d) >= self.COHENS_D_LARGE:
            verdict = Verdict.STRONG_SUPPORT
            confidence = 0.9
        elif len(gaps) <= 1 and is_significant:
            verdict = Verdict.SUPPORT
            confidence = 0.7
        elif is_significant:
            verdict = Verdict.WEAK_SUPPORT
            confidence = 0.5
        elif n >= 30:
            verdict = Verdict.INSUFFICIENT
            confidence = 0.3
        else:
            verdict = Verdict.REJECT
            confidence = 0.1
        
        report = self.report_generator.generate(
            claim=claim,
            verdict=verdict,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            confidence=confidence,
        )
        
        return AuditResult(
            claim=claim,
            audit_type=AuditType.STATISTICAL,
            verdict=verdict,
            confidence=confidence,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            report=report,
        )
    
    def audit_causal(self, experiment_results: Dict[str, Any]) -> AuditResult:
        """
        Audit causal validity of an experiment.
        
        Args:
            experiment_results: Dictionary with experimental data
                - model: model name
                - n_controls: number of control experiments
                - control_results: list of control outcomes
                - intervention_result: main intervention outcome
                - baseline: baseline measurement
                
        Returns:
            AuditResult with causal validity assessment
        """
        claim = experiment_results.get("claim", "Causal claim")
        evidence = {"experiment": experiment_results}
        gaps = []
        recommendations = []
        
        # Check for 4-control standard
        n_controls = experiment_results.get("n_controls", 0)
        control_results = experiment_results.get("control_results", [])
        intervention = experiment_results.get("intervention_result", {})
        
        # Required controls for activation patching
        required_controls = [
            "source_run",
            "target_run", 
            "patched_run",
            "metric_validation"
        ]
        
        if n_controls < 4:
            gaps.append(f"Only {n_controls}/4 required controls performed")
            recommendations.append("Implement all 4 controls for activation patching:")
            for ctrl in required_controls[:4-n_controls]:
                recommendations.append(f"  - {ctrl}")
        
        # Check control consistency
        if control_results:
            consistent = all(
                r.get("direction") == control_results[0].get("direction")
                for r in control_results
            )
            if not consistent:
                gaps.append("Control results show inconsistent directions")
                recommendations.append("Investigate control inconsistencies before claiming causality")
        
        # Check for baseline
        baseline = experiment_results.get("baseline")
        if baseline is None:
            gaps.append("No baseline measurement")
            recommendations.append("Include baseline measurement for comparison")
        
        # Check for statistical validation
        cohens_d = intervention.get("cohens_d")
        if cohens_d is None:
            gaps.append("No effect size (Cohen's d) reported")
            recommendations.append("Calculate and report Cohen's d for intervention")
        elif abs(cohens_d) < 0.8:
            gaps.append(f"Small effect size (d={cohens_d:.2f})")
            recommendations.append("Effect size should be large (d>0.8) for causal claims")
        
        # Check for transfer efficiency
        transfer = intervention.get("transfer_efficiency")
        if transfer is None:
            gaps.append("Transfer efficiency not measured")
            recommendations.append("Measure transfer efficiency to validate circuit completeness")
        
        # Determine verdict
        if n_controls >= 4 and len(gaps) == 0:
            verdict = Verdict.STRONG_SUPPORT
            confidence = 0.95
        elif n_controls >= 4 and len(gaps) <= 2:
            verdict = Verdict.SUPPORT
            confidence = 0.75
        elif n_controls >= 2:
            verdict = Verdict.WEAK_SUPPORT
            confidence = 0.5
        else:
            verdict = Verdict.INSUFFICIENT
            confidence = 0.2
        
        report = self.report_generator.generate(
            claim=claim,
            verdict=verdict,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            confidence=confidence,
        )
        
        return AuditResult(
            claim=claim,
            audit_type=AuditType.CAUSAL,
            verdict=verdict,
            confidence=confidence,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            report=report,
        )
    
    def audit_cross_arch(self, models_tested: List[str]) -> AuditResult:
        """
        Audit cross-architecture replication claims.
        
        Args:
            models_tested: List of model names that were tested
            
        Returns:
            AuditResult with cross-architecture assessment
        """
        claim = f"Cross-architecture replication across {len(models_tested)} models"
        evidence = {"models_tested": models_tested}
        gaps = []
        recommendations = []
        
        # Count by tier
        tier_counts = {1: 0, 2: 0, 3: 0}
        arch_families = set()
        
        for model in models_tested:
            model_lower = model.lower()
            found = False
            
            for canonical, info in self.model_status.items():
                if canonical in model_lower or model_lower in canonical:
                    tier_counts[info["tier"]] += 1
                    found = True
                    
                    # Identify architecture family
                    if "mistral" in model_lower or "mixtral" in model_lower:
                        arch_families.add("mistral-family")
                    elif "llama" in model_lower:
                        arch_families.add("llama-family")
                    elif "gemma" in model_lower:
                        arch_families.add("gemma-family")
                    elif "qwen" in model_lower:
                        arch_families.add("qwen")
                    elif "phi" in model_lower:
                        arch_families.add("phi")
                    elif "pythia" in model_lower:
                        arch_families.add("pythia")
                    elif "falcon" in model_lower:
                        arch_families.add("falcon")
                    break
            
            if not found:
                gaps.append(f"Unknown model: {model}")
        
        evidence["tier_distribution"] = tier_counts
        evidence["architecture_families"] = list(arch_families)
        
        # Check for diverse architectures
        if len(arch_families) < 2:
            gaps.append("Only 1 architecture family tested")
            recommendations.append("Test across diverse architectures (Mistral, Llama, Gemma, etc.)")
        elif len(arch_families) < 3:
            recommendations.append("Consider testing additional architecture families")
        
        # Check for ironclad models
        if tier_counts[1] == 0:
            gaps.append("No Tier 1 (causally validated) models")
            recommendations.append("Include at least one Tier 1 model for strong claims")
        
        # Check for heterogeneity analysis
        if "heterogeneity" not in str(models_tested).lower():
            recommendations.append("Report I² statistic for heterogeneity across architectures")
        
        # Publication readiness
        if tier_counts[1] >= 2 and len(arch_families) >= 3:
            publication_tier = "NeurIPS/ICML ready"
            verdict = Verdict.STRONG_SUPPORT
            confidence = 0.85
        elif tier_counts[1] >= 1 and len(arch_families) >= 2:
            publication_tier = "ICLR ready"
            verdict = Verdict.SUPPORT
            confidence = 0.7
        elif len(models_tested) >= 3:
            publication_tier = "Workshop ready"
            verdict = Verdict.WEAK_SUPPORT
            confidence = 0.5
        else:
            publication_tier = "Needs more replication"
            verdict = Verdict.INSUFFICIENT
            confidence = 0.3
        
        evidence["publication_readiness"] = publication_tier
        
        report = self.report_generator.generate(
            claim=claim,
            verdict=verdict,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            confidence=confidence,
        )
        
        return AuditResult(
            claim=claim,
            audit_type=AuditType.CROSS_ARCH,
            verdict=verdict,
            confidence=confidence,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            report=report,
        )
    
    def position_in_literature(self, claim: str) -> Dict[str, Any]:
        """
        Position a claim relative to SOTA literature.
        
        Args:
            claim: The claim to position
            
        Returns:
            Dictionary with literature comparison
        """
        result = {
            "claim": claim,
            "supporting_papers": [],
            "contradicting_papers": [],
            "methodology_references": [],
            "novelty": None,
            "related_work": [],
        }
        
        claim_lower = claim.lower()
        
        # Check knowledge base if available
        if self.kb:
            citations = self.kb.cite_for_claim(claim)
            result["supporting_papers"] = citations.get("supporting", [])
            result["contradicting_papers"] = citations.get("contradicting", [])
            result["methodology_references"] = citations.get("methodology", [])
        
        # Keywords analysis
        keywords = {
            "attention": ["attention_is_all_you_need", "transformer_circuits"],
            "induction": ["induction_heads"],
            "superposition": ["toy_superposition"],
            "sae": ["monosemanticity", "scaling_monosemanticity"],
            "emergence": ["emergent_abilities", "emergence_mirage"],
            "causal": ["induction_heads"],
            "circuit": ["transformer_circuits", "induction_heads"],
            "scaling": ["scaling_laws", "chinchilla"],
            "consciousness": ["consciousness_in_ai"],
            "truth": ["geometry_of_truth"],
            "steering": ["representation_engineering"],
        }
        
        for keyword, papers in keywords.items():
            if keyword in claim_lower:
                result["related_work"].extend(papers)
        
        # Novelty assessment
        if result["contradicting_papers"]:
            result["novelty"] = "controversial"
        elif len(result["related_work"]) == 0:
            result["novelty"] = "potentially_novel"
        elif len(result["related_work"]) > 3:
            result["novelty"] = "well_established"
        else:
            result["novelty"] = "incremental"
        
        # SOTA comparison for specific claims
        if "r_v" in claim_lower or "participation ratio" in claim_lower:
            result["sota_comparison"] = {
                "our_work": "R_V contraction measurement",
                "comparable_to": [
                    "Marks & Tegmark (2023) - linear structure in representations",
                    "Elhage et al. (2021) - transformer circuits",
                ],
                "advancement": "Geometric analysis of value matrix space",
            }
        
        return result
    
    def tier_status(self, model_name: str) -> Dict[str, Any]:
        """
        Get the validation tier status of a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with tier information
        """
        model_lower = model_name.lower()
        
        for canonical, info in self.model_status.items():
            if canonical in model_lower or model_lower in canonical:
                return {
                    "model": model_name,
                    "canonical_name": canonical,
                    **info,
                }
        
        return {
            "model": model_name,
            "status": "unknown",
            "message": "Model not in validation database",
        }
    
    def full_audit(self, claim: str, context: Dict[str, Any]) -> List[AuditResult]:
        """
        Run a full audit across all dimensions.
        
        Args:
            claim: The claim to audit
            context: Dictionary with all relevant data
            
        Returns:
            List of AuditResult objects
        """
        results = []
        
        # Statistical audit
        if "statistical_data" in context:
            results.append(self.audit_statistical(claim, context["statistical_data"]))
        
        # Causal audit
        if "experiment_results" in context:
            results.append(self.audit_causal(context["experiment_results"]))
        
        # Cross-arch audit
        if "models_tested" in context:
            results.append(self.audit_cross_arch(context["models_tested"]))
        
        return results
    
    def generate_report(self, results: List[AuditResult], format: str = "markdown") -> str:
        """
        Generate a consolidated audit report.
        
        Args:
            results: List of AuditResult objects
            format: Output format ("markdown", "json", "text")
            
        Returns:
            Formatted report string
        """
        if format == "json":
            return json.dumps([r.to_dict() for r in results], indent=2)
        
        elif format == "text":
            lines = []
            for r in results:
                lines.append(str(r))
                lines.append("")
            return "\n".join(lines)
        
        else:  # markdown
            lines = ["# MI Audit Report\n"]
            
            for i, r in enumerate(results, 1):
                lines.append(f"## Audit {i}: {r.audit_type.value.title()}\n")
                lines.append(f"**Claim:** {r.claim}\n")
                lines.append(f"**Verdict:** {r.verdict.value.upper()}\n")
                lines.append(f"**Confidence:** {r.confidence*100:.1f}%\n")
                
                if r.gaps:
                    lines.append("\n### Gaps Identified\n")
                    for gap in r.gaps:
                        lines.append(f"- ⚠️ {gap}")
                    lines.append("")
                
                if r.recommendations:
                    lines.append("\n### Recommendations\n")
                    for rec in r.recommendations:
                        lines.append(f"- 💡 {rec}")
                    lines.append("")
                
                lines.append("---\n")
            
            return "\n".join(lines)


# Convenience functions for direct use
def audit_statistical(claim: str, data: Dict[str, Any]) -> AuditResult:
    """Standalone statistical audit."""
    return MIAuditor().audit_statistical(claim, data)


def audit_causal(experiment_results: Dict[str, Any]) -> AuditResult:
    """Standalone causal audit."""
    return MIAuditor().audit_causal(experiment_results)


def audit_cross_arch(models_tested: List[str]) -> AuditResult:
    """Standalone cross-architecture audit."""
    return MIAuditor().audit_cross_arch(models_tested)


def position_in_literature(claim: str) -> Dict[str, Any]:
    """Standalone literature positioning."""
    return MIAuditor().position_in_literature(claim)


__all__ = [
    "MIAuditor",
    "AuditResult",
    "AuditType",
    "Verdict",
    "audit_statistical",
    "audit_causal",
    "audit_cross_arch",
    "position_in_literature",
    "MIKnowledgeBase",
    "AuditReport",
]
