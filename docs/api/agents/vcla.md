# Version Control Listener Agent API

This document describes the API endpoints and messages for interacting with the Version Control Listener Agent (VCLA).

## Message Bus Topics

### Published Topics

Topics that the VCLA publishes messages to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `vcla.event.detected` | Published when a VC event is detected | `VCEventNotification` |
| `vcla.notification.sent` | Published when a notification is sent | `NotificationResult` |
| `vcla.statistics.updated` | Published when statistics are updated | `VCStatisticsUpdate` |
| `vcla.history.response` | Response to history queries | `VCHistoryResponse` |

### Subscribed Topics

Topics that the VCLA subscribes to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `vcla.event.register` | Register for specific VC events | `EventRegistration` |
| `vcla.history.query` | Query VC event history | `HistoryQuery` |
| `vcla.statistics.query` | Query VC statistics | `StatisticsQuery` |
| `vcla.notification.configure` | Configure notifications | `NotificationConfig` |

## Data Types

### VCEventNotification

Notification of a version control event.

```typescript
interface VCEventNotification {
  eventType: 'commit' | 'push' | 'pull' | 'merge' | 'branch' | 'tag';
  timestamp: string;
  repository: string;
  branch: string;
  author: string;
  message?: string;
  commitId?: string;
  affectedFiles?: string[];
  metadata?: Record<string, any>;
}
```

### NotificationResult

Result of sending a notification.

```typescript
interface NotificationResult {
  success: boolean;
  notificationType: 'email' | 'slack' | 'system' | 'custom';
  recipients: string[];
  eventType: string;
  timestamp: string;
  error?: string;
}
```

### VCStatisticsUpdate

Update to version control statistics.

```typescript
interface VCStatisticsUpdate {
  period: 'daily' | 'weekly' | 'monthly';
  commitCount: number;
  authorCount: number;
  fileChangeCount: number;
  topAuthors: Array<{author: string, commitCount: number}>;
  topFiles: Array<{file: string, changeCount: number}>;
  timestamp: string;
}
```

### VCHistoryResponse

Response to a history query.

```typescript
interface VCHistoryResponse {
  events: VCEventNotification[];
  totalCount: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
```

### EventRegistration

Registration for version control events.

```typescript
interface EventRegistration {
  eventTypes: Array<'commit' | 'push' | 'pull' | 'merge' | 'branch' | 'tag'>;
  repository?: string;
  branch?: string;
  author?: string;
  callbackTopic: string;
}
```

### HistoryQuery

Query for version control event history.

```typescript
interface HistoryQuery {
  eventTypes?: Array<'commit' | 'push' | 'pull' | 'merge' | 'branch' | 'tag'>;
  startDate?: string;
  endDate?: string;
  author?: string;
  repository?: string;
  branch?: string;
  limit?: number;
  page?: number;
}
```

## Python Client Example

```python
from core.message_bus import MessageBus

async def query_commit_history(message_bus: MessageBus, author=None, limit=10):
    """Query recent commit history, optionally filtered by author."""
    result = await message_bus.request(
        topic="vcla.history.query",
        message={
            "eventTypes": ["commit"],
            "author": author,
            "limit": limit
        },
        response_topic="vcla.history.response"
    )
    return result
```
