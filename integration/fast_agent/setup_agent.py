#!/usr/bin/env python
"""
Setup script for Dev Sentinel fast-agent integration.

This script installs and configures dependencies required for Dev Sentinel
to work with the Model Context Protocol (MCP) and fast-agent.
"""

import os
import sys
import subprocess
import argparse
import logging
import json
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("setup_agent")

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Dependencies required for fast-agent integration
REQUIRED_PACKAGES = [
    "fast-agent-mcp>=0.2.20",    # The fast-agent framework
    "mcp-agent>=0.2.0",          # Base MCP client library
    "fastapi>=0.104.0",          # For HTTP API server
    "uvicorn>=0.24.0",           # ASGI server
    "pydantic>=2.5.0",           # Data validation
    "httpx>=0.25.0"              # HTTP client
]

# Optional packages for advanced features
OPTIONAL_PACKAGES = [
    "matplotlib>=3.8.0",         # For diagram generation
    "plotly>=5.17.0",            # For interactive visualizations
    "pygraphviz>=1.11",          # For graph visualization
    "pandas>=2.1.1",             # For data processing
]

def check_python_version() -> bool:
    """
    Check if the current Python version is compatible.
    
    Returns:
        True if compatible, False otherwise
    """
    major, minor, _ = sys.version_info[:3]
    min_major, min_minor = 3, 10  # Minimum Python 3.10
    
    if major > min_major or (major == min_major and minor >= min_minor):
        logger.info(f"Python version {major}.{minor} is compatible")
        return True
    else:
        logger.error(f"Python version {major}.{minor} is not compatible")
        logger.error(f"Minimum required version is {min_major}.{min_minor}")
        return False

def check_package_installed(package: str) -> bool:
    """
    Check if a Python package is installed.
    
    Args:
        package: Name of the package to check
        
    Returns:
        True if installed, False otherwise
    """
    try:
        # Extract package name and version
        name = package.split(">=")[0].split("==")[0].strip()
        __import__(name.replace("-", "_").replace(".", "_"))
        return True
    except ImportError:
        return False

def install_packages(packages: List[str], upgrade: bool = False) -> Tuple[bool, List[str]]:
    """
    Install required Python packages.
    
    Args:
        packages: List of packages to install
        upgrade: Whether to upgrade existing packages
        
    Returns:
        Tuple of (success, failed_packages)
    """
    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.error("pip is not installed. Please install pip first.")
        return False, packages
    
    failed_packages = []
    
    # Install each package
    for package in packages:
        logger.info(f"Installing {package}...")
        
        try:
            cmd = [sys.executable, "-m", "pip", "install"]
            
            if upgrade:
                cmd.append("--upgrade")
                
            cmd.append(package)
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                logger.error(f"Failed to install {package}: {process.stderr}")
                failed_packages.append(package)
            else:
                logger.info(f"Successfully installed {package}")
                
        except Exception as e:
            logger.exception(f"Error installing {package}: {e}")
            failed_packages.append(package)
    
    success = len(failed_packages) == 0
    return success, failed_packages

