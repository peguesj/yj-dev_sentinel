#!/usr/bin/env python3
"""
Simple structure test for the refactored Dev Sentinel MCP integration.

This script validates the basic structure and imports without requiring
external dependencies.
"""

import sys
import os
import logging

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_core_structure():
    """Test that core components can be imported."""
    logger.info("Testing core structure...")
    
    try:
        from core.agent import BaseAgent
        from core.message_bus import get_message_bus
        from core.task_manager import get_task_manager
        
        logger.info("✓ Core components imported successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Core structure test failed: {e}")
        return False

def test_adapter_structure():
    """Test that adapter components can be imported."""
    logger.info("Testing adapter structure...")
    
    try:
        from integration.fast_agent.adapter import BaseAgentAdapter, MCPAgentAdapter
        logger.info("✓ Base adapter classes imported successfully")
        
        from integration.fast_agent.specialized_adapters import (
            VCMAAdapter,
            VCLAAdapter, 
            CDIAAdapter,
            RDIAAdapter,
            SAAAdapter,
            create_specialized_adapter
        )
        logger.info("✓ Specialized adapter classes imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"✗ Adapter structure test failed: {e}")
        return False

def test_mcp_server_structure():
    """Test that MCP server structure is correct."""
    logger.info("Testing MCP server structure...")
    
    try:
        from integration.fast_agent.mcp_servers import DevSentinelMCPServer
        logger.info("✓ MCP server class imported successfully")
        
        # Test that the class has expected methods
        expected_methods = ['__init__', '_setup_server']
        for method in expected_methods:
            if hasattr(DevSentinelMCPServer, method):
                logger.info(f"  ✓ Method {method} found")
            else:
                logger.warning(f"  ⚠ Method {method} not found")
        
        return True
    except Exception as e:
        logger.error(f"✗ MCP server structure test failed: {e}")
        return False

def test_file_structure():
    """Test that key files exist in the expected locations."""
    logger.info("Testing file structure...")
    
    expected_files = [
        "integration/fast_agent/adapter.py",
        "integration/fast_agent/specialized_adapters.py",
        "integration/fast_agent/mcp_servers.py",
        "core/agent.py",
        "core/message_bus.py",
        "core/task_manager.py",
    ]
    
    missing_files = []
    for file_path in expected_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            logger.info(f"  ✓ {file_path}")
        else:
            logger.error(f"  ✗ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing files: {missing_files}")
        return False
    else:
        logger.info("✓ All expected files found")
        return True

def run_tests():
    """Run all structure tests."""
    logger.info("Starting Dev Sentinel structure validation...")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Core Structure", test_core_structure),
        ("Adapter Structure", test_adapter_structure),
        ("MCP Server Structure", test_mcp_server_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("STRUCTURE VALIDATION SUMMARY")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All structure tests passed! The refactored architecture is well-structured.")
        return True
    else:
        logger.error("❌ Some structure tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)
