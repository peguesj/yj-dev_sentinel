# Agent Architecture

## Overview

Dev Sentinel employs a multi-agent architecture where specialized agents collaborate to provide autonomous development assistance. Each agent is designed with a specific focus area and collaborates with other agents through the central message bus.

## Core Agent Architecture

All Dev Sentinel agents follow a common architectural pattern:

1. **Base Agent Structure**: Implemented in `core/agent.py`, providing:
   - Event-driven processing
   - Message bus integration
   - Task management
   - Configuration handling
   - Lifecycle management

2. **Specialized Agent Extensions**: Each agent type extends the base structure with:
   - Domain-specific logic
   - Specialized analysis capabilities
   - Custom tool integrations
   - Targeted response patterns

3. **Agent Communication**: All agents communicate through:
   - Central message bus
   - Event-driven subscriptions
   - Task delegation patterns
   - Context sharing mechanisms

## Agent Types

Dev Sentinel includes several specialized agent types:

| Agent Type | Purpose | Key Capabilities |
|------------|---------|------------------|
| Version Control Master Agent (VCMA) | Monitors and executes version control operations | Change monitoring, commit management, branch management |
| Version Control Listener Agent (VCLA) | Listens for and responds to version control events | Event monitoring, notification management, integration triggers |
| Code Documentation Inspector Agent (CDIA) | Analyzes and manages code documentation | Documentation analysis, quality assessment, generation assistance |
| README Documentation Inspector Agent (RDIA) | Focuses on README and markdown documentation | Format validation, content completeness checks, improvement suggestions |
| Static Analysis Agent (SAA) | Performs static code analysis | Code quality checks, security analysis, performance reviews |

## Integration Points

Agents integrate with other system components through:

1. **FORCE Framework**: Agents use FORCE tools, patterns, and constraints
2. **Message Bus**: Central communication channel for all agents
3. **Task Manager**: Coordinates task execution across agents
4. **MCP Protocol**: Integration with VS Code and external tools

## Implementation Details

For detailed specifications of each agent type, see the component documentation under [Components: Agents](/docs/components/agents/index.md).
