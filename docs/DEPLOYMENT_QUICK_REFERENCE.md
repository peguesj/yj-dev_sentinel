# Dev Sentinel Deployment Quick Reference

## Quick Install Commands

### From Git Repository
```bash
# Latest version
pip install git+https://github.com/peguesj/yj-dev_sentinel.git

# Specific version
pip install git+https://github.com/peguesj/yj-dev_sentinel.git@v0.3.0

# With dev dependencies
pip install "git+https://github.com/peguesj/yj-dev_sentinel.git[dev]"
```

### Development Setup
```bash
git clone https://github.com/peguesj/yj-dev_sentinel.git
cd yj-dev_sentinel
pip install -e .
```

### Verify Installation
```bash
dev-sentinel --version
force-mcp-stdio --help
dev-sentinel status
```

## Available CLI Commands

| Command | Description |
|---------|-------------|
| `dev-sentinel` | Main CLI interface |
| `force-mcp-stdio` | Force MCP server (stdio) |
| `dev-sentinel-stdio` | Dev Sentinel MCP server (stdio) |
| `force-mcp-http` | Force MCP server (HTTP) |
| `dev-sentinel-http` | Dev Sentinel MCP server (HTTP) |

## Docker Quick Start

```bash
# Test installation
docker run -it python:3.10 bash -c "
  pip install git+https://github.com/peguesj/yj-dev_sentinel.git &&
  dev-sentinel --version
"

# Run HTTP server
docker run -p 8080:8080 python:3.10 bash -c "
  pip install git+https://github.com/peguesj/yj-dev_sentinel.git &&
  force-mcp-http --port 8080 --host 0.0.0.0
"
```

## Environment Variables

```bash
export PYTHONUNBUFFERED=1
export FORCE_DEBUG=0
export ENVIRONMENT=production
```

## Common Use Cases

### VS Code Integration
```json
{
  "mcpServers": {
    "force_mcp_stdio": {
      "command": "force-mcp-stdio",
      "cwd": "${workspaceFolder}",
      "env": {
        "PATH": "${workspaceFolder}/.venv/bin:${env:PATH}"
      }
    }
  }
}
```

### Production Server
```bash
# Install and start HTTP server
pip install git+https://github.com/peguesj/yj-dev_sentinel.git
force-mcp-http --port 8080 --host 0.0.0.0
```

### Development with Hot Reload
```bash
# Clone and develop
git clone https://github.com/peguesj/yj-dev_sentinel.git
cd yj-dev_sentinel
pip install -e .
force-mcp-stdio --debug
```

---

📚 **Full Documentation**: [docs/deployment.md](./deployment.md)  
🔧 **MCP Examples**: [examples/mcp-configurations/](../examples/mcp-configurations/)  
🏠 **Home**: [README.md](../README.md)
