# Getting Started with Dev Sentinel

This guide will help you get started with Dev Sentinel, a force-enabled development assistant that combines intelligent agents with the FORCE development framework.

## What is Dev Sentinel?

Dev Sentinel is an autonomous development assistant designed to help you:

- Automate routine development tasks
- Enforce code quality and documentation standards
- Manage version control operations
- Provide development insights through intelligent analysis

## Quick Installation

### Prerequisites

- Python 3.10+
- Git
- VS Code (for full integration)

### Installation Steps

1. Clone the repository:

```bash
git clone https://github.com/pegues/dev-sentinel.git
cd dev-sentinel
```

2. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the system:

```bash
cp config/fastagent.config.yaml.example config/fastagent.config.yaml
# Edit the config file as needed
```

4. Run the server:

```bash
python run_server.py
```

For more detailed installation instructions, see the [Installation Guide](./installation.md).

## Basic Usage

### Running Dev Sentinel

Once Dev Sentinel is running, you can interact with it through:

1. **Terminal Commands**: Use the YUNG command syntax for direct interaction
2. **VS Code Extension**: Use the Dev Sentinel VS Code extension for integrated experience
3. **MCP Integration**: Interact with Dev Sentinel through Copilot Chat

### YUNG Commands

Dev Sentinel uses the YUNG (YES Ultimate Net Good) universal instruction set. Here are some basic commands:

```bash
# Check git status
$VCS status

# Analyze code quality
$SCA analyze-code ./src

# Check documentation coverage
$DOC validate ./docs

# Run a comprehensive analysis
$FULL-ANALYSIS
```

For a complete list of commands, see the [YUNG Command Reference](../reference/yung-commands.md).

## Next Steps

- [Architecture Overview](../architecture/overview.md): Understand the Dev Sentinel architecture
- [Agent Documentation](../components/agents/index.md): Explore the different autonomous agents
- [FORCE Framework](../components/force/index.md): Learn about the FORCE framework
- [Usage Examples](./usage-examples.md): See examples of Dev Sentinel in action
- [API Reference](../api/index.md): Integration API documentation
