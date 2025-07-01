"""
Modern adapter for integrating Dev Sentinel agents with MCP and fast-agent frameworks.

This module provides adapters that bridge Dev Sentinel's agent architecture with
the Model Context Protocol and fast-agent frameworks, enabling seamless integration
with VS Code and other MCP-compatible tools.
"""
import asyncio
import sys
import os
import logging
import json
from datetime import datetime

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Any, Dict, List, Optional, Callable, Union, Protocol
from abc import ABC, abstractmethod

# Import Dev Sentinel core components
from core.agent import BaseAgent, AgentStatus
from core.message_bus import get_message_bus
from core.task_manager import get_task_manager

# Configure logging
logger = logging.getLogger(__name__)

class AgentAdapter(Protocol):
    """Protocol for agent adapters."""
    
    async def process_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a command through the adapted agent."""
        ...
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the adapted agent."""
        ...

class BaseAgentAdapter(ABC):
    """
    Abstract base class for Dev Sentinel agent adapters.
    
    This adapter provides a standardized interface for integrating Dev Sentinel
    agents with external frameworks while maintaining the agent's core functionality.
    """
    
    def __init__(self, agent: BaseAgent, name: Optional[str] = None, 
                 description: Optional[str] = None):
        """
        Initialize the adapter.
        
        Args:
            agent: The Dev Sentinel agent to adapt
            name: Optional name override for the adapter
            description: Optional description override
        """
        self.agent = agent
        self.name = name or f"{agent.__class__.__name__}Adapter"
        self.description = description or f"Adapter for {agent.__class__.__name__}"
        self.message_bus = get_message_bus()
        self.task_manager = get_task_manager()
        self._initialized = False
        self._startup_time = None
        
        logger.info(f"Initialized {self.name} for agent {agent.agent_id}")
        
    async def initialize(self) -> None:
        """Initialize the adapter and underlying agent."""
        if self._initialized:
            return
            
        try:
            # Ensure the agent is started
            if self.agent.status == AgentStatus.INITIALIZING:
                await self.agent.start()
            
            self._startup_time = datetime.now()
            self._initialized = True
            logger.info(f"{self.name} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {e}")
            raise
    
    @abstractmethod
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a command through the adapted agent.
        
        Args:
            command: Command to process
            context: Optional context information
            
        Returns:
            Processing result
        """
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the adapted agent."""
        await self.initialize()
        
        return {
            "adapter_name": self.name,
            "agent_id": self.agent.agent_id,
            "agent_status": self.agent.status.value,
            "initialized": self._initialized,
            "startup_time": self._startup_time.isoformat() if self._startup_time else None,
            "agent_type": self.agent.__class__.__name__
        }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the adapted agent."""
        await self.initialize()
        
        return {
            "adapter_name": self.name,
            "description": self.description,
            "agent_capabilities": await self._get_agent_capabilities(),
            "supported_commands": await self._get_supported_commands()
        }
    
    async def _get_agent_capabilities(self) -> List[str]:
        """Get the capabilities of the underlying agent."""
        # Default implementation - can be overridden by subclasses
        capabilities = ["status", "process_task"]
        
        if hasattr(self.agent, 'process_message'):
            capabilities.append("process_message")
        if hasattr(self.agent, 'analyze'):
            capabilities.append("analyze")
        if hasattr(self.agent, 'inspect'):
            capabilities.append("inspect")
        if hasattr(self.agent, 'validate'):
            capabilities.append("validate")
            
        return capabilities
    
    async def _get_supported_commands(self) -> List[str]:
        """Get the commands supported by this adapter."""
        # Default implementation - should be overridden by subclasses
        return ["status", "capabilities"]
    
    async def handle_error(self, error: Exception, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors in a standardized way."""
        error_info = {
            "status": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "command": command,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "adapter": self.name,
            "agent_id": self.agent.agent_id
        }
        
        logger.error(f"Error in {self.name}: {error_info}")
        return error_info

class MCPAgentAdapter(BaseAgentAdapter):
    """
    MCP-specific adapter for Dev Sentinel agents.
    
    This adapter provides MCP-compatible interfaces for Dev Sentinel agents,
    enabling integration with VS Code and other MCP-compatible tools.
    """
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a command through the MCP interface."""
        try:
            await self.initialize()
            context = context or {}
            
            # Create a task for the agent to process
            task_params = {
                "command": command,
                "context": context,
                "source": "mcp_adapter",
                "timestamp": datetime.now().isoformat()
            }
            
            # Create and process the task
            task = self.task_manager.create_task(
                task_type=f"{self.agent.__class__.__name__.lower()}_command",
                params=task_params,
                creator_id=self.name
            )
            
            # Process through the agent
            result = await self.agent.process_task(task.to_dict())
            
            return {
                "status": "success",
                "result": result,
                "task_id": task.task_id,
                "command": command,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _get_supported_commands(self) -> List[str]:
        """Get MCP-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        
        # Add agent-specific commands based on agent type
        agent_type = self.agent.__class__.__name__.lower()
        
        if "vcma" in agent_type or "version" in agent_type:
            base_commands.extend(["status", "analyze_commits", "refresh_repo"])
        elif "vcla" in agent_type or "listener" in agent_type:
            base_commands.extend(["monitor_path", "detect_changes"])
        elif "cdia" in agent_type or "documentation" in agent_type:
            base_commands.extend(["inspect_code", "analyze_documentation"])
        elif "rdia" in agent_type or "readme" in agent_type:
            base_commands.extend(["inspect_readme", "validate_structure"])
        elif "saa" in agent_type or "analysis" in agent_type:
            base_commands.extend(["analyze_code", "run_static_analysis"])
            
        return base_commands

# Alias for compatibility with legacy and fast-agent code
FastAgentAdapter = MCPAgentAdapter