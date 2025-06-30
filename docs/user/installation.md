# Installation Guide

This guide provides detailed instructions for installing and setting up Dev Sentinel.

## Prerequisites

Before installing Dev Sentinel, ensure you have the following prerequisites:

- **Python 3.10 or later**: Dev Sentinel requires Python 3.10+ for its async features and type annotations
- **Git**: Required for version control operations
- **VS Code** (optional): Recommended for MCP integration and best development experience

## Installation Methods

### Method 1: Standard Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/peguesj/yj-dev_sentinel.git
   cd yj-dev_sentinel
   ```

2. **Create a virtual environment**:

   For Linux/macOS:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   For Windows:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the environment**:

   Copy the example configuration file and modify as needed:

   ```bash
   cp config/fastagent.config.example.yaml config/fastagent.config.yaml
   cp config/fastagent.secrets.example.yaml config/fastagent.secrets.yaml
   ```

   Edit the configuration files to match your environment.

### Method 2: Development Installation

For contributors and developers:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/peguesj/yj-dev_sentinel.git
   cd yj-dev_sentinel
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install development dependencies**:

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**:

   ```bash
   pre-commit install
   ```

5. **Configure the environment**:

   ```bash
   cp config/fastagent.config.example.yaml config/fastagent.config.yaml
   cp config/fastagent.secrets.example.yaml config/fastagent.secrets.yaml
   ```

   Edit the configuration files to match your environment.

### Method 3: Docker Installation

For containerized deployment:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/peguesj/yj-dev_sentinel.git
   cd yj-dev_sentinel
   ```

2. **Build the Docker image**:

   ```bash
   docker build -t dev-sentinel .
   ```

3. **Run the container**:

   ```bash
   docker run -v $(pwd)/config:/app/config -p 8000:8000 dev-sentinel
   ```

## Configuration

### Basic Configuration

The main configuration files are:

- `config/fastagent.config.yaml`: Main configuration for agents and FORCE components
- `config/fastagent.secrets.yaml`: Secret configuration values (API keys, tokens, etc.)

### Agent Configuration

Enable or disable specific agents:

```yaml
agents:
  vcma:
    enabled: true
    # VCMA-specific configuration...
  vcla:
    enabled: true
    # VCLA-specific configuration...
  # Other agents...
```

### FORCE Configuration

Configure FORCE framework components:

```yaml
force:
  enabled: true
  tools:
    enabled: true
    # Tool-specific configuration...
  patterns:
    enabled: true
    # Pattern-specific configuration...
  # Other FORCE components...
```

## Verification

After installation, verify that Dev Sentinel is working correctly:

1. **Run the server**:

   ```bash
   python run_server.py
   ```

2. **Check the server status**:

   Open a web browser and navigate to `http://localhost:8000/status`

3. **Run a basic test**:

   ```bash
   python scripts/force_demo.py
   ```

## Troubleshooting

### Common Issues

1. **Missing dependencies**:

   If you encounter errors about missing dependencies, try reinstalling:

   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **Configuration errors**:

   Ensure your configuration files are properly formatted and contain valid values.

3. **Permission issues**:

   Make sure you have appropriate permissions for the directories you're working with.

### Getting Help

If you encounter issues not covered here:

- Check the [common issues](/docs/user/common-issues.md) guide
- Ask for help in our community chat
- Open an issue on GitHub

## Next Steps

- Read the [Getting Started](/docs/user/getting-started.md) guide to learn how to use Dev Sentinel
- Explore the [Architecture Documentation](/docs/architecture/overview.md) to understand the system design
- Check the [API Reference](/docs/api/index.md) to learn how to integrate with Dev Sentinel

## Uninstallation

To uninstall Dev Sentinel:

1. Deactivate the virtual environment:

   ```bash
   deactivate
   ```

2. Remove the project directory:

   ```bash
   cd ..
   rm -rf yj-dev_sentinel
   ```
