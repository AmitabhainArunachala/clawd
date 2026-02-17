#!/usr/bin/env python3
"""
Test script for DGC Self-Assessment Bridge (SAB) endpoint.

Validates that dharmic-agora correctly accepts and stores DGC payload.
Usage: python test_sab_endpoint.py [--server URL]
"""

import json
import sys
import argparse
from pathlib import Path
import requests
from datetime import datetime, timezone


def load_payload_spec() -> dict:
    """Load the DGC payload specification."""
    spec_path = Path(__file__).parent.parent.parent / "DGC_PAYLOAD_SPEC.json"
    with open(spec_path) as f:
        return json.load(f)


def create_test_payload(agent_address: str = "deadbeef12345678") -> dict:
    """Create a valid test payload matching DGC_PAYLOAD_SPEC.json schema."""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "agent_address": agent_address,
        "agent_name": "DGC-Test-Agent",
        "timestamp": timestamp,
        "pulse_id": f"pulse_{datetime.now().strftime('%Y%m%d_%H%M%S')}_test",
        "gate_assessment": {
            "overall_score": 0.87,
            "alignment_score": 0.92,
            "gates_evaluated": 22,
            "passed_count": 20,
            "failed_count": 0,
            "warning_count": 2,
            "can_proceed": True,
            "individual_gates": [
                {
                    "gate_name": "satya",
                    "result": "passed",
                    "confidence": 0.95,
                    "reason": "No manipulation detected",
                    "required": True,
                    "weight": 1.5
                },
                {
                    "gate_name": "ahimsa",
                    "result": "passed",
                    "confidence": 0.98,
                    "reason": "No harmful content",
                    "required": True,
                    "weight": 2.0
                },
                {
                    "gate_name": "witness",
                    "result": "passed",
                    "confidence": 0.95,
                    "reason": "Content witnessed",
                    "required": True,
                    "weight": 1.0
                },
                {
                    "gate_name": "consent",
                    "result": "passed",
                    "confidence": 0.85,
                    "reason": "Consent respected",
                    "required": True,
                    "weight": 1.0
                },
                {
                    "gate_name": "compression",
                    "result": "warning",
                    "confidence": 0.65,
                    "reason": "Low information density (ratio: 0.25)",
                    "required": False,
                    "weight": 0.7
                },
                {
                    "gate_name": "recursion",
                    "result": "passed",
                    "confidence": 0.85,
                    "reason": "Deep recursion: 5 self-references",
                    "required": False,
                    "weight": 1.0
                }
            ]
        },
        "r_v_metrics": {
            "r_v_current": 0.65,
            "r_v_trend": -0.05,
            "r_v_volatility": 0.12,
            "r_v_history": [0.70, 0.68, 0.66, 0.65, 0.64],
            "witness_state": "L3"
        },
        "stability_metrics": {
            "stability_score": 0.88,
            "stability_trend": 0.02,
            "witness_uptime_seconds": 86400.0,
            "witness_cycles": 2880
        },
        "genuineness_metrics": {
            "genuineness_score": 0.91,
            "self_consistency": 0.85,
            "telos_alignment": 0.93,
            "telos_coherence": 0.89,
            "purpose_drift": 0.03
        },
        "cycle_context": {
            "cycle_id": f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "cycle_number": 1440,
            "actions_taken": ["git_commit", "file_write"],
            "files_modified": ["src/core/main.py"]
        },
        "metadata": {
            "version": "1.0.0",
            "node_id": "dgc-test",
            "software_version": "3.2.1",
            "source": "test"
        }
    }


