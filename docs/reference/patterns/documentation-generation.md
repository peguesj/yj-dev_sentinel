# Documentation Generation Pattern

The Documentation Generation Pattern provides a standardized workflow for generating and updating documentation for code, APIs, and project components.

## Pattern Information

- **Pattern ID**: `documentation-generation`
- **Name**: Documentation Generation Pattern
- **Description**: Generates and updates documentation for code and APIs

## Steps

1. **Code Analysis**
   - Analyzes code structure, comments, and function signatures
   - Extracts documentation comments and annotations

2. **Schema Extraction**
   - Extracts API schemas, data models, and interfaces
   - Identifies endpoints, parameters, and return types

3. **Documentation Template Selection**
   - Selects appropriate templates based on the content type
   - Applies project-specific documentation standards

4. **Content Generation**
   - Generates documentation content from the extracted information
   - Creates formatted documentation in the target format (Markdown, HTML, etc.)

5. **Integration**
   - Integrates the generated documentation into the project's documentation system
   - Updates existing documentation or creates new files as needed

## Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `scope` | Scope of documentation to generate (file, module, project) | Yes | - |
| `target_path` | Target path for the generated documentation | Yes | - |
| `format` | Output format (markdown, html, rst) | No | markdown |
| `templates` | Custom templates to use | No | Default templates |
| `update_existing` | Whether to update existing documentation or create new files | No | true |

## Example Usage

**Programmatic Usage**:

```python
result = await force_engine.execute_pattern("documentation-generation", context={
    "scope": "module",
    "target_path": "docs/api",
    "format": "markdown",
    "module_path": "force/tools"
})
```

**YUNG Command**:

```bash
$FORCE PATTERN RUN documentation-generation SCOPE=module TARGET=docs/api MODULE=force/tools
```

## Return Value

The pattern returns a dictionary with the following structure:

```json
{
  "status": "success",
  "generated_files": [
    {
      "path": "docs/api/tool-executor.md",
      "type": "new",
      "content_summary": "API documentation for the ToolExecutor class"
    },
    {
      "path": "docs/api/tool-registry.md",
      "type": "updated",
      "content_summary": "Updated API documentation for the ToolRegistry class"
    }
  ],
  "statistics": {
    "total_files": 5,
    "new_files": 2,
    "updated_files": 3,
    "total_endpoints": 12,
    "total_classes": 4
  }
}
```

## Related Patterns

- [Code Analysis Pattern](code-analysis.md)

## Related Constraints

- [Documentation Completeness Constraints](../constraints/documentation-completeness.md)
- [API Documentation Constraints](../constraints/api-documentation.md)
