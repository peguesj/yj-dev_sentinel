# Pattern Development Guide

This guide explains how to create and register custom patterns in the FORCE system.

## Understanding Patterns

FORCE patterns define reusable workflows and execution templates. A pattern consists of:

1. **Pattern Steps**: Individual operations that make up the pattern
2. **Context**: Data shared between steps during execution
3. **Metadata**: Information about the pattern (ID, name, description)

## Creating Patterns Programmatically

### Step 1: Import Required Classes

```python
from force.patterns import PatternStep, ToolStep, ConditionalStep, JsonPattern, PatternRegistry
```

### Step 2: Create Pattern Steps

You can create pattern steps by extending the `PatternStep` base class or using predefined step types:

```python
class CustomAnalysisStep(PatternStep):
    def __init__(self, name, description):
        super().__init__(name, description)
    
    async def execute(self, context, force_engine):
        # Custom analysis logic here
        result = analyze_code(context["code"])
        # Add results to context for later steps
        context["analysis_result"] = result
        return context
```

### Step 3: Create a Pattern

You can create patterns programmatically using the `JsonPattern` class:

```python
# Create pattern steps
analyze_step = CustomAnalysisStep("Analyze Code", "Analyzes code for quality issues")
lint_step = ToolStep("Lint Code", "Runs linting tools on the code", 
                     "code-linter", {"path": "${file_path}"})
report_step = ToolStep("Generate Report", "Creates a report from analysis results",
                       "report-generator", {"results": "${analysis_result}"})

# Create the pattern
code_quality_pattern = JsonPattern(
    pattern_id="code-quality-check",
    name="Code Quality Check Pattern",
    description="Checks code quality using analysis and linting tools",
    steps=[analyze_step, lint_step, report_step]
)

# Register the pattern
PatternRegistry.register("code-quality-check", code_quality_pattern)
```

## Creating Patterns with JSON

You can also define patterns using JSON files placed in the `force/patterns` directory:

```json
{
  "pattern_id": "documentation-check",
  "name": "Documentation Check Pattern",
  "description": "Checks documentation completeness and quality",
  "steps": [
    {
      "type": "tool",
      "name": "Extract Docstrings",
      "description": "Extracts docstrings from code files",
      "tool_id": "docstring-extractor",
      "parameters": {
        "path": "${file_path}"
      }
    },
    {
      "type": "tool",
      "name": "Analyze Docstrings",
      "description": "Analyzes docstring quality and completeness",
      "tool_id": "docstring-analyzer",
      "parameters": {
        "docstrings": "${extracted_docstrings}"
      }
    },
    {
      "type": "conditional",
      "name": "Check Coverage",
      "description": "Checks documentation coverage",
      "condition": "${doc_coverage} < 80",
      "then_step": {
        "type": "tool",
        "name": "Generate Doc Stubs",
        "description": "Generates documentation stubs for missing docstrings",
        "tool_id": "doc-stub-generator",
        "parameters": {
          "path": "${file_path}",
          "missing_docs": "${missing_docstrings}"
        }
      }
    }
  ]
}
```

## Pattern Step Types

### Tool Step

Executes a tool with specified parameters. Parameters can reference context values using `${context_key}` syntax.

```python
tool_step = ToolStep(
    name="Run Linter",
    description="Runs a linter on the code",
    tool_id="linter",
    parameters={"path": "${file_path}", "fix": True}
)
```

### Conditional Step

Executes different steps based on a condition:

```python
condition_step = ConditionalStep(
    name="Check Coverage",
    description="Checks if coverage is sufficient",
    condition="${coverage} < 90",
    then_step=ToolStep("Generate Tests", "Generates additional tests", 
                      "test-generator", {"path": "${file_path}"}),
    else_step=ToolStep("Report Success", "Reports success to user", 
                      "notifier", {"message": "Coverage is sufficient"})
)
```

## Testing Patterns

You can test patterns using the FORCE API:

```python
async def test_pattern():
    from force.tool_executor import ForceEngine
    
    engine = ForceEngine()
    
    # Execute the pattern with test context
    result = await engine.execute_pattern("code-quality-check", {
        "file_path": "path/to/test/file.py"
    })
    
    print(f"Pattern execution result: {result}")
```

## Best Practices

1. **Descriptive Names**: Use clear, descriptive names for patterns and steps
2. **Error Handling**: Handle errors in pattern steps gracefully
3. **Context Management**: Be careful with context manipulation to avoid conflicts
4. **Step Composition**: Break down complex operations into smaller steps
5. **Pattern Documentation**: Document your patterns with examples and parameter descriptions
6. **Testing**: Test patterns with a variety of inputs and edge cases
7. **Versioning**: Consider versioning patterns if they change significantly

## Related Resources

- [FORCE Patterns Reference](../reference/patterns/index.md)
- [FORCE Tools Reference](../reference/tools/index.md)
- [FORCE Constraints Reference](../reference/constraints/index.md)
