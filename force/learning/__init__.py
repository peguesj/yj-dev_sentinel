"""
Learning module for the FORCE system.

Provides learning data collection and analysis for improving FORCE components.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class LearningManager:
    """Manager for collecting and analyzing learning data."""
    
    def __init__(self, force_engine):
        """Initialize the learning manager."""
        self.force_engine = force_engine
        self.learning_records = []
        
    async def record_execution(self, 
                             component_type: str, 
                             component_id: str, 
                             parameters: Dict[str, Any], 
                             result: Any,
                             execution_time: float,
                             success: bool):
        """
        Record an execution for learning purposes.
        
        Args:
            component_type: Type of component (tool, pattern, constraint)
            component_id: ID of the component
            parameters: Execution parameters
            result: Execution result
            execution_time: Time taken to execute
            success: Whether execution was successful
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "component_type": component_type,
            "component_id": component_id,
            "parameters": parameters,
            "result_summary": self._summarize_result(result),
            "execution_time": execution_time,
            "success": success
        }
        
        self.learning_records.append(record)
        await self._save_learning_data()
        
    def _summarize_result(self, result: Any) -> Dict[str, Any]:
        """Create a summarized version of the result for storage."""
        # Implement result summarization logic
        if isinstance(result, Dict):
            return {k: str(v) if not isinstance(v, (str, int, float, bool)) else v 
                   for k, v in result.items()}
        return {"summary": str(result)}
        
    async def _save_learning_data(self):
        """Save learning data to the learning directory."""
        try:
            learning_dir = self.force_engine.learning_dir
            if not learning_dir.exists():
                learning_dir.mkdir(parents=True, exist_ok=True)
                
            daily_file = learning_dir / f"learning_data_{datetime.now().strftime('%Y%m%d')}.json"
            
            existing_data = []
            if daily_file.exists():
                with open(daily_file, 'r') as f:
                    existing_data = json.load(f)
                    
            with open(daily_file, 'w') as f:
                json.dump(existing_data + self.learning_records, f, indent=2)
                
            # Reset in-memory records after saving
            self.learning_records = []
            
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
            
    async def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in learning data.
        
        Returns:
            Analysis results
        """
        # Implement pattern analysis logic
        return {"analysis": "Not implemented yet"}


# Initialize the learning manager when this module is imported
learning_manager = None

def initialize(force_engine):
    """Initialize the learning module with a reference to the Force engine."""
    global learning_manager
    learning_manager = LearningManager(force_engine)
    return learning_manager
