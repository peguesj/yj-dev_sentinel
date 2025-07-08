# Dev Sentinel MCP Server Configurations

This directory contains example MCP (Model Context Protocol) server configurations for integrating Dev Sentinel with various AI development environments.

## Quick Start

### 1. Install Dev Sentinel Package
```bash
pip install dev-sentinel
# or for development
pip install -e .
```

### 2. Verify Installation
```bash
dev-sentinel --version
force-mcp-stdio --help
```

### 3. Choose Your Integration

## Available MCP Servers

### Core Servers

| Server | Transport | Command | Description |
|--------|-----------|---------|-------------|
| **Force MCP** | stdio | `force-mcp-stdio` | Primary Force framework server with development tools |
| **Dev Sentinel** | stdio | `dev-sentinel-stdio` | Full Dev Sentinel with AI agents |
| **Force HTTP** | http | `force-mcp-http` | Force server with HTTP transport |
| **Dev Sentinel HTTP** | http | `dev-sentinel-http` | Dev Sentinel with HTTP API |

## Configuration Files

### VS Code Integration (`vscode-mcp.json`)
Complete VS Code MCP extension configuration with all four servers.

**Setup:**
1. Copy `vscode-mcp.json` to your VS Code settings
2. Update `${workspaceFolder}` paths if needed
3. Ensure your virtual environment is activated
4. Restart VS Code

**Features:**
- Auto-detection of workspace folder
- Environment variable inheritance
- Debug logging support
- Proper timeout handling

### Claude Desktop (`claude-mcp.json`)
Configuration for Claude Desktop application.

**Setup:**
1. Copy content to Claude's MCP configuration
2. Update `/path/to/your/project` with actual paths
3. Ensure virtual environment paths are correct

**Usage:**
- Basic integration: Uses `force-mcp-stdio`
- Advanced: Includes debug and custom directory options
- Validation: Run validation checks without starting server

### Generic MCP Client (`generic-mcp.json`)
Universal configuration for any MCP-compatible client.

**Features:**
- Complete server metadata
- Usage examples
- Installation instructions
- Capability descriptions

## Configuration Examples

### Basic Force MCP Server
```bash
force-mcp-stdio
```

### Debug Mode
```bash
force-mcp-stdio --debug
```

### Validation Only
```bash
force-mcp-stdio --validation-only
```

### HTTP Server
```bash
force-mcp-http --port 8080
```

### Custom Force Directory
```bash
force-mcp-stdio --force-dir /custom/path/.force
```

## Environment Setup

### Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install package
pip install -e .
```

### Environment Variables
Key environment variables for MCP servers:

- `PATH`: Include virtual environment bin directory
- `PYTHONUNBUFFERED=1`: Ensure proper stdout/stderr handling
- `FORCE_DEBUG=1`: Enable Force framework debug logging
- `PYTHONPATH`: Set if using custom package locations

## Server Capabilities

### Force MCP Server
- **Tools**: 40+ development automation tools
- **Patterns**: Workflow patterns and best practices
- **Constraints**: Development constraints and validations
- **Learning**: Capture and apply development insights
- **Validation**: Component health checks and fixes

### Dev Sentinel Server
- **AI Agents**: Specialized development agents
- **Task Management**: Automated task orchestration
- **Message Bus**: Inter-agent communication
- **Integration**: Fast-agent framework integration
- **HTTP API**: RESTful API for external integrations

## Troubleshooting

### Common Issues

#### Command Not Found
```bash
# Check installation
pip list | grep dev-sentinel

# Verify PATH
which force-mcp-stdio

# Reinstall if needed
pip install -e . --force-reinstall
```

#### Import Errors
```bash
# Check Python path
python -c "import dev_sentinel; print('OK')"

# Verify virtual environment
which python
pip list
```

#### MCP Connection Issues
```bash
# Test server directly
force-mcp-stdio --validation-only

# Check debug output
force-mcp-stdio --debug
```

#### Force Validation Errors
```bash
# Run validation
force-mcp-stdio --validation-only

# Check Force directory
ls -la .force/

# Initialize if needed
dev-sentinel init
```

### Debug Mode
Enable debug logging for troubleshooting:

```bash
# Server debug
force-mcp-stdio --debug

# Environment debug
FORCE_DEBUG=1 force-mcp-stdio

# Validation debug
force-mcp-stdio --debug --validation-only
```

## Advanced Configuration

### Custom Transport Settings
```json
{
  "transport": "stdio",
  "timeout": 60000,
  "reconnectAttempts": 5,
  "reconnectDelay": 3000
}
```

### Environment Customization
```json
{
  "env": {
    "PATH": "/custom/venv/bin:$PATH",
    "PYTHONUNBUFFERED": "1",
    "FORCE_DEBUG": "1",
    "FORCE_CONFIG_PATH": "/custom/config"
  }
}
```

### Argument Customization
```json
{
  "args": [
    "--debug",
    "--force-dir", "/custom/force",
    "--no-auto-fix"
  ]
}
```

## Integration Examples

### VS Code Extension
```json
{
  "mcpServers": {
    "dev-sentinel": {
      "command": "force-mcp-stdio",
      "cwd": "${workspaceFolder}",
      "env": {
        "PATH": "${workspaceFolder}/.venv/bin:${env:PATH}"
      }
    }
  }
}
```

### Claude Desktop
```json
{
  "mcpServers": {
    "dev-sentinel": {
      "command": "force-mcp-stdio",
      "cwd": "/path/to/project"
    }
  }
}
```

### Custom MCP Client
```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def connect_to_dev_sentinel():
    server_params = StdioServerParameters(
        command="force-mcp-stdio",
        args=["--debug"]
    )
    
    async with ClientSession(server_params) as session:
        # Initialize connection
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {len(tools)}")

# Run the example
asyncio.run(connect_to_dev_sentinel())
```

## Support

### Documentation
- [Dev Sentinel Documentation](https://dev-sentinel.readthedocs.io)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Force Framework Guide](./docs/force/)

### Community
- [GitHub Issues](https://github.com/peguesj/yj-dev_sentinel/issues)
- [GitHub Discussions](https://github.com/peguesj/yj-dev_sentinel/discussions)

### Getting Help
1. Check server status: `dev-sentinel status`
2. Run validation: `force-mcp-stdio --validation-only`
3. Enable debug mode: `force-mcp-stdio --debug`
4. Check logs and error messages
5. Create GitHub issue with details

---

**Version**: 0.3.0  
**Updated**: July 2, 2025  
**Compatibility**: MCP Protocol v1.0+
