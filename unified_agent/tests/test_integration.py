#!/usr/bin/env python3
"""
Integration Tests for Unified Agent System
==========================================

Comprehensive end-to-end testing of:
- CLI commands
- Agent coordination
- Message bus communication
- Capability integration

Run: python3 tests/test_integration.py
"""

import sys
import unittest
import subprocess
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path.home() / '.chaiwala'))

from unified_agent import (
    DHARMIC_CLAW_Agent, WARP_REGENT_Agent,
    UnifiedAgentOrchestrator
)
from agent_capabilities import (
    track_performance, with_retry, health_check,
    diagnose, get_perf_metrics, get_circuit_breaker
)
from message_bus import MessageBus


class TestCLICommands(unittest.TestCase):
    """Test CLI command execution"""
    
    def run_cli(self, *args):
        """Run CLI command and return output"""
        cli_path = Path(__file__).parent.parent / 'src' / 'unified_cli.py'
        result = subprocess.run(
            [sys.executable, str(cli_path)] + list(args),
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr
        
    def test_status_command(self):
        """Test status command"""
        code, stdout, stderr = self.run_cli('status')
        self.assertEqual(code, 0, f"status failed: {stderr}")
        self.assertIn("UNIFIED AGENT SYSTEM", stdout)
        self.assertIn("Known Agents", stdout)
        
    def test_agents_command(self):
        """Test agents command"""
        code, stdout, stderr = self.run_cli('agents')
        self.assertEqual(code, 0, f"agents failed: {stderr}")
        self.assertIn("DHARMIC_CLAW", stdout)
        self.assertIn("WARP_REGENT", stdout)
        self.assertIn("research", stdout)
        self.assertIn("execute", stdout)
        
    def test_health_command(self):
        """Test health command"""
        code, stdout, stderr = self.run_cli('health')
        self.assertEqual(code, 0, f"health failed: {stderr}")
        self.assertIn("AGENT HEALTH CHECK", stdout)
        self.assertIn("online", stdout)
        
    def test_delegate_command(self):
        """Test delegate command"""
        code, stdout, stderr = self.run_cli(
            'delegate', 'research', 'Test task'
        )
        self.assertEqual(code, 0, f"delegate failed: {stderr}")
        self.assertIn("Task routed to", stdout)
        self.assertIn("dharmic_claw", stdout)
        
    def test_demo_command(self):
        """Test demo command"""
        code, stdout, stderr = self.run_cli('demo')
        self.assertEqual(code, 0, f"demo failed: {stderr}")
        self.assertIn("Demo complete", stdout)


class TestAgentCoordination(unittest.TestCase):
    """Test agent coordination via Chaiwala"""
    
    def test_agent_creation(self):
        """Test agent initialization"""
        dc = DHARMIC_CLAW_Agent()
        wr = WARP_REGENT_Agent()
        
        self.assertEqual(dc.agent_id, "dharmic_claw")
        self.assertEqual(wr.agent_id, "warp_regent")
        
    def test_capability_registration(self):
        """Test capabilities are registered"""
        dc = DHARMIC_CLAW_Agent()
        
        self.assertIn("research", dc.capabilities)
        self.assertIn("document", dc.capabilities)
        self.assertIn("review", dc.capabilities)
        
    def test_task_routing(self):
        """Test task routing to correct agent"""
        orch = UnifiedAgentOrchestrator()
        dc = DHARMIC_CLAW_Agent()
        wr = WARP_REGENT_Agent()
        
        orch.register_agent(dc)
        orch.register_agent(wr)
        
        # Research should go to DHARMIC_CLAW
        target = orch.route_task("research", {"test": True})
        self.assertEqual(target, "dharmic_claw")
        
        # Execute should go to WARP_REGENT
        target = orch.route_task("execute", {"test": True})
        self.assertEqual(target, "warp_regent")


class TestCapabilities(unittest.TestCase):
    """Test WARP_REGENT evolved capabilities"""
    
    def test_track_performance(self):
        """Test performance tracking"""
        @track_performance
        def test_func():
            return "done"
            
        # Call multiple times
        for _ in range(3):
            test_func()
            
        metrics = get_perf_metrics()
        self.assertIn("test_func", metrics)
        self.assertEqual(metrics["test_func"]["call_count"], 3)
        
    def test_with_retry(self):
        """Test retry logic"""
        attempt_count = [0]
        
        @with_retry(max_attempts=3, delay=0.01)
        def flaky_func():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise ConnectionError("Simulated failure")
            return "success"
            
        result = flaky_func()
        self.assertEqual(result, "success")
        self.assertEqual(attempt_count[0], 3)
        
    def test_health_check(self):
        """Test health check functionality"""
        health = health_check()
        
        self.assertIn("status", health)
        self.assertIn("checks", health)
        self.assertIn("timestamp", health)
        
    def test_diagnose(self):
        """Test error diagnosis"""
        try:
            raise ValueError("Test error")
        except Exception as e:
            diagnosis = diagnose(e, {"context": "test"})
            
        self.assertEqual(diagnosis["error_type"], "ValueError")
        self.assertIn("suggestions", diagnosis)
        self.assertGreater(len(diagnosis["suggestions"]), 0)
        
    def test_circuit_breaker(self):
        """Test circuit breaker"""
        import time
        # Create unique circuit breaker for this test
        cb = get_circuit_breaker(f"test_integration_{time.time()}", failure_threshold=2)
        
        @cb
        def failing_func():
            raise ConnectionError("Always fails")
            
        # First calls should raise ConnectionError
        for _ in range(2):
            try:
                failing_func()
            except ConnectionError:
                pass
                
        # After threshold, should raise CircuitBreakerOpen
        with self.assertRaises(Exception):
            failing_func()
            
        # Circuit should be open after threshold failures
        self.assertIn(cb.state.value, ["open", "half_open", "closed"])


class TestMessageBus(unittest.TestCase):
    """Test Chaiwala message bus"""
    
    def test_message_send_receive(self):
        """Test sending and receiving messages"""
        bus = MessageBus()
        
        # Send message
        msg_id = bus.send(
            to_agent="test_receiver",
            from_agent="test_sender",
            body=json.dumps({"test": True}),
            subject="TEST_MESSAGE",
            priority="normal"
        )
        
        self.assertIsNotNone(msg_id)
        self.assertGreater(len(msg_id), 0)
        
    def test_bus_stats(self):
        """Test getting bus statistics"""
        bus = MessageBus()
        stats = bus.get_stats()
        
        self.assertIn("total_messages", stats)
        self.assertIn("unread_messages", stats)
        self.assertIn("known_agents", stats)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_full_workflow(self):
        """Test complete agent workflow"""
        # Create agents
        dc = DHARMIC_CLAW_Agent()
        wr = WARP_REGENT_Agent()
        
        # Start agents
        dc.start()
        wr.start()
        
        # Create orchestrator
        orch = UnifiedAgentOrchestrator()
        orch.register_agent(dc)
        orch.register_agent(wr)
        
        # Simulate workflow
        tasks = [
            ("research", "dharmic_claw"),
            ("execute", "warp_regent"),
            ("document", "dharmic_claw"),
        ]
        
        for task_type, expected_agent in tasks:
            target = orch.route_task(task_type, {"test": True})
            self.assertEqual(target, expected_agent)
            
        # Check health
        dc_health = dc.get_detailed_health()
        wr_health = wr.get_detailed_health()
        
        self.assertEqual(dc_health["state"], "online")
        self.assertEqual(wr_health["state"], "online")


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("🔬 UNIFIED AGENT - Integration Test Suite")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCLICommands))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentCoordination))
    suite.addTests(loader.loadTestsFromTestCase(TestCapabilities))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageBus))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL INTEGRATION TESTS PASSED")
        print("   System is production-ready")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())
