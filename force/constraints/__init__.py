"""
Force Constraint System

Provides validation and enforcement of quality rules.
"""

import importlib
import logging
import os
import pkgutil
import json
from typing import Dict, Any, List, Optional, Type, Set, Union, Callable, Awaitable

logger = logging.getLogger(__name__)

class ConstraintViolation:
    """Represents a constraint violation."""
    
    def __init__(self, constraint_id: str, message: str, location: Optional[str] = None, 
                 severity: str = "error", auto_fixable: bool = False):
        self.constraint_id = constraint_id
        self.message = message
        self.location = location
        self.severity = severity  # "error", "warning", or "info"
        self.auto_fixable = auto_fixable
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "constraint_id": self.constraint_id,
            "message": self.message,
            "location": self.location,
            "severity": self.severity,
            "auto_fixable": self.auto_fixable
        }


class BaseConstraintValidator:
    """Base class for constraint validators."""
    
    constraint_id = None
    constraint_name = None
    constraint_description = None
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        
    async def validate(self, context: Dict[str, Any]) -> List[ConstraintViolation]:
        """Validate against the constraint."""
        raise NotImplementedError("Constraint validators must implement validate()")
        
    async def auto_fix(self, violations: List[ConstraintViolation], context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to automatically fix constraint violations."""
        # Default implementation doesn't fix anything
        return {
            "fixed": 0,
            "remaining": len(violations),
            "violations": [v.to_dict() for v in violations],
            "fixed_details": []
        }
        
    def get_metadata(self) -> Dict[str, Any]:
        """Return constraint metadata."""
        return {
            "id": self.constraint_id,
            "name": self.constraint_name,
            "description": self.constraint_description,
        }

    @classmethod
    def supports_constraint_id(cls, constraint_id: str) -> bool:
        """Check if this validator supports the given constraint ID."""
        return cls.constraint_id == constraint_id


class ConstraintRegistry:
    """Registry for constraint validators."""
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        self._validators: Dict[str, Type[BaseConstraintValidator]] = {}
        self._discovered = False
        
    def register_validator(self, validator_class: Type[BaseConstraintValidator]) -> None:
        """Register a constraint validator class."""
        if validator_class.constraint_id is None:
            logger.warning(f"Skipping registration of {validator_class.__name__} with no constraint_id")
            return
            
        if validator_class.constraint_id in self._validators:
            logger.warning(f"Constraint validator for {validator_class.constraint_id} already registered, overriding")
            
        self._validators[validator_class.constraint_id] = validator_class
        logger.debug(f"Registered constraint validator for {validator_class.constraint_id}")
        
    def get_validator_class(self, constraint_id: str) -> Optional[Type[BaseConstraintValidator]]:
        """Get the validator class for a constraint ID."""
        self._ensure_discovery()
        return self._validators.get(constraint_id)
        
    def create_validator(self, constraint_id: str) -> Optional[BaseConstraintValidator]:
        """Create a validator instance for a constraint ID."""
        validator_class = self.get_validator_class(constraint_id)
        if validator_class:
            return validator_class(self.force_engine)
        return None
        
    def get_available_constraints(self) -> List[Dict[str, Any]]:
        """Get a list of all available constraints."""
        self._ensure_discovery()
        result = []
        for constraint_id, validator_class in self._validators.items():
            instance = validator_class(self.force_engine)
            result.append(instance.get_metadata())
        return result
        
    def _ensure_discovery(self) -> None:
        """Ensure constraint discovery has run."""
        if not self._discovered:
            self._discover_constraints()
            self._discovered = True
            
    def _discover_constraints(self) -> None:
        """Discover and register all constraint validators."""
        # First, import any modules in the constraints package
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for _, name, ispkg in pkgutil.iter_modules([current_dir]):
            if not name.startswith('_'):
                importlib.import_module(f'force.constraints.{name}')
                
        # Then register any BaseConstraintValidator subclasses
        for subclass in BaseConstraintValidator.__subclasses__():
            self.register_validator(subclass)
        
        logger.info(f"Discovered {len(self._validators)} constraint validators")


class ConstraintDefinition:
    """Represents a constraint definition loaded from a JSON file."""
    
    def __init__(self, definition_data: Dict[str, Any]):
        """Initialize a constraint definition from JSON data."""
        self.data = definition_data
        self.id = definition_data.get("id")
        self.type = definition_data.get("type")
        self.description = definition_data.get("description")
        self.enforcement = definition_data.get("enforcement", {})
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the definition to a dictionary."""
        return self.data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConstraintDefinition':
        """Create a constraint definition from a dictionary."""
        return cls(data)


class ConstraintDefinitionRegistry:
    """Registry for constraint definitions loaded from JSON."""
    
    def __init__(self):
        self._definitions: Dict[str, ConstraintDefinition] = {}
        
    def register(self, definition: ConstraintDefinition) -> None:
        """Register a constraint definition."""
        if not definition.id:
            logger.warning("Skipping registration of constraint definition with no ID")
            return
        
        if definition.id in self._definitions:
            logger.warning(f"Constraint definition for {definition.id} already registered, overriding")
            
        self._definitions[definition.id] = definition
        logger.info(f"Registered constraint definition for {definition.id}")
        
    def get(self, constraint_id: str) -> Optional[ConstraintDefinition]:
        """Get a constraint definition by ID."""
        return self._definitions.get(constraint_id)
        
    def get_all(self) -> Dict[str, ConstraintDefinition]:
        """Get all registered constraint definitions."""
        return self._definitions


class JsonConstraintValidator(BaseConstraintValidator):
    """Validator for JSON-defined constraints."""
    
    def __init__(self, force_engine, definition: ConstraintDefinition):
        super().__init__(force_engine)
        self.definition = definition
        self.constraint_id = definition.id
        self.constraint_name = definition.id
        self.constraint_description = definition.description
        
    async def validate(self, context: Dict[str, Any]) -> List[ConstraintViolation]:
        """Validate against the constraint using the JSON definition."""
        if hasattr(self.force_engine, "validate_json_constraint"):
            return await self.force_engine.validate_json_constraint(
                self.definition, context)
        else:
            logger.warning(f"JSON constraint validation not implemented for {self.constraint_id}")
            return []
        
    async def auto_fix(self, violations: List[ConstraintViolation], context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to automatically fix constraint violations."""
        if (hasattr(self.force_engine, "auto_fix_json_constraint") and 
            self.definition.enforcement.get("auto_fix", False)):
            return await self.force_engine.auto_fix_json_constraint(
                self.definition, violations, context)
        return {
            "fixed": 0,
            "remaining": len(violations),
            "violations": [v.to_dict() for v in violations],
            "fixed_details": []
        }


# Global constraint definition registry
constraint_definition_registry = ConstraintDefinitionRegistry()


def load_constraint_definitions(force_dir):
    """
    Load constraint definitions from the .force directory.
    
    Args:
        force_dir: Path to the .force directory
    """
    try:
        constraints_dir = force_dir / "constraints"
        if constraints_dir.exists() and constraints_dir.is_dir():
            logger.info(f"Loading constraint definitions from {constraints_dir}")
            for json_file in constraints_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        constraint_data = json.load(f)
                        
                    # Handle both single constraints and collections
                    if "id" in constraint_data and isinstance(constraint_data.get("id"), str):
                        logger.info(f"Found single constraint definition in {json_file}")
                        definition = ConstraintDefinition.from_dict(constraint_data)
                        constraint_definition_registry.register(definition)
                    elif "constraints" in constraint_data and isinstance(constraint_data.get("constraints"), list):
                        constraints_list = constraint_data.get("constraints", [])
                        logger.info(f"Found {len(constraints_list)} constraint definitions in {json_file}")
                        for constraint_def in constraints_list:
                            if isinstance(constraint_def, dict) and "id" in constraint_def:
                                definition = ConstraintDefinition.from_dict(constraint_def)
                                constraint_definition_registry.register(definition)
                            else:
                                logger.warning(f"Invalid constraint definition in {json_file}")
                    else:
                        logger.warning(f"Unknown constraint definition format in {json_file}")
                        
                except Exception as e:
                    logger.error(f"Error loading constraint definition from {json_file}: {e}")
        else:
            logger.warning(f"Constraint definitions directory not found: {constraints_dir}")
            
    except Exception as e:
        logger.error(f"Error loading constraint definitions: {e}")
        import traceback
        traceback.print_exc()


def register_json_constraint_validators(registry: ConstraintRegistry) -> None:
    """
    Register JSON constraint definitions as validators in the given registry.
    
    Args:
        registry: ConstraintRegistry to register the validators with
    """
    for constraint_id, definition in constraint_definition_registry.get_all().items():
        # Check if there's already a native validator for this constraint
        if registry.get_validator_class(constraint_id):
            logger.debug(f"Native validator already exists for {constraint_id}, skipping JSON registration")
            continue
            
        # Create a specialized validator class for this constraint definition
        class_name = f"{constraint_id.title().replace('_', '')}JsonValidator"
        
        # Create a dynamic validator class
        JsonConstraintValidatorClass = type(
            class_name,
            (JsonConstraintValidator,),
            {
                "constraint_id": constraint_id,
                "constraint_name": constraint_id,
                "constraint_description": definition.description
            }
        )
        
        # Register the validator class
        registry.register_validator(JsonConstraintValidatorClass)
        logger.info(f"Registered JSON constraint validator for {constraint_id}")


# Update the discovery method to include JSON-defined constraints
def extend_constraint_registry(registry: ConstraintRegistry) -> None:
    """
    Extend the given constraint registry with JSON-defined constraints.
    
    Args:
        registry: ConstraintRegistry to extend
    """
    register_json_constraint_validators(registry)
