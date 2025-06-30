"""
Core Force engine for the Dev Sentinel agentic development system.

This module provides the main execution engine for Force components,
handling schema validation, tool execution, pattern application,
constraint enforcement, learning data collection, and governance.
"""

import os
import json
import logging
import asyncio
import traceback
import subprocess
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timezone
from pathlib import Path

# Try to import jsonschema, fall back gracefully if not available
try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    logging.warning("jsonschema not available - validation will be limited")
    JSONSCHEMA_AVAILABLE = False
    
    class ValidationError(Exception):
        pass
    
    def validate(instance, schema):
        # Basic validation placeholder
        if not isinstance(instance, dict):
            raise ValidationError("Instance must be a dictionary")

# Configure logging
logger = logging.getLogger(__name__)

class ForceEngineError(Exception):
    """Base exception for Force engine errors."""
    pass

class SchemaValidationError(ForceEngineError):
    """Raised when schema validation fails."""
    pass

class ToolExecutionError(ForceEngineError):
    """Raised when tool execution fails."""
    pass

class ForceEngine:
    """
    Core execution engine for the Force agentic development system.
    
    Provides schema validation, tool execution, pattern application,
    constraint enforcement, learning data collection, and governance
    policy enforcement.
    """
    
    # Module import flags to prevent circular imports
    _tools_module_imported = False
    _patterns_module_imported = False
    _constraints_module_imported = False
    _learning_module_imported = False
    _governance_module_imported = False
    
    def __init__(self, force_directory: Optional[str] = None):
        """
        Initialize the Force engine.
        
        Args:
            force_directory: Path to the .force directory. If None,
                           will search for it in standard locations.
        """
        self.force_dir = self._find_force_directory(force_directory)
        self.schemas_dir = self.force_dir / "schemas"
        self.tools_dir = self.force_dir / "tools"
        self.patterns_dir = self.force_dir / "patterns"
        self.constraints_dir = self.force_dir / "constraints"
        self.learning_dir = self.force_dir / "learning"
        self.governance_dir = self.force_dir / "governance"
        
        # Load and cache components
        self._master_schema = None
        self._tools_cache = {}
        self._patterns_cache = {}
        self._constraints_cache = {}
        self._governance_policies = {}
        
        # Performance tracking
        self._execution_metrics = {}
        self._learning_records = []
        
        # Initialize tool executor
        from .tool_executor import ToolExecutor
        self.tool_executor = ToolExecutor(self)
        
        # Initialize modular components
        self._initialize_modular_components()
        
    def _find_force_directory(self, force_directory: Optional[str]) -> Path:
        """Find the Force directory in standard locations."""
        if force_directory:
            path = Path(force_directory)
            if path.exists():
                return path
            raise ForceEngineError(f"Force directory not found: {force_directory}")
        
        # Search in standard locations (prioritize root .force directory)
        current_dir = Path.cwd()
        search_paths = [
            current_dir / ".force",
            current_dir / "docs" / ".force",
            current_dir.parent / ".force",
            current_dir.parent / "docs" / ".force",
        ]
        
        for path in search_paths:
            if path.exists() and path.is_dir():
                logger.info(f"Found Force directory: {path}")
                return path
        
        raise ForceEngineError("Force directory not found in standard locations")
    
    def get_master_schema(self) -> Dict[str, Any]:
        """Load and return the master Force schema."""
        if self._master_schema is None:
            schema_path = self.schemas_dir / "force-schema.json"
            if not schema_path.exists():
                raise ForceEngineError(f"Master schema not found: {schema_path}")
            
            with open(schema_path, 'r') as f:
                self._master_schema = json.load(f)
                logger.info("Loaded master Force schema")
        
        return self._master_schema
    
    def validate_component(self, component: Dict[str, Any], component_type: str) -> None:
        """
        Validate a Force component against the schema.
        
        Args:
            component: The component data to validate
            component_type: Type of component (tool, pattern, constraint, etc.)
        """
        try:
            schema = self.get_master_schema()
            
            if component_type not in schema.get("definitions", {}):
                raise SchemaValidationError(f"Unknown component type: {component_type}")
            
            component_schema = {
                "$ref": f"#/definitions/{component_type.title()}"
            }
            
            # Create a complete schema for validation
            validation_schema = {
                **schema,
                **component_schema
            }
            
            validate(instance=component, schema=validation_schema)
            logger.debug(f"Successfully validated {component_type}: {component.get('id', 'unknown')}")
            
        except ValidationError as e:
            error_msg = f"Schema validation failed for {component_type}: {getattr(e, 'message', str(e))}"
            logger.error(error_msg)
            raise SchemaValidationError(error_msg) from e
    
    def load_tools(self) -> Dict[str, Dict[str, Any]]:
        """Load and validate all tools."""
        if not self._tools_cache:
            self._tools_cache = self._load_component_directory(
                self.tools_dir, "Tool"
            )
        return self._tools_cache
    
    def load_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load and validate all patterns."""
        if not self._patterns_cache:
            self._patterns_cache = self._load_component_directory(
                self.patterns_dir, "Pattern"
            )
        return self._patterns_cache
    
    def load_constraints(self) -> Dict[str, Dict[str, Any]]:
        """Load and validate all constraints."""
        if not self._constraints_cache:
            self._constraints_cache = self._load_component_directory(
                self.constraints_dir, "Constraint"
            )
        return self._constraints_cache
    
    def load_governance_policies(self) -> Dict[str, Dict[str, Any]]:
        """Load and validate all governance policies."""
        if not self._governance_policies:
            self._governance_policies = self._load_component_directory(
                self.governance_dir, "GovernancePolicy"
            )
        return self._governance_policies
    
    def _load_component_directory(self, directory: Path, component_type: str) -> Dict[str, Dict[str, Any]]:
        """Load and validate all JSON files in a component directory."""
        components = {}
        
        if not directory.exists():
            logger.warning(f"Component directory not found: {directory}")
            return components
        
        for json_file in directory.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Handle both single components and arrays of components
                if isinstance(data, list):
                    for component in data:
                        self.validate_component(component, component_type)
                        components[component["id"]] = component
                elif isinstance(data, dict):
                    if "id" in data:
                        # Single component
                        self.validate_component(data, component_type)
                        components[data["id"]] = data
                    else:
                        # Object with component arrays
                        for key, component_list in data.items():
                            if isinstance(component_list, list):
                                for component in component_list:
                                    if isinstance(component, dict) and "id" in component:
                                        self.validate_component(component, component_type)
                                        components[component["id"]] = component
                
                logger.info(f"Loaded {len([c for c in components.values() if c])} {component_type}s from {json_file}")
                
            except Exception as e:
                logger.error(f"Error loading {component_type} from {json_file}: {e}")
                continue
        
        return components
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any], 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a Force tool with validation and monitoring.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Parameters for tool execution
            context: Execution context information
            
        Returns:
            Execution result with metrics and status
        """
        start_time = datetime.now(timezone.utc)
        execution_id = f"{tool_id}_{start_time.strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Load tool definition
            tools = self.load_tools()
            if tool_id not in tools:
                raise ToolExecutionError(f"Tool not found: {tool_id}")
            
            tool = tools[tool_id]
            
            # Validate parameters against tool schema
            if "parameters" in tool and "schema" in tool["parameters"]:
                try:
                    validate(instance=parameters, schema=tool["parameters"]["schema"])
                except ValidationError as e:
                    raise ToolExecutionError(f"Parameter validation failed: {getattr(e, 'message', str(e))}")
            
            # Check governance policies
            await self._check_governance_policies(tool_id, parameters, context)
            
            # Execute pre-conditions
            if "validation" in tool and "preConditions" in tool["validation"]:
                await self._validate_conditions(tool["validation"]["preConditions"], context)
            
            # Execute the tool
            logger.info(f"Executing tool {tool_id} with execution ID {execution_id}")
            
            result = await self.tool_executor.execute_tool_command(tool, parameters, context)
            
            # Execute post-conditions
            if "validation" in tool and "postConditions" in tool["validation"]:
                await self._validate_conditions(tool["validation"]["postConditions"], context)
            
            # Record successful execution
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            learning_record = {
                "id": execution_id,
                "timestamp": start_time.isoformat(),
                "context": context or {},
                "toolId": tool_id,
                "outcome": {
                    "success": True,
                    "executionTime": execution_time,
                    "metrics": {
                        "executionTimeMs": execution_time * 1000,
                        "memoryUsageMB": 0,  # TODO: Implement memory tracking
                        "successRate": 1.0,
                        "errorCount": 0,
                        "lastExecuted": datetime.now(timezone.utc).isoformat()
                    }
                },
                "insights": []
            }
            
            await self._record_learning_data(learning_record)
            
            return {
                "success": True,
                "executionId": execution_id,
                "result": result,
                "executionTime": execution_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            # Record failed execution
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            learning_record = {
                "id": execution_id,
                "timestamp": start_time.isoformat(),
                "context": context or {},
                "toolId": tool_id,
                "outcome": {
                    "success": False,
                    "executionTime": execution_time,
                    "errorMessage": str(e)
                },
                "insights": [{
                    "type": "error-pattern",
                    "description": f"Tool execution failed: {str(e)}",
                    "confidence": 1.0
                }]
            }
            
            await self._record_learning_data(learning_record)
            
            logger.error(f"Tool execution failed for {tool_id}: {e}")
            return {
                "success": False,
                "executionId": execution_id,
                "error": str(e),
                "executionTime": execution_time,
                "timestamp": start_time.isoformat()
            }
    
    def execute_tool_sync(self, tool_id: str, parameters: Dict[str, Any], 
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synchronous wrapper for execute_tool.
        
        Args:
            tool_id: ID of the tool to execute
            parameters: Parameters for tool execution
            context: Execution context information
            
        Returns:
            Execution result with metrics and status
        """
        import asyncio
        
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in a loop, we need to create a new one in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.execute_tool(tool_id, parameters, context))
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(self.execute_tool(tool_id, parameters, context))

    async def _check_governance_policies(self, tool_id: str, parameters: Dict[str, Any], 
                                       context: Optional[Dict[str, Any]]) -> None:
        """Check governance policies before tool execution."""
        policies = self.load_governance_policies()
        
        for policy_id, policy in policies.items():
            # TODO: Implement policy evaluation logic
            logger.debug(f"Checking governance policy: {policy_id}")
    
    async def _validate_conditions(self, conditions: List[Dict[str, Any]], 
                                 context: Optional[Dict[str, Any]]) -> None:
        """Validate pre/post conditions."""
        for condition in conditions:
            # TODO: Implement condition validation logic
            logger.debug(f"Validating condition: {condition.get('rule', 'unknown')}")
    
    async def _record_learning_data(self, learning_record: Dict[str, Any]) -> None:
        """Record learning data for system improvement."""
        self._learning_records.append(learning_record)
        
        # Periodically persist learning data
        if len(self._learning_records) >= 100:
            await self._persist_learning_data()
    
    async def _persist_learning_data(self) -> None:
        """Persist accumulated learning data to files."""
        if not self._learning_records:
            return
        
        learning_file = self.learning_dir / "execution-analytics.json"
        
        # Load existing data
        existing_data = []
        if learning_file.exists():
            try:
                with open(learning_file, 'r') as f:
                    existing_data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load existing learning data: {e}")
        
        # Append new records
        existing_data.extend(self._learning_records)
        
        # Save updated data
        learning_file.parent.mkdir(parents=True, exist_ok=True)
        with open(learning_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        logger.info(f"Persisted {len(self._learning_records)} learning records")
        self._learning_records.clear()
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get a list of all available tools with their metadata."""
        tools = self.load_tools()
        return [
            {
                "id": tool_id,
                "name": tool.get("name", tool_id),
                "description": tool.get("description", ""),
                "category": tool.get("category", "unknown"),
                "version": tool.get("version", "1.0.0")
            }
            for tool_id, tool in tools.items()
        ]
    
    def get_pattern_list(self) -> List[Dict[str, Any]]:
        """Get a list of all available patterns with their metadata."""
        patterns = self.load_patterns()
        return [
            {
                "id": pattern_id,
                "name": pattern.get("name", pattern_id),
                "description": pattern.get("description", ""),
                "category": pattern.get("category", "unknown"),
                "version": pattern.get("version", "1.0.0")
            }
            for pattern_id, pattern in patterns.items()
        ]
    
    def list_tools(self) -> List[str]:
        """Get a list of all available tool IDs."""
        tools = self.load_tools()
        return list(tools.keys())
    
    def list_patterns(self) -> List[str]:
        """Get a list of all available pattern IDs."""
        patterns = self.load_patterns()
        return list(patterns.keys())
    
    def list_constraints(self) -> List[str]:
        """Get a list of all available constraint IDs."""
        constraints = self.load_constraints()
        return list(constraints.keys())
    
    def list_governance_policies(self) -> List[str]:
        """Get a list of all available governance policy IDs."""
        policies = self.load_governance_policies()
        return list(policies.keys())
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific tool by ID."""
        tools = self.load_tools()
        return tools.get(tool_id)
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by ID."""
        patterns = self.load_patterns()
        return patterns.get(pattern_id)
    
    def get_constraint(self, constraint_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific constraint by ID."""
        constraints = self.load_constraints()
        return constraints.get(constraint_id)

    def get_reports_directory(self) -> Path:
        """Get the default reports directory path."""
        return self.force_dir / "reports"
    
    def ensure_reports_directory(self) -> Path:
        """Ensure the reports directory exists and return its path."""
        reports_dir = self.get_reports_directory()
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir
    
    def generate_report_filename(self, report_type: str, timestamp: Optional[datetime] = None) -> str:
        """Generate a standardized report filename."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        return f"FORCE_{report_type.upper()}_REPORT_{timestamp_str}.md"
    
    def save_report(self, content: str, report_type: str, timestamp: Optional[datetime] = None, 
                   custom_filename: Optional[str] = None) -> Path:
        """
        Save a report to the Force reports directory.
        
        Args:
            content: Report content to save
            report_type: Type of report (completion, git_task, doc_vcs, etc.)
            timestamp: Optional timestamp for filename generation
            custom_filename: Optional custom filename (should include .md extension)
            
        Returns:
            Path to the saved report file
        """
        reports_dir = self.ensure_reports_directory()
        
        if custom_filename:
            filename = custom_filename
        else:
            filename = self.generate_report_filename(report_type, timestamp)
        
        report_path = reports_dir / filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Report saved: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Failed to save report {report_path}: {e}")
            raise ForceEngineError(f"Report save failed: {e}")
    
    def list_reports(self) -> List[Dict[str, Any]]:
        """List all reports in the Force reports directory."""
        reports_dir = self.get_reports_directory()
        
        if not reports_dir.exists():
            return []
        
        reports = []
        for report_file in reports_dir.glob("*.md"):
            try:
                stat = report_file.stat()
                reports.append({
                    "filename": report_file.name,
                    "path": str(report_file),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                })
            except Exception as e:
                logger.warning(f"Error reading report file {report_file}: {e}")
        
        return sorted(reports, key=lambda x: x["modified"], reverse=True)

    async def cleanup(self) -> None:
        """Cleanup and persist any pending data."""
        await self._persist_learning_data()
        logger.info("Force engine cleanup completed")
    
    def _initialize_modular_components(self):
        """Initialize the modular components system."""
        try:
            # Initialize the tools module if not already done
            if not ForceEngine._tools_module_imported:
                from . import tools
                self.tool_registry = tools.ToolRegistry(self)
                ForceEngine._tools_module_imported = True
                logger.info("Imported tools module")
                
            # Initialize the patterns module if not already done
            if not ForceEngine._patterns_module_imported:
                from . import patterns
                self.pattern_registry = patterns.initialize(self)
                ForceEngine._patterns_module_imported = True
                logger.info("Initialized patterns module")
                
            # Initialize the constraints module if not already done
            if not ForceEngine._constraints_module_imported:
                from . import constraints
                self.constraint_registry = constraints.ConstraintRegistry(self)
                ForceEngine._constraints_module_imported = True
                logger.info("Imported constraints module")
                
            # Initialize the learning module if not already done
            if not ForceEngine._learning_module_imported:
                from . import learning
                self.learning_manager = learning.initialize(self)
                ForceEngine._learning_module_imported = True
                logger.info("Initialized learning module")
                
            # Initialize the governance module if not already done
            if not ForceEngine._governance_module_imported:
                from . import governance
                self.governance_manager = governance.initialize(self)
                ForceEngine._governance_module_imported = True
                logger.info("Initialized governance module")
                
            # Load components from the .force directory
            self._load_force_components()
            
        except Exception as e:
            logger.error(f"Error initializing modular components: {e}")
            traceback.print_exc()
            
    def _load_force_components(self):
        """Load components from the .force directory into the modular system."""
        try:
            # Import necessary modules
            from . import tools
            from . import patterns
            from . import constraints
            
            # Load tool definitions from the .force directory
            if hasattr(tools, 'load_tool_definitions'):
                tools.load_tool_definitions(self.force_dir)
                logger.info("Loaded tool definitions from .force directory")
            else:
                logger.warning("Tool definition loader not available")
            
            # Load pattern definitions
            if hasattr(patterns, 'load_json_patterns'):
                patterns.load_json_patterns()
                logger.info("Loaded pattern definitions from .force directory")
            else:
                logger.warning("Pattern definition loader not available")
            
            # Load constraint definitions
            if hasattr(constraints, 'load_constraint_definitions'):
                constraints.load_constraint_definitions(self.force_dir)
                logger.info("Loaded constraint definitions from .force directory")
            else:
                logger.warning("Constraint definition loader not available")
                
            # Extend registries with JSON definitions
            if hasattr(self, 'tool_registry') and hasattr(tools, 'extend_tool_registry'):
                tools.extend_tool_registry(self.tool_registry)
                logger.info("Extended tool registry with JSON tool definitions")
                
            if hasattr(self, 'constraint_registry') and hasattr(constraints, 'extend_constraint_registry'):
                constraints.extend_constraint_registry(self.constraint_registry)
                logger.info("Extended constraint registry with JSON constraint definitions")
            
        except ImportError as e:
            logger.error(f"Error importing modules for Force components: {e}")
            traceback.print_exc()
        except Exception as e:
            logger.error(f"Error loading Force components: {e}")
            traceback.print_exc()
    
    async def execute_json_tool(self, 
                           tool_definition, 
                           parameters: Dict[str, Any], 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a tool defined in JSON.
        
        Args:
            tool_definition: Tool definition object
            parameters: Parameters for tool execution
            context: Optional execution context
            
        Returns:
            Execution result
        """
        start_time = datetime.now(timezone.utc)
        tool_id = tool_definition.id
        execution_id = f"{tool_id}_{start_time.strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            logger.info(f"Executing JSON-defined tool {tool_id} with execution ID {execution_id}")
            
            # Validate parameters against schema if available
            if "parameters" in tool_definition.data:
                schema = tool_definition.data.get("parameters", {}).get("schema")
                if schema:
                    try:
                        if JSONSCHEMA_AVAILABLE:
                            validate(instance=parameters, schema=schema)
                    except ValidationError as e:
                        raise ToolExecutionError(f"Parameter validation failed: {getattr(e, 'message', str(e))}")
            
            # Execute the tool commands
            result = await self._execute_json_tool_commands(
                tool_definition.execution.get("commands", []),
                parameters,
                context
            )
            
            # Record successful execution
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._record_json_tool_execution(
                tool_id, 
                execution_id, 
                parameters, 
                result, 
                execution_time, 
                True
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing JSON tool {tool_id}: {e}")
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            await self._record_json_tool_execution(
                tool_id, 
                execution_id, 
                parameters, 
                {"error": str(e)}, 
                execution_time, 
                False
            )
            
            raise ToolExecutionError(f"JSON tool execution failed: {str(e)}") from e
            
    async def _execute_json_tool_commands(self, 
                                       commands: List[Dict[str, Any]], 
                                       parameters: Dict[str, Any], 
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute commands defined in a JSON tool.
        
        Args:
            commands: List of command definitions
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            Execution result
        """
        results = {}
        execution_context = {**(context or {}), **parameters}
        
        for i, command in enumerate(commands):
            try:
                action = command.get("action")
                if not action:
                    logger.error(f"Command {i+1} has no action defined")
                    results[f"command_{i+1}_error"] = "No action defined"
                    continue
                    
                cmd_params = command.get("parameters", {})
                description = command.get("description", f"Command {i+1}")
                
                logger.info(f"Executing command: {action} - {description}")
                
                # Process parameters with template substitution from context
                processed_params = self._process_template_params(cmd_params, execution_context)
                
                # Handle different command actions
                if action.startswith("git "):
                    # Git command
                    cmd_parts = action.split()
                    result = await self._execute_system_command(cmd_parts, processed_params)
                elif hasattr(self.tool_executor, action):
                    # Tool executor method
                    method = getattr(self.tool_executor, action)
                    result = await method(processed_params, execution_context)
                else:
                    # Try to find a tool with this ID
                    result = await self.execute_tool(action, processed_params, execution_context)
                
                # Store result in context for subsequent commands
                results[f"command_{i+1}"] = result
                execution_context[f"{action}_result"] = result
                
            except Exception as e:
                logger.error(f"Error executing command {i+1}: {e}")
                results[f"command_{i+1}_error"] = str(e)
                
                # Check error handling strategy
                error_handling = command.get("on_error", "stop")
                if error_handling == "continue":
                    continue
                elif error_handling == "stop":
                    break
                elif error_handling == "fail":
                    raise ToolExecutionError(f"Command {i+1} failed: {str(e)}") from e
                
        return {
            "success": True,
            "command_results": results,
            "final_context": execution_context
        }

    def _process_template_params(self, 
                               params: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process template parameters, substituting values from context.
        
        Args:
            params: Parameters with potential template values
            context: Execution context with values
            
        Returns:
            Processed parameters
        """
        result = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                context_key = value[2:-1]
                if context_key in context:
                    result[key] = context[context_key]
                else:
                    result[key] = value  # Keep original if not found
            else:
                result[key] = value
                
        return result
        
    async def _execute_system_command(self, 
                                    cmd_parts: List[str], 
                                    params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a system command.
        
        Args:
            cmd_parts: Command parts (e.g. ["git", "status"])
            params: Additional parameters
            
        Returns:
            Command execution result
        """
        try:
            # Build final command
            cmd = list(cmd_parts)
            
            # Add parameters as command arguments
            for key, value in params.items():
                if isinstance(value, bool):
                    if value:
                        cmd.append(f"--{key}")
                elif value is not None:
                    cmd.append(f"--{key}={value}")
            
            logger.info(f"Executing system command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "success": True,
                "output": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"System command failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": e.stdout if hasattr(e, 'stdout') else "",
                "stderr": e.stderr if hasattr(e, 'stderr') else "",
                "returncode": e.returncode
            }
        except Exception as e:
            logger.error(f"Error executing system command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _record_json_tool_execution(self,
                                       tool_id: str,
                                       execution_id: str,
                                       parameters: Dict[str, Any],
                                       result: Dict[str, Any],
                                       execution_time: float,
                                       success: bool) -> None:
        """
        Record execution of a JSON-defined tool.
        
        Args:
            tool_id: Tool ID
            execution_id: Unique execution ID
            parameters: Tool parameters
            result: Execution result
            execution_time: Execution time in seconds
            success: Whether execution was successful
        """
        if hasattr(self, 'learning_manager'):
            await self.learning_manager.record_execution(
                component_type="tool",
                component_id=tool_id,
                parameters=parameters,
                result=result,
                execution_time=execution_time,
                success=success
            )
