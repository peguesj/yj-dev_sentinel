#!/usr/bin/env python3
"""
Dev Sentinel MCP HTTP server entry point.

This module provides the CLI entry point for the Dev Sentinel MCP server using HTTP transport.
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add the project root to the Python path to ensure proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integration.fast_agent.dev_sentinel_server import main as dev_sentinel_main
import logging

logger = logging.getLogger(__name__)


def main():
    """Entry point for dev-sentinel-http CLI command."""
    parser = argparse.ArgumentParser(description="Dev Sentinel HTTP Server")
    parser.add_argument(
        "--http-port", 
        type=int, 
        default=8000, 
        help="Port for HTTP API server (default: 8000)"
    )
    parser.add_argument(
        "--mcp-port", 
        type=int, 
        default=8090, 
        help="Port for MCP server (default: 8090)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--log-dir", 
        help="Directory for log files"
    )
    
    args = parser.parse_args()
    
    # Set up arguments for the dev sentinel server
    sys.argv = [
        sys.argv[0],
        "--http-port", str(args.http_port),
        "--mcp-port", str(args.mcp_port),
        "--host", args.host
    ]
    
    if args.verbose:
        sys.argv.extend(["--verbose"])
    
    if args.log_dir:
        sys.argv.extend(["--log-dir", args.log_dir])
    
    try:
        asyncio.run(dev_sentinel_main())
    except KeyboardInterrupt:
        print("\n🛑 Dev Sentinel HTTP server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Dev Sentinel HTTP server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
