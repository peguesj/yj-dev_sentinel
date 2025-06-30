# Version Control Listener Agent (VCLA)

> Version: 0.1.0

## Overview

The Version Control Listener Agent (VCLA) is responsible for monitoring and responding to version control events such as commits, pushes, pulls, and merges. It acts as a notification and integration bridge between the version control system and other components of Dev Sentinel.

## Core Capabilities

### Event Monitoring

The VCLA continuously monitors version control events:

- Commit events (local and remote)
- Push and pull events
- Branch creation and deletion events
- Merge and rebase events
- Tag creation and deletion events

### Event Processing

The agent processes version control events to determine appropriate responses:

- Event classification by type and importance
- Context attachment with metadata
- Correlation with previous events
- Priority determination

### Notification Management

Generation and routing of notifications based on events:

- Team notifications for significant changes
- Integration triggers for CI/CD pipelines
- Status updates for connected systems
- Custom notification rules based on configuration

### History Tracking

Maintains a historical record of version control events:

- Event sequence tracking
- Change pattern analysis
- Contribution statistics
- Historical trend reporting

## System Interfaces

### Input Interfaces

The VCLA accepts the following inputs:

- Raw version control events from Git hooks
- System status queries
- Notification configuration updates
- History and statistics queries

### Output Interfaces

The VCLA produces the following outputs:

- Formatted event notifications
- Integration triggers
- Statistical reports
- Historical event queries

## Implementation

The VCLA is implemented in `agents/vcla/vcla_agent.py` and follows the standard Dev Sentinel agent architecture. It extends the base `Agent` class and implements the required interfaces.

### Key Components

- **EventMonitor**: Listens for version control events
- **EventProcessor**: Processes and classifies events
- **NotificationManager**: Manages notification delivery
- **HistoryTracker**: Maintains event history

## Configuration

The VCLA can be configured in the `config/fastagent.config.yaml` file:

```yaml
agents:
  vcla:
    enabled: true
    notification_channels:
      - slack
      - email
      - system
    monitored_events:
      - commit
      - push
      - merge
      - branch
    history_retention_days: 30
```

## Usage

The VCLA operates automatically but can also be queried:

```python
# Get recent version control events
await message_bus.request(
    topic="vcla.history.query",
    message={
        "event_types": ["commit", "push"],
        "limit": 10
    },
    response_topic="vcla.history.response"
)
```

## Related Components

- [Version Control Master Agent (VCMA)](vcma.md) - Active version control management
- [Git Integration Tools](/docs/reference/tools/git-tools.md) - Tools for Git operations
