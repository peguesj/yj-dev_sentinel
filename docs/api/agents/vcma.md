# Version Control Master Agent API

This document describes the API endpoints and messages for interacting with the Version Control Master Agent (VCMA).

## Message Bus Topics

### Published Topics

Topics that the VCMA publishes messages to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `vcma.status.update` | Regular status updates from the VC system | `VCStatusUpdate` |
| `vcma.commit.completed` | Published when a commit operation completes | `CommitResult` |
| `vcma.branch.completed` | Published when a branch operation completes | `BranchResult` |
| `vcma.change.detected` | Published when a file change is detected | `ChangeNotification` |

### Subscribed Topics

Topics that the VCMA subscribes to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `vcma.commit.request` | Request to perform a commit | `CommitRequest` |
| `vcma.branch.request` | Request to perform a branch operation | `BranchOperation` |
| `system.file.changed` | Notification of a file change | `ChangeNotification` |

## Data Types

### CommitRequest

Request for a commit operation.

```typescript
interface CommitRequest {
  files?: string[];  // Optional list of files to commit (all changes if omitted)
  message?: string;  // Optional commit message (generated if omitted)
  branch?: string;   // Target branch (current branch if omitted)
  priority: 'low' | 'medium' | 'high' | 'critical';
}
```

### CommitResult

Result of a commit operation.

```typescript
interface CommitResult {
  success: boolean;
  commitId?: string;
  message?: string;
  files: string[];
  timestamp: string;
  branch: string;
  error?: string;
}
```

### BranchOperation

Request for a branch operation.

```typescript
interface BranchOperation {
  operation: 'create' | 'switch' | 'merge' | 'delete';
  branchName: string;
  baseBranch?: string;  // For 'create' operations
  message?: string;     // For merge commits
}
```

### BranchResult

Result of a branch operation.

```typescript
interface BranchResult {
  success: boolean;
  operation: 'create' | 'switch' | 'merge' | 'delete';
  branchName: string;
  error?: string;
}
```

### ChangeNotification

Notification of a file change.

```typescript
interface ChangeNotification {
  filePath: string;
  changeType: 'add' | 'modify' | 'delete' | 'rename';
  timestamp: string;
  agent?: string;  // Agent responsible for change, if known
  operation?: string;  // Operation that caused the change, if known
}
```

### VCStatusUpdate

Current status of the version control system.

```typescript
interface VCStatusUpdate {
  branch: string;
  uncommittedChanges: number;
  lastCommitId: string;
  lastCommitTimestamp: string;
  lastCommitMessage: string;
  dirtyFiles: string[];
  repoStatus: 'clean' | 'dirty' | 'rebasing' | 'merging' | 'conflict';
}
```

## Python Client Example

```python
from core.message_bus import MessageBus

async def request_commit(message_bus: MessageBus, files, message=None):
    """Request a commit from the VCMA."""
    result = await message_bus.request(
        topic="vcma.commit.request",
        message={
            "files": files,
            "message": message,
            "priority": "medium"
        },
        response_topic="vcma.commit.completed"
    )
    return result
```
