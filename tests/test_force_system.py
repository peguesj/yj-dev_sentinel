#!/usr/bin/env python3
"""
Comprehensive test suite for the Force Agentic Development System.

Tests the core Force engine, tool execution, pattern application,
constraint validation, legacy agent integration, and YUNG command processing.
"""

import unittest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from force import ForceEngine
from force.legacy_adapter import LegacyAgentManager
from force.yung_integration import YUNGForceIntegration


class TestForceEngine(unittest.TestCase):
    """Test cases for the core Force engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = ForceEngine()
        
    def test_engine_initialization(self):
        """Test Force engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertTrue(self.engine.force_dir.exists())
        
    def test_tool_loading(self):
        """Test tool loading and discovery."""
        tools = self.engine.list_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check specific tools
        expected_tools = [
            'git_workflow_commit',
            'documentation_analysis',
            'code_quality_check'
        ]
        for tool in expected_tools:
            self.assertIn(tool, tools)
            
    def test_pattern_loading(self):
        """Test pattern loading and discovery."""
        patterns = self.engine.list_patterns()
        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        
        # Check specific patterns
        expected_patterns = [
            'agent_development_workflow',
            'mcp_integration_pattern'
        ]
        for pattern in expected_patterns:
            self.assertIn(pattern, patterns)
            
    def test_constraint_loading(self):
        """Test constraint loading and discovery."""
        constraints = self.engine.list_constraints()
        self.assertIsInstance(constraints, list)
        self.assertGreater(len(constraints), 0)
        
    def test_tool_execution(self):
        """Test tool execution functionality."""
        result = self.engine.execute_tool_sync('documentation_analysis', {
            'directory': '.',
            'analyze_readmes': True,
            'check_completeness': True
        })
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result['success'])
        self.assertIn('executionId', result)
        self.assertIn('result', result)
        self.assertIn('executionTime', result)
        
    def test_tool_validation(self):
        """Test tool parameter validation."""
        # Test with missing required parameters
        with self.assertRaises(Exception):
            self.engine.execute_tool_sync('documentation_analysis', {})
            
    def test_tool_not_found(self):
        """Test handling of non-existent tools."""
        with self.assertRaises(Exception):
            self.engine.execute_tool_sync('non_existent_tool', {})


class TestLegacyAgentIntegration(unittest.TestCase):
    """Test cases for legacy agent integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = LegacyAgentManager()
        
    def test_agent_discovery(self):
        """Test legacy agent discovery."""
        agents = self.manager.get_available_agents()
        self.assertIsInstance(agents, dict)
        self.assertGreater(len(agents), 0)
        
        # Check specific agents
        expected_agents = ['VCMA', 'VCLA', 'RDIA', 'CDIA', 'SAA']
        for agent in expected_agents:
            self.assertIn(agent, agents)
            
    def test_agent_adapter_creation(self):
        """Test agent adapter creation."""
        adapter = self.manager.get_agent_adapter('VCMA')
        self.assertIsNotNone(adapter)
        
    def test_agent_capabilities(self):
        """Test agent capability listing."""
        capabilities = self.manager.list_agent_capabilities('VCMA')
        self.assertIsInstance(capabilities, list)
        self.assertGreater(len(capabilities), 0)


class TestYUNGIntegration(unittest.TestCase):
    """Test cases for YUNG command integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.integration = YUNGForceIntegration()
        
    def test_integration_initialization(self):
        """Test YUNG integration initialization."""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.force_engine)
        
    async def test_command_processing(self):
        """Test YUNG command processing."""
        result = await self.integration.process_yung_command('ANALYZE README')
        self.assertIsInstance(result, dict)
        
    def test_command_processing_sync(self):
        """Test YUNG command processing (sync wrapper)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.integration.process_yung_command('ANALYZE README')
            )
            self.assertIsInstance(result, dict)
        finally:
            loop.close()


class TestForceSystemIntegration(unittest.TestCase):
    """Integration tests for the complete Force system."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = ForceEngine()
        self.legacy_manager = LegacyAgentManager()
        self.yung_integration = YUNGForceIntegration()
        
    def test_end_to_end_workflow(self):
        """Test end-to-end Force workflow."""
        # 1. Execute a Force tool
        tool_result = self.engine.execute_tool_sync('project_structure_analysis', {
            'directory': '.',
            'include_hidden': False,
            'max_depth': 3
        })
        self.assertTrue(tool_result['success'])
        
        # 2. Get legacy agent
        adapter = self.legacy_manager.get_agent_adapter('RDIA')
        self.assertIsNotNone(adapter)
        
        # 3. Test YUNG command processing (sync)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            yung_result = loop.run_until_complete(
                self.yung_integration.process_yung_command('STATUS')
            )
            self.assertIsInstance(yung_result, dict)
        finally:
            loop.close()
            
    def test_force_component_consistency(self):
        """Test consistency across Force components."""
        # Check that all tools have valid definitions
        tools = self.engine.load_tools()
        for tool_id, tool_def in tools.items():
            self.assertIn('id', tool_def)
            self.assertIn('name', tool_def)
            self.assertIn('description', tool_def)
            self.assertIn('parameters', tool_def)
            
        # Check that all patterns have valid definitions
        patterns = self.engine.load_patterns()
        for pattern_id, pattern_def in patterns.items():
            self.assertIn('id', pattern_def)
            self.assertIn('name', pattern_def)
            self.assertIn('description', pattern_def)
            
    def test_schema_validation(self):
        """Test schema validation across components."""
        # This will be automatically tested during component loading
        # since the engine validates against schemas
        try:
            tools = self.engine.load_tools()
            patterns = self.engine.load_patterns()
            constraints = self.engine.load_constraints()
            
            # If we get here without exceptions, validation passed
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Schema validation failed: {e}")


def run_tests():
    """Run all Force system tests."""
    print("🚀 Running Force System Test Suite")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestForceEngine))
    suite.addTest(unittest.makeSuite(TestLegacyAgentIntegration))
    suite.addTest(unittest.makeSuite(TestYUNGIntegration))
    suite.addTest(unittest.makeSuite(TestForceSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"🎯 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
            
    if result.errors:
        print(f"\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
            
    success = len(result.failures) == 0 and len(result.errors) == 0
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"\n🏁 Overall Result: {status}")
    
    return success


if __name__ == '__main__':
    run_tests()
