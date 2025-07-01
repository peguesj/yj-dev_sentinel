# Code Quality Constraints

Code quality constraints ensure that code meets quality standards for readability, maintainability, and adherence to best practices.

## Available Constraints

### CQ001: Line Length

- **ID**: `code-quality-line-length`
- **Severity**: Warning
- **Description**: Ensures that lines of code do not exceed the maximum line length.
- **Rule**: Line length should be less than or equal to 100 characters.
- **Auto-fixable**: Yes (for some cases)

### CQ002: Function Length

- **ID**: `code-quality-function-length`
- **Severity**: Warning
- **Description**: Ensures that functions are not too long, promoting better code organization.
- **Rule**: Functions should contain less than 50 lines of code.
- **Auto-fixable**: No

### CQ003: Class Length

- **ID**: `code-quality-class-length`
- **Severity**: Warning
- **Description**: Ensures that classes are not too large, promoting better code organization.
- **Rule**: Classes should contain less than 300 lines of code.
- **Auto-fixable**: No

### CQ004: Function Arguments

- **ID**: `code-quality-function-arguments`
- **Severity**: Warning
- **Description**: Ensures that functions do not have too many parameters.
- **Rule**: Functions should have 5 or fewer parameters.
- **Auto-fixable**: No

### CQ005: Variable Naming

- **ID**: `code-quality-variable-naming`
- **Severity**: Warning
- **Description**: Ensures that variable names follow the project's naming convention.
- **Rule**: Variable names should use snake_case for Python, camelCase for JavaScript, etc.
- **Auto-fixable**: Yes

### CQ006: Import Order

- **ID**: `code-quality-import-order`
- **Severity**: Info
- **Description**: Ensures that imports are organized in a consistent manner.
- **Rule**: Imports should be grouped and ordered according to standard conventions.
- **Auto-fixable**: Yes

### CQ007: Dead Code

- **ID**: `code-quality-dead-code`
- **Severity**: Warning
- **Description**: Identifies and warns about code that is never executed.
- **Rule**: Code should not contain unreachable statements or unused functions.
- **Auto-fixable**: Yes

### CQ008: Code Duplication

- **ID**: `code-quality-duplication`
- **Severity**: Warning
- **Description**: Identifies duplicated code blocks that should be refactored.
- **Rule**: Code should not contain duplicated blocks exceeding 10 lines with high similarity.
- **Auto-fixable**: No

## Example Violations

Here are some examples of code quality constraint violations:

```python
# CQ001: Line length violation
def some_function_with_a_very_long_name_that_exceeds_line_length_limits(parameter_one, parameter_two, parameter_three, parameter_four, parameter_five):
    # This line is too long and should be broken up or refactored

# CQ005: Variable naming violation
def calculate_total(ItemPrice, TAX_RATE, quantity):  # Inconsistent naming styles
    totalCost = ItemPrice * quantity * (1 + TAX_RATE)  # camelCase in a Python file
    return totalCost
```

## Enforcement

Code quality constraints are typically enforced during:

- **Pre-commit checks**: Automatically check before committing code
- **Pull request validation**: Ensure code meets standards before merging
- **Continuous Integration**: Regular checks as part of the CI pipeline

## Configuration

Code quality constraints can be configured in the project's `.force/config.json` file:

```json
{
  "constraints": {
    "code-quality": {
      "line-length": {
        "max": 100,
        "severity": "warning"
      },
      "function-length": {
        "max": 50,
        "severity": "warning"
      }
    }
  }
}
```

## Related Constraints

- [Complexity Constraints](complexity.md)
- [Security Constraints](security.md)

## Related Patterns

- [Code Analysis Pattern](../patterns/code-analysis.md)
- [Refactoring Pattern](../patterns/refactoring.md)
