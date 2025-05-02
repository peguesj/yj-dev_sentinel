"""
Static Analysis Agent (SAA)

This module implements the Static Analysis Agent as specified in the
Dev Sentinel architecture. SAA is responsible for analyzing code quality
using static analysis tools and providing reports on potential issues.
"""

import asyncio
import logging
import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Set, Tuple

from core.agent import BaseAgent, AgentStatus
from core.message_bus import get_message_bus
from core.task_manager import get_task_manager, Task

logger = logging.getLogger(__name__)

# Linting and static analysis configurations for different languages
STATIC_ANALYSIS_TOOLS = {
    "python": {
        "extensions": [".py"],
        "tools": {
            "pylint": {
                "command": "pylint --output-format=json {file_path}",
                "result_processor": "_process_pylint_results"
            },
            "mypy": {
                "command": "mypy --show-column-numbers --json {file_path}",
                "result_processor": "_process_mypy_results"
            },
            "flake8": {
                "command": "flake8 --format=json {file_path}",
                "result_processor": "_process_flake8_results"
            }
        }
    },
    "javascript": {
        "extensions": [".js", ".jsx", ".ts", ".tsx"],
        "tools": {
            "eslint": {
                "command": "eslint -f json {file_path}",
                "result_processor": "_process_eslint_results"
            },
            "tsc": {
                "command": "tsc --noEmit --project {tsconfig_path} {file_path}",
                "result_processor": "_process_tsc_results"
            }
        }
    },
    "ruby": {
        "extensions": [".rb"],
        "tools": {
            "rubocop": {
                "command": "rubocop --format json {file_path}",
                "result_processor": "_process_rubocop_results"
            }
        }
    },
    "elixir": {
        "extensions": [".ex", ".exs"],
        "tools": {
            "credo": {
                "command": "mix credo {file_path} --format json",
                "result_processor": "_process_credo_results"
            }
        }
    },
    "php": {
        "extensions": [".php"],
        "tools": {
            "phpstan": {
                "command": "phpstan analyse --error-format=json {file_path}",
                "result_processor": "_process_phpstan_results"
            }
        }
    },
    "swift": {
        "extensions": [".swift"],
        "tools": {
            "swiftlint": {
                "command": "swiftlint lint --reporter json {file_path}",
                "result_processor": "_process_swiftlint_results"
            }
        }
    },
    "go": {
        "extensions": [".go"],
        "tools": {
            "golint": {
                "command": "golint -json {file_path}",
                "result_processor": "_process_golint_results"
            }
        }
    },
    "shell": {
        "extensions": [".sh", ".bash"],
        "tools": {
            "shellcheck": {
                "command": "shellcheck -f json {file_path}",
                "result_processor": "_process_shellcheck_results"
            }
        }
    }
}


