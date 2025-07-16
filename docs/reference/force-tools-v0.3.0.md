# Force Tools Reference - v0.3.0

> **Note:** For v0.5.0, see new tools and schema updates in the main documentation. Variant, learning, and analytics tools are now available.

## Overview

This reference provides a comprehensive guide to all Force tools available in v0.3.0. Tools are organized by category and include both primary implementation tools and extended JSON-defined tools.

## Tool Categories

### Analysis Tools

#### Code Change Analysis

#### Release Readiness Check

#### Code Quality Assessment

### Git Workflow Tools

#### Git Commit Tool

#### Git Diff Analysis

#### Git Status Reporting

#### Branch Creation

#### Workflow Commit

#### Grouped Commit Tool
  - Logical change analysis
  - Granular commit creation
  - Semantic version determination
  - Automated tagging

### Documentation Tools

#### Documentation Analysis

#### Documentation Extraction

#### Documentation Validation

#### Documentation Update Summary

#### Documentation Sync Tool
  - Change categorization
  - Cross-reference validation
  - Comprehensive commit creation

### Security & Compliance Tools

#### Infrastructure Security Check

#### Secrets Scanner

#### Compliance Checker

### Performance & System Tools

#### Static Analysis

#### Dependency Analysis

#### Performance Analysis

#### Test Execution

### Project Management Tools

#### Project Migration Tool
  - Structure backup and migration
  - Reference updates
  - Symlink creation for compatibility
  - Validation and rollback

## Tool Usage Patterns

### Command Line Usage

All tools support command-line execution:

```bash
# Primary tools (Python modules)
python -m force.tools.git.grouped_commit.tool [options]
python -m force.tools.documentation.doc_sync.tool [options]
python -m force.tools.project.migration.tool [options]

# Extended tools (JSON-defined, via executor)
python -m force.tool_executor --tool analyze-code-changes [options]
python -m force.tool_executor --tool check-release-readiness [options]
```

### Programmatic Usage

All tools can be used programmatically:

```python
# Primary tools
from force.tools.git.grouped_commit import GroupedCommitTool
tool = GroupedCommitTool(scope="feature", dry_run=True)
result = tool.run()

# Extended tools via executor
from force.tool_executor import ToolExecutor
executor = ToolExecutor()
result = executor.execute_tool("analyze-code-changes", {"sinceCommit": "HEAD~5"})
```

### MCP Integration

Tools are available through the MCP server:

```json
{
  "method": "tools/call",
  "params": {
    "name": "force_execute_tool",
    "arguments": {
      "toolId": "analyze-code-changes",
      "parameters": {"sinceCommit": "HEAD~5"}
    }
  }
}
```

## Tool Configuration

### Primary Tools

Configure through Python parameters or configuration files:

```python
# Configuration example
config = {
    "scope": "feature/new-functionality",
    "version_increment": "minor",
    "dry_run": False,
    "commit_message_prefix": "[FEAT]"
}
```

### Extended Tools

Configure through JSON schema validation:

```json
{
  "toolId": "analyze-code-changes",
  "parameters": {
    "sinceCommit": "v0.2.0",
    "focusAreas": ["api", "interfaces", "documentation"]
  },
  "context": {
    "projectPhase": "development",
    "complexityLevel": "medium"
  }
}
```

## Best Practices

### Tool Selection

1. **Use specific tools for specific tasks**: Don't use general-purpose tools when specialized ones exist
2. **Combine tools for workflows**: Chain tools for comprehensive workflows
3. **Validate before execution**: Use dry-run modes for validation

### Quality Assurance

1. **Regular analysis**: Run analysis tools regularly during development
2. **Pre-commit validation**: Use quality tools in pre-commit hooks
3. **Release validation**: Use comprehensive validation before releases

### Documentation

1. **Automated documentation**: Use documentation tools for consistent updates
2. **Cross-reference validation**: Regularly validate documentation links
3. **Change tracking**: Use summary tools for tracking documentation changes

## Troubleshooting

### Common Issues

1. **Tool not found**: Check tool registry and ensure proper installation
2. **Parameter validation**: Verify parameters match tool schema
3. **Permission issues**: Ensure proper file and directory permissions

### Debug Mode

Enable debug mode for detailed execution information:

```bash
export FORCE_DEBUG=true
python -m force.tools.git.grouped_commit.tool --debug
```

### Logging

Tools provide comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

### Adding New Tools

1. **Follow schema**: Use Force schema for tool definitions
2. **Include documentation**: Provide comprehensive documentation
3. **Add tests**: Include unit and integration tests
4. **Update reference**: Add tool to this reference document

### Tool Categories

When adding tools, choose appropriate categories:

For more information, see the [Force Development Guide](../developer/force-development.md).

| Version | Date       | Author   | Description                                  |
|---------|------------|----------|----------------------------------------------|
| v0.3.0  | 2024-12-01 | peguesj  | Reference for v0.3.0 tools                   |
| v0.5.0  | 2025-07-16 | peguesj  | See new tools: Variant, learning, analytics   |

![Build Status](https://img.shields.io/github/actions/workflow/status/peguesj/yj-dev_sentinel/ci.yml?branch=main)
![Release](https://img.shields.io/github/v/release/peguesj/yj-dev_sentinel)
## Best Practices
