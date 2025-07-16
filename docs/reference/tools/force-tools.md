
# FORCE Tools Reference

| Version | Date       | Author   | Description                                  |
|---------|------------|----------|----------------------------------------------|
| v0.5.0  | 2025-07-16 | peguesj  | Release: Variant support, schema, docs update |

![Build Status](https://img.shields.io/github/actions/workflow/status/peguesj/yj-dev_sentinel/ci.yml?branch=main)
![Release](https://img.shields.io/github/v/release/peguesj/yj-dev_sentinel)

## New in v0.5.0

- **Variant Tooling**: Session orchestration, prompt engineering, and agentic workflows
- **Learning Tool**: Ad hoc learning records and analytics
- **Execution Analytics**: Track and analyze tool execution

This document provides comprehensive reference documentation for all tools available in the FORCE (Framework for Organized and Robust Code Evolution) system. These tools enhance software development workflows by providing automation for common tasks related to code organization, documentation, and project management.

## Tools Structure

All FORCE tools are located in the `force/tools` directory and are organized into categories:

```bash
force/tools/
├── documentation/     # Documentation-related tools
│   └── doc_sync/      # Documentation synchronization tool
├── git/               # Git-related tools
│   ├── grouped_commit/# Grouped commit workflow tool
│   └── status/        # Git status tool
└── project/           # Project management tools
    └── migration/     # Project structure migration tool
```

Each tool is implemented as a Python module with a main class that encapsulates the tool's functionality.

## Git Tools

### Grouped Commit Tool

**Module**: `force.tools.git.grouped_commit`

**Description**: Intelligently groups untracked work based on logical changes and git history, creating granular commits for developer clarity, and applying semantic versioning tags based on change impact weight.

**Features:**

- Analyzes changes by logical context
- Creates granular commits for each logical group
- Determines appropriate semantic version increments
- Applies semantic version tags

**Usage**:

```python
from force.tools.git.grouped_commit import GroupedCommitTool

# Initialize the tool
tool = GroupedCommitTool(
    scope="feature/my-feature",
    version_increment="auto",
    commit_message_prefix="[FEAT]",
    dry_run=True
)

# Execute the tool
tool.run()
```

**Command Line**:
```bash
python -m force.tools.git.grouped_commit.tool --scope feature/my-feature --version-increment auto --commit-message-prefix "[FEAT]" --dry-run
```

### Git Status Tool

**Module**: `force.tools.git.status`

**Description**: Provides enhanced git status functionality with detailed analysis and formatted output.

**Features:**

- Detailed status information
- Formatted output options
- Integration with other git tools

**Usage**:

```python
from force.tools.git.status import GitStatusExecutor

# Initialize the executor
executor = GitStatusExecutor()

# Execute the tool
result = await executor.execute({"porcelain": True}, {})
```

## Documentation Tools

### Documentation Sync Tool

**Module**: `force.tools.documentation.doc_sync`

**Description**: Synchronizes documentation changes with code changes, ensuring documentation updates are properly tracked and linked to implementation changes through cross-references and anchors.

**Features:**

- Scans documentation changes and categorizes them
- Updates changelog entries with implementation references
- Validates cross-references between documents
- Creates comprehensive commit for all documentation changes

**Usage**:

```python
from force.tools.documentation.doc_sync import DocSyncTool

# Initialize the tool
tool = DocSyncTool(
    docs_dir="docs",
    code_dir="src",
    patterns=["*.md", "*.py"],
    dry_run=True
)

# Execute the tool
tool.run()
```

**Command Line**:
```bash
python -m force.tools.documentation.doc_sync.tool --docs-dir docs --code-dir src --patterns "*.md" "*.py" --dry-run
```

## Project Tools

### Project Migration Tool

**Module**: `force.tools.project.migration`

**Description**: Performs comprehensive project structure migrations with file moves, link updates, and symlink creation for backward compatibility.

**Features:**

- Creates a complete backup of the original structure
- Creates the new directory structure
- Migrates files based on logical grouping
- Updates internal references to new paths
- Creates backward compatibility symlinks
- Validates the migration results

**Usage**:

```python
from force.tools.project.migration import ProjectMigrationTool

# Initialize the tool
tool = ProjectMigrationTool(
    source_dir="my_project",
    target_dir="my_project_new",
    mapping_file="migration_plan.json",
    create_symlinks=True,
    update_imports=True,
    update_links=True
)

# Execute the tool
tool.run()
```

**Command Line**:
```bash
python -m force.tools.project.migration.tool --source-dir my_project --target-dir my_project_new --mapping-file migration_plan.json
```

## Report Generation

All tools generate detailed reports of their execution, which are stored in the `.force/reports` directory structure, organized by branch, version, and atomic scoping:

```bash
.force/reports/
├── main/              # Branch name
│   └── v0.1.1/        # Version
│       ├── FORCE_COMPLETION_REPORT.md
│       ├── FORCE_DOC_VCS_EXECUTION_REPORT.md
│       ├── FORCE_GIT_TASK_REPORT.md
│       ├── FORCE_IMPLEMENTATION_SUMMARY.md
│       ├── FORCE_MIGRATION_GUIDE.md
│       └── FORCE_SUCCESS_REPORT.md
```
