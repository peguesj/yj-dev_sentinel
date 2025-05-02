"""
Master Agent for FORCE architecture.

This module implements the master agent responsible for orchestrating
subagents, processing YUNG commands, and managing the integration 
between fast-agent and Dev Sentinel.
"""

import os
import re
import json
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Callable, Tuple

from core.agent import BaseAgent
from core.message_bus import MessageBus
from integration.terminal_manager import get_terminal_manager, execute_in_subagent_terminal
from integration.fast_agent.setup import setup_fast_agent_integration
from integration.fast_agent.adapter import FastAgentAdapter
from integration.fast_agent.async_initialization import get_async_initializer, initialize_fast_agent
from integration.fast_agent.specialized_adapters import create_specialized_adapter, ensure_adapters_initialized
from integration.diagram_generator import ArchitectureDiagramGenerator, generate_diagrams_from_markdown
import mcp_agent as fast

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("force_master_agent")

# YUNG command patterns
YUNG_COMMAND_PATTERNS = {
    "vic": r"\$VIC\s+(ALL|LAST|DOCS|FILE=([^\s;]+))",
    "code": r"\$CODE\s+(TIER=([^\s,;]+)|ALL)(?:\s+([^;]+))?(?:\s+Stage\s+([^;]+))?",
    "vcs": r"\$VCS\s+(\w+)(?:\s+([^;\"]+|\"[^\"]+\"))?(?:\s+([^;]+))?",
    "infra": r"\$INFRA\s+(\w+)(?:\s+(\w+))?(?:\s+([^;]+))?",
    "test": r"\$TEST\s+(\w+)(?:\s+([^;]+))?(?:\s+([^;]+))?",
    "fast": r"\$FAST\s+(\w+)(?:\s+(\w+))?(?:\s+([^;]+))?",
    "diagram": r"\$DIAGRAM\s+(ARCH|FLOW|COMP|TERM|EXTRACT)(?:\s+((?:FILE|FORMAT)=[^\s;]+|FORCE|YUNG|AGENT))?(?:\s+(FORMAT=[^\s;]+))?"
}

class SubagentMapping:
    """Mapping between subagent types and their implementations."""
    
    # Subagent name to terminal ID mapping
    SUBAGENT_TERMINALS = {
        "vcs": "TERMINAL-VCS",
        "documentation": "TERMINAL-DOC",
        "code": "TERMINAL-CODE",
        "infrastructure": "TERMINAL-INFRA",
        "testing": "TERMINAL-TEST",
        "fast_agent": "TERMINAL-FAST"
    }
    
    # YUNG command to subagent mapping
    COMMAND_SUBAGENT_MAPPING = {
        "vic": "documentation",
        "code": "code",
        "vcs": "vcs",
        "infra": "infrastructure",
        "test": "testing",
        "fast": "fast_agent",
        "diagram": "code"  # Diagrams are handled by the code subagent
    }
    
    # Subagent to fast-agent adapter mapping
    SUBAGENT_FASTADAPTER_MAPPING = {
        "documentation": ["cdia", "rdia"],
        "code": ["saa"],
        "vcs": ["vcma", "vcla"],
        "testing": ["saa"],
        "infrastructure": ["vcma"],  # Placeholder - would need infrastructure-specific agents
        "fast_agent": []  # Directly uses fast-agent
    }


