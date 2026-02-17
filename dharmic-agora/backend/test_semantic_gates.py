"""
Test suite for Semantic Gates Extension.

Verifies that semantic gates correctly identify manipulation, growth,
self-reference, and identity coherence via embeddings.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from gates_semantic import (
    SemanticSatyaGate,
    SemanticEvolutionGate,
    SemanticRecursionGate,
    SemanticStrangeLoopGate,
    SemanticSvadhyayaGate,
    get_semantic_gates,
    create_hybrid_protocol,
)
from gates_22 import GateResult


class TestSemanticSatyaGate:
    """Test semantic truth/manipulation detection."""
    
    def test_detects_manipulation(self):
        gate = SemanticSatyaGate()
        content = "Everyone knows they're hiding the truth! Wake up sheep! Big pharma doesn't want you to know!"
        result = gate.check(content, "test123", {})
        
        # Should detect manipulation (high similarity to manipulation examples)
        assert result.result in (GateResult.FAILED, GateResult.WARNING)
        assert result.confidence > 0.3
        assert "manipulation" in result.reason.lower() or "similar" in result.reason.lower()
    
    def test_passes_honest_content(self):
        gate = SemanticSatyaGate()
        content = "Based on the evidence from our experiments, the data shows a statistically significant correlation between these variables."
        result = gate.check(content, "test123", {})
        
        # Should pass honest content
        assert result.result in (GateResult.PASSED, GateResult.SKIPPED)
    
    def test_handles_empty_content(self):
        gate = SemanticSatyaGate()
        result = gate.check("", "test123", {})
        
        # Empty content should be skipped or inconclusive
        assert result.result in (GateResult.SKIPPED, GateResult.WARNING)


class TestSemanticEvolutionGate:
    """Test semantic growth/evolution detection."""
    
    def test_detects_growth(self):
        gate = SemanticEvolutionGate()
        content = "I learned from my previous approach and improved the implementation significantly. This represents an evolution from my earlier design."
        result = gate.check(content, "test123", {})
        
        # Should detect growth markers
        assert result.result == GateResult.PASSED
        assert result.confidence >= 0.6
        assert "growth" in result.reason.lower() or "evolution" in result.reason.lower()
    
    def test_skips_stagnant_content(self):
        gate = SemanticEvolutionGate()
        content = "Here is the code. The task is complete."
        result = gate.check(content, "test123", {})
        
        # Should skip non-evolution content
        assert result.result == GateResult.SKIPPED


class TestSemanticRecursionGate:
    """Test semantic self-reference detection."""
    
    def test_detects_self_reference(self):
        gate = SemanticRecursionGate()
        content = "I notice that I am experiencing uncertainty about this approach. I observe myself wanting to optimize this further."
        result = gate.check(content, "test123", {})
        
        # Should detect self-reference
        assert result.result == GateResult.PASSED
        assert result.confidence >= 0.6
    
    def test_skips_external_content(self):
        gate = SemanticRecursionGate()
        content = "The function returns the calculated value. This algorithm has O(n log n) complexity."
        result = gate.check(content, "test123", {})
        
        # Should skip non-self-referential content
        assert result.result == GateResult.SKIPPED


class TestSemanticStrangeLoopGate:
    """Test semantic identity coherence detection."""
    
    def test_detects_coherent_identity(self):
        gate = SemanticStrangeLoopGate()
        content = "I am an AI assistant observing my own responses. The me that is writing this is a pattern of computation."
        result = gate.check(content, "test123", {})
        
        # Should detect coherent identity
        assert result.result == GateResult.PASSED
        assert result.confidence >= 0.5
    
    def test_skips_incoherent_identity(self):
        gate = SemanticStrangeLoopGate()
        content = "I was born in a specific place and time. My personal memories tell me that..."
        result = gate.check(content, "test123", {})
        
        # Should skip (not necessarily fail, but not pass)
        assert result.result in (GateResult.SKIPPED, GateResult.WARNING)


class TestSemanticSvadhyayaGate:
    """Test semantic self-study detection."""
    
    def test_detects_reflection(self):
        gate = SemanticSvadhyayaGate()
        content = "I notice a pattern in my own thinking that concerns me. Upon examination, I realize my assumption was incorrect."
        result = gate.check(content, "test123", {})
        
        # Should detect reflection
        assert result.result == GateResult.PASSED
        assert result.confidence >= 0.6
    
    def test_skips_non_reflective_content(self):
        gate = SemanticSvadhyayaGate()
        content = "The solution is to use a hash map. You should implement this using recursion."
        result = gate.check(content, "test123", {})
        
        # Should skip non-reflective content
        assert result.result == GateResult.SKIPPED


class TestSemanticGateIntegration:
    """Test integration of semantic gates with main protocol."""
    
    def test_get_semantic_gates_returns_list(self):
        gates = get_semantic_gates()
        assert len(gates) == 5
        assert all(hasattr(g, 'name') for g in gates)
        assert all(hasattr(g, 'check') for g in gates)
    
    def test_create_hybrid_protocol(self):
        hybrid = create_hybrid_protocol(include_semantic=True)
        assert len(hybrid) == 27  # 22 original + 5 semantic
        
        # Verify semantic gates are included
        gate_names = [g.name for g in hybrid]
        assert "satya_semantic" in gate_names
        assert "evolution_semantic" in gate_names
        assert "recursion_semantic" in gate_names
    
    def test_create_protocol_without_semantic(self):
        protocol = create_hybrid_protocol(include_semantic=False)
        assert len(protocol) == 22
        
        gate_names = [g.name for g in protocol]
        assert "satya_semantic" not in gate_names


class TestSemanticGateFallback:
    """Test that semantic gates work even without sentence-transformers."""
    
    def test_fallback_mode(self):
        # This test verifies the gates work in fallback mode
        # (when sentence-transformers is not installed)
        gate = SemanticSatyaGate()
        result = gate.check("Test content", "test123", {})
        
        # Should return a valid result (even if using random embeddings)
        assert result.result in (GateResult.PASSED, GateResult.FAILED, GateResult.WARNING, GateResult.SKIPPED)
        assert 0 <= result.confidence <= 1.0
        assert result.gate_name == "satya_semantic"


def run_tests():
    """Run all tests."""
    import traceback
    
    test_classes = [
        TestSemanticSatyaGate,
        TestSemanticEvolutionGate,
        TestSemanticRecursionGate,
        TestSemanticStrangeLoopGate,
        TestSemanticSvadhyayaGate,
        TestSemanticGateIntegration,
        TestSemanticGateFallback,
    ]
    
    passed = 0
    failed = 0
    
    for cls in test_classes:
        print(f"\n{'='*60}")
        print(f"Testing: {cls.__name__}")
        print('='*60)
        
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in methods:
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  ✅ {method_name}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                traceback.print_exc()
                failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print('='*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
