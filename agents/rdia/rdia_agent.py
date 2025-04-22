"""
README Inspector Agent (RDIA)

This module implements the README Inspector Agent as specified in the
Dev Sentinel architecture. RDIA is responsible for analyzing the project's
README file(s) to ensure they accurately reflect the current state of the
project, especially concerning recent changes.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional

import markdown # Assuming markdown library for parsing

from ...core.agent import BaseAgent, AgentStatus
from ...core.message_bus import get_message_bus
from ...core.task_manager import get_task_manager, Task
from ...utils.file_operations import read_file_content # Assuming a utility function

logger = logging.getLogger(__name__)

class READMEInspectorAgent(BaseAgent):
    """
    README Inspector Agent implementation.

    Analyzes README files for consistency, accuracy, and completeness
    based on recent project changes communicated via the message bus.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the RDIA."""
        super().__init__(agent_id, config or {})
        self.message_bus = get_message_bus()
        self.task_manager = get_task_manager()

        self.repo_path = self.config.get("repo_path", os.getcwd())
        self.readme_paths = self.config.get("readme_paths", [os.path.join(self.repo_path, "README.md")])
        self.last_analyzed_commit: Optional[str] = None

        # Subscribe to relevant messages
        self.message_bus.subscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        self.message_bus.subscribe("vc.repo_refreshed", self._handle_repo_refreshed)

        # Register task handlers
        self.task_manager.register_handler(f"rdia.{self.agent_id}.inspect_readme", self._handle_inspect_readme_task)

        self.logger.info(f"READMEInspectorAgent ({self.agent_id}) initialized. Monitoring: {self.readme_paths}")

    async def start(self) -> None:
        """Start the RDIA."""
        self.update_status(AgentStatus.IDLE)
        self.logger.info(f"RDIA agent {self.agent_id} started.")
        # Initial inspection on startup?
        # await self.inspect_readmes()

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task assigned to this RDIA."""
        self.logger.debug(f"Processing task {task.task_id}: {task.task_type}")
        handler = self.task_manager.get_handler(task.task_type)
        if handler:
            return await handler(task)
        else:
            error_msg = f"No handler registered for task type: {task.task_type}"
            self.log_error("task_handler_not_found", error_msg, {"task_id": task.task_id})
            return {"error": error_msg, "status": "failed"}

    async def _handle_commit_analyzed(self, message: Dict[str, Any]) -> None:
        """Handle notifications about newly analyzed commits."""
        commit_hash = message.get("commit_hash")
        summary = message.get("summary", "No summary provided.")
        files_changed = message.get("files_changed", [])
        self.logger.info(f"Received commit analyzed event: {commit_hash}. Triggering README inspection.")
        self.last_analyzed_commit = commit_hash
        # Trigger inspection based on commit info
        await self.inspect_readmes(commit_info=message)

    async def _handle_repo_refreshed(self, message: Dict[str, Any]) -> None:
        """Handle notifications that the repository state has been refreshed."""
        self.logger.info("Repository refreshed event received. Triggering README inspection.")
        # Trigger inspection based on general refresh
        await self.inspect_readmes()

    async def _handle_inspect_readme_task(self, task: Task) -> Dict[str, Any]:
        """Handle a direct task to inspect the README."""
        self.logger.info(f"Received task to inspect README: {task.task_id}")
        results = await self.inspect_readmes(commit_info=task.params.get("commit_info"))
        return {"status": "success", "results": results}

    async def inspect_readmes(self, commit_info: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Core logic to inspect the configured README files.

        Args:
            commit_info: Optional dictionary containing details about the latest commit.

        Returns:
            A list of dictionaries, each containing inspection results for a README file.
        """
        self.update_status(AgentStatus.BUSY)
        self.logger.info("Starting README inspection...")
        results = []

        for readme_path in self.readme_paths:
            if not os.path.exists(readme_path):
                self.logger.warning(f"README file not found: {readme_path}")
                results.append({"path": readme_path, "status": "not_found"})
                continue

            try:
                content = await read_file_content(readme_path) # Assumes async file read
                self.logger.debug(f"Read {len(content)} bytes from {readme_path}")

                # --- Placeholder for actual analysis logic ---
                issues = self._analyze_readme_content(content, commit_info)
                # --- End Placeholder ---

                results.append({
                    "path": readme_path,
                    "status": "inspected",
                    "issues_found": len(issues),
                    "issues": issues,
                    "last_commit_analyzed": self.last_analyzed_commit
                })
                self.logger.info(f"Inspection complete for {readme_path}. Found {len(issues)} potential issues.")

                # Publish results
                await self.message_bus.publish(
                    "rdia.inspection_complete",
                    {"path": readme_path, "issues": issues, "commit": self.last_analyzed_commit}
                )

            except Exception as e:
                error_msg = f"Error inspecting README {readme_path}: {e}"
                self.log_error("readme_inspection_failed", error_msg, {"path": readme_path})
                results.append({"path": readme_path, "status": "error", "error": error_msg})

        self.update_status(AgentStatus.IDLE)
        return results

    def _analyze_readme_content(self, content: str, commit_info: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes the content of a README file. (Placeholder)

        This function should contain the actual logic to parse the README
        (e.g., using markdown library) and compare its content against
        recent changes (commit_info) or general project structure/features.

        Args:
            content: The string content of the README file.
            commit_info: Optional dictionary with details of the latest commit.

        Returns:
            A list of dictionaries, each describing a potential issue found.
        """
        issues = []
        self.logger.debug("Analyzing README content (placeholder logic)...")

        # Example checks (replace with actual logic):
        if commit_info:
             # - Check if new features mentioned in commit summary are documented.
             # - Check if file changes correspond to sections in README (e.g., setup, usage).
             pass
        # - Check for broken links (requires more advanced parsing/checking).
        # - Check for "TODO" or "FIXME" markers.
        if "TODO" in content or "FIXME" in content:
             issues.append({"type": "placeholder_marker", "details": "Found TODO/FIXME marker."})
        # - Check if installation/usage instructions seem up-to-date (heuristic or LLM-based).
        # - Check for presence of key sections (e.g., Installation, Usage, Contributing, License).
        if "## Installation" not in content:
             issues.append({"type": "missing_section", "details": "Missing 'Installation' section."})
        if "## Usage" not in content:
             issues.append({"type": "missing_section", "details": "Missing 'Usage' section."})
        if "## License" not in content and "LICENSE" not in content:
             issues.append({"type": "missing_section", "details": "Missing 'License' section or reference."})


        # More sophisticated analysis could involve:
        # - Parsing the Markdown AST.
        # - Using NLP/LLM to understand semantics and compare with commit messages/code changes.
        # - Checking code examples for validity.

        return issues


    async def shutdown(self) -> None:
        """Perform clean shutdown of the RDIA."""
        self.logger.info(f"Shutting down RDIA {self.agent_id}")
        self.update_status(AgentStatus.TERMINATED)

        # Unsubscribe from message bus topics
        self.message_bus.unsubscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        self.message_bus.unsubscribe("vc.repo_refreshed", self._handle_repo_refreshed)

        # Unregister task handlers
        self.task_manager.unregister_handler(f"rdia.{self.agent_id}.inspect_readme", self._handle_inspect_readme_task)

        self.logger.info(f"RDIA {self.agent_id} shutdown complete.")

# Factory function to create an instance
def create_rdia(config: Optional[Dict[str, Any]] = None) -> READMEInspectorAgent:
    """
    Create a new README Inspector Agent instance.

    Args:
        config: Optional configuration dictionary. Should include 'agent_id'.
                May include 'repo_path', 'readme_paths'.

    Returns:
        New RDIA instance.
    """
    if not config or "agent_id" not in config:
         # RDIA might need specific IDs if multiple instances monitor different READMEs
         raise ValueError("RDIA configuration must include an 'agent_id'")
    return READMEInspectorAgent(agent_id=config["agent_id"], config=config)
