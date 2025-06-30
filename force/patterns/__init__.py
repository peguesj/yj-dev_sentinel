"""
Force Pattern System

Provides the base classes and registration mechanism for Force patterns.
"""

import importlib
import logging
import os
import pkgutil
from typing import Dict, Any, List, Optional, Type, Set, Union, Callable, Awaitable

logger = logging.getLogger(__name__)

class PatternStep:
    """Represents a single step in a pattern."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    async def execute(self, context: Dict[str, Any], force_engine) -> Dict[str, Any]:
        """Execute this pattern step."""
        raise NotImplementedError("Pattern steps must implement execute()")


class ToolStep(PatternStep):
    """A pattern step that executes a tool."""
    
    def __init__(self, name: str, description: str, tool_id: str, parameters: Dict[str, Any]):
        super().__init__(name, description)
        self.tool_id = tool_id
        self.parameters = parameters
        
    async def execute(self, context: Dict[str, Any], force_engine) -> Dict[str, Any]:
        """Execute the tool."""
        # Replace template parameters with context values
        processed_params = {}
        for key, value in self.parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                context_key = value[2:-1]  # Remove ${ and }
                if context_key in context:
                    processed_params[key] = context[context_key]
                else:
                    logger.warning(f"Context key {context_key} not found for parameter {key}")
                    processed_params[key] = value
            else:
                processed_params[key] = value
                
        # Execute the tool
        result = await force_engine.execute_tool(self.tool_id, processed_params, context)
        
        # Update context with result
        context[self.name + "_result"] = result
        return result


class ConditionalStep(PatternStep):
    """A pattern step with conditional execution."""
    
    def __init__(self, name: str, description: str, condition: Dict[str, Any], 
                 then_step: PatternStep, else_step: Optional[PatternStep] = None):
        super().__init__(name, description)
        self.condition = condition
        self.then_step = then_step
        self.else_step = else_step
        
    async def execute(self, context: Dict[str, Any], force_engine) -> Dict[str, Any]:
        """Execute based on condition."""
        if self._evaluate_condition(context):
            return await self.then_step.execute(context, force_engine)
        elif self.else_step:
            return await self.else_step.execute(context, force_engine)
        return {"condition_result": False}
        
    def _evaluate_condition(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition against the context."""
        condition_type = self.condition.get("type")
        if condition_type == "equals":
            field = self.condition.get("field")
            value = self.condition.get("value")
            if field in context:
                return context[field] == value
        elif condition_type == "exists":
            field = self.condition.get("field")
            return field in context
        return False


class PatternImplementation:
    """Implementation of a pattern with execution steps."""
    
    def __init__(self, pattern_id: str, name: str, description: str, steps: List[PatternStep]):
        self.pattern_id = pattern_id
        self.name = name
        self.description = description
        self.steps = steps
        
    async def execute(self, parameters: Dict[str, Any], force_engine) -> Dict[str, Any]:
        """Execute the pattern."""
        context = parameters.copy()
        results = []
        
        for step in self.steps:
            try:
                step_result = await step.execute(context, force_engine)
                results.append({
                    "step": step.name,
                    "success": True,
                    "result": step_result
                })
            except Exception as e:
                logger.error(f"Error executing step {step.name}: {e}")
                results.append({
                    "step": step.name,
                    "success": False,
                    "error": str(e)
                })
                # Determine whether to continue based on step failure handling
                # For now, we'll stop on first error
                break
                
        return {
            "pattern_id": self.pattern_id,
            "success": all(result["success"] for result in results),
            "steps": results,
            "context": context
        }


class JsonPattern:
    """Bridge class for JSON pattern definitions."""
    
    def __init__(self, pattern_def: Dict[str, Any]):
        self.id = pattern_def.get("id")
        self.name = pattern_def.get("name")
        self.description = pattern_def.get("description")
        self.steps = []
        
        for step_def in pattern_def.get("steps", []):
            if step_def["type"] == "tool":
                step = ToolStep(
                    name=step_def.get("name"),
                    description=step_def.get("description"),
                    tool_id=step_def.get("tool_id"),
                    parameters=step_def.get("parameters", {})
                )
            else:
                logger.warning(f"Unknown step type: {step_def['type']}")
                continue
            self.steps.append(step)
    
    async def execute(self, context: Dict[str, Any], force_engine) -> Dict[str, Any]:
        """Execute all steps in the pattern."""
        results = {}
        for step in self.steps:
            step_result = await step.execute(context, force_engine)
            results[step.name] = step_result
        return results


class PatternRegistry:
    """Registry for Force patterns."""
    
    _instance = None
    _patterns: Dict[str, Union[Type[PatternStep], JsonPattern]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, pattern_id: str, pattern: Union[Type[PatternStep], JsonPattern]):
        """Register a pattern."""
        cls._patterns[pattern_id] = pattern
        logger.info(f"Registered pattern: {pattern_id}")
    
    @classmethod
    def get_pattern(cls, pattern_id: str) -> Optional[Union[Type[PatternStep], JsonPattern]]:
        """Get a pattern by ID."""
        return cls._patterns.get(pattern_id)
    
    @classmethod
    def list_patterns(cls) -> List[str]:
        """List all registered patterns."""
        return list(cls._patterns.keys())

def load_json_patterns():
    """Load and register JSON pattern definitions."""
    import json
    import glob
    from pathlib import Path
    
    pattern_paths = [
        Path(__file__).parent.parent.parent / ".force" / "patterns",
        Path(__file__).parent.parent.parent / "docs" / ".force" / "patterns"
    ]
    
    for pattern_dir in pattern_paths:
        if not pattern_dir.exists():
            continue
            
        for pattern_file in pattern_dir.glob("*.json"):
            try:
                with open(pattern_file) as f:
                    pattern_def = json.load(f)
                    pattern = JsonPattern(pattern_def)
                    PatternRegistry.register(pattern.id, pattern)
            except Exception as e:
                logger.error(f"Error loading pattern from {pattern_file}: {e}")

# Initialize pattern system
def init_patterns():
    """Initialize the pattern system."""
    load_json_patterns()

def initialize(force_engine):
    """
    Initialize the pattern system for the Force engine.
    
    Args:
        force_engine: The Force engine instance
        
    Returns:
        PatternRegistry instance
    """
    # Initialize patterns
    init_patterns()
    
    # Create and return registry
    registry = PatternRegistry()
    return registry
