# Version Control Pattern

The Version Control Pattern provides a standardized workflow for version control operations, including commits, branches, and merges.

## Pattern Information

- **Pattern ID**: `version-control`
- **Name**: Version Control Pattern
- **Description**: Manages version control operations in a standardized way

## Steps

1. **Status Check**
   - Checks the status of the working directory
   - Identifies changes, untracked files, and conflicts

2. **Change Selection**
   - Selects changes to include in the operation
   - Filters files based on patterns and content

3. **Preparation**
   - Performs any necessary pre-operation steps (e.g., formatting, linting)
   - Validates that changes meet project standards

4. **Execute Operation**
   - Executes the requested version control operation
   - Handles commits, branch creation, merges, etc.

5. **Post-Operation Actions**
   - Performs any necessary post-operation steps
   - Updates related systems, triggers notifications, etc.

## Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `operation` | Version control operation to perform (commit, branch, merge) | Yes | - |
| `message` | Message for the operation (e.g., commit message) | Conditional | - |
| `files` | Specific files to include | No | All changed files |
| `branch_name` | Name for branch operations | Conditional | - |
| `skip_validation` | Whether to skip pre-commit validation | No | false |

## Example Usage

**Programmatic Usage**:

```python
result = await force_engine.execute_pattern("version-control", context={
    "operation": "commit",
    "message": "Fix authentication bug in login service",
    "files": ["src/auth/login.py", "tests/auth/test_login.py"]
})
```

**YUNG Command**:

```bash
$FORCE PATTERN RUN version-control OPERATION=commit MESSAGE="Fix authentication bug in login service" FILES=src/auth/login.py,tests/auth/test_login.py
```

## Return Value

The pattern returns a dictionary with the following structure:

```json
{
  "status": "success",
  "operation_details": {
    "operation": "commit",
    "result": "success",
    "id": "a1b2c3d4e5f6",
    "summary": "Created commit a1b2c3d4e5f6: Fix authentication bug in login service",
    "included_files": [
      "src/auth/login.py",
      "tests/auth/test_login.py"
    ],
    "validation_results": {
      "passed": true,
      "messages": []
    }
  }
}
```

## Related Patterns

- [Code Analysis Pattern](code-analysis.md)
- [Test Generation Pattern](test-generation.md)

## Related Constraints

- [Commit Quality Constraints](../constraints/commit-quality.md)
- [Branch Naming Constraints](../constraints/branch-naming.md)
