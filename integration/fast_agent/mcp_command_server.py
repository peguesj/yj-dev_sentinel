"""
MCP Server implementations for Dev Sentinel.

This module provides Model Context Protocol (MCP) server implementations
that can be used with fast-agent to execute Dev Sentinel commands.
"""

import os
import sys
import json
import logging
import asyncio
import copy
from typing import Dict, List, Any, Optional, Union, Callable, AsyncIterator

from mcp.server import Server
from mcp.types import Tool as tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("dev_sentinel_mcp")

class DevSentinelContext:
    def __init__(self):
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        self.force_processor = None

    async def ensure_initialized(self):
        if self._initialized:
            return
        async with self._initialization_lock:
            if self._initialized:
                return
            # TODO: Initialize force_processor, etc.
            self._initialized = True
            logger.info("Dev Sentinel MCP server initialized.")

class DevSentinelMCPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8090):
        self.server = Server("dev_sentinel_command")
        self.host = host
        self.port = port
        self.context = DevSentinelContext()
        self._setup_server()

    def _setup_server(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[tool]:
            return [
                tool(
                    name="execute_command",
                    description="Execute a Dev Sentinel command.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command type to execute (e.g., VIC, CODE, VCS)"},
                            "args": {"type": "object", "description": "Command arguments as a JSON object"}
                        },
                        "required": ["command", "args"]
                    }
                ),
                tool(
                    name="stream_command",
                    description="Execute a Dev Sentinel command and stream the results.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command type to execute (e.g., VIC, CODE, VCS)"},
                            "args": {"type": "object", "description": "Command arguments as a JSON object"}
                        },
                        "required": ["command", "args"]
                    }
                ),
                tool(
                    name="get_commands",
                    description="Get the list of available Dev Sentinel commands.",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> Any:
            arguments = arguments or {}
            if name == "execute_command":
                command = arguments.get("command") or ""
                args_ = arguments.get("args", {})
                result = await self.execute_command(command, args_)
                return result
            elif name == "stream_command":
                command = arguments.get("command") or ""
                args_ = arguments.get("args", {})
                return [frame async for frame in self.stream_command(command, args_)]
            elif name == "get_commands":
                result = await self.get_commands()
                return result
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def execute_command(self, command: str, args: dict):
        try:
            await self.context.ensure_initialized()
            # For now, just echo the command and args as a result
            result = {"executed": True, "command": command, "args": args}
            return {"success": True, "result": result}
        except Exception as e:
            logger.exception(f"Error executing command: {e}")
            return {"success": False, "error": str(e)}

    async def stream_command(self, command: str, args: dict):
        yield {"frame": 1, "command": command, "args": args}

    async def get_commands(self):
        try:
            commands = [
                {"command": "VIC", "description": "Version/Integration Command", "args": {}},
                {"command": "CODE", "description": "Code Command", "args": {}},
                {"command": "VCS", "description": "Version Control Command", "args": {}},
                {"command": "DIAGRAM", "description": "Generate diagram", "args": {"type": "Diagram type (ARCH, FLOW, COMP, TERM, EXTRACT)", "source": "Source data (FILE=path, FORCE, YUNG, AGENT)", "format": "Output format (svg, png, pdf)"}},
                {"command": "MAN", "description": "Display YUNG command manual", "args": {}}
            ]
            return {"success": True, "commands": commands}
        except Exception as e:
            logger.exception(f"Error getting commands: {e}")
            return {"success": False, "error": str(e)}

    async def run(self):
        from mcp.server import stdio
        from mcp.server.models import InitializationOptions
        class NotificationOptionsStub:
            tools_changed = False
        notification_options = NotificationOptionsStub()
        capabilities = self.server.get_capabilities(
            notification_options=notification_options,
            experimental_capabilities={}
        )
        async with stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dev_sentinel_command",
                    server_version="1.0.0",
                    capabilities=capabilities
                )
            )

def is_running_in_event_loop():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False

async def start_server(host: str = "0.0.0.0", port: int = 8090, *args, **kwargs):
    """Entry point for starting the Dev Sentinel MCP server (for import)."""
    server = DevSentinelMCPServer(host=host, port=port)
    await server.run()

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Start Dev Sentinel MCP server (Server)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8090, help="Port to listen on")
    args = parser.parse_args()
    server = DevSentinelMCPServer(host=args.host, port=args.port)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())