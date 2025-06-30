# FORCE Constraints Reference

FORCE constraints define quality rules and requirements that are enforced throughout the Dev Sentinel ecosystem. These constraints help maintain code quality, consistency, and adherence to best practices.

## What are FORCE Constraints?

Constraints in the FORCE system are validation rules that check various aspects of code, documentation, and project structure. Each constraint represents a specific requirement that should be met for the project to be considered high quality. Constraints consist of:

- **Constraint ID**: A unique identifier for the constraint
- **Name**: A human-readable name
- **Description**: Detailed explanation of the constraint's purpose
- **Validator**: Logic that checks whether the constraint is met

## Constraint Categories

FORCE supports several categories of constraints:

- **Code Quality**: Constraints related to code structure, style, and maintainability
- **Security**: Constraints related to security best practices
- **Documentation**: Constraints related to documentation completeness and quality
- **Testing**: Constraints related to test coverage and quality
- **Performance**: Constraints related to performance characteristics
- **Architecture**: Constraints related to system architecture and design

## Available Constraints

The following constraint reference documents are available:

- [Code Quality Constraints](code-quality.md)
- [Security Constraints](security.md)
- [Documentation Completeness Constraints](documentation-completeness.md)
- [API Documentation Constraints](api-documentation.md)
- [Test Coverage Constraints](test-coverage.md)
- [Test Quality Constraints](test-quality.md)
- [Commit Quality Constraints](commit-quality.md)
- [Branch Naming Constraints](branch-naming.md)
- [Complexity Constraints](complexity.md)

## Constraint Violations

When a constraint is violated, a `ConstraintViolation` object is created with the following information:

- **Constraint ID**: The ID of the violated constraint
- **Message**: A description of the violation
- **Location**: Where the violation occurred (file path, line number, etc.)
- **Severity**: The severity level (error, warning, info)
- **Auto-fixable**: Whether the violation can be automatically fixed

## Creating Custom Constraints

Custom constraints can be defined programmatically by extending the `BaseConstraintValidator` class or by creating JSON constraint definitions. See the [Constraint Development Guide](../../developer/constraint-development.md) for details.

## Constraint Usage

Constraints can be checked through the FORCE API or through the YUNG command interface. For example:

```python
# Check constraints programmatically
violations = await force_engine.validate_constraints("code-quality", context={
    "file_path": "path/to/file.py",
})
```

Or via YUNG command:

```bash
$FORCE CONSTRAINT CHECK code-quality FILE=path/to/file.py
```

## Related Resources

- [FORCE Tools Reference](../tools/index.md)
- [FORCE Patterns Reference](../patterns/index.md)
- [Developer Guide](../../developer/index.md)
