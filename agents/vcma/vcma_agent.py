"""
Version Control Master Agent (VCMA)

This module implements the Version Control Master Agent as specified in the
Dev Sentinel architecture. The VCMA is responsible for coordinating version control
operations and maintaining a high-level understanding of the repository structure.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Set
import json
import subprocess
from datetime import datetime, timedelta

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use absolute imports instead of relative ones
from core.agent import BaseAgent, AgentStatus
from core.message_bus import get_message_bus
from core.task_manager import get_task_manager, Task

logger = logging.getLogger(__name__)

class VersionControlMasterAgent(BaseAgent):
    """
    Version Control Master Agent implementation.
    
    The VCMA serves as the central coordinator for version control monitoring
    and analysis within the Dev Sentinel system. It maintains a comprehensive
    view of the repository state and orchestrates specialized listener agents (VCLAs)
    to perform targeted monitoring of repository components.
    
    Features:
    - Repository state tracking and change detection
    - Commit history analysis and monitoring
    - Coordination of Version Control Listener Agents (VCLAs)
    - File change tracking and history maintenance
    - Periodic repository scanning for changes
    - Event-driven architecture via message bus integration
    - Task-based API for on-demand repository operations
    - Git integration for repository operations
    
    The VCMA acts as the primary interface between the version control system
    and other Dev Sentinel components, providing consistent and reliable
    information about repository state and changes.
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the VCMA with default configuration."""
        super().__init__(agent_id, config or {})
        self.message_bus = get_message_bus()
        self.task_manager = get_task_manager()
        
        # VC-specific data structures
        self.repo_path = self.config.get("repo_path", os.getcwd())
        self.known_branches = set()
        self.tracked_files = set()
        self.last_commit_hash = None
        self.file_change_history = {}
        self.vcla_agents = set()
        
        # Set up message bus subscriptions
        self.message_bus.subscribe("vc.changes", self._handle_vc_changes)
        self.message_bus.subscribe("vc.status_request", self._handle_status_request)
        
        # Register task handlers
        self.task_manager.register_handler("vc.refresh_repo_state", self._handle_refresh_repo_task)
        self.task_manager.register_handler("vc.analyze_commit", self._handle_analyze_commit_task)
        
        self.logger.info("VersionControlMasterAgent initialized")
        
    async def start(self) -> None:
        """Start the agent and perform initial repository analysis."""
        self.update_status(AgentStatus.BUSY)
        
        # Initial repository scan
        await self._refresh_repo_state()
        
        # Schedule periodic repository scanning
        asyncio.create_task(self._periodic_repo_scan())
        
        self.update_status(AgentStatus.IDLE)
        self.logger.info("VCMA agent started successfully")
        
    async def _periodic_repo_scan(self, interval_seconds: int = 600) -> None:
        """
        Periodically scan the repository for changes.
        
        Args:
            interval_seconds: Time between scans in seconds
        """
        self.logger.info(f"Starting periodic repository scanning every {interval_seconds} seconds")
        
        while self.status != AgentStatus.TERMINATED:
            await asyncio.sleep(interval_seconds)
            if self.status != AgentStatus.BUSY:
                self.update_status(AgentStatus.BUSY)
                await self._refresh_repo_state()
                self.update_status(AgentStatus.IDLE)
    
    async def _refresh_repo_state(self) -> Dict[str, Any]:
        """
        Refresh the internal state representation of the repository.
        
        Returns:
            Dictionary with updated repository state information
        """
        self.logger.info("Refreshing repository state")
        
        try:
            # Get current branch
            current_branch = await self._run_git_command("git rev-parse --abbrev-ref HEAD")
            
            # Get all branches
            branches = await self._run_git_command("git branch --list --format='%(refname:short)'")
            branches = set(branches.split("\n") if branches else [])
            
            # Get current commit hash
            current_commit = await self._run_git_command("git rev-parse HEAD")
            
            # Check for changes since last scan
            is_changed = False
            if self.last_commit_hash and self.last_commit_hash != current_commit:
                is_changed = True
                await self._analyze_new_commits(self.last_commit_hash, current_commit)
            
            # Update state
            self.last_commit_hash = current_commit
            new_branches = branches - self.known_branches
            removed_branches = self.known_branches - branches
            self.known_branches = branches
            
            # Update tracked files
            await self._update_tracked_files()
            
            result = {
                "current_branch": current_branch,
                "all_branches": list(branches),
                "current_commit": current_commit,
                "new_branches": list(new_branches),
                "removed_branches": list(removed_branches),
                "tracked_files_count": len(self.tracked_files),
                "has_changes": is_changed
            }
            
            # Publish results to message bus
            await self.message_bus.publish(
                "vc.state_updated", 
                result, 
                self.agent_id
            )
            
            self.log_activity("repo_state_refresh", result)
            return result
            
        except Exception as e:
            error_msg = f"Error refreshing repository state: {str(e)}"
            self.log_error("repo_refresh_error", error_msg, {"critical": True})
            return {"error": error_msg}
    
    async def _update_tracked_files(self) -> None:
        """Update the set of tracked files in the repository."""
        tracked_files_output = await self._run_git_command("git ls-files")
        self.tracked_files = set(tracked_files_output.strip().split("\n") if tracked_files_output else [])
        
    async def _analyze_new_commits(self, old_hash: str, new_hash: str) -> None:
        """
        Analyze new commits that have appeared since the last scan.
        
        Args:
            old_hash: Previous commit hash
            new_hash: Current commit hash
        """
        # Get commit range
        commit_range = f"{old_hash}..{new_hash}"
        
        # Get commit count
        commit_count_output = await self._run_git_command(f"git rev-list --count {commit_range}")
        commit_count = int(commit_count_output.strip()) if commit_count_output else 0
        
        # Get commit data
        commit_format = "--pretty=format:{\\\"hash\\\":\\\"%H\\\",\\\"author\\\":\\\"%an\\\",\\\"date\\\":\\\"%ad\\\",\\\"subject\\\":\\\"%s\\\"}"
        commits_json = await self._run_git_command(f"git log {commit_format} {commit_range}")
        
        # Process commits
        if commits_json:
            commits = []
            for line in commits_json.strip().split("\n"):
                try:
                    commits.append(json.loads(line))
                except json.JSONDecodeError:
                    self.logger.warning(f"Failed to parse commit data: {line}")
            
            # Queue analysis tasks for each commit
            for commit in commits:
                task = self.task_manager.create_task(
                    "vc.analyze_commit",
                    {"commit_hash": commit["hash"]},
                    self.agent_id
                )
                self.logger.debug(f"Queued analysis for commit {commit['hash']} (task: {task.task_id})")
            
            # Publish information about new commits
            await self.message_bus.publish(
                "vc.new_commits",
                {
                    "commit_count": commit_count,
                    "commits": commits
                },
                self.agent_id
            )
    
    async def _run_git_command(self, command: str) -> str:
        """
        Run a git command in the repository directory.
        
        Args:
            command: Git command to run
            
        Returns:
            Command output as string
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.repo_path
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error = stderr.decode().strip()
            self.logger.error(f"Git command failed: {command}\nError: {error}")
            raise Exception(f"Git command failed: {error}")
            
        return stdout.decode().strip()
    
    async def _handle_vc_changes(self, message: Dict[str, Any]) -> None:
        """
        Handle notifications of repository changes.
        
        Args:
            message: Message containing change details
        """
        self.logger.info(f"Received VC changes notification: {message}")
        
        # If we're not already busy, refresh repository state
        if self.status != AgentStatus.BUSY:
            self.update_status(AgentStatus.BUSY)
            await self._refresh_repo_state()
            self.update_status(AgentStatus.IDLE)
    
    async def _handle_status_request(self, message: Dict[str, Any]) -> None:
        """
        Handle requests for repository status information.
        
        Args:
            message: Message containing the request
        """
        self.logger.info(f"Received VC status request")
        
        status_info = {
            "agent_state": self.get_agent_state(),
            "repo_state": {
                "current_branch": list(self.known_branches)[0] if self.known_branches else None,
                "branch_count": len(self.known_branches),
                "tracked_files": len(self.tracked_files),
                "last_commit": self.last_commit_hash
            }
        }
        
        # Reply to the request with current status
        reply_topic = message.get("reply_topic", "vc.status_response")
        await self.message_bus.publish(
            reply_topic,
            status_info,
            self.agent_id
        )
    
    async def _handle_refresh_repo_task(self, task: Task) -> Dict[str, Any]:
        """
        Task handler for refreshing repository state.
        
        Args:
            task: The refresh repository task
            
        Returns:
            Result of the repository refresh operation
        """
        self.logger.info(f"Handling task: {task.task_type} ({task.task_id})")
        return await self._refresh_repo_state()
    
    async def _handle_analyze_commit_task(self, task: Task) -> Dict[str, Any]:
        """
        Task handler for analyzing a specific commit.
        
        Args:
            task: The analyze commit task
            
        Returns:
            Results of commit analysis
        """
        commit_hash = task.params.get("commit_hash")
        if not commit_hash:
            return {"error": "No commit hash provided"}
            
        self.logger.info(f"Analyzing commit: {commit_hash}")
        
        try:
            # Get detailed commit info
            commit_detail_format = "--pretty=format:{\\\"hash\\\":\\\"%H\\\",\\\"author\\\":\\\"%an\\\",\\\"email\\\":\\\"%ae\\\",\\\"date\\\":\\\"%ad\\\",\\\"subject\\\":\\\"%s\\\",\\\"body\\\":\\\"%b\\\"}"
            commit_detail = await self._run_git_command(f"git show {commit_detail_format} {commit_hash}")
            
            # Get file changes
            files_changed = await self._run_git_command(f"git diff-tree --no-commit-id --name-status -r {commit_hash}")
            
            # Process file changes
            change_records = []
            if files_changed:
                for line in files_changed.strip().split("\n"):
                    if line:
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            change_type, file_path = parts[0], parts[1]
                            change_records.append({
                                "type": change_type,
                                "path": file_path
                            })
            
            result = {
                "commit_hash": commit_hash,
                "commit_detail": json.loads(commit_detail) if commit_detail else None,
                "files_changed": change_records,
                "analysis_time": datetime.now().isoformat()
            }
            
            # Update file change history
            for change in change_records:
                file_path = change["path"]
                if file_path not in self.file_change_history:
                    self.file_change_history[file_path] = []
                
                self.file_change_history[file_path].append({
                    "commit": commit_hash,
                    "type": change["type"],
                    "date": result["commit_detail"]["date"] if result["commit_detail"] else None
                })
            
            # Publish analysis results
            await self.message_bus.publish(
                "vc.commit_analyzed",
                result,
                self.agent_id
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Error analyzing commit {commit_hash}: {str(e)}"
            self.log_error("commit_analysis_error", error_msg, {"commit_hash": commit_hash})
            return {"error": error_msg}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task assigned to this agent.
        
        Args:
            task: Task details
            
        Returns:
            Task processing result
        """
        task_type = task.get("type")
        
        if task_type == "refresh_repo_state":
            return await self._refresh_repo_state()
        elif task_type == "get_file_history":
            file_path = task.get("file_path")
            if file_path:
                return {"history": self.file_change_history.get(file_path, [])}
            return {"error": "No file path provided"}
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    def register_vcla(self, agent_id: str) -> None:
        """
        Register a Version Control Listener Agent with this master.
        
        Args:
            agent_id: ID of the VCLA to register
        """
        self.vcla_agents.add(agent_id)
        self.logger.info(f"Registered VCLA: {agent_id}")
        
    def unregister_vcla(self, agent_id: str) -> None:
        """
        Unregister a Version Control Listener Agent from this master.
        
        Args:
            agent_id: ID of the VCLA to unregister
        """
        if agent_id in self.vcla_agents:
            self.vcla_agents.remove(agent_id)
            self.logger.info(f"Unregistered VCLA: {agent_id}")
            
    async def shutdown(self) -> None:
        """Perform clean shutdown of the agent."""
        self.logger.info("Shutting down VCMA")
        
        # Unsubscribe from message bus topics
        self.message_bus.unsubscribe("vc.changes", self._handle_vc_changes)
        self.message_bus.unsubscribe("vc.status_request", self._handle_status_request)
        
        # Unregister task handlers
        self.task_manager.unregister_handler("vc.refresh_repo_state", self._handle_refresh_repo_task)
        self.task_manager.unregister_handler("vc.analyze_commit", self._handle_analyze_commit_task)
        
        # Update agent status to terminated
        self.update_status(AgentStatus.TERMINATED)
        
        self.logger.info("VCMA shutdown complete")

# Factory function to create an instance
def create_vcma(config: Optional[Dict[str, Any]] = None) -> VersionControlMasterAgent:
    """
    Create a new Version Control Master Agent instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        New VCMA instance
    """
    return VersionControlMasterAgent(config=config)