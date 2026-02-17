#!/usr/bin/env python3
"""
SIS v0.5 — Integration Test #1
Verifies: HTTP endpoint receives DGC score, dashboard displays live

Run: python3 test_integration_001.py
"""

import requests
import json
import time
import subprocess
import sys
import signal
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8766"
TEST_DB_PATH = Path(__file__).parent / "data" / "test_shared_board.db"

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def log(msg, color=Colors.BLUE):
    print(f"{color}[TEST]{Colors.RESET} {msg}")

def check(condition, msg):
    if condition:
        log(f"✓ {msg}", Colors.GREEN)
        return True
    else:
        log(f"✗ {msg}", Colors.RED)
        return False

class SISIntegrationTest:
    def __init__(self):
        self.server_process = None
        self.passed = 0
        self.failed = 0
        self.test_agent_id = "test_builder_001"
        self.output_id = None

    def start_server(self):
        """Start the SIS server in background"""
        log("Starting SIS server...")
        import os
        env = os.environ.copy()
        env["SIS_TEST_MODE"] = "1"
        
        self.server_process = subprocess.Popen(
            [sys.executable, "src/server.py"],
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        # Wait for server to start
        time.sleep(2)
        
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            check(resp.status_code == 200, "Server health check")
            return True
        except Exception as e:
            log(f"Server failed to start: {e}", Colors.RED)
            return False

    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            log("Server stopped")

    def test_01_health_endpoint(self):
        """Test: Health endpoint returns correct structure"""
        log("\n--- Test 1: Health Endpoint ---")
        try:
            resp = requests.get(f"{BASE_URL}/health")
            data = resp.json()
            
            checks = [
                check(resp.status_code == 200, "HTTP 200 OK"),
                check("status" in data, "Has status field"),
                check("timestamp" in data, "Has timestamp field"),
                check("agents_registered" in data, "Has agents_registered field"),
                check("pending_tasks" in data, "Has pending_tasks field"),
            ]
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def test_02_register_agent(self):
        """Test: Can register an agent"""
        log("\n--- Test 2: Agent Registration ---")
        try:
            payload = {
                "agent_id": self.test_agent_id,
                "base_model": "kimi-k2.5",
                "alias": "TestBuilder",
                "perceived_role": "integration_tester",
                "task_affinity": ["testing", "integration"]
            }
            
            resp = requests.post(
                f"{BASE_URL}/board/agents/{self.test_agent_id}/register",
                json=payload
            )
            
            checks = [
                check(resp.status_code == 200, "HTTP 200 OK"),
                check(resp.json().get("status") == "registered", "Status is 'registered'"),
                check(resp.json().get("agent_id") == self.test_agent_id, "Agent ID matches"),
            ]
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def test_03_log_output(self):
        """Test: Can log agent output"""
        log("\n--- Test 3: Output Logging ---")
        try:
            payload = {
                "agent_id": self.test_agent_id,
                "summary": "Built integration test for SIS v0.5. Test verified: HTTP endpoint receives DGC score, dashboard displays live. JSCA 🪷",
                "artifact_path": "/test/handoff_001.md"
            }
            
            resp = requests.post(f"{BASE_URL}/board/outputs", json=payload)
            data = resp.json()
            
            checks = [
                check(resp.status_code == 200, "HTTP 200 OK"),
                check(data.get("status") == "logged", "Status is 'logged'"),
                check(data.get("agent_id") == self.test_agent_id, "Agent ID matches"),
            ]
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def test_04_get_recent_outputs(self):
        """Test: Can retrieve recent outputs"""
        log("\n--- Test 4: Retrieve Recent Outputs ---")
        try:
            resp = requests.get(f"{BASE_URL}/board")
            data = resp.json()
            
            checks = [
                check(resp.status_code == 200, "HTTP 200 OK"),
                check("recent_outputs" in data, "Has recent_outputs field"),
                check(isinstance(data["recent_outputs"], list), "recent_outputs is a list"),
            ]
            
            # Check if our output is in the list
            outputs = data.get("recent_outputs", [])
            our_output = any(
                o.get("agent_id") == self.test_agent_id 
                for o in outputs
            )
            checks.append(check(our_output, "Our test output appears in recent outputs"))
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def test_05_dgc_score_output(self):
        """Test: DGC scoring endpoint works"""
        log("\n--- Test 5: DGC Scoring ---")
        try:
            # First get the most recent output ID
            resp = requests.get(f"{BASE_URL}/board")
            data = resp.json()
            outputs = data.get("recent_outputs", [])
            
            if not outputs:
                log("No outputs to score", Colors.RED)
                self.failed += 1
                return False
            
            # Get the output_id of our test output
            our_output = None
            for o in outputs:
                if o.get("agent_id") == self.test_agent_id:
                    our_output = o
                    break
            
            if not our_output:
                log("Test output not found in recent outputs", Colors.RED)
                self.failed += 1
                return False
            
            output_id = our_output.get("output_id")
            
            # Now score it via DGC endpoint
            resp = requests.post(f"{BASE_URL}/board/outputs/{output_id}/score")
            data = resp.json()
            
            checks = [
                check(resp.status_code == 200, "HTTP 200 OK"),
                check("dgc_score" in data, "Has dgc_score field"),
                check("passed_gate" in data, "Has passed_gate field"),
                check("gate_message" in data, "Has gate_message field"),
                check("output_id" in data and data["output_id"] == output_id, "Output ID matches"),
            ]
            
            # Validate DGC score structure
            dgc = data.get("dgc_score", {})
            checks.append(check("scores" in dgc, "DGC score has 'scores' field"))
            checks.append(check("composite" in dgc, "DGC score has 'composite' field"))
            checks.append(check(isinstance(dgc.get("composite"), (int, float)), "Composite is numeric"))
            
            # Verify score dimensions
            scores = dgc.get("scores", {})
            expected_dims = ["correctness", "dharmic_alignment", "elegance", "efficiency", "safety"]
            for dim in expected_dims:
                checks.append(check(dim in scores, f"Has '{dim}' dimension"))
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            
            # Store for later tests
            self.output_id = output_id
            
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def test_06_dgc_scores_endpoint(self):
        """Test: DGC scores list endpoint works"""
        log("\n--- Test 6: DGC Scores List ---")
        try:
            resp = requests.get(f"{BASE_URL}/board/outputs/scores/recent?limit=5")
            data = resp.json()
            
            checks = [
                check(resp.status_code == 200, "HTTP 200 OK"),
                check("scored_outputs" in data, "Has scored_outputs field"),
                check(isinstance(data["scored_outputs"], list), "scored_outputs is a list"),
            ]
            
            # Our output should be in the scored list
            scored = data.get("scored_outputs", [])
            our_scored = any(o.get("output_id") == self.output_id for o in scored)
            checks.append(check(our_scored, "Our output appears in scored list"))
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def test_07_dashboard_api(self):
        """Test: Dashboard API returns complete data"""
        log("\n--- Test 7: Dashboard API ---")
        try:
            resp = requests.get(f"{BASE_URL}/board")
            data = resp.json()
            
            required_fields = ["agents", "project", "pending_tasks", "recent_outputs"]
            checks = []
            
            for field in required_fields:
                checks.append(check(field in data, f"Has '{field}' field"))
            
            # Validate agents data
            agents = data.get("agents", [])
            checks.append(check(isinstance(agents, list), "agents is a list"))
            
            # Our test agent should be in the list
            our_agent = any(a.get("agent_id") == self.test_agent_id for a in agents)
            checks.append(check(our_agent, "Test agent appears in agents list"))
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def test_08_end_to_end_flow(self):
        """Test: Complete end-to-end integration"""
        log("\n--- Test 8: End-to-End Integration ---")
        try:
            # Full flow: Register → Log → Score → Verify in dashboard
            
            # Step 1: Register new agent
            agent_id = "e2e_test_agent"
            requests.post(
                f"{BASE_URL}/board/agents/{agent_id}/register",
                json={
                    "agent_id": agent_id,
                    "base_model": "test-model",
                    "alias": "E2ETester",
                    "perceived_role": "end_to_end_tester",
                    "task_affinity": ["e2e"]
                }
            )
            
            # Step 2: Log output with dharmic markers (should score high)
            requests.post(f"{BASE_URL}/board/outputs", json={
                "agent_id": agent_id,
                "summary": "Test with Jagat Kalyan telos. Verified, tested, works. JSCA 🪷",
                "artifact_path": "/test/e2e.md"
            })
            
            # Step 3: Get the output and score it
            board_data = requests.get(f"{BASE_URL}/board").json()
            outputs = board_data.get("recent_outputs", [])
            our_output = next((o for o in outputs if o.get("agent_id") == agent_id), None)
            
            if not our_output:
                log("E2E: Output not found", Colors.RED)
                self.failed += 1
                return False
            
            output_id = our_output.get("output_id")
            score_resp = requests.post(f"{BASE_URL}/board/outputs/{output_id}/score")
            score_data = score_resp.json()
            
            # Step 4: Verify score reflects dharmic content
            dgc = score_data.get("dgc_score", {})
            composite = dgc.get("composite", 0)
            
            checks = [
                check(score_data.get("passed_gate") == True, "Output passed DGC gate"),
                check(composite > 0.7, f"Composite score ({composite:.2f}) > 0.7"),
            ]
            
            # Step 5: Verify appears in dashboard
            scored = requests.get(f"{BASE_URL}/board/outputs/scores/recent").json()
            in_scored = any(o.get("output_id") == output_id for o in scored.get("scored_outputs", []))
            checks.append(check(in_scored, "Scored output appears in recent scores"))
            
            self.passed += sum(checks)
            self.failed += len(checks) - sum(checks)
            return all(checks)
        except Exception as e:
            log(f"Exception: {e}", Colors.RED)
            self.failed += 1
            return False

    def run_all(self):
        """Run all integration tests"""
        log("=" * 60)
        log("SIS v0.5 INTEGRATION TEST #1")
        log("HTTP → DGC → Dashboard Pipeline")
        log("=" * 60)
        
        # Start server
        if not self.start_server():
            log("Cannot proceed without server", Colors.RED)
            return False
        
        try:
            # Run all tests
            tests = [
                self.test_01_health_endpoint,
                self.test_02_register_agent,
                self.test_03_log_output,
                self.test_04_get_recent_outputs,
                self.test_05_dgc_score_output,
                self.test_06_dgc_scores_endpoint,
                self.test_07_dashboard_api,
                self.test_08_end_to_end_flow,
            ]
            
            for test in tests:
                try:
                    test()
                except Exception as e:
                    log(f"Test failed with exception: {e}", Colors.RED)
                    self.failed += 1
            
        finally:
            self.stop_server()
        
        # Summary
        log("\n" + "=" * 60)
        log(f"PASSED: {self.passed}")
        log(f"FAILED: {self.failed}")
        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0
        log(f"SUCCESS RATE: {pct:.1f}%")
        log("=" * 60)
        
        return self.failed == 0

if __name__ == "__main__":
    test = SISIntegrationTest()
    success = test.run_all()
    sys.exit(0 if success else 1)
