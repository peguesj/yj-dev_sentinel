"""
Base Agent Implementation

This module provides the base agent class that all specialized agents inherit from.
It defines the common functionality and interface for all agents in the Dev Sentinel ecosystem.

The BaseAgent class serves as the foundation for Dev Sentinel's autonomous agent architecture,
providing standardized mechanisms for:

- Agent lifecycle management (initialization, startup, shutdown)
- Status tracking and state management
- Task processing capabilities
- Activity logging and metrics collection
- Error handling and reporting
- Configuration management

Each specialized agent in the system inherits from this base class and extends
its functionality to perform specific roles within the Dev Sentinel ecosystem.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable

class AgentStatus(Enum):
    """Possible states for an agent"""
    INITIALIZING = "initializing"  # Agent is starting up
    IDLE = "idle"                  # Agent is ready but not working on anything
    BUSY = "busy"                  # Agent is actively working
    PAUSED = "paused"              # Agent execution is paused
    TERMINATED = "terminated"      # Agent has been shut down
    ERROR = "error"                # Agent is in an error state

class BaseAgent:
    """
    Base agent class that all Dev Sentinel agents inherit from.
    
    This class provides common functionality for agent lifecycle management,
    status tracking, configuration, and logging.
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new agent instance.
        
        Args:
            agent_id: Unique identifier for this agent instance
            config: Configuration dictionary for this agent
        """
        self.agent_id = agent_id or f"{self.__class__.__name__.lower()}-{str(uuid.uuid4())[:8]}"
        self.config = config or {}
        self.status = AgentStatus.INITIALIZING
        self.start_time = datetime.now()
        self.last_activity = self.start_time
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")
        
        # Performance metrics
        self.tasks_processed = 0
        self.errors_encountered = 0
        self.activities = []
        
        self.logger.info(f"Agent {self.agent_id} initialized")
    
    async def start(self) -> None:
        """
        Start the agent's operation.
        
        This method should be overridden by agent implementations to perform
        their startup routines.
        """
        self.logger.info(f"Agent {self.agent_id} starting")
        self.update_status(AgentStatus.IDLE)
    
    async def shutdown(self) -> None:
        """
        Gracefully shut down the agent.
        
        This method should be overridden by agent implementations to perform
        their cleanup routines.
        """
        self.logger.info(f"Agent {self.agent_id} shutting down")
        self.update_status(AgentStatus.TERMINATED)
    
    def update_status(self, status: AgentStatus) -> None:
        """
        Update the agent's status.
        
        Args:
            status: New status for the agent
        """
        old_status = self.status
        self.status = status
        self.last_activity = datetime.now()
        self.logger.debug(f"Agent {self.agent_id} status changed: {old_status.value} -> {status.value}")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task assigned to this agent.
        
        Args:
            task: Task details
            
        Returns:
            Results from processing the task
        """
        self.update_status(AgentStatus.BUSY)
        self.tasks_processed += 1
        
        try:
            # Default implementation just returns the task unmodified
            # Subclasses should override this method
            result = {"message": "Task received but not processed", "task": task}
            self.logger.warning(f"Agent {self.agent_id} does not implement task processing")
            
        except Exception as e:
            self.errors_encountered += 1
            error_message = f"Error processing task: {str(e)}"
            self.logger.error(error_message, exc_info=True)
            result = {"error": error_message}
            
        self.update_status(AgentStatus.IDLE)
        return result
        
    def log_activity(self, activity_type: str, details: Dict[str, Any] = None) -> None:
        """
        Log an activity performed by this agent.
        
        Args:
            activity_type: Type of activity performed
            details: Additional details about the activity
        """
        activity = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "details": details or {}
        }
        self.activities.append(activity)
        self.logger.debug(f"Activity: {activity_type} - {details}")
        self.last_activity = datetime.now()
        
    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None) -> None:
        """
        Log an error encountered by this agent.
        
        Args:
            error_type: Type of error
            message: Error message
            details: Additional error details
        """
        error = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "details": details or {}
        }
        self.errors_encountered += 1
        self.logger.error(f"Error: {error_type} - {message}")
        if details:
            self.logger.debug(f"Error details: {details}")
        
    def get_agent_state(self) -> Dict[str, Any]:
        """
        Get the current state of the agent.
        
        Returns:
            Dictionary containing agent state information
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            "status": self.status.value,
            "uptime_seconds": uptime,
            "tasks_processed": self.tasks_processed,
            "errors": self.errors_encountered,
            "last_activity": self.last_activity.isoformat(),
            "recent_activities": self.activities[-10:] if self.activities else []
        }
        
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """
        Update agent configuration.
        
        Args:
            config_updates: Dictionary containing configuration updates
        """
        self.config.update(config_updates)
        self.logger.info(f"Configuration updated: {list(config_updates.keys())}")