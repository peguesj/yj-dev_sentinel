#!/usr/bin/env python3
"""
Force Tools Validation Report
Validates all Force tool JSON files and provides a compliance report.
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
import os
from pathlib import Path

def validate_tool_file(tool_path, schema_data):
    """Validate a single tool file against the Force schema."""
    try:
        with open(tool_path, 'r', encoding='utf-8') as f:
            tool_data = json.load(f)
        
        # Validate against the schema
        validate(instance=tool_data, schema=schema_data['definitions']['ToolDefinition'], 
                resolver=jsonschema.RefResolver.from_schema(schema_data))
        return True, None
        
    except ValidationError as e:
        return False, e.message
    except Exception as e:
        return False, str(e)

def main():
    """Generate validation report for all Force tools."""
    base_path = Path("/Users/jeremiah/Developer/dev_sentinel")
    schema_path = base_path / ".force" / "schemas" / "force-schema.json"
    tools_path = base_path / ".force" / "tools"
    
    print("🔍 FORCE TOOLS VALIDATION REPORT")
    print("=" * 60)
    
    # Load schema
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        return
    
    # Find all JSON files in tools directory
    json_files = list(tools_path.glob("*.json"))
    
    valid_tools = []
    invalid_tools = []
    
    print(f"📊 Found {len(json_files)} tool JSON files to validate\n")
    
    for tool_file in sorted(json_files):
        tool_name = tool_file.name
        is_valid, error_msg = validate_tool_file(tool_file, schema_data)
        
        if is_valid:
            valid_tools.append(tool_name)
            print(f"✅ {tool_name:<40} VALID")
        else:
            invalid_tools.append((tool_name, error_msg))
            print(f"❌ {tool_name:<40} INVALID")
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total tools: {len(json_files)}")
    print(f"Valid tools: {len(valid_tools)} ({len(valid_tools)/len(json_files)*100:.1f}%)")
    print(f"Invalid tools: {len(invalid_tools)} ({len(invalid_tools)/len(json_files)*100:.1f}%)")
    
    if invalid_tools:
        print(f"\n❌ INVALID TOOLS ({len(invalid_tools)}):")
        for tool_name, error in invalid_tools[:10]:  # Show first 10 errors
            short_error = error[:80] + "..." if len(error) > 80 else error
            print(f"  • {tool_name}: {short_error}")
        if len(invalid_tools) > 10:
            print(f"  ... and {len(invalid_tools) - 10} more")
    
    if valid_tools:
        print(f"\n✅ VALID TOOLS ({len(valid_tools)}):")
        for tool_name in valid_tools[:10]:  # Show first 10
            print(f"  • {tool_name}")
        if len(valid_tools) > 10:
            print(f"  ... and {len(valid_tools) - 10} more")

if __name__ == "__main__":
    main()
