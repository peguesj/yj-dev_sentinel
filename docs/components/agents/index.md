# Agent Components

This section provides detailed documentation for each agent type in the Dev Sentinel system.

## Available Agents

Dev Sentinel includes the following specialized agent types:

### [Version Control Master Agent (VCMA)](vcma.md)

The VCMA is responsible for monitoring development activities, identifying code changes that warrant version control operations, and executing those operations autonomously. It serves as the primary observer for version control-related activities.

### [Version Control Listener Agent (VCLA)](vcla.md)

The VCLA listens for version control events (commits, pushes, pulls, merges) and triggers appropriate responses or notifications. It serves as the event responder for version control operations.

### [Code Documentation Inspector Agent (CDIA)](cdia.md)

The CDIA analyzes code documentation, validates quality, and suggests improvements. It ensures that code is properly documented according to project standards.

### [README Documentation Inspector Agent (RDIA)](rdia.md)

The RDIA focuses specifically on README and markdown documentation files, ensuring they are complete, accurate, and well-structured.

### [Static Analysis Agent (SAA)](saa.md)

The SAA performs static code analysis to identify quality, security, and performance issues in the codebase.

## Agent Implementation

All agents are implemented as extensions of the base Agent class defined in `core/agent.py`. For implementation details, see the respective agent documentation pages linked above.

## Adding New Agents

To add a new agent type to Dev Sentinel:

1. Create a new agent class that extends the base Agent class
2. Implement required interfaces and methods
3. Register the agent with the message bus
4. Configure the agent in the configuration files
5. Create appropriate documentation in this section

For detailed development guidelines, see the [Developer Guide](/docs/developer/index.md).
