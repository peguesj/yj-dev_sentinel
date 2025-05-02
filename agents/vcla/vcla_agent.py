"""
Version Control Listener Agent (VCLA)

This module implements the Version Control Listener Agent as specified in the
Dev Sentinel architecture. VCLAs are responsible for monitoring specific aspects
of the repository, often delegated by the VCMA.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional, Set

from core.agent import BaseAgent, AgentStatus
from core.message_bus import get_message_bus
from core.task_manager import get_task_manager, Task

logger = logging.getLogger(__name__)

class VersionControlListenerAgent(BaseAgent):
    """
    Version Control Listener Agent implementation.

    The VCLA is responsible for monitoring specific aspects of a version control system,
    acting as specialized observers that report changes to other components of the Dev Sentinel
    system. Each VCLA instance can focus on particular paths, file types, or behaviors
    within the repository.
    
    Features:
    - Path-specific monitoring for targeted observation
    - Integration with the Version Control Master Agent (VCMA) for coordination
    - Event-driven architecture via message bus subscription
    - Task-based API for on-demand monitoring
    - Configurable monitoring targets and behaviors
    - Real-time change detection and notification
    - Specialized analysis of repository components
    
    VCLAs typically operate as part of a hierarchy with the VCMA as coordinator,
    enabling distributed and focused monitoring of repository activities.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the VCLA."""
        super().__init__(agent_id, config or {})
        self.message_bus = get_message_bus()
        self.task_manager = get_task_manager()

        self.repo_path = self.config.get("repo_path", os.getcwd())
        self.monitored_paths: Set[str] = set(self.config.get("monitored_paths", []))
        self.vcma_id: Optional[str] = self.config.get("vcma_id")

        # Example: Subscribe to messages relevant to this VCLA's focus
        # self.message_bus.subscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        # self.message_bus.subscribe(f"vcla.{self.agent_id}.config_update", self._handle_config_update)

        # Example: Register task handlers specific to VCLA
        # self.task_manager.register_handler(f"vcla.{self.agent_id}.monitor_file", self._handle_monitor_file_task)

        self.logger.info(f"VersionControlListenerAgent ({self.agent_id}) initialized. Monitoring: {self.monitored_paths or 'All'}")

    async def start(self) -> None:
        """Start the VCLA."""
        self.update_status(AgentStatus.IDLE)
        self.logger.info(f"VCLA agent {self.agent_id} started.")
        # Optionally, register with VCMA if vcma_id is known
        if self.vcma_id:
            await self.message_bus.publish(
                "vcma.register_vcla",
                {"vcla_id": self.agent_id},
                target_agent=self.vcma_id # Assuming message bus supports targeted messages
            )
            self.logger.info(f"Sent registration request to VCMA {self.vcma_id}")

        # VCLA specific startup logic, e.g., start a file watcher if configured
        # asyncio.create_task(self._monitor_filesystem())

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task assigned to this VCLA."""
        self.logger.debug(f"Processing task {task.task_id}: {task.task_type}")
        handler = self.task_manager.get_handler(task.task_type)
        if handler:
            return await handler(task)
        else:
            error_msg = f"No handler registered for task type: {task.task_type}"
            self.log_error("task_handler_not_found", error_msg, {"task_id": task.task_id})
            return {"error": error_msg, "status": "failed"}

    # --- Example Message Handlers ---
    # async def _handle_commit_analyzed(self, message: Dict[str, Any]) -> None:
    #     """Handle notifications about analyzed commits."""
    #     commit_hash = message.get("commit_hash")
    #     files_changed = message.get("files_changed", [])
    #     self.logger.debug(f"Received commit analyzed event: {commit_hash}")
    #     # Check if any monitored paths were affected
    #     affected_monitored = [
    #         change for change in files_changed
    #         if any(change["path"].startswith(p) for p in self.monitored_paths)
    #     ]
    #     if affected_monitored:
    #         self.logger.info(f"Monitored paths affected by commit {commit_hash}: {affected_monitored}")
    #         # Trigger further analysis or actions...

    # async def _handle_config_update(self, message: Dict[str, Any]) -> None:
    #     """Handle configuration updates from VCMA or supervisor."""
    #     new_paths = message.get("monitored_paths")
    #     if isinstance(new_paths, list):
    #         self.monitored_paths = set(new_paths)
    #         self.logger.info(f"Updated monitored paths: {self.monitored_paths}")
    #     # Update other config as needed...

    # --- Example Task Handlers ---
    # async def _handle_monitor_file_task(self, task: Task) -> Dict[str, Any]:
    #     """Handle a task to specifically monitor a file."""
    #     file_path = task.params.get("file_path")
    #     if not file_path:
    #         return {"error": "Missing file_path parameter", "status": "failed"}
    #     self.logger.info(f"Tasked to specifically monitor file: {file_path}")
    #     self.monitored_paths.add(file_path)
    #     # Potentially trigger immediate check or add to a watcher
    #     return {"status": "success", "message": f"Now monitoring {file_path}"}

    # --- Example Background Task ---
    # async def _monitor_filesystem(self):
    #     """(Example) Monitor filesystem for changes using a library like watchdog."""
    #     # Implementation would require adding 'watchdog' dependency
    #     # This is a placeholder for potential future implementation
    #     self.logger.info("Filesystem monitoring task started (placeholder).")
    #     while self.status != AgentStatus.TERMINATED:
    #         # Check for file changes in self.monitored_paths
    #         # If changes detected, publish to message bus, e.g., "vcla.file_changed"
    #         await asyncio.sleep(30) # Example polling interval

    async def shutdown(self) -> None:
        """Perform clean shutdown of the VCLA."""
        self.logger.info(f"Shutting down VCLA {self.agent_id}")
        self.update_status(AgentStatus.TERMINATED)

        # Unsubscribe from message bus topics
        # self.message_bus.unsubscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        # self.message_bus.unsubscribe(f"vcla.{self.agent_id}.config_update", self._handle_config_update)

        # Unregister task handlers
        # self.task_manager.unregister_handler(f"vcla.{self.agent_id}.monitor_file", self._handle_monitor_file_task)

        # Optionally, unregister from VCMA
        if self.vcma_id:
             await self.message_bus.publish(
                "vcma.unregister_vcla",
                {"vcla_id": self.agent_id},
                target_agent=self.vcma_id
            )
             self.logger.info(f"Sent unregistration request to VCMA {self.vcma_id}")


        self.logger.info(f"VCLA {self.agent_id} shutdown complete.")

# Factory function to create an instance
def create_vcla(config: Optional[Dict[str, Any]] = None) -> VersionControlListenerAgent:
    """
    Create a new Version Control Listener Agent instance.

    Args:
        config: Optional configuration dictionary. Should include 'agent_id'.
                May include 'repo_path', 'monitored_paths', 'vcma_id'.

    Returns:
        New VCLA instance.
    """
    if not config or "agent_id" not in config:
         # VCLAs likely need specific IDs for targeting by VCMA
         raise ValueError("VCLA configuration must include an 'agent_id'")
    return VersionControlListenerAgent(agent_id=config["agent_id"], config=config)
