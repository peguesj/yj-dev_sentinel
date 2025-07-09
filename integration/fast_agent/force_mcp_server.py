"""
Enhanced MCP server for Dev Sentinel with Force system integration.

This module provides a comprehensive Model Context Protocol server that
exposes all Force system capabilities, including tools, patterns, constraints,
learning insights, and governance controls.

The server performs validation and fixing of Force components at startup
before loading any JSON tool files to ensure system integrity.
"""

import os
import sys
import json
import logging
import asyncio
import traceback
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Sequence
from contextlib import asynccontextmanager, AbstractAsyncContextManager

# --- Compatibility Layer for MCP Types ---
class MCPCompat:
    Tool: Any
    TextContent: Any
    ServerCapabilities: Any
    Server: Any
    InitializationOptions: Any
    stdio_server: Any
    @staticmethod
    def patch():
        try:
            from mcp import types as real_types
            from mcp.server import Server as real_Server
            from mcp.server.models import InitializationOptions as real_InitializationOptions
            import mcp.server.stdio as real_stdio
            MCPCompat.Tool = real_types.Tool
            MCPCompat.TextContent = real_types.TextContent
            MCPCompat.ServerCapabilities = real_types.ServerCapabilities
            MCPCompat.Server = real_Server
            MCPCompat.InitializationOptions = real_InitializationOptions
            MCPCompat.stdio_server = real_stdio.stdio_server
            return True
        except ImportError:
            class Tool:
                def __init__(self, name, description, inputSchema): pass
            class TextContent:
                def __init__(self, type, text): pass
            class ServerCapabilities:
                def __init__(self):
                    self.capabilities = {}
            class Server:
                def __init__(self, name): pass
                def list_tools(self): return lambda f: f
                def call_tool(self): return lambda f: f
                async def run(self, *args, **kwargs): pass
                def get_capabilities(self, *args, **kwargs): return ServerCapabilities()
            class InitializationOptions:
                def __init__(self, *args, **kwargs): pass
            class DummyAsyncContextManager(AbstractAsyncContextManager):
                async def __aenter__(self): return (None, None)
                async def __aexit__(self, exc_type, exc, tb): return False
            MCPCompat.Tool = Tool
            MCPCompat.TextContent = TextContent
            MCPCompat.ServerCapabilities = ServerCapabilities
            MCPCompat.Server = Server
            MCPCompat.InitializationOptions = InitializationOptions
            MCPCompat.stdio_server = DummyAsyncContextManager
            return False

MCP_AVAILABLE = MCPCompat.patch()

