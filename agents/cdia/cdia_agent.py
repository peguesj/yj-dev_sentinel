"""
Code Documentation Inspector Agent (CDIA)

This module implements the Code Documentation Inspector Agent as specified in the
Dev Sentinel architecture. CDIA is responsible for analyzing code documentation
to ensure it follows best practices and is complete.
"""

import asyncio
import logging
import os
import re
from typing import Dict, List, Any, Optional, Set, Tuple

from core.agent import BaseAgent, AgentStatus
from core.message_bus import get_message_bus
from core.task_manager import get_task_manager, Task
from utils.file_utils import read_file_content # Assuming a utility function

logger = logging.getLogger(__name__)

# Language-specific documentation patterns and rules
LANGUAGE_DOC_PATTERNS = {
    # Python documentation patterns
    "python": {
        "extensions": [".py"],
        "doc_patterns": {
            "class": r'class\s+(\w+).*?:(?:\s*"""(.*?)"""|\s*\'\'\')|\s*#\s*(.*?)$',
            "function": r'def\s+(\w+).*?:(?:\s*"""(.*?)"""|\s*\'\'\')|\s*#\s*(.*?)$',
            "module": r'^"""(.*?)"""|\'\'\',?(.+?)\'\'\'',
        },
        "required_elements": ["param", "return", "raises", "type"],
    },
    # JavaScript/TypeScript documentation patterns
    "javascript": {
        "extensions": [".js", ".jsx", ".ts", ".tsx"],
        "doc_patterns": {
            "class": r'class\s+(\w+).*?{(?:\s*\/\*\*(.*?)\*\/|\s*\/\/\s*(.*?)$)',
            "function": r'function\s+(\w+).*?{(?:\s*\/\*\*(.*?)\*\/|\s*\/\/\s*(.*?)$)',
            "method": r'(\w+)\s*\([^)]*\)\s*{(?:\s*\/\*\*(.*?)\*\/|\s*\/\/\s*(.*?)$)',
        },
        "required_elements": ["param", "returns", "throws", "type"],
    },
    # Ruby documentation patterns
    "ruby": {
        "extensions": [".rb"],
        "doc_patterns": {
            "class": r'class\s+(\w+)(?:\s*#\s*(.*?)$|\s*=begin(.*?)=end)',
            "function": r'def\s+(\w+)(?:\s*#\s*(.*?)$|\s*=begin(.*?)=end)',
            "module": r'module\s+(\w+)(?:\s*#\s*(.*?)$|\s*=begin(.*?)=end)',
        },
        "required_elements": ["param", "return", "raise", "yield"],
    },
    # Elixir documentation patterns
    "elixir": {
        "extensions": [".ex", ".exs"],
        "doc_patterns": {
            "module": r'defmodule\s+(\w+)(?:\s*@doc\s*"""(.*?)"""|\s*#\s*(.*?)$)',
            "function": r'def\s+(\w+)(?:\s*@doc\s*"""(.*?)"""|\s*#\s*(.*?)$)',
            "struct": r'defstruct(?:\s*@doc\s*"""(.*?)"""|\s*#\s*(.*?)$)',
        },
        "required_elements": ["param", "returns", "spec"],
    },
    # Erlang documentation patterns
    "erlang": {
        "extensions": [".erl", ".hrl"],
        "doc_patterns": {
            "module": r'^\s*-\s*module\s*\(([^)]+)\)(?:\s*%+\s*(.*?)$)',
            "function": r'^(\w+)\s*\([^)]*\)\s*->(?:\s*%+\s*(.*?)$)',
        },
        "required_elements": ["param", "return", "spec"],
    },
    # YAML documentation patterns
    "yaml": {
        "extensions": [".yml", ".yaml"],
        "doc_patterns": {
            "document": r'^\s*#\s*(.*?)$',
            "section": r'^\s*(\w+)\s*:(?:\s*#\s*(.*?)$)',
        },
        "required_elements": ["description"],
    },
    # Swift/Objective-C documentation patterns
    "swift": {
        "extensions": [".swift", ".m", ".h"],
        "doc_patterns": {
            "class": r'(?:@interface|class)\s+(\w+)(?:\s*\/\/\/\s*(.*?)$|\s*\/\*\*(.*?)\*\/)',
            "function": r'(?:func|-\s*\(.*?\))\s+(\w+)(?:\s*\/\/\/\s*(.*?)$|\s*\/\*\*(.*?)\*\/)',
            "method": r'(?:-|\+)\s*\([^)]*\)\s*(\w+)(?:\s*\/\/\/\s*(.*?)$|\s*\/\*\*(.*?)\*\/)',
        },
        "required_elements": ["param", "return", "throws"],
    },
    # Shell scripting documentation patterns
    "shell": {
        "extensions": [".sh", ".bash", ".zsh"],
        "doc_patterns": {
            "script": r'^(?:#!.*?\n)(?:\s*#\s*(.*?)$)',
            "function": r'function\s+(\w+)(?:\s*#\s*(.*?)$)',
        },
        "required_elements": ["usage", "arguments", "return"],
    },
    # AppleScript documentation patterns
    "applescript": {
        "extensions": [".scpt", ".applescript"],
        "doc_patterns": {
            "script": r'^(?:\s*--\s*(.*?)$)',
            "handler": r'on\s+(\w+)(?:\s*--\s*(.*?)$)',
        },
        "required_elements": ["param", "return"],
    },
    # PowerShell documentation patterns
    "powershell": {
        "extensions": [".ps1", ".psm1"],
        "doc_patterns": {
            "script": r'^(?:<#(.*?)#>)',
            "function": r'function\s+(\w+)(?:\s*<#(.*?)#>|\s*#\s*(.*?)$)',
        },
        "required_elements": ["param", "return", "example"],
    },
    # PHP documentation patterns
    "php": {
        "extensions": [".php"],
        "doc_patterns": {
            "class": r'class\s+(\w+)(?:\s*\/\*\*(.*?)\*\/)',
            "function": r'function\s+(\w+)(?:\s*\/\*\*(.*?)\*\/)',
        },
        "required_elements": ["param", "return", "throws"],
    },
    # Project definition and configuration files
    "config": {
        "extensions": [".json", ".toml", ".ini", ".xml", ".md", ".gitignore", ".gitattributes", ".editorconfig", ".env.example"],
        "doc_patterns": {
            "document": r'^\s*(?:#|\/\/|\/\*\*|\<!--)\s*(.*?)(?:\*\/|\-->)?$',
            "section": r'^\s*\[([^]]+)\](?:\s*(?:#|\/\/|\/\*\*|\<!--)\s*(.*?)(?:\*\/|\-->)?$)',
        },
        "required_elements": ["purpose", "usage"],
    }
}

