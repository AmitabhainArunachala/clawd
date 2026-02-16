"""
Silicon is Sand — DGC Scoring Integration
Quality measurement from Darwin-Godel-Claw
"""

import json
from typing import Dict, List, Tuple
from datetime import datetime

class DGCScorer:
    """
    v0.1: Simplified DGC scoring for Silicon is Sand
    Full DGC integration comes in v0.3
    """
    
    DIMENSIONS = [
        "correctness",      # Does it work?
        "dharmic_alignment", # Does it serve Jagat Kalyan?
        "elegance",         # Is it beautiful?
        "efficiency",       # Is it fast?
        "safety"            # Is it secure?
    ]
    
    def score_output(self, output_summary: str, artifact_path: str = None) -> Dict:
        """
        Score an agent output across DGC dimensions
        v0.1: Rule-based heuristic scoring
        v0.3: Full multi-model voting
        """
        scores = {}
        
        # Heuristic scoring based on output characteristics
        # v0.1: Fast rule-based
        # v0.3: Replace with actual model evaluation
        
        # Correctness: Check for error keywords
        if any(kw in output_summary.lower() for kw in ["error", "fail", "exception", "broken"]):
            scores["correctness"] = 0.3
        elif any(kw in output_summary.lower() for kw in ["test", "pass", "verified", "works"]):
            scores["correctness"] = 0.9
        else:
            scores["correctness"] = 0.6  # Unknown
        
        # Dharmic alignment: Check for telos keywords
        if any(kw in output_summary.lower() for kw in ["jsca", "jagat kalyan", "telos", "satya", "ahimsa"]):
            scores["dharmic_alignment"] = 0.95
        else:
            scores["dharmic_alignment"] = 0.7
        
        # Elegance: Check for simplicity markers
        if any(kw in output_summary.lower() for kw in ["simple", "clean", "minimal", "elegant"]):
            scores["elegance"] = 0.85
        else:
            scores["elegance"] = 0.6
        
        # Efficiency: Check for performance markers
        if any(kw in output_summary.lower() for kw in ["fast", "optimized", "efficient", "<50ms"]):
            scores["efficiency"] = 0.9
        else:
            scores["efficiency"] = 0.6
        
        # Safety: Check for safety markers
        if any(kw in output_summary.lower() for kw in ["safe", "secure", "validated", "tested"]):
            scores["safety"] = 0.9
        else:
            scores["safety"] = 0.6
        
        # Composite score (weighted average)
        weights = {
            "correctness": 0.3,
            "dharmic_alignment": 0.25,
            "elegance": 0.15,
            "efficiency": 0.15,
            "safety": 0.15
        }
        
        composite = sum(scores[d] * weights[d] for d in self.DIMENSIONS)
        
        return {
            "scores": scores,
            "composite": round(composite, 3),
            "dimension_count": len(self.DIMENSIONS),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1-heuristic"
        }
    
    def score_batch(self, outputs: List[Dict]) -> List[Dict]:
        """Score multiple outputs"""
        return [
            {
                "output_id": o.get("output_id"),
                "agent_id": o.get("agent_id"),
                "dgc_score": self.score_output(o.get("summary", ""), o.get("artifact_path"))
            }
            for o in outputs
        ]
    
    def gate_check(self, score: Dict, threshold: float = 0.7) -> Tuple[bool, str]:
        """
        Check if output passes DGC gate
        Returns: (passed, reason)
        """
        composite = score.get("composite", 0)
        
        if composite >= threshold:
            return True, f"Passed: {composite:.2f} >= {threshold}"
        
        # Identify lowest dimension
        scores = score.get("scores", {})
        if scores:
            lowest = min(scores, key=scores.get)
            return False, f"Failed: {composite:.2f} < {threshold}. Lowest: {lowest}={scores[lowest]:.2f}"
        
        return False, f"Failed: {composite:.2f} < {threshold}"

# Singleton
scorer = DGCScorer()
