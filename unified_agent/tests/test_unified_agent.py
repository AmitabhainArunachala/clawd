#!/usr/bin/env python3
"""
Tests for Unified Agent Core
Iteration 1 Verification
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path.home() / '.chaiwala'))

from unified_agent import (
    BaseAgent, DHARMIC_CLAW_Agent, WARP_REGENT_Agent,
    UnifiedAgentOrchestrator, AgentState, Capability
)


class TestBaseAgent(unittest.TestCase):
    """Test base agent functionality"""
    
    def test_agent_initialization(self):
        agent = BaseAgent("test_agent", "Test agent")
        self.assertEqual(agent.agent_id, "test_agent")
        self.assertEqual(agent.state, AgentState.INITIALIZING)
        
    def test_capability_registration(self):
        agent = BaseAgent("test_agent")
        
        def dummy_handler(msg, payload):
            return {'status': 'ok'}
            
        agent.register_capability("test", "Test capability", dummy_handler)
        
        self.assertIn("test", agent.capabilities)
        self.assertEqual(agent.capabilities["test"].name, "test")
        
    def test_health_check(self):
        agent = BaseAgent("test_agent")
        agent.start()
        
        health = agent.get_health()
        self.assertEqual(health.agent_id, "test_agent")
        self.assertEqual(health.state, AgentState.ONLINE)
        
    def test_message_routing(self):
        agent = BaseAgent("test_agent")
        
        handler_calls = []
        def test_handler(msg, payload):
            handler_calls.append((msg, payload))
            return {'status': 'handled'}
            
        agent.register_handler("TEST", test_handler)
        
        # Simulate message
        msg = {
            'subject': 'TEST_MESSAGE',
            'body': '{"data": "test"}'
        }
        
        result = agent.process_message(msg)
        self.assertEqual(result['status'], 'handled')


class TestDHARMIC_CLAW_Agent(unittest.TestCase):
    """Test DHARMIC_CLAW specialization"""
    
    def test_capabilities(self):
        agent = DHARMIC_CLAW_Agent()
        
        self.assertIn("research", agent.capabilities)
        self.assertIn("document", agent.capabilities)
        self.assertIn("review", agent.capabilities)
        
    def test_research_handler(self):
        agent = DHARMIC_CLAW_Agent()
        
        msg = {'subject': 'RESEARCH_REQUEST'}
        payload = {'query': 'AI consciousness'}
        
        result = agent._handle_research(msg, payload)
        
        self.assertEqual(result['status'], 'research_complete')
        self.assertEqual(result['query'], 'AI consciousness')


class TestWARP_REGENT_Agent(unittest.TestCase):
    """Test WARP_REGENT specialization"""
    
    def test_capabilities(self):
        agent = WARP_REGENT_Agent()
        
        self.assertIn("execute", agent.capabilities)
        self.assertIn("email", agent.capabilities)
        self.assertIn("monitor", agent.capabilities)
        
    def test_execute_handler(self):
        agent = WARP_REGENT_Agent()
        
        msg = {'subject': 'EXECUTE_REQUEST'}
        payload = {'command': 'ls -la'}
        
        result = agent._handle_execute(msg, payload)
        
        self.assertEqual(result['status'], 'executed')
        self.assertEqual(result['command'], 'ls -la')


class TestOrchestrator(unittest.TestCase):
    """Test orchestrator functionality"""
    
    def test_agent_registration(self):
        orch = UnifiedAgentOrchestrator()
        agent = BaseAgent("test_agent")
        
        orch.register_agent(agent)
        
        self.assertIn("test_agent", orch.agents)
        self.assertEqual(orch.agents["test_agent"].state, AgentState.ONLINE)
        
    def test_task_routing(self):
        orch = UnifiedAgentOrchestrator()
        
        dc = DHARMIC_CLAW_Agent()
        wr = WARP_REGENT_Agent()
        
        orch.register_agent(dc)
        orch.register_agent(wr)
        
        # Research should go to DHARMIC_CLAW
        target = orch.route_task("research", {"query": "test"})
        self.assertEqual(target, "dharmic_claw")
        
        # Execute should go to WARP_REGENT
        target = orch.route_task("execute", {"command": "test"})
        self.assertEqual(target, "warp_regent")


def run_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("🧪 UNIFIED AGENT CORE - Test Suite")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBaseAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestDHARMIC_CLAW_Agent))
    suite.addTests(loader.loadTestsFromTestCase(TestWARP_REGENT_Agent))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
