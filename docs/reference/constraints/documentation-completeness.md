# Documentation Completeness Constraints

Documentation completeness constraints ensure that code is properly documented with comments, docstrings, and explanations to facilitate understanding and maintenance.

## Available Constraints

### DOC001: Module Documentation

- **ID**: `doc-module-documentation`
- **Severity**: Warning
- **Description**: Ensures that each module has documentation describing its purpose and functionality.
- **Rule**: Every module should have a module-level docstring explaining its purpose.
- **Auto-fixable**: No

### DOC002: Class Documentation

- **ID**: `doc-class-documentation`
- **Severity**: Warning
- **Description**: Ensures that each class has documentation describing its purpose and usage.
- **Rule**: Every class should have a class-level docstring explaining its purpose and usage.
- **Auto-fixable**: No

### DOC003: Method Documentation

- **ID**: `doc-method-documentation`
- **Severity**: Warning
- **Description**: Ensures that each method has documentation describing its purpose, parameters, and return value.
- **Rule**: Public methods should have docstrings with parameter and return value descriptions.
- **Auto-fixable**: No

### DOC004: Function Documentation

- **ID**: `doc-function-documentation`
- **Severity**: Warning
- **Description**: Ensures that each function has documentation describing its purpose, parameters, and return value.
- **Rule**: Public functions should have docstrings with parameter and return value descriptions.
- **Auto-fixable**: No

### DOC005: Parameter Documentation

- **ID**: `doc-parameter-documentation`
- **Severity**: Warning
- **Description**: Ensures that function and method parameters are documented.
- **Rule**: Each parameter should be documented in the function/method docstring.
- **Auto-fixable**: No

### DOC006: Return Value Documentation

- **ID**: `doc-return-documentation`
- **Severity**: Warning
- **Description**: Ensures that function and method return values are documented.
- **Rule**: Return values should be documented in the function/method docstring.
- **Auto-fixable**: No

### DOC007: Example Documentation

- **ID**: `doc-example-documentation`
- **Severity**: Info
- **Description**: Encourages the inclusion of examples in documentation for complex functions or classes.
- **Rule**: Complex functions or classes should include usage examples in their docstrings.
- **Auto-fixable**: No

### DOC008: README Completeness

- **ID**: `doc-readme-completeness`
- **Severity**: Warning
- **Description**: Ensures that the project's README contains essential information.
- **Rule**: README should contain title, description, installation instructions, usage examples, and contribution guidelines.
- **Auto-fixable**: No

## Example Violations

Here are some examples of documentation completeness constraint violations:

```python
# DOC001: Missing module documentation
# This module should have a docstring at the top

# DOC002: Missing class documentation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    # DOC003: Missing method documentation
    def validate_email(self):
        # Implementation...
        return True or False
    
# DOC004: Missing function documentation
def calculate_total(items, tax_rate):
    total = sum(item.price for item in items)
    return total * (1 + tax_rate)
```

## Properly Documented Examples

```python
"""
User Management Module

This module provides functionality for managing user accounts, including
creation, validation, and authentication.
"""

class User:
    """
    User class for representing and managing user accounts.
    
    This class handles user data, validation, and authentication operations.
    """
    
    def __init__(self, name, email):
        """
        Initialize a new User instance.
        
        Args:
            name (str): The user's full name
            email (str): The user's email address
        """
        self.name = name
        self.email = email
    
    def validate_email(self):
        """
        Validate that the user's email address is properly formatted.
        
        Returns:
            bool: True if the email is valid, False otherwise
        """
        # Implementation...
        return True or False
    
def calculate_total(items, tax_rate):
    """
    Calculate the total cost including tax.
    
    Args:
        items (list): List of Item objects with a price attribute
        tax_rate (float): The tax rate as a decimal (e.g., 0.07 for 7%)
    
    Returns:
        float: The total cost including tax
    
    Example:
        >>> items = [Item(10.0), Item(5.0)]
        >>> calculate_total(items, 0.07)
        16.05
    """
    total = sum(item.price for item in items)
    return total * (1 + tax_rate)
```

## Enforcement

Documentation completeness constraints are typically enforced during:

- **Pre-commit checks**: Automatically check before committing code
- **Pull request validation**: Ensure code meets documentation standards before merging
- **Continuous Integration**: Regular documentation checks as part of the CI pipeline

## Configuration

Documentation completeness constraints can be configured in the project's `.force/config.json` file:

```json
{
  "constraints": {
    "documentation": {
      "method-documentation": {
        "enabled": true,
        "severity": "warning",
        "exclude_patterns": ["test/**/*.py"]
      },
      "readme-completeness": {
        "enabled": true,
        "severity": "warning",
        "required_sections": ["description", "installation", "usage"]
      }
    }
  }
}
```

## Related Constraints

- [API Documentation Constraints](api-documentation.md)

## Related Patterns

- [Documentation Generation Pattern](../patterns/documentation-generation.md)
