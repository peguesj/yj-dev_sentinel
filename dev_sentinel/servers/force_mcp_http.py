#!/usr/bin/env python3
"""
Force MCP HTTP server entry point.

This module provides the CLI entry point for the Force MCP server using HTTP transport.
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add the project root to the Python path to ensure proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integration.fast_agent.force_mcp_server import ForceMCPServer
import logging

logger = logging.getLogger(__name__)


async def run_http_server(port: int = 8080, host: str = "0.0.0.0", **kwargs):
    """Run the Force MCP server over HTTP."""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
        
        app = FastAPI(
            title="Force MCP HTTP Server",
            description="HTTP interface for Force MCP server",
            version="0.3.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize Force MCP server
        force_server = ForceMCPServer(**kwargs)
        
        @app.get("/")
        async def root():
            """Root endpoint."""
            return {"message": "Force MCP HTTP Server", "version": "0.3.0"}
        
        @app.get("/health")
        async def health():
            """Health check endpoint."""
            return {"status": "healthy", "server": "force-mcp-http"}
        
        @app.post("/mcp/call")
        async def mcp_call(request: dict):
            """MCP call endpoint."""
            # This is a simplified implementation
            # In a full implementation, you'd properly handle MCP protocol over HTTP
            return {"error": "MCP over HTTP not fully implemented yet"}
        
        logger.info(f"🚀 Starting Force MCP HTTP server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
        
    except ImportError as e:
        logger.error(f"Missing dependencies for HTTP server: {e}")
        logger.error("Please install: pip install fastapi uvicorn")
        sys.exit(1)


def main():
    """Entry point for force-mcp-http CLI command."""
    parser = argparse.ArgumentParser(description="Force MCP HTTP Server")
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--force-dir",
        type=str,
        help="Path to Force directory (default: auto-detect)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--no-auto-fix",
        action="store_true",
        help="Disable automatic fixing of Force components at startup"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Enable auto-fix unless explicitly disabled
    auto_fix = not args.no_auto_fix
    
    try:
        asyncio.run(run_http_server(
            port=args.port,
            host=args.host,
            force_directory=args.force_dir,
            auto_fix=auto_fix
        ))
    except KeyboardInterrupt:
        print("\n🛑 Force MCP HTTP server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Force MCP HTTP server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
