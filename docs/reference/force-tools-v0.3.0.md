# Force Tools Reference - v0.3.0

## Overview

This reference provides a comprehensive guide to all Force tools available in v0.3.0. Tools are organized by category and include both primary implementation tools and extended JSON-defined tools.

## Tool Categories

### Analysis Tools

#### Code Change Analysis
- **Tool ID**: `analyze-code-changes`
- **Purpose**: Analyzes code changes to determine documentation impact
- **Parameters**: `sinceCommit`, `focusAreas`
- **Usage**: Impact assessment for code modifications

#### Release Readiness Check
- **Tool ID**: `check-release-readiness`
- **Purpose**: Comprehensive validation for release preparation
- **Usage**: Pre-release quality gates and validation

#### Code Quality Assessment
- **Tool ID**: `code-quality-check`
- **Purpose**: Multi-dimensional code quality scoring
- **Usage**: Continuous quality monitoring and improvement

### Git Workflow Tools

#### Git Commit Tool
- **Tool ID**: `git-commit`
- **Purpose**: Intelligent commit message generation
- **Usage**: Standardized commit practices

#### Git Diff Analysis
- **Tool ID**: `git-diff`
- **Purpose**: Enhanced diff analysis and reporting
- **Usage**: Change analysis and review

#### Git Status Reporting
- **Tool ID**: `git-status`
- **Purpose**: Context-aware status reporting
- **Usage**: Repository state analysis

#### Branch Creation
- **Tool ID**: `git_branch_create`
- **Purpose**: Automated branch creation with conventions
- **Usage**: Standardized branching workflows

#### Workflow Commit
- **Tool ID**: `git_workflow_commit`
- **Purpose**: Semantic versioning and workflow integration
- **Parameters**: `scope`, `semanticVersionIncrement`
- **Usage**: Automated semantic commit workflows

#### Grouped Commit Tool
- **Module**: `force.tools.git.grouped_commit`
- **Purpose**: Intelligent grouping of changes into atomic commits
- **Features**:
  - Logical change analysis
  - Granular commit creation
  - Semantic version determination
  - Automated tagging

### Documentation Tools

#### Documentation Analysis
- **Tool ID**: `docs-analysis`
- **Purpose**: Quality and completeness assessment
- **Usage**: Documentation quality monitoring

#### Documentation Extraction
- **Tool ID**: `docs-extraction`
- **Purpose**: Automated extraction from code
- **Usage**: API documentation generation

#### Documentation Validation
- **Tool ID**: `docs-validation`
- **Purpose**: Structure and content validation
- **Usage**: Quality assurance for documentation

#### Documentation Update Summary
- **Tool ID**: `generate-docs-update-summary`
- **Purpose**: Change summary generation
- **Usage**: Release notes and changelog automation

#### Documentation Sync Tool
- **Module**: `force.tools.documentation.doc_sync`
- **Purpose**: Synchronize documentation with code changes
- **Features**:
  - Change categorization
  - Cross-reference validation
  - Comprehensive commit creation

### Security & Compliance Tools

#### Infrastructure Security Check
- **Tool ID**: `infrastructure-security-check`
- **Purpose**: Infrastructure security validation
- **Usage**: Security compliance monitoring

#### Secrets Scanner
- **Tool ID**: `secrets-scan`
- **Purpose**: Sensitive data detection
- **Usage**: Security vulnerability prevention

#### Compliance Checker
- **Tool ID**: `compliance-check`
- **Purpose**: Automated compliance validation
- **Usage**: Regulatory and standards compliance

### Performance & System Tools

#### Static Analysis
- **Tool ID**: `static-analysis`
- **Purpose**: Advanced static code analysis
- **Usage**: Code quality and performance optimization

#### Dependency Analysis
- **Tool ID**: `dependency-analysis`
- **Purpose**: Dependency tracking and vulnerability assessment
- **Usage**: Security and maintenance planning

#### Performance Analysis
- **Tool ID**: `performance-analysis`
- **Purpose**: Performance monitoring and optimization
- **Usage**: Performance bottleneck identification

#### Test Execution
- **Tool ID**: `test-execution`
- **Purpose**: Automated test execution and reporting
- **Usage**: Continuous testing and quality assurance

### Project Management Tools

#### Project Migration Tool
- **Module**: `force.tools.project.migration`
- **Purpose**: Comprehensive project structure migrations
- **Features**:
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
- **Analysis**: Code and project analysis tools
- **Git**: Version control and workflow tools
- **Documentation**: Documentation generation and validation
- **Security**: Security and compliance tools
- **Performance**: Performance monitoring and optimization
- **Project**: Project management and migration tools

For more information, see the [Force Development Guide](../developer/force-development.md).
