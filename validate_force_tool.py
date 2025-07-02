#!/usr/bin/env python3

import json
import jsonschema
from jsonschema import validate, ValidationError
import sys

def validate_force_tool(tool_file, schema_file):
    """Validate a Force tool definition against the Force schema"""
    
    print(f"🔍 Validating Force Tool: {tool_file}")
    print(f"📋 Using Schema: {schema_file}")
    print("=" * 60)
    
    try:
        # Load the schema
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        # Load the tool definition
        with open(tool_file, 'r') as f:
            tool_data = json.load(f)
        
        print(f"✅ Successfully loaded files")
        print(f"🔧 Tool ID: {tool_data.get('id', 'Unknown')}")
        print(f"📝 Tool Name: {tool_data.get('name', 'Unknown')}")
        print(f"📂 Category: {tool_data.get('category', 'Unknown')}")
        print()
        
        # Validate against ToolDefinition schema
        tool_schema = schema['definitions']['ToolDefinition']
        
        print("🚀 Running validation...")
        validate(instance=tool_data, schema=tool_schema)
        
        print("✅ VALIDATION PASSED!")
        print("The tool definition is valid according to the Force schema.")
        
        # Additional analysis
        print("\n📊 ANALYSIS:")
        print(f"- Required fields present: {all(field in tool_data for field in tool_schema['required'])}")
        print(f"- Has parameters: {'parameters' in tool_data}")
        print(f"- Has execution strategy: {'execution' in tool_data}")
        print(f"- Has metadata: {'metadata' in tool_data}")
        
        return True
        
    except ValidationError as e:
        print("❌ VALIDATION FAILED!")
        print(f"Error: {e.message}")
        print(f"Failed at: {e.json_path}")
        if e.schema_path:
            print(f"Schema path: {e.schema_path}")
        
        # Provide helpful suggestions
        print("\n💡 SUGGESTIONS:")
        if "required" in str(e):
            missing_fields = []
            for field in tool_schema['required']:
                if field not in tool_data:
                    missing_fields.append(field)
            if missing_fields:
                print(f"- Missing required fields: {', '.join(missing_fields)}")
        
        return False
        
    except FileNotFoundError as e:
        print(f"❌ FILE ERROR: {e}")
        return False
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    tool_file = "force/tools/analyze-code-changes.json"
    schema_file = ".force/schemas/force-schema.json"
    
    success = validate_force_tool(tool_file, schema_file)
    sys.exit(0 if success else 1)
