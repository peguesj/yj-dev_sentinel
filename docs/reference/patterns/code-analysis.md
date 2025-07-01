# Code Analysis Pattern

The Code Analysis Pattern provides a standardized workflow for analyzing code quality, identifying potential issues, and generating insights.

## Pattern Information

- **Pattern ID**: `code-analysis`
- **Name**: Code Analysis Pattern
- **Description**: Analyzes code for quality, patterns, and potential issues

## Steps

1. **Code Preprocessing**
   - Prepares the code for analysis by normalizing formatting and structure
   - Identifies code language and applies appropriate parsing rules

2. **Static Analysis**
   - Runs static analysis tools appropriate for the language
   - Identifies potential bugs, code smells, and security vulnerabilities

3. **Pattern Recognition**
   - Identifies common patterns and anti-patterns in the code
   - Compares against known best practices

4. **Complexity Analysis**
   - Calculates code complexity metrics
   - Identifies areas that may benefit from refactoring

5. **Report Generation**
   - Compiles analysis results into a structured report
   - Provides recommendations for improvements

## Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `file_path` | Path to the file or directory to analyze | Yes | - |
| `analysis_depth` | Depth of analysis (quick, standard, deep) | No | standard |
| `metrics` | List of metrics to calculate | No | All available |
| `report_format` | Format for the output report (json, html, markdown) | No | markdown |

## Example Usage

**Programmatic Usage**:

```python
result = await force_engine.execute_pattern("code-analysis", context={
    "file_path": "path/to/file.py",
    "analysis_depth": "deep",
    "report_format": "json"
})
```

**YUNG Command**:

```bash
$FORCE PATTERN RUN code-analysis FILE=path/to/file.py DEPTH=deep FORMAT=json
```

## Return Value

The pattern returns a dictionary with the following structure:

```json
{
  "status": "success",
  "analysis_results": {
    "complexity": {
      "cyclomatic": 12,
      "cognitive": 8
    },
    "issues": [
      {
        "type": "bug",
        "description": "Potential null pointer dereference",
        "location": "line 42",
        "severity": "high"
      }
    ],
    "patterns_found": ["singleton", "observer"],
    "anti_patterns_found": ["god-class"],
    "recommendations": [
      "Consider breaking down the large class into smaller, more focused classes",
      "Add null checks before dereferencing the object on line 42"
    ]
  }
}
```

## Related Patterns

- [Refactoring Pattern](refactoring.md)
- [Test Generation Pattern](test-generation.md)

## Related Constraints

- [Code Quality Constraints](../constraints/code-quality.md)
- [Security Constraints](../constraints/security.md)
