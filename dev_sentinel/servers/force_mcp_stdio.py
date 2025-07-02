#!/usr/bin/env python3
"""
Force MCP stdio server entry point.

This module provides the CLI entry point for the Force MCP server using stdio transport.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path to ensure proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integration.fast_agent.force_mcp_server import main as force_mcp_main


def main():
    """Entry point for force-mcp-stdio CLI command."""
    try:
        asyncio.run(force_mcp_main())
    except KeyboardInterrupt:
        print("\n🛑 Force MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Force MCP server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
