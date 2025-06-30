# Development Environment Setup

This guide will help you set up your development environment for working with Dev Sentinel.

## Prerequisites

Before getting started, ensure you have the following installed:

- Python 3.10 or later
- Git
- VS Code (recommended for MCP integration)

## Setting Up the Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/peguesj/yj-dev_sentinel.git
cd yj-dev_sentinel
```

### 2. Create a Virtual Environment

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

### 3. Install Dependencies

Install the development dependencies:

```bash
pip install -r requirements.txt
# Optional: Install development extras
pip install -e ".[dev]"
```

### 4. Install Pre-commit Hooks

Pre-commit hooks help maintain code quality:

```bash
pip install pre-commit
pre-commit install
```

## IDE Configuration

### VS Code Setup

1. Open the project folder in VS Code
2. Install recommended extensions:
   - Python
   - Python Intellisense (Pylance)
   - Python Docstring Generator
   - GitLens
   - Markdown All in One

3. Configure settings.json for the project:

   ```json
   {
     "python.linting.enabled": true,
     "python.linting.flake8Enabled": true,
     "python.linting.mypyEnabled": true,
     "python.formatting.provider": "black",
     "editor.formatOnSave": true,
     "python.analysis.typeCheckingMode": "basic"
   }
   ```

## Running Dev Sentinel

### Basic Execution

Run the main server:

```bash
python run_server.py
```

### Development Mode

Run with debug output:

```bash
PYTHONPATH=. LOG_LEVEL=DEBUG python run_server.py
```

## Testing

### Running Tests

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=force --cov=agents --cov=core
```

### Continuous Integration

The CI pipeline runs the following checks:

- Linting with flake8
- Type checking with mypy
- Tests with pytest
- Documentation building

## Common Development Tasks

### Adding a New Agent

1. Create a new directory under `agents/`
2. Implement the agent class
3. Add configuration to `config/fastagent.config.yaml`
4. Add tests under `tests/`

### Adding a New FORCE Tool

1. Create a new directory under `force/tools/`
2. Implement the tool class
3. Register with the tool executor
4. Add tests under `tests/`

## Troubleshooting

### Common Issues

1. **Import errors** - Ensure your PYTHONPATH includes the project root
2. **Configuration errors** - Check that you have proper config files in the config directory
3. **Missing dependencies** - Make sure all requirements are installed

### Getting Help

If you run into issues not covered here:

1. Check the existing issues on GitHub
2. Ask in the developer chat
3. Open a new issue with details about your problem
