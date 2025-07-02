# Force MCP Integration Guide

**Version:** 0.3.0  
**Status:** ✅ Production Ready  
**Updated:** July 2, 2025

## Overview

The Force Model Context Protocol (MCP) server provides seamless integration between the Force framework and MCP-compatible clients like VS Code Copilot, Claude Desktop, and other AI assistants. This integration enables direct access to Force tools, patterns, constraints, and the extended schema system through natural language interactions.

## Key Features

### 🛠️ **Comprehensive Tool Access**
- Execute any of 38+ Force tools directly through MCP
- Real-time tool discovery and metadata retrieval
- Schema validation with extended schema support
- Contextual tool recommendations

### 📋 **Pattern Execution System**
- Apply development patterns with both executable and descriptive steps
- Support for complex workflows (atomic commits, documentation generation, etc.)
- Pattern discovery by category and complexity
- Step-by-step execution with user confirmation

### ✅ **Flexible Schema Validation**
- Extended schema system with relaxed enum constraints
- Custom category support (security, release management, monitoring, etc.)
- Backward compatibility with strict schema validation
- Comprehensive error reporting and suggestions

### 🔄 **Real-time Monitoring**
- Live execution feedback and progress reporting
- Comprehensive error handling and recovery
- Performance analytics and insights
- Tool usage tracking and optimization

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- VS Code (for VS Code integration) or Claude Desktop
- Active virtual environment with Force dependencies

### Quick Setup for VS Code

1. **Install MCP Extension** (if not already installed)
   
   Install the official MCP extension from the VS Code marketplace.

2. **Create MCP Configuration**

   Create or update `.vscode/mcp.json` in your workspace root:

   ```json
   {
     "servers": {
       "force_mcp_stdio": {
         "command": "${workspaceFolder}/.venv/bin/python",
         "args": ["${workspaceFolder}/integration/fast_agent/force_mcp_server.py"],
         "cwd": "${workspaceFolder}",
         "env": {
           "PYTHONPATH": "${workspaceFolder}",
           "PYTHONUNBUFFERED": "1"
         },
         "pattern": ".*(?:Force MCP server|Starting Force MCP server|Listening).*",
         "transport": "stdio",
         "timeout": 30000
       }
     }
   }
   ```

3. **Initialize Force System** (Optional but Recommended)

   ```bash
   # Initialize .force directory with extended schema and sample tools
   python -c "
   import sys; sys.path.append('.')
   from integration.fast_agent.force_mcp_server import main
   # The server will auto-initialize .force directory if needed
   "
   ```

4. **Test the Integration**

   Open VS Code Copilot Chat and try:

   ```text
   @force_mcp_stdio list all available Force tools
   @force_mcp_stdio show me tools in the security category
   @force_mcp_stdio execute force_tool_generator to create a new analysis tool
   ```

### Setup for Claude Desktop

