#!/usr/bin/env python
"""
YUNG Command Processor Agent for fast-agent integration

This module provides a fast-agent implementation that processes YUNG commands
and delegates them to the appropriate MCP servers.
"""

import os
import sys
import re
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("yung_processor")

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Also add parent directory to handle imports from sibling modules
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Import fast-agent framework
    import mcp_agent as fast
except ImportError:
    raise ImportError("mcp_agent (fast-agent-mcp) package is not installed. Run 'pip install fast-agent-mcp'")

# Import Dev Sentinel components
try:
    from integration.force.master_agent import ForceCommandProcessor
except ImportError:
    logger.error("Failed to import ForceCommandProcessor. Make sure Dev Sentinel is properly installed.")
    raise

class CommandType(Enum):
    """Enumeration of YUNG command types."""
    VIC = "VIC"
    CODE = "CODE"
    VCS = "VCS"
    TEST = "TEST"
    INFRA = "INFRA"
    FAST = "FAST"
    DIAGRAM = "DIAGRAM"
    MAN = "MAN"
    UNKNOWN = "UNKNOWN"

class YUNGCommandParser:
    """Parser for YUNG command syntax."""
    
    # Command pattern with advanced argument parsing
    COMMAND_PATTERN = r'^\$(VIC|CODE|VCS|TEST|INFRA|FAST|DIAGRAM|MAN)\s*(.*?)$'
    
    # Argument patterns
    SCOPE_ARG = r'(ALL|LAST|DOCS|FILE=([^\s;]+))'
    TIER_ARG = r'(TIER=([^\s,;]+)|ALL)'
    ACTION_ARG = r'(ACTION=([^\s,;]+)|([A-Z]+))'
    TARGET_ARG = r'(TARGET=([^\s,;]+)|([A-Z]+))'
    OPTIONS_ARG = r'([^\s=]+)="([^"]*)"'
    
    @staticmethod
    def parse_command(command_str: str) -> Dict[str, Any]:
        """
        Parse a YUNG command string into a structured representation.
        
        Args:
            command_str: The YUNG command string to parse
            
        Returns:
            A dictionary containing the parsed command and arguments
        """
        command_match = re.match(YUNGCommandParser.COMMAND_PATTERN, command_str.strip())
        if not command_match:
            return {
                "command": CommandType.UNKNOWN.value,
                "args": {},
                "raw": command_str
            }
        
        command_type = command_match.group(1)
        args_str = command_match.group(2).strip()
        
        # Parse command-specific arguments
        args = {}
        
        if command_type == CommandType.VIC.value:
            scope_match = re.search(YUNGCommandParser.SCOPE_ARG, args_str)
            if scope_match:
                scope = scope_match.group(1)
                file_path = scope_match.group(2)
                args["scope"] = scope.replace(f'FILE={file_path}', 'FILE') if file_path else scope
                if file_path:
                    args["file"] = file_path
        
        elif command_type == CommandType.CODE.value:
            tier_match = re.search(YUNGCommandParser.TIER_ARG, args_str)
            if tier_match:
                tier = tier_match.group(2) if tier_match.group(2) else 'ALL'
                args["tier"] = tier
                
            # Extract actions
            actions = []
            action_words = [word for word in args_str.split() if word not in ['TIER=' + tier] and word.isupper()]
            if action_words:
                args["actions"] = " ".join(action_words)
                
            # Extract stage
            stage_match = re.search(r'STAGE=(\w+)', args_str)
            if stage_match:
                args["stage"] = stage_match.group(1)
        
        elif command_type == CommandType.VCS.value:
            action_match = re.search(YUNGCommandParser.ACTION_ARG, args_str)
            if action_match:
                action = action_match.group(2) or action_match.group(3)
                args["action"] = action
                
            target_match = re.search(YUNGCommandParser.TARGET_ARG, args_str)
            if target_match:
                target = target_match.group(2) or target_match.group(3)
                args["target"] = target
                
            # Extract quoted options
            options_matches = re.findall(YUNGCommandParser.OPTIONS_ARG, args_str)
            if options_matches:
                options = {}
                for opt_name, opt_value in options_matches:
                    options[opt_name] = opt_value
                args["options"] = options
        
        elif command_type == CommandType.DIAGRAM.value:
            # Extract diagram type
            type_match = re.search(r'(ARCH|FLOW|COMP|TERM|EXTRACT)', args_str)
            if type_match:
                args["type"] = type_match.group(1)
                
            # Extract source
            source_match = re.search(r'SOURCE=([^\s;]+)', args_str)
            if source_match:
                args["source"] = source_match.group(1)
                
            # Extract format
            format_match = re.search(r'FORMAT=([a-z]+)', args_str)
            if format_match:
                args["format"] = format_match.group(1)
        
        return {
            "command": command_type,
            "args": args,
            "raw": command_str
        }

