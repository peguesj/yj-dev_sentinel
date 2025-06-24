"""
Legacy Agent Adapter Layer for Force Integration.

This module provides compatibility adapters that allow existing Dev Sentinel agents
(VCMA, VCLA, RDIA, CDIA, SAA) to work with the new Force system while maintaining
backward compatibility and adding Force capabilities.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Type, Callable
from datetime import datetime, timezone
from pathlib import Path

from core.agent import BaseAgent
from . import ForceEngine, ForceEngineError

logger = logging.getLogger(__name__)

class LegacyAgentManager:
    """
    Manager for all legacy agents with Force integration.
    
    Provides a unified interface to discover, initialize, and interact
    with legacy agents while enabling Force tool and pattern integration.
    """
    
    def __init__(self, force_engine=None):
        """Initialize the legacy agent manager."""
        from . import ForceEngine
        
        self.force_engine = force_engine or ForceEngine()
        self._agents: Dict[str, LegacyAgentAdapter] = {}
        self._agent_classes = {
            'VCMA': 'agents.vcma.vcma_agent.VersionControlMasterAgent',
            'VCLA': 'agents.vcla.vcla_agent.VersionControlListenerAgent', 
            'RDIA': 'agents.rdia.rdia_agent.READMEInspectorAgent',
            'CDIA': 'agents.cdia.cdia_agent.CodeDocumentationInspectorAgent',
            'SAA': 'agents.saa.saa_agent.StaticAnalysisAgent',
        }
        
        logger.info("Legacy agent manager initialized")
        
    def get_available_agents(self) -> Dict[str, str]:
        """Get available legacy agent types."""
        return {
            'VCMA': 'Version Control Master Agent',
            'VCLA': 'Version Control Listener Agent',
            'RDIA': 'README Documentation Inspector Agent', 
            'CDIA': 'Code Documentation Inspector Agent',
            'SAA': 'Static Analysis Agent',
        }
        
    def get_agent_adapter(self, agent_type: str) -> Optional['LegacyAgentAdapter']:
        """Get or create a legacy agent adapter."""
        if agent_type not in self._agent_classes:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
            
        if agent_type not in self._agents:
            try:
                # Dynamically import and instantiate the agent
                module_path, class_name = self._agent_classes[agent_type].rsplit('.', 1)
                import importlib
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                
                # Create agent instance
                agent_instance = agent_class()
                
                # Create adapter
                adapter = LegacyAgentAdapter(agent_instance, self.force_engine)
                self._agents[agent_type] = adapter
                
                logger.info(f"Created adapter for {agent_type}")
                
            except Exception as e:
                logger.error(f"Failed to create adapter for {agent_type}: {e}")
                return None
                
        return self._agents[agent_type]
        
    async def execute_agent_command(self, agent_type: str, command: str, 
                                  parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command on a legacy agent."""
        adapter = self.get_agent_adapter(agent_type)
        if not adapter:
            return {
                "status": "error",
                "error": f"Agent {agent_type} not available",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        return await adapter.process_command(command, parameters)
        
    def list_agent_capabilities(self, agent_type: str) -> List[str]:
        """List capabilities of a specific agent type.""" 
        adapter = self.get_agent_adapter(agent_type)
        if not adapter:
            return []
            
        # Return basic capabilities for now
        return ["analyze", "inspect", "monitor", "status", "health"]


class LegacyAgentAdapter:
    """
    Base adapter class for integrating legacy agents with Force system.
    
    Provides:
    - Force tool execution capabilities
    - Pattern-based workflow automation
    - Constraint validation
    - Learning data collection
    - Legacy method compatibility
    """
    
    def __init__(self, agent: BaseAgent, force_engine: Optional[ForceEngine] = None):
        """
        Initialize the legacy adapter.
        
        Args:
            agent: The legacy agent to adapt
            force_engine: Optional Force engine instance
        """
        self.agent = agent
        self.agent_type = type(agent).__name__
        self.force_engine = force_engine or ForceEngine()
        
        # Capability mapping
        self._capability_mapping = {}
        self._tool_mapping = {}
        self._pattern_mapping = {}
        
        # Performance tracking
        self._execution_history = []
        self._learning_data = []
        
        # Initialize mappings
        self._initialize_mappings()
        
    def _initialize_mappings(self):
        """Initialize capability, tool, and pattern mappings for the agent."""
        # Base mappings that all agents support
        self._capability_mapping = {
            "status": "get_agent_status",
            "health": "health_check",
            "capabilities": "get_capabilities",
            "initialize": "initialize_agent",
        }
        
        # Tool mappings (will be extended by specific adapters)
        self._tool_mapping: Dict[str, Union[str, List[str]]] = {
            "git-status": ["git", "status"],
            "git-log": ["git", "log"],
            "file-read": ["filesystem", "read"],
            "file-write": ["filesystem", "write"],
        }
        
        # Pattern mappings (will be extended by specific adapters)
        self._pattern_mapping = {
            "analyze": "analysis-workflow",
            "inspect": "inspection-workflow",
            "monitor": "monitoring-workflow",
        }
    
    async def execute_force_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Force tool through the adapter.
        
        Args:
            tool_name: Name of the Force tool to execute
            parameters: Tool execution parameters
            
        Returns:
            Execution result with metadata
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Load tool definition
            tool_def = await self._load_tool_definition(tool_name)
            if not tool_def:
                raise ForceEngineError(f"Tool not found: {tool_name}")
            
            # Validate parameters against tool schema
            await self._validate_tool_parameters(tool_def, parameters)
            
            # Execute through Force engine
            result = await self.force_engine.tool_executor.execute_tool_command(
                tool_def, parameters, context={"adapter": self.agent_type}
            )
            
            # Record execution for learning
            execution_record = {
                "timestamp": start_time.isoformat(),
                "tool": tool_name,
                "parameters": parameters,
                "result": result,
                "agent_type": self.agent_type,
                "duration": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "success": result.get("success", True)
            }
            
            self._execution_history.append(execution_record)
            self._learning_data.append(execution_record)
            
            return result
            
        except Exception as e:
            error_record = {
                "timestamp": start_time.isoformat(),
                "tool": tool_name,
                "parameters": parameters,
                "error": str(e),
                "agent_type": self.agent_type,
                "duration": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "success": False
            }
            
            self._execution_history.append(error_record)
            logger.error(f"Force tool execution failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def apply_pattern(self, pattern_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a Force pattern through the adapter.
        
        Args:
            pattern_name: Name of the pattern to apply
            context: Pattern execution context
            
        Returns:
            Pattern application result
        """
        try:
            # Load pattern definition
            pattern_def = await self._load_pattern_definition(pattern_name)
            if not pattern_def:
                raise ForceEngineError(f"Pattern not found: {pattern_name}")
            
            # Execute pattern steps
            results = []
            for step in pattern_def.get("steps", []):
                step_result = await self._execute_pattern_step(step, context)
                results.append(step_result)
                
                # Update context with step results
                if step_result.get("success"):
                    context.update(step_result.get("output", {}))
            
            return {
                "success": True,
                "pattern": pattern_name,
                "steps": results,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Pattern application failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pattern": pattern_name
            }
    
    async def validate_constraints(self, operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate operation against Force constraints.
        
        Args:
            operation: Operation to validate
            context: Operation context
            
        Returns:
            Validation result
        """
        try:
            # Load applicable constraints
            constraints = await self._load_applicable_constraints(operation)
            
            violations = []
            warnings = []
            
            for constraint in constraints:
                result = await self._validate_constraint(constraint, operation, context)
                
                if result.get("violation"):
                    violations.append(result)
                elif result.get("warning"):
                    warnings.append(result)
            
            return {
                "valid": len(violations) == 0,
                "violations": violations,
                "warnings": warnings,
                "operation": operation
            }
            
        except Exception as e:
            logger.error(f"Constraint validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "operation": operation
            }
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a command through the adapter with Force capabilities.
        
        Args:
            command: Command to process
            context: Command context
            
        Returns:
            Command execution result
        """
        context = context or {}
        
        try:
            # Check if this is a Force-enhanced command
            if command.startswith("force:"):
                return await self._process_force_command(command[6:], context)
            
            # Check if command maps to a Force tool
            if command in self._tool_mapping:
                tool_name = self._tool_mapping[command]
                if isinstance(tool_name, list):
                    tool_name = "-".join(tool_name)
                return await self.execute_force_tool(tool_name, context)
            
            # Check if command maps to a Force pattern
            if command in self._pattern_mapping:
                pattern_name = self._pattern_mapping[command]
                return await self.apply_pattern(pattern_name, context)
            
            # Fall back to legacy agent method
            return await self._call_legacy_method(command, context)
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    async def get_enhanced_capabilities(self) -> Dict[str, Any]:
        """
        Get the enhanced capabilities provided by Force integration.
        
        Returns:
            Capabilities dictionary
        """
        try:
            # Get base agent capabilities
            base_capabilities = []
            if hasattr(self.agent, 'get_capabilities'):
                base_capabilities = await self._safe_call_agent_method('get_capabilities') or []
            
            # Load available Force tools
            force_tools = await self._get_available_force_tools()
            
            # Load available patterns
            force_patterns = await self._get_available_patterns()
            
            return {
                "agent_type": self.agent_type,
                "legacy_capabilities": base_capabilities,
                "force_tools": force_tools,
                "force_patterns": force_patterns,
                "enhanced_features": [
                    "schema_validation",
                    "pattern_automation",
                    "constraint_enforcement",
                    "learning_analytics",
                    "governance_policies"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get capabilities: {e}")
            return {
                "agent_type": self.agent_type,
                "error": str(e)
            }
    
    async def collect_learning_data(self) -> Dict[str, Any]:
        """
        Collect learning data for Force analytics.
        
        Returns:
            Learning data summary
        """
        try:
            return {
                "agent_type": self.agent_type,
                "execution_count": len(self._execution_history),
                "success_rate": self._calculate_success_rate(),
                "popular_tools": self._get_popular_tools(),
                "performance_metrics": self._get_performance_metrics(),
                "learning_records": self._learning_data[-100:],  # Last 100 records
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to collect learning data: {e}")
            return {
                "agent_type": self.agent_type,
                "error": str(e)
            }
    
    # Helper methods
    
    async def _load_tool_definition(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Load a Force tool definition."""
        try:
            tool_files = list(self.force_engine.tools_dir.glob("*.json"))
            
            for tool_file in tool_files:
                with open(tool_file, 'r') as f:
                    tools_data = json.load(f)
                    
                for tool in tools_data.get("tools", []):
                    if tool.get("name") == tool_name:
                        return tool
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load tool definition: {e}")
            return None
    
    async def _load_pattern_definition(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Load a Force pattern definition."""
        try:
            pattern_files = list(self.force_engine.patterns_dir.glob("*.json"))
            
            for pattern_file in pattern_files:
                with open(pattern_file, 'r') as f:
                    patterns_data = json.load(f)
                    
                for pattern in patterns_data.get("patterns", []):
                    if pattern.get("name") == pattern_name:
                        return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load pattern definition: {e}")
            return None
    
    async def _validate_tool_parameters(self, tool_def: Dict[str, Any], parameters: Dict[str, Any]):
        """Validate tool parameters against schema."""
        # Basic validation - can be enhanced with full JSON schema validation
        required_params = tool_def.get("parameters", {}).get("required", [])
        
        for param in required_params:
            if param not in parameters:
                raise ForceEngineError(f"Missing required parameter: {param}")
    
    async def _execute_pattern_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single pattern step."""
        step_type = step.get("type")
        
        if step_type == "tool":
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})
            
            # Substitute context variables in parameters
            resolved_params = self._resolve_context_variables(parameters, context)
            
            if tool_name:
                return await self.execute_force_tool(tool_name, resolved_params)
            else:
                return {
                    "success": False,
                    "error": "Tool name not specified in step"
                }
        
        elif step_type == "condition":
            # Evaluate condition
            condition = step.get("condition")
            if condition:
                result = self._evaluate_condition(condition, context)
                
                return {
                    "success": True,
                    "condition_result": result,
                    "output": {"condition_met": result}
                }
            else:
                return {
                    "success": False,
                    "error": "No condition specified in step"
                }
        
        else:
            return {
                "success": False,
                "error": f"Unknown step type: {step_type}"
            }
    
    async def _load_applicable_constraints(self, operation: str) -> List[Dict[str, Any]]:
        """Load constraints applicable to an operation."""
        try:
            constraints = []
            constraint_files = list(self.force_engine.constraints_dir.glob("*.json"))
            
            for constraint_file in constraint_files:
                with open(constraint_file, 'r') as f:
                    constraints_data = json.load(f)
                    
                for constraint in constraints_data.get("constraints", []):
                    if self._constraint_applies_to_operation(constraint, operation):
                        constraints.append(constraint)
            
            return constraints
            
        except Exception as e:
            logger.error(f"Failed to load constraints: {e}")
            return []
    
    async def _validate_constraint(self, constraint: Dict[str, Any], operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific constraint."""
        try:
            constraint_type = constraint.get("type")
            condition = constraint.get("condition")
            
            if condition and self._evaluate_condition(condition, context):
                return {
                    "violation": True,
                    "constraint": constraint.get("name"),
                    "message": constraint.get("message"),
                    "severity": constraint.get("severity", "error")
                }
            
            return {"violation": False}
            
        except Exception as e:
            return {
                "violation": True,
                "error": str(e),
                "constraint": constraint.get("name", "unknown")
            }
    
    async def _process_force_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a Force-specific command."""
        parts = command.split(":")
        
        if len(parts) >= 2:
            command_type = parts[0]
            command_name = parts[1]
            
            if command_type == "tool":
                return await self.execute_force_tool(command_name, context)
            elif command_type == "pattern":
                return await self.apply_pattern(command_name, context)
            elif command_type == "validate":
                return await self.validate_constraints(command_name, context)
        
        return {
            "success": False,
            "error": f"Invalid Force command format: {command}"
        }
    
    async def _call_legacy_method(self, method_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call a legacy agent method safely."""
        try:
            # Check capability mapping
            actual_method = self._capability_mapping.get(method_name, method_name)
            
            result = await self._safe_call_agent_method(actual_method, **context)
            
            return {
                "success": True,
                "result": result,
                "method": actual_method
            }
            
        except Exception as e:
            logger.error(f"Legacy method call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": method_name
            }
    
    async def _safe_call_agent_method(self, method_name: str, *args, **kwargs) -> Any:
        """Safely call an agent method if it exists."""
        if hasattr(self.agent, method_name):
            method = getattr(self.agent, method_name)
            if asyncio.iscoroutinefunction(method):
                return await method(*args, **kwargs)
            else:
                return method(*args, **kwargs)
        return None
    
    async def _get_available_force_tools(self) -> List[str]:
        """Get list of available Force tools."""
        try:
            tools = []
            tool_files = list(self.force_engine.tools_dir.glob("*.json"))
            
            for tool_file in tool_files:
                with open(tool_file, 'r') as f:
                    tools_data = json.load(f)
                    
                for tool in tools_data.get("tools", []):
                    tools.append(tool.get("name"))
            
            return tools
            
        except Exception as e:
            logger.error(f"Failed to get Force tools: {e}")
            return []
    
    async def _get_available_patterns(self) -> List[str]:
        """Get list of available Force patterns."""
        try:
            patterns = []
            pattern_files = list(self.force_engine.patterns_dir.glob("*.json"))
            
            for pattern_file in pattern_files:
                with open(pattern_file, 'r') as f:
                    patterns_data = json.load(f)
                    
                for pattern in patterns_data.get("patterns", []):
                    patterns.append(pattern.get("name"))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get Force patterns: {e}")
            return []
    
    def _resolve_context_variables(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve context variables in parameters."""
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                resolved[key] = context.get(var_name, value)
            else:
                resolved[key] = value
        
        return resolved
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition against context."""
        try:
            condition_type = condition.get("type")
            
            if condition_type == "equals":
                field = condition.get("field")
                value = condition.get("value")
                if field:
                    return context.get(field) == value
                return False
            
            elif condition_type == "exists":
                field = condition.get("field")
                if field:
                    return field in context
                return False
            
            elif condition_type == "greater_than":
                field = condition.get("field")
                value = condition.get("value")
                if field and isinstance(value, (int, float)):
                    field_value = context.get(field, 0)
                    if isinstance(field_value, (int, float)):
                        return field_value > value
                return False
            
            return False
            
        except Exception:
            return False
    
    def _constraint_applies_to_operation(self, constraint: Dict[str, Any], operation: str) -> bool:
        """Check if a constraint applies to an operation."""
        applicable_operations = constraint.get("applies_to", [])
        return operation in applicable_operations or "all" in applicable_operations
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate from execution history."""
        if not self._execution_history:
            return 0.0
        
        successes = sum(1 for record in self._execution_history if record.get("success"))
        return successes / len(self._execution_history)
    
    def _get_popular_tools(self) -> List[Dict[str, Any]]:
        """Get most popular tools from execution history."""
        tool_counts = {}
        
        for record in self._execution_history:
            tool = record.get("tool")
            if tool:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        # Sort by usage count
        popular = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"tool": tool, "usage_count": count} for tool, count in popular[:10]]
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from execution history."""
        if not self._execution_history:
            return {}
        
        durations = [record.get("duration", 0) for record in self._execution_history]
        
        return {
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_executions": len(self._execution_history)
        }


class VCMAForceAdapter(LegacyAgentAdapter):
    """Force adapter for Version Control Master Agent."""
    
    def _initialize_mappings(self):
        """Initialize VCMA-specific mappings."""
        super()._initialize_mappings()
        
        # VCMA-specific capabilities
        self._capability_mapping.update({
            "analyze_commits": "analyze_repository_commits",
            "repo_status": "get_repository_status",
            "refresh_repo": "refresh_repository_state",
            "manage_branches": "manage_git_branches",
            "merge_analysis": "analyze_merge_conflicts"
        })
        
        # VCMA-specific tool mappings
        self._tool_mapping.update({
            "analyze_commits": "git-commit-analysis",
            "repo_status": "git-status", 
            "refresh_repo": "git-refresh",
            "branch_management": "git-branch-ops",
            "merge_analysis": "git-merge-analysis"
        })
        
        # VCMA-specific pattern mappings
        self._pattern_mapping.update({
            "analyze": "git-analysis-workflow",
            "commit_workflow": "commit-validation-workflow",
            "branch_workflow": "branch-management-workflow"
        })


class VCLAForceAdapter(LegacyAgentAdapter):
    """Force adapter for Version Control Listener Agent."""
    
    def _initialize_mappings(self):
        """Initialize VCLA-specific mappings."""
        super()._initialize_mappings()
        
        # VCLA-specific capabilities
        self._capability_mapping.update({
            "start_monitoring": "start_repository_monitoring",
            "stop_monitoring": "stop_repository_monitoring",
            "get_changes": "get_repository_changes",
            "monitor_status": "get_monitoring_status"
        })
        
        # VCLA-specific tool mappings
        self._tool_mapping.update({
            "start_monitoring": "git-monitor-start",
            "stop_monitoring": "git-monitor-stop", 
            "get_changes": "git-changes",
            "monitor_status": "git-monitor-status"
        })
        
        # VCLA-specific pattern mappings
        self._pattern_mapping.update({
            "monitor": "repository-monitoring-workflow",
            "change_detection": "change-detection-workflow"
        })


class CDIAForceAdapter(LegacyAgentAdapter):
    """Force adapter for Code Documentation Inspector Agent."""
    
    def _initialize_mappings(self):
        """Initialize CDIA-specific mappings."""
        super()._initialize_mappings()
        
        # CDIA-specific capabilities
        self._capability_mapping.update({
            "analyze_code_docs": "analyze_code_documentation",
            "extract_docstrings": "extract_code_docstrings",
            "validate_docs": "validate_documentation_standards",
            "generate_docs": "generate_missing_documentation"
        })
        
        # CDIA-specific tool mappings  
        self._tool_mapping.update({
            "analyze_code_docs": "docs-code-analysis",
            "extract_docstrings": "docs-extraction",
            "validate_docs": "docs-validation",
            "generate_docs": "docs-generation"
        })
        
        # CDIA-specific pattern mappings
        self._pattern_mapping.update({
            "analyze": "documentation-analysis-workflow",
            "inspect": "code-documentation-inspection",
            "validate": "documentation-validation-workflow"
        })


class RDIAForceAdapter(LegacyAgentAdapter):
    """Force adapter for README Documentation Inspector Agent."""
    
    def _initialize_mappings(self):
        """Initialize RDIA-specific mappings."""
        super()._initialize_mappings()
        
        # RDIA-specific capabilities
        self._capability_mapping.update({
            "analyze_readme": "analyze_readme_documentation",
            "validate_structure": "validate_readme_structure",
            "check_completeness": "check_documentation_completeness",
            "suggest_improvements": "suggest_readme_improvements"
        })
        
        # RDIA-specific tool mappings
        self._tool_mapping.update({
            "analyze_readme": "readme-analysis",
            "validate_structure": "readme-validation", 
            "check_completeness": "docs-completeness-check",
            "suggest_improvements": "docs-improvement-suggestions"
        })
        
        # RDIA-specific pattern mappings
        self._pattern_mapping.update({
            "analyze": "readme-analysis-workflow",
            "inspect": "readme-inspection-workflow",
            "validate": "readme-validation-workflow"
        })


class SAAForceAdapter(LegacyAgentAdapter):
    """Force adapter for Static Analysis Agent."""
    
    def _initialize_mappings(self):
        """Initialize SAA-specific mappings."""
        super()._initialize_mappings()
        
        # SAA-specific capabilities
        self._capability_mapping.update({
            "analyze_code": "perform_static_analysis",
            "check_quality": "check_code_quality",
            "detect_issues": "detect_code_issues",
            "security_scan": "perform_security_scan"
        })
        
        # SAA-specific tool mappings
        self._tool_mapping.update({
            "analyze_code": "static-analysis",
            "check_quality": "code-quality-check",
            "detect_issues": "issue-detection", 
            "security_scan": "security-analysis"
        })
        
        # SAA-specific pattern mappings
        self._pattern_mapping.update({
            "analyze": "static-analysis-workflow",
            "quality_check": "code-quality-workflow",
            "security_scan": "security-analysis-workflow"
        })


# Factory function for creating appropriate adapters
def create_force_adapter(agent: BaseAgent, force_engine: Optional[ForceEngine] = None) -> LegacyAgentAdapter:
    """
    Create the appropriate Force adapter for a legacy agent.
    
    Args:
        agent: The legacy agent to adapt
        force_engine: Optional Force engine instance
        
    Returns:
        Appropriate Force adapter instance
    """
    agent_type = type(agent).__name__
    
    adapter_mapping = {
        "VersionControlMasterAgent": VCMAForceAdapter,
        "VersionControlListenerAgent": VCLAForceAdapter,
        "CodeDocumentationInspectorAgent": CDIAForceAdapter,
        "READMEInspectorAgent": RDIAForceAdapter,
        "StaticAnalysisAgent": SAAForceAdapter,
    }
    
    adapter_class = adapter_mapping.get(agent_type, LegacyAgentAdapter)
    return adapter_class(agent, force_engine)
