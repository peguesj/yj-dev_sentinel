# Version Control Master Agent (VCMA)

> Version: 0.1.0

## Overview

The Version Control Master Agent (VCMA) is an autonomous agent responsible for monitoring development activities across the platform, identifying code changes that warrant version control operations, and executing those operations at appropriate times. It serves as the "observer" in the system, proactively managing version control without requiring explicit commands.

## Core Capabilities

### Change Monitoring

The VCMA continuously monitors the workspace for relevant changes:

- File system watches for modified, added, and deleted files
- Detection of meaningful change patterns
- Filtering of temporary/generated files via configurable rules
- Recording of change history and patterns

### Decision Intelligence

The agent employs sophisticated decision-making to determine when to perform version control operations:

- Semantic analysis of code changes to identify logical completion points
- Temporal patterns to identify appropriate commit frequency
- Contextual understanding of development workflows
- Learning from past commit patterns and outcomes

### Operation Execution

Autonomous execution of version control operations:

- Staging of related changes into logical groups
- Generation of descriptive commit messages
- Management of branches for different workflows
- Stashing and retrieval of work-in-progress changes
- Conflict resolution during merges

### Integration

Integration with the broader agent ecosystem:

- Notification of other agents about version control state changes
- Coordination with development agents on timing of commits
- Knowledge sharing with the central knowledge base
- Metrics collection and reporting for system monitoring

## System Interfaces

### Input Interfaces

The VCMA accepts the following input interfaces:

- **ChangeNotification**: Information about file changes
- **CommitRequest**: Requests to commit changes
- **BranchOperation**: Instructions for branch operations

### Output Interfaces

The VCMA produces the following output interfaces:

- **CommitResult**: Results of commit operations
- **BranchResult**: Results of branch operations
- **VCStatusUpdate**: Current version control status information

## Implementation

The VCMA is implemented in `agents/vcma/vcma_agent.py` and follows the standard Dev Sentinel agent architecture. It extends the base `Agent` class and implements the required interfaces.

### Key Components

- **ChangeDetector**: Monitors the filesystem for changes
- **CommitAnalyzer**: Analyzes changes to determine commit points
- **MessageGenerator**: Generates descriptive commit messages
- **VCExecutor**: Executes version control operations

## Configuration

The VCMA can be configured in the `config/fastagent.config.yaml` file:

```yaml
agents:
  vcma:
    enabled: true
    commit_threshold: 5  # Minimum meaningful changes for auto-commit
    ignored_patterns:
      - "*.log"
      - "*.tmp"
      - "node_modules/**"
    commit_frequency: "adaptive"  # adaptive, frequent, conservative
```

## Usage

The VCMA operates autonomously but can be interacted with through the message bus:

```python
# Requesting a manual commit
await message_bus.publish(
    topic="vcma.commit.request",
    message={
        "files": ["file1.py", "file2.py"],
        "message": "Implemented feature X",
        "priority": "high"
    }
)
```

## Related Components

- [Version Control Listener Agent (VCLA)](vcla.md) - Handles version control events
- [FORCE Version Control Tools](/docs/reference/tools/version-control.md) - Tools for version control operations
