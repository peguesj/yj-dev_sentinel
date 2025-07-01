#!/usr/bin/env python
"""
Simple script to view FORCE tools and modules

This script loads the FORCE engine and displays information about available tools,
patterns, and constraints.
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

# Add project root to path
try:
    import path_setup
    logger.info(f"Set up Python path: {path_setup.project_root}")
except ImportError:
    logger.error("Failed to import path_setup module")
    sys.exit(1)

# Import Force engine
try:
    from force import ForceEngine
    logger.info("Successfully imported ForceEngine")
except ImportError as e:
    logger.error(f"Failed to import ForceEngine: {e}")
    sys.exit(1)

def print_section(title, items):
    """Print a section with a title and items."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)
    
    for i, item in enumerate(items, 1):
        print(f"{i}. {item}")
    
    if not items:
        print("No items found.")

def main():
    """Main function to display FORCE tools and modules."""
    try:
        # Initialize FORCE engine
        logger.info("Initializing FORCE engine...")
        force_engine = ForceEngine()
        logger.info("FORCE engine initialized successfully")
        
        # Print FORCE directory locations
        print_section("FORCE Directory Locations", [
            f"FORCE Dir: {force_engine.force_dir}",
            f"Schemas Dir: {force_engine.schemas_dir}",
            f"Tools Dir: {force_engine.tools_dir}",
            f"Patterns Dir: {force_engine.patterns_dir}",
            f"Constraints Dir: {force_engine.constraints_dir}",
            f"Learning Dir: {force_engine.learning_dir}",
            f"Governance Dir: {force_engine.governance_dir}"
        ])
        
        # Load and display tools
        logger.info("Loading tools...")
        tools = force_engine.load_tools()
        tool_info = [f"{tool_id}: {tool.get('name', 'Unnamed')} - {tool.get('description', 'No description')}" 
                     for tool_id, tool in tools.items()]
        print_section("Available Tools", tool_info)
        
        # Load and display patterns
        logger.info("Loading patterns...")
        patterns = force_engine.load_patterns()
        pattern_info = [f"{pattern_id}: {pattern.get('name', 'Unnamed')} - {pattern.get('description', 'No description')}" 
                       for pattern_id, pattern in patterns.items()]
        print_section("Available Patterns", pattern_info)
        
        # Load and display constraints
        logger.info("Loading constraints...")
        constraints = force_engine.load_constraints()
        constraint_info = [f"{constraint_id}: {constraint.get('name', 'Unnamed')} - {constraint.get('description', 'No description')}" 
                          for constraint_id, constraint in constraints.items()]
        print_section("Available Constraints", constraint_info)
        
        # If available, also show tool registry info
        if hasattr(force_engine, 'tool_registry') and force_engine.tool_registry:
            try:
                available_tools = force_engine.tool_registry.get_available_tools()
                registry_info = [f"{tool['id']}: {tool['name']} - {tool['description']}" 
                               for tool in available_tools]
                print_section("Tool Registry", registry_info)
            except Exception as e:
                logger.error(f"Error getting registry tools: {e}")
                
        # If available, also show constraint registry info
        if hasattr(force_engine, 'constraint_registry') and force_engine.constraint_registry:
            try:
                available_constraints = force_engine.constraint_registry.get_available_constraints()
                constraint_registry_info = [f"{constraint['id']}: {constraint['name']} - {constraint['description']}" 
                                          for constraint in available_constraints]
                print_section("Constraint Registry", constraint_registry_info)
            except Exception as e:
                logger.error(f"Error getting registry constraints: {e}")
        
    except Exception as e:
        logger.error(f"Error initializing or using FORCE engine: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
