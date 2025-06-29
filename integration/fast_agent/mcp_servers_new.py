"""
Modern MCP Server implementations for Dev Sentinel.

This module provides Model Context Protocol (MCP) server implementations
that follow the latest MCP standards and best practices for integration
with VS Code and other MCP-compatible tools.
"""

import os
import sys
import json
import logging
import asyncio
import traceback
from typing import Dict, List, Any, Optional, Sequence
from contextlib import asynccontextmanager

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# MCP imports - graceful fallback if not available
try:
    from mcp import types
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"MCP not available: {e}")
    MCP_AVAILABLE = False
    # Create minimal type stubs for development
    class types:
        class Tool:
            def __init__(self, name, description, inputSchema): pass
        class TextContent:
            def __init__(self, type, text): pass
    class Server:
        def __init__(self, name): pass
        def list_tools(self): pass
        def call_tool(self): pass

# Dev Sentinel imports - graceful fallback
try:
    from integration.force.master_agent import ForceCommandProcessor
    from integration.fast_agent.async_initialization import get_async_initializer
    FORCE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"FORCE components not available: {e}")
    FORCE_AVAILABLE = False
    ForceCommandProcessor = None
    get_async_initializer = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("dev_sentinel_mcp")

class DevSentinelMCPServer:
    """
    Modern MCP server implementation for Dev Sentinel.
    
    Provides a comprehensive interface to Dev Sentinel functionality through
    the Model Context Protocol, enabling integration with VS Code and other
    MCP-compatible tools.
    """

    def __init__(self):
        """Initialize the Dev Sentinel MCP server."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP package not available - install with 'pip install mcp'")
            
        self.server = Server("dev-sentinel")
        self.force_processor = None
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        
        # Set up server capabilities and handlers
        self._setup_server()
        
    def _setup_server(self):
        """Set up server capabilities and tool handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="execute_yung_command",
                    description="Execute a Dev Sentinel YUNG command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "YUNG command to execute (e.g., '$VIC DOCS', '$CODE TIER=BACKEND IMPL')"
                            }
                        },
                        "required": ["command"]
                    }
                ),
                types.Tool(
                    name="validate_documentation",
                    description="Validate project documentation integrity using VIC command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "enum": ["ALL", "LAST", "DOCS"],
                                "description": "Validation scope",
                                "default": "DOCS"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Specific file path for FILE scope"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="analyze_code",
                    description="Analyze code using CODE command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tier": {
                                "type": "string",
                                "enum": ["FRONTEND", "BACKEND", "ALL"],
                                "description": "Code tier to analyze",
                                "default": "ALL"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["IMPL", "COMMENT", "DOCS", "TEST"],
                                "description": "Analysis action to perform",
                                "default": "IMPL"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_repository_status",
                    description="Get version control repository status using VCS command",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="commit_changes",
                    description="Commit changes to version control",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Commit message"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                types.Tool(
                    name="generate_diagram",
                    description="Generate system diagrams using DIAGRAM command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["ARCH", "FLOW", "COMP", "FORCE"],
                                "description": "Diagram type to generate",
                                "default": "ARCH"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["png", "svg", "pdf"],
                                "description": "Output format",
                                "default": "svg"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_yung_manual",
                    description="Get the YUNG command manual",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls."""
            try:
                await self.ensure_initialized()
                
                if name == "execute_yung_command":
                    command = arguments.get("command", "")
                    result = await self._execute_yung_command(command)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "validate_documentation":
                    scope = arguments.get("scope", "DOCS")
                    file_path = arguments.get("file_path")
                    result = await self._validate_documentation(scope, file_path)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "analyze_code":
                    tier = arguments.get("tier", "ALL")
                    action = arguments.get("action", "IMPL")
                    result = await self._analyze_code(tier, action)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "get_repository_status":
                    result = await self._get_repository_status()
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "commit_changes":
                    message = arguments.get("message", "")
                    result = await self._commit_changes(message)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "generate_diagram":
                    diagram_type = arguments.get("type", "ARCH")
                    format_type = arguments.get("format", "svg")
                    result = await self._generate_diagram(diagram_type, format_type)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "get_yung_manual":
                    result = await self._get_yung_manual()
                    return [types.TextContent(type="text", text=result)]
                
                else:
                    return [types.TextContent(
                        type="text", 
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                traceback.print_exc()
                return [types.TextContent(
                    type="text", 
                    text=f"Error: {str(e)}"
                )]
    
    async def ensure_initialized(self) -> None:
        """Ensure the server is properly initialized."""
        if self._initialized:
            return
            
        async with self._initialization_lock:
            if self._initialized:
                return
                
            try:
                # Initialize FORCE command processor if available
                if FORCE_AVAILABLE and ForceCommandProcessor:
                    self.force_processor = ForceCommandProcessor()
                    if hasattr(self.force_processor, 'initialize'):
                        await self.force_processor.initialize()
                    logger.info("FORCE processor initialized")
                else:
                    logger.warning("FORCE processor not available - using fallback processing")
                
                self._initialized = True
                logger.info("Dev Sentinel MCP Server initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Dev Sentinel MCP Server: {e}")
                raise

    async def _execute_yung_command(self, command: str) -> Dict[str, Any]:
        """Execute a YUNG command through the FORCE processor."""
        try:
            if not command.startswith('$'):
                command = f"${command}"
            
            if self.force_processor and hasattr(self.force_processor, 'process_command'):
                result = await self.force_processor.process_command(command)
            else:
                # Fallback processing
                result = await self._fallback_command_processing(command)
            
            return {
                "status": "success",
                "command": command,
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error executing YUNG command '{command}': {e}")
            return {
                "status": "error",
                "command": command,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

    async def _validate_documentation(self, scope: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Validate documentation using VIC command."""
        if file_path:
            command = f"$VIC FILE={file_path}"
        else:
            command = f"$VIC {scope}"
        
        return await self._execute_yung_command(command)

    async def _analyze_code(self, tier: str, action: str) -> Dict[str, Any]:
        """Analyze code using CODE command."""
        command = f"$CODE TIER={tier} {action}"
        return await self._execute_yung_command(command)

    async def _get_repository_status(self) -> Dict[str, Any]:
        """Get repository status using VCS command."""
        command = "$VCS STATUS"
        return await self._execute_yung_command(command)

    async def _commit_changes(self, message: str) -> Dict[str, Any]:
        """Commit changes using VCS command."""
        command = f'$VCS COMMIT "{message}"'
        return await self._execute_yung_command(command)

    async def _generate_diagram(self, diagram_type: str, format_type: str) -> Dict[str, Any]:
        """Generate diagrams using DIAGRAM command."""
        command = f"$DIAGRAM {diagram_type} FORMAT={format_type}"
        return await self._execute_yung_command(command)

    async def _get_yung_manual(self) -> str:
        """Get the YUNG command manual."""
        manual = """
# YUNG: YES Ultimate Net Good - Command Reference

## Primary Commands

### $VIC [SCOPE]
Validate integrity of codebase or documentation.
- ALL: Validate full project structure
- LAST: Validate last affected components  
- DOCS: Validate only documentation assets
- FILE=<filepath>: Validate a specific file

### $CODE [SCOPE] [ACTIONS] [STAGE]
Code generation, patching, or updates.
- TIER=FRONTEND/BACKEND/ALL: Target application tier
- Actions: IMPL, COMMENT, DOCS, TEST, PKG=<format>
- Stage: Branch or patch label (e.g., Stage F-1)

### $VCS [ACTION] [OPTIONS]
Version control operations.
- STATUS: Get repository status
- COMMIT "message": Commit changes
- BRANCH <name>: Create branch
- MERGE <source> <target>: Merge branches

### $DIAGRAM [TYPE] [SOURCE] [FORMAT=<format>]
Generate diagrams.
- Types: ARCH, FLOW, COMP, TERM, EXTRACT
- Sources: FILE=<path>, FORCE, YUNG, AGENT
- Formats: png, svg, pdf

### $INFRA [SERVICE] [ACTION] [OPTIONS]
Infrastructure operations.

### $TEST [TYPE] [SCOPE] [OPTIONS]  
Testing operations.

### $FAST [ACTION] [OPTIONS] [MODEL]
Fast-agent integration operations.

## Examples
$VIC DOCS
$CODE TIER=BACKEND IMPL
$VCS COMMIT "fix: update documentation"
$DIAGRAM ARCH FORMAT=svg
"""
        return manual

    async def _fallback_command_processing(self, command: str) -> Dict[str, Any]:
        """Fallback command processing when FORCE processor is not available."""
        logger.warning(f"Using fallback processing for command: {command}")
        
        # Parse basic command structure
        if command.startswith("$"):
            parts = command[1:].split()
            cmd_type = parts[0] if parts else "UNKNOWN"
            
            return {
                "command_type": cmd_type,
                "command": command,
                "status": "processed_fallback",
                "message": f"Command {cmd_type} processed using fallback method - full functionality requires FORCE processor",
                "available_commands": ["VIC", "CODE", "VCS", "DIAGRAM", "INFRA", "TEST", "FAST"]
            }
        
        return {
            "command": command,
            "status": "unprocessed",
            "message": "Command format not recognized - commands should start with $"
        }

async def create_server() -> DevSentinelMCPServer:
    """Create and return a new Dev Sentinel MCP server instance."""
    server = DevSentinelMCPServer()
    await server.ensure_initialized()
    return server

async def run_stdio_server():
    """Run the MCP server using stdio transport."""
    if not MCP_AVAILABLE:
        logger.error("MCP package not available - install with 'pip install mcp'")
        return
        
    server = DevSentinelMCPServer()
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dev-sentinel",
                server_version="0.2.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

# Legacy compatibility functions
async def start_server(host: str = "localhost", port: int = 8090):
    """Start the Dev Sentinel MCP server (legacy compatibility)."""
    await run_stdio_server()

async def run_async():
    """Run the MCP server (legacy compatibility)."""
    await run_stdio_server()

if __name__ == "__main__":
    logger.info("Starting Dev Sentinel MCP Server...")
    try:
        asyncio.run(run_stdio_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        traceback.print_exc()
