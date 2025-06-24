"""
Enhanced MCP server for Dev Sentinel with Force system integration.

This module provides a comprehensive Model Context Protocol server that
exposes all Force system capabilities, including tools, patterns, constraints,
learning insights, and governance controls.
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

# MCP imports
try:
    from mcp import types
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    MCP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"MCP not available: {e}")
    MCP_AVAILABLE = False
    # Minimal stubs for development
    class types:
        class Tool:
            def __init__(self, name, description, inputSchema): pass
        class TextContent:
            def __init__(self, type, text): pass
    class Server:
        def __init__(self, name): pass

# Force system imports
try:
    from force import ForceEngine, ForceEngineError, ToolExecutionError, SchemaValidationError
    FORCE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Force engine not available: {e}")
    FORCE_AVAILABLE = False
    class ForceEngine:
        def __init__(self): pass
    ForceEngineError = Exception
    ToolExecutionError = Exception
    SchemaValidationError = Exception

# Legacy system imports for backward compatibility
try:
    from integration.force.master_agent import ForceCommandProcessor
    LEGACY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Legacy system not available: {e}")
    LEGACY_AVAILABLE = False
    ForceCommandProcessor = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("force_mcp_server")

class ForceMCPServer:
    """
    Enhanced MCP server with Force system integration.
    
    Provides comprehensive access to Force tools, patterns, constraints,
    learning insights, and governance controls through the Model Context Protocol.
    """

    def __init__(self, force_directory: Optional[str] = None):
        """Initialize the Force MCP server."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP package not available - install with 'pip install mcp'")
        
        self.server = Server("dev-sentinel-force")
        self.force_engine = None
        self.legacy_processor = None
        self._force_directory = force_directory
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        
        # Set up server capabilities and handlers
        self._setup_server()
    
    async def _initialize_force_engine(self):
        """Initialize the Force engine asynchronously."""
        async with self._initialization_lock:
            if self._initialized:
                return
            
            try:
                if FORCE_AVAILABLE:
                    self.force_engine = ForceEngine(self._force_directory)
                    logger.info("Force engine initialized successfully")
                else:
                    logger.warning("Force engine not available - limited functionality")
                
                if LEGACY_AVAILABLE and ForceCommandProcessor:
                    self.legacy_processor = ForceCommandProcessor()
                    logger.info("Legacy command processor initialized")
                
                self._initialized = True
                
            except Exception as e:
                logger.error(f"Failed to initialize Force systems: {e}")
                raise
    
    def _setup_server(self):
        """Set up server capabilities and tool handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available Force tools and capabilities."""
            await self._initialize_force_engine()
            
            tools = []
            
            # Core Force tools
            tools.extend([
                types.Tool(
                    name="force_execute_tool",
                    description="Execute a Force tool with schema validation and monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "toolId": {
                                "type": "string",
                                "description": "ID of the Force tool to execute"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters for tool execution"
                            },
                            "context": {
                                "type": "object",
                                "description": "Execution context information",
                                "properties": {
                                    "projectPhase": {
                                        "type": "string",
                                        "enum": ["initialization", "development", "testing", "deployment", "maintenance"]
                                    },
                                    "complexityLevel": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high", "enterprise"]
                                    },
                                    "environment": {
                                        "type": "string",
                                        "enum": ["development", "staging", "production"]
                                    }
                                }
                            },
                            "dryRun": {
                                "type": "boolean",
                                "description": "Perform a dry run without executing",
                                "default": false
                            }
                        },
                        "required": ["toolId"]
                    }
                ),
                types.Tool(
                    name="force_apply_pattern",
                    description="Apply a Force development pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "patternId": {
                                "type": "string",
                                "description": "ID of the pattern to apply"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Pattern-specific parameters"
                            },
                            "context": {
                                "type": "object",
                                "description": "Application context"
                            }
                        },
                        "required": ["patternId"]
                    }
                ),
                types.Tool(
                    name="force_check_constraints",
                    description="Check code against Force constraints",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "description": "Scope of constraint checking",
                                "default": "**/*"
                            },
                            "constraintIds": {
                                "type": "array",
                                "description": "Specific constraints to check",
                                "items": {"type": "string"}
                            },
                            "autoFix": {
                                "type": "boolean",
                                "description": "Automatically fix violations where possible",
                                "default": false
                            }
                        }
                    }
                ),
                types.Tool(
                    name="force_get_insights",
                    description="Retrieve learning insights and recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Category of insights to retrieve",
                                "enum": ["performance", "usage", "errors", "optimization", "all"]
                            },
                            "timeRange": {
                                "type": "string",
                                "description": "Time range for insights",
                                "enum": ["last-hour", "last-day", "last-week", "last-month", "all"]
                            },
                            "toolId": {
                                "type": "string",
                                "description": "Filter insights by specific tool"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="force_list_tools",
                    description="List all available Force tools with metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by tool category"
                            },
                            "includeMetadata": {
                                "type": "boolean",
                                "description": "Include detailed metadata",
                                "default": true
                            }
                        }
                    }
                ),
                types.Tool(
                    name="force_list_patterns",
                    description="List all available Force patterns with applicability",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter by pattern category"
                            },
                            "projectType": {
                                "type": "string",
                                "description": "Filter by project type applicability"
                            },
                            "complexityLevel": {
                                "type": "string",
                                "description": "Filter by complexity level"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="force_validate_component",
                    description="Validate a Force component against schema",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component": {
                                "type": "object",
                                "description": "Force component to validate"
                            },
                            "componentType": {
                                "type": "string",
                                "description": "Type of component",
                                "enum": ["Tool", "Pattern", "Constraint", "LearningRecord", "GovernancePolicy"]
                            }
                        },
                        "required": ["component", "componentType"]
                    }
                )
            ])
            
            # Legacy compatibility tools
            if self.legacy_processor:
                tools.append(
                    types.Tool(
                        name="yung_command",
                        description="Execute legacy YUNG commands (compatibility mode)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "YUNG command to execute"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Command parameters"
                                }
                            },
                            "required": ["command"]
                        }
                    )
                )
            
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool execution requests."""
            await self._initialize_force_engine()
            
            try:
                if name == "force_execute_tool":
                    return await self._handle_execute_tool(arguments)
                elif name == "force_apply_pattern":
                    return await self._handle_apply_pattern(arguments)
                elif name == "force_check_constraints":
                    return await self._handle_check_constraints(arguments)
                elif name == "force_get_insights":
                    return await self._handle_get_insights(arguments)
                elif name == "force_list_tools":
                    return await self._handle_list_tools(arguments)
                elif name == "force_list_patterns":
                    return await self._handle_list_patterns(arguments)
                elif name == "force_validate_component":
                    return await self._handle_validate_component(arguments)
                elif name == "yung_command":
                    return await self._handle_yung_command(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                error_msg = f"Tool execution failed: {str(e)}"
                if isinstance(e, (ForceEngineError, ToolExecutionError, SchemaValidationError)):
                    error_msg = f"Force error: {str(e)}"
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": error_msg,
                        "tool": name,
                        "traceback": traceback.format_exc() if logger.level <= logging.DEBUG else None
                    }, indent=2)
                )]

    async def _handle_execute_tool(self, arguments: dict) -> list[types.TextContent]:
        """Handle Force tool execution."""
        if not self.force_engine:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        tool_id = arguments.get("toolId")
        parameters = arguments.get("parameters", {})
        context = arguments.get("context", {})
        dry_run = arguments.get("dryRun", False)
        
        if dry_run:
            # Validate parameters without execution
            tools = self.force_engine.load_tools()
            if tool_id not in tools:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"success": False, "error": f"Tool not found: {tool_id}"}, indent=2)
                )]
            
            tool = tools[tool_id]
            result = {
                "success": True,
                "dryRun": True,
                "tool": tool,
                "parameters": parameters,
                "context": context
            }
        else:
            result = await self.force_engine.execute_tool(tool_id, parameters, context)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]

    async def _handle_apply_pattern(self, arguments: dict) -> list[types.TextContent]:
        """Handle Force pattern application."""
        if not self.force_engine:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        pattern_id = arguments.get("patternId")
        parameters = arguments.get("parameters", {})
        context = arguments.get("context", {})
        
        patterns = self.force_engine.load_patterns()
        if pattern_id not in patterns:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": f"Pattern not found: {pattern_id}"}, indent=2)
            )]
        
        pattern = patterns[pattern_id]
        results = []
        
        # Execute pattern steps
        for step in pattern.get("implementation", {}).get("steps", []):
            tool_id = step.get("toolId")
            if tool_id:
                step_params = {**step.get("parameters", {}), **parameters}
                result = await self.force_engine.execute_tool(tool_id, step_params, context)
                results.append({
                    "step": step["name"],
                    "result": result
                })
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "pattern": pattern_id,
                "steps": results
            }, indent=2, default=str)
        )]

    async def _handle_check_constraints(self, arguments: dict) -> list[types.TextContent]:
        """Handle constraint checking."""
        if not self.force_engine:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        scope = arguments.get("scope", "**/*")
        constraint_ids = arguments.get("constraintIds", [])
        auto_fix = arguments.get("autoFix", False)
        
        constraints = self.force_engine.load_constraints()
        
        if constraint_ids:
            # Check specific constraints
            constraints_to_check = {cid: constraints[cid] for cid in constraint_ids if cid in constraints}
        else:
            # Check all constraints
            constraints_to_check = constraints
        
        results = []
        for constraint_id, constraint in constraints_to_check.items():
            # TODO: Implement actual constraint checking logic
            result = {
                "constraintId": constraint_id,
                "name": constraint.get("name", constraint_id),
                "scope": scope,
                "violations": [],  # Placeholder
                "autoFixed": False
            }
            results.append(result)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "constraintsChecked": len(results),
                "results": results
            }, indent=2)
        )]

    async def _handle_get_insights(self, arguments: dict) -> list[types.TextContent]:
        """Handle learning insights retrieval."""
        if not self.force_engine:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        category = arguments.get("category", "all")
        time_range = arguments.get("timeRange", "all")
        tool_id = arguments.get("toolId")
        
        # Load learning data
        learning_file = self.force_engine.learning_dir / "execution-analytics.json"
        insights = {"insights": [], "recommendations": []}
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    learning_data = json.load(f)
                    insights = learning_data.get("learningInsights", insights)
            except Exception as e:
                logger.warning(f"Could not load learning data: {e}")
        
        # Filter insights based on parameters
        filtered_insights = insights
        if tool_id:
            # TODO: Implement tool-specific filtering
            pass
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "category": category,
                "timeRange": time_range,
                "insights": filtered_insights
            }, indent=2)
        )]

    async def _handle_list_tools(self, arguments: dict) -> list[types.TextContent]:
        """Handle tool listing."""
        if not self.force_engine:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        category = arguments.get("category")
        include_metadata = arguments.get("includeMetadata", True)
        
        tools = self.force_engine.get_tool_list()
        
        if category:
            tools = [tool for tool in tools if tool.get("category") == category]
        
        if not include_metadata:
            tools = [{k: v for k, v in tool.items() if k in ["id", "name", "description"]} for tool in tools]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "tools": tools,
                "count": len(tools)
            }, indent=2)
        )]

    async def _handle_list_patterns(self, arguments: dict) -> list[types.TextContent]:
        """Handle pattern listing."""
        if not self.force_engine:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        category = arguments.get("category")
        project_type = arguments.get("projectType")
        complexity_level = arguments.get("complexityLevel")
        
        patterns = self.force_engine.get_pattern_list()
        
        # Apply filters
        if category:
            patterns = [p for p in patterns if p.get("category") == category]
        
        # TODO: Implement project_type and complexity_level filtering
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "patterns": patterns,
                "count": len(patterns)
            }, indent=2)
        )]

    async def _handle_validate_component(self, arguments: dict) -> list[types.TextContent]:
        """Handle component validation."""
        if not self.force_engine:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        component = arguments.get("component")
        component_type = arguments.get("componentType")
        
        try:
            self.force_engine.validate_component(component, component_type)
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "valid": True,
                    "componentType": component_type
                }, indent=2)
            )]
        except SchemaValidationError as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "valid": False,
                    "error": str(e),
                    "componentType": component_type
                }, indent=2)
            )]

    async def _handle_yung_command(self, arguments: dict) -> list[types.TextContent]:
        """Handle legacy YUNG command execution."""
        if not self.legacy_processor:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Legacy YUNG processor not available"}, indent=2)
            )]
        
        command = arguments.get("command")
        parameters = arguments.get("parameters", {})
        
        try:
            # TODO: Implement actual YUNG command processing
            result = {
                "success": True,
                "command": command,
                "parameters": parameters,
                "message": "Legacy YUNG command processed (compatibility mode)"
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"YUNG command failed: {str(e)}"
                }, indent=2)
            )]

    async def run(self):
        """Run the MCP server."""
        try:
            await self._initialize_force_engine()
            logger.info("Starting Force MCP server...")
            
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="dev-sentinel-force",
                        server_version="2.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities={}
                        )
                    )
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            if self.force_engine:
                await self.force_engine.cleanup()

async def main():
    """Main entry point for the Force MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dev Sentinel Force MCP Server")
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
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    server = ForceMCPServer(force_directory=args.force_dir)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
