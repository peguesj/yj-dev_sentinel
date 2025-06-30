# Code Documentation Inspector Agent API

This document describes the API endpoints and messages for interacting with the Code Documentation Inspector Agent (CDIA).

## Message Bus Topics

### Published Topics

Topics that the CDIA publishes messages to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `cdia.analysis.response` | Response to documentation analysis requests | `DocAnalysisResponse` |
| `cdia.metrics.updated` | Published when documentation metrics are updated | `DocMetricsUpdate` |
| `cdia.improvement.suggestion` | Suggestions for documentation improvements | `DocImprovement` |
| `cdia.generation.response` | Response to documentation generation requests | `DocGenerationResponse` |

### Subscribed Topics

Topics that the CDIA subscribes to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `cdia.analysis.request` | Request for documentation analysis | `DocAnalysisRequest` |
| `cdia.metrics.request` | Request for documentation metrics | `DocMetricsRequest` |
| `cdia.improvement.request` | Request for documentation improvement suggestions | `DocImprovementRequest` |
| `cdia.generation.request` | Request for documentation generation | `DocGenerationRequest` |
| `system.file.changed` | Notification of file changes | `FileChangeNotification` |

## Data Types

### DocAnalysisRequest

Request for documentation analysis.

```typescript
interface DocAnalysisRequest {
  filePaths: string[];
  detailed?: boolean;
  checkTypes?: boolean;
  checkExamples?: boolean;
  checkCoverage?: boolean;
  formats?: Array<'html' | 'markdown' | 'json'>;
}
```

### DocAnalysisResponse

Response with documentation analysis results.

```typescript
interface DocAnalysisResponse {
  results: Array<{
    filePath: string;
    coverage: number;
    issues: Array<{
      type: 'missing' | 'incomplete' | 'outdated' | 'formatting';
      location: string;
      message: string;
      severity: 'info' | 'warning' | 'error';
      suggestion?: string;
    }>;
    metrics: {
      totalSymbols: number;
      documentedSymbols: number;
      coveragePercentage: number;
      qualityScore: number;
    };
  }>;
  summary: {
    totalFiles: number;
    totalIssues: number;
    averageCoverage: number;
    averageQuality: number;
  };
}
```

### DocMetricsRequest

Request for documentation metrics.

```typescript
interface DocMetricsRequest {
  scope?: 'file' | 'directory' | 'project';
  path?: string;
  detailed?: boolean;
}
```

### DocMetricsUpdate

Update to documentation metrics.

```typescript
interface DocMetricsUpdate {
  scope: 'file' | 'directory' | 'project';
  path?: string;
  metrics: {
    totalSymbols: number;
    documentedSymbols: number;
    coveragePercentage: number;
    qualityScore: number;
    typeAnnotationPercentage?: number;
    examplePercentage?: number;
  };
  timestamp: string;
}
```

### DocImprovementRequest

Request for documentation improvement suggestions.

```typescript
interface DocImprovementRequest {
  filePath: string;
  symbolPath?: string;
  improvementTypes?: Array<'coverage' | 'clarity' | 'examples' | 'format'>;
}
```

### DocImprovement

Documentation improvement suggestion.

```typescript
interface DocImprovement {
  filePath: string;
  symbolPath?: string;
  currentDoc?: string;
  suggestedDoc: string;
  improvementReason: string;
  type: 'coverage' | 'clarity' | 'examples' | 'format';
}
```

### DocGenerationRequest

Request for documentation generation.

```typescript
interface DocGenerationRequest {
  filePath: string;
  symbolPaths?: string[];
  style?: 'google' | 'numpy' | 'sphinx' | 'jsdoc';
  includeTypes?: boolean;
  includeExamples?: boolean;
}
```

### DocGenerationResponse

Response with generated documentation.

```typescript
interface DocGenerationResponse {
  filePath: string;
  results: Array<{
    symbolPath: string;
    generatedDoc: string;
  }>;
  appliedChanges: boolean;
}
```

## Python Client Example

```python
from core.message_bus import MessageBus

async def analyze_file_documentation(message_bus: MessageBus, file_path):
    """Analyze documentation in a file."""
    response = await message_bus.request(
        topic="cdia.analysis.request",
        message={
            "filePaths": [file_path],
            "detailed": True,
            "checkCoverage": True
        },
        response_topic="cdia.analysis.response"
    )
    return response
```
