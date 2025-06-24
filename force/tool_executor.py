"""
Tool executor module for the Force system.

Handles the execution of Force tools with comprehensive validation,
monitoring, and error handling.
"""

import asyncio
import subprocess
import logging
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ToolExecutor:
    """Handles Force tool execution with monitoring and validation."""
    
    def __init__(self, force_engine):
        """Initialize the tool executor with reference to Force engine."""
        self.force_engine = force_engine
        self._active_executions = {}
    
    async def execute_tool_command(self, tool: Dict[str, Any], parameters: Dict[str, Any], 
                                 context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a tool command with proper handling and monitoring.
        
        Args:
            tool: Tool definition from Force configuration
            parameters: Validated parameters for execution
            context: Execution context information
            
        Returns:
            Execution result
        """
        execution = tool.get("execution", {})
        command = execution.get("command", "")
        timeout = execution.get("timeout", 300)
        
        # Replace command with actual implementation based on tool type
        if command.startswith("force_"):
            return await self._execute_force_command(command, tool, parameters, context)
        else:
            return await self._execute_shell_command(command, parameters, context, timeout)
    
    async def _execute_force_command(self, command: str, tool: Dict[str, Any], 
                                   parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Any:
        """Execute Force-specific commands."""
        try:
            if command == "force_git_commit":
                return await self._execute_git_commit(parameters, context)
            elif command == "force_git_branch":
                return await self._execute_git_branch(parameters, context)
            elif command == "force_doc_analysis":
                return await self._execute_doc_analysis(parameters, context)
            elif command == "force_code_quality":
                return await self._execute_code_quality(parameters, context)
            elif command == "force_project_analysis":
                return await self._execute_project_analysis(parameters, context)
            else:
                raise ValueError(f"Unknown Force command: {command}")
                
        except Exception as e:
            logger.error(f"Force command execution failed: {e}")
            raise
    
    async def _execute_git_commit(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute git commit workflow."""
        scope = parameters.get("scope", "chore")
        message = parameters.get("message")
        semantic_version = parameters.get("semanticVersionIncrement", "patch")
        include_files = parameters.get("includeFiles", [])
        exclude_files = parameters.get("excludeFiles", [])
        dry_run = parameters.get("dryRun", False)
        
        result = {
            "command": "git_commit",
            "scope": scope,
            "dry_run": dry_run,
            "files_staged": [],
            "commit_message": "",
            "commit_hash": None
        }
        
        try:
            # Check for changes
            status_result = await self._run_command("git status --porcelain")
            if not status_result["stdout"].strip():
                raise ValueError("No changes to commit")
            
            # Stage files
            if include_files:
                for file_path in include_files:
                    if file_path not in exclude_files:
                        await self._run_command(f"git add {file_path}")
                        result["files_staged"].append(file_path)
            else:
                # Stage all modified files except excluded ones
                changed_files = [line.split()[1] for line in status_result["stdout"].strip().split('\n') if line.strip()]
                for file_path in changed_files:
                    if file_path not in exclude_files:
                        await self._run_command(f"git add {file_path}")
                        result["files_staged"].append(file_path)
            
            # Generate commit message if not provided
            if not message:
                message = f"{scope}: automated commit with {len(result['files_staged'])} file(s)"
            
            result["commit_message"] = message
            
            if not dry_run:
                # Perform the commit
                commit_result = await self._run_command(f'git commit -m "{message}"')
                if commit_result["returncode"] == 0:
                    # Get commit hash
                    hash_result = await self._run_command("git rev-parse HEAD")
                    result["commit_hash"] = hash_result["stdout"].strip()
                else:
                    raise ValueError(f"Commit failed: {commit_result['stderr']}")
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            return result
    
    async def _execute_git_branch(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute git branch creation."""
        branch_name = parameters["branchName"]
        branch_type = parameters.get("branchType", "feature")
        base_branch = parameters.get("baseBranch", "main")
        switch_to_branch = parameters.get("switchToBranch", True)
        
        # Format branch name with type prefix if not already present
        if not branch_name.startswith(f"{branch_type}/"):
            formatted_branch_name = f"{branch_type}/{branch_name}"
        else:
            formatted_branch_name = branch_name
        
        result = {
            "command": "git_branch",
            "branch_name": formatted_branch_name,
            "base_branch": base_branch,
            "switched": False
        }
        
        try:
            # Check if branch already exists
            branch_check = await self._run_command(f"git branch --list {formatted_branch_name}")
            if branch_check["stdout"].strip():
                raise ValueError(f"Branch {formatted_branch_name} already exists")
            
            # Create branch
            create_result = await self._run_command(f"git checkout -b {formatted_branch_name} {base_branch}")
            if create_result["returncode"] != 0:
                raise ValueError(f"Failed to create branch: {create_result['stderr']}")
            
            result["switched"] = switch_to_branch
            result["success"] = True
            return result
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            return result
    
    async def _execute_doc_analysis(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute documentation analysis."""
        target_files = parameters.get("targetFiles", ["README.md", "docs/**/*.md"])
        check_links = parameters.get("checkLinks", True)
        check_code_examples = parameters.get("checkCodeExamples", True)
        generate_report = parameters.get("generateReport", True)
        
        result = {
            "command": "documentation_analysis",
            "files_analyzed": [],
            "issues_found": [],
            "report": None
        }
        
        try:
            # Find documentation files
            doc_files = []
            for pattern in target_files:
                if pattern.startswith("**"):
                    # Use glob to find files
                    from pathlib import Path
                    files = list(Path(".").glob(pattern))
                    doc_files.extend([str(f) for f in files if f.is_file()])
                elif os.path.exists(pattern):
                    doc_files.append(pattern)
            
            result["files_analyzed"] = doc_files
            
            # Analyze each file
            for doc_file in doc_files:
                if os.path.exists(doc_file):
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Basic analysis
                        if len(content.strip()) == 0:
                            result["issues_found"].append({
                                "file": doc_file,
                                "type": "empty_file",
                                "severity": "warning",
                                "message": "File is empty"
                            })
                        
                        # Check for basic structure (headers, etc.)
                        if not content.startswith('#'):
                            result["issues_found"].append({
                                "file": doc_file,
                                "type": "missing_header",
                                "severity": "info",
                                "message": "File does not start with a header"
                            })
                        
                        # TODO: Implement link checking and code example validation
                        
                    except Exception as e:
                        result["issues_found"].append({
                            "file": doc_file,
                            "type": "read_error",
                            "severity": "error",
                            "message": f"Could not read file: {str(e)}"
                        })
            
            if generate_report:
                result["report"] = {
                    "total_files": len(doc_files),
                    "files_with_issues": len(set(issue["file"] for issue in result["issues_found"])),
                    "total_issues": len(result["issues_found"]),
                    "issue_breakdown": {}
                }
                
                # Categorize issues
                for issue in result["issues_found"]:
                    issue_type = issue["type"]
                    if issue_type not in result["report"]["issue_breakdown"]:
                        result["report"]["issue_breakdown"][issue_type] = 0
                    result["report"]["issue_breakdown"][issue_type] += 1
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            return result
    
    async def _execute_code_quality(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute code quality analysis."""
        target_files = parameters.get("targetFiles", ["**/*.py"])
        linters = parameters.get("linters", ["flake8"])
        auto_fix = parameters.get("autoFix", False)
        generate_report = parameters.get("generateReport", True)
        
        result = {
            "command": "code_quality",
            "linters_run": [],
            "issues_found": [],
            "auto_fixed": [],
            "report": None
        }
        
        try:
            # Run each linter
            for linter in linters:
                if linter == "flake8":
                    linter_result = await self._run_command("flake8 --format=json .", capture_output=True)
                    result["linters_run"].append(linter)
                    
                    if linter_result["stdout"]:
                        try:
                            issues = json.loads(linter_result["stdout"])
                            result["issues_found"].extend(issues)
                        except json.JSONDecodeError:
                            # Fallback to text parsing
                            lines = linter_result["stdout"].strip().split('\n')
                            for line in lines:
                                if ':' in line:
                                    result["issues_found"].append({
                                        "linter": linter,
                                        "message": line.strip()
                                    })
                
                elif linter == "mypy":
                    linter_result = await self._run_command("mypy --show-error-codes .", capture_output=True)
                    result["linters_run"].append(linter)
                    
                    if linter_result["stdout"]:
                        lines = linter_result["stdout"].strip().split('\n')
                        for line in lines:
                            if ':' in line and 'error:' in line:
                                result["issues_found"].append({
                                    "linter": linter,
                                    "message": line.strip()
                                })
                
                # TODO: Implement other linters (pylint, black, isort)
            
            if generate_report:
                result["report"] = {
                    "linters_run": len(result["linters_run"]),
                    "total_issues": len(result["issues_found"]),
                    "issues_by_linter": {}
                }
                
                for issue in result["issues_found"]:
                    linter = issue.get("linter", "unknown")
                    if linter not in result["report"]["issues_by_linter"]:
                        result["report"]["issues_by_linter"][linter] = 0
                    result["report"]["issues_by_linter"][linter] += 1
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            return result
    
    async def _execute_project_analysis(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute project structure analysis."""
        project_type = parameters.get("projectType", "python-package")
        check_naming = parameters.get("checkNaming", True)
        check_structure = parameters.get("checkStructure", True)
        suggest_improvements = parameters.get("suggestImprovements", True)
        
        result = {
            "command": "project_analysis",
            "project_type": project_type,
            "structure_issues": [],
            "naming_issues": [],
            "suggestions": []
        }
        
        try:
            # Analyze project structure
            if check_structure:
                expected_files = {
                    "python-package": ["setup.py", "requirements.txt", "README.md", "__init__.py"],
                    "web-app": ["requirements.txt", "app.py", "templates/", "static/"],
                    "cli-tool": ["setup.py", "requirements.txt", "README.md", "main.py"],
                    "library": ["setup.py", "requirements.txt", "README.md", "__init__.py", "tests/"]
                }.get(project_type, [])
                
                for expected_file in expected_files:
                    if not os.path.exists(expected_file):
                        result["structure_issues"].append({
                            "type": "missing_file",
                            "file": expected_file,
                            "severity": "warning",
                            "message": f"Expected file/directory not found: {expected_file}"
                        })
            
            # Check naming conventions
            if check_naming:
                # Check for Python naming conventions
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if file.endswith(".py"):
                            if "-" in file:  # Python files should use underscores
                                result["naming_issues"].append({
                                    "type": "naming_convention",
                                    "file": os.path.join(root, file),
                                    "severity": "info",
                                    "message": "Python files should use underscores instead of hyphens"
                                })
            
            # Generate suggestions
            if suggest_improvements:
                if project_type == "python-package" and not os.path.exists("tests/"):
                    result["suggestions"].append({
                        "type": "add_testing",
                        "priority": "high",
                        "message": "Consider adding a tests/ directory with unit tests"
                    })
                
                if not os.path.exists(".gitignore"):
                    result["suggestions"].append({
                        "type": "add_gitignore",
                        "priority": "medium",
                        "message": "Consider adding a .gitignore file"
                    })
            
            result["success"] = True
            return result
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            return result
    
    async def _execute_shell_command(self, command: str, parameters: Dict[str, Any], 
                                   context: Optional[Dict[str, Any]], timeout: int = 300) -> Any:
        """Execute a shell command with timeout and monitoring."""
        try:
            # Substitute parameters in command if needed
            formatted_command = command.format(**parameters)
            
            result = await self._run_command(formatted_command, timeout=timeout)
            
            return {
                "command": formatted_command,
                "returncode": result["returncode"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "success": result["returncode"] == 0
            }
            
        except Exception as e:
            return {
                "command": command,
                "success": False,
                "error": str(e)
            }
    
    async def _run_command(self, command: str, timeout: int = 300, capture_output: bool = True) -> Dict[str, Any]:
        """Run a shell command with proper error handling."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                cwd=os.getcwd()
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8") if stdout else "",
                "stderr": stderr.decode("utf-8") if stderr else ""
            }
            
        except asyncio.TimeoutError:
            if process:
                process.terminate()
                await process.wait()
            raise ValueError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise ValueError(f"Command execution failed: {str(e)}")
