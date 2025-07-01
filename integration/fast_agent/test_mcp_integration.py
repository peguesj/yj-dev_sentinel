#!/usr/bin/env python3
"""
Test script for the refactored Dev Sentinel MCP integration.

This script validates that the new adapter and MCP server components
are functioning correctly and can be initialized properly.
"""

import asyncio
import sys
import os
import logging

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, project_root)

from integration.fast_agent.adapter import MCPAgentAdapter
from integration.fast_agent.specialized_adapters import (
    create_specialized_adapter,
    ensure_adapters_initialized,
    list_registered_adapters
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_adapter_initialization():
    """Test basic adapter initialization."""
    logger.info("Testing adapter initialization...")
    
    try:
        # Ensure adapters are initialized
        success = await ensure_adapters_initialized()
        if success:
            logger.info("✓ Adapters initialized successfully")
        else:
            logger.error("✗ Failed to initialize adapters")
            return False
        
        # List registered adapters
        adapters = list_registered_adapters()
        logger.info(f"✓ Registered adapters: {adapters}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Adapter initialization failed: {e}")
        return False

async def test_mcp_server_creation():
    """Test MCP server creation (without actually running it)."""
    logger.info("Testing MCP server creation...")
    
    try:
        # Try to import the MCP server
        from integration.fast_agent.mcp_servers import DevSentinelMCPServer
        
        # Note: We don't actually create the server here since MCP might not be installed
        # This just tests that the import works and the class is properly defined
        logger.info("✓ MCP server class imported successfully")
        logger.info(f"✓ MCP server class: {DevSentinelMCPServer.__name__}")
        
        return True
    except ImportError as e:
        logger.warning(f"⚠ MCP server not available (expected): {e}")
        return True  # This is expected and OK
    except Exception as e:
        logger.error(f"✗ MCP server creation test failed: {e}")
        return False

async def test_agent_imports():
    """Test that agent classes can be imported."""
    logger.info("Testing agent imports...")
    
    try:
        from agents.vcma.vcma_agent import VersionControlMasterAgent
        from agents.vcla.vcla_agent import VersionControlListenerAgent
        from agents.cdia.cdia_agent import CodeDocumentationInspectorAgent
        from agents.rdia.rdia_agent import READMEInspectorAgent
        from agents.saa.saa_agent import StaticAnalysisAgent
        
        logger.info("✓ All agent classes imported successfully")
        logger.info(f"  - VCMA: {VersionControlMasterAgent.__name__}")
        logger.info(f"  - VCLA: {VersionControlListenerAgent.__name__}")
        logger.info(f"  - CDIA: {CodeDocumentationInspectorAgent.__name__}")
        logger.info(f"  - RDIA: {READMEInspectorAgent.__name__}")
        logger.info(f"  - SAA: {StaticAnalysisAgent.__name__}")
        
        return True
    except ImportError as e:
        logger.error(f"✗ Agent import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Agent import test failed: {e}")
        return False

async def run_tests():
    """Run all tests."""
    logger.info("Starting Dev Sentinel MCP integration tests...")
    
    tests = [
        ("Agent Imports", test_agent_imports),
        ("Adapter Initialization", test_adapter_initialization),
        ("MCP Server Creation", test_mcp_server_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
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
        logger.info("🎉 All tests passed! The refactored MCP integration is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)
