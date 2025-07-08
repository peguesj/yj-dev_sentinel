#!/usr/bin/env python3

import json
import jsonschema
from jsonschema import validate, ValidationError
import sys

def detailed_validation_analysis(tool_file, schema_file):
    """Provide detailed analysis of Force tool validation"""
    
    print(f"🔍 DETAILED FORCE TOOL VALIDATION ANALYSIS")
    print(f"Tool: {tool_file}")
    print(f"Schema: {schema_file}")
    print("=" * 80)
    
    try:
        # Load files
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        with open(tool_file, 'r') as f:
            tool_data = json.load(f)
        
        tool_schema = schema['definitions']['ToolDefinition']
        
        print("📋 SCHEMA REQUIREMENTS:")
        print(f"Required fields: {tool_schema['required']}")
        print()
        
        print("📁 CURRENT TOOL STRUCTURE:")
        for key, value in tool_data.items():
            print(f"  ✅ {key}: {type(value).__name__}")
        print()
        
        print("❌ MISSING REQUIRED FIELDS:")
        missing_fields = []
        for field in tool_schema['required']:
            if field not in tool_data:
                missing_fields.append(field)
                print(f"  - {field}")
        
        if not missing_fields:
            print("  None - all required fields present!")
        print()
        
        print("🔧 FIELD-BY-FIELD ANALYSIS:")
        for field in tool_schema['required']:
            if field in tool_data:
                print(f"  ✅ {field}: Present")
            else:
                print(f"  ❌ {field}: MISSING")
                
                # Show what this field should contain
                if field in tool_schema['properties']:
                    field_def = tool_schema['properties'][field]
                    print(f"      Expected: {field_def.get('description', 'No description')}")
                    if 'type' in field_def:
                        print(f"      Type: {field_def['type']}")
                    if 'required' in field_def and field_def['type'] == 'object':
                        print(f"      Required subfields: {field_def['required']}")
        print()
        
        print("💡 FORCE SCHEMA COMPLIANCE REQUIREMENTS:")
        print("To make this tool compliant, it needs:")
        print()
        
        if 'parameters' not in tool_data or not isinstance(tool_data.get('parameters'), dict):
            print("1. 📝 PARAMETERS object with:")
            print("   - required: array of Parameter objects")
            print("   - optional: array of Parameter objects")
            print("   - Each Parameter needs: name, type, description")
        
        if 'execution' not in tool_data:
            print("2. ⚙️ EXECUTION object with:")
            print("   - strategy: 'sequential'|'parallel'|'conditional'|'iterative'")
            print("   - commands: array of Command objects")
            print("   - validation: object with pre_conditions, post_conditions, error_handling")
        
        if 'metadata' not in tool_data:
            print("3. 📊 METADATA object with:")
            print("   - created: ISO datetime string")
            print("   - updated: ISO datetime string") 
            print("   - version: semantic version (x.y.z)")
            print("   - complexity: 'low'|'medium'|'high'|'expert'")
            print("   - tags: array of strings")
            print("   - dependencies: array of strings")
            print("   - performance_metrics: object with avg_execution_time, success_rate, usage_count")
        
        print()
        print("🚨 CURRENT TOOL STATUS: INCOMPLETE")
        print("This tool needs to be completed to match Force schema requirements.")
        
        return missing_fields
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return []

if __name__ == "__main__":
    tool_file = "force/tools/analyze-code-changes.json"
    schema_file = ".force/schemas/force-schema.json"
    
    missing = detailed_validation_analysis(tool_file, schema_file)
