# Dev Sentinel: Force-Enabled Development Assistant

<div align="center">
  <img src="docs/diagrams/dev_sentinel_logo.svg" alt="Dev Sentinel Logo" width="200"/>
  
  [![Version: 0.3.0](https://img.shields.io/badge/Version-0.3.0-blue)](force/version.py)
  [![Built with: Python](https://img.shields.io/badge/Built%20with-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
  [![Architecture: Force-Enabled](https://img.shields.io/badge/Architecture-Force%20Enabled-009688?logo=blueprint&logoColor=white)](docs/architecture/force/index.md)
  [![Documentation: PlantUML](https://img.shields.io/badge/Documentation-PlantUML-orange?logo=diagram&logoColor=white)](docs/diagrams/)
  [![Force System: Active](https://img.shields.io/badge/Force%20System-Active-brightgreen?logo=star&logoColor=white)](docs/reference/tools/force-tools.md)
</div>

## Overview

Dev Sentinel is an autonomous development assistant that combines intelligent agents with the FORCE development framework. The system helps automate and streamline development tasks through tools, patterns, constraints, and continuous learning.

**Latest Release (v0.3.0)** brings enhanced Force tools structure, comprehensive git workflow automation, improved MCP server implementations, and modular documentation capabilities.

### Key Components

1. **Dev Sentinel Core**: Event-driven agent system that coordinates development tasks
2. **FORCE Framework**: Modular schema-driven development engine with:
   - **Tools**: Executable development actions
   - **Patterns**: Reusable workflows for common tasks
   - **Constraints**: Quality rules and validations
   - **Learning**: System improvement through execution analysis
   - **Governance**: Policy enforcement for security and compliance
3. **Autonomous Agents**: Specialized agents for version control, documentation, and analysis
4. **Model Context Protocol**: VS Code integration for intelligent assistance

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- VS Code (for MCP integration)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/peguesj/yj-dev_sentinel.git
cd yj-dev_sentinel

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\\Scripts\\activate   # Windows

# Install package with CLI commands
pip install -e .
```

### Package Installation

Dev Sentinel is available as a proper Python package with CLI commands:

```bash
# Install from source (development)
pip install -e .

# Verify installation
dev-sentinel --version
force-mcp-stdio --help
```

## Deployment Options

### Install from Git Repository

#### Direct Installation
```bash
# Install latest from main branch
pip install git+https://github.com/peguesj/yj-dev_sentinel.git

# Install specific version
pip install git+https://github.com/peguesj/yj-dev_sentinel.git@v0.3.0

# Install with optional dependencies
pip install "git+https://github.com/peguesj/yj-dev_sentinel.git[dev,docs]"
```

#### Development Installation
```bash
# Clone and install in editable mode
git clone https://github.com/peguesj/yj-dev_sentinel.git
cd yj-dev_sentinel
pip install -e .
```

#### Docker Deployment
```bash
# Quick Docker run
docker run -it python:3.10 bash -c "
  pip install git+https://github.com/peguesj/yj-dev_sentinel.git &&
  force-mcp-stdio --validation-only
"

# HTTP server deployment
docker run -p 8080:8080 python:3.10 bash -c "
  pip install git+https://github.com/peguesj/yj-dev_sentinel.git &&
  force-mcp-http --port 8080 --host 0.0.0.0
"
```

For comprehensive deployment guides including cloud platforms, CI/CD integration, and production setup, see [Deployment Documentation](docs/deployment.md).

### Available CLI Commands

After installation, these commands are available:

- `dev-sentinel` - Main CLI with system management
- `force-mcp-stdio` - Force MCP server (stdio transport)
- `dev-sentinel-stdio` - Dev Sentinel MCP server (stdio transport)  
- `force-mcp-http` - Force MCP server (HTTP transport)
- `dev-sentinel-http` - Dev Sentinel MCP server (HTTP transport)

## MCP Server Integration

Dev Sentinel provides comprehensive MCP (Model Context Protocol) server integration with VS Code, Claude, and other AI development tools.

### Available MCP Servers

| Server | Command | Transport | Description |
|--------|---------|-----------|-------------|
| **Force MCP** | `force-mcp-stdio` | stdio | Primary Force framework server |
| **Dev Sentinel** | `dev-sentinel-stdio` | stdio | Full Dev Sentinel with AI agents |
| **Force HTTP** | `force-mcp-http` | http | Force server with HTTP transport |
| **Dev Sentinel HTTP** | `dev-sentinel-http` | http | Dev Sentinel with HTTP API |

### Quick Setup for VS Code

1. **Install the package**:
   ```bash
   pip install -e .
   ```

2. **Create MCP Configuration**

   Create `.vscode/mcp.json` in your workspace:

   ```json
   {
     "mcpServers": {
       "force_mcp_stdio": {
         "command": "force-mcp-stdio",
         "args": [],
         "cwd": "${workspaceFolder}",
         "env": {
           "PATH": "${workspaceFolder}/.venv/bin:${env:PATH}",
           "PYTHONUNBUFFERED": "1"
         },
         "transport": "stdio",
         "timeout": 30000
       }
     }
   }
   ```

3. **Test the server**:
   ```bash
   force-mcp-stdio --validation-only
   ```

### Configuration Examples

Complete configuration examples are available in [`examples/mcp-configurations/`](examples/mcp-configurations/):

- [`vscode-mcp.json`](examples/mcp-configurations/vscode-mcp.json) - VS Code integration
- [`claude-mcp.json`](examples/mcp-configurations/claude-mcp.json) - Claude Desktop  
- [`generic-mcp.json`](examples/mcp-configurations/generic-mcp.json) - Universal configuration

### Server Features

- **🛠️ Direct Tool Execution**: Access 40+ Force tools through MCP
- **📋 Pattern Application**: Execute development patterns with executable and descriptive steps
- **✅ Schema Validation**: Flexible validation with extended schema support
- **🔄 Real-time Monitoring**: Live execution feedback and error handling
- **🎯 Context-Aware**: Project-specific tool discovery and configuration
   ```

3. **Test Integration**

   In VS Code Copilot Chat:

   ```text
   @force_mcp_stdio list all available Force tools
   @force_mcp_stdio execute force_tool_generator to create a new tool
   @force_mcp_stdio apply pattern atomic_commit_pattern
   ```

### Configuration for Other MCP Clients

For **Claude Desktop** or other MCP clients, adapt the configuration:

```json
{
  "mcpServers": {
    "force_mcp_stdio": {
      "command": "/path/to/your/python",
      "args": ["/path/to/dev_sentinel/integration/fast_agent/force_mcp_server.py"],
      "cwd": "/path/to/dev_sentinel",
      "env": {
        "PYTHONPATH": "/path/to/dev_sentinel"
      }
    }
  }
}
```

### Extended Schema System

The Force MCP server leverages the new **Extended Schema System** for flexible validation:

- **✅ Automatic Schema Detection**: Prefers `force-extended-schema.json` over strict schema
- **🔄 Flexible Categories**: Supports custom tool categories (security, release, monitoring, etc.)
- **⚡ Enhanced Error Handling**: Open-ended error handling strategies
- **📊 Improved Loading**: 38+ tools load successfully vs. 31 with strict schema

### Available MCP Tools

The server exposes these key Force capabilities:

| Tool | Description |
|------|-------------|
| `force_list_tools` | List all available Force tools with metadata |
| `force_execute_tool` | Execute any Force tool with validation |
| `force_apply_pattern` | Apply development patterns with step execution |
| `force_list_patterns` | Browse available patterns by category |
| `force_check_constraints` | Validate code against Force constraints |
| `force_get_insights` | Retrieve learning insights and recommendations |
| `force_component_validator` | Validate Force components for schema compliance |

### Troubleshooting

1. **Server Won't Start**

   ```bash
   # Check Python path and dependencies
   python integration/fast_agent/force_mcp_server.py --version
   ```

2. **Schema Validation Errors**

   ```bash
   # Verify extended schema is present
   ls -la .force/schemas/force-extended-schema.json
   ```

3. **Tool Loading Issues**

   ```bash
   # Test tool discovery
   python -c "from force import ForceEngine; f = ForceEngine(); print(f.list_tools())"
   ```

For detailed documentation, see [MCP Integration Guide](docs/integration/mcp-integration.md).

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [📚 Documentation Home](docs/index.md) - Start here for all documentation
- [🏛️ Architecture Documentation](docs/architecture/overview.md) - System design and architecture
- [🧩 Component Documentation](docs/components/index.md) - Details of each component
- [📝 API Reference](docs/api/index.md) - API documentation
- [👤 User Guide](docs/user/getting-started.md) - Getting started and user documentation
- [💻 Developer Guide](docs/developer/index.md) - Contributing and development documentation
- [📋 Reference](docs/reference/index.md) - Tools, patterns, and constraints reference

### Basic Usage

1. **Start the Server**:
   ```bash
   python run_server.py
   ```

2. **Configure Project**:
   ```bash
   # Initialize FORCE configuration
   mkdir .force
   cp config/fastagent.config.yaml .force/
   ```

3. **Connect VS Code**:
   - Install the Dev Sentinel VS Code extension
   - Use Command Palette: `Dev Sentinel: Connect to Server`

## Architecture


<details>
<summary>Core System Architecture</summary>

```plantuml
@startuml Dev Sentinel Core
skinparam backgroundColor transparent

package "Dev Sentinel" {
    [Message Bus] as MB
    [Task Manager] as TM
    [FORCE Engine] as FE
    
    package "Agents" {
        [Version Control Master] as VCMA
        [Version Control Listener] as VCLA
        [Code Documentation] as CDIA
        [Readme Documentation] as RDIA
        [System Analysis] as SAA
    }
    
    MB --> TM
    MB --> FE
    
    VCMA --> MB
    VCLA --> MB
    CDIA --> MB
    RDIA --> MB
    SAA --> MB
}
@enduml

```

```mermaid
flowchart TB
    subgraph "Dev Sentinel"
        MB["Message Bus"]
        TM["Task Manager"]
        FE["FORCE Engine"]
        subgraph "Agents"
            VCMA["Version Control Master"]
            VCLA["Version Control Listener"]
            CDIA["Code Documentation"]
            RDIA["Readme Documentation"]
            SAA["System Analysis"]
        end
    end
    MB --> TM
    MB --> FE
    VCMA --> MB
    VCLA --> MB
    CDIA --> MB
    RDIA --> MB
    SAA --> MB

@enduml
```

```mermaid
flowchart TB
    subgraph "FORCE Framework"
        TM["Tool Manager"]
        PM["Pattern Manager"]
        CM["Constraint Manager"]
        LM["Learning Manager"]
        GM["Governance Manager"]
        TR["Tool Registry"]
        PR["Pattern Registry"]
        CR["Constraint Registry"]
    end
    TM --> TR
    PM --> PR
    CM --> CR
    TM <-- LM
    PM <-- LM
    CM <-- LM
    TM <-- GM
    PM <-- GM
    CM <-- GM
```
</details>
    CM <-- GM
@enduml
    SAA --> MB
@enduml

## Core Features

### 1. Enhanced Development Tools (v0.3.0)

- **Git Workflow Management**: Smart commit grouping, atomic commits, and semantic versioning
- **Documentation Analysis**: Quality checks, completeness validation, and sync capabilities
- **Code Analysis**: Static analysis, quality scoring, and release readiness assessment
- **Release Management**: Automated changelog generation and dependency analysis

### 2. Advanced Pattern Application

- **Development Patterns**: Atomic commit grouping, branch end tasks, continuous changelog
- **Documentation Patterns**: Handoff documentation, modular structure, cross-referencing
- **Git Patterns**: Grouped commit workflows, semantic versioning, release management

### 3. Comprehensive Quality Constraints

- **Code Quality**: Automated style checks, complexity analysis, and best practices
- **Documentation Quality**: Structure validation, completeness scoring, and consistency
- **Git Quality**: Commit message standards, history validation, and workflow compliance
- **Security**: Infrastructure security checks, secrets scanning, and compliance validation

### 4. Intelligent Learning System

- **Pattern Recognition**: Learn from successful development workflows
- **Task Optimization**: Improve efficiency based on execution metrics
- **Suggestion Engine**: Context-aware recommendations and automation
- **Performance Analytics**: Track tool usage and success patterns

## Documentation

- [Core Architecture](docs/01-architecture/): System design and components
- [Development Guide](docs/02-development/): Setup and contribution
- [Agent Reference](docs/03-agents/): Agent specifications
- [FORCE Framework](docs/04-force/): Tools and patterns
- [MCP Integration](docs/05-mcp/): VS Code extension

## Contributing

See our [Contributing Guide](CONTRIBUTING.md) for details on:
- Development setup
- Code style
- Pull request process
- Documentation standards

## License

This project is licensed under the MIT License - see [LICENSE-MIT.md](LICENSE-MIT.md) for details.

## Acknowledgments

- FORCE framework inspired by advanced software development practices
- Agent architecture based on proven autonomous systems
- Diagrams created with [PlantUML](https://plantuml.com/)


