# FORCE Framework APIs

This section provides API documentation for the FORCE framework, which enables interaction with the core FORCE components: tools, patterns, constraints, learning, and governance.

## API Overview

The FORCE framework exposes several API endpoints for programmatic interaction:

1. **Tools API**: For invoking and managing FORCE tools
2. **Patterns API**: For executing and managing patterns
3. **Constraints API**: For checking and managing constraints
4. **Learning API**: For interacting with the learning system
5. **Governance API**: For applying and checking governance rules

## Message Bus Topics

FORCE components communicate through the following message bus topics:

### Published Topics

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `force.tool.completed` | Published when a tool execution completes | `ToolExecutionResult` |
| `force.pattern.completed` | Published when a pattern execution completes | `PatternExecutionResult` |
| `force.constraint.violation` | Published when a constraint violation is detected | `ConstraintViolation` |
| `force.learning.insight` | Published when the learning system generates an insight | `LearningInsight` |
| `force.governance.decision` | Published when a governance decision is made | `GovernanceDecision` |

### Subscribed Topics

| Topic | Description | Message Format |
|-------|-------------|---------------|
| `force.tool.execute` | Request to execute a tool | `ToolExecutionRequest` |
| `force.pattern.execute` | Request to execute a pattern | `PatternExecutionRequest` |
| `force.constraint.check` | Request to check constraints | `ConstraintCheckRequest` |
| `force.learning.query` | Query the learning system | `LearningQuery` |
| `force.governance.check` | Request a governance check | `GovernanceCheckRequest` |

## Data Types

### Tool API

#### ToolExecutionRequest

```typescript
interface ToolExecutionRequest {
  toolName: string;
  parameters: Record<string, any>;
  context?: Record<string, any>;
  async?: boolean;
  timeout?: number;
  callbackTopic?: string;
}
```

#### ToolExecutionResult

```typescript
interface ToolExecutionResult {
  toolName: string;
  success: boolean;
  result?: any;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  executionTime: number;
  timestamp: string;
}
```

### Pattern API

#### PatternExecutionRequest

```typescript
interface PatternExecutionRequest {
  patternName: string;
  parameters: Record<string, any>;
  context?: Record<string, any>;
  async?: boolean;
  timeout?: number;
  callbackTopic?: string;
}
```

#### PatternExecutionResult

```typescript
interface PatternExecutionResult {
  patternName: string;
  success: boolean;
  result?: any;
  steps: Array<{
    stepName: string;
    toolName?: string;
    success: boolean;
    result?: any;
    error?: {
      code: string;
      message: string;
    };
  }>;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  executionTime: number;
  timestamp: string;
}
```

### Constraint API

#### ConstraintCheckRequest

```typescript
interface ConstraintCheckRequest {
  constraintName?: string;
  constraintType?: string;
  context: Record<string, any>;
  content?: any;
  enforceLevel?: 'info' | 'warn' | 'error' | 'block';
}
```

#### ConstraintViolation

```typescript
interface ConstraintViolation {
  constraintName: string;
  constraintType: string;
  level: 'info' | 'warn' | 'error' | 'block';
  message: string;
  location?: {
    file?: string;
    line?: number;
    column?: number;
  };
  context?: Record<string, any>;
  suggestion?: string;
  timestamp: string;
}
```

### Learning API

#### LearningQuery

```typescript
interface LearningQuery {
  queryType: 'insight' | 'recommendation' | 'history' | 'metrics';
  context?: Record<string, any>;
  filters?: Record<string, any>;
  limit?: number;
}
```

#### LearningInsight

```typescript
interface LearningInsight {
  insightType: 'pattern' | 'tool' | 'performance' | 'quality';
  target: string;
  confidence: number;
  description: string;
  recommendation?: string;
  metrics?: Record<string, any>;
  timestamp: string;
}
```

### Governance API

#### GovernanceCheckRequest

```typescript
interface GovernanceCheckRequest {
  action: string;
  resource: string;
  context?: Record<string, any>;
  user?: string;
  role?: string;
}
```

#### GovernanceDecision

```typescript
interface GovernanceDecision {
  action: string;
  resource: string;
  allowed: boolean;
  reason?: string;
  policy?: string;
  conditions?: Record<string, any>;
  timestamp: string;
}
```

## Python Client Examples

### Tool Execution

```python
from core.message_bus import MessageBus

async def execute_tool(message_bus: MessageBus, tool_name, parameters):
    """Execute a FORCE tool."""
    result = await message_bus.request(
        topic="force.tool.execute",
        message={
            "toolName": tool_name,
            "parameters": parameters,
            "async": False
        },
        response_topic="force.tool.completed"
    )
    return result
```

### Pattern Execution

```python
from core.message_bus import MessageBus

async def execute_pattern(message_bus: MessageBus, pattern_name, parameters):
    """Execute a FORCE pattern."""
    result = await message_bus.request(
        topic="force.pattern.execute",
        message={
            "patternName": pattern_name,
            "parameters": parameters,
            "async": False
        },
        response_topic="force.pattern.completed"
    )
    return result
```

### Constraint Checking

```python
from core.message_bus import MessageBus

async def check_constraints(message_bus: MessageBus, context, content=None):
    """Check constraints for given context and content."""
    result = await message_bus.request(
        topic="force.constraint.check",
        message={
            "context": context,
            "content": content,
            "enforceLevel": "warn"
        },
        response_topic="force.constraint.result"
    )
    return result
```

## REST API

The FORCE framework also exposes a REST API for external integration:

### Tool Execution Endpoint

```http
POST /api/v1/force/tools/{tool_name}
```

Request Body:

```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "context": {
    "contextKey": "contextValue"
  }
}
```

### Pattern Execution Endpoint

```http
POST /api/v1/force/patterns/{pattern_name}
```

Request Body:

```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "context": {
    "contextKey": "contextValue"
  }
}
```

### Constraint Checking Endpoint

```http
POST /api/v1/force/constraints/check
```

Request Body:

```json
{
  "constraintType": "quality",
  "context": {
    "file": "path/to/file.py"
  },
  "content": "file content to check",
  "enforceLevel": "warn"
}
```
