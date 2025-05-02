#!/usr/bin/env python
"""
Example client for interacting with Dev Sentinel MCP Server.

This script demonstrates how to send commands to Dev Sentinel using both
the HTTP API and native MCP protocol.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import argparse

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("mcp_client")

# Try to import fast-agent-mcp for native MCP
try:
    import mcp_agent as fast
except ImportError:
    logger.warning("fast-agent-mcp not installed, only HTTP API will be available")
    fast = None

class DevSentinelClient:
    """Client for interacting with Dev Sentinel MCP Server."""
    
    def __init__(
        self, 
        http_host: str = "localhost",
        http_port: int = 8000,
        mcp_host: str = "localhost",
        mcp_port: int = 8090
    ):
        """
        Initialize the client.
        
        Args:
            http_host: Host for HTTP API
            http_port: Port for HTTP API
            mcp_host: Host for MCP server
            mcp_port: Port for MCP server
        """
        self.http_base_url = f"http://{http_host}:{http_port}"
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port
        
    async def execute_command_http(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command using the HTTP API.
        
        Args:
            command: Command type (e.g., VIC, CODE)
            args: Command arguments
            
        Returns:
            Command execution result
        """
        async with httpx.AsyncClient() as client:
            # Prepare request
            url = f"{self.http_base_url}/api/commands"
            payload = {
                "command": command,
                "args": args
            }
            
            # Send request
            try:
                logger.info(f"Sending HTTP request: {payload}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                # Check if command is pending
                result = response.json()
                if result.get("status") == "pending":
                    request_id = result.get("requestId")
                    if not request_id:
                        raise ValueError("Missing request ID for pending command")
                        
                    # Poll for result
                    logger.info(f"Command {request_id} is pending, polling for result...")
                    return await self._poll_command_result(client, request_id)
                    
                return result
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                return {"status": "error", "error": str(e)}
                
            except Exception as e:
                logger.exception(f"Error executing command: {e}")
                return {"status": "error", "error": str(e)}
    
    async def _poll_command_result(
        self, 
        client: httpx.AsyncClient, 
        request_id: str,
        max_attempts: int = 60,
        delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Poll for command execution result.
        
        Args:
            client: HTTP client
            request_id: Request ID
            max_attempts: Maximum number of polling attempts
            delay: Delay between polling attempts
            
        Returns:
            Command execution result
        """
        url = f"{self.http_base_url}/api/commands/{request_id}"
        
        for attempt in range(max_attempts):
            await asyncio.sleep(delay)
            
            try:
                response = await client.get(url)
                response.raise_for_status()
                
                result = response.json()
                if result.get("status") != "pending":
                    return result
                    
                logger.info(f"Command still pending (attempt {attempt + 1}/{max_attempts})...")
                
            except Exception as e:
                logger.error(f"Error polling result: {e}")
                return {"status": "error", "error": str(e)}
                
        return {"status": "error", "error": f"Command timed out after {max_attempts} attempts"}
    
    async def execute_command_mcp(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command using the native MCP protocol.
        
        Args:
            command: Command type (e.g., VIC, CODE)
            args: Command arguments
            
        Returns:
            Command execution result
        """
        if fast is None:
            return {"status": "error", "error": "fast-agent-mcp not installed"}
            
        try:
            logger.info(f"Sending MCP command: {command} {args}")
            
            # Execute command through MCP
            async with fast.connect(f"{self.mcp_host}:{self.mcp_port}") as agent:
                result = await agent.executeCommand(command=command, args=args)
                return result
                
        except Exception as e:
            logger.exception(f"Error executing MCP command: {e}")
            return {"status": "error", "error": str(e)}
    
    async def stream_command_mcp(self, command: str, args: Dict[str, Any]) -> None:
        """
        Execute a command and stream the results.
        
        Args:
            command: Command type (e.g., VIC, CODE)
            args: Command arguments
        """
        if fast is None:
            logger.error("fast-agent-mcp not installed")
            return
            
        try:
            logger.info(f"Streaming MCP command: {command} {args}")
            
            # Execute command through MCP with streaming
            async with fast.connect(f"{self.mcp_host}:{self.mcp_port}") as agent:
                async for frame in agent.streamCommand(command=command, args=args):
                    if frame.is_final:
                        logger.info("Final result received:")
                    else:
                        logger.info("Progress update:")
                        
                    logger.info(json.dumps(frame.content, indent=2))
                    
        except Exception as e:
            logger.exception(f"Error streaming MCP command: {e}")
    
    async def get_available_commands(self) -> List[Dict[str, Any]]:
        """
        Get the list of available commands.
        
        Returns:
            List of available commands
        """
        if fast is None:
            return [{"error": "fast-agent-mcp not installed"}]
            
        try:
            logger.info("Getting available commands...")
            
            # Get commands through MCP
            async with fast.connect(f"{self.mcp_host}:{self.mcp_port}") as agent:
                commands = await agent.getCommands()
                return commands
                
        except Exception as e:
            logger.exception(f"Error getting commands: {e}")
            return [{"error": str(e)}]

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Dev Sentinel MCP Client Example")
    parser.add_argument("--http-host", default="localhost", help="HTTP API host")
    parser.add_argument("--http-port", type=int, default=8000, help="HTTP API port")
    parser.add_argument("--mcp-host", default="localhost", help="MCP server host")
    parser.add_argument("--mcp-port", type=int, default=8090, help="MCP server port")
    parser.add_argument("--method", choices=["http", "mcp", "stream"], default="http",
                      help="Method to use for command execution")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # VIC command
    vic_parser = subparsers.add_parser("VIC", help="Validate Integrity of Code/Documentation")
    vic_parser.add_argument("--scope", choices=["ALL", "LAST", "DOCS", "FILE"], default="ALL",
                         help="Validation scope")
    vic_parser.add_argument("--file", help="File path (when scope is FILE)")
    
    # CODE command
    code_parser = subparsers.add_parser("CODE", help="Perform code operations")
    code_parser.add_argument("--tier", default="ALL", help="Code tier")
    code_parser.add_argument("--actions", help="Actions to perform")
    code_parser.add_argument("--stage", help="Stage identifier")
    
    # VCS command
    vcs_parser = subparsers.add_parser("VCS", help="Perform version control operations")
    vcs_parser.add_argument("--action", required=True, help="VCS action")
    vcs_parser.add_argument("--target", help="Target for the operation")
    vcs_parser.add_argument("--options", help="Additional options")
    
    # DIAGRAM command
    diagram_parser = subparsers.add_parser("DIAGRAM", help="Generate diagrams")
    diagram_parser.add_argument("--type", choices=["ARCH", "FLOW", "COMP", "TERM", "EXTRACT"],
                             default="ARCH", help="Diagram type")
    diagram_parser.add_argument("--source", help="Source data")
    diagram_parser.add_argument("--format", default="svg", help="Output format")
    
    # LIST command (special case)
    subparsers.add_parser("LIST", help="List available commands")
    
    args = parser.parse_args()
    
    # Create client
    client = DevSentinelClient(
        http_host=args.http_host,
        http_port=args.http_port,
        mcp_host=args.mcp_host,
        mcp_port=args.mcp_port
    )
    
    # Handle LIST command
    if args.command == "LIST":
        if args.method != "mcp":
            logger.error("LIST command requires MCP method")
            return 1
            
        commands = await client.get_available_commands()
        print(json.dumps(commands, indent=2))
        return 0
    
    # Check if command is provided
    if not args.command:
        logger.error("Command is required")
        parser.print_help()
        return 1
        
    # Create command arguments based on command type
    cmd_args = {}
    if args.command == "VIC":
        cmd_args = {"scope": args.scope}
        if args.file:
            cmd_args["file"] = args.file
    elif args.command == "CODE":
        cmd_args = {"tier": args.tier}
        if args.actions:
            cmd_args["actions"] = args.actions
        if args.stage:
            cmd_args["stage"] = args.stage
    elif args.command == "VCS":
        cmd_args = {"action": args.action}
        if args.target:
            cmd_args["target"] = args.target
        if args.options:
            cmd_args["options"] = args.options
    elif args.command == "DIAGRAM":
        cmd_args = {"type": args.type, "format": args.format}
        if args.source:
            cmd_args["source"] = args.source
            
    # Execute command using selected method
    if args.method == "http":
        result = await client.execute_command_http(args.command, cmd_args)
        print(json.dumps(result, indent=2))
    elif args.method == "mcp":
        if fast is None:
            logger.error("fast-agent-mcp not installed")
            return 1
            
        result = await client.execute_command_mcp(args.command, cmd_args)
        print(json.dumps(result, indent=2))
    elif args.method == "stream":
        if fast is None:
            logger.error("fast-agent-mcp not installed")
            return 1
            
        await client.stream_command_mcp(args.command, cmd_args)
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)