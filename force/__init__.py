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
        
    def _find_force_directory(self, force_directory: Optional[str]) -> Path:
        """Find the Force directory in standard locations."""
        if force_directory:
            path = Path(force_directory)
            if path.exists():
                return path
            raise ForceEngineError(f"Force directory not found: {force_directory}")
        
        # Search in standard locations
        current_dir = Path.cwd()
        search_paths = [
            current_dir / "docs" / ".force",
            current_dir / ".force",
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

    async def cleanup(self) -> None:
        """Cleanup and persist any pending data."""
        await self._persist_learning_data()
        logger.info("Force engine cleanup completed")
