# Static Analysis Agent API

This document describes the API endpoints and messages for interacting with the Static Analysis Agent (SAA).

## Message Bus Topics

### Published Topics

Topics that the SAA publishes messages to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `saa.analysis.response` | Response to code analysis requests | `CodeAnalysisResponse` |
| `saa.metrics.updated` | Published when code quality metrics are updated | `QualityMetricsUpdate` |
| `saa.issue.detected` | Published when a new issue is detected | `IssueNotification` |
| `saa.trend.response` | Response to trend analysis requests | `TrendAnalysisResponse` |

### Subscribed Topics

Topics that the SAA subscribes to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `saa.analysis.request` | Request for code analysis | `CodeAnalysisRequest` |
| `saa.metrics.request` | Request for code quality metrics | `QualityMetricsRequest` |
| `saa.rule.update` | Update analysis rules | `RuleUpdateRequest` |
| `saa.trend.request` | Request for trend analysis | `TrendAnalysisRequest` |
| `system.file.changed` | Notification of file changes | `FileChangeNotification` |

## Data Types

### CodeAnalysisRequest

Request for code analysis.

```typescript
interface CodeAnalysisRequest {
  filePaths: string[];
  ruleSets?: Array<'security' | 'quality' | 'performance' | 'custom'>;
  ruleIds?: string[];
  excludedRuleIds?: string[];
  severity?: 'info' | 'warning' | 'error' | 'all';
  reportFormat?: 'json' | 'html' | 'markdown';
  includeMetrics?: boolean;
  includeSuggestions?: boolean;
}
```

### CodeAnalysisResponse

Response with code analysis results.

```typescript
interface CodeAnalysisResponse {
  results: Array<{
    filePath: string;
    issues: Array<{
      ruleId: string;
      message: string;
      line: number;
      column?: number;
      severity: 'info' | 'warning' | 'error';
      category: 'security' | 'quality' | 'performance' | 'style';
      suggestion?: string;
      moreInfo?: string;
    }>;
    metrics?: {
      complexity: number;
      maintainability: number;
      testCoverage?: number;
      duplication?: number;
    };
  }>;
  summary: {
    totalFiles: number;
    totalIssues: number;
    issuesBySeverity: {
      error: number;
      warning: number;
      info: number;
    };
    issuesByCategory: {
      security: number;
      quality: number;
      performance: number;
      style: number;
    };
    qualityScore: number;
  };
}
```

### QualityMetricsRequest

Request for code quality metrics.

```typescript
interface QualityMetricsRequest {
  scope?: 'file' | 'directory' | 'project';
  path?: string;
  metrics?: Array<'complexity' | 'maintainability' | 'security' | 'duplication'>;
  detailed?: boolean;
}
```

### QualityMetricsUpdate

Update to code quality metrics.

```typescript
interface QualityMetricsUpdate {
  scope: 'file' | 'directory' | 'project';
  path?: string;
  metrics: {
    complexity: number;
    maintainability: number;
    security: number;
    duplication?: number;
    testCoverage?: number;
    qualityScore: number;
  };
  timestamp: string;
}
```

### RuleUpdateRequest

Request to update analysis rules.

```typescript
interface RuleUpdateRequest {
  action: 'add' | 'update' | 'remove' | 'enable' | 'disable';
  ruleId?: string;
  ruleDefinition?: {
    id: string;
    name: string;
    description: string;
    category: 'security' | 'quality' | 'performance' | 'style';
    severity: 'info' | 'warning' | 'error';
    enabled: boolean;
    parameters?: Record<string, any>;
  };
}
```

### IssueNotification

Notification of a detected issue.

```typescript
interface IssueNotification {
  filePath: string;
  ruleId: string;
  message: string;
  line: number;
  column?: number;
  severity: 'info' | 'warning' | 'error';
  category: 'security' | 'quality' | 'performance' | 'style';
  timestamp: string;
  commitId?: string;
  suggestion?: string;
}
```

### TrendAnalysisRequest

Request for trend analysis.

```typescript
interface TrendAnalysisRequest {
  period: 'day' | 'week' | 'month' | 'quarter';
  metrics: Array<'complexity' | 'maintainability' | 'security' | 'issues'>;
  scope?: 'project' | 'directory';
  path?: string;
  groupBy?: 'day' | 'week' | 'commit';
}
```

### TrendAnalysisResponse

Response with trend analysis results.

```typescript
interface TrendAnalysisResponse {
  period: 'day' | 'week' | 'month' | 'quarter';
  dataPoints: Array<{
    timestamp: string;
    commitId?: string;
    metrics: {
      complexity?: number;
      maintainability?: number;
      security?: number;
      issues?: number;
      qualityScore?: number;
    };
  }>;
  trends: {
    complexity?: 'increasing' | 'decreasing' | 'stable';
    maintainability?: 'increasing' | 'decreasing' | 'stable';
    security?: 'increasing' | 'decreasing' | 'stable';
    issues?: 'increasing' | 'decreasing' | 'stable';
    qualityScore?: 'increasing' | 'decreasing' | 'stable';
  };
}
```

## Python Client Example

```python
from core.message_bus import MessageBus

async def analyze_code_quality(message_bus: MessageBus, file_paths):
    """Analyze code quality for the specified files."""
    response = await message_bus.request(
        topic="saa.analysis.request",
        message={
            "filePaths": file_paths,
            "ruleSets": ["quality", "security"],
            "severity": "warning",
            "reportFormat": "markdown",
            "includeMetrics": True
        },
        response_topic="saa.analysis.response"
    )
    return response
```