1. **Update Claude Configuration**

   Edit your Claude Desktop configuration file (usually `~/.anthropic-desktop/mcp_servers.json`):

   ```json
   {
     "mcpServers": {
       "force_mcp_stdio": {
         "command": "/path/to/your/.venv/bin/python",
         "args": ["/path/to/dev_sentinel/integration/fast_agent/force_mcp_server.py"],
         "cwd": "/path/to/dev_sentinel",
         "env": {
           "PYTHONPATH": "/path/to/dev_sentinel",
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop**

3. **Test Integration**

   In Claude, you can now access Force tools:
   ```text
   Can you use the Force MCP server to list available development tools?
   Please execute the force_component_validator to check my project's Force components.
   ```

### Setup for Other MCP Clients

The Force MCP server follows the standard MCP protocol. Adapt the configuration above for your specific client:

- **Command**: Path to Python interpreter in your virtual environment
- **Arguments**: Path to `force_mcp_server.py`
- **Working Directory**: Project root directory
- **Environment**: Set `PYTHONPATH` to project root

## Extended Schema System

### Overview

The Force MCP server leverages the new Extended Schema System, which provides flexible validation while maintaining quality standards. This system addresses the limitations of overly restrictive enum constraints in the original schema.

### Key Benefits

1. **Flexible Categories**: Supports any tool category, not just predefined ones
2. **Open Error Handling**: Custom error handling strategies beyond the standard set
3. **Enhanced Execution**: Support for dynamic and adaptive execution patterns
4. **Better Tool Loading**: 38+ tools load successfully vs. 31 with strict schema

### Schema Loading Priority

The Force engine automatically selects the appropriate schema:

1. **Extended Schema** (`force-extended-schema.json`) - Preferred for flexibility
2. **Standard Schema** (`force-schema.json`) - Fallback for strict validation
3. **Error State** - If neither schema is available

### Migration from Strict Schema

If you're upgrading from the strict schema system:

1. **Automatic Migration**: The system automatically detects and uses the extended schema
2. **No Breaking Changes**: Existing tools continue to work without modification
3. **Enhanced Capabilities**: Previously failing tools now load and execute successfully

## Available MCP Tools

### Core Force Tools

| Tool | Description | Usage Example |
|------|-------------|---------------|
| `force_list_tools` | List all Force tools with metadata and categories | `list all security tools` |
| `force_execute_tool` | Execute any Force tool with parameters | `execute git_smart_commit with message "feat: add login"` |
| `force_list_patterns` | Browse development patterns by category | `show me all git workflow patterns` |
| `force_apply_pattern` | Apply patterns with executable/descriptive steps | `apply atomic_commit_pattern to stage my changes` |
| `force_check_constraints` | Validate code against quality constraints | `check constraints for Python files in src/` |
| `force_get_insights` | Get learning insights and recommendations | `show performance insights from last week` |

### System Management Tools

| Tool | Description | Usage Example |
|------|-------------|---------------|
| `force_component_validator` | Validate Force components for schema compliance | `validate all tools in my project` |
| `force_component_fix_system` | Fix common validation issues across components | `fix validation errors in my Force tools` |
| `force_mcp_integration` | Manage MCP integration and component loading | `check MCP server component status` |
| `force_sync` | Synchronize Force components between directories | `sync tools from default to project directory` |

### Generator Tools

| Tool | Description | Usage Example |
|------|-------------|---------------|
| `force_init_system` | Initialize Force directory structure | `set up Force system in my project` |
| `force_tool_generator` | Generate new Force tools | `create a security scanning tool` |
| `force_pattern_generator` | Generate development patterns | `create a code review pattern` |
| `force_constraint_generator` | Generate quality constraints | `create Python code quality constraints` |
| `force_mcp_component_generator` | Generate complete component sets | `create a complete testing toolset` |

## Usage Examples

### Basic Tool Discovery

```text
# List all available tools
@force_mcp_stdio list all Force tools

# Find tools by category
@force_mcp_stdio show me all security and analysis tools

# Get tool details
@force_mcp_stdio describe the git_smart_commit tool
```

### Tool Execution

```text
# Execute a simple tool
@force_mcp_stdio execute force_component_validator

# Execute with parameters
@force_mcp_stdio execute git_smart_commit with message "feat: add user authentication" and scope "backend"

# Dry run mode
@force_mcp_stdio execute code_quality_check in dry run mode for the src/ directory
```

### Pattern Application

```text
# List available patterns
@force_mcp_stdio show me development patterns for git workflows

# Apply a pattern
@force_mcp_stdio apply atomic_commit_pattern to organize my current changes

# Apply pattern with custom parameters
@force_mcp_stdio apply documentation_handoff_pattern for the authentication module
```

### Project Management

```text
# Initialize Force in a new project
@force_mcp_stdio initialize Force system in this project

# Generate project-specific tools
@force_mcp_stdio create a tool for automated testing of React components

# Validate project configuration
@force_mcp_stdio validate all Force components in this project
```

### Advanced Workflows

```text
# Multi-step development workflow
@force_mcp_stdio execute the following workflow:
1. Validate code quality for changed files
2. Apply atomic commit pattern
3. Generate documentation updates
4. Check security constraints