class YUNGCommandProcessor:
    """
    Processor for YUNG commands that maps them to fast-agent actions.
    
    This class handles the translation between YUNG commands and the appropriate
    fast-agent and MCP server calls.
    """
    
    def __init__(self):
        """Initialize the YUNG command processor."""
        self.force_processor = ForceCommandProcessor()
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        
    async def ensure_initialized(self):
        """Ensure the FORCE command processor is initialized."""
        if self._initialized:
            return
            
        async with self._initialization_lock:
            if self._initialized:
                return
                
            try:
                await self.force_processor.initialize()
                # Also ensure fast-agent is initialized
                await self.force_processor.ensure_fast_agent_initialized()
                
                self._initialized = True
                logger.info("YUNG Command Processor initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize YUNG Command Processor: {e}")
                raise
    
    async def process_command(self, command_str: str) -> Dict[str, Any]:
        """
        Process a YUNG command string and execute it using the appropriate agent.
        
        Args:
            command_str: The YUNG command string to process
            
        Returns:
            Result of the command execution
        """
        # Ensure initialized
        await self.ensure_initialized()
        
        # Parse the command
        parsed = YUNGCommandParser.parse_command(command_str)
        
        # Log the parsed command
        logger.info(f"Processing command: {parsed['command']}")
        logger.debug(f"Command details: {json.dumps(parsed, indent=2)}")
        
        # Process the command using the FORCE processor
        result = await self.force_processor.process_command(command_str)
        
        return result

# Define the fast-agent decorator with server list
@fast.agent(
    name="yung_processor",
    instruction="""You are the YUNG command processor agent for Dev Sentinel.
    You understand the YUNG command syntax and can execute commands through the FORCE architecture.
    
    YUNG Command Structure:
    - $<COMMAND_TYPE> [ARGUMENTS]
    
    Primary Commands:
    - $VIC [SCOPE] - Validate integrity of code/documentation
    - $CODE [TIER] [ACTIONS] - Code generation and management
    - $VCS [ACTION] [TARGET] [OPTIONS] - Version control operations
    - $FAST [ACTION] [TARGET] [OPTIONS] - fast-agent operations
    - $DIAGRAM [TYPE] [FORMAT] - Generate system diagrams
    - $MAN - Display command manual
    """,
    servers=["dev_sentinel", "filesystem", "vcs", "documentation", "code_analysis"],
    model="o3-mini.high"
)
async def yung_processor_agent(message: str) -> str:
    """
    YUNG command processor agent.
    
    Args:
        message: User message containing a YUNG command
        
    Returns:
        Result of the command execution
    """
    # Create a YUNG command processor
    processor = YUNGCommandProcessor()
    
    # Check if the message contains a YUNG command
    command_match = re.search(r'\$(VIC|CODE|VCS|TEST|INFRA|FAST|DIAGRAM|MAN)\s', message)
    if not command_match:
        return """I'm the YUNG Command Processor. Please provide a valid YUNG command.
        
YUNG Command examples:
$VIC DOCS - Validate documentation
$CODE ALL IMPL - Implement code for all tiers
$VCS STATUS - Check git repository status
$DIAGRAM ARCH - Generate architecture diagram
$MAN - Display command manual"""
    
    # Extract the command from the message
    command_start = command_match.start()
    command_str = message[command_start:].strip()
    
    try:
        # Process the command
        result = await processor.process_command(command_str)
        
        # Return the result
        if isinstance(result, dict):
            return json.dumps(result, indent=2)
        else:
            return str(result)
    except Exception as e:
        logger.exception(f"Error processing command: {e}")
        return f"Error processing command: {str(e)}"

# Define workflow that combines document inspection and code analysis
@fast.workflow(
    name="inspect_and_analyze",
    agents=["doc_inspector", "code_analyzer"],
    description="Inspect documentation and analyze code quality in the repository"
)
async def inspect_and_analyze_workflow(repo_path: str) -> Dict[str, Any]:
    """
    Workflow that combines documentation inspection and code quality analysis.
    
    Args:
        repo_path: Path to the repository to analyze
        
    Returns:
        Analysis results
    """
    # Connect to MCP servers
    async with fast.connect("documentation") as doc_agent:
        async with fast.connect("code_analysis") as code_agent:
            # Inspect documentation
            doc_results = await doc_agent.inspect_documentation(file_path=repo_path)
            
            # Analyze code
            code_results = await code_agent.analyze_code(file_path=repo_path)
            
            # Combine results
            return {
                "documentation": doc_results,
                "code_analysis": code_results
            }

# Define workflow that executes a YUNG command
@fast.workflow(
    name="execute_yung_command",
    agents=["yung_processor"],
    description="Execute a YUNG command through the FORCE architecture"
)
async def execute_yung_command_workflow(command: str) -> Dict[str, Any]:
    """
    Workflow that executes a YUNG command.
    
    Args:
        command: The YUNG command to execute
        
    Returns:
        Command execution results
    """
    # Connect to YUNG processor agent
    async with fast.connect("yung_processor") as yung_agent:
        return await yung_agent(command)

async def main():
    """Main entry point for interactive mode."""
    # Initialize agent with model specified through argparse
    import argparse
    parser = argparse.ArgumentParser(description="YUNG Command Processor Agent")
    parser.add_argument("--model", default="o3-mini.high", help="Model to use (e.g., o3-mini.high, haiku)")
    args = parser.parse_args()
    
    # Start interactive agent
    async with fast.run(model=args.model) as agent:
        print("YUNG Command Processor initialized. Type '$MAN' for help or 'exit' to quit.")
        
        while True:
            # Get user input
            user_input = input("\nEnter a YUNG command: ")
            
            # Check if user wants to exit
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            
            # Process the command
            result = await agent(user_input)
            print("\n" + result)

if __name__ == "__main__":
    asyncio.run(main())