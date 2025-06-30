# Constraint Development Guide

This guide explains how to create and register custom constraints in the FORCE system.

## Understanding Constraints

FORCE constraints define quality rules and validation checks. A constraint consists of:

1. **Validator**: Logic that checks whether the constraint is met
2. **Metadata**: Information about the constraint (ID, name, description)
3. **Violation Reporting**: Mechanism to report and describe violations

## Creating Constraints Programmatically

### Step 1: Import Required Classes

```python
from force.constraints import BaseConstraintValidator, ConstraintViolation
```

### Step 2: Create a Constraint Validator

You can create a constraint validator by extending the `BaseConstraintValidator` class:

```python
class FunctionLengthValidator(BaseConstraintValidator):
    constraint_id = "code-quality-function-length"
    constraint_name = "Function Length"
    constraint_description = "Ensures that functions are not too long."
    
    def __init__(self, force_engine, max_lines=50):
        super().__init__(force_engine)
        self.max_lines = max_lines
    
    async def validate(self, context):
        violations = []
        file_path = context.get("file_path")
        functions = await self.force_engine.execute_tool("code-analyzer", {
            "file_path": file_path,
            "analysis_type": "functions"
        })
        
        for function in functions:
            if function["line_count"] > self.max_lines:
                violations.append(ConstraintViolation(
                    constraint_id=self.constraint_id,
                    message=f"Function '{function['name']}' is too long ({function['line_count']} lines > {self.max_lines})",
                    location=f"{file_path}:{function['start_line']}-{function['end_line']}",
                    severity="warning",
                    auto_fixable=False
                ))
        
        return violations
```

### Step 3: Register the Constraint

Register your constraint in your module's initialization code:

```python
from force.constraints import ConstraintRegistry

def register_constraints():
    ConstraintRegistry.register(FunctionLengthValidator.constraint_id, FunctionLengthValidator)
    
register_constraints()
```

## Creating Constraints with JSON

You can also define constraints using JSON files placed in the `force/constraints` directory:

```json
{
  "constraint_id": "documentation-module-docstring",
  "name": "Module Docstring",
  "description": "Ensures that each module has a docstring",
  "severity": "warning",
  "auto_fixable": false,
  "validator": {
    "type": "regex",
    "pattern": "^\\s*\"\"\"[\\s\\S]+?\"\"\"",
    "file_pattern": "*.py",
    "message": "Module is missing a docstring"
  }
}
```

For more complex constraints, you can define multiple validators in a single JSON file:

```json
{
  "constraints": [
    {
      "constraint_id": "naming-snake-case",
      "name": "Snake Case Variables",
      "description": "Ensures that variables use snake_case naming convention",
      "severity": "warning",
      "auto_fixable": true,
      "validator": {
        "type": "regex",
        "pattern": "\\b[a-z][a-z0-9_]*\\b",
        "match_type": "inverse",
        "file_pattern": "*.py",
        "target": "variables",
        "message": "Variable name should use snake_case"
      }
    },
    {
      "constraint_id": "naming-camel-case-classes",
      "name": "CamelCase Classes",
      "description": "Ensures that class names use CamelCase naming convention",
      "severity": "warning",
      "auto_fixable": true,
      "validator": {
        "type": "regex",
        "pattern": "\\bclass\\s+[A-Z][a-zA-Z0-9]*\\b",
        "match_type": "required",
        "file_pattern": "*.py",
        "message": "Class name should use CamelCase"
      }
    }
  ]
}
```

## Constraint Validator Types

### Custom Validators

Custom validators provide the most flexibility and are defined by extending the `BaseConstraintValidator` class.

### Built-in Validators

The FORCE system includes several built-in validator types:

1. **Regex Validator**: Validates content against regular expressions
2. **Pattern Validator**: Checks for specific patterns in code
3. **Tool Validator**: Uses a FORCE tool to perform validation
4. **Composition Validator**: Combines multiple validators with AND/OR logic

## Testing Constraints

You can test constraints using the FORCE API:

```python
async def test_constraint():
    from force.tool_executor import ForceEngine
    
    engine = ForceEngine()
    
    # Validate a file against a constraint
    violations = await engine.validate_constraints("code-quality-function-length", {
        "file_path": "path/to/test/file.py"
    })
    
    for violation in violations:
        print(f"Violation: {violation.message} at {violation.location}")
```

## Handling Violations

Constraint violations include:

- **Constraint ID**: The ID of the violated constraint
- **Message**: A description of the violation
- **Location**: Where the violation occurred (file path, line number, etc.)
- **Severity**: The severity level (error, warning, info)
- **Auto-fixable**: Whether the violation can be automatically fixed

### Auto-fixing Violations

For auto-fixable violations, you can implement a `fix` method:

```python
class SnakeCaseValidator(BaseConstraintValidator):
    # ...other code...
    
    async def fix(self, violation, context):
        file_path = violation.location.split(":")[0]
        variable_name = violation.metadata.get("variable_name")
        snake_case_name = self._to_snake_case(variable_name)
        
        return {
            "file_path": file_path,
            "replacements": [
                {
                    "old_text": variable_name,
                    "new_text": snake_case_name,
                    "line": violation.metadata.get("line")
                }
            ]
        }
    
    def _to_snake_case(self, name):
        # Convert to snake_case
        # ...implementation...
```

## Best Practices

1. **Clear Messages**: Provide clear, actionable violation messages
2. **Precise Location**: Specify exact locations for violations
3. **Performance**: Optimize validators for performance, especially for large files
4. **Auto-fix Safely**: Ensure auto-fixes don't introduce new issues
5. **Documentation**: Document constraints with examples of compliant and non-compliant code
6. **Testing**: Test constraints with a variety of inputs and edge cases
7. **Configuration**: Allow constraints to be configured with parameters

## Related Resources

- [FORCE Constraints Reference](../reference/constraints/index.md)
- [FORCE Tools Reference](../reference/tools/index.md)
- [FORCE Patterns Reference](../reference/patterns/index.md)
