"""
Force Patterns Module

This module provides pattern loading and management functionality for the Force framework.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class PatternRegistry:
    """Registry for Force patterns"""
    
    def __init__(self, force_engine):
        self.force_engine = force_engine
        self.patterns = {}
        
    def load_patterns(self):
        """Load all patterns from the patterns directory"""
        patterns_dir = os.path.join(os.path.dirname(__file__))
        pattern_files = [f for f in os.listdir(patterns_dir) if f.endswith('.json')]
        
        for pattern_file in pattern_files:
            try:
                pattern_path = os.path.join(patterns_dir, pattern_file)
                with open(pattern_path, 'r') as f:
                    pattern_data = json.load(f)
                    pattern_id = pattern_data.get('id', pattern_file.replace('.json', ''))
                    self.patterns[pattern_id] = pattern_data
                    logger.debug(f"Loaded pattern: {pattern_id}")
            except Exception as e:
                logger.warning(f"Failed to load pattern {pattern_file}: {e}")
                
        logger.info(f"Loaded {len(self.patterns)} patterns")
        return self.patterns
        
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a pattern by ID"""
        return self.patterns.get(pattern_id)
        
    def list_patterns(self) -> List[Dict[str, Any]]:
        """List all available patterns"""
        return list(self.patterns.values())

def initialize(force_engine):
    """Initialize the patterns module"""
    registry = PatternRegistry(force_engine)
    registry.load_patterns()
    return registry
