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


import logging
logger = logging.getLogger("force_mcp_stdio")
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def format_validation_report(report):
    lines = []
    lines.append(Fore.CYAN + Style.BRIGHT + "🔍 FORCE COMPONENT VALIDATION REPORT")
    lines.append("=" * 80)
    lines.append(f"Validation Time: {report.get('validation_time', 'N/A')}")
    lines.append(f"Schema Path: {report.get('schema_path', 'N/A')}")
    lines.append("")
    lines.append(Fore.YELLOW + "📊 VALIDATION SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Total Components: {report.get('total_components', 'N/A')}")
    lines.append(f"Valid Components: {report.get('valid_components', 'N/A')}")
    lines.append(f"Invalid Components: {report.get('invalid_components', 'N/A')}")
    ready_for_loading = report.get('ready_for_loading', False)
    ready_color = Fore.GREEN if ready_for_loading else Fore.RED
    ready_text = "YES" if ready_for_loading else "NO"
    lines.append(f"Ready for Loading: {ready_color}{ready_text}")
    lines.append("")
    lines.append(Fore.YELLOW + "🔧 TOOLS")
    lines.append("-" * 40)
    for tool in report.get('invalid_tools', []):
        lines.append(Fore.RED + f"❌ Invalid tool: {tool.get('full_path', tool.get('path', 'Unknown'))} (Project: {tool.get('is_project', 'Unknown')}) - {tool.get('error', 'No error info')}")
    lines.append("")
    lines.append(Fore.YELLOW + "🔧 PATTERNS")
    lines.append("-" * 40)
    for pattern in report.get('invalid_patterns', []):
        lines.append(Fore.RED + f"❌ Invalid pattern: {pattern.get('full_path', pattern.get('path', 'Unknown'))} (Project: {pattern.get('is_project', 'Unknown')}) - {pattern.get('error', 'No error info')}")
    lines.append("")
    lines.append(Fore.YELLOW + "🔧 CONSTRAINTS")
    lines.append("-" * 40)
    for constraint in report.get('invalid_constraints', []):
        lines.append(Fore.RED + f"❌ Invalid constraint: {constraint.get('full_path', constraint.get('path', 'Unknown'))} (Project: {constraint.get('is_project', 'Unknown')}) - {constraint.get('error', 'No error info')}")
    lines.append("")
    lines.append(Fore.YELLOW + "🔧 GOVERNANCE")
    lines.append("-" * 40)
    for governance in report.get('invalid_governance', []):
        lines.append(Fore.RED + f"❌ Invalid governance: {governance.get('full_path', governance.get('path', 'Unknown'))} (Project: {governance.get('is_project', 'Unknown')}) - {governance.get('error', 'No error info')}")
    lines.append("")
    return "\n".join(lines)

def main():
    """Entry point for force-mcp-stdio CLI command."""
    import asyncio
    try:
        # ANCHOR: Docu-Commentary - Logging Setup
        logging.basicConfig(level=logging.DEBUG)
        # Run the main MCP server function and get validation report
        validation_report = asyncio.run(force_mcp_main())
        # ANCHOR: Docu-Commentary - Validation Report Output
        logger.info("Validation report follows:")
        logger.info(format_validation_report(validation_report))
        # ANCHOR: Docu-Commentary - Validation Summary
        if validation_report:
            valid_tools = validation_report.get('valid_tools', [])
            invalid_tools = validation_report.get('invalid_tools', [])
            logger.info(f"Loaded {len(valid_tools)} valid tools, {len(invalid_tools)} invalid tools.")
    except KeyboardInterrupt:
        # ANCHOR: Docu-Commentary - Server Stop
        logger.info("Force MCP server stopped by user")
        sys.exit(0)
    except Exception as e:
        # ANCHOR: Error Handling - Unhandled Exception
        logger.error(f"Force MCP server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
