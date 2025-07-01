#!/usr/bin/env python
"""
FORCE Tool Viewer (Schema-Aware)

Displays detailed information about FORCE tools, parsing all fields as defined in the schema.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("force_tools_viewer")

TOOLS_DIR = Path(__file__).parent.parent / ".force" / "tools"


def print_section(title, items=None):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)
    if items:
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
    elif items is not None:
        print("No items found.")


def print_parameters(params):
    if not params:
        print("  None")
        return
    for param in params:
        name = param.get("name", "<unnamed>")
        typ = param.get("type", "<type?>")
        desc = param.get("description", "")
        default = param.get("default", None)
        validation = param.get("validation", {})
        print(f"  - {name} ({typ}): {desc}")
        if validation:
            vstr = ", ".join(f"{k}={v}" for k, v in validation.items())
            print(f"    Validation: {vstr}")
        if default is not None:
            print(f"    Default: {default}")


def print_execution(exec_block):
    if not exec_block:
        print("  None")
        return
    print(f"Strategy: {exec_block.get('strategy', 'N/A')}")
    cmds = exec_block.get("commands", [])
    if cmds:
        print("Commands:")
        for i, cmd in enumerate(cmds, 1):
            action = cmd.get("action", "<action?>")
            desc = cmd.get("description", "")
            params = cmd.get("parameters", {})
            print(f"  {i}. {action}: {desc}")
            if params:
                pstr = ", ".join(f"{k}={v}" for k, v in params.items())
                print(f"     Parameters: {pstr}")
    val = exec_block.get("validation", {})
    if val:
        print("Validation:")
        for k, v in val.items():
            print(f"  {k}: {v}")


def print_metadata(meta):
    if not meta:
        print("  None")
        return
    for k, v in meta.items():
        print(f"  {k}: {v}")


def print_tool(tool):
    print_section(f"{tool.get('name', '<unnamed>')} ({tool.get('id', '<id?>')})")
    print(f"Category: {tool.get('category', 'N/A')}")
    print(f"Description: {tool.get('description', '')}")
    # Parameters
    params = tool.get("parameters", {})
    print("\n-- Parameters --")
    if params.get("required"):
        print("Required:")
        print_parameters(params["required"])
    if params.get("optional"):
        print("Optional:")
        print_parameters(params["optional"])
    # Execution
    print("\n-- Execution --")
    print_execution(tool.get("execution", {}))
    # Metadata
    print("\n-- Metadata --")
    print_metadata(tool.get("metadata", {}))


def main():
    logger.info(f"Looking for FORCE tool definitions in {TOOLS_DIR}")
    if not TOOLS_DIR.exists():
        logger.error(f"Tools directory not found: {TOOLS_DIR}")
        sys.exit(1)
    for toolfile in TOOLS_DIR.glob("*.json"):
        logger.info(f"Parsing {toolfile.name}")
        with open(toolfile, "r") as f:
            try:
                data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to parse {toolfile}: {e}")
                continue
        # Some files have a 'tools' array, others are single tool objects
        if isinstance(data, dict) and "tools" in data:
            for tool in data["tools"]:
                print_tool(tool)
        else:
            print_tool(data)

if __name__ == "__main__":
    main()
