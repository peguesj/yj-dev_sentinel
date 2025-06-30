# System Architecture Overview

This document provides an overview of the Dev Sentinel system architecture, including the FORCE framework, agent architecture, and integration components.

## High-Level Architecture

Dev Sentinel is built on a modular architecture with the following key components:

1. **FORCE Framework**: Core engine providing tools, patterns, constraints, learning, and governance
2. **Autonomous Agents**: Specialized agents for various development tasks
3. **Message Bus**: Communication infrastructure for agent coordination
4. **Task Manager**: Manages task lifecycle and dependencies
5. **Integration Layer**: Connects Dev Sentinel to external systems

```ascii
┌────────────────────────────────────────────────────────────────────────┐
│                            Dev Sentinel                                │
├────────────┬─────────────────────────────┬───────────────┬─────────────┤
│   Agents   │      FORCE Framework        │ Message Bus   │     Task    │
│            │                             │               │   Manager   │
├────────────┼─────────────────────────────┼───────────────┼─────────────┤
│  VCMA      │ ┌─────────┬─────────────┐   │               │             │
│  VCLA      │ │  Tools  │  Patterns   │   │  Event-based  │  Task       │
│  CDIA      │ ├─────────┼─────────────┤   │  message      │  lifecycle  │
│  RDIA      │ │Constraint│  Learning  │   │  routing      │  management │
│  SAA       │ ├─────────┼─────────────┤   │               │             │
│            │ │Governance│             │   │               │             │
│            │ └─────────┴─────────────┘   │               │             │
├────────────┴─────────────────────────────┴───────────────┴─────────────┤
│                        Integration Layer                               │
├────────────┬─────────────────────────────┬───────────────┬─────────────┤
│ VS Code    │ Terminal Manager            │ YUNG Command  │ MCP Server  │
│ Extension  │                             │ Processor     │             │
└────────────┴─────────────────────────────┴───────────────┴─────────────┘
```

## FORCE Framework

The FORCE (Federated Orchestration & Reporting for Copilot Execution) Framework is the core engine of Dev Sentinel, providing:

1. **Tools**: Executable development actions (git operations, documentation tools, etc.)
2. **Patterns**: Reusable workflows for common tasks
3. **Constraints**: Quality rules and validations
4. **Learning**: System improvement through execution analysis
5. **Governance**: Policy enforcement for security and compliance

## Agent Architecture

Dev Sentinel implements the following specialized agents:

1. **Version Control Master Agent (VCMA)**: Manages git operations and version control workflows
2. **Version Control Listener Agent (VCLA)**: Monitors version control events and triggers reactions
3. **Code Documentation Inspector Agent (CDIA)**: Analyzes and enforces code documentation standards
4. **README Documentation Inspector Agent (RDIA)**: Ensures comprehensive project documentation
5. **Static Analysis Agent (SAA)**: Performs code quality and security analysis

## Communication and Coordination

Agents communicate through a central message bus that:

1. Routes events to appropriate agents
2. Enables publish/subscribe patterns
3. Supports synchronous and asynchronous communication
4. Provides message persistence

## Task Management

The Task Manager handles:

1. Task creation and assignment
2. Task dependencies and prioritization
3. Task state tracking
4. Task completion reporting

## Integration Architecture

Dev Sentinel integrates with external systems through:

1. **VS Code Integration**: Direct integration with VS Code through extensions
2. **Terminal Manager**: Controlled access to terminal for command execution
3. **YUNG Command Processor**: Parses and routes YUNG commands
4. **MCP Server**: Model Context Protocol server for AI assistant integration

## Data Flow

Data flows through the system as follows:

1. User or AI assistant initiates a command through VS Code or terminal
2. Command is parsed by YUNG Command Processor
3. Message Bus routes command to appropriate agent(s)
4. Agent executes command using FORCE Framework tools and patterns
5. Results are reported back through Message Bus
6. User receives results through VS Code or terminal