class ForceCommandProcessor:
    """
    Processes YUNG commands and routes them to appropriate subagents.
    """
    
    def __init__(self):
        """Initialize the FORCE command processor."""
        self.terminal_manager = None
        self.fast_agent_initialized = False
        self.async_fast_agent_initializer = None
        self.fast_agent_integration_dir = os.path.join(os.getcwd(), ".force", "fast_agent")
        self.diagram_output_dir = os.path.join(os.getcwd(), "docs", "diagrams")
        self.arch_diagram_generator = None
        self.initialization_lock = asyncio.Lock()
        self.agent_cache = {}
        self.adapter_cache = {}
        
    async def initialize(self):
        """Initialize the command processor."""
        # Get terminal manager
        self.terminal_manager = await get_terminal_manager()
        
        # Create directories if needed
        os.makedirs(os.path.join(os.getcwd(), ".force"), exist_ok=True)
        os.makedirs(self.diagram_output_dir, exist_ok=True)
        
        # Initialize architecture diagram generator
        self.arch_diagram_generator = ArchitectureDiagramGenerator(self.diagram_output_dir)
        
        # Start fast-agent initialization asynchronously
        try:
            # We're doing this asynchronously to avoid blocking the initialization process
            # The actual adapters will be created lazily when needed
            self.async_fast_agent_initializer = get_async_initializer(
                workspace_dir=os.path.dirname(self.fast_agent_integration_dir)
            )
            
            # Trigger initialization but don't wait for it
            asyncio.create_task(self._initialize_fast_agent_async())
            
        except Exception as e:
            logger.warning(f"Failed to start fast-agent initialization: {e}")
    
    async def _initialize_fast_agent_async(self):
        """Initialize fast-agent asynchronously."""
        try:
            async with self.initialization_lock:
                if not self.fast_agent_initialized:
                    logger.info("Initializing fast-agent integration asynchronously...")
                    
                    # Initialize fast-agent
                    result = await initialize_fast_agent(
                        workspace_dir=os.path.dirname(self.fast_agent_integration_dir)
                    )
                    
                    if result.get("status") == "success":
                        logger.info("Fast-agent initialization completed successfully")
                        self.fast_agent_initialized = True
                    else:
                        logger.error(f"Fast-agent initialization failed: {result.get('message', 'Unknown error')}")
                        
                    return result
                    
                return {"status": "success", "message": "Already initialized"}
        except Exception as e:
            logger.error(f"Error during fast-agent initialization: {e}")
            return {"status": "error", "message": str(e)}
    
    async def ensure_fast_agent_initialized(self) -> bool:
        """
        Ensure that fast-agent is initialized.
        
        Returns:
            True if fast-agent is initialized, False otherwise
        """
        if self.fast_agent_initialized:
            return True
            
        try:
            # If initialization is already in progress, wait for it
            async with self.initialization_lock:
                if not self.fast_agent_initialized:
                    logger.info("Waiting for fast-agent initialization to complete...")
                    
                    # Initialize fast-agent and wait for completion
                    result = await initialize_fast_agent(
                        workspace_dir=os.path.dirname(self.fast_agent_integration_dir)
                    )
                    
                    self.fast_agent_initialized = result.get("status") == "success"
                    
                    if not self.fast_agent_initialized:
                        logger.error(f"Fast-agent initialization failed: {result.get('message', 'Unknown error')}")
                        
                return self.fast_agent_initialized
        except Exception as e:
            logger.error(f"Error ensuring fast-agent initialization: {e}")
            return False
    
    async def get_agent_adapter(self, agent_id: str, adapter_type: str) -> Optional[FastAgentAdapter]:
        """
        Get or create a fast-agent adapter for the given agent.
        
        Args:
            agent_id: ID of the agent to get an adapter for
            adapter_type: Type of adapter to create
            
        Returns:
            The agent adapter or None if creation failed
        """
        # Ensure fast-agent is initialized
        if not await self.ensure_fast_agent_initialized():
            logger.error("Cannot get agent adapter: fast-agent not initialized")
            return None
            
        # Get or create the agent
        agent = await self._get_or_create_agent(agent_id)
        if not agent:
            logger.error(f"Failed to get or create agent: {agent_id}")
            return None
            
        # Check adapter cache
        adapter_key = f"{agent_id}_{adapter_type}"
        if adapter_key in self.adapter_cache:
            return self.adapter_cache[adapter_key]
            
        try:
            # Create adapter using the async initializer
            adapter = await self.async_fast_agent_initializer.get_adapter(agent, adapter_type)
            
            # Cache the adapter
            self.adapter_cache[adapter_key] = adapter
            
            return adapter
        except Exception as e:
            logger.error(f"Failed to create adapter for agent {agent_id}: {e}")
            return None
    
    async def _get_or_create_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get or create an agent by ID.
        
        Args:
            agent_id: ID of the agent to get or create
            
        Returns:
            The agent or None if creation failed
        """
        # Check agent cache
        if agent_id in self.agent_cache:
            return self.agent_cache[agent_id]
            
        try:
            # Import agent creation functions based on agent_id
            if agent_id.startswith("vcma"):
                from agents.vcma.vcma_agent import create_vcma
                agent = create_vcma()
            elif agent_id.startswith("vcla"):
                from agents.vcla.vcla_agent import create_vcla
                agent = create_vcla()
            elif agent_id.startswith("cdia"):
                from agents.cdia.cdia_agent import create_cdia
                agent = create_cdia()
            elif agent_id.startswith("rdia"):
                from agents.rdia.rdia_agent import create_rdia
                agent = create_rdia()
            elif agent_id.startswith("saa"):
                from agents.saa.saa_agent import create_saa
                agent = create_saa()
            else:
                logger.error(f"Unknown agent ID: {agent_id}")
                return None
                
            # Initialize agent
            await agent.initialize()
            await agent.start()
            
            # Cache the agent
            self.agent_cache[agent_id] = agent
            
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent {agent_id}: {e}")
            return None
        
    async def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a YUNG command.
        
        Args:
            command: YUNG command string
            
        Returns:
            Dict containing command execution results
        """
        # Check for empty command
        if not command or not command.strip():
            return {"error": "Empty command", "exit_code": 1}
        
        # Split into individual commands (semicolon separated)
        commands = [cmd.strip() for cmd in command.split(";") if cmd.strip()]
        results = []
        
        # Process each command
        for cmd in commands:
            cmd_result = await self._process_single_command(cmd)
            results.append(cmd_result)
        
        return {
            "command": command,
            "results": results,
            "exit_code": any(r.get("exit_code", 0) != 0 for r in results)
        }
        
    async def _process_single_command(self, command: str) -> Dict[str, Any]:
        """
        Process a single YUNG command.
        
        Args:
            command: Single YUNG command string
            
        Returns:
            Dict containing command execution results
        """
        # Extract command type
        command_type = self._extract_command_type(command)
        if not command_type:
            return {"error": f"Unknown command: {command}", "exit_code": 1}
            
        # Process command by type
        handler = getattr(self, f"_handle_{command_type}_command", None)
        if not handler:
            return {"error": f"No handler for command type: {command_type}", "exit_code": 1}
        
        # Execute command handler
        try:
            return await handler(command)
        except Exception as e:
            logger.exception(f"Error processing command: {command}")
            return {"error": str(e), "command": command, "exit_code": 1}
            
    def _extract_command_type(self, command: str) -> Optional[str]:
        """
        Extract the command type from a YUNG command.
        
        Args:
            command: YUNG command string
            
        Returns:
            Command type or None if not found
        """
        for cmd_type, pattern in YUNG_COMMAND_PATTERNS.items():
            if re.match(pattern, command):
                return cmd_type
                
        # Special cases
        if command.startswith("$MASTER"):
            return "master"
        elif command.startswith("$PP"):
            return "pp"
        elif command.startswith("$CLOG"):
            return "clog"
        elif command.startswith("$man") or command == "$$":
            return "man"
            
        return None

    # ... keep existing command handlers ...

    async def _handle_fast_command(self, command: str) -> Dict[str, Any]:
        """
        Handle a FAST command for fast-agent integration.
        
        Args:
            command: FAST command string
            
        Returns:
            Dict containing command execution results
        """
        # Parse command
        match = re.match(YUNG_COMMAND_PATTERNS["fast"], command)
        if not match:
            return {"error": "Invalid FAST command", "exit_code": 1}
            
        action = match.group(1)
        target = match.group(2) if match.group(2) else None
        options = match.group(3) if match.group(3) else None
        
        # Make sure fast-agent is initialized
        if not await self.ensure_fast_agent_initialized():
            return {"error": "Fast-agent not initialized", "exit_code": 1}
        
        # Process different actions
        if action.lower() == "workflow" and target and target.lower() == "run":
            # Execute a fast-agent workflow
            return await self._execute_fast_agent_workflow(options)
            
        elif action.lower() == "server" and target and target.lower() == "restart":
            # Restart an MCP server
            return await self._execute_fast_agent_server_restart(options)
            
        elif action.lower() == "model" and target and target.lower() == "switch":
            # Switch fast-agent model
            return await self._execute_fast_agent_model_switch(options)
            
        else:
            return {"error": f"Unknown FAST command action: {action}", "exit_code": 1}

    async def _execute_documentation_validation(self, scope: str, file_path: Optional[str] = None,
                                              doc_type: str = "readme") -> Dict[str, Any]:
        """
        Execute documentation validation using the appropriate agent adapter.
        
        Args:
            scope: Validation scope (ALL, DOCS, FILE)
            file_path: Path to file to validate (if scope is FILE)
            doc_type: Type of documentation to validate (readme or code)
            
        Returns:
            Dict containing validation results
        """
        # Choose the appropriate adapter type
        adapter_type = "rdia" if doc_type == "readme" else "cdia"
        agent_id = f"{adapter_type}_main"
        
        try:
            # Get the adapter using the new async initialization
            adapter = await self.get_agent_adapter(agent_id, adapter_type)
            if not adapter or not adapter.fast_agent:
                return {"error": f"Failed to get {adapter_type.upper()} adapter", "exit_code": 1}
            
            # Build the message based on scope
            message = f"Validate {doc_type} documentation"
            if scope == "ALL":
                message += " for the entire project"
            elif scope == "LAST":
                message += " for the last changes"
            elif scope == "DOCS":
                message += " files"
            elif file_path:
                message += f" in {file_path}"
            
            # Execute through fast-agent
            async with fast.run() as agent:
                # Use the appropriate adapter method
                agent_method = getattr(agent, adapter_type, None)
                if not agent_method:
                    return {"error": f"No method for adapter type: {adapter_type}", "exit_code": 1}
                    
                response = await agent_method(message)
                
                # Execute in terminal as well for state persistence
                terminal_id = SubagentMapping.SUBAGENT_TERMINALS["documentation"]
                terminal_cmd = f"# {message}\n# Processing using {adapter_type.upper()} adapter..."
                await execute_in_subagent_terminal(terminal_id, terminal_cmd)
                
                return {"response": response, "exit_code": 0}
                
        except Exception as e:
            logger.exception(f"Error executing documentation validation: {e}")
            return {"error": str(e), "exit_code": 1}
            
    async def _execute_fast_agent_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        Execute a fast-agent workflow.
        
        Args:
            workflow_name: Name of the workflow to execute
            
        Returns:
            Dict containing workflow execution results
        """
        if not workflow_name:
            return {"error": "Workflow name is required", "exit_code": 1}
            
        try:
            # Execute through fast-agent
            async with fast.run() as agent:
                # Get the workflow method
                workflow_method = getattr(agent, workflow_name, None)
                if not workflow_method:
                    return {"error": f"Unknown workflow: {workflow_name}", "exit_code": 1}
                    
                # Execute the workflow
                response = await workflow_method()
                
                # Execute in terminal for state persistence
                terminal_id = SubagentMapping.SUBAGENT_TERMINALS["fast_agent"]
                terminal_cmd = f"# Executing fast-agent workflow: {workflow_name}"
                await execute_in_subagent_terminal(terminal_id, terminal_cmd)
                
                return {"response": response, "exit_code": 0}
                
        except Exception as e:
            logger.exception(f"Error executing fast-agent workflow: {e}")
            return {"error": str(e), "exit_code": 1}
            
    async def _execute_fast_agent_server_restart(self, server_name: str) -> Dict[str, Any]:
        """
        Restart an MCP server.
        
        Args:
            server_name: Name of the server to restart
            
        Returns:
            Dict containing server restart results
        """
        if not server_name:
            return {"error": "Server name is required", "exit_code": 1}
            
        try:
            # Execute server restart in terminal
            terminal_id = SubagentMapping.SUBAGENT_TERMINALS["fast_agent"]
            terminal_cmd = f"cd {self.fast_agent_integration_dir}/servers && uv run dev_sentinel_{server_name}_server.py"
            
            result = await execute_in_subagent_terminal(terminal_id, terminal_cmd)
            
            return {"response": f"Server {server_name} restart initiated", "exit_code": 0}
                
        except Exception as e:
            logger.exception(f"Error restarting MCP server: {e}")
            return {"error": str(e), "exit_code": 1}
            
    async def _execute_fast_agent_model_switch(self, model_name: str) -> Dict[str, Any]:
        """
        Switch the fast-agent model.
        
        Args:
            model_name: Name of the model to switch to
            
        Returns:
            Dict containing model switch results
        """
        if not model_name:
            return {"error": "Model name is required", "exit_code": 1}
            
        try:
            # Update the fast-agent configuration file
            config_path = os.path.join(self.fast_agent_integration_dir, "fastagent.config.yaml")
            
            if not os.path.exists(config_path):
                return {"error": f"Fast-agent config file not found: {config_path}", "exit_code": 1}
                
            # Read the current config
            import yaml
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                
            # Update the model
            if "model" not in config:
                config["model"] = {}
                
            config["model"]["name"] = model_name
            
            # Write the updated config
            with open(config_path, "w") as f:
                yaml.safe_dump(config, f)
                
            # Execute in terminal for state persistence
            terminal_id = SubagentMapping.SUBAGENT_TERMINALS["fast_agent"]
            terminal_cmd = f"# Switched fast-agent model to: {model_name}"
            await execute_in_subagent_terminal(terminal_id, terminal_cmd)
            
            return {"response": f"Fast-agent model switched to: {model_name}", "exit_code": 0}
                
        except Exception as e:
            logger.exception(f"Error switching fast-agent model: {e}")
            return {"error": str(e), "exit_code": 1}