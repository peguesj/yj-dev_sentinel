"""
Force Constraint System

Provides validation and enforcement of quality rules.
"""

import importlib
import logging
import os
import pkgutil
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
