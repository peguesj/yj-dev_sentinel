#!/usr/bin/env python
"""
This script displays the git workflow tools from the FORCE system,
parsing the specific format found in the git-workflow-tools.json file.
"""

import os
import sys
import json
from pathlib import Path

def print_section_header(title):
    """Print a section header with the given title."""
    print("=" * 80)
    print(f"{title:^80}")
    print("=" * 80)

def main():
    # Find the .force directory
    force_dir = Path(os.path.expanduser("~")) / "Developer" / "dev_sentinel" / ".force"
    
    if not force_dir.exists():
        print(f"FORCE directory not found at {force_dir}")
        return 1
    
    # Print directory locations
    print_section_header("FORCE Directory Locations")
    print(f"1. FORCE Dir: {force_dir}")
    print(f"2. Schemas Dir: {force_dir / 'schemas'}")
    print(f"3. Tools Dir: {force_dir / 'tools'}")
    print(f"4. Patterns Dir: {force_dir / 'patterns'}")
    print(f"5. Constraints Dir: {force_dir / 'constraints'}")
    print(f"6. Learning Dir: {force_dir / 'learning'}")
    print(f"7. Governance Dir: {force_dir / 'governance'}")
    
    # Look specifically for git-related tools
    print_section_header("Git Tools")
    git_tools_path = force_dir / "tools" / "git-workflow-tools.json"
    
    if git_tools_path.exists():
        try:
            with open(git_tools_path, "r") as f:
                git_tools_data = json.load(f)
                
            if "tools" in git_tools_data:
                for i, tool in enumerate(git_tools_data.get("tools", []), 1):
                    tool_id = tool.get("id", "unnamed")
                    description = tool.get("description", "No description")
                    print(f"{i}. {tool_id}: {description}")
                    
                    # Show parameters
                    required_params = tool.get("parameters", {}).get("required", [])
                    optional_params = tool.get("parameters", {}).get("optional", [])
                    
                    if required_params or optional_params:
                        print(f"   Parameters:")
                        
                        for param in required_params:
                            param_name = param.get("name", "unnamed")
                            param_type = param.get("type", "unknown")
                            param_desc = param.get("description", "No description")
                            print(f"     - {param_name} ({param_type}, REQUIRED): {param_desc}")
                            
                        for param in optional_params:
                            param_name = param.get("name", "unnamed")
                            param_type = param.get("type", "unknown")
                            param_desc = param.get("description", "No description")
                            default = param.get("default", "No default")
                            print(f"     - {param_name} ({param_type}): {param_desc} [Default: {default}]")
                    
                    print()  # Empty line for readability
            else:
                print("No tools found in git-workflow-tools.json (Expected 'tools' key)")
        except json.JSONDecodeError:
            print(f"Error: Unable to parse {git_tools_path} as JSON")
        except Exception as e:
            print(f"Error loading {git_tools_path}: {str(e)}")
    else:
        print(f"Git tools file not found at {git_tools_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
