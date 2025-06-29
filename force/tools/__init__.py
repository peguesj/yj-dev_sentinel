"""
Force Tool System

Provides the base classes and registration mechanism for Force tools.
"""

import importlib
import logging
import os
import pkgutil
import json
from typing import Dict, Any, List, Optional, Type, Set

logger = logging.getLogger(__name__)

class BaseToolExecutor:
    """Base class for all tool executors."""
    
    tool_id = None
    tool_category = None
    tool_name = None
    tool_description = None
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the tool with the provided parameters."""
        raise NotImplementedError("Tool executors must implement execute()")
        
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters against tool schema."""
        # Default implementation relies on schema validation in Force engine
        return True
        
    def get_metadata(self) -> Dict[str, Any]:
        """Return tool metadata."""
        return {
            "id": self.tool_id,
            "name": self.tool_name,
            "category": self.tool_category,
            "description": self.tool_description,
        }

    @classmethod
    def supports_tool_id(cls, tool_id: str) -> bool:
        """Check if this executor supports the given tool ID."""
        return cls.tool_id == tool_id


class ToolRegistry:
    """Registry for all tool executors."""
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        self._executors: Dict[str, Type[BaseToolExecutor]] = {}
        self._discovered = False
        
    def register_tool_executor(self, executor_class: Type[BaseToolExecutor]) -> None:
        """Register a tool executor class."""
        if executor_class.tool_id is None:
            logger.warning(f"Skipping registration of {executor_class.__name__} with no tool_id")
            return
            
        if executor_class.tool_id in self._executors:
            logger.warning(f"Tool executor for {executor_class.tool_id} already registered, overriding")
            
        self._executors[executor_class.tool_id] = executor_class
        logger.debug(f"Registered tool executor for {executor_class.tool_id}")
        
    def get_executor_class(self, tool_id: str) -> Optional[Type[BaseToolExecutor]]:
        """Get the executor class for a tool ID."""
        self._ensure_discovery()
        return self._executors.get(tool_id)
        
    def create_executor(self, tool_id: str) -> Optional[BaseToolExecutor]:
        """Create an executor instance for a tool ID."""
        executor_class = self.get_executor_class(tool_id)
        if executor_class:
            return executor_class(self.force_engine)
        return None
        
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get a list of all available tools."""
        self._ensure_discovery()
        result = []
        for tool_id, executor_class in self._executors.items():
            instance = executor_class(self.force_engine)
            result.append(instance.get_metadata())
        return result
        
    def _ensure_discovery(self) -> None:
        """Ensure tool discovery has run."""
        if not self._discovered:
            self._discover_tools()
            self._discovered = True
            
    def _discover_tools(self) -> None:
        """Discover and register all tool executors."""
        # First, import any modules in the tools package
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for _, name, ispkg in pkgutil.iter_modules([current_dir]):
            if not name.startswith('_'):
                importlib.import_module(f'force.tools.{name}')
                
        # Then register any BaseToolExecutor subclasses
        for subclass in BaseToolExecutor.__subclasses__():
            self.register_tool_executor(subclass)
            
        # Add JSON-defined tool executors
        extend_tool_registry(self)
        
        logger.info(f"Discovered {len(self._executors)} tool executors")
        
# Function to load tool definitions from the .force directory
def load_tool_definitions(force_dir):
    """
    Load tool definitions from the .force directory.
    
    Args:
        force_dir: Path to the .force directory
    """
    try:
        tools_dir = force_dir / "tools"
        if tools_dir.exists() and tools_dir.is_dir():
            logger.info(f"Loading tool definitions from {tools_dir}")
            for json_file in tools_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        tool_data = json.load(f)
                        
                    # Handle both single tools and collections
                    if "id" in tool_data and isinstance(tool_data.get("id"), str):
                        logger.info(f"Found single tool definition in {json_file}")
                        definition = ToolDefinition.from_dict(tool_data)
                        tool_definition_registry.register(definition)
                    elif "tools" in tool_data and isinstance(tool_data.get("tools"), list):
                        tools_list = tool_data.get("tools", [])
                        logger.info(f"Found {len(tools_list)} tool definitions in {json_file}")
                        for tool_def in tools_list:
                            if isinstance(tool_def, dict) and "id" in tool_def:
                                definition = ToolDefinition.from_dict(tool_def)
                                tool_definition_registry.register(definition)
                            else:
                                logger.warning(f"Invalid tool definition in {json_file}")
                    else:
                        logger.warning(f"Unknown tool definition format in {json_file}")
                        
                except Exception as e:
                    logger.error(f"Error loading tool definition from {json_file}: {e}")
        else:
            logger.warning(f"Tool definitions directory not found: {tools_dir}")
            
    except Exception as e:
        logger.error(f"Error loading tool definitions: {e}")
        import traceback
        traceback.print_exc()

class ToolDefinition:
    """Represents a tool definition loaded from a JSON file."""
    
    def __init__(self, definition_data: Dict[str, Any]):
        """Initialize a tool definition from JSON data."""
        self.data = definition_data
        self.id = definition_data.get("id")
        self.name = definition_data.get("name")
        self.category = definition_data.get("category")
        self.description = definition_data.get("description")
        self.parameters = definition_data.get("parameters", {})
        self.execution = definition_data.get("execution", {})
        self.metadata = definition_data.get("metadata", {})
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the definition to a dictionary."""
        return self.data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolDefinition':
        """Create a tool definition from a dictionary."""
        return cls(data)


