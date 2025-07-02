#!/usr/bin/env python3
"""
Dev Sentinel MCP stdio server entry point.

This module provides the CLI entry point for the Dev Sentinel MCP server using stdio transport.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path to ensure proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from integration.fast_agent.dev_sentinel_server import main as dev_sentinel_main


def main():
    """Entry point for dev-sentinel-stdio CLI command."""
    try:
        asyncio.run(dev_sentinel_main())
    except KeyboardInterrupt:
        print("\n🛑 Dev Sentinel server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Dev Sentinel server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
