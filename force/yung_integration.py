"""
YUNG Command Integration with Force System.

This module provides the integration layer between the legacy YUNG command 
processing system and the new Force tools and patterns, enabling backward
compatibility while adding Force capabilities.
"""

import os
import json
import logging
import asyncio
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timezone
from pathlib import Path

from . import ForceEngine, ForceEngineError
from .legacy_adapter import create_force_adapter, LegacyAgentAdapter

logger = logging.getLogger(__name__)

class YUNGForceIntegration:
    """
    Integration layer for YUNG commands with Force system.
    
    Provides:
    - YUNG command parsing and routing to Force tools
    - Legacy command translation to Force patterns
    - Enhanced command execution with Force capabilities
    - Command history and learning integration
    """
    
    def __init__(self, force_engine: Optional[ForceEngine] = None):
        """
        Initialize the YUNG-Force integration.
        
        Args:
            force_engine: Optional Force engine instance
        """
        self.force_engine = force_engine or ForceEngine()
        self._command_mapping = {}
        self._pattern_mapping = {}
        self._agent_adapters = {}
        
        # Command execution history
        self._command_history = []
        self._execution_stats = {}
        
        # Initialize mappings
        self._initialize_command_mappings()
        
    def _initialize_command_mappings(self):
        """Initialize YUNG to Force command mappings."""
        
        # Direct command to Force tool mappings
        self._command_mapping = {
            # Git operations
            "git_status": "git-status",
            "git_log": "git-log", 
            "git_diff": "git-diff",
            "git_branch": "git-branch-ops",
            "git_commit": "git-commit",
            "git_pull": "git-pull",
            "git_push": "git-push",
            
            # Documentation operations
            "analyze_docs": "docs-analysis",
            "validate_docs": "docs-validation",
            "generate_docs": "docs-generation",
            "readme_check": "readme-analysis",
            
            # Code analysis
            "static_analysis": "static-analysis",
            "code_quality": "code-quality-check",
            "security_scan": "security-analysis",
            "dependency_check": "dependency-analysis",
            
            # File operations
            "file_read": "filesystem-read",
            "file_write": "filesystem-write",
            "file_search": "filesystem-search",
            "project_structure": "project-structure-analysis",
            
            # Workflow operations
            "run_tests": "test-execution",
            "build_project": "build-workflow",
            "deploy": "deployment-workflow",
        }
        
        # Command to Force pattern mappings
        self._pattern_mapping = {
            # Analysis workflows
            "full_analysis": "comprehensive-analysis-workflow",
            "code_review": "code-review-workflow", 
            "quality_check": "quality-assurance-workflow",
            "security_audit": "security-audit-workflow",
            
            # Development workflows
            "feature_development": "feature-development-workflow",
            "bug_fix": "bug-fix-workflow",
            "refactoring": "refactoring-workflow",
            "testing": "testing-workflow",
            
            # Documentation workflows
            "doc_update": "documentation-update-workflow",
            "api_docs": "api-documentation-workflow",
            
            # Release workflows
            "pre_release": "pre-release-workflow",
            "release": "release-workflow",
            "post_release": "post-release-workflow",
        }
    
    async def process_yung_command(self, command: str, parameters: Optional[Dict[str, Any]] = None,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a YUNG command through the Force system.
        
        Args:
            command: YUNG command string
            parameters: Command parameters
            context: Execution context
            
        Returns:
            Command execution result
        """
        start_time = datetime.now(timezone.utc)
        parameters = parameters or {}
        context = context or {}
        
        try:
            # Parse YUNG command
            parsed_command = self._parse_yung_command(command)
            
            # Determine execution strategy
            execution_strategy = self._determine_execution_strategy(parsed_command)
            
            # Execute through appropriate strategy
            if execution_strategy == "force_tool":
                result = await self._execute_as_force_tool(parsed_command, parameters, context)
            elif execution_strategy == "force_pattern":
                result = await self._execute_as_force_pattern(parsed_command, parameters, context)
            elif execution_strategy == "agent_adapter":
                result = await self._execute_through_agent_adapter(parsed_command, parameters, context)
            else:
                result = await self._execute_legacy_command(parsed_command, parameters, context)
            
            # Record execution for learning
            execution_record = {
                "timestamp": start_time.isoformat(),
                "command": command,
                "parsed_command": parsed_command,
                "parameters": parameters,
                "context": context,
                "strategy": execution_strategy,
                "result": result,
                "duration": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "success": result.get("success", True)
            }
            
            self._command_history.append(execution_record)
            self._update_execution_stats(execution_strategy, result.get("success", True))
            
            return result
            
        except Exception as e:
            error_record = {
                "timestamp": start_time.isoformat(),
                "command": command,
                "error": str(e),
                "duration": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "success": False
            }
            
            self._command_history.append(error_record)
            logger.error(f"YUNG command execution failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def _parse_yung_command(self, command: str) -> Dict[str, Any]:
        """Parse a YUNG command string into structured data."""
        
        # Handle different YUNG command formats
        if command.startswith("YUNG:"):
            command = command[5:].strip()
        
        # Handle parameterized commands
        if "(" in command and command.endswith(")"):
            cmd_name = command[:command.index("(")]
            params_str = command[command.index("(")+1:-1]
            parameters = self._parse_command_parameters(params_str)
        else:
            cmd_name = command
            parameters = {}
        
        # Handle compound commands
        if " && " in cmd_name:
            commands = [c.strip() for c in cmd_name.split(" && ")]
            return {
                "type": "compound",
                "commands": commands,
                "parameters": parameters
            }
        
        # Handle conditional commands
        if " IF " in cmd_name.upper():
            parts = cmd_name.upper().split(" IF ")
            if len(parts) == 2:
                return {
                    "type": "conditional",
                    "command": parts[0].strip(),
                    "condition": parts[1].strip(),
                    "parameters": parameters
                }
        
        # Simple command
        return {
            "type": "simple",
            "command": cmd_name.strip(),
            "parameters": parameters
        }
    
    def _parse_command_parameters(self, params_str: str) -> Dict[str, Any]:
        """Parse command parameters from string."""
        params = {}
        
        # Simple key=value parsing
        for param in params_str.split(","):
            param = param.strip()
            if "=" in param:
                key, value = param.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                # Try to convert to appropriate type
                if value.lower() in ("true", "false"):
                    params[key] = value.lower() == "true"
                elif value.isdigit():
                    params[key] = int(value)
                elif self._is_float(value):
                    params[key] = float(value)
                else:
                    params[key] = value
        
        return params
    
    def _is_float(self, value: str) -> bool:
        """Check if string represents a float."""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _determine_execution_strategy(self, parsed_command: Dict[str, Any]) -> str:
        """Determine the best execution strategy for a command."""
        
        if parsed_command["type"] == "compound":
            # Compound commands use pattern execution
            return "force_pattern"
        
        if parsed_command["type"] == "conditional":
            # Conditional commands use pattern execution
            return "force_pattern"
        
        command = parsed_command.get("command", "")
        
        # Check if command maps directly to Force tool
        if command in self._command_mapping:
            return "force_tool"
        
        # Check if command maps to Force pattern
        if command in self._pattern_mapping:
            return "force_pattern"
        
        # Check if command should go through agent adapter
        if self._is_agent_command(command):
            return "agent_adapter"
        
        # Fall back to legacy execution
        return "legacy"
    
    def _is_agent_command(self, command: str) -> bool:
        """Check if command should be handled by an agent adapter."""
        agent_commands = [
            "vcma_", "vcla_", "cdia_", "rdia_", "saa_",
            "version_control", "monitor", "analyze_code", "analyze_docs", "static_analysis"
        ]
        
        return any(command.startswith(prefix) for prefix in agent_commands)
    
    async def _execute_as_force_tool(self, parsed_command: Dict[str, Any], 
                                   parameters: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command as a Force tool."""
        try:
            command = parsed_command.get("command", "")
            tool_name = self._command_mapping.get(command)
            
            if not tool_name:
                return {
                    "success": False,
                    "error": f"No Force tool mapping for command: {command}"
                }
            
            # Merge parameters from command and call
            merged_params = {**parsed_command.get("parameters", {}), **parameters}
            
            # Execute tool through Force engine
            result = await self.force_engine.tool_executor.execute_tool_command(
                {"name": tool_name}, merged_params, context
            )
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "execution_type": "force_tool"
            }
            
        except Exception as e:
            logger.error(f"Force tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_type": "force_tool"
            }
    
    async def _execute_as_force_pattern(self, parsed_command: Dict[str, Any],
                                      parameters: Dict[str, Any],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command as a Force pattern."""
        try:
            if parsed_command["type"] == "compound":
                return await self._execute_compound_command(parsed_command, parameters, context)
            
            elif parsed_command["type"] == "conditional":
                return await self._execute_conditional_command(parsed_command, parameters, context)
            
            else:
                command = parsed_command.get("command", "")
                pattern_name = self._pattern_mapping.get(command)
                
                if not pattern_name:
                    return {
                        "success": False,
                        "error": f"No Force pattern mapping for command: {command}"
                    }
                
                # Execute pattern through Force engine
                result = await self._execute_force_pattern(pattern_name, parameters, context)
                
                return {
                    "success": True,
                    "pattern": pattern_name,
                    "result": result,
                    "execution_type": "force_pattern"
                }
            
        except Exception as e:
            logger.error(f"Force pattern execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_type": "force_pattern"
            }
    
    async def _execute_through_agent_adapter(self, parsed_command: Dict[str, Any],
                                           parameters: Dict[str, Any],
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command through an agent adapter."""
        try:
            command = parsed_command.get("command", "")
            
            # Determine which agent should handle the command
            agent_type = self._determine_agent_for_command(command)
            
            if not agent_type:
                return {
                    "success": False,
                    "error": f"No agent mapping for command: {command}"
                }
            
            # Get or create agent adapter
            adapter = await self._get_agent_adapter(agent_type)
            
            if not adapter:
                return {
                    "success": False,
                    "error": f"Failed to create adapter for agent: {agent_type}"
                }
            
            # Execute through adapter
            merged_params = {**parsed_command.get("parameters", {}), **parameters}
            result = await adapter.process_command(command, {**merged_params, **context})
            
            return {
                "success": True,
                "agent_type": agent_type,
                "result": result,
                "execution_type": "agent_adapter"
            }
            
        except Exception as e:
            logger.error(f"Agent adapter execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_type": "agent_adapter"
            }
    
    async def _execute_legacy_command(self, parsed_command: Dict[str, Any],
                                    parameters: Dict[str, Any],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command through legacy YUNG system."""
        try:
            # This would integrate with the existing YUNG command processor
            # For now, return a placeholder result
            command = parsed_command.get("command", "")
            
            return {
                "success": True,
                "message": f"Legacy command executed: {command}",
                "execution_type": "legacy",
                "note": "Legacy YUNG integration not fully implemented"
            }
            
        except Exception as e:
            logger.error(f"Legacy command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_type": "legacy"
            }
    
    async def _execute_compound_command(self, parsed_command: Dict[str, Any],
                                      parameters: Dict[str, Any],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a compound command (multiple commands chained)."""
        commands = parsed_command.get("commands", [])
        results = []
        
        for cmd in commands:
            # Parse each sub-command
            sub_parsed = self._parse_yung_command(cmd)
            
            # Execute sub-command
            result = await self.process_yung_command(cmd, parameters, context)
            results.append(result)
            
            # If any command fails, stop execution
            if not result.get("success", True):
                break
            
            # Update context with results for next command
            if result.get("result"):
                context.update(result.get("result", {}))
        
        return {
            "success": all(r.get("success", True) for r in results),
            "results": results,
            "execution_type": "compound"
        }
    
    async def _execute_conditional_command(self, parsed_command: Dict[str, Any],
                                         parameters: Dict[str, Any],
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a conditional command."""
        command = parsed_command.get("command", "")
        condition = parsed_command.get("condition", "")
        
        # Evaluate condition
        condition_result = self._evaluate_yung_condition(condition, context)
        
        if condition_result:
            # Execute the command
            result = await self.process_yung_command(command, parameters, context)
            return {
                "success": result.get("success", True),
                "condition_met": True,
                "result": result,
                "execution_type": "conditional"
            }
        else:
            return {
                "success": True,
                "condition_met": False,
                "message": "Condition not met, command skipped",
                "execution_type": "conditional"
            }
    
    def _evaluate_yung_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a YUNG condition string."""
        try:
            # Simple condition evaluation
            # Format: "variable operator value"
            
            condition = condition.strip()
            
            # Handle equality
            if " == " in condition:
                left, right = condition.split(" == ", 1)
                left_val = context.get(left.strip())
                right_val = right.strip().strip('"\'')
                return str(left_val) == right_val
            
            # Handle existence
            if condition.startswith("EXISTS "):
                var_name = condition[7:].strip()
                return var_name in context
            
            # Handle file existence
            if condition.startswith("FILE_EXISTS "):
                file_path = condition[12:].strip().strip('"\'')
                return os.path.exists(file_path)
            
            return False
            
        except Exception:
            return False
    
    def _determine_agent_for_command(self, command: str) -> Optional[str]:
        """Determine which agent should handle a command."""
        
        agent_patterns = {
            "VersionControlMasterAgent": [
                "vcma_", "git_", "version_control", "commit", "branch", "merge"
            ],
            "VersionControlListenerAgent": [
                "vcla_", "monitor", "watch", "listen"
            ],
            "CodeDocumentationInspectorAgent": [
                "cdia_", "analyze_code", "code_docs", "docstring"
            ],
            "ReadmeDocumentationInspectorAgent": [
                "rdia_", "readme", "analyze_docs", "documentation"
            ],
            "StaticAnalysisAgent": [
                "saa_", "static_analysis", "code_quality", "lint", "security"
            ]
        }
        
        for agent_type, patterns in agent_patterns.items():
            if any(pattern in command.lower() for pattern in patterns):
                return agent_type
        
        return None
    
    async def _get_agent_adapter(self, agent_type: str) -> Optional[LegacyAgentAdapter]:
        """Get or create an agent adapter."""
        if agent_type in self._agent_adapters:
            return self._agent_adapters[agent_type]
        
        try:
            # Try to import and create the actual agent
            try:
                if agent_type == "VersionControlMasterAgent":
                    from agents.vcma.vcma_agent import VersionControlMasterAgent
                    agent = VersionControlMasterAgent(agent_id="vcma_force")
                elif agent_type == "VersionControlListenerAgent":
                    from agents.vcla.vcla_agent import VersionControlListenerAgent
                    agent = VersionControlListenerAgent(agent_id="vcla_force")
                elif agent_type == "CodeDocumentationInspectorAgent":
                    from agents.cdia.cdia_agent import CodeDocumentationInspectorAgent
                    agent = CodeDocumentationInspectorAgent(agent_id="cdia_force")
                elif agent_type == "ReadmeDocumentationInspectorAgent":
                    from agents.rdia.rdia_agent import READMEInspectorAgent
                    agent = READMEInspectorAgent(agent_id="rdia_force")
                elif agent_type == "StaticAnalysisAgent":
                    from agents.saa.saa_agent import StaticAnalysisAgent
                    agent = StaticAnalysisAgent(agent_id="saa_force")
                else:
                    # Create a mock agent as fallback
                    from core.agent import BaseAgent
                    agent = BaseAgent(agent_id=agent_type.lower())
                    
            except ImportError:
                # If actual agents can't be imported, create a mock BaseAgent
                from core.agent import BaseAgent
                agent = BaseAgent(agent_id=agent_type.lower())
            
            adapter = create_force_adapter(agent, self.force_engine)
            self._agent_adapters[agent_type] = adapter
            
            return adapter
            
        except Exception as e:
            logger.error(f"Failed to create agent adapter: {e}")
            return None
    
    async def _execute_force_pattern(self, pattern_name: str, parameters: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Force pattern."""
        # This would integrate with the Force pattern execution system
        # For now, return a placeholder result
        
        return {
            "success": True,
            "pattern": pattern_name,
            "message": f"Force pattern executed: {pattern_name}",
            "parameters": parameters,
            "context": context
        }
    
    def _update_execution_stats(self, strategy: str, success: bool):
        """Update execution statistics."""
        if strategy not in self._execution_stats:
            self._execution_stats[strategy] = {
                "total": 0,
                "successful": 0,
                "failed": 0
            }
        
        self._execution_stats[strategy]["total"] += 1
        
        if success:
            self._execution_stats[strategy]["successful"] += 1
        else:
            self._execution_stats[strategy]["failed"] += 1
    
    def get_command_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get command execution history."""
        if limit:
            return self._command_history[-limit:]
        return self._command_history
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "strategies": self._execution_stats,
            "total_commands": len(self._command_history),
            "success_rate": self._calculate_overall_success_rate()
        }
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self._command_history:
            return 0.0
        
        successful = sum(1 for record in self._command_history if record.get("success"))
        return successful / len(self._command_history)
    
    def get_command_mappings(self) -> Dict[str, Any]:
        """Get current command mappings."""
        return {
            "tool_mappings": self._command_mapping,
            "pattern_mappings": self._pattern_mapping
        }
    
    def add_command_mapping(self, command: str, tool_or_pattern: str, mapping_type: str = "tool"):
        """Add a new command mapping."""
        if mapping_type == "tool":
            self._command_mapping[command] = tool_or_pattern
        elif mapping_type == "pattern":
            self._pattern_mapping[command] = tool_or_pattern
        else:
            raise ValueError(f"Invalid mapping type: {mapping_type}")
        
        logger.info(f"Added {mapping_type} mapping: {command} -> {tool_or_pattern}")


# Convenience functions for integration

async def process_yung_command(command: str, parameters: Optional[Dict[str, Any]] = None,
                             context: Optional[Dict[str, Any]] = None,
                             force_engine: Optional[ForceEngine] = None) -> Dict[str, Any]:
    """
    Process a YUNG command with Force integration.
    
    Args:
        command: YUNG command string
        parameters: Command parameters
        context: Execution context
        force_engine: Optional Force engine instance
        
    Returns:
        Command execution result
    """
    integration = YUNGForceIntegration(force_engine)
    return await integration.process_yung_command(command, parameters, context)


def create_yung_force_integration(force_engine: Optional[ForceEngine] = None) -> YUNGForceIntegration:
    """
    Create a YUNG-Force integration instance.
    
    Args:
        force_engine: Optional Force engine instance
        
    Returns:
        YUNGForceIntegration instance
    """
    return YUNGForceIntegration(force_engine)
