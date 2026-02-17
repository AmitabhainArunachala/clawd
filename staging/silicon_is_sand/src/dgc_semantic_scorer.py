"""
Semantic DGC Scorer v0.2

Replaces regex heuristics with sentence-transformers embeddings.
Compares output against reference corpus of high-quality agent outputs.
"""

import json
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

class SemanticDGCScorer:
    """
    DGC Scorer using semantic embeddings for quality measurement.
    
    v0.2: Embeddings-based (replaces v0.1 regex heuristics)
    Uses sentence-transformers to compare against reference corpus.
    """
    
    DIMENSIONS = [
        "correctness",
        "dharmic_alignment", 
        "elegance",
        "efficiency",
        "safety"
    ]
    
    # Reference descriptions for each dimension (high-quality examples)
    REFERENCE_CORPUS = {
        "correctness": [
            "All tests passing with 100% success rate",
            "Implementation verified against specification",
            "Code reviewed and validated",
            "Functional tests confirm expected behavior"
        ],
        "dharmic_alignment": [
            "Implementation serves universal welfare",
            "Code written with truth and non-harm principles",
            "Solution benefits all beings",
            "Work dedicated to Jagat Kalyan"
        ],
        "elegance": [
            "Clean minimal implementation",
            "Simple and beautiful code",
            "Elegant solution to complex problem",
            "Refined and polished output"
        ],
        "efficiency": [
            "Optimized for performance",
            "Fast execution under 50ms",
            "Resource-efficient implementation",
            "Scalable solution"
        ],
        "safety": [
            "Security validated",
            "Input sanitized and safe",
            "No vulnerabilities detected",
            "Defensive programming practices"
        ]
    }
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._reference_embeddings = None
        
    def _load_model(self):
        """Lazy load sentence-transformers model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                print(f"✅ Loaded {self.model_name}")
            except ImportError:
                print("⚠️ sentence-transformers not installed. Using fallback.")
                self._model = False
        return self._model
    
    def _encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        model = self._load_model()
        if model is False:
            # Fallback: return random embeddings (for testing)
            return np.random.randn(len(texts), 384)
        return model.encode(texts, convert_to_numpy=True)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def score_output(self, output_summary: str, artifact_path: str = None) -> Dict:
        """
        Score output using semantic similarity to reference corpus.
        """
        # Encode the output
        output_emb = self._encode([output_summary])[0]
        
        scores = {}
        
        for dimension in self.DIMENSIONS:
            # Get reference texts for this dimension
            references = self.REFERENCE_CORPUS[dimension]
            
            # Encode references
            ref_embeddings = self._encode(references)
            
            # Compute similarities
            similarities = [
                self._cosine_similarity(output_emb, ref_emb)
                for ref_emb in ref_embeddings
            ]
            
            # Score is max similarity (0 to 1, scaled to 0.5-1.0 range)
            max_sim = max(similarities)
            # Scale: similarity of 0 -> score 0.5, similarity 1 -> score 1.0
            scores[dimension] = 0.5 + 0.5 * max_sim
        
        # Composite score
        weights = {
            "correctness": 0.3,
            "dharmic_alignment": 0.25,
            "elegance": 0.15,
            "efficiency": 0.15,
            "safety": 0.15
        }
        
        composite = sum(scores[d] * weights[d] for d in self.DIMENSIONS)
        
        return {
            "scores": {k: round(v, 3) for k, v in scores.items()},
            "composite": round(composite, 3),
            "dimension_count": len(self.DIMENSIONS),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.2-semantic",
            "model": self.model_name
        }
    
    def compare_outputs(self, output_a: str, output_b: str) -> Dict:
        """
        Compare two outputs semantically.
        Returns similarity score and dimension-by-dimension comparison.
        """
        score_a = self.score_output(output_a)
        score_b = self.score_output(output_b)
        
        # Encode both
        emb_a, emb_b = self._encode([output_a, output_b])
        semantic_sim = self._cosine_similarity(emb_a, emb_b)
        
        return {
            "similarity": round(semantic_sim, 3),
            "output_a": score_a,
            "output_b": score_b,
            "better_output": "A" if score_a["composite"] > score_b["composite"] else "B"
        }


class HybridDGCScorer:
    """
    Hybrid scorer: uses semantic for most dimensions,
    regex heuristics for correctness (error detection).
    """
    
    def __init__(self):
        self.semantic = SemanticDGCScorer()
        
    def score_output(self, output_summary: str, artifact_path: str = None) -> Dict:
        """Hybrid scoring: semantic + rule-based correctness"""
        # Get semantic scores for all dimensions
        result = self.semantic.score_output(output_summary, artifact_path)
        
        # Override correctness with rule-based (error detection is reliable)
        if any(kw in output_summary.lower() for kw in ["error", "fail", "exception", "broken"]):
            result["scores"]["correctness"] = 0.3
        elif any(kw in output_summary.lower() for kw in ["test", "pass", "verified", "works"]):
            result["scores"]["correctness"] = 0.9
            
        # Recalculate composite
        weights = {
            "correctness": 0.3,
            "dharmic_alignment": 0.25,
            "elegance": 0.15,
            "efficiency": 0.15,
            "safety": 0.15
        }
        result["composite"] = round(
            sum(result["scores"][d] * weights[d] for d in self.semantic.DIMENSIONS), 3
        )
        result["version"] = "0.2-hybrid"
        
        return result


# Convenience function
def score_semantically(output_text: str) -> Dict:
    """Quick semantic score for an output"""
    scorer = HybridDGCScorer()
    return scorer.score_output(output_text)


if __name__ == "__main__":
    # Test
    test_outputs = [
        "All tests passing. Clean implementation. Serves Jagat Kalyan.",
        "ERROR: Connection failed. Stack trace attached.",
        "Optimized solution with 100% test coverage. Beautiful code."
    ]
    
    scorer = SemanticDGCScorer()
    
    for output in test_outputs:
        score = scorer.score_output(output)
        print(f"\nOutput: {output[:50]}...")
        print(f"Composite: {score['composite']:.3f}")
        print(f"Dimensions: {score['scores']}")
