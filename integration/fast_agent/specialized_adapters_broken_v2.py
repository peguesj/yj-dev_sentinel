"""
Specialized adapters for specific Dev Sentinel agent types.

This module provides specialized MCP and fast-agent adapters for each type of
Dev Sentinel agent, offering tailored interfaces that expose agent-specific
capabilities and commands.
"""
from typing import List, Optional, Dict, Any, Type, Union
import asyncio
import logging

from integration.fast_agent.adapter import BaseAgentAdapter, MCPAgentAdapter
from core.agent import BaseAgent

# Import agent types
try:
    from agents.vcma.vcma_agent import VersionControlMasterAgent
    from agents.vcla.vcla_agent import VersionControlListenerAgent
    from agents.cdia.cdia_agent import CodeDocumentationInspectorAgent
    from agents.rdia.rdia_agent import READMEInspectorAgent as ReadmeDocumentationInspectorAgent
    from agents.saa.saa_agent import StaticAnalysisAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some agent types not available: {e}")
    AGENTS_AVAILABLE = False
    # Create stub classes for development
    VersionControlMasterAgent = type('VersionControlMasterAgent', (BaseAgent,), {})
    VersionControlListenerAgent = type('VersionControlListenerAgent', (BaseAgent,), {})
    CodeDocumentationInspectorAgent = type('CodeDocumentationInspectorAgent', (BaseAgent,), {})
    ReadmeDocumentationInspectorAgent = type('ReadmeDocumentationInspectorAgent', (BaseAgent,), {})
    StaticAnalysisAgent = type('StaticAnalysisAgent', (BaseAgent,), {})

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
            # Use MCPAgentAdapter as the default since BaseAgentAdapter is abstract
            adapter = MCPAgentAdapter(agent)
    
    await adapter.initialize()
    return adapter

class VCMAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for Version Control Master Agent."""
    
    def __init__(self, agent: BaseAgent):
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
            get_repo_status = getattr(self.agent, 'get_repo_status')
            status = await get_repo_status()
            return {"status": "success", "repo_status": status}
        else:
            return {"status": "error", "message": "Repository status not available"}
    
    async def _analyze_commits(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commits using VCMA."""
        if hasattr(self.agent, 'analyze_commits'):
            analyze_commits = getattr(self.agent, 'analyze_commits')
            result = await analyze_commits(context)
            return {"status": "success", "analysis": result}
        else:
            return {"status": "error", "message": "Commit analysis not available"}
    
    async def _refresh_repo(self) -> Dict[str, Any]:
        """Refresh repository state."""
        if hasattr(self.agent, '_refresh_repo_state'):
            refresh_repo_state = getattr(self.agent, '_refresh_repo_state')
            await refresh_repo_state()
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
    
    def __init__(self, agent: BaseAgent):
        """Initialize the VCLA adapter."""
        super().__init__(
            agent=agent,
            name="vcla_adapter", 
            description="Version Control Listener Agent - monitors specific repository aspects"
        )
    
    async def _safe_call_agent_method(self, method_name: str, *args, **kwargs) -> Any:
        """Safely call an agent method if it exists."""
        if hasattr(self.agent, method_name):
            method = getattr(self.agent, method_name)
            return await method(*args, **kwargs)
        return None
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process VCLA-specific commands."""
        try:
            context = context or {}
            
            if command.lower() in ["monitor", "start_monitoring"]:
                return await self._start_monitoring(context)
            elif command.lower() in ["stop_monitoring", "stop"]:
                return await self._stop_monitoring()
            elif command.lower() in ["get_listening_status", "listening_status"]:
                return await self._get_listening_status()
            else:
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _start_monitoring(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Start monitoring with VCLA."""
        result = await self._safe_call_agent_method('start_monitoring', context)
        if result is not None:
            return {"status": "success", "monitoring": result}
        else:
            return {"status": "error", "message": "Monitoring not available"}
    
    async def _stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring."""
        result = await self._safe_call_agent_method('stop_monitoring')
        if result is not None:
            return {"status": "success", "message": "Monitoring stopped"}
        else:
            return {"status": "error", "message": "Stop monitoring not available"}
    
    async def _get_listening_status(self) -> Dict[str, Any]:
        """Get current listening status."""
        result = await self._safe_call_agent_method('get_listening_status')
        if result is not None:
            return {"status": "success", "listening_status": result}
        else:
            return {"status": "error", "message": "Listening status not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get VCLA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        vcla_commands = ["monitor", "start_monitoring", "stop_monitoring", "stop", "get_listening_status", "listening_status"]
        return base_commands + vcla_commands

class CDIAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for Code Documentation Inspector Agent."""
    
    def __init__(self, agent: BaseAgent):
        """Initialize the CDIA adapter."""
        super().__init__(
            agent=agent,
            name="cdia_adapter",
            description="Code Documentation Inspector Agent - analyzes and improves code documentation"
        )
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process CDIA-specific commands."""
        try:
            context = context or {}
            
            if command.lower() in ["inspect_code", "inspect"]:
                file_path = context.get("file_path")
                return await self._inspect_code(file_path)
            elif command.lower() in ["analyze_documentation", "analyze_docs"]:
                return await self._analyze_documentation(context)
            elif command.lower() in ["generate_docs", "generate_documentation"]:
                return await self._generate_documentation(context)
            else:
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _inspect_code(self, file_path: Optional[str]) -> Dict[str, Any]:
        """Inspect code documentation."""
        if not file_path:
            return {"status": "error", "message": "File path required for inspection"}
        
        if hasattr(self.agent, 'inspect_code'):
            result = await self.agent.inspect_code(file_path)
            return {"status": "success", "inspection": result}
        else:
            return {"status": "error", "message": "Code inspection not available"}
    
    async def _analyze_documentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documentation quality."""
        if hasattr(self.agent, 'analyze_documentation'):
            result = await self.agent.analyze_documentation(context)
            return {"status": "success", "analysis": result}
        else:
            return {"status": "error", "message": "Documentation analysis not available"}
    
    async def _generate_documentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation."""
        if hasattr(self.agent, 'generate_documentation'):
            result = await self.agent.generate_documentation(context)
            return {"status": "success", "documentation": result}
        else:
            return {"status": "error", "message": "Documentation generation not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get CDIA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        cdia_commands = ["inspect_code", "inspect", "analyze_documentation", "analyze_docs", "generate_docs", "generate_documentation"]
        return base_commands + cdia_commands

class RDIAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for README Documentation Inspector Agent."""
    
    def __init__(self, agent: BaseAgent):
        """Initialize the RDIA adapter."""
        super().__init__(
            agent=agent,
            name="rdia_adapter",
            description="README Documentation Inspector Agent - ensures project documentation quality"
        )
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process RDIA-specific commands."""
        try:
            context = context or {}
            
            if command.lower() in ["inspect_readme", "inspect"]:
                return await self._inspect_readme(context)
            elif command.lower() in ["validate_docs", "validate"]:
                return await self._validate_documentation(context)
            elif command.lower() in ["improve_readme", "improve"]:
                return await self._improve_readme(context)
            else:
                return await super().process_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, command, context or {})
    
    async def _inspect_readme(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Inspect README files."""
        if hasattr(self.agent, 'inspect_readme'):
            result = await self.agent.inspect_readme(context)
            return {"status": "success", "inspection": result}
        else:
            return {"status": "error", "message": "README inspection not available"}
    
    async def _validate_documentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate documentation consistency."""
        if hasattr(self.agent, 'validate_documentation'):
            result = await self.agent.validate_documentation(context)
            return {"status": "success", "validation": result}
        else:
            return {"status": "error", "message": "Documentation validation not available"}
    
    async def _improve_readme(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate README improvements."""
        if hasattr(self.agent, 'improve_readme'):
            result = await self.agent.improve_readme(context)
            return {"status": "success", "improvements": result}
        else:
            return {"status": "error", "message": "README improvement not available"}
    
    async def _get_supported_commands(self) -> List[str]:
        """Get RDIA-specific supported commands."""
        base_commands = await super()._get_supported_commands()
        rdia_commands = ["inspect_readme", "inspect", "validate_docs", "validate", "improve_readme", "improve"]
        return base_commands + rdia_commands

class SAAAdapter(MCPAgentAdapter):
    """Specialized MCP adapter for Static Analysis Agent."""
    
    def __init__(self, agent: BaseAgent):
        """Initialize the SAA adapter."""
        super().__init__(
            agent=agent,
            name="saa_adapter",
            description="Static Analysis Agent - performs comprehensive code quality analysis"
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
        logger.info("Specialized adapters initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize adapters: {e}")
        return False

def get_adapter_for_agent_type(agent_cls: Type) -> Optional[Type[BaseAgentAdapter]]:
    """
    Get the registered adapter class for a specific agent type.
    
    Args:
        agent_cls: The agent class to get an adapter for
        
    Returns:
        The adapter class if registered, None otherwise
    """
    return ADAPTER_REGISTRY.get(agent_cls)

def list_registered_adapters() -> Dict[str, str]:
    """
    Get a list of all registered adapters.
    
    Returns:
        Dictionary mapping agent class names to adapter class names
    """
    return {
        agent_cls.__name__: adapter_cls.__name__
        for agent_cls, adapter_cls in ADAPTER_REGISTRY.items()
    }
