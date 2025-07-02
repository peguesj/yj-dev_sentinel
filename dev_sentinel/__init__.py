"""
Dev Sentinel - AI-powered development sentinel with Force framework

This package provides AI agents, Force framework integration, and MCP servers
for intelligent development automation and assistance.
"""

__version__ = "0.3.0"
__author__ = "Dev Sentinel Team"
__email__ = "dev@devsentinel.ai"

from .core.agent import BaseAgent as Agent
from .core.message_bus import MessageBus
from .core.task_manager import TaskManager

# Import Force framework for external use
try:
    from .force import ForceEngine
except ImportError:
    # Force engine not available
    ForceEngine = None

__all__ = [
    "Agent",
    "MessageBus", 
    "TaskManager",
    "ForceEngine",
    "__version__",
]