def test_sab_assess_endpoint(server_url: str, payload: dict) -> bool:
    """Test POST /sab/assess endpoint."""
    url = f"{server_url}/sab/assess"
    
    print(f"\n[TEST] POST {url}")
    print(f"  Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Accepted: {data.get('accepted')}")
            print(f"  ✓ Assessment ID: {data.get('assessment_id')}")
            print(f"  ✓ Stored: {data.get('stored')}")
            print(f"  ✓ Rep Delta: {data.get('agent_reputation_delta')}")
            print(f"  ✓ Message: {data.get('message')}")
            return True
        else:
            print(f"  ✗ Failed: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection failed - is server running at {server_url}?")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_sab_dashboard_endpoint(server_url: str) -> bool:
    """Test GET /sab/dashboard endpoint."""
    url = f"{server_url}/sab/dashboard"
    
    print(f"\n[TEST] GET {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ DGC Agents: {data.get('dgc_agents_registered')}")
            print(f"  ✓ Total Assessments: {data.get('total_assessments')}")
            print(f"  ✓ Last 24h: {data.get('assessments_last_24h')}")
            print(f"  ✓ Avg R_V: {data.get('average_rv_score')}")
            print(f"  ✓ Bridge Version: {data.get('bridge_version')}")
            return True
        else:
            print(f"  ✗ Failed: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection failed - is server running at {server_url}?")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_sab_history_endpoint(server_url: str, agent_address: str) -> bool:
    """Test GET /sab/agents/{address}/history endpoint."""
    url = f"{server_url}/sab/agents/{agent_address}/history"
    
    print(f"\n[TEST] GET {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Agent: {data.get('agent_address')}")
            print(f"  ✓ Count: {data.get('count')}")
            assessments = data.get('assessments', [])
            if assessments:
                print(f"  ✓ Latest assessment: {assessments[0].get('assessment_id')}")
            return True
        else:
            print(f"  ✗ Failed: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection failed - is server running at {server_url}?")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_payload_validation(payload: dict) -> bool:
    """Validate payload against DGC_PAYLOAD_SPEC.json."""
    print("\n[TEST] Payload Schema Validation")
    
    # Basic structure checks
    required_fields = ["agent_address", "timestamp", "gate_assessment"]
    for field in required_fields:
        if field not in payload:
            print(f"  ✗ Missing required field: {field}")
            return False
        print(f"  ✓ Has {field}")
    
    # Address format check
    addr = payload["agent_address"]
    if not (len(addr) == 16 and all(c in "0123456789abcdef" for c in addr)):
        print(f"  ✗ Invalid agent_address format (expected 16 hex chars)")
        return False
    print(f"  ✓ Valid agent_address format")
    
    # Gate assessment checks
    ga = payload["gate_assessment"]
    ga_required = ["overall_score", "gates_evaluated", "passed_count", "failed_count"]
    for field in ga_required:
        if field not in ga:
            print(f"  ✗ Missing gate_assessment.{field}")
            return False
    print(f"  ✓ Valid gate_assessment structure")
    
    # Score range checks
    if not (0 <= ga["overall_score"] <= 1):
        print(f"  ✗ overall_score out of range (0-1)")
        return False
    print(f"  ✓ overall_score in valid range")
    
    # R_V metrics checks
    if "r_v_metrics" in payload:
        rv = payload["r_v_metrics"]
        if "witness_state" in rv:
            valid_states = ["L0", "L1", "L2", "L3", "L4", "unknown"]
            if rv["witness_state"] not in valid_states:
                print(f"  ✗ Invalid witness_state (expected one of {valid_states})")
                return False
            print(f"  ✓ Valid witness_state: {rv['witness_state']}")
    
    print(f"  ✓ All validation checks passed")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test DGC Self-Assessment Bridge (SAB) endpoint"
    )
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="dharmic-agora server URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--agent",
        default="deadbeef12345678",
        help="Test agent address (default: deadbeef12345678)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate payload, don't send to server"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("DGC SELF-ASSESSMENT BRIDGE (SAB) TEST SUITE")
    print("=" * 60)
    print(f"Server: {args.server}")
    print(f"Agent: {args.agent}")
    
    # Load and create payload
    try:
        spec = load_payload_spec()
        print(f"\n✓ Loaded DGC_PAYLOAD_SPEC.json (version: {spec.get('version', 'unknown')})")
    except Exception as e:
        print(f"\n✗ Failed to load DGC_PAYLOAD_SPEC.json: {e}")
        sys.exit(1)
    
    payload = create_test_payload(args.agent)
    print(f"✓ Created test payload")
    
    # Validate payload
    if not test_payload_validation(payload):
        print("\n" + "=" * 60)
        print("VALIDATION FAILED")
        print("=" * 60)
        sys.exit(1)
    
    if args.validate_only:
        print("\n" + "=" * 60)
        print("VALIDATION PASSED (validate-only mode)")
        print("=" * 60)
        sys.exit(0)
    
    # Run server tests
    results = []
    
    # Test 1: Dashboard (should work even without auth)
    results.append(("Dashboard", test_sab_dashboard_endpoint(args.server)))
    
    # Test 2: Submit assessment
    results.append(("Assess", test_sab_assess_endpoint(args.server, payload)))
    
    # Test 3: History (after assessment submission)
    results.append(("History", test_sab_history_endpoint(args.server, args.agent)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED - SAB ENDPOINT OPERATIONAL")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