# Force system imports
try:
    from force import ForceEngine, ForceEngineError, ToolExecutionError, SchemaValidationError
    FORCE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Force engine not available: {e}")
    FORCE_AVAILABLE = False
    class ForceEngineStub:
        def __init__(self, *args, **kwargs): pass
        def load_tools(self): return {}
        def load_patterns(self): return {}
        def load_constraints(self): return {}
        def get_tool_list(self): return []
        def get_pattern_list(self): return []
        def validate_component(self, component, component_type): return True
        def save_report(self, content, report_type, custom_filename=None): return '/tmp/fake_report.md'
        def list_reports(self): return []
        def get_reports_directory(self): return '/tmp/reports'
        async def execute_tool(self, tool_id, parameters, context): return {"executed": True, "tool_id": tool_id, "parameters": parameters, "context": context}
        async def cleanup(self): pass
        @property
        def learning_dir(self):
            import pathlib
            return pathlib.Path('/tmp')
    ForceEngine = ForceEngineStub
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
    
    Performs validation and fixing of Force components at startup before loading
    any JSON tool files to ensure system integrity.
    """

    def __init__(self, force_directory: Optional[str] = None, auto_fix: bool = True):
        """Initialize the Force MCP server."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP package not available - install with 'pip install mcp'")
        
        self.server = MCPCompat.Server("dev-sentinel-force")
        self.force_engine = None
        self.legacy_processor = None
        self._force_directory = force_directory
        self._auto_fix = auto_fix
        self._initialized = False
        self._validation_passed = False
        self._initialization_lock = asyncio.Lock()
        
        # Set up server capabilities and handlers
        self._setup_server()
    
    async def _run_startup_validation_and_fix(self) -> bool:
        """Run Force component validation and fixing at startup using embedded system."""
        logger.info("🔍 Starting Force component validation at MCP server startup...")
        
        # Determine Force directory
        force_root = self._force_directory or ".force"
        if not Path(force_root).exists():
            logger.error(f"❌ Force directory not found: {force_root}")
            return False
        
        try:
            # Import the embedded validation system directly
            from force.system.force_component_validator import ForceValidator
            
            # Initialize validator
            validator = ForceValidator(force_root)
            logger.info(f"📋 Using schema: {validator.schema_file.name}")
            
            # Run validation
            validation_result = validator.validate_all()
            
            # Generate and log validation report
            report = validator.generate_validation_report(validation_result)
            logger.info(f"Validation output:\n{report}")
            
            # Save detailed validation report
            report_path = validator.save_validation_report(validation_result)
            logger.info(f"📄 Detailed validation report saved to: {report_path}")
            
            # Check for blocking issues
            blocking_issues = validator.check_blocking_issues(validation_result)
            if blocking_issues:
                logger.error("🚨 BLOCKING ISSUES DETECTED:")
                for issue in blocking_issues:
                    logger.error(f"  • {issue}")
                logger.error("❌ MCP server startup blocked until issues are resolved")
                return False
            
            # Check validation summary
            summary = validation_result.get('summary', {})
            invalid_count = summary.get('invalid_components', 0)
            total_count = summary.get('total_components', 0)
            
            if invalid_count > 0:
                logger.warning(f"⚠️  {invalid_count}/{total_count} Force components have validation errors")
                logger.warning("💡 Components with validation errors will be skipped during loading")
                logger.warning("🔧 Consider updating components to match current schema format")
                logger.warning(f"📖 Schema reference: {validator.schema_file.relative_to(Path(force_root))}")
                
                if self._auto_fix:
                    logger.info("🔧 Auto-fix is enabled - invalid components could be automatically repaired")
                else:
                    logger.info("🔧 Auto-fix is disabled - use --auto-fix to enable automatic component repair")
            
            # No blocking issues found - validation passes even with some invalid components
            logger.info("✅ Force component validation passed - MCP server can proceed")
            return True
                
        except Exception as e:
            logger.error(f"❌ Error during startup validation: {e}")
            # Fallback to ForceStartupValidator if direct validation fails
            logger.info("⚠️ Falling back to ForceStartupValidator method...")
            return await self._run_validation_fallback(force_root)
    
    async def _run_validation_fallback(self, force_root: str) -> bool:
        """Fallback validation method using embedded validation."""
        try:
            # Import ForceValidator directly
            from force.system.force_component_validator import ForceValidator
            
            # Initialize validator
            validator = ForceValidator(force_root)
            
            # Run validation
            validation_result = validator.validate_all()
            
            # Generate and print validation report
            report = validator.generate_validation_report(validation_result)
            logger.info(f"Validation output:\n{report}")
            
            # Check for blocking issues
            blocking_issues = validator.check_blocking_issues(validation_result)
            if blocking_issues:
                logger.error("🚨 BLOCKING ISSUES DETECTED:")
                for issue in blocking_issues:
                    logger.error(f"  • {issue}")
                return False
            
            # Check if validation passed (some components can be invalid but not blocking)
            validation_success = validation_result.get('summary', {}).get('ready_for_loading', True)
            
            if not validation_success and self._auto_fix:
                logger.info("🔧 Validation failed, attempting automatic fixes...")
                
                # Import and use the auto-fixer
                try:
                    from force.system.force_component_auto_fixer import ForceComponentAutoFixer
                    
                    auto_fixer = ForceComponentAutoFixer(force_root)
                    fix_results = auto_fixer.auto_fix_all_components()
                    
                    if fix_results['success']:
                        logger.info(f"🔧 Auto-fix results: {fix_results['files_fixed']}/{fix_results['total_files_processed']} files fixed")
                        if fix_results.get('backup_created'):
                            logger.info(f"📁 Backup created at: {fix_results['backup_location']}")
                        
                        # Log specific fixes applied
                        for fix in fix_results.get('fixes_applied', []):
                            logger.debug(f"Fixed {fix['file']}: {', '.join(fix['fixes'])}")
                        
                        # Re-run validation after auto-fix
                        validation_result = validator.validate_all()
                        report = validator.generate_validation_report(validation_result)
                        logger.info(f"Re-validation output:\n{report}")
                        
                        # Check for blocking issues again
                        blocking_issues = validator.check_blocking_issues(validation_result)
                        if blocking_issues:
                            logger.error("❌ Auto-fix failed to resolve blocking issues")
                            for issue in blocking_issues:
                                logger.error(f"  • {issue}")
                            return False
                        
                        validation_success = validation_result.get('summary', {}).get('ready_for_loading', True)
                        if validation_success:
                            logger.info("✅ Auto-fix successful - validation now passes")
                        else:
                            logger.warning("⚠️ Auto-fix partial - some issues remain but not blocking")
                    else:
                        logger.error(f"❌ Auto-fix failed: {fix_results.get('error', 'Unknown error')}")
                        return False
                        
                except ImportError as e:
                    logger.error(f"❌ Auto-fixer not available: {e}")
                    logger.info("Auto-fix output:\n🔧 Auto-fix functionality requires force_component_auto_fixer module")
                    logger.info("Manual intervention may be required for invalid components.")
                    return False
                except Exception as e:
                    logger.error(f"❌ Auto-fix error: {e}")
                    return False
            elif not validation_success:
                logger.error("❌ Validation failed and auto-fix is disabled")
                return False
            
            return validation_success
            
        except Exception as e:
            logger.error(f"❌ Error in fallback validation: {e}")
            return False

    async def _initialize_force_engine(self):
        """Initialize the Force engine asynchronously after validation."""
        async with self._initialization_lock:
            if self._initialized:
                return
            
            # Run startup validation and fix before initializing
            if not self._validation_passed:
                self._validation_passed = await self._run_startup_validation_and_fix()
                if not self._validation_passed:
                    raise RuntimeError("Force component validation failed - cannot start MCP server")
            
            try:
                if FORCE_AVAILABLE:
                    self.force_engine = ForceEngine(self._force_directory)
                    logger.info("Force engine initialized successfully")
                    
                    # Automatically attempt project-to-project force sync on startup
                    try:
                        await self._handle_force_sync({
                            "direction": "project-to-project",
                            "components": [],  # Empty for all components
                            "convertPatternTools": True,
                            "updateExisting": True,
                            "dryRun": False
                        })
                        logger.info("Initial project-to-project force sync completed")
                    except Exception as e:
                        logger.error(f"Initial force sync failed: {e}")
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
        async def handle_list_tools():
            """List available Force tools and capabilities."""
            await self._initialize_force_engine()
            
            tools = []
            
            # Add JSON-defined tools as individual MCP tools
            if self.force_engine:
                available_tools = self.force_engine.get_tool_list()
                for tool_info in available_tools:
                    tool_id = tool_info.get('id')
                    tool_name = tool_info.get('name', tool_id)
                    tool_description = tool_info.get('description', f'Execute {tool_name}')
                    tool_parameters = tool_info.get('parameters', {})
                    
                    # Create MCP tool schema from Force tool definition
                    input_schema = {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                    
                    # Convert Force tool parameters to MCP input schema
                    if isinstance(tool_parameters, dict) and 'properties' in tool_parameters:
                        input_schema["properties"] = tool_parameters.get('properties', {})
                        input_schema["required"] = tool_parameters.get('required', [])
                    elif isinstance(tool_parameters, dict):
                        # If parameters is a flat dict, use it directly
                        input_schema["properties"] = tool_parameters
                    
                    # Add context parameter for all tools
                    input_schema["properties"]["context"] = {
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
                    }
                    
                    tools.append(MCPCompat.Tool(
                        name=tool_id,
                        description=tool_description,
                        inputSchema=input_schema
                    ))
            
            # Core Force management tools (always available)
            tools.extend([
                MCPCompat.Tool(
                    name="force_sync",
                    description="Synchronize Force components between default and project directories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "direction": {
                                "type": "string",
                                "description": "Direction to sync (default->project, project->default, or project->project)",
                                "enum": ["default-to-project", "project-to-default", "project-to-project"]
                            },
                            "components": {
                                "type": "array",
                                "description": "Components to sync (empty for all)",
                                "items": {
                                    "type": "string",
                                    "enum": ["tools", "patterns", "constraints", "governance"]
                                }
                            },
                            "dryRun": {
                                "type": "boolean",
                                "description": "Show what would be synced without making changes",
                                "default": False
                            }
                        }
                    }
                ),
                MCPCompat.Tool(
                    name="force_execute_tool",
                    description="Execute any Force tool (including dynamically created ones) with schema validation",
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
                                "default": False
                            }
                        },
                        "required": ["toolId"]
                    }
                ),
                MCPCompat.Tool(
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
                MCPCompat.Tool(
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
                                "default": False
                            }
                        }
                    }
                ),
                MCPCompat.Tool(
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
                MCPCompat.Tool(
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
                                "default": True
                            }
                        }
                    }
                ),
                MCPCompat.Tool(
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
                MCPCompat.Tool(
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
                ),
                MCPCompat.Tool(
                    name="force_save_report",
                    description="Save a report to the Force reports directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Report content to save"
                            },
                            "reportType": {
                                "type": "string",
                                "description": "Type of report (completion, git_task, doc_vcs, etc.)"
                            },
                            "customFilename": {
                                "type": "string",
                                "description": "Optional custom filename (should include .md extension)"
                            }
                        },
                        "required": ["content", "reportType"]
                    }
                ),
                MCPCompat.Tool(
                    name="force_list_reports",
                    description="List all reports in the Force reports directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "includeContent": {
                                "type": "boolean",
                                "description": "Include report content in response",
                                "default": False
                            }
                        }
                    }
                ),
                MCPCompat.Tool(
                    name="force_get_reports_directory",
                    description="Get the Force reports directory path",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ])
            
            # Legacy compatibility tools
            if self.legacy_processor:
                tools.append(
                    MCPCompat.Tool(
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
        async def handle_call_tool(name: str, arguments: dict):
            """Handle tool execution requests."""
            await self._initialize_force_engine()
            
            try:
                # Check if this is a Force management tool
                if name == "force_sync":
                    return await self._handle_force_sync(arguments)
                elif name == "force_execute_tool":
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
                elif name == "force_save_report":
                    return await self._handle_save_report(arguments)
                elif name == "force_list_reports":
                    return await self._handle_list_reports(arguments)
                elif name == "force_get_reports_directory":
                    return await self._handle_get_reports_directory(arguments)
                elif name == "yung_command":
                    return await self._handle_yung_command(arguments)
                else:
                    # Check if this is a JSON-defined tool that should be executed directly
                    if self.force_engine:
                        available_tools = self.force_engine.get_tool_list()
                        tool_ids = [tool.get('id') for tool in available_tools]
                        if name in tool_ids:
                            # Execute the JSON-defined tool directly
                            return await self._handle_execute_tool({
                                "toolId": name,
                                "parameters": {k: v for k, v in arguments.items() if k != "context"},
                                "context": arguments.get("context", {})
                            })
                    
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                error_msg = f"Tool execution failed: {str(e)}"
                if isinstance(e, (ForceEngineError, ToolExecutionError, SchemaValidationError)):
                    error_msg = f"Force error: {str(e)}"
                
                return [MCPCompat.TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": error_msg,
                        "tool": name,
                        "traceback": traceback.format_exc() if logger.level <= logging.DEBUG else None
                    }, indent=2)
                )]

    async def _handle_execute_tool(self, arguments: dict):
        """Handle Force tool execution."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        tool_id = arguments.get("toolId")
        parameters = arguments.get("parameters", {})
        context = arguments.get("context", {})
        dry_run = arguments.get("dryRun", False)
        if not tool_id:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Missing required argument: toolId"}, indent=2)
            )]
        if dry_run:
            tools = self.force_engine.load_tools()
            if tool_id not in tools:
                return [MCPCompat.TextContent(
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
        return [MCPCompat.TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]

    async def _handle_apply_pattern(self, arguments: dict):
        """Handle Force pattern application."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        pattern_id = arguments.get("patternId")
        parameters = arguments.get("parameters", {})
        context = arguments.get("context", {})
        if not pattern_id:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Missing required argument: patternId"}, indent=2)
            )]
        patterns = self.force_engine.load_patterns()
        if pattern_id not in patterns:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": f"Pattern not found: {pattern_id}"}, indent=2)
            )]
        pattern = patterns[pattern_id]
        results = []
        implementation = pattern.get("implementation", {})
        
        # Check for executable steps first
        executable_steps = implementation.get("executable_steps", [])
        if executable_steps:
            # Execute tool-based steps
            for step in executable_steps:
                if isinstance(step, dict) and "toolId" in step:
                    tool_id = step.get("toolId")
                    if tool_id:  # Ensure tool_id is not None
                        step_name = step.get("name", f"Step with {tool_id}")
                        step_params = {**step.get("parameters", {}), **parameters}
                        try:
                            result = await self.force_engine.execute_tool(tool_id, step_params, context)
                            results.append({
                                "step": step_name,
                                "tool_id": tool_id,
                                "result": result,
                                "status": "executed"
                            })
                        except Exception as e:
                            results.append({
                                "step": step_name,
                                "tool_id": tool_id,
                                "error": str(e),
                                "status": "failed"
                            })
                    else:
                        results.append({
                            "step": step.get("name", "Unnamed step"),
                            "error": "Missing toolId",
                            "status": "failed"
                        })
        else:
            # Handle descriptive steps (non-executable)
            steps = implementation.get("steps", [])
            if steps:
                for i, step in enumerate(steps):
                    if isinstance(step, str):
                        results.append({
                            "step": f"Step {i+1}",
                            "description": step,
                            "status": "documented",
                            "note": "This is a descriptive step - manual execution required"
                        })
                    elif isinstance(step, dict):
                        # Handle step objects
                        step_name = step.get("name", f"Step {i+1}")
                        if "toolId" in step:
                            tool_id = step.get("toolId")
                            if tool_id:  # Ensure tool_id is not None
                                step_params = {**step.get("parameters", {}), **parameters}
                                try:
                                    result = await self.force_engine.execute_tool(tool_id, step_params, context)
                                    results.append({
                                        "step": step_name,
                                        "tool_id": tool_id,
                                        "result": result,
                                        "status": "executed"
                                    })
                                except Exception as e:
                                    results.append({
                                        "step": step_name,
                                        "tool_id": tool_id,
                                        "error": str(e),
                                        "status": "failed"
                                    })
                            else:
                                results.append({
                                    "step": step_name,
                                    "error": "Missing toolId",
                                    "status": "failed"
                                })
                        else:
                            results.append({
                                "step": step_name,
                                "description": step.get("description", "No description provided"),
                                "status": "documented",
                                "note": "This is a descriptive step - manual execution required"
                            })
            
        # If no steps found at all
        if not results:
            results.append({
                "step": "Pattern Application",
                "status": "completed",
                "note": f"Pattern '{pattern_id}' applied successfully but contains no executable steps"
            })
        

        return [MCPCompat.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "pattern": pattern_id,
                "pattern_name": pattern.get("name", pattern_id),
                "description": pattern.get("description", ""),
                "total_steps": len(results),
                "executed_steps": len([r for r in results if r.get("status") == "executed"]),
                "documented_steps": len([r for r in results if r.get("status") == "documented"]),
                "failed_steps": len([r for r in results if r.get("status") == "failed"]),

                "steps": results
            }, indent=2, default=str)
        )]

    async def _handle_check_constraints(self, arguments: dict):
        """Handle constraint checking."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
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
        
        return [MCPCompat.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "constraintsChecked": len(results),
                "results": results
            }, indent=2)
        )]

    async def _handle_get_insights(self, arguments: dict):
        """Handle learning insights retrieval."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
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
                    # Handle both list format (execution analytics) and dict format (insights)
                    if isinstance(learning_data, list):
                        # Extract insights from execution analytics
                        extracted_insights = []
                        for entry in learning_data:
                            if entry.get("insights"):
                                extracted_insights.extend(entry["insights"])
                        insights = {"insights": extracted_insights, "recommendations": []}
                    else:
                        insights = learning_data.get("learningInsights", insights)

            except Exception as e:
                logger.warning(f"Could not load learning data: {e}")
        
        # Filter insights based on parameters
        filtered_insights = insights
        if tool_id:
            # TODO: Implement tool-specific filtering
            pass
        
        return [MCPCompat.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "category": category,
                "timeRange": time_range,
                "insights": filtered_insights
            }, indent=2)
        )]

    async def _handle_list_tools(self, arguments: dict):
        """Handle tool listing."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
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
        
        return [MCPCompat.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "tools": tools,
                "count": len(tools)
            }, indent=2)
        )]

    async def _handle_list_patterns(self, arguments: dict) -> List[Any]:
        """Handle pattern listing."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
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
        
        return [MCPCompat.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "patterns": patterns,
                "count": len(patterns)
            }, indent=2)
        )]

    async def _handle_validate_component(self, arguments: dict) -> List[Any]:
        """Handle component validation."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        component = arguments.get("component")
        component_type = arguments.get("componentType")
        if component is None or component_type is None:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Missing required argument: component or componentType"
                }, indent=2)
            )]
        try:
            self.force_engine.validate_component(component, component_type)
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "valid": True,
                    "componentType": component_type
                }, indent=2)
            )]
        except SchemaValidationError as e:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "valid": False,
                    "error": str(e),
                    "componentType": component_type
                }, indent=2)
            )]

    async def _handle_save_report(self, arguments: dict) -> List[Any]:
        """Handle saving a report to the Force reports directory."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        content = arguments.get("content")
        report_type = arguments.get("reportType")
        custom_filename = arguments.get("customFilename")
        if content is None or report_type is None:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "Missing required argument: content or reportType"
                }, indent=2)
            )]
        # Validate report type
        valid_report_types = ["completion", "git_task", "doc_vcs"]
        if report_type not in valid_report_types:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Invalid report type: {report_type}. Must be one of {valid_report_types}"
                }, indent=2)
            )]
        # Save report
        try:
            report_path = self.force_engine.save_report(content, report_type, custom_filename=custom_filename)
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "reportPath": str(report_path)
                }, indent=2)
            )]
        except Exception as e:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Failed to save report: {str(e)}"
                }, indent=2)
            )]

    async def _handle_list_reports(self, arguments: dict) -> List[Any]:
        """Handle listing reports in the Force reports directory."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        include_content = arguments.get("includeContent", False)
        # List reports
        try:
            reports = self.force_engine.list_reports()
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "reports": reports,
                    "count": len(reports)
                }, indent=2)
            )]
        except Exception as e:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Failed to list reports: {str(e)}"
                }, indent=2)
            )]

    async def _handle_get_reports_directory(self, arguments: dict) -> List[Any]:
        """Handle getting the Force reports directory path."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        # Get reports directory
        try:
            reports_directory = self.force_engine.get_reports_directory()
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "reportsDirectory": str(reports_directory)
                }, indent=2)
            )]
        except Exception as e:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Failed to get reports directory: {str(e)}"
                }, indent=2)
            )]

    async def _handle_force_sync(self, arguments: dict) -> List[Any]:
        """Handle Force component synchronization between default and project directories."""
        if not self.force_engine:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Force engine not available"}, indent=2)
            )]
        
        direction = arguments.get("direction", "default-to-project")
        components = arguments.get("components", [])
        dry_run = arguments.get("dryRun", False)
        
        try:
            import shutil
            import os
            from pathlib import Path
            
            # Define source and target directories
            if direction == "default-to-project":
                source_dir = Path("./force")
                target_dir = Path("./.force")
            else:  # project-to-default
                source_dir = Path("./.force")
                target_dir = Path("./force")
            
            # Default to all components if none specified
            if not components:
                components = ["tools", "patterns", "constraints", "governance"]
            
            sync_results = []
            
            for component in components:
                source_path = source_dir / component
                target_path = target_dir / component
                
                if not source_path.exists():
                    sync_results.append({
                        "component": component,
                        "status": "skipped",
                        "reason": f"Source directory {source_path} does not exist"
                    })
                    continue
                
                if dry_run:
                    # Just report what would be synced
                    files_to_sync = []
                    if source_path.is_dir():
                        for file_path in source_path.rglob("*"):
                            if file_path.is_file():
                                files_to_sync.append(str(file_path.relative_to(source_path)))
                    
                    sync_results.append({
                        "component": component,
                        "status": "would_sync",
                        "files": files_to_sync,
                        "count": len(files_to_sync)
                    })
                else:
                    # Actually perform the sync
                    try:
                        if target_path.exists():
                            shutil.rmtree(target_path)
                        
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(source_path, target_path)
                        
                        # Count synced files
                        synced_files = len(list(target_path.rglob("*"))) if target_path.is_dir() else 1
                        
                        sync_results.append({
                            "component": component,
                            "status": "synced",
                            "files_synced": synced_files
                        })
                    except Exception as e:
                        sync_results.append({
                            "component": component,
                            "status": "error",
                            "error": str(e)
                        })
            
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "direction": direction,
                    "dry_run": dry_run,
                    "results": sync_results
                }, indent=2)
            )]
            
        except Exception as e:
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Force sync failed: {str(e)}"
                }, indent=2)
            )]

    async def _handle_yung_command(self, arguments: dict) -> List[Any]:
        """Handle legacy YUNG command execution."""
        if not self.legacy_processor:
            return [MCPCompat.TextContent(
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
            return [MCPCompat.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            return [MCPCompat.TextContent(
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

            if MCP_AVAILABLE:
                try:
                    # Minimal notification options for get_capabilities
                    class NotificationOptions:
                        tools_changed = False
                    notification_options = NotificationOptions()
                    async with MCPCompat.stdio_server() as (read_stream, write_stream):
                        init_opts = MCPCompat.InitializationOptions(
                            server_name="dev-sentinel-force",
                            server_version="2.0.0",
                            capabilities=self.server.get_capabilities(
                                notification_options,
                                experimental_capabilities={}
                            )
                        )
                        await self.server.run(
                            read_stream,
                            write_stream,
                            init_opts
                        )
                except Exception as e:
                    logger.error(f"Error running real MCP server: {e}")
                    raise
            else:
                logger.warning("MCP not available: running in stub mode, server not started.")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            if self.force_engine:
                await self.force_engine.cleanup()

async def main():
    """Main entry point for the Force MCP server."""
    
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
    parser.add_argument(
        "--no-auto-fix",
        action="store_true",
        help="Disable automatic fixing of Force components at startup"
    )
    parser.add_argument(
        "--validation-only",
        action="store_true",
        help="Run validation only and exit (don't start MCP server)"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Enable auto-fix unless explicitly disabled
    auto_fix = not args.no_auto_fix
    
    if args.validation_only:
        # Run validation only mode
        logger.info("🔍 Running Force validation only mode...")
        server = ForceMCPServer(force_directory=args.force_dir, auto_fix=auto_fix)
        validation_passed = await server._run_startup_validation_and_fix()
        if validation_passed:
            logger.info("✅ Validation passed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Validation failed")
            sys.exit(1)
    
    server = ForceMCPServer(force_directory=args.force_dir, auto_fix=auto_fix)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
