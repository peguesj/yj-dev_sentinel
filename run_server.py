#!/usr/local/bin/python
"""
Dev Sentinel Server Runner

This script properly launches the Dev Sentinel MCP server with correct path setup.
"""

import os
import sys
import argparse
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("dev_sentinel_runner")

# Import path setup to ensure all modules can be properly imported
try:
    import path_setup
    logger.debug(f"Set up Python path: {path_setup.project_root}")
except ImportError:
    logger.error("Failed to import path_setup module")
    sys.exit(1)

# Now we can safely import Dev Sentinel components
try:
    from integration.fast_agent.dev_sentinel_server import ServerManager
except ImportError as e:
    logger.error(f"Failed to import Dev Sentinel components: {e}")
    logger.error("Make sure you have all required dependencies installed")
    sys.exit(1)

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Dev Sentinel MCP Server Launcher")
    parser.add_argument("--http-port", type=int, default=8000, help="Port for HTTP API server")
    parser.add_argument("--mcp-port", type=int, default=8090, help="Port for MCP server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--log-dir", help="Directory for log files")
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Create and start server manager
    manager = ServerManager(
        http_port=args.http_port,
        mcp_port=args.mcp_port,
        host=args.host,
        verbose=args.verbose
    )
    
    await manager.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by keyboard interrupt")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)