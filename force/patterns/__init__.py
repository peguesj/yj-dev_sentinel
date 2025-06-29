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


class PatternRegistry:
    """Registry for pattern implementations."""
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        self._patterns: Dict[str, PatternImplementation] = {}
        self._discovered = False
        
    def register_pattern(self, pattern: PatternImplementation) -> None:
        """Register a pattern implementation."""
        if pattern.pattern_id is None:
            logger.warning(f"Skipping registration of pattern with no pattern_id")
            return
            
        if pattern.pattern_id in self._patterns:
            logger.warning(f"Pattern {pattern.pattern_id} already registered, overriding")
            
        self._patterns[pattern.pattern_id] = pattern
        logger.debug(f"Registered pattern {pattern.pattern_id}")
        
    def get_pattern(self, pattern_id: str) -> Optional[PatternImplementation]:
        """Get a pattern implementation by ID."""
        self._ensure_discovery()
        return self._patterns.get(pattern_id)
        
    def get_available_patterns(self) -> List[Dict[str, Any]]:
        """Get a list of all available patterns."""
        self._ensure_discovery()
        return [
            {
                "id": pattern.pattern_id,
                "name": pattern.name,
                "description": pattern.description
            }
            for pattern in self._patterns.values()
        ]
        
    def _ensure_discovery(self) -> None:
        """Ensure pattern discovery has run."""
        if not self._discovered:
            self._discover_patterns()
            self._discovered = True
            
    def _discover_patterns(self) -> None:
        """Discover and register all patterns."""
        # TODO: Implement discovery of patterns from JSON files
        # For now, we'll rely on programmatic registration
        logger.info(f"Discovered {len(self._patterns)} patterns")
