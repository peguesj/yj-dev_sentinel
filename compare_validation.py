#!/usr/bin/env python3

import json
import jsonschema
from jsonschema import validate, ValidationError
import sys

def compare_tools_validation():
    """Compare validation of incomplete vs complete Force tools"""
    
    print("🔍 FORCE TOOL VALIDATION COMPARISON")
    print("=" * 80)
    
    schema_file = ".force/schemas/force-schema.json"
    incomplete_tool = "force/tools/analyze-code-changes.json"  # Incomplete
    complete_tool = ".force/tools/secrets-scan.json"          # Complete
    
    # Load schema
    with open(schema_file, 'r') as f:
        schema = json.load(f)
    tool_schema = schema['definitions']['ToolDefinition']
    
    print("1️⃣ INCOMPLETE TOOL (force/tools/analyze-code-changes.json):")
    print("-" * 60)
    
    try:
        with open(incomplete_tool, 'r') as f:
            incomplete_data = json.load(f)
        
        print(f"Fields present: {list(incomplete_data.keys())}")
        
        try:
            validate(instance=incomplete_data, schema=tool_schema)
            print("✅ VALIDATION: PASSED")
        except ValidationError as e:
            print(f"❌ VALIDATION: FAILED - {e.message}")
            
        missing_fields = [field for field in tool_schema['required'] if field not in incomplete_data]
        print(f"Missing required fields: {missing_fields}")
        
    except Exception as e:
        print(f"Error processing incomplete tool: {e}")
    
    print("\n2️⃣ COMPLETE TOOL (.force/tools/secrets-scan.json):")
    print("-" * 60)
    
    try:
        with open(complete_tool, 'r') as f:
            complete_data = json.load(f)
        
        print(f"Fields present: {list(complete_data.keys())}")
        
        try:
            validate(instance=complete_data, schema=tool_schema)
            print("✅ VALIDATION: PASSED")
            
            # Show structure details
            print("\nStructure details:")
            print(f"  - Parameters: {len(complete_data.get('parameters', {}).get('required', []))} required, {len(complete_data.get('parameters', {}).get('optional', []))} optional")
            print(f"  - Execution strategy: {complete_data.get('execution', {}).get('strategy', 'N/A')}")
            print(f"  - Commands: {len(complete_data.get('execution', {}).get('commands', []))}")
            print(f"  - Complexity: {complete_data.get('metadata', {}).get('complexity', 'N/A')}")
            print(f"  - Tags: {complete_data.get('metadata', {}).get('tags', [])}")
            
        except ValidationError as e:
            print(f"❌ VALIDATION: FAILED - {e.message}")
            
        missing_fields = [field for field in tool_schema['required'] if field not in complete_data]
        print(f"Missing required fields: {missing_fields}")
        
    except Exception as e:
        print(f"Error processing complete tool: {e}")
    
    print("\n🎯 SUMMARY:")
    print("=" * 80)
    print("The incomplete tool in force/tools/ lacks the comprehensive structure")
    print("required by the Force schema, while the complete tool in .force/tools/")
    print("follows the full schema with all required components.")
    print()
    print("✅ Complete tools have: parameters, execution, metadata")
    print("❌ Incomplete tools missing: execution strategy, metadata, proper parameter structure")

if __name__ == "__main__":
    compare_tools_validation()
