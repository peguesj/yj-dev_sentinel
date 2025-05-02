"""
Base adapter for integrating Dev Sentinel agents with fast-agent framework.
"""
import asyncio
import sys
import os

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Any, Dict, List, Optional, Callable, Union

# Import Dev Sentinel core components
from core.agent import BaseAgent
from core.message_bus import MessageBus

# These will need to be installed as dependencies
try:
    import mcp as fast
except ImportError:
    raise ImportError("mcp is not installed. Install with 'pip install mcp'")

class FastAgentAdapter:
    """Base adapter for converting Dev Sentinel agents to fast-agent compatible agents."""
    
    def __init__(self, agent: BaseAgent, name: Optional[str] = None, 
                 instruction: Optional[str] = None,
                 servers: Optional[List[str]] = None):
        """
        Initialize the adapter.
        
        Args:
            agent: The Dev Sentinel agent to adapt
            name: Optional name override for the fast-agent
            instruction: Optional instruction override for the fast-agent
            servers: Optional list of MCP servers to use
        """
        self.agent = agent
        self.name = name or agent.agent_id
        self.instruction = instruction or f"You are {agent.agent_type}, responsible for {agent.get_description()}"
        self.servers = servers or []
        self.fast_agent = None
        
    def create_fast_agent(self) -> Callable:
        """Create and return a fast-agent compatible agent."""
        
        @fast.agent(
            name=self.name,
            instruction=self.instruction,
            servers=self.servers
        )
        async def adapted_agent():
            """Generated fast-agent function"""
            return self.agent
            
        self.fast_agent = adapted_agent
        return adapted_agent
    
    async def handle_message(self, message: str) -> str:
        """
        Handle a message from fast-agent by adapting it to Dev Sentinel's format.
        
        Args:
            message: The message to process
            
        Returns:
            The response from the Dev Sentinel agent
        """
        # Convert the message to Dev Sentinel format
        ds_message = {
            "sender": {
                "agentId": "fast_agent_user",
                "agentType": "external"
            },
            "messageType": "Command",
            "payload": message
        }
        
        # Process the message through the Dev Sentinel agent
        response = await self.agent.process_message(ds_message)
        
        # Extract and return the response text
        if isinstance(response, dict) and "payload" in response:
            return response["payload"]
        return str(response)