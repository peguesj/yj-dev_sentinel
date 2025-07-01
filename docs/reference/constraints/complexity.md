# Complexity Constraints

Complexity constraints ensure that code remains maintainable by limiting various measures of code complexity.

## Available Constraints

### CPX001: Cyclomatic Complexity

- **ID**: `complexity-cyclomatic`
- **Severity**: Warning
- **Description**: Ensures that functions and methods do not exceed a specified cyclomatic complexity threshold.
- **Rule**: Functions should have a cyclomatic complexity of less than 10.
- **Auto-fixable**: No

### CPX002: Cognitive Complexity

- **ID**: `complexity-cognitive`
- **Severity**: Warning
- **Description**: Ensures that functions and methods do not exceed a specified cognitive complexity threshold.
- **Rule**: Functions should have a cognitive complexity of less than 15.
- **Auto-fixable**: No

### CPX003: Nesting Depth

- **ID**: `complexity-nesting-depth`
- **Severity**: Warning
- **Description**: Ensures that code does not have excessive nesting of control structures.
- **Rule**: Code should not have more than 4 levels of nesting.
- **Auto-fixable**: No

### CPX004: Function Parameter Count

- **ID**: `complexity-parameter-count`
- **Severity**: Warning
- **Description**: Ensures that functions and methods do not have too many parameters.
- **Rule**: Functions should have 5 or fewer parameters.
- **Auto-fixable**: No

### CPX005: Class Complexity

- **ID**: `complexity-class`
- **Severity**: Warning
- **Description**: Ensures that classes are not too complex.
- **Rule**: Classes should not have more than 20 methods or more than 500 lines of code.
- **Auto-fixable**: No

### CPX006: File Complexity

- **ID**: `complexity-file`
- **Severity**: Warning
- **Description**: Ensures that files are not too complex.
- **Rule**: Files should not have more than 1000 lines of code or a weighted complexity score above 120.
- **Auto-fixable**: No

## Understanding Complexity Metrics

### Cyclomatic Complexity

Cyclomatic complexity is a quantitative measure of the number of linearly independent paths through a program's source code. It is calculated by:

1. Starting with 1 for the base path
2. Adding 1 for each control flow statement (if, while, for, case, etc.)
3. Adding 1 for each logical operator (&&, ||) in conditional expressions

### Cognitive Complexity

Cognitive complexity measures how difficult code is to understand. Unlike cyclomatic complexity, it:

1. Doesn't increase on straight-line sequences of control flow statements
2. Increases when control flow is broken or interrupted
3. Increments more for nested structures than for sequential ones

### Nesting Depth

Nesting depth measures how many levels of nesting exist in control structures. Each level of nesting makes code harder to understand.

## Example Violations

Here are some examples of complexity constraint violations:

```python
# CPX001: High cyclomatic complexity
def process_data(data, mode, options, flags):
    result = []
    if mode == "fast":
        if options.get("optimize"):
            # Complex processing with many branches
            for item in data:
                if item.type == "A":
                    if item.value > 10:
                        result.append(process_a_high(item))
                    elif item.value > 5:
                        result.append(process_a_medium(item))
                    else:
                        result.append(process_a_low(item))
                elif item.type == "B":
                    if flags.get("special"):
                        if item.value > 20:
                            result.append(process_b_special_high(item))
                        else:
                            result.append(process_b_special_low(item))
                    else:
                        result.append(process_b_normal(item))
                else:
                    result.append(process_other(item))
        else:
            # Simple processing for non-optimized mode
            for item in data:
                result.append(process_simple(item))
    else:
        # Process in thorough mode
        for item in data:
            if item.quality > 80:
                result.append(process_high_quality(item))
            else:
                result.append(process_regular_quality(item))
    
    return result
```

## Reducing Complexity

Here are some techniques to reduce code complexity:

### Extract Method/Function

Break down complex functions into smaller, well-named functions:

```python
def process_data(data, mode, options, flags):
    if mode == "fast":
        return process_data_fast(data, options, flags)
    else:
        return process_data_thorough(data)

def process_data_fast(data, options, flags):
    if options.get("optimize"):
        return process_data_optimized(data, flags)
    else:
        return [process_simple(item) for item in data]

def process_data_optimized(data, flags):
    result = []
    for item in data:
        if item.type == "A":
            result.append(process_type_a(item))
        elif item.type == "B":
            result.append(process_type_b(item, flags))
        else:
            result.append(process_other(item))
    return result

def process_type_a(item):
    if item.value > 10:
        return process_a_high(item)
    elif item.value > 5:
        return process_a_medium(item)
    else:
        return process_a_low(item)
```

### Use Early Returns

Reduce nesting by using early returns or guard clauses:

```python
def process_item(item):
    # Guard clauses for special cases
    if item is None:
        return None
    
    if not item.is_valid():
        return error_result()
    
    if item.is_special():
        return special_processing(item)
    
    # Regular processing path
    result = standard_processing(item)
    return result
```

## Enforcement

Complexity constraints are typically enforced during:

- **Pre-commit checks**: Automatically check before committing code
- **Pull request validation**: Ensure code meets complexity standards before merging
- **Continuous Integration**: Regular complexity checks as part of the CI pipeline
- **Code reviews**: Manually review complex code and suggest improvements

## Configuration

Complexity constraints can be configured in the project's `.force/config.json` file:

```json
{
  "constraints": {
    "complexity": {
      "cyclomatic": {
        "enabled": true,
        "severity": "warning",
        "threshold": 10
      },
      "cognitive": {
        "enabled": true,
        "severity": "warning",
        "threshold": 15
      },
      "nesting-depth": {
        "enabled": true,
        "severity": "warning",
        "threshold": 4
      },
      "parameter-count": {
        "enabled": true,
        "severity": "warning",
        "threshold": 5
      }
    }
  }
}
```

## Related Constraints

- [Code Quality Constraints](code-quality.md)

## Related Patterns

- [Code Analysis Pattern](../patterns/code-analysis.md)
- [Refactoring Pattern](../patterns/refactoring.md)
