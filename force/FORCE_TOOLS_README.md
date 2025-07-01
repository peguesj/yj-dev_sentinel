# FORCE Tools Documentation

This document describes the tools available in the FORCE (Framework for Organized and Robust Code Evolution) system. These tools are designed to enhance software development workflows by providing automation for common tasks related to code organization, documentation, and project management.

## Tools Structure

All FORCE tools are located in the `force/tools` directory and are organized into categories:

```
force/tools/
├── documentation/     # Documentation-related tools
│   └── doc_sync/      # Documentation synchronization tool
├── git/               # Git-related tools
│   └── grouped_commit/# Grouped commit workflow tool
└── project/           # Project management tools
    └── migration/     # Project structure migration tool
```

Each tool is implemented as a Python module with a main class that encapsulates the tool's functionality.

## Available Tools

### 1. Git Tools

#### Grouped Commit Tool

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

### 2. Documentation Tools

#### Documentation Sync Tool

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

### 3. Project Tools

#### Project Migration Tool

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

```
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

## Implementation Notes

Each tool follows FORCE principles and includes:

1. A command-line interface for easy use
2. A Python API for programmatic integration
3. Configurable options for customizing behavior
4. Detailed output explaining the actions being performed
5. A "dry run" mode for testing without making changes
6. Report generation for documenting the changes made

## Integration with FORCE System

These tools are designed to integrate seamlessly with the larger FORCE system, supporting its principles of:

1. **Consistency** - Enforcing consistent practices across development processes
2. **Traceability** - Ensuring all changes are properly tracked and documented
3. **Knowledge Preservation** - Maintaining comprehensive documentation of development activities
4. **Automation** - Reducing manual effort through intelligent automation

## Requirements

- Python 3.6+
- Git repository (for Git-related tools)

## Contributing

To add a new tool to the FORCE system:

1. Create a new directory under the appropriate category in `force/tools/`
2. Implement your tool as a Python module with a main class
3. Create an `__init__.py` file that exports your tool class
4. Update this documentation to include your tool
5. Add appropriate tests in the `tests/` directory

## License

These tools are provided under the MIT license. See LICENSE-MIT.md for details.
