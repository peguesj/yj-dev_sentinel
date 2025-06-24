#!/usr/bin/env python
"""
Dev Sentinel MCP Server Launcher

This script launches the Dev Sentinel MCP server which provides a JSON-based 
interface to the Dev Sentinel FORCE architecture through fast-agent integration.

Usage:
  python dev_sentinel_server.py [--http-port PORT] [--mcp-port PORT] [--host HOST] [--verbose]
"""

import os
import sys
import json
import argparse
import asyncio
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple
import signal
import time
import traceback

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Setup console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Get logger for this module
logger = logging.getLogger("dev_sentinel_server")

def check_dependencies():
    """
    Check if all required dependencies are installed.
    Returns a tuple of (success, missing_deps)
    """
    required_deps = {
        "httpx": "HTTP client library for API server",
        "uvicorn": "ASGI server for FastAPI",
        "fastapi": "Web framework for API server",
        "pydantic": "Data validation library",
        "mcp_agent": "Fast agent framework (fast-agent-mcp)",
        "mcp": "MCP server toolkit"
    }
    
    missing_deps = {}
    
    for dep, desc in required_deps.items():
        try:
            module = __import__(dep)
            logger.debug(f"Dependency check: {dep} - OK")
        except ImportError:
            logger.debug(f"Dependency check: {dep} - MISSING")
            missing_deps[dep] = desc
    
    return len(missing_deps) == 0, missing_deps

def setup_file_logging(log_dir: str = None, log_level: int = logging.INFO):
    """
    Set up file logging in addition to console logging.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level for file handler
    """
    if log_dir is None:
        log_dir = os.path.join(os.getcwd(), "logs")
    
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(log_dir, f"dev_sentinel_server_{timestamp}.log")
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Add file handler to root logger
    root_logger.addHandler(file_handler)
    
    logger.info(f"Logging to file: {log_file}")
    return log_file

# Add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    logger.debug(f"Added project root to sys.path: {project_root}")

# Also add the current directory's parent to handle imports from sibling modules
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    logger.debug(f"Added parent directory to sys.path: {parent_dir}")

# Check dependencies before trying to import Dev Sentinel components
deps_ok, missing_deps = check_dependencies()
if not deps_ok:
    logger.error("Missing required dependencies:")
    for dep, desc in missing_deps.items():
        logger.error(f"  - {dep}: {desc}")
    logger.error("Please install missing dependencies with: pip install " + " ".join(missing_deps.keys()))
    sys.exit(1)

# Import Dev Sentinel components
try:
    logger.info("Importing Dev Sentinel components...")
    # First try absolute imports (more reliable)
    try:
        from integration.fast_agent.mcp_command_server import start_server as start_http_server
        from integration.fast_agent.mcp_servers import start_server as start_mcp_server
        from integration.fast_agent.async_initialization import initialize_fast_agent
        logger.debug("Using absolute imports")
    except ImportError as e:
        logger.warning(f"Absolute imports failed: {e}, trying relative imports")
        # Fall back to relative imports
        from mcp_command_server import start_server as start_http_server
        from mcp_servers import start_server as start_mcp_server
        from async_initialization import initialize_fast_agent
        logger.debug("Using relative imports")
    logger.info("Successfully imported Dev Sentinel components")
except ImportError as e:
    logger.error(f"Failed to import required components: {e}")
    logger.error("Make sure you're running from the project root directory")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Python path: {sys.path}")
    logger.error("Traceback:")
    traceback.print_exc()
    sys.exit(1)

