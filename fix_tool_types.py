#!/usr/bin/env python3
"""
Script to fix tool JSON files by adding missing "type": "tool" field.
"""

import json
import os
from pathlib import Path

def fix_tool_json_files():
    """Fix all tool JSON files by adding the missing type field."""
    tools_dir = Path(".force/tools")
    
    if not tools_dir.exists():
        print(f"Tools directory {tools_dir} does not exist")
        return
    
    fixed_files = []
    
    for json_file in tools_dir.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Check if it's a single tool definition
            if isinstance(data, dict) and "id" in data and "type" not in data:
                # Add the type field
                data["type"] = "tool"
                
                # Write back to file
                with open(json_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                fixed_files.append(str(json_file))
                print(f"Fixed: {json_file}")
            
            # Check if it's a multi-tool file
            elif isinstance(data, dict) and "tools" in data:
                tools_list = data.get("tools", [])
                modified = False
                
                for tool in tools_list:
                    if isinstance(tool, dict) and "id" in tool and "type" not in tool:
                        tool["type"] = "tool"
                        modified = True
                
                if modified:
                    with open(json_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    fixed_files.append(str(json_file))
                    print(f"Fixed multi-tool file: {json_file}")
            
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    print(f"\nFixed {len(fixed_files)} files:")
    for file in fixed_files:
        print(f"  - {file}")

if __name__ == "__main__":
    fix_tool_json_files()
