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

# Install dependencies
pip install -r requirements.txt
```

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
</details>

<details>
<summary>FORCE Framework Architecture</summary>

```plantuml
@startuml FORCE Framework
skinparam backgroundColor transparent

package "FORCE Framework" {
    [Tool Manager] as TM
    [Pattern Manager] as PM
    [Constraint Manager] as CM
    [Learning Manager] as LM
    [Governance Manager] as GM
    
    database "Tool Registry" as TR
    database "Pattern Registry" as PR
    database "Constraint Registry" as CR
    
    TM --> TR
    PM --> PR
    CM --> CR
    
    TM <-- LM
    PM <-- LM
    CM <-- LM
    
    TM <-- GM
    PM <-- GM
    CM <-- GM
}
@enduml
```
</details>

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
