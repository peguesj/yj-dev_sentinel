"""
Force Constraints Module

This module provides constraint loading and management functionality for the Force framework.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ConstraintRegistry:
    """Registry for Force constraints"""
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        self.constraints = {}
        
    def load_constraints(self):
        """Load all constraints from the constraints directory"""
        constraints_dir = os.path.join(os.path.dirname(__file__))
        constraint_files = [f for f in os.listdir(constraints_dir) if f.endswith('.json')]
        
        for constraint_file in constraint_files:
            try:
                constraint_path = os.path.join(constraints_dir, constraint_file)
                with open(constraint_path, 'r') as f:
                    constraint_data = json.load(f)
                    constraint_id = constraint_data.get('id', constraint_file.replace('.json', ''))
                    self.constraints[constraint_id] = constraint_data
                    logger.debug(f"Loaded constraint: {constraint_id}")
            except Exception as e:
                logger.warning(f"Failed to load constraint {constraint_file}: {e}")
                
        logger.info(f"Loaded {len(self.constraints)} constraints")
        return self.constraints
        
    def get_constraint(self, constraint_id: str) -> Optional[Dict[str, Any]]:
        """Get a constraint by ID"""
        return self.constraints.get(constraint_id)
        
    def list_constraints(self) -> List[Dict[str, Any]]:
        """List all available constraints"""
        return list(self.constraints.values())

def initialize(force_engine):
    """Initialize the constraints module"""
    registry = ConstraintRegistry(force_engine)
    registry.load_constraints()
    return registry
