# Usage Examples

This document provides practical examples of using Dev Sentinel in various scenarios.

## Basic Usage

### Starting the System

To start Dev Sentinel:

```bash
# Start the main server
python run_server.py

# Or with specific log level
PYTHONPATH=. LOG_LEVEL=DEBUG python run_server.py
```

### Checking System Status

```python
from core.message_bus import MessageBus

async def check_system_status():
    message_bus = MessageBus.get_instance()
    status = await message_bus.request(
        topic="system.status.request", 
        message={}, 
        response_topic="system.status.response"
    )
    print(f"System Status: {status}")
```

## Using Agents

### Version Control Master Agent (VCMA)

#### Requesting an Automatic Commit

```python
from core.message_bus import MessageBus

async def request_auto_commit(message_bus):
    result = await message_bus.request(
        topic="vcma.commit.request",
        message={
            "priority": "medium",
            "message": None  # Auto-generate the message
        },
        response_topic="vcma.commit.completed"
    )
    return result
```

#### Creating a New Branch

```python
from core.message_bus import MessageBus

async def create_branch(message_bus, branch_name, base_branch="main"):
    result = await message_bus.request(
        topic="vcma.branch.request",
        message={
            "operation": "create",
            "branchName": branch_name,
            "baseBranch": base_branch
        },
        response_topic="vcma.branch.completed"
    )
    return result
```

### Documentation Inspector Agents

#### Analyzing README Quality

```python
from core.message_bus import MessageBus

async def analyze_readme(message_bus, file_path="README.md"):
    result = await message_bus.request(
        topic="rdia.analyze.request",
        message={
            "filePath": file_path,
            "checkLinks": True
        },
        response_topic="rdia.analyze.response"
    )
    return result
```

#### Analyzing Code Documentation

```python
from core.message_bus import MessageBus

async def analyze_code_documentation(message_bus, file_paths):
    result = await message_bus.request(
        topic="cdia.analyze.request",
        message={
            "filePaths": file_paths,
            "detailed": True
        },
        response_topic="cdia.analyze.response"
    )
    return result
```

### Static Analysis

```python
from core.message_bus import MessageBus

async def perform_static_analysis(message_bus, file_paths):
    result = await message_bus.request(
        topic="saa.analysis.request",
        message={
            "filePaths": file_paths,
            "ruleSets": ["security", "quality"],
            "severity": "warning"
        },
        response_topic="saa.analysis.response"
    )
    return result
```

## Using FORCE Framework

### Executing Tools

#### Git Grouped Commit Tool

```python
from force.tool_executor import ToolExecutor

async def grouped_commit(scope="feature"):
    executor = ToolExecutor()
    result = await executor.execute_tool(
        tool_name="git.grouped_commit",
        parameters={
            "scope": scope,
            "version_increment": "auto",
            "commit_message_prefix": "[FEAT]"
        }
    )
    return result
```

#### Documentation Sync Tool

```python
from force.tool_executor import ToolExecutor

async def sync_documentation():
    executor = ToolExecutor()
    result = await executor.execute_tool(
        tool_name="documentation.doc_sync",
        parameters={
            "source_path": "docs/",
            "verify_links": True,
            "update_toc": True
        }
    )
    return result
```

### Applying Patterns

```python
from force.patterns import PatternExecutor

async def apply_feature_workflow(feature_name):
    executor = PatternExecutor()
    result = await executor.execute_pattern(
        pattern_name="development.feature_workflow",
        parameters={
            "feature_name": feature_name,
            "create_branch": True,
            "run_tests": True,
            "auto_commit": True
        }
    )
    return result
```

### Checking Constraints

```python
from force.constraints import ConstraintChecker

async def validate_code_quality(file_path):
    checker = ConstraintChecker()
    result = await checker.check_constraints(
        constraints=["code_quality", "security"],
        context={
            "file_path": file_path
        }
    )
    return result
```

## Command-Line Interface

Dev Sentinel also provides a command-line interface for common operations:

### Git Tasks

```bash
# Run a git task with FORCE
python scripts/force_git_task.py --operation commit --scope feature/my-feature
```

### Documentation Tasks

```bash
# Generate documentation
python scripts/force_doc_task.py --operation generate --path docs/
```

### Static Analysis

```bash
# Run static analysis
python scripts/force_code_task.py --operation analyze --path src/
```

## Model Context Protocol (MCP) Integration

When using Dev Sentinel with VS Code and the Model Context Protocol:

1. Ensure VS Code is open to your project folder
2. Start the MCP server:
   ```bash
   python -m integration.fast_agent.mcp_servers
   ```

3. In VS Code, use the Command Palette (Ctrl+Shift+P) to run "Dev Sentinel: Connect"

4. You can now interact with Dev Sentinel directly in VS Code:
   ```
   @dev_sentinel analyze code quality for this file
   ```

## Real-World Scenarios

### Scenario 1: Automated Documentation Review

Review and improve all markdown documentation:

```python
import asyncio
from pathlib import Path
from core.message_bus import MessageBus

async def improve_all_documentation():
    message_bus = MessageBus.get_instance()
    
    # Find all markdown files
    md_files = list(Path('.').glob('**/*.md'))
    
    # Analyze README files
    readme_results = await message_bus.request(
        topic="rdia.analyze.request",
        message={
            "filePaths": [str(f) for f in md_files],
            "checkLinks": True,
            "detailed": True
        },
        response_topic="rdia.analyze.response"
    )
    
    # Generate improvement suggestions
    for file in readme_results.get('results', []):
        if file.get('issues'):
            await message_bus.request(
                topic="rdia.improvement.request",
                message={
                    "filePath": file['filePath'],
                    "improvementTypes": ["structure", "content", "clarity"]
                },
                response_topic="rdia.improvement.response"
            )

# Run the function
asyncio.run(improve_all_documentation())
```

### Scenario 2: Intelligent Version Control

Automatically commit changes when they form a logical unit:

```python
import asyncio
from core.message_bus import MessageBus

async def monitor_and_commit():
    message_bus = MessageBus.get_instance()
    
    # Subscribe to file change events
    async def handle_file_changes(message):
        # Check if changes form a logical unit
        status = await message_bus.request(
            topic="vcma.status.request",
            message={},
            response_topic="vcma.status.response"
        )
        
        if status.get('uncommittedChanges', 0) >= 5:
            # Request an automatic commit
            await message_bus.request(
                topic="vcma.commit.request",
                message={"priority": "medium"},
                response_topic="vcma.commit.completed"
            )
    
    # Subscribe to file change events
    await message_bus.subscribe("system.file.changed", handle_file_changes)
    
    print("Monitoring file changes...")
    # Keep the script running
    while True:
        await asyncio.sleep(1)

# Run the function
asyncio.run(monitor_and_commit())
```

For more detailed examples, see the [code samples](/docs/user/code-samples/) directory.
