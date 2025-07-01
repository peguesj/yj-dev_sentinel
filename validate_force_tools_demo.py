#!/usr/bin/env python3
"""
Force Tool Validation Demo
Demonstrates validation of Force tool JSON files against the Force schema.
Shows the difference between complete and incomplete tool definitions.
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
import os
from pathlib import Path

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def validate_tool_against_schema(tool_data, schema_data, tool_name):
    """Validate a tool definition against the Force schema."""
    print(f"\n{'='*60}")
    print(f"VALIDATING: {tool_name}")
    print(f"{'='*60}")
    
    try:
        # Validate against the full schema with ToolDefinition
        validate(instance=tool_data, schema=schema_data['definitions']['ToolDefinition'], resolver=jsonschema.RefResolver.from_schema(schema_data))
        print(f"✅ {tool_name} is VALID according to Force schema")
        return True
        
    except ValidationError as e:
        print(f"❌ {tool_name} is INVALID according to Force schema")
        print(f"\nValidation Error Details:")
        print(f"  Path: {' -> '.join(str(x) for x in e.absolute_path)}")
        print(f"  Message: {e.message}")
        
        if e.validator == 'required':
            missing_fields = e.validator_value
            print(f"  Missing required fields: {missing_fields}")
        
        # Show specific validation issues
        if 'execution' in tool_data and e.absolute_path and e.absolute_path[0] == 'execution':
            print(f"  Issue in execution section: {e.message}")
        elif 'metadata' in tool_data and e.absolute_path and e.absolute_path[0] == 'metadata':
            print(f"  Issue in metadata section: {e.message}")
        elif 'parameters' in tool_data and e.absolute_path and e.absolute_path[0] == 'parameters':
            print(f"  Issue in parameters section: {e.message}")
        
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error validating {tool_name}: {e}")
        return False

def analyze_tool_completeness(tool_data, tool_name):
    """Analyze the completeness of a tool definition."""
    print(f"\n📊 COMPLETENESS ANALYSIS: {tool_name}")
    print("-" * 40)
    
    required_fields = ['id', 'name', 'category', 'description', 'parameters', 'execution', 'metadata']
    present_fields = []
    missing_fields = []
    
    for field in required_fields:
        if field in tool_data:
            present_fields.append(field)
        else:
            missing_fields.append(field)
    
    print(f"Present fields ({len(present_fields)}/{len(required_fields)}): {', '.join(present_fields)}")
    if missing_fields:
        print(f"Missing fields: {', '.join(missing_fields)}")
    
    # Check nested required fields
    if 'execution' in tool_data:
        execution = tool_data['execution']
        exec_required = ['strategy', 'commands', 'validation']
        exec_present = [f for f in exec_required if f in execution]
        exec_missing = [f for f in exec_required if f not in execution]
        print(f"Execution fields ({len(exec_present)}/{len(exec_required)}): {', '.join(exec_present)}")
        if exec_missing:
            print(f"Missing execution fields: {', '.join(exec_missing)}")
    
    if 'metadata' in tool_data:
        metadata = tool_data['metadata']
        meta_required = ['created', 'updated', 'version', 'complexity']
        meta_present = [f for f in meta_required if f in metadata]
        meta_missing = [f for f in meta_required if f not in metadata]
        print(f"Metadata fields ({len(meta_present)}/{len(meta_required)}): {', '.join(meta_present)}")
        if meta_missing:
            print(f"Missing metadata fields: {', '.join(meta_missing)}")

def main():
    """Main validation demo."""
    base_path = Path("/Users/jeremiah/Developer/dev_sentinel")
    schema_path = base_path / ".force" / "schemas" / "force-schema.json"
    tools_path = base_path / ".force" / "tools"
    
    print("🔍 FORCE TOOL VALIDATION DEMO")
    print("=" * 60)
    print("This demo validates Force tool JSON files against the Force schema.")
    print("We'll compare a complete tool vs. an incomplete tool.")
    
    # Load the Force schema
    print(f"\n📋 Loading Force schema from: {schema_path}")
    schema_data = load_json_file(schema_path)
    if not schema_data:
        print("❌ Failed to load Force schema!")
        return
    
    print("✅ Force schema loaded successfully")
    
    # Test tools
    test_tools = [
        {
            "file": "secrets-scan.json",
            "description": "Complete tool with all required fields"
        },
        {
            "file": "code-quality-check.json", 
            "description": "Incomplete tool missing required fields"
        }
    ]
    
    validation_results = []
    
    for tool_info in test_tools:
        tool_file = tool_info["file"]
        tool_path = tools_path / tool_file
        
        print(f"\n🔧 Loading tool: {tool_file}")
        print(f"   Description: {tool_info['description']}")
        
        tool_data = load_json_file(tool_path)
        if not tool_data:
            continue
        
        print(f"✅ Tool loaded successfully")
        
        # Analyze completeness
        analyze_tool_completeness(tool_data, tool_file)
        
        # Validate against schema
        is_valid = validate_tool_against_schema(tool_data, schema_data, tool_file)
        validation_results.append({
            "tool": tool_file,
            "valid": is_valid,
            "description": tool_info["description"]
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    for result in validation_results:
        status = "✅ VALID" if result["valid"] else "❌ INVALID"
        print(f"{result['tool']:<30} {status}")
        print(f"  → {result['description']}")
    
    print(f"\n🎯 KEY TAKEAWAYS:")
    print("  • Complete tools with all required fields pass validation")
    print("  • Incomplete tools fail validation and show specific missing fields")
    print("  • The Force schema enforces consistent tool structure and metadata")
    print("  • Validation helps maintain quality and compatibility across the Force system")

if __name__ == "__main__":
    main()
