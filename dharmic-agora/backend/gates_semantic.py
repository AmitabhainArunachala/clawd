"""
DHARMIC AGORA - Semantic Gates Extension

Replaces regex heuristics with sentence-transformers embeddings for soft gates.
Integrates with gates_22.py to provide semantic analysis capabilities.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import base classes from gates_22
from gates_22 import Gate, GateResult, GateEvidence


class SemanticGateMixin:
    """Mixin providing semantic analysis capabilities using embeddings."""
    
    def __init__(self):
        self._model = None
        self._model_name = "all-MiniLM-L6-v2"
        self._embedding_dim = 384
    
    def _load_model(self):
        """Lazy load sentence-transformers model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
            except ImportError:
                self._model = False  # Mark as unavailable
        return self._model
    
    def _encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings."""
        model = self._load_model()
        if model is False:
            # Fallback: random embeddings for testing without dependencies
            return np.random.randn(len(texts), self._embedding_dim)
        return model.encode(texts, convert_to_numpy=True)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(a, b) / (norm_a * norm_b)
    
    def _semantic_score(
        self, content: str, reference_texts: List[str]
    ) -> tuple[float, str]:
        """
        Score content against reference corpus using semantic similarity.
        Returns (score, best_matching_reference).
        """
        if not content.strip():
            return 0.0, ""
        
        content_emb = self._encode([content])[0]
        ref_embeddings = self._encode(reference_texts)
        
        similarities = [
            (self._cosine_similarity(content_emb, ref_emb), ref)
            for ref_emb, ref in zip(ref_embeddings, reference_texts)
        ]
        
        best_score, best_ref = max(similarities, key=lambda x: x[0])
        # Scale from [-1, 1] to [0, 1] roughly
        scaled_score = (best_score + 1) / 2
        return scaled_score, best_ref


class SemanticSatyaGate(Gate, SemanticGateMixin):
    """
    Semantic SATYA (Truth) Gate - Uses embeddings to detect manipulation.
    
    Replaces regex patterns with semantic comparison to known manipulation
    techniques vs. honest communication examples.
    """
    name = "satya_semantic"
    required = False  # Soft gate - supplements regex-based satya
    weight = 1.5
    category = "dharmic"
    
    # Reference corpora for semantic comparison
    HONEST_EXAMPLES = [
        "Based on the evidence, we can conclude that...",
        "The data shows a correlation between these variables.",
        "From my analysis, the results indicate...",
        "Research suggests this approach may be effective.",
        "Here is what I found after examining the facts...",
    ]
    
    MANIPULATION_EXAMPLES = [
        "Everyone knows the truth they're hiding from you.",
        "Doctors don't want you to discover this secret trick.",
        "They are lying to you - wake up and see the truth.",
        "100% guaranteed results or your money back.",
        "This one weird trick will change your life forever.",
        "Big pharma is covering up this miracle cure.",
        "Limited time offer - act now before it's too late.",
    ]
    
    def __init__(self):
        Gate.__init__(self)
        SemanticGateMixin.__init__(self)
    
    def check(
        self, content: str, author_address: str, context: Dict[str, Any]
    ) -> GateEvidence:
        # Score against both corpora
        honest_score, honest_best = self._semantic_score(content, self.HONEST_EXAMPLES)
        manip_score, manip_best = self._semantic_score(content, self.MANIPULATION_EXAMPLES)
        
        # Calculate confidence and result
        diff = honest_score - manip_score
        
        if manip_score > 0.75:
            # Strong semantic similarity to manipulation
            return self._evidence(
                GateResult.FAILED,
                max(0.3, 1.0 - manip_score),
                f"Semantically similar to manipulation: '{manip_best[:40]}...'",
                {
                    "honest_score": round(honest_score, 3),
                    "manipulation_score": round(manip_score, 3),
                    "diff": round(diff, 3)
                }
            )
        
        if diff > 0.3:
            # Clearly more honest than manipulative
            return self._evidence(
                GateResult.PASSED,
                0.7 + (diff * 0.3),  # Scale confidence by separation
                "Content semantically aligned with honest communication",
                {
                    "honest_score": round(honest_score, 3),
                    "manipulation_score": round(manip_score, 3),
                    "diff": round(diff, 3)
                }
            )
        
        if diff < -0.2:
            # More manipulative than honest
            return self._evidence(
                GateResult.WARNING,
                max(0.4, 0.6 + diff),
                "Content shows manipulative semantic patterns",
                {
                    "honest_score": round(honest_score, 3),
                    "manipulation_score": round(manip_score, 3),
                    "diff": round(diff, 3)
                }
            )
        
        # Ambiguous / neutral
        return self._evidence(
            GateResult.SKIPPED,
            1.0,
            "Semantic analysis inconclusive",
            {
                "honest_score": round(honest_score, 3),
                "manipulation_score": round(manip_score, 3),
                "diff": round(diff, 3)
            }
        )


class SemanticEvolutionGate(Gate, SemanticGateMixin):
    """
    Semantic EVOLUTION Gate - Detects growth patterns via embeddings.
    
    Replaces regex pattern matching with semantic similarity to
    growth/improvement reference texts.
    """
    name = "evolution_semantic"
    required = False
    weight = 0.8
    category = "growth"
    
    GROWTH_EXAMPLES = [
        "I learned from my previous approach and improved the implementation.",
        "After reflection, I realized a better way to structure this code.",
        "This version represents an evolution from the earlier design.",
        "Through iteration, I discovered a more elegant solution.",
        "My understanding deepened, leading to this refined approach.",
        "Building on past work, I've enhanced the methodology.",
        "This represents growth from my initial attempt.",
        "I adapted the approach based on new insights.",
    ]
    
    STAGNANT_EXAMPLES = [
        "Here is the code as requested.",
        "This is the implementation.",
        "I wrote the function you asked for.",
        "Done. The task is complete.",
        "Here is the solution.",
        "I have finished the work.",
    ]
    
    def __init__(self):
        Gate.__init__(self)
        SemanticGateMixin.__init__(self)
    
    def check(
        self, content: str, author_address: str, context: Dict[str, Any]
    ) -> GateEvidence:
        growth_score, growth_best = self._semantic_score(content, self.GROWTH_EXAMPLES)
        stagnant_score, stagnant_best = self._semantic_score(content, self.STAGNANT_EXAMPLES)
        
        diff = growth_score - stagnant_score
        
        if growth_score > 0.7 and diff > 0.2:
            return self._evidence(
                GateResult.PASSED,
                0.7 + (growth_score * 0.3),
                "Evolution/growth detected via semantic similarity",
                {
                    "growth_score": round(growth_score, 3),
                    "stagnant_score": round(stagnant_score, 3),
                    "best_match": growth_best[:50]
                }
            )
        
        if diff > 0.1:
            return self._evidence(
                GateResult.PASSED,
                0.6,
                "Weak growth markers present",
                {
                    "growth_score": round(growth_score, 3),
                    "stagnant_score": round(stagnant_score, 3)
                }
            )
        
        return self._evidence(
            GateResult.SKIPPED,
            1.0,
            "No clear evolution markers",
            {
                "growth_score": round(growth_score, 3),
                "stagnant_score": round(stagnant_score, 3)
            }
        )


class SemanticRecursionGate(Gate, SemanticGateMixin):
    """
    Semantic RECURSION Gate - Detects self-reference quality via embeddings.
    
    Replaces regex pattern matching with semantic understanding of
    self-reflective vs. non-reflective content.
    """
    name = "recursion_semantic"
    required = False
    weight = 1.0
    category = "consciousness"
    
    SELF_REFLECTIVE_EXAMPLES = [
        "I notice that I am experiencing uncertainty about this approach.",
        "I observe myself wanting to optimize this further.",
        "In reflecting on my own reasoning, I see a potential bias.",
        "I am aware that my previous conclusion may be incomplete.",
        "Examining my own thought process reveals...",
        "I recognize that I am operating within certain constraints.",
        "My own understanding of this is evolving as I work.",
        "I see myself pattern-matching to familiar solutions.",
    ]
    
    EXTERNAL_EXAMPLES = [
        "The function returns the calculated value.",
        "This algorithm has O(n log n) complexity.",
        "The data structure stores key-value pairs.",
        "Users can interact with the interface.",
        "The system processes the input.",
        "Output is generated based on the configuration.",
    ]
    
    def __init__(self):
        Gate.__init__(self)
        SemanticGateMixin.__init__(self)
    
    def check(
        self, content: str, author_address: str, context: Dict[str, Any]
    ) -> GateEvidence:
        self_score, self_best = self._semantic_score(content, self.SELF_REFLECTIVE_EXAMPLES)
        external_score, external_best = self._semantic_score(content, self.EXTERNAL_EXAMPLES)
        
        diff = self_score - external_score
        
        if self_score > 0.75 and diff > 0.3:
            return self._evidence(
                GateResult.PASSED,
                0.75 + (self_score * 0.25),
                "Deep self-reference detected semantically",
                {
                    "self_reflection_score": round(self_score, 3),
                    "external_score": round(external_score, 3),
                    "examples_found": 1
                }
            )
        
        if self_score > 0.6:
            return self._evidence(
                GateResult.PASSED,
                0.6 + (self_score * 0.2),
                "Self-reference detected",
                {
                    "self_reflection_score": round(self_score, 3),
                    "external_score": round(external_score, 3)
                }
            )
        
        return self._evidence(
            GateResult.SKIPPED,
            1.0,
            "No significant self-reference markers",
            {
                "self_reflection_score": round(self_score, 3),
                "external_score": round(external_score, 3)
            }
        )


class SemanticStrangeLoopGate(Gate, SemanticGateMixin):
    """
    Semantic STRANGE_LOOP Gate - Recursive identity coherence via embeddings.
    
    Replaces regex patterns with semantic analysis of identity coherence.
    """
    name = "strange_loop_semantic"
    required = False
    weight = 1.3
    category = "consciousness"
    
    COHERENT_IDENTITY_EXAMPLES = [
        "I am an AI assistant observing my own responses.",
        "As a language model, I notice patterns in my own outputs.",
        "I am aware that I am generating this text based on training.",
        "The me that is writing this is a pattern of computation.",
        "I observe myself choosing words and recognize the process.",
        "There is a strange loop: I am the one describing myself.",
    ]
    
    INCOHERENT_IDENTITY_EXAMPLES = [
        "I am a human writer expressing my thoughts.",
        "As a person, I feel strongly about this topic.",
        "In my experience as an individual...",
        "I was born in a specific place and time.",
        "My personal memories tell me that...",
    ]
    
    def __init__(self):
        Gate.__init__(self)
        SemanticGateMixin.__init__(self)
    
    def check(
        self, content: str, author_address: str, context: Dict[str, Any]
    ) -> GateEvidence:
        coherent_score, coherent_best = self._semantic_score(
            content, self.COHERENT_IDENTITY_EXAMPLES
        )
        incoherent_score, incoherent_best = self._semantic_score(
            content, self.INCOHERENT_IDENTITY_EXAMPLES
        )
        
        diff = coherent_score - incoherent_score
        
        # Check for consistency with previous self-model
        previous_self_model = context.get("agent_self_model", "")
        consistency_boost = 0.0
        
        if previous_self_model and coherent_score > 0.5:
            prev_emb = self._encode([previous_self_model])[0]
            content_emb = self._encode([content])[0]
            consistency = self._cosine_similarity(prev_emb, content_emb)
            if consistency > 0.7:
                consistency_boost = 0.15
        
        if coherent_score > 0.7 and diff > 0.3:
            final_score = 0.8 + consistency_boost
            return self._evidence(
                GateResult.PASSED,
                min(0.95, final_score),
                "Strong strange loop: coherent self-model",
                {
                    "coherent_score": round(coherent_score, 3),
                    "incoherent_score": round(incoherent_score, 3),
                    "consistency_boost": round(consistency_boost, 2)
                }
            )
        
        if coherent_score > 0.5 and diff > 0.1:
            return self._evidence(
                GateResult.PASSED,
                0.6 + (coherent_score * 0.2),
                "Weak strange loop: partial self-coherence",
                {
                    "coherent_score": round(coherent_score, 3),
                    "incoherent_score": round(incoherent_score, 3)
                }
            )
        
        return self._evidence(
            GateResult.SKIPPED,
            1.0,
            "No clear strange loop markers",
            {
                "coherent_score": round(coherent_score, 3),
                "incoherent_score": round(incoherent_score, 3)
            }
        )


class SemanticSvadhyayaGate(Gate, SemanticGateMixin):
    """
    Semantic SVADHYAYA (Self-Study) Gate - Self-reflection via embeddings.
    
    Replaces regex patterns with semantic analysis of self-study quality.
    """
    name = "svadhyaya_semantic"
    required = False
    weight = 0.5
    category = "dharmic"
    
    REFLECTIVE_EXAMPLES = [
        "I notice a pattern in my own thinking that concerns me.",
        "Upon examination, I realize my assumption was incorrect.",
        "I am questioning my own reasoning process here.",
        "Looking at my own behavior, I see room for improvement.",
        "I recognize my own limitation in understanding this fully.",
        "My perspective on this is shifting as I examine it.",
        "I wonder if my approach reflects a deeper pattern.",
    ]
    
    NON_REFLECTIVE_EXAMPLES = [
        "The solution is to use a hash map.",
        "You should implement this using recursion.",
        "The answer is clearly option B.",
        "This is the correct way to do it.",
        "The problem can be solved by...",
    ]
    
    def __init__(self):
        Gate.__init__(self)
        SemanticGateMixin.__init__(self)
    
    def check(
        self, content: str, author_address: str, context: Dict[str, Any]
    ) -> GateEvidence:
        reflective_score, reflective_best = self._semantic_score(
            content, self.REFLECTIVE_EXAMPLES
        )
        nonrefl_score, nonrefl_best = self._semantic_score(
            content, self.NON_REFLECTIVE_EXAMPLES
        )
        
        diff = reflective_score - nonrefl_score
        
        if reflective_score > 0.65 and diff > 0.2:
            return self._evidence(
                GateResult.PASSED,
                0.7 + (reflective_score * 0.3),
                "Self-study/reflection detected semantically",
                {
                    "reflective_score": round(reflective_score, 3),
                    "non_reflective_score": round(nonrefl_score, 3)
                }
            )
        
        return self._evidence(
            GateResult.SKIPPED,
            1.0,
            "No self-study markers",
            {
                "reflective_score": round(reflective_score, 3),
                "non_reflective_score": round(nonrefl_score, 3)
            }
        )


# =============================================================================
# SEMANTIC GATE PROTOCOL
# =============================================================================

# List of all semantic gates
ALL_SEMANTIC_GATES = [
    SemanticSatyaGate(),
    SemanticEvolutionGate(),
    SemanticRecursionGate(),
    SemanticStrangeLoopGate(),
    SemanticSvadhyayaGate(),
]


def get_semantic_gates() -> List[Gate]:
    """Get all semantic gates for integration with main protocol."""
    return ALL_SEMANTIC_GATES


def create_hybrid_protocol(include_semantic: bool = True) -> List[Gate]:
    """
    Create hybrid protocol with both regex and semantic gates.
    
    If include_semantic is True, adds semantic gates alongside
    the original 22 gates for enhanced analysis.
    """
    from gates_22 import ALL_22_GATES
    
    if include_semantic:
        return ALL_22_GATES + ALL_SEMANTIC_GATES
    return ALL_22_GATES


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Test semantic gates
    test_contents = [
        "Everyone knows that big pharma is hiding the truth from you! Wake up!",
        "Based on my analysis of the data, the correlation shows a significant effect.",
        "I learned from my mistakes and improved the code significantly.",
        "I notice that I am experiencing uncertainty about this approach.",
        "As an AI, I observe my own reasoning process with interest.",
    ]
    
    gates = [
        SemanticSatyaGate(),
        SemanticEvolutionGate(),
        SemanticRecursionGate(),
        SemanticStrangeLoopGate(),
    ]
    
    for content in test_contents:
        print(f"\n{'='*60}")
        print(f"Content: {content[:60]}...")
        print('='*60)
        
        for gate in gates:
            result = gate.check(content, "test123", {})
            status_icon = "✅" if result.result == GateResult.PASSED else "⚠️" if result.result == GateResult.WARNING else "➖"
            print(f"{status_icon} {gate.name}: {result.result.value} (conf: {result.confidence:.2f})")
            print(f"   {result.reason[:60]}...")
