# Agent APIs

This section documents the APIs for interacting with Dev Sentinel's autonomous agents.

## Agent Communication

All agents communicate through the central message bus using an event-based publish/subscribe pattern. Agents expose their functionality through well-defined message topics and data formats.

## Common Message Patterns

Agents support the following common message patterns:

1. **Command Pattern**: Request an agent to perform an action

   ```plain
   <agent-id>.<command>.<request|response>
   ```

2. **Status Pattern**: Get or receive updates about agent status

   ```plain
   <agent-id>.status.<update|request>
   ```

3. **Event Pattern**: Notifications about events detected by an agent

   ```plain
   <agent-id>.<event-type>.<detected|processed>
   ```

## Agent-Specific APIs

| Agent | Description | API Documentation |
|-------|-------------|------------------|
| [Version Control Master Agent (VCMA)](vcma.md) | Manages version control operations | [API](vcma.md) |
| [Version Control Listener Agent (VCLA)](vcla.md) | Listens for version control events | [API](vcla.md) |
| [Code Documentation Inspector Agent (CDIA)](cdia.md) | Analyzes code documentation | [API](cdia.md) |
| [README Documentation Inspector Agent (RDIA)](rdia.md) | Inspects README and markdown docs | [API](rdia.md) |
| [Static Analysis Agent (SAA)](saa.md) | Performs static code analysis | [API](saa.md) |

## Programmatic Usage

To interact with agents programmatically, use the message bus:

```python
from core.message_bus import MessageBus

# Get message bus instance
message_bus = MessageBus.get_instance()

# Subscribe to a topic
async def handle_vc_status(message):
    print(f"VC Status: {message}")

await message_bus.subscribe("vcma.status.update", handle_vc_status)

# Publish a message
await message_bus.publish("vcma.commit.request", {
    "files": ["file1.py", "file2.py"],
    "message": "Fix bug in login flow",
    "priority": "high"
})

# Request-response pattern
result = await message_bus.request(
    "vcma.commit.request", 
    {"files": ["file1.py"], "priority": "medium"},
    "vcma.commit.completed"
)
```

## JavaScript/TypeScript Client

For front-end integration, a JavaScript client is available:

```typescript
import { DevSentinelClient } from '@dev-sentinel/client';

const client = new DevSentinelClient();

// Subscribe to a topic
client.subscribe('vcma.status.update', (message) => {
  console.log('VC Status:', message);
});

// Send a command
client.sendCommand('vcma.commit.request', {
  files: ['file1.js', 'file2.js'],
  message: 'Update authentication flow',
  priority: 'medium'
});
```