class ServerManager:
    """Manages the lifecycle of HTTP and MCP servers."""
    
    def __init__(
        self, 
        http_port: int = 8000, 
        mcp_port: int = 8090, 
        host: str = "0.0.0.0",
        verbose: bool = False
    ):
        """
        Initialize the server manager.
        
        Args:
            http_port: Port for the HTTP API server
            mcp_port: Port for the MCP server
            host: Host to bind to
            verbose: Enable verbose logging
        """
        self.http_port = http_port
        self.mcp_port = mcp_port
        self.host = host
        self.http_task = None
        self.mcp_task = None
        self.is_running = False
        self.stop_event = asyncio.Event()
        
        # Set logging level based on verbose flag
        if verbose:
            logger.info("Enabling verbose logging")
            root_logger.setLevel(logging.DEBUG)
            for handler in root_logger.handlers:
                handler.setLevel(logging.DEBUG)
        
    async def initialize(self):
        """Initialize fast-agent and other required components."""
        try:
            logger.info("Initializing Dev Sentinel MCP Server...")
            
            # Log environment information
            logger.debug(f"Python version: {sys.version}")
            logger.debug(f"Working directory: {os.getcwd()}")
            logger.debug(f"System platform: {sys.platform}")
            
            # Initialize fast-agent
            logger.info("Starting fast-agent initialization...")
            init_result = await initialize_fast_agent()
            
            if init_result.get("status") != "success":
                logger.error(f"Fast-agent initialization failed: {init_result.get('message', 'Unknown error')}")
                logger.error(f"Initialization details: {json.dumps(init_result, indent=2)}")
                return False
                
            logger.info("Fast-agent initialization complete")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to initialize: {e}")
            logger.error("Detailed traceback:")
            traceback.print_exc()
            return False
            
    async def start(self):
        """Start both HTTP and MCP servers."""
        if self.is_running:
            logger.warning("Servers are already running")
            return
            
        # Initialize components
        logger.info("Starting initialization process...")
        if not await self.initialize():
            logger.error("Failed to initialize required components")
            return
            
        # Set up signals for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)
            
        try:
            # Start HTTP server
            logger.info(f"Starting HTTP API server on {self.host}:{self.http_port}")
            self.http_task = asyncio.create_task(
                self._start_http_server()
            )
            
            # Start MCP server
            logger.info(f"Starting MCP server on {self.host}:{self.mcp_port}")
            self.mcp_task = asyncio.create_task(
                self._start_mcp_server()
            )
            
            self.is_running = True
            logger.info("Both servers started successfully")
            
            # Wait for stop signal
            await self.stop_event.wait()
            
        except Exception as e:
            logger.exception(f"Error starting servers: {e}")
            logger.error("Detailed traceback:")
            traceback.print_exc()
            
        finally:
            # Clean up
            await self.stop()
    
    async def stop(self):
        """Stop all running servers."""
        logger.info("Stopping servers...")
        
        # Cancel tasks
        if self.http_task:
            logger.debug("Canceling HTTP server task")
            self.http_task.cancel()
            try:
                await self.http_task
                logger.debug("HTTP server task canceled successfully")
            except asyncio.CancelledError:
                logger.debug("HTTP server task cancellation completed")
            except Exception as e:
                logger.error(f"Error during HTTP server task cancellation: {e}")
            
        if self.mcp_task:
            logger.debug("Canceling MCP server task")
            self.mcp_task.cancel()
            try:
                await self.mcp_task
                logger.debug("MCP server task canceled successfully")
            except asyncio.CancelledError:
                logger.debug("MCP server task cancellation completed")
            except Exception as e:
                logger.error(f"Error during MCP server task cancellation: {e}")
                
        self.is_running = False
        logger.info("All servers stopped")
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop_event.set()
        
    async def _start_http_server(self):
        """Start the HTTP API server in a separate process."""
        try:
            # Import server module
            logger.debug("Importing HTTP server components...")
            # Use both relative and absolute imports for robustness
            try:
                # First try relative imports
                from .mcp_command_server import FastMCP as app
                logger.debug("Using relative imports for HTTP server")
            except ImportError:
                # Fall back to absolute imports
                from integration.fast_agent.mcp_command_server import FastMCP as app
                logger.debug("Using absolute imports for HTTP server")
            
            # Start uvicorn server
            import uvicorn
            logger.debug("Configuring uvicorn server...")
            config = uvicorn.Config(
                self, 
                host=self.host, 
                port=self.http_port,
                log_level="debug" if root_logger.level <= logging.DEBUG else "info"
            )
            server = uvicorn.Server(config)
            logger.debug("Starting uvicorn server...")
            await server.serve()
            
        except ImportError as e:
            logger.error(f"Failed to import HTTP server components: {e}")
            logger.error("Make sure all dependencies are installed")
            self.stop_event.set()
        except Exception as e:
            logger.exception(f"Error in HTTP server: {e}")
            logger.error("Detailed traceback:")
            traceback.print_exc()
            self.stop_event.set()
            
    async def _start_mcp_server(self):
        """Start the MCP server."""
        try:
            # Start MCP server
            logger.debug("Starting MCP server...")
            # Import the correct start_server function
            from integration.fast_agent.mcp_servers import start_server
            
            # Use the run_async method to avoid creating a new event loop
            await start_server("dev_sentinel", self.host, self.mcp_port)
            
        except ImportError as e:
            logger.error(f"Failed to import MCP server components: {e}")
            logger.error("Make sure all dependencies are installed")
            self.stop_event.set()
        except Exception as e:
            logger.exception(f"Error in MCP server: {e}")
            logger.error("Detailed traceback:")
            traceback.print_exc()
            self.stop_event.set()

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Dev Sentinel MCP Server Launcher")
    parser.add_argument("--http-port", type=int, default=8000, help="Port for HTTP API server")
    parser.add_argument("--mcp-port", type=int, default=8090, help="Port for MCP server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--log-dir", help="Directory for log files")
    args = parser.parse_args()
    
    # Setup file logging if requested
    if args.log_dir:
        log_file = setup_file_logging(args.log_dir, 
                                    log_level=logging.DEBUG if args.verbose else logging.INFO)
    
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                 DEV SENTINEL MCP SERVER                   ║
    ╚═══════════════════════════════════════════════════════════╝
    
    HTTP API Server: http://{host}:{http_port}/api/commands
    MCP Server:      {host}:{mcp_port}
    
    Use the JSON-based API to execute Dev Sentinel commands through FORCE.
    
    Press Ctrl+C to stop the server.
    """
    print(banner.format(host="localhost" if args.host == "0.0.0.0" else args.host, 
                      http_port=args.http_port, 
                      mcp_port=args.mcp_port))
    
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
        logger.critical("Detailed traceback:")
        traceback.print_exc()
        sys.exit(1)