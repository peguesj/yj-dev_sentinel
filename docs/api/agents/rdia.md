# README Documentation Inspector Agent API

This document describes the API endpoints and messages for interacting with the README Documentation Inspector Agent (RDIA).

## Message Bus Topics

### Published Topics

Topics that the RDIA publishes messages to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `rdia.analysis.response` | Response to markdown analysis requests | `MarkdownAnalysisResponse` |
| `rdia.validation.response` | Response to README validation requests | `ReadmeValidationResponse` |
| `rdia.improvement.suggestion` | Suggestions for documentation improvements | `DocImprovement` |
| `rdia.structure.response` | Response to structure check requests | `StructureResponse` |

### Subscribed Topics

Topics that the RDIA subscribes to:

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `rdia.analysis.request` | Request for markdown analysis | `MarkdownAnalysisRequest` |
| `rdia.validation.request` | Request for README validation | `ReadmeValidationRequest` |
| `rdia.improvement.request` | Request for documentation improvement suggestions | `DocImprovementRequest` |
| `rdia.structure.request` | Request for documentation structure check | `StructureRequest` |
| `system.file.changed` | Notification of file changes | `FileChangeNotification` |

## Data Types

### MarkdownAnalysisRequest

Request for markdown analysis.

```typescript
interface MarkdownAnalysisRequest {
  filePath: string;
  checkLinks?: boolean;
  checkImages?: boolean;
  checkFormatting?: boolean;
  checkStructure?: boolean;
}
```

### MarkdownAnalysisResponse

Response with markdown analysis results.

```typescript
interface MarkdownAnalysisResponse {
  filePath: string;
  issues: Array<{
    type: 'link' | 'image' | 'formatting' | 'structure' | 'content';
    location?: string;
    line?: number;
    message: string;
    severity: 'info' | 'warning' | 'error';
    suggestion?: string;
  }>;
  metrics: {
    wordCount: number;
    headingCount: number;
    linkCount: number;
    brokenLinkCount?: number;
    imageCount: number;
    codeBlockCount: number;
    readabilityScore?: number;
  };
}
```

### ReadmeValidationRequest

Request for README validation.

```typescript
interface ReadmeValidationRequest {
  filePath: string;
  standardLevel?: 'basic' | 'standard' | 'comprehensive';
  requiredSections?: string[];
  checkBadges?: boolean;
  checkLinks?: boolean;
}
```

### ReadmeValidationResponse

Response with README validation results.

```typescript
interface ReadmeValidationResponse {
  filePath: string;
  valid: boolean;
  missingRequiredSections?: string[];
  issues: Array<{
    type: 'missing_section' | 'incomplete_section' | 'badge' | 'link' | 'structure';
    section?: string;
    message: string;
    severity: 'info' | 'warning' | 'error';
    recommendation?: string;
  }>;
  metrics: {
    sectionCount: number;
    completeness: number;
    badgeCount?: number;
    exampleCount?: number;
    imageCount?: number;
  };
}
```

### DocImprovementRequest

Request for documentation improvement suggestions.

```typescript
interface DocImprovementRequest {
  filePath: string;
  section?: string;
  improvementTypes?: Array<'structure' | 'content' | 'clarity' | 'examples'>;
}
```

### DocImprovement

Documentation improvement suggestion.

```typescript
interface DocImprovement {
  filePath: string;
  section?: string;
  currentContent?: string;
  suggestedContent: string;
  improvementReason: string;
  type: 'structure' | 'content' | 'clarity' | 'examples';
}
```

### StructureRequest

Request for documentation structure check.

```typescript
interface StructureRequest {
  directories: string[];
  validateCrossLinks?: boolean;
  validateNavigation?: boolean;
  validateConsistency?: boolean;
}
```

### StructureResponse

Response with documentation structure check results.

```typescript
interface StructureResponse {
  valid: boolean;
  issues: Array<{
    type: 'missing_file' | 'broken_link' | 'inconsistent_structure' | 'orphaned_file';
    path?: string;
    message: string;
    severity: 'info' | 'warning' | 'error';
    recommendation?: string;
  }>;
  metrics: {
    fileCount: number;
    directoryCount: number;
    brokenLinkCount: number;
    orphanedFileCount: number;
    consistencyScore: number;
  };
}
```

## Python Client Example

```python
from core.message_bus import MessageBus

async def validate_readme(message_bus: MessageBus, file_path="README.md"):
    """Validate a README file against best practices."""
    response = await message_bus.request(
        topic="rdia.validation.request",
        message={
            "filePath": file_path,
            "standardLevel": "comprehensive",
            "checkLinks": True,
            "checkBadges": True
        },
        response_topic="rdia.validation.response"
    )
    return response
```