class ToolDefinitionRegistry:
    """Registry for tool definitions loaded from JSON."""
    
    def __init__(self):
        self._definitions: Dict[str, ToolDefinition] = {}
        
    def register(self, definition: ToolDefinition) -> None:
        """Register a tool definition."""
        if not definition.id:
            logger.warning("Skipping registration of tool definition with no ID")
            return
        
        if definition.id in self._definitions:
            logger.warning(f"Tool definition for {definition.id} already registered, overriding")
            
        self._definitions[definition.id] = definition
        logger.info(f"Registered tool definition for {definition.id}")
        
    def get(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get a tool definition by ID."""
        return self._definitions.get(tool_id)
        
    def get_all(self) -> Dict[str, ToolDefinition]:
        """Get all registered tool definitions."""
        return self._definitions


class JsonToolExecutor(BaseToolExecutor):
    """Executor for JSON-defined tools."""
    
    def __init__(self, force_engine, definition: ToolDefinition):
        super().__init__(force_engine)
        self.definition = definition
        self.tool_id = definition.id
        self.tool_name = definition.name
        self.tool_category = definition.category
        self.tool_description = definition.description
        
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the tool using the JSON definition."""
        # This implementation will depend on how your tool execution system works
        # For now, we'll delegate to the force_engine's tool execution
        if hasattr(self.force_engine, "execute_json_tool"):
            return await self.force_engine.execute_json_tool(self.definition, parameters, context)
        else:
            raise NotImplementedError("JSON tool execution not implemented in the Force engine")


# Global tool definition registry
tool_definition_registry = ToolDefinitionRegistry()

def register_json_tool_executors(registry: ToolRegistry) -> None:
    """
    Register JSON tool definitions as executors in the given registry.
    
    Args:
        registry: ToolRegistry to register the executors with
    """
    for tool_id, definition in tool_definition_registry.get_all().items():
        # Check if there's already a native executor for this tool
        if registry.get_executor_class(tool_id):
            logger.debug(f"Native executor already exists for {tool_id}, skipping JSON registration")
            continue
            
        # Create a specialized executor class for this tool definition
        class_name = f"{tool_id.title().replace('_', '')}JsonExecutor"
        
        # Create a dynamic executor class
        JsonToolExecutorClass = type(
            class_name,
            (JsonToolExecutor,),
            {
                "tool_id": tool_id,
                "tool_name": definition.name,
                "tool_category": definition.category,
                "tool_description": definition.description
            }
        )
        
        # Register the executor class
        registry.register_tool_executor(JsonToolExecutorClass)
        logger.info(f"Registered JSON tool executor for {tool_id}")


# Update the discovery method to include JSON-defined tools
def extend_tool_registry(registry: ToolRegistry) -> None:
    """
    Extend the given tool registry with JSON-defined tools.
    
    Args:
        registry: ToolRegistry to extend
    """
    register_json_tool_executors(registry)