class StaticAnalysisAgent(BaseAgent):
    """
    Static Analysis Agent implementation.

    The SAA performs comprehensive static code analysis across multiple programming
    languages to identify potential issues, bugs, and code quality concerns before
    they impact application stability or performance. It serves as a critical early
    detection system in the development workflow.
    
    Features:
    - Multi-language support (Python, JavaScript/TypeScript, Ruby, Elixir, PHP, Swift, Go, Shell)
    - Integration with numerous industry-standard analysis tools
    - Tool-specific result processing and normalization
    - Configurable severity thresholds and issue reporting
    - Path exclusion for avoiding analysis of third-party code
    - Event-driven analysis triggered by repository changes
    - Selective file analysis based on extensions and paths
    - Standardized issue reporting format across languages and tools
    - Task-based API for on-demand analysis
    
    The SAA helps maintain code quality by providing automated feedback on
    coding standards, potential bugs, type issues, and other code quality concerns
    throughout the development lifecycle.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the SAA."""
        super().__init__(agent_id, config or {})
        self.message_bus = get_message_bus()
        self.task_manager = get_task_manager()

        self.repo_path = self.config.get("repo_path", os.getcwd())
        self.file_extensions = self._get_all_extensions()
        self.excluded_paths = set(self.config.get("excluded_paths", ["node_modules", "venv", ".git", "__pycache__"]))
        self.severity_threshold = self.config.get("severity_threshold", "warning")  # Minimum severity level to report
        self.max_issues_per_file = self.config.get("max_issues_per_file", 50)
        self.tool_configs = self.config.get("tool_configs", {})  # Optional tool-specific configs
        self.last_analyzed_commit: Optional[str] = None

        # Subscribe to relevant messages
        self.message_bus.subscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        self.message_bus.subscribe("vc.repo_refreshed", self._handle_repo_refreshed)

        # Register task handlers
        self.task_manager.register_handler(f"saa.{self.agent_id}.analyze", self._handle_analyze_task)
        self.task_manager.register_handler(f"saa.{self.agent_id}.analyze_file", self._handle_analyze_file_task)

        self.logger.info(f"StaticAnalysisAgent ({self.agent_id}) initialized. "
                       f"Monitoring extensions: {self.file_extensions}")

    def _get_all_extensions(self) -> List[str]:
        """Get all file extensions that can be analyzed from the static analysis tools config."""
        extensions = []
        for language in STATIC_ANALYSIS_TOOLS.values():
            extensions.extend(language["extensions"])
        return extensions

    def _get_language_for_file(self, file_path: str) -> Optional[str]:
        """Determine the language of a file based on its extension."""
        _, ext = os.path.splitext(file_path)
        for language, info in STATIC_ANALYSIS_TOOLS.items():
            if ext in info["extensions"]:
                return language
        return None
        
    def _get_tools_for_language(self, language: str) -> Dict[str, Dict[str, str]]:
        """Get the available analysis tools for a language."""
        if language in STATIC_ANALYSIS_TOOLS:
            return STATIC_ANALYSIS_TOOLS[language]["tools"]
        return {}

    async def start(self) -> None:
        """Start the SAA."""
        self.update_status(AgentStatus.IDLE)
        self.logger.info(f"SAA agent {self.agent_id} started.")

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task assigned to this SAA."""
        self.logger.debug(f"Processing task {task.task_id}: {task.task_type}")
        handler = self.task_manager.get_handler(task.task_type)
        if handler:
            return await handler(task)
        else:
            error_msg = f"No handler registered for task type: {task.task_type}"
            self.log_error("task_handler_not_found", error_msg, {"task_id": task.task_id})
            return {"error": error_msg, "status": "failed"}

    async def _handle_commit_analyzed(self, message: Dict[str, Any]) -> None:
        """Handle notifications about newly analyzed commits, focusing on code files."""
        commit_hash = message.get("commit_hash")
        files_changed = message.get("files_changed", [])
        self.last_analyzed_commit = commit_hash
        
        # Filter to only files we care about
        code_files = [
            f for f in files_changed if any(f["path"].endswith(ext) for ext in self.file_extensions) and 
            not any(exclude in f["path"] for exclude in self.excluded_paths)
        ]
        
        if code_files:
            self.logger.info(f"Received commit analyzed event with {len(code_files)} relevant code files. "
                           f"Triggering static analysis.")
            await self.analyze_files([f["path"] for f in code_files], commit_info=message)
        else:
            self.logger.debug(f"No relevant code files changed in commit {commit_hash}.")

    async def _handle_repo_refreshed(self, message: Dict[str, Any]) -> None:
        """Handle notifications that the repository state has been refreshed."""
        # Optional: Could trigger analysis of recently modified files
        pass

    async def _handle_analyze_task(self, task: Task) -> Dict[str, Any]:
        """Handle a task to analyze code across the project or specific paths."""
        self.logger.info(f"Received task to perform static analysis: {task.task_id}")
        
        path_filters = task.params.get("path_filters", [])
        exclude_filters = task.params.get("exclude_filters", list(self.excluded_paths))
        max_files = task.params.get("max_files", 100)
        
        # Find files to analyze
        files_to_analyze = []
        for root, _, files in os.walk(self.repo_path):
            # Skip excluded paths
            if any(exclude in root for exclude in exclude_filters):
                continue
                
            # Apply path filters if specified
            if path_filters and not any(root.startswith(os.path.join(self.repo_path, p)) for p in path_filters):
                continue
                
            for file in files:
                if len(files_to_analyze) >= max_files:
                    break
                    
                if any(file.endswith(ext) for ext in self.file_extensions):
                    files_to_analyze.append(os.path.join(root, file))
        
        results = await self.analyze_files(files_to_analyze)
        return {
            "status": "success", 
            "files_analyzed": len(results),
            "results": results
        }

    async def _handle_analyze_file_task(self, task: Task) -> Dict[str, Any]:
        """Handle a task to analyze a specific file."""
        file_path = task.params.get("file_path")
        if not file_path:
            return {"error": "Missing file_path parameter", "status": "failed"}
            
        self.logger.info(f"Received task to analyze file: {file_path}")
        results = await self.analyze_files([file_path])
        return {
            "status": "success", 
            "results": results[0] if results else {"error": "Failed to analyze file"}
        }

    async def analyze_files(self, file_paths: List[str], commit_info: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Analyze a list of files using appropriate static analysis tools.

        Args:
            file_paths: List of file paths to analyze
            commit_info: Optional information about the commit that triggered this analysis

        Returns:
            List of results for each file
        """
        self.update_status(AgentStatus.BUSY)
        self.logger.info(f"Starting static analysis for {len(file_paths)} files...")
        results = []

        for file_path in file_paths:
            try:
                # Skip files we don't care about or can't analyze
                language = self._get_language_for_file(file_path)
                if not language:
                    self.logger.debug(f"Skipping {file_path}: Unsupported file type")
                    continue

                if not os.path.exists(file_path):
                    self.logger.warning(f"File not found: {file_path}")
                    results.append({"path": file_path, "status": "not_found"})
                    continue

                # Get the tools for this language
                tools = self._get_tools_for_language(language)
                if not tools:
                    self.logger.warning(f"No analysis tools available for {language} files")
                    results.append({"path": file_path, "status": "no_tools_available", "language": language})
                    continue

                file_result = {
                    "path": file_path,
                    "language": language,
                    "status": "analyzed",
                    "tools_run": [],
                    "issues": [],
                    "last_commit_analyzed": self.last_analyzed_commit
                }

                # Run each applicable tool
                for tool_name, tool_info in tools.items():
                    try:
                        # Check if tool is configured to be skipped
                        if self.tool_configs.get(tool_name, {}).get("skip", False):
                            continue
                            
                        # Run the tool and process results
                        command = tool_info["command"].format(file_path=file_path, 
                                                            tsconfig_path=os.path.join(self.repo_path, "tsconfig.json"))
                        tool_result = await self._run_analysis_tool(command)
                        
                        # Process results if we have a processor method
                        if "result_processor" in tool_info:
                            processor_method = getattr(self, tool_info["result_processor"])
                            if callable(processor_method):
                                tool_issues = processor_method(tool_result)
                                file_result["issues"].extend(tool_issues)
                                file_result["tools_run"].append(tool_name)
                    except Exception as e:
                        self.logger.error(f"Error running {tool_name} on {file_path}: {e}")
                        file_result.setdefault("tool_errors", []).append({
                            "tool": tool_name,
                            "error": str(e)
                        })

                # Limit the number of issues reported per file
                if len(file_result["issues"]) > self.max_issues_per_file:
                    file_result["issues"] = file_result["issues"][:self.max_issues_per_file]
                    file_result["issues_truncated"] = True

                results.append(file_result)
                self.logger.info(f"Analysis complete for {file_path}. "
                               f"Found {len(file_result['issues'])} issues using {len(file_result['tools_run'])} tools.")

                # Publish results
                await self.message_bus.publish(
                    "saa.analysis_complete",
                    {"path": file_path, "issues": file_result["issues"], "commit": self.last_analyzed_commit}
                )

            except Exception as e:
                error_msg = f"Error analyzing file {file_path}: {e}"
                self.log_error("file_analysis_failed", error_msg, {"path": file_path})
                results.append({"path": file_path, "status": "error", "error": str(e)})

        self.update_status(AgentStatus.IDLE)
        return results

    async def _run_analysis_tool(self, command: str) -> Dict[str, Any]:
        """
        Run an analysis tool command and return the results.

        Args:
            command: The command to execute

        Returns:
            Dictionary containing the tool output
        """
        try:
            self.logger.debug(f"Running command: {command}")
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                # Some tools return non-zero exit codes even for successful runs with issues
                self.logger.debug(f"Command exited with code {process.returncode}: {stderr.decode()}")
            
            # Try to parse JSON output
            try:
                result = json.loads(stdout.decode())
                return result
            except json.JSONDecodeError:
                # Return as text if not JSON
                return {"text_output": stdout.decode(), "stderr": stderr.decode()}
                
        except Exception as e:
            self.logger.error(f"Error running analysis command: {e}")
            return {"error": str(e)}

    # --- Result Processors ---

    def _process_pylint_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process pylint results into standard format."""
        issues = []
        for item in results:
            issues.append({
                "tool": "pylint",
                "rule_id": item.get("symbol", ""),
                "severity": self._map_pylint_severity(item.get("type", "")),
                "message": item.get("message", ""),
                "location": f"line:{item.get('line', 0)}:col:{item.get('column', 0)}",
            })
        return issues

    def _process_mypy_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process mypy results into standard format."""
        issues = []
        for item in results.get("data", {}).get("errors", []):
            issues.append({
                "tool": "mypy",
                "rule_id": item.get("code", ""),
                "severity": "error" if item.get("error_code") else "warning",
                "message": item.get("message", ""),
                "location": f"line:{item.get('line', 0)}:col:{item.get('column', 0)}",
            })
        return issues

    def _process_flake8_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process flake8 results into standard format."""
        issues = []
        for file_path, file_errors in results.items():
            for error in file_errors:
                issues.append({
                    "tool": "flake8",
                    "rule_id": error.get("code", ""),
                    "severity": "warning",
                    "message": error.get("text", ""),
                    "location": f"line:{error.get('line_number', 0)}:col:{error.get('column_number', 0)}",
                })
        return issues

    def _process_eslint_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process eslint results into standard format."""
        issues = []
        for file_result in results:
            for message in file_result.get("messages", []):
                issues.append({
                    "tool": "eslint",
                    "rule_id": message.get("ruleId", ""),
                    "severity": self._map_eslint_severity(message.get("severity", 1)),
                    "message": message.get("message", ""),
                    "location": f"line:{message.get('line', 0)}:col:{message.get('column', 0)}",
                })
        return issues

    def _process_tsc_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process TypeScript compiler results into standard format."""
        issues = []
        # TSC often outputs plain text, so we may need to parse it if not in JSON
        if "text_output" in results:
            lines = results["text_output"].split('\n')
            for line in lines:
                # Parse error lines like: file.ts(line,col): error TS2345: Type 'string' is not assignable to type 'number'.
                if ":" in line and ("error" in line or "warning" in line):
                    parts = line.split(':', 3)
                    if len(parts) >= 3:
                        location_part = parts[0]
                        error_type = "error" if "error" in parts[1] else "warning"
                        message = parts[2].strip() if len(parts) > 2 else ""
                        
                        # Extract line and column from location_part
                        import re
                        loc_match = re.search(r'\((\d+),(\d+)\)', location_part)
                        line_num = loc_match.group(1) if loc_match else "0"
                        col_num = loc_match.group(2) if loc_match else "0"
                        
                        issues.append({
                            "tool": "tsc",
                            "rule_id": "",
                            "severity": error_type,
                            "message": message,
                            "location": f"line:{line_num}:col:{col_num}",
                        })
        return issues

    # Add more result processors for other tools as needed...

    # --- Utility Methods ---

    def _map_pylint_severity(self, severity_type: str) -> str:
        """Map pylint message types to standard severity."""
        mapping = {
            "error": "error",
            "warning": "warning",
            "convention": "info",
            "refactor": "info",
            "info": "info"
        }
        return mapping.get(severity_type.lower(), "info")

    def _map_eslint_severity(self, severity: int) -> str:
        """Map ESLint severity levels to standard severity."""
        if severity == 2:
            return "error"
        elif severity == 1:
            return "warning"
        else:
            return "info"

    async def shutdown(self) -> None:
        """Perform clean shutdown of the SAA."""
        self.logger.info(f"Shutting down SAA {self.agent_id}")
        self.update_status(AgentStatus.TERMINATED)

        # Unsubscribe from message bus topics
        self.message_bus.unsubscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        self.message_bus.unsubscribe("vc.repo_refreshed", self._handle_repo_refreshed)

        # Unregister task handlers
        self.task_manager.unregister_handler(f"saa.{self.agent_id}.analyze", self._handle_analyze_task)
        self.task_manager.unregister_handler(f"saa.{self.agent_id}.analyze_file", self._handle_analyze_file_task)

        self.logger.info(f"SAA {self.agent_id} shutdown complete.")


# Factory function to create an instance
def create_saa(config: Optional[Dict[str, Any]] = None) -> StaticAnalysisAgent:
    """
    Create a new Static Analysis Agent instance.

    Args:
        config: Optional configuration dictionary. Should include 'agent_id'.
                May include 'repo_path', 'excluded_paths', 'severity_threshold',
                'max_issues_per_file', and 'tool_configs'.

    Returns:
        New SAA instance.
    """
    if not config or "agent_id" not in config:
         raise ValueError("SAA configuration must include an 'agent_id'")
    return StaticAnalysisAgent(agent_id=config["agent_id"], config=config)