# Custom tool generation
@force_mcp_stdio generate a comprehensive toolset for:
- API security scanning
- Performance monitoring
- Documentation validation
- Release management
```

## Configuration Options

### Server Configuration

The Force MCP server supports several configuration options through environment variables:

```bash
# Enable debug logging
FORCE_DEBUG=true

# Set custom Force directory
FORCE_CONFIG_DIR=/path/to/custom/.force

# Enable extended schema (default: auto-detect)
FORCE_USE_EXTENDED_SCHEMA=true

# Set tool execution timeout (seconds)
FORCE_TOOL_TIMEOUT=300

# Enable performance monitoring
FORCE_ENABLE_METRICS=true
```

### Schema Configuration

Control schema validation behavior:

```bash
# Force strict schema usage (not recommended)
FORCE_STRICT_SCHEMA=true

# Custom schema path
FORCE_SCHEMA_PATH=/path/to/custom/schema.json

# Disable schema validation (not recommended)
FORCE_SKIP_VALIDATION=false
```

### Performance Configuration

Optimize server performance:

```bash
# Enable async tool execution
FORCE_ASYNC_EXECUTION=true

# Set concurrent tool limit
FORCE_MAX_CONCURRENT=5

# Enable result caching
FORCE_ENABLE_CACHE=true

# Cache TTL in seconds
FORCE_CACHE_TTL=3600
```

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Symptoms:**
- MCP client shows "Server failed to start" error
- No Force tools appear in tool list

**Solutions:**

```bash
# Check Python environment
which python
python --version

# Verify Force dependencies
pip list | grep -E "(force|mcp|jsonrpc)"

# Test server directly
python integration/fast_agent/force_mcp_server.py --test

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 2. Schema Validation Errors

**Symptoms:**
- Tools fail to load with schema validation errors
- "Category not in enum" errors

**Solutions:**

```bash
# Check extended schema presence
ls -la .force/schemas/force-extended-schema.json

# Validate schema manually
python -c "
from force import ForceEngine
engine = ForceEngine()
print(f'Schema type: {engine.get_schema_info()}')
print(f'Tools loaded: {len(engine.list_tools())}')
"

# Force schema regeneration
python -c "
from force.tools.system.force_init_system import force_init_system
force_init_system('.', regenerate_schema=True)
"
```

#### 3. Tool Discovery Issues

**Symptoms:**
- Some tools don't appear in listings
- Tool execution fails with "not found" errors

**Solutions:**

```bash
# Check tool registry
python -c "
from force import ForceEngine
engine = ForceEngine()
tools = engine.list_tools()
print(f'Total tools: {len(tools)}')
for tool in tools:
    print(f'  {tool[\"id\"]}: {tool[\"category\"]}')
"

# Verify tool paths
ls -la force/tools/*/
ls -la .force/tools/*/

# Resync tool directories
python -c "
from force.tools.system.force_sync import force_sync
force_sync(direction='default-to-project')
"
```

#### 4. Performance Issues

**Symptoms:**
- Slow tool execution
- Timeouts during operations
- High memory usage

**Solutions:**

```bash
# Enable performance monitoring
export FORCE_ENABLE_METRICS=true
export FORCE_DEBUG=true

# Check system resources
ps aux | grep force_mcp_server
top -p $(pgrep -f force_mcp_server)

# Optimize configuration
export FORCE_MAX_CONCURRENT=3
export FORCE_TOOL_TIMEOUT=120
```

### Debug Mode

Enable comprehensive debugging:

```bash
# Set debug environment
export FORCE_DEBUG=true
export FORCE_LOG_LEVEL=DEBUG
export PYTHONUNBUFFERED=1

# Run server in debug mode
python integration/fast_agent/force_mcp_server.py --debug
```

### Logging Configuration

Configure detailed logging:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('force_mcp_debug.log'),
        logging.StreamHandler()
    ]
)
```

## Security Considerations

### Access Control

The Force MCP server operates with the permissions of the user running it. Consider:

1. **File System Access**: The server can read/write files in the project directory
2. **Tool Execution**: Force tools can execute system commands and modify files
3. **Network Access**: Some tools may require network connectivity

### Best Practices

1. **Run in Isolated Environment**: Use virtual environments and containers when possible
2. **Review Tool Definitions**: Understand what each tool does before execution
3. **Monitor Execution**: Enable logging and monitoring for audit trails
4. **Limit Scope**: Use project-specific configurations to limit tool access

### Security Tools

The Force system includes several security-focused tools:

- `security_scan`: Automated security vulnerability scanning
- `secrets_detection`: Identify potential secrets in code
- `dependency_audit`: Check for vulnerable dependencies
- `infrastructure_security`: Validate infrastructure configurations

## Performance Optimization

### Tool Execution Optimization

1. **Async Execution**: Enable async mode for I/O-bound operations
2. **Concurrent Limits**: Set appropriate concurrent execution limits
3. **Caching**: Enable result caching for repeated operations
4. **Timeout Management**: Configure appropriate timeouts for different tool types

### Memory Management

1. **Tool Cleanup**: Ensure tools clean up resources after execution
2. **Result Limits**: Limit result size for large operations
3. **Garbage Collection**: Monitor and optimize Python garbage collection

### Network Optimization

1. **Connection Pooling**: Reuse connections for network-based tools
2. **Request Batching**: Batch similar requests when possible
3. **Timeout Configuration**: Set appropriate network timeouts

## API Reference

### MCP Protocol Methods

The Force MCP server implements the standard MCP protocol methods:

#### `tools/list`
Returns all available Force tools with metadata.

**Response:**
```json
{
  "tools": [
    {
      "name": "force_execute_tool",
      "description": "Execute any Force tool with validation",
      "inputSchema": {
        "type": "object",
        "properties": {
          "toolId": {"type": "string"},
          "parameters": {"type": "object"},
          "dryRun": {"type": "boolean"}
        }
      }
    }
  ]
}
```

#### `tools/call`
Executes a Force tool with specified parameters.

**Request:**
```json
{
  "name": "force_execute_tool",
  "arguments": {
    "toolId": "git_smart_commit",
    "parameters": {
      "message": "feat: add user authentication",
      "scope": "backend"
    },
    "dryRun": false
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Successfully executed git_smart_commit tool"
    }
  ]
}
```

### Force-Specific Extensions

The server also provides Force-specific capabilities:

- **Pattern Application**: Execute multi-step development patterns
- **Constraint Validation**: Check code against quality constraints
- **Learning Insights**: Retrieve analytics and recommendations
- **Component Management**: Validate and manage Force components

## Contributing

### Adding New MCP Tools

1. **Define Tool Schema**: Add tool definition to appropriate category
2. **Implement Handler**: Create handler function in `force_mcp_server.py`
3. **Add Tests**: Include comprehensive tests for new functionality
4. **Update Documentation**: Update this guide and inline documentation

### Extending Functionality

1. **New Protocols**: Add support for additional MCP protocol features
2. **Performance Enhancements**: Optimize execution and resource usage
3. **Security Features**: Enhance security and access control
4. **Integration Improvements**: Better integration with MCP clients

## Changelog

### Version 0.3.0 (Current)

- **Enhanced Pattern System**: Support for executable and descriptive steps
- **Extended Schema Integration**: Flexible validation with backward compatibility
- **Improved Error Handling**: Comprehensive error reporting and recovery
- **Performance Optimization**: Async execution and caching
- **Security Enhancements**: Better access control and audit logging
- **Documentation Updates**: Comprehensive guides and examples

### Previous Versions

See [CHANGELOG.md](../../CHANGELOG.md) for complete version history.

## Related Documentation

- [Force Framework Overview](../architecture/force/index.md)
- [Tool Development Guide](../developer/tool-development.md)
- [Pattern Creation Guide](../developer/pattern-development.md)
- [Schema Reference](../reference/schemas/index.md)
- [Security Guide](../user/security.md)

---

**Need Help?** Check the [troubleshooting section](#troubleshooting) or create an issue in the project repository.
