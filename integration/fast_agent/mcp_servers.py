"""
MCP Server implementations for Dev Sentinel.

This module provides Model Context Protocol (MCP) server implementations
that can be used with fast-agent to execute Dev Sentinel commands.
"""

import os
import sys
import json
import logging
import asyncio
import copy
from typing import Dict, List, Any, Optional, Union, Callable, AsyncIterator
import uvicorn

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Also add parent directory to handle imports from sibling modules
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Use the correct imports from the current MCP SDK
    from mcp.server.fastmcp import FastMCP
    from mcp.types import Result
except ImportError:
    raise ImportError("mcp package is not installed. Run 'pip install mcp'")

# Import Dev Sentinel components
from integration.force.master_agent import ForceCommandProcessor
from integration.fast_agent.async_initialization import get_async_initializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("dev_sentinel_mcp")

class DevSentinelCommandServer:
    """
    MCP server implementation for executing Dev Sentinel commands.
    
    This server exposes a command execution capability that takes JSON
    commands and executes them using Dev Sentinel's FORCE architecture.
    """

    def __init__(self):
        """Initialize the Dev Sentinel command server."""
        self.mcp = FastMCP(name="dev_sentinel_command")
        self.force_processor = None
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        
        # Register tools with the MCP instance
        self.register_tools()
        
    def register_tools(self):
        """Register all tools with the MCP instance."""
        
        @self.mcp.tool()
        async def execute_command(command: str, args: Dict[str, Any]) -> Result:
            """
            Execute a Dev Sentinel command.
            
            Args:
                command: Command type to execute (e.g., VIC, CODE, VCS)
                args: Command arguments as a JSON object
                
            Returns:
                Result object containing command execution results
            """
            return await self._execute_command(command, args)
        
        @self.mcp.tool()
        async def stream_command(command: str, args: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
            """
            Execute a Dev Sentinel command and stream the results.
            
            Args:
                command: Command type to execute (e.g., VIC, CODE, VCS)
                args: Command arguments as a JSON object
                
            Returns:
                Stream of command execution results as they become available
            """
            async for frame in self._stream_command(command, args):
                yield frame
        
        @self.mcp.tool()
        async def get_commands() -> Result:
            """
            Get the list of available Dev Sentinel commands.
            
            Returns:
                Result object containing list of available commands and their descriptions
            """
            return await self._get_commands()
        
    async def ensure_initialized(self) -> None:
        """Ensure the FORCE command processor is initialized."""
        if self._initialized:
            return
            
        async with self._initialization_lock:
            if self._initialized:
                return
                
            try:
                # Initialize fast-agent
                initializer = get_async_initializer()
                await initializer.initialize()
                
                # Initialize FORCE command processor
                from integration.force.master_agent import ForceCommandProcessor
                
                self.force_processor = ForceCommandProcessor()
                await self.force_processor.initialize()
                
                # Also ensure fast-agent is initialized
                await self.force_processor.ensure_fast_agent_initialized()
                
                self._initialized = True
                logger.info("Dev Sentinel Command Server initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Dev Sentinel Command Server: {e}")
                raise

    async def _map_command(self, command: Dict[str, Any]) -> str:
        """
        Map a JSON command to YUNG command syntax.
        
        Args:
            command: Command dictionary with 'command' and 'args' fields
            
        Returns:
            YUNG command string
        """
        # Import command mapper
        from integration.fast_agent.mcp_command_server import CommandMapperService
        
        # Map the command
        cmd_type = command.get("command", "").upper()
        cmd_args = command.get("args", {})
        
        return CommandMapperService.map_to_yung(cmd_type, cmd_args)
        
    async def _map_result(self, yung_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map YUNG command result to API response format.
        
        Args:
            yung_result: Result from FORCE command execution
            
        Returns:
            Mapped result in API format
        """
        # Import command mapper
        from integration.fast_agent.mcp_command_server import CommandMapperService
        
        # Map the result
        return CommandMapperService.map_from_yung_result(yung_result)

    async def _execute_command(self, command: str, args: Dict[str, Any]) -> Result:
        """
        Execute a Dev Sentinel command.
        
        Args:
            command: Command type to execute (e.g., VIC, CODE, VCS)
            args: Command arguments as a JSON object
            
        Returns:
            Result object containing command execution results
        """
        try:
            # Ensure initialization
            await self.ensure_initialized()
            
            # Map to YUNG command
            yung_command = await self._map_command({"command": command, "args": args})
            
            # Execute command
            result = await self.force_processor.process_command(yung_command)
            
            # Map result to API format
            mapped_result = await self._map_result(result)
            
            return Result(status="success", result=mapped_result)
            
        except Exception as e:
            logger.exception(f"Error executing command: {e}")
            return Result(status="error", result={"error": str(e)})

    async def _stream_command(self, command: str, args: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a Dev Sentinel command and stream the results.
        
        Args:
            command: Command type to execute (e.g., VIC, CODE, VCS)
            args: Command arguments as a JSON object
            
        Returns:
            Stream of command execution results
        """
        try:
            # Ensure initialization
            await self.ensure_initialized()
            
            # Map to YUNG command
            yung_command = await self._map_command({"command": command, "args": args})
            
            # Yield initial response
            yield {
                "is_final": False,
                "content": {"status": "started", "command": yung_command}
            }
            
            # Execute command
            result = await self.force_processor.process_command(yung_command)
            
            # Map result to API format
            mapped_result = await self._map_result(result)
            
            # Yield final result
            yield {
                "is_final": True,
                "content": mapped_result
            }
            
        except Exception as e:
            logger.exception(f"Error streaming command: {e}")
            yield {
                "is_final": True,
                "content": {"error": str(e), "status": "error"}
            }

    async def _get_commands(self) -> Result:
        """
        Get the list of available Dev Sentinel commands.
        
        Returns:
            Result object containing list of available commands
        """
        try:
            commands = [
                {
                    "command": "VIC",
                    "description": "Validate Integrity of Code/Documentation",
                    "args": {
                        "scope": "Validation scope (ALL, LAST, DOCS, FILE)",
                        "file": "Optional file path when scope is FILE"
                    }
                },
                {
                    "command": "CODE",
                    "description": "Perform code operations",
                    "args": {
                        "tier": "Code tier (BACKEND, FRONTEND, ALL)",
                        "actions": "Actions to perform (IMPL, TEST, REVIEW)",
                        "stage": "Optional stage identifier"
                    }
                },
                {
                    "command": "VCS",
                    "description": "Perform version control operations",
                    "args": {
                        "action": "VCS action (COMMIT, BRANCH, MERGE, etc.)",
                        "target": "Target for the operation",
                        "options": "Additional options for the operation"
                    }
                },
                {
                    "command": "INFRA",
                    "description": "Manage infrastructure",
                    "args": {
                        "action": "Infrastructure action",
                        "target": "Target resource",
                        "options": "Additional options"
                    }
                },
                {
                    "command": "TEST",
                    "description": "Run tests",
                    "args": {
                        "action": "Test action (RUN, REVIEW, COVERAGE)",
                        "target": "Target tests",
                        "options": "Additional options"
                    }
                },
                {
                    "command": "FAST",
                    "description": "Fast-agent operations",
                    "args": {
                        "action": "Fast-agent action (WORKFLOW, SERVER, MODEL)",
                        "target": "Target for action (RUN, RESTART, SWITCH)",
                        "options": "Name of workflow, server, or model"
                    }
                },
                {
                    "command": "DIAGRAM",
                    "description": "Generate diagrams",
                    "args": {
                        "type": "Diagram type (ARCH, FLOW, COMP, TERM, EXTRACT)",
                        "source": "Source data (FILE=path, FORCE, YUNG, AGENT)",
                        "format": "Output format (svg, png, pdf)"
                    }
                },
                {
                    "command": "MAN",
                    "description": "Display YUNG command manual",
                    "args": {}
                }
            ]
            
            return Result(status="success", result=commands)
            
        except Exception as e:
            logger.exception(f"Error getting commands: {e}")
            return Result(status="error", result={"error": str(e)})

    async def start(self, host: str = "0.0.0.0", port: int = 8090):
        """Start the MCP server."""
        config = uvicorn.Config(
            app=self.mcp,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

class FileSystemMCPServer:
    """File system operations MCP server implementation."""
    def __init__(self):
        """Initialize the File System MCP server."""
        self.mcp = FastMCP(name="filesystem")
        # Register tools here
        
    async def start(self, host: str = "0.0.0.0", port: int = 8091):
        """Start the MCP server."""
        config = uvicorn.Config(
            app=self.mcp,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

class VersionControlMCPServer:
    """Version control operations MCP server implementation."""
    def __init__(self):
        """Initialize the Version Control MCP server."""
        self.mcp = FastMCP(name="vcs")
        # Register tools here
        
    async def start(self, host: str = "0.0.0.0", port: int = 8092):
        """Start the MCP server."""
        config = uvicorn.Config(
            app=self.mcp,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

class DocumentationInspectorMCPServer:
    """Documentation inspection operations MCP server implementation."""
    def __init__(self):
        """Initialize the Documentation Inspector MCP server."""
        self.mcp = FastMCP(name="documentation")
        # Register tools here
        
    async def start(self, host: str = "0.0.0.0", port: int = 8093):
        """Start the MCP server."""
        config = uvicorn.Config(
            app=self.mcp,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

class CodeAnalysisMCPServer:
    """Code analysis operations MCP server implementation."""
    def __init__(self):
        """Initialize the Code Analysis MCP server."""
        self.mcp = FastMCP(name="code_analysis")
        # Register tools here
        
    async def start(self, host: str = "0.0.0.0", port: int = 8094):
        """Start the MCP server."""
        config = uvicorn.Config(
            app=self.mcp,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

# Register all MCP server classes
MCP_SERVER_CLASSES = {
    "dev_sentinel": DevSentinelCommandServer,
    "filesystem": FileSystemMCPServer,
    "vcs": VersionControlMCPServer,
    "documentation": DocumentationInspectorMCPServer,
    "code_analysis": CodeAnalysisMCPServer,
}

def get_server(server_type: str):
    """
    Get an instance of an MCP server by type.
    
    Args:
        server_type: Type of MCP server to get
        
    Returns:
        MCP server instance
    
    Raises:
        ValueError: If server_type is not supported
    """
    server_class = MCP_SERVER_CLASSES.get(server_type.lower())
    if server_class is None:
        raise ValueError(f"Unsupported MCP server type: {server_type}")
        
    return server_class()

async def start_server(server_type: str, host: str = "0.0.0.0", port: int = None) -> None:
    """
    Start an MCP server.
    
    Args:
        server_type: Type of MCP server to start
        host: Host to bind to
        port: Port to listen on (default is based on server type)
    """
    try:
        # Get server instance
        server = get_server(server_type)
        
        # Determine port if not provided
        if port is None:
            # Default port mappings
            port_mappings = {
                "dev_sentinel": 8090,
                "filesystem": 8091,
                "vcs": 8092,
                "documentation": 8093,
                "code_analysis": 8094
            }
            port = port_mappings.get(server_type.lower(), 8090)
        
        # Start server
        logger.info(f"Starting {server_type} MCP server on {host}:{port}")
        await server.start(host=host, port=port)
        
    except Exception as e:
        logger.exception(f"Failed to start {server_type} MCP server: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start an MCP server for Dev Sentinel")
    parser.add_argument("server_type", help="Type of MCP server to start")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to listen on")
    args = parser.parse_args()
    
    # Start server
    asyncio.run(start_server(args.server_type, args.host, args.port))