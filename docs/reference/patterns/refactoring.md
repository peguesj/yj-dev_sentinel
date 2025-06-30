# Refactoring Pattern

The Refactoring Pattern provides a standardized workflow for refactoring code to improve quality, readability, and maintainability without changing its external behavior.

## Pattern Information

- **Pattern ID**: `refactoring`
- **Name**: Refactoring Pattern
- **Description**: Refactors code to improve quality while preserving behavior

## Steps

1. **Code Analysis**
   - Analyzes the target code for refactoring opportunities
   - Identifies code smells, complexity issues, and anti-patterns

2. **Refactoring Planning**
   - Plans the refactoring approach based on analysis results
   - Determines the sequence of refactorings to apply

3. **Test State Capture**
   - Captures the current test state to ensure behavior preservation
   - Ensures adequate test coverage before proceeding

4. **Apply Refactorings**
   - Applies the planned refactorings in sequence
   - Performs transformations like extract method, rename, move, etc.

5. **Validation**
   - Runs tests to verify that behavior has been preserved
   - Validates that code quality metrics have improved

## Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `target_path` | Path to the code to refactor | Yes | - |
| `refactoring_type` | Type of refactoring to apply (auto, extract-method, etc.) | No | auto |
| `complexity_threshold` | Complexity threshold for targeting refactoring | No | 10 |
| `skip_validation` | Whether to skip validation tests | No | false |
| `aggressive` | Whether to apply more aggressive refactorings | No | false |

## Example Usage

**Programmatic Usage**:

```python
result = await force_engine.execute_pattern("refactoring", context={
    "target_path": "src/services/data_processor.py",
    "refactoring_type": "extract-method",
    "complexity_threshold": 8
})
```

**YUNG Command**:

```bash
$FORCE PATTERN RUN refactoring TARGET=src/services/data_processor.py TYPE=extract-method THRESHOLD=8
```

## Return Value

The pattern returns a dictionary with the following structure:

```json
{
  "status": "success",
  "refactoring_results": {
    "refactored_files": [
      {
        "path": "src/services/data_processor.py",
        "changes": [
          {
            "type": "extract-method",
            "original_location": "DataProcessor.process, lines 45-65",
            "new_method": "DataProcessor._validate_input",
            "lines_affected": 20
          },
          {
            "type": "rename-variable",
            "original_name": "d",
            "new_name": "data_item",
            "occurrences": 12
          }
        ]
      }
    ],
    "metrics": {
      "before": {
        "complexity": 22,
        "maintainability_index": 65,
        "lines_of_code": 150
      },
      "after": {
        "complexity": 14,
        "maintainability_index": 78,
        "lines_of_code": 165
      }
    },
    "validation": {
      "tests_passed": true,
      "behavior_preserved": true
    }
  }
}
```

## Related Patterns

- [Code Analysis Pattern](code-analysis.md)
- [Test Generation Pattern](test-generation.md)

## Related Constraints

- [Code Quality Constraints](../constraints/code-quality.md)
- [Complexity Constraints](../constraints/complexity.md)