def generate_config_files(config_dir: str, include_optional: bool = False) -> bool:
    """
    Generate fast-agent configuration files.
    
    Args:
        config_dir: Directory to store configuration files
        include_optional: Whether to include optional configurations
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Define the base configuration for fastagent.config.yaml
        config = {
            "model": {
                "default": "o3-mini.high",
                "allowed": [
                    "o3-mini.high",
                    "o3-mini.low",
                    "o3-preview.high",
                    "o1.high",
                    "haiku",
                    "sonnet",
                    "opus"
                ]
            },
            "mcp": {
                "servers": {
                    "dev_sentinel": {
                        "command": "python",
                        "args": ["-m", "integration.fast_agent.mcp_servers", "dev_sentinel"],
                        "env": {
                            "PYTHONPATH": "${PYTHONPATH}:${workspaceRoot}"
                        },
                        "port": 8090
                    },
                    "filesystem": {
                        "command": "python",
                        "args": ["-m", "integration.fast_agent.mcp_servers", "filesystem"],
                        "env": {
                            "PYTHONPATH": "${PYTHONPATH}:${workspaceRoot}"
                        },
                        "port": 8091
                    },
                    "vcs": {
                        "command": "python",
                        "args": ["-m", "integration.fast_agent.mcp_servers", "vcs"],
                        "env": {
                            "PYTHONPATH": "${PYTHONPATH}:${workspaceRoot}"
                        },
                        "port": 8092
                    },
                    "documentation": {
                        "command": "python",
                        "args": ["-m", "integration.fast_agent.mcp_servers", "documentation"],
                        "env": {
                            "PYTHONPATH": "${PYTHONPATH}:${workspaceRoot}"
                        },
                        "port": 8093
                    },
                    "code_analysis": {
                        "command": "python",
                        "args": ["-m", "integration.fast_agent.mcp_servers", "code_analysis"],
                        "env": {
                            "PYTHONPATH": "${PYTHONPATH}:${workspaceRoot}"
                        },
                        "port": 8094
                    }
                }
            }
        }
        
        # Add agents and workflows
        config.update({
            "agents": {
                "yung_processor": {
                    "servers": ["dev_sentinel", "filesystem", "vcs", "documentation", "code_analysis"],
                    "instruction": "You are the YUNG command processor agent for Dev Sentinel.",
                    "model": "${model.default}"
                },
                "doc_inspector": {
                    "servers": ["documentation", "filesystem"],
                    "instruction": "You are a documentation expert that inspects code documentation for quality and completeness.",
                    "model": "${model.default}"
                },
                "code_analyzer": {
                    "servers": ["code_analysis", "filesystem"],
                    "instruction": "You are a code quality expert that analyzes code for issues, bugs, and best practices.",
                    "model": "${model.default}"
                }
            },
            "workflows": {
                "doc_validation": {
                    "chain": ["documentation", "code_analysis"],
                    "description": "Inspect documentation and code quality in the repository"
                },
                "code_improvement": {
                    "chain": ["code_analysis", "documentation", "vcs"],
                    "description": "Analyze code quality, improve documentation, and commit changes"
                }
            }
        })
        
        # Add optional configurations
        if include_optional:
            config["mcp"]["servers"]["data_analysis"] = {
                "command": "python",
                "args": ["-m", "integration.fast_agent.data_analysis_server"],
                "env": {
                    "PYTHONPATH": "${PYTHONPATH}:${workspaceRoot}"
                },
                "port": 8095
            }
        
        # Write fastagent.config.yaml
        config_path = os.path.join(config_dir, "fastagent.config.yaml")
        import yaml
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Created configuration file: {config_path}")
        
        # Write fastagent.secrets.yaml
        secrets = {
            "openai": {
                "api_key": "${OPENAI_API_KEY}"
            },
            "anthropic": {
                "api_key": "${ANTHROPIC_API_KEY}"
            }
        }
        
        secrets_path = os.path.join(config_dir, "fastagent.secrets.yaml")
        with open(secrets_path, "w") as f:
            yaml.dump(secrets, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Created secrets file: {secrets_path}")
        
        return True
    except Exception as e:
        logger.exception(f"Error generating config files: {e}")
        return False

def setup_environment_variables() -> bool:
    """
    Setup environment variables for API keys.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check and prompt for API keys
        openai_key = os.environ.get("OPENAI_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Check and prompt for OpenAI API key
        if not openai_key:
            print("OpenAI API key not found in environment variables.")
            print("Please set the OPENAI_API_KEY environment variable.")
        else:
            logger.info("OpenAI API key found in environment variables")
        
        # Check and prompt for Anthropic API key
        if not anthropic_key:
            print("Anthropic API key not found in environment variables.")
            print("Please set the ANTHROPIC_API_KEY environment variable.")
        else:
            logger.info("Anthropic API key found in environment variables")
        
        return True
    except Exception as e:
        logger.exception(f"Error setting up environment variables: {e}")
        return False

def setup_fast_agent(install_optional: bool = False, upgrade: bool = False) -> bool:
    """
    Set up fast-agent for Dev Sentinel.
    
    Args:
        install_optional: Whether to install optional packages
        upgrade: Whether to upgrade existing packages
        
    Returns:
        True if setup was successful, False otherwise
    """
    logger.info("Setting up fast-agent for Dev Sentinel...")
    
    # Check Python version
    if not check_python_version():
        logger.error("Python version check failed")
        return False
    
    # Install required packages
    packages = REQUIRED_PACKAGES
    if install_optional:
        packages.extend(OPTIONAL_PACKAGES)
    
    logger.info(f"Installing {'required' if not install_optional else 'required and optional'} packages...")
    success, failed = install_packages(packages, upgrade)
    
    if not success:
        logger.error("Failed to install some packages:")
        for pkg in failed:
            logger.error(f"  - {pkg}")
        return False
    
    # Generate configuration files
    config_dir = os.path.join(project_root, "config")
    logger.info(f"Generating configuration files in {config_dir}...")
    if not generate_config_files(config_dir, install_optional):
        logger.error("Failed to generate configuration files")
        return False
    
    # Setup environment variables
    logger.info("Setting up environment variables...")
    if not setup_environment_variables():
        logger.error("Failed to setup environment variables")
        return False
    
    logger.info("fast-agent setup completed successfully!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup fast-agent for Dev Sentinel")
    parser.add_argument("--optional", action="store_true", help="Install optional packages")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade existing packages")
    args = parser.parse_args()
    
    success = setup_fast_agent(args.optional, args.upgrade)
    sys.exit(0 if success else 1)