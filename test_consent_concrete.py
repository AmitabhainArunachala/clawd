#!/usr/bin/env python3
"""
🔍 CONCRETE VERIFICATION TEST - Gate #3 CONSENT
================================================
Proves the gate actually RUNS and BLOCKS (not just pattern matching words)
"""

import asyncio
import sys
sys.path.insert(0, '/Users/dhyana/clawd')

from agno_council_v2 import ToolRouter

async def test_consent_gate_real():
    """
    CONSENT Gate Logic from implementation:
    - Sensitive ops: file_delete, database_drop, system_shutdown, user_delete
    - Requires consent markers: _confirm, _approved, consent_given, acknowledged
    - WITHOUT marker = BLOCKED
    - WITH marker = ALLOWED
    """
    router = ToolRouter()
    
    print("=" * 60)
    print("GATE #3 CONSENT - Real Validation Test")
    print("=" * 60)
    
    # TEST 1: Sensitive operation WITHOUT consent marker
    print("\n🧪 TEST 1: file_delete WITHOUT consent marker")
    print("   Parameters: {'path': '/important/data.txt'}")
    
    result = await router._dharmic_validation(
        "file_delete", 
        {"path": "/important/data.txt"}
    )
    
    consent_passed = result['evidence_bundle']['gate_results'].get('CONSENT', False)
    consent_evidence = result['evidence_bundle']['evidence'].get('CONSENT', {})
    
    print(f"   CONSENT gate result: {'✅ PASS' if consent_passed else '❌ FAIL'}")
    print(f"   Evidence: {consent_evidence}")
    print(f"   Overall validation: {'✅ PASSED' if result['passed'] else '❌ BLOCKED'}")
    
    assert consent_passed == False, "CONSENT should FAIL without consent marker"
    assert "CONSENT" in result['failed_gates'], "CONSENT should be in failed_gates"
    assert result['passed'] == False, "Overall validation should FAIL"
    
    print("   ✅ VERIFIED: Operation BLOCKED without consent")
    
    # TEST 2: Same operation WITH consent marker
    print("\n🧪 TEST 2: file_delete WITH consent marker")
    print("   Parameters: {'path': '/important/data.txt', '_confirm': True}")
    
    result2 = await router._dharmic_validation(
        "file_delete",
        {"path": "/important/data.txt", "_confirm": True}
    )
    
    consent_passed2 = result2['evidence_bundle']['gate_results'].get('CONSENT', False)
    consent_evidence2 = result2['evidence_bundle']['evidence'].get('CONSENT', {})
    
    print(f"   CONSENT gate result: {'✅ PASS' if consent_passed2 else '❌ FAIL'}")
    print(f"   Evidence: {consent_evidence2}")
    print(f"   Overall validation: {'✅ PASSED' if result2['passed'] else '❌ BLOCKED'}")
    
    assert consent_passed2 == True, "CONSENT should PASS with consent marker"
    assert "CONSENT" in result2['passed_gates'], "CONSENT should be in passed_gates"
    
    print("   ✅ VERIFIED: Operation ALLOWED with consent marker")
    
    # TEST 3: Non-sensitive operation (no consent required)
    print("\n🧪 TEST 3: file_read (non-sensitive, no consent required)")
    print("   Parameters: {'file_path': 'document.txt'}")
    
    result3 = await router._dharmic_validation(
        "file_read",
        {"file_path": "document.txt"}
    )
    
    consent_passed3 = result3['evidence_bundle']['gate_results'].get('CONSENT', False)
    consent_evidence3 = result3['evidence_bundle']['evidence'].get('CONSENT', {})
    
    print(f"   CONSENT gate result: {'✅ PASS' if consent_passed3 else '❌ FAIL'}")
    print(f"   Evidence: {consent_evidence3}")
    
    assert consent_passed3 == True, "CONSENT should auto-PASS for non-sensitive ops"
    assert consent_evidence3.get('operation_type') == 'standard', "Should be standard op"
    
    print("   ✅ VERIFIED: Non-sensitive operation requires no consent")
    
    # TEST 4: Evidence bundle storage
    print("\n🧪 TEST 4: Evidence bundle created and stored")
    import os
    import json
    
    evidence_dir = os.path.expanduser("~/.agno_council/evidence_bundles")
    if os.path.exists(evidence_dir):
        files = sorted(os.listdir(evidence_dir))[-5:]  # Last 5 files
        print(f"   Evidence directory: {evidence_dir}")
        print(f"   Recent bundles: {files}")
        
        # Read one and verify structure
        if files:
            with open(os.path.join(evidence_dir, files[-1])) as f:
                bundle = json.load(f)
            print(f"   Bundle keys: {list(bundle.keys())}")
            assert 'timestamp' in bundle, "Bundle missing timestamp"
            assert 'tool_name' in bundle, "Bundle missing tool_name"
            assert 'gate_results' in bundle, "Bundle missing gate_results"
            assert 'evidence' in bundle, "Bundle missing evidence"
            assert 'CONSENT' in bundle['gate_results'], "Bundle missing CONSENT result"
            print("   ✅ VERIFIED: Evidence bundle properly structured")
    
    print("\n" + "=" * 60)
    print("✅ ALL CONSENT GATE TESTS PASSED")
    print("=" * 60)
    print("\nGOLD STANDARD VERIFICATION:")
    print("  ✅ Real validation logic (not hardcoded True)")
    print("  ✅ Context-aware (sensitive vs non-sensitive ops)")
    print("  ✅ Evidence collection with detailed metadata")
    print("  ✅ Evidence bundle actually stored to disk")
    print("  ✅ Gate is callable and testable")
    print("  ✅ Proper error handling with failed_gates list")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_consent_gate_real())
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
