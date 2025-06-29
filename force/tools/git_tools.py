"""
Git tool implementations for the Force system.

Provides executors for git-related tools.
"""

import logging
import os
import subprocess
from typing import Dict, Any, Optional, List

from . import BaseToolExecutor

logger = logging.getLogger(__name__)

class GitStatusExecutor(BaseToolExecutor):
    """Executor for git-status tool."""
    
    tool_id = "git_status"
    tool_name = "Git Status"
    tool_category = "git"
    tool_description = "Gets the current git repository status."
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the git status command.
        
        Args:
            parameters: Optional parameters for git status
            context: Execution context
            
        Returns:
            Execution result with git status information
        """
        try:
            # Build command with parameters
            cmd = ["git", "status"]
            
            # Add optional parameters
            if parameters.get("porcelain", False):
                cmd.append("--porcelain")
                
            # Execute command
            logger.info(f"Executing git status: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Process output
            status_output = result.stdout.strip()
            status_lines = status_output.split("\n") if status_output else []
            
            # Return structured result
            return {
                "success": True,
                "output": status_output,
                "lines": status_lines,
                "has_changes": bool(status_output),
                "returncode": result.returncode
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git status command failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode
            }
        except Exception as e:
            logger.error(f"Error executing git status: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GitCommitExecutor(BaseToolExecutor):
    """Executor for git-commit tool."""
    
    tool_id = "grouped_commit_workflow"  # Match the ID from the JSON definition
    tool_name = "Grouped Commit Workflow"
    tool_category = "git"
    tool_description = "Intelligently groups untracked work based on logical changes and creates granular commits."
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the grouped commit workflow.
        
        Args:
            parameters: Parameters for the commit workflow
            context: Execution context
            
        Returns:
            Execution result with commit information
        """
        try:
            # Get current status
            status_result = await GitStatusExecutor(self.force_engine).execute({"porcelain": True}, context)
            if not status_result["success"]:
                return status_result
                
            if not status_result["has_changes"]:
                return {
                    "success": True,
                    "message": "No changes to commit",
                    "commits_created": 0
                }
                
            # Group changes by context (simplified implementation)
            changes = await self._analyze_changes(status_result["lines"])
            
            # Create commits
            commits_created = await self._create_granular_commits(changes, parameters)
            
            # Determine version increment if requested
            version_increment = None
            if parameters.get("semantic_version_increment", "auto") != "none":
                version_increment = await self._determine_version_increment(changes)
                
                if version_increment and parameters.get("tag_version", False):
                    await self._apply_semantic_version_tag(version_increment)
            
            return {
                "success": True,
                "commits_created": commits_created,
                "version_increment": version_increment,
                "message": f"Created {commits_created} commits"
            }
            
        except Exception as e:
            logger.error(f"Error in grouped commit workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _analyze_changes(self, status_lines: List[str]) -> Dict[str, Any]:
        """Analyze and group changes by context."""
        # Simple grouping by file type for demonstration
        groups = {
            "code": [],
            "documentation": [],
            "configuration": [],
            "other": []
        }
        
        for line in status_lines:
            if not line.strip():
                continue
                
            status = line[:2]
            file_path = line[3:].strip()
            
            if file_path.endswith((".md", ".txt", ".rst")):
                groups["documentation"].append((status, file_path))
            elif file_path.endswith((".json", ".yaml", ".yml", ".toml", ".ini")):
                groups["configuration"].append((status, file_path))
            elif file_path.endswith((".py", ".js", ".ts", ".java", ".c", ".cpp")):
                groups["code"].append((status, file_path))
            else:
                groups["other"].append((status, file_path))
                
        return groups
        
    async def _create_granular_commits(self, changes: Dict[str, Any], parameters: Dict[str, Any]) -> int:
        """Create granular commits for each logical group."""
        commit_count = 0
        prefix = parameters.get("commit_message_prefix", "")
        
        # Commit documentation changes
        if changes["documentation"]:
            files = [f[1] for f in changes["documentation"]]
            cmd = ["git", "add"] + files
            subprocess.run(cmd, check=True)
            
            msg = f"{prefix}docs: Update documentation"
            commit_cmd = ["git", "commit", "-m", msg]
            subprocess.run(commit_cmd, check=True)
            commit_count += 1
            
        # Commit configuration changes
        if changes["configuration"]:
            files = [f[1] for f in changes["configuration"]]
            cmd = ["git", "add"] + files
            subprocess.run(cmd, check=True)
            
            msg = f"{prefix}config: Update configuration files"
            commit_cmd = ["git", "commit", "-m", msg]
            subprocess.run(commit_cmd, check=True)
            commit_count += 1
            
        # Commit code changes
        if changes["code"]:
            files = [f[1] for f in changes["code"]]
            cmd = ["git", "add"] + files
            subprocess.run(cmd, check=True)
            
            msg = f"{prefix}feat: Update code implementation"
            commit_cmd = ["git", "commit", "-m", msg]
            subprocess.run(commit_cmd, check=True)
            commit_count += 1
            
        # Commit other changes
        if changes["other"]:
            files = [f[1] for f in changes["other"]]
            cmd = ["git", "add"] + files
            subprocess.run(cmd, check=True)
            
            msg = f"{prefix}chore: Update miscellaneous files"
            commit_cmd = ["git", "commit", "-m", msg]
            subprocess.run(commit_cmd, check=True)
            commit_count += 1
            
        return commit_count
        
    async def _determine_version_increment(self, changes: Dict[str, Any]) -> str:
        """Determine appropriate semantic version increment."""
        # Simple logic for demonstration
        if any("BREAKING CHANGE" in str(f) for group in changes.values() for f in group):
            return "major"
        elif changes["code"]:
            return "minor"
        else:
            return "patch"
            
    async def _apply_semantic_version_tag(self, increment: str) -> None:
        """Apply semantic version tag based on increment."""
        # Get current version
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True
            )
            current_version = result.stdout.strip()
            
            # Parse version
            if current_version.startswith("v"):
                current_version = current_version[1:]
                
            major, minor, patch = map(int, current_version.split("."))
            
            # Increment version
            if increment == "major":
                major += 1
                minor = 0
                patch = 0
            elif increment == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1
                
            new_version = f"v{major}.{minor}.{patch}"
            
            # Create and push tag
            subprocess.run(["git", "tag", new_version], check=True)
            logger.info(f"Created new version tag: {new_version}")
            
        except Exception as e:
            logger.error(f"Error applying version tag: {e}")
            raise
