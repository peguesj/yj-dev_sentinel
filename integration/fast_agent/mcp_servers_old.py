"""
MCP Server implementations for Dev Sentinel.

This module provides Model Context Protocol (MCP) server implementations
that can be used with fast-agent to execute Dev Sentinel commands.
Follows MCP best practices and modern async patterns.
"""

import os
import sys
import json
import logging
import asyncio
import traceback
from typing import Dict, List, Any, Optional, Union, Sequence
from contextlib import asynccontextmanager

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
    from mcp import types
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
except ImportError as e:
    raise ImportError(f"mcp package is not installed. Run 'pip install mcp': {e}")

# Import Dev Sentinel components
try:
    from integration.force.master_agent import ForceCommandProcessor
    from integration.fast_agent.async_initialization import get_async_initializer
except ImportError:
    # Graceful fallback for missing components
    ForceCommandProcessor = None
    get_async_initializer = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("dev_sentinel_mcp")

class DevSentinelServer:
    """
    Modern MCP server implementation for Dev Sentinel.
    
    This server exposes Dev Sentinel functionality through the Model Context Protocol,
    allowing integration with MCP-compatible tools and environments.
    """

    def __init__(self):
        """Initialize the Dev Sentinel MCP server."""
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
                    name="execute_command",
                    description="Execute a Dev Sentinel YUNG command",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "YUNG command to execute (e.g., '$VIC DOCS', '$CODE TIER=BACKEND IMPL')"
                            },
                            "args": {
                                "type": "object",
                                "description": "Additional command arguments",
                                "default": {}
                            }
                        },
                        "required": ["command"]
                    }
                ),
                types.Tool(
                    name="validate_documentation",
                    description="Validate project documentation integrity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "enum": ["ALL", "LAST", "DOCS", "FILE"],
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
                    description="Analyze code for documentation and quality issues",
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
                    description="Get version control repository status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="generate_diagram",
                    description="Generate system diagrams",
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
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls."""
            try:
                await self.ensure_initialized()
                
                if name == "execute_command":
                    command = arguments.get("command", "")
                    args = arguments.get("args", {})
                    result = await self._execute_yung_command(command, args)
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
                
                elif name == "generate_diagram":
                    diagram_type = arguments.get("type", "ARCH")
                    format_type = arguments.get("format", "svg")
                    result = await self._generate_diagram(diagram_type, format_type)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
                
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
                # Initialize FORCE command processor
                if ForceCommandProcessor:
                    self.force_processor = ForceCommandProcessor()
                    if hasattr(self.force_processor, 'initialize'):
                        await self.force_processor.initialize()
                else:
                    logger.warning("ForceCommandProcessor not available - some functionality will be limited")
                
                self._initialized = True
                logger.info("Dev Sentinel MCP Server initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Dev Sentinel MCP Server: {e}")
                raise

    async def _execute_yung_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a YUNG command through the FORCE processor."""
        try:
            if not self.force_processor:
                return {
                    "status": "error",
                    "message": "FORCE processor not available",
                    "command": command,
                    "args": args
                }
            
            # Process the YUNG command
            if hasattr(self.force_processor, 'process_command'):
                result = await self.force_processor.process_command(command)
            else:
                # Fallback processing
                result = await self._fallback_command_processing(command, args)
            
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
        
        return await self._execute_yung_command(command, {})

    async def _analyze_code(self, tier: str, action: str) -> Dict[str, Any]:
        """Analyze code using CODE command."""
        command = f"$CODE TIER={tier} {action}"
        return await self._execute_yung_command(command, {})

    async def _get_repository_status(self) -> Dict[str, Any]:
        """Get repository status using VCS command."""
        command = "$VCS STATUS"
        return await self._execute_yung_command(command, {})

    async def _generate_diagram(self, diagram_type: str, format_type: str) -> Dict[str, Any]:
        """Generate diagrams using DIAGRAM command."""
        command = f"$DIAGRAM {diagram_type} FORMAT={format_type}"
        return await self._execute_yung_command(command, {})

    async def _fallback_command_processing(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback command processing when FORCE processor is not available."""
        logger.warning(f"Using fallback processing for command: {command}")
        
        # Parse basic command structure
        if command.startswith("$"):
            parts = command[1:].split()
            cmd_type = parts[0] if parts else "UNKNOWN"
            
            return {
                "command_type": cmd_type,
                "command": command,
                "args": args,
                "status": "processed_fallback",
                "message": "Command processed using fallback method - full functionality requires FORCE processor"
            }
        
        return {
            "command": command,
            "args": args,
            "status": "unprocessed",
            "message": "Command format not recognized"
        }
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
        await self.mcp.run_sse_async()

class FileSystemMCPServer:
    """File system operations MCP server implementation."""
    def __init__(self):
        """Initialize the File System MCP server."""
        self.mcp = FastMCP(name="filesystem")
        self.register_tools()
        
    def register_tools(self):
        """Register all tools with the MCP instance."""
        
        @self.mcp.tool()
        async def read_file(path: str) -> Result:
            """
            Read a file from the filesystem.
            
            Args:
                path: Path to the file to read
                
            Returns:
                Result containing file contents
            """
            try:
                with open(path, 'r') as f:
                    content = f.read()
                return Result(status="success", result={"content": content})
            except Exception as e:
                logger.exception(f"Error reading file: {e}")
                return Result(status="error", result={"error": str(e)})
        
        @self.mcp.tool()
        async def write_file(path: str, content: str) -> Result:
            """
            Write content to a file.
            
            Args:
                path: Path to the file to write
                content: Content to write
                
            Returns:
                Result indicating success or failure
            """
            try:
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content)
                return Result(status="success", result={"message": f"File written: {path}"})
            except Exception as e:
                logger.exception(f"Error writing file: {e}")
                return Result(status="error", result={"error": str(e)})
        
        @self.mcp.tool()
        async def list_directory(path: str) -> Result:
            """
            List contents of a directory.
            
            Args:
                path: Path to the directory to list
                
            Returns:
                Result containing directory contents
            """
            try:
                files = os.listdir(path)
                result = []
                for file in files:
                    full_path = os.path.join(path, file)
                    result.append({
                        "name": file,
                        "is_directory": os.path.isdir(full_path),
                        "size": os.path.getsize(full_path),
                        "last_modified": os.path.getmtime(full_path)
                    })
                return Result(status="success", result={"files": result})
            except Exception as e:
                logger.exception(f"Error listing directory: {e}")
                return Result(status="error", result={"error": str(e)})
        
    async def start(self, host: str = "0.0.0.0", port: int = 8091):
        """Start the MCP server."""
        await self.mcp.run_async(host=host, port=port)

class VersionControlMCPServer:
    """Version control operations MCP server implementation."""
    def __init__(self):
        """Initialize the Version Control MCP server."""
        self.mcp = FastMCP(name="vcs")
        self.register_tools()
        
    def register_tools(self):
        """Register all tools with the MCP instance."""
        
        @self.mcp.tool()
        async def get_changes(repo_path: str = None) -> Result:
            """
            Get changes in the git repository.
            
            Args:
                repo_path: Path to the git repository (defaults to current directory)
                
            Returns:
                Result containing changes in the repository
            """
            try:
                if repo_path is None:
                    repo_path = os.getcwd()
                    
                import subprocess
                cmd = ["git", "-C", repo_path, "status", "--porcelain"]
                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode != 0:
                    return Result(status="error", result={"error": process.stderr})
                    
                lines = process.stdout.strip().split("\n")
                changes = []
                
                for line in lines:
                    if not line:
                        continue
                    status = line[:2]
                    file_path = line[3:]
                    
                    changes.append({
                        "status": status,
                        "file": file_path
                    })
                    
                return Result(status="success", result={"changes": changes})
                
            except Exception as e:
                logger.exception(f"Error getting changes: {e}")
                return Result(status="error", result={"error": str(e)})
        
        @self.mcp.tool()
        async def commit(repo_path: str = None, message: str = None, files: List[str] = None) -> Result:
            """
            Commit changes to git repository.
            
            Args:
                repo_path: Path to the git repository (defaults to current directory)
                message: Commit message
                files: List of files to commit (defaults to all changed files)
                
            Returns:
                Result indicating commit status
            """
            try:
                if repo_path is None:
                    repo_path = os.getcwd()
                    
                if message is None:
                    return Result(status="error", result={"error": "Commit message is required"})
                    
                import subprocess
                
                if files:
                    # Stage specific files
                    cmd = ["git", "-C", repo_path, "add"] + files
                    process = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if process.returncode != 0:
                        return Result(status="error", result={"error": process.stderr})
                else:
                    # Stage all files
                    cmd = ["git", "-C", repo_path, "add", "."]
                    process = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if process.returncode != 0:
                        return Result(status="error", result={"error": process.stderr})
                
                # Commit changes
                cmd = ["git", "-C", repo_path, "commit", "-m", message]
                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode != 0:
                    return Result(status="error", result={"error": process.stderr})
                    
                return Result(status="success", result={"message": "Changes committed successfully"})
                
            except Exception as e:
                logger.exception(f"Error committing changes: {e}")
                return Result(status="error", result={"error": str(e)})
        
        @self.mcp.tool()
        async def create_branch(repo_path: str = None, branch_name: str = None) -> Result:
            """
            Create a new branch in the git repository.
            
            Args:
                repo_path: Path to the git repository (defaults to current directory)
                branch_name: Name of the branch to create
                
            Returns:
                Result indicating branch creation status
            """
            try:
                if repo_path is None:
                    repo_path = os.getcwd()
                    
                if branch_name is None:
                    return Result(status="error", result={"error": "Branch name is required"})
                    
                import subprocess
                
                # Create branch
                cmd = ["git", "-C", repo_path, "branch", branch_name]
                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode != 0:
                    return Result(status="error", result={"error": process.stderr})
                    
                # Checkout branch
                cmd = ["git", "-C", repo_path, "checkout", branch_name]
                process = subprocess.run(cmd, capture_output=True, text=True)
                
                if process.returncode != 0:
                    return Result(status="error", result={"error": process.stderr})
                    
                return Result(status="success", result={"message": f"Branch '{branch_name}' created and checked out"})
                
            except Exception as e:
                logger.exception(f"Error creating branch: {e}")
                return Result(status="error", result={"error": str(e)})
        
    async def start(self, host: str = "0.0.0.0", port: int = 8092):
        """Start the MCP server."""
        await self.mcp.run_async(host=host, port=port)

class DocumentationInspectorMCPServer:
    """Documentation inspection operations MCP server implementation."""
    def __init__(self):
        """Initialize the Documentation Inspector MCP server."""
        self.mcp = FastMCP(name="documentation")
        self.register_tools()
        
    def register_tools(self):
        """Register all tools with the MCP instance."""
        
        @self.mcp.tool()
        async def inspect_documentation(file_path: str) -> Result:
            """
            Inspect documentation in a file.
            
            Args:
                file_path: Path to the file to inspect
                
            Returns:
                Result containing documentation analysis
            """
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Simple documentation inspection logic
                # In reality, you would use RDIA agent functionality here
                lines = content.split('\n')
                doc_lines = [line for line in lines if '"""' in line or "'''" in line or '#' in line]
                doc_coverage = len(doc_lines) / len(lines) if lines else 0
                
                return Result(status="success", result={
                    "file": file_path,
                    "doc_coverage": doc_coverage,
                    "doc_lines_count": len(doc_lines),
                    "total_lines": len(lines)
                })
                
            except Exception as e:
                logger.exception(f"Error inspecting documentation: {e}")
                return Result(status="error", result={"error": str(e)})
        
        @self.mcp.tool()
        async def generate_documentation(file_path: str, content: str = None) -> Result:
            """
            Generate documentation for a file.
            
            Args:
                file_path: Path to the file to generate documentation for
                content: Optional content to generate documentation for (instead of reading from file)
                
            Returns:
                Result containing generated documentation
            """
            try:
                if content is None:
                    with open(file_path, 'r') as f:
                        content = f.read()
                
                # Simple documentation generation logic
                # In reality, you would use CDIA agent functionality here
                import re
                
                # Find functions and classes
                function_pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
                class_pattern = r'class\s+(\w+)'
                
                functions = re.findall(function_pattern, content)
                classes = re.findall(class_pattern, content)
                
                docs = []
                
                for name, _ in functions:
                    docs.append(f"### Function: {name}\n\n```python\ndef {name}():\n    \"\"\"\n    [TODO: Add function description]\n    \"\"\"\n    pass\n```\n")
                
                for name in classes:
                    docs.append(f"### Class: {name}\n\n```python\nclass {name}:\n    \"\"\"\n    [TODO: Add class description]\n    \"\"\"\n    pass\n```\n")
                
                return Result(status="success", result={
                    "file": file_path,
                    "generated_docs": "\n".join(docs)
                })
                
            except Exception as e:
                logger.exception(f"Error generating documentation: {e}")
                return Result(status="error", result={"error": str(e)})
        
    async def start(self, host: str = "0.0.0.0", port: int = 8093):
        """Start the MCP server."""
        await self.mcp.run_async(host=host, port=port)

class CodeAnalysisMCPServer:
    """Code analysis operations MCP server implementation."""
    def __init__(self):
        """Initialize the Code Analysis MCP server."""
        self.mcp = FastMCP(name="code_analysis")
        self.register_tools()
        
    def register_tools(self):
        """Register all tools with the MCP instance."""
        
        @self.mcp.tool()
        async def analyze_code(file_path: str) -> Result:
            """
            Analyze code in a file.
            
            Args:
                file_path: Path to the file to analyze
                
            Returns:
                Result containing code analysis
            """
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Simple code analysis logic
                # In reality, you would use SAA agent functionality here
                lines = content.split('\n')
                
                # Count lines of code, excluding comments and blank lines
                code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
                
                # Check for common code smells
                long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 100]
                complex_functions = []  # Would require actual parsing
                
                return Result(status="success", result={
                    "file": file_path,
                    "total_lines": len(lines),
                    "code_lines": len(code_lines),
                    "issues": {
                        "long_lines": long_lines,
                        "complex_functions": complex_functions
                    }
                })
                
            except Exception as e:
                logger.exception(f"Error analyzing code: {e}")
                return Result(status="error", result={"error": str(e)})
        
    async def start(self, host: str = "0.0.0.0", port: int = 8094):
        """Start the MCP server."""
        await self.mcp.run_async(host=host, port=port)

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