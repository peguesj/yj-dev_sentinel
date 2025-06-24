"""
Specialized adapters for specific Dev Sentinel agent types.

This module provides specialized MCP and fast-agent adapters for each type of
Dev Sentinel agent, offering tailored interfaces that expose agent-specific
capabilities and commands.
"""
from typing import List, Optional, Dict, Any, Type
import asyncio
import logging

from integration.fast_agent.adapter import BaseAgentAdapter, MCPAgentAdapter
from core.agent import BaseAgent

# Import agent types
try:
    from agents.vcma.vcma_agent import VersionControlMasterAgent
    from agents.vcla.vcla_agent import VersionControlListenerAgent
    from agents.cdia.cdia_agent import CodeDocumentationInspectorAgent
    from agents.rdia.rdia_agent import ReadmeInspectorAgent as ReadmeDocumentationInspectorAgent
    from agents.saa.saa_agent import StaticAnalysisAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some agent types not available: {e}")
    AGENTS_AVAILABLE = False
    # Create stub classes for development
    class VersionControlMasterAgent: pass
    class VersionControlListenerAgent: pass
    class CodeDocumentationInspectorAgent: pass
    class ReadmeDocumentationInspectorAgent: pass
    class StaticAnalysisAgent: pass

logger = logging.getLogger(__name__)

# Registry for mapping agent types to their specialized adapters
ADAPTER_REGISTRY: Dict[Type, Type[BaseAgentAdapter]] = {}

def register_adapter(agent_cls: Type, adapter_cls: Type[BaseAgentAdapter]):
    """
    Register an adapter class for a specific agent type.
    
    Args:
        agent_cls: The agent class to register an adapter for
        adapter_cls: The adapter class to use for the agent
    """
    ADAPTER_REGISTRY[agent_cls] = adapter_cls
    logger.debug(f"Registered adapter {adapter_cls.__name__} for {agent_cls.__name__}")

async def create_specialized_adapter(agent: BaseAgent, adapter_type: str = "mcp") -> BaseAgentAdapter:
    """
    Create a specialized adapter for the given agent based on its type.
    
    Args:
        agent: The agent to create an adapter for
        adapter_type: Type of adapter to create ("mcp" or "base")
        
    Returns:
        A specialized adapter for the agent
    """
    agent_type = type(agent)
    
    # Get the appropriate adapter class
    adapter_cls = ADAPTER_REGISTRY.get(agent_type)
    
    if adapter_cls:
        adapter = adapter_cls(agent)
    else:
        # Use the appropriate base adapter
        if adapter_type == "mcp":
            adapter = MCPAgentAdapter(agent)
        else:
            adapter = BaseAgentAdapter(agent)
    
    await adapter.initialize()
    return adapter

class VCMAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for Version Control Master Agent."""
    
    def __init__(self, agent: VersionControlMasterAgent):
        """Initialize the VCMA adapter."""
        super().__init__(
            agent=agent,
            name="vcma_adapter",
            description="Version Control Master Agent - proactively manages version control operations"
        )
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process VCMA-specific commands."""
        try:
            context = context or {}
            
            # Handle VCMA-specific commands
            if command.lower() in ["status", "repo_status"]:
                return await self._get_repo_status()
            elif command.lower() in ["analyze_commits", "analyze"]:
                return await self._analyze_commits(context)
            elif command.lower() in ["refresh_repo", "refresh"]:
                return await self._refresh_repo()
            else:
                # Fall back to base command processing
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _get_repo_status(self) -> Dict[str, Any]:
        """Get repository status from VCMA."""
        if hasattr(self.agent, 'get_repo_status'):
            status = await self.agent.get_repo_status()
            return {"status": "success", "repo_status": status}
        else:
            return {"status": "error", "message": "Repository status not available"}
    
    async def _analyze_commits(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commits using VCMA."""
        if hasattr(self.agent, 'analyze_commits'):
            result = await self.agent.analyze_commits(context)
            return {"status": "success", "analysis": result}
        else:
            return {"status": "error", "message": "Commit analysis not available"}
    
    async def _refresh_repo(self) -> Dict[str, Any]:
        """Refresh repository state."""
        if hasattr(self.agent, '_refresh_repo_state'):
            await self.agent._refresh_repo_state()
            return {"status": "success", "message": "Repository state refreshed"}
        else:
            return {"status": "error", "message": "Repository refresh not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get VCMA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        vcma_commands = ["status", "repo_status", "analyze_commits", "analyze", "refresh_repo", "refresh"]
        return base_commands + vcma_commands

class VCLAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for Version Control Listener Agent."""
    
    def __init__(self, agent: VersionControlListenerAgent):
        """Initialize the VCLA adapter."""
        super().__init__(
            agent=agent,
            name="vcla_adapter", 
            description="Version Control Listener Agent - monitors specific repository aspects"
        )
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process VCLA-specific commands."""
        try:
            context = context or {}
            
            if command.lower() in ["monitor_path", "monitor"]:
                path = context.get("path")
                return await self._monitor_path(path)
            elif command.lower() in ["detect_changes", "changes"]:
                return await self._detect_changes(context)
            else:
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _monitor_path(self, path: Optional[str]) -> Dict[str, Any]:
        """Monitor a specific path."""
        if not path:
            return {"status": "error", "message": "Path required for monitoring"}
        
        if hasattr(self.agent, 'add_monitored_path'):
            self.agent.add_monitored_path(path)
            return {"status": "success", "message": f"Monitoring path: {path}"}
        else:
            return {"status": "error", "message": "Path monitoring not available"}
    
    async def _detect_changes(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes in monitored paths."""
        if hasattr(self.agent, 'detect_changes'):
            changes = await self.agent.detect_changes()
            return {"status": "success", "changes": changes}
        else:
            return {"status": "error", "message": "Change detection not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get VCLA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        vcla_commands = ["monitor_path", "monitor", "detect_changes", "changes"]
        return base_commands + vcla_commands

class CDIAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for Code Documentation Inspector Agent."""
    
    def __init__(self, agent: CodeDocumentationInspectorAgent):
        """Initialize the CDIA adapter."""
        super().__init__(
            agent=agent,
            name="cdia_adapter",
            description="Code Documentation Inspector Agent - analyzes code documentation quality"
        )
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process CDIA-specific commands."""
        try:
            context = context or {}
            
            if command.lower() in ["inspect_code", "inspect"]:
                files = context.get("files", [])
                return await self._inspect_code(files)
            elif command.lower() in ["analyze_documentation", "analyze_docs"]:
                return await self._analyze_documentation(context)
            else:
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _inspect_code(self, files: List[str]) -> Dict[str, Any]:
        """Inspect code documentation."""
        if hasattr(self.agent, 'inspect_files'):
            result = await self.agent.inspect_files(files)
            return {"status": "success", "inspection": result}
        else:
            return {"status": "error", "message": "Code inspection not available"}
    
    async def _analyze_documentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documentation coverage and quality."""
        if hasattr(self.agent, 'analyze_documentation'):
            result = await self.agent.analyze_documentation(context)
            return {"status": "success", "analysis": result}
        else:
            return {"status": "error", "message": "Documentation analysis not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get CDIA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        cdia_commands = ["inspect_code", "inspect", "analyze_documentation", "analyze_docs"]
        return base_commands + cdia_commands

class RDIAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for README Inspector Agent."""
    
    def __init__(self, agent: ReadmeDocumentationInspectorAgent):
        """Initialize the RDIA adapter."""
        super().__init__(
            agent=agent,
            name="rdia_adapter",
            description="README Inspector Agent - validates and improves README files"
        )
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process RDIA-specific commands."""
        try:
            context = context or {}
            
            if command.lower() in ["inspect_readme", "inspect"]:
                file_path = context.get("file_path", "README.md")
                return await self._inspect_readme(file_path)
            elif command.lower() in ["validate_structure", "validate"]:
                return await self._validate_structure(context)
            else:
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _inspect_readme(self, file_path: str) -> Dict[str, Any]:
        """Inspect README file."""
        if hasattr(self.agent, 'inspect_readme'):
            result = await self.agent.inspect_readme(file_path)
            return {"status": "success", "inspection": result}
        else:
            return {"status": "error", "message": "README inspection not available"}
    
    async def _validate_structure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate README structure."""
        if hasattr(self.agent, 'validate_structure'):
            result = await self.agent.validate_structure(context)
            return {"status": "success", "validation": result}
        else:
            return {"status": "error", "message": "Structure validation not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get RDIA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        rdia_commands = ["inspect_readme", "inspect", "validate_structure", "validate"]
        return base_commands + rdia_commands

class SAAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for Static Analysis Agent."""
    
    def __init__(self, agent: StaticAnalysisAgent):
        """Initialize the SAA adapter."""
        super().__init__(
            agent=agent,
            name="saa_adapter",
            description="Static Analysis Agent - performs code quality analysis"
        )
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process SAA-specific commands."""
        try:
            context = context or {}
            
            if command.lower() in ["analyze_code", "analyze"]:
                file_path = context.get("file_path")
                return await self._analyze_code(file_path)
            elif command.lower() in ["run_static_analysis", "run_analysis"]:
                return await self._run_static_analysis(context)
            else:
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _analyze_code(self, file_path: Optional[str]) -> Dict[str, Any]:
        """Analyze code for quality issues."""
        if not file_path:
            return {"status": "error", "message": "File path required for analysis"}
        
        if hasattr(self.agent, 'analyze_code'):
            result = await self.agent.analyze_code(file_path)
            return {"status": "success", "analysis": result}
        else:
            return {"status": "error", "message": "Code analysis not available"}
    
    async def _run_static_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive static analysis."""
        if hasattr(self.agent, 'run_static_analysis'):
            result = await self.agent.run_static_analysis(context)
            return {"status": "success", "analysis": result}
        else:
            return {"status": "error", "message": "Static analysis not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get SAA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        saa_commands = ["analyze_code", "analyze", "run_static_analysis", "run_analysis"]
        return base_commands + saa_commands

# Register all specialized adapters
if AGENTS_AVAILABLE:
    register_adapter(VersionControlMasterAgent, VCMAAdapter)
    register_adapter(VersionControlListenerAgent, VCLAAdapter)
    register_adapter(CodeDocumentationInspectorAgent, CDIAAdapter)
    register_adapter(ReadmeDocumentationInspectorAgent, RDIAAdapter)
    register_adapter(StaticAnalysisAgent, SAAAdapter)
        """
        instruction = """
        You are the README Inspector Agent, responsible for ensuring that project documentation is 
        comprehensive, accurate, up-to-date, and follows best practices.
        
        You can:
        - Parse README and related documentation files
        - Extract and validate structured sections
        - Compare documentation against actual project capabilities
        - Identify gaps, inconsistencies, and outdated information
        - Generate documentation improvement recommendations
        """
        super().__init__(agent, name=name or "rdia", instruction=instruction, servers=servers)


class SAAFastAdapter(FastAgentAdapter):
    """Adapter for Static Analysis Agent."""
    
    def __init__(self, agent: StaticAnalysisAgent, name: Optional[str] = None, 
                 servers: Optional[List[str]] = None):
        """
        Initialize the SAA adapter.
        
        Args:
            agent: The SAA agent to adapt
            name: Optional name for the fast-agent (defaults to 'saa')
            servers: Optional list of MCP servers to use
        """
        instruction = """
        You are the Static Analysis Agent, responsible for applying static analysis techniques to identify 
        code quality issues, potential bugs, and anti-patterns.
        
        You can:
        - Perform linting against configurable rule sets
        - Analyze code complexity
        - Check types and infer types
        - Detect security vulnerabilities
        - Identify performance issues
        """
        super().__init__(agent, name=name or "saa", instruction=instruction, servers=servers)


# Register specialized adapters
register_adapter(VersionControlMasterAgent, VCMAFastAdapter)
register_adapter(VersionControlListenerAgent, VCLAFastAdapter)
register_adapter(CodeDocumentationInspectorAgent, CDIAFastAdapter)
register_adapter(ReadmeDocumentationInspectorAgent, RDIAFastAdapter)
register_adapter(StaticAnalysisAgent, SAAFastAdapter)

# Async initialization flag
_INITIALIZED = False

async def ensure_adapters_initialized() -> bool:
    """
    Ensure all adapter types are initialized and ready to use.
    
    Returns:
        True if initialization was successful, False otherwise
    """
    global _INITIALIZED
    
    if _INITIALIZED:
        return True
    
    try:
        # This could include any setup that needs to happen before adapters are used
        # For example, ensuring necessary MCP servers are running
        
        _INITIALIZED = True
        return True
    except Exception as e:
        logger.error(f"Failed to initialize adapters: {e}")
        return False