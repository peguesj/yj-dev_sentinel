#!/usr/bin/env python3
"""
Force MCP Server Startup Script with Validation
Demonstrates the integrated validation and fix system that runs before server startup.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the enhanced MCP server
from integration.fast_agent.force_mcp_server import ForceMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("force_mcp_startup")


async def main():
    """Main startup function with validation."""
    logger.info("🚀 Starting Dev Sentinel Force MCP Server with integrated validation...")
    
    try:
        # Create server with auto-fix enabled by default
        server = ForceMCPServer(force_directory=".force", auto_fix=True)
        
        # The server will automatically run validation and fixes during initialization
        logger.info("🔧 Server will run validation and auto-fix during initialization...")
        
        # Start the server (validation happens in _initialize_force_engine)
        await server.run()
        
    except RuntimeError as e:
        logger.error(f"❌ Failed to start MCP server: {e}")
        logger.info("💡 Try running with manual fix: python force/tools/force_component_fix_system.py --force-root .force --fix")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
