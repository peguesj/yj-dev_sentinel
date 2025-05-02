"""
Setup module for fast-agent integration with Dev Sentinel.
"""
import os
import asyncio
import subprocess
from typing import Dict, Any, List, Optional

from integration.fast_agent.config_templates import (
    generate_server_scripts, 
    generate_fastagent_config, 
    generate_fastagent_secrets,
    generate_agent_examples
)

# Package requirements for fast-agent integration
REQUIREMENTS = [
    "mcp>=1.6.0",
    "mcp-server-sdk>=0.2.0",
    "pyyaml>=6.0",
    "uv>=0.1.0",
]

class FastAgentSetup:
    """Setup helper for fast-agent integration with Dev Sentinel."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize setup helper.
        
        Args:
            output_dir: Directory to write generated files to (defaults to project root)
        """
        self.output_dir = output_dir or os.getcwd()
        self.config_dir = os.path.join(self.output_dir, "fast_agent_integration")
        self.server_scripts_dir = os.path.join(self.config_dir, "servers")
        self.examples_dir = os.path.join(self.config_dir, "examples")
        
    async def setup(self, install_dependencies: bool = True) -> Dict[str, Any]:
        """
        Set up the fast-agent integration.
        
        Args:
            install_dependencies: Whether to install required dependencies
            
        Returns:
            Dict containing setup results
        """
        results = {}
        
        # Create directories
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.server_scripts_dir, exist_ok=True)
        os.makedirs(self.examples_dir, exist_ok=True)
        
        # Generate server scripts
        results['server_scripts'] = generate_server_scripts(self.server_scripts_dir)
        
        # Generate config files
        results['config_file'] = generate_fastagent_config(self.config_dir)
        results['secrets_file'] = generate_fastagent_secrets(self.config_dir)
        
        # Generate examples
        results['examples'] = generate_agent_examples(self.examples_dir)
        
        # Install dependencies
        if install_dependencies:
            results['dependencies'] = await self.install_dependencies()
            
        return results
    
    async def install_dependencies(self) -> Dict[str, Any]:
        """
        Install required dependencies for fast-agent integration.
        
        Returns:
            Dict containing installation results
        """
        results = {}
        
        # Check if uv is installed
        try:
            subprocess.run(['uv', '--version'], check=True, capture_output=True)
            uv_installed = True
        except (subprocess.SubprocessError, FileNotFoundError):
            uv_installed = False
        
        # Install uv if not present
        if not uv_installed:
            try:
                print("Installing uv package manager...")
                subprocess.run(['curl', '-L', 'https://astral.sh/uv/install.sh', '|', 'bash'], check=True)
                results['uv_install'] = 'success'
            except subprocess.SubprocessError as e:
                results['uv_install'] = f'error: {str(e)}'
                return results
        else:
            results['uv_install'] = 'already_installed'
        
        # Install required packages
        try:
            print("Installing required packages...")
            subprocess.run(['uv', 'pip', 'install'] + REQUIREMENTS, check=True)
            results['package_install'] = 'success'
        except subprocess.SubprocessError as e:
            results['package_install'] = f'error: {str(e)}'
        
        return results
    
    def create_integration_readme(self) -> str:
        """
        Create a README file for the fast-agent integration.
        
        Returns:
            Path to the generated README file
        """
        readme_content = """# Dev Sentinel Integration with fast-agent

This directory contains the integration between Dev Sentinel autonomous development agents and the fast-agent MCP framework.

## Directory Structure

- `servers/` - MCP server implementations for Dev Sentinel capabilities
- `examples/` - Example scripts for using Dev Sentinel agents with fast-agent
- `fastagent.config.yaml` - Configuration file for fast-agent
- `fastagent.secrets.yaml` - Secrets file template for fast-agent (requires your API keys)

## Getting Started

1. Make sure to have the required dependencies installed:
   ```
   uv pip install fast-agent-mcp mcp-server-sdk pyyaml
   ```

2. Set up your API keys in the `fastagent.secrets.yaml` file

3. Run one of the example scripts:
   ```
   uv run examples/dev_sentinel_agents.py
   ```

## Available MCP Servers

- `FileSystemMCPServer` - File system operations
- `VersionControlMCPServer` - Version control operations
- `DocumentationInspectorMCPServer` - Documentation inspection operations
- `CodeAnalysisMCPServer` - Code analysis operations

## YUNG Command Processor

The YUNG command processor allows you to use the Dev Sentinel universal instruction set with fast-agent:

```
uv run examples/yung_command_processor.py
```

Then enter commands like:
- `$VIC ALL` - Validate integrity of all code
- `$CODE TIER=BACKEND IMPL,TEST Stage F-1` - Implement and test backend code
- `$man` - Display the YUNG command manual

## Creating Custom Dev Sentinel + fast-agent Workflows

See the examples directory for demonstrations of how to create custom workflows combining Dev Sentinel agents using fast-agent's workflow capabilities.
"""
        readme_path = os.path.join(self.config_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write(readme_content)
        return readme_path


async def setup_fast_agent_integration(output_dir: str = None, install_dependencies: bool = True) -> Dict[str, Any]:
    """
    Set up fast-agent integration with Dev Sentinel.
    
    Args:
        output_dir: Directory to write generated files to (defaults to project root)
        install_dependencies: Whether to install required dependencies
        
    Returns:
        Dict containing setup results
    """
    setup = FastAgentSetup(output_dir)
    results = await setup.setup(install_dependencies)
    results['readme'] = setup.create_integration_readme()
    return results


if __name__ == "__main__":
    # When run as a script, set up the integration
    asyncio.run(setup_fast_agent_integration())