class CodeDocumentationInspectorAgent(BaseAgent):
    """
    Code Documentation Inspector Agent implementation.

    The CDIA monitors code repositories to ensure documentation quality and completeness.
    It analyzes source code files against language-specific documentation standards,
    reports issues, and calculates documentation coverage metrics.
    
    Features:
    - Language-specific documentation pattern detection
    - Documentation coverage calculation
    - Automatic inspection triggered by repository events
    - Task-based API for on-demand inspection
    - Integration with version control events for change detection
    - Cross-reference with README inspector results
    
    This agent helps maintain high documentation standards across projects by
    continuously monitoring changes and providing actionable feedback on
    documentation issues.
    """

    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the CDIA."""
        super().__init__(agent_id, config or {})
        self.message_bus = get_message_bus()
        self.task_manager = get_task_manager()

        self.repo_path = self.config.get("repo_path", os.getcwd())
        self.file_extensions = self.config.get("file_extensions", self._get_all_extensions())
        self.excluded_paths = set(self.config.get("excluded_paths", ["node_modules", "venv", ".git", "__pycache__"]))
        self.min_doc_coverage = self.config.get("min_doc_coverage", 0.7)  # Minimum acceptable documentation coverage
        self.last_analyzed_commit: Optional[str] = None

        # Subscribe to relevant messages
        self.message_bus.subscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        self.message_bus.subscribe("vc.repo_refreshed", self._handle_repo_refreshed)
        self.message_bus.subscribe("rdia.inspection_complete", self._handle_readme_inspection)

        # Register task handlers
        self.task_manager.register_handler(f"cdia.{self.agent_id}.inspect_code", self._handle_inspect_code_task)
        self.task_manager.register_handler(f"cdia.{self.agent_id}.inspect_file", self._handle_inspect_file_task)

        self.logger.info(f"CodeDocumentationInspectorAgent ({self.agent_id}) initialized. Monitoring extensions: {self.file_extensions}")

    def _get_all_extensions(self) -> List[str]:
        """Get all file extensions we can analyze from the language patterns."""
        extensions = []
        for language in LANGUAGE_DOC_PATTERNS.values():
            extensions.extend(language["extensions"])
        return extensions

    def _get_language_for_file(self, file_path: str) -> Optional[str]:
        """Determine the language of a file based on its extension."""
        _, ext = os.path.splitext(file_path)
        for language, info in LANGUAGE_DOC_PATTERNS.items():
            if ext in info["extensions"]:
                return language
        return None

    async def start(self) -> None:
        """Start the CDIA."""
        self.update_status(AgentStatus.IDLE)
        self.logger.info(f"CDIA agent {self.agent_id} started.")

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task assigned to this CDIA."""
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
            self.logger.info(f"Received commit analyzed event with {len(code_files)} relevant code files. Triggering inspection.")
            await self.inspect_files([f["path"] for f in code_files], commit_info=message)
        else:
            self.logger.debug(f"No relevant code files changed in commit {commit_hash}.")

    async def _handle_repo_refreshed(self, message: Dict[str, Any]) -> None:
        """Handle notifications that the repository state has been refreshed."""
        self.logger.info("Repository refreshed event received. Triggering code documentation inspection.")
        # Could trigger a scan of all files, but that might be heavy
        # Instead, let's rely on specific requests or limit to recent changes
        # await self.inspect_recent_files()
        pass

    async def _handle_readme_inspection(self, message: Dict[str, Any]) -> None:
        """Handle notifications about README inspection results for correlation."""
        # We could check if README refers to code that's undocumented, or vice versa
        self.logger.debug(f"Received README inspection results for {message.get('path')}")
        # For now, we just log it; could be enhanced to cross-reference results

    async def _handle_inspect_code_task(self, task: Task) -> Dict[str, Any]:
        """Handle a task to inspect code documentation across the project."""
        self.logger.info(f"Received task to inspect project code documentation: {task.task_id}")
        
        # This could potentially scan the entire codebase; using path filters if provided
        path_filters = task.params.get("path_filters", [])
        exclude_filters = task.params.get("exclude_filters", list(self.excluded_paths))
        max_files = task.params.get("max_files", 100)  # Limit to prevent overload
        
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
        
        results = await self.inspect_files(files_to_analyze)
        return {
            "status": "success", 
            "files_analyzed": len(results),
            "results": results
        }

    async def _handle_inspect_file_task(self, task: Task) -> Dict[str, Any]:
        """Handle a task to inspect a specific file's documentation."""
        file_path = task.params.get("file_path")
        if not file_path:
            return {"error": "Missing file_path parameter", "status": "failed"}
            
        self.logger.info(f"Received task to inspect file documentation: {file_path}")
        results = await self.inspect_files([file_path])
        return {
            "status": "success", 
            "results": results[0] if results else {"error": "Failed to analyze file"}
        }

    async def inspect_files(self, file_paths: List[str], commit_info: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Inspect a list of files for code documentation issues.

        Args:
            file_paths: List of file paths to inspect
            commit_info: Optional information about the commit that triggered this inspection

        Returns:
            List of results for each file
        """
        self.update_status(AgentStatus.BUSY)
        self.logger.info(f"Starting code documentation inspection for {len(file_paths)} files...")
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

                content = await read_file_content(file_path)  # Assumes async file read
                self.logger.debug(f"Read {len(content)} bytes from {file_path}")

                # Analyze file documentation
                doc_issues = self._analyze_file_documentation(content, language, file_path)
                doc_coverage = self._calculate_doc_coverage(content, language)

                file_result = {
                    "path": file_path,
                    "language": language,
                    "status": "inspected",
                    "issues_found": len(doc_issues),
                    "issues": doc_issues,
                    "documentation_coverage": doc_coverage,
                    "meets_standards": doc_coverage >= self.min_doc_coverage and len(doc_issues) == 0,
                    "last_commit_analyzed": self.last_analyzed_commit
                }
                results.append(file_result)
                self.logger.info(f"Inspection complete for {file_path}. Found {len(doc_issues)} documentation issues. Coverage: {doc_coverage:.1%}")

                # Publish results
                await self.message_bus.publish(
                    "cdia.inspection_complete",
                    {"path": file_path, "issues": doc_issues, "coverage": doc_coverage, "commit": self.last_analyzed_commit}
                )

            except Exception as e:
                error_msg = f"Error inspecting file {file_path}: {e}"
                self.log_error("file_inspection_failed", error_msg, {"path": file_path})
                results.append({"path": file_path, "status": "error", "error": str(e)})

        self.update_status(AgentStatus.IDLE)
        return results

    def _analyze_file_documentation(self, content: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Analyze a file's code documentation for issues.

        Args:
            content: File content as string
            language: Programming language of the file
            file_path: Path to the file (for reference in issues)

        Returns:
            List of documentation issues found
        """
        issues = []
        language_patterns = LANGUAGE_DOC_PATTERNS.get(language, {})
        doc_patterns = language_patterns.get("doc_patterns", {})
        required_elements = language_patterns.get("required_elements", [])

        # Check if file has a module/file-level docstring
        if "module" in doc_patterns:
            module_pattern = doc_patterns["module"]
            module_doc_match = re.search(module_pattern, content, re.DOTALL)
            if not module_doc_match:
                issues.append({
                    "type": "missing_module_doc",
                    "location": "file_start",
                    "details": f"File is missing a module-level docstring/comment.",
                    "severity": "medium"
                })

        # Count and check functions/methods/classes with missing docs
        if "function" in doc_patterns:
            function_pattern = doc_patterns["function"]
            # Find all function definitions
            function_matches = re.finditer(r'def\s+(\w+)', content)
            for match in function_matches:
                func_name = match.group(1)
                # Skip if it's likely a private function (starts with underscore)
                if func_name.startswith('_') and not func_name.startswith('__'):
                    continue
                    
                # Look for doc comment near the definition
                func_pos = match.start()
                func_line = content[:func_pos].count('\n') + 1
                context_start = max(0, func_pos - 200)  # Look 200 chars before function
                context = content[context_start:func_pos + 100]
                
                if not re.search(function_pattern, context, re.DOTALL):
                    issues.append({
                        "type": "missing_function_doc",
                        "location": f"line:{func_line}",
                        "symbol": func_name,
                        "details": f"Function '{func_name}' is missing documentation.",
                        "severity": "high"
                    })
                else:
                    # Check for required doc elements
                    for element in required_elements:
                        element_pattern = r'@' + element + r'|:' + element + r':|' + element + r':'
                        if not re.search(element_pattern, context, re.IGNORECASE):
                            issues.append({
                                "type": "incomplete_function_doc",
                                "location": f"line:{func_line}",
                                "symbol": func_name,
                                "details": f"Function '{func_name}' documentation is missing '{element}' information.",
                                "severity": "medium"
                            })

        # Similar checks for classes
        if "class" in doc_patterns:
            class_pattern = doc_patterns["class"]
            class_matches = re.finditer(r'class\s+(\w+)', content)
            for match in class_matches:
                class_name = match.group(1)
                class_pos = match.start()
                class_line = content[:class_pos].count('\n') + 1
                context_start = max(0, class_pos - 200)
                context = content[context_start:class_pos + 100]
                
                if not re.search(class_pattern, context, re.DOTALL):
                    issues.append({
                        "type": "missing_class_doc",
                        "location": f"line:{class_line}",
                        "symbol": class_name,
                        "details": f"Class '{class_name}' is missing documentation.",
                        "severity": "high"
                    })

        # Add other language-specific checks here...

        return issues

    def _calculate_doc_coverage(self, content: str, language: str) -> float:
        """
        Calculate documentation coverage as a ratio of documented symbols to total symbols.
        
        Args:
            content: File content as string
            language: Programming language of the file
            
        Returns:
            Float between 0.0 and 1.0 representing documentation coverage
        """
        doc_count = 0
        symbol_count = 0
        language_patterns = LANGUAGE_DOC_PATTERNS.get(language, {})
        
        # Count module docstring
        if "module" in language_patterns.get("doc_patterns", {}):
            module_pattern = language_patterns["doc_patterns"]["module"]
            if re.search(module_pattern, content, re.DOTALL):
                doc_count += 1
            symbol_count += 1
        
        # Count function docstrings
        if "function" in language_patterns.get("doc_patterns", {}):
            # Count all functions (public)
            function_matches = re.finditer(r'def\s+(\w+)', content)
            functions = [m.group(1) for m in function_matches if not m.group(1).startswith('_')]
            symbol_count += len(functions)
            
            # Count functions with docs
            function_pattern = language_patterns["doc_patterns"]["function"]
            for func_name in functions:
                if re.search(function_pattern + r'.*?' + func_name, content, re.DOTALL):
                    doc_count += 1
        
        # Count class docstrings
        if "class" in language_patterns.get("doc_patterns", {}):
            class_matches = re.finditer(r'class\s+(\w+)', content)
            classes = [m.group(1) for m in class_matches]
            symbol_count += len(classes)
            
            class_pattern = language_patterns["doc_patterns"]["class"]
            for class_name in classes:
                if re.search(class_pattern + r'.*?' + class_name, content, re.DOTALL):
                    doc_count += 1
        
        # Default to 1.0 if no symbols detected to avoid division by zero
        if symbol_count == 0:
            return 1.0
            
        return doc_count / symbol_count

    async def shutdown(self) -> None:
        """Perform clean shutdown of the CDIA."""
        self.logger.info(f"Shutting down CDIA {self.agent_id}")
        self.update_status(AgentStatus.TERMINATED)

        # Unsubscribe from message bus topics
        self.message_bus.unsubscribe("vc.commit_analyzed", self._handle_commit_analyzed)
        self.message_bus.unsubscribe("vc.repo_refreshed", self._handle_repo_refreshed)
        self.message_bus.unsubscribe("rdia.inspection_complete", self._handle_readme_inspection)

        # Unregister task handlers
        self.task_manager.unregister_handler(f"cdia.{self.agent_id}.inspect_code", self._handle_inspect_code_task)
        self.task_manager.unregister_handler(f"cdia.{self.agent_id}.inspect_file", self._handle_inspect_file_task)

        self.logger.info(f"CDIA {self.agent_id} shutdown complete.")


# Factory function to create an instance
def create_cdia(config: Optional[Dict[str, Any]] = None) -> CodeDocumentationInspectorAgent:
    """
    Create a new Code Documentation Inspector Agent instance.

    Args:
        config: Optional configuration dictionary. Should include 'agent_id'.
                May include 'repo_path', 'file_extensions', 'excluded_paths', 'min_doc_coverage'.

    Returns:
        New CDIA instance.
    """
    if not config or "agent_id" not in config:
         raise ValueError("CDIA configuration must include an 'agent_id'")
    return CodeDocumentationInspectorAgent(agent_id=config["agent_id"], config=config)