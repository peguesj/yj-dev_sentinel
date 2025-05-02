"""
Configuration templates for fast-agent integration.
"""
import os
import yaml
from typing import Dict, Any, List, Optional
import re
import asyncio
from integration.fast_agent.specialized_adapters import (
    VCMAFastAdapter, VCLAFastAdapter, CDIAFastAdapter,
    RDIAFastAdapter, SAAFastAdapter
)

import mcp_agent as fast

async def main():
    """
    Main function to run the fast-agent integration.
    
    This function initializes the MCP server and creates a fast agent instance.
    """   
    # Create a fast agent instance
    mcp = fast.create_fast_agent()


# Base configuration template for fastagent.config.yaml
FASTAGENT_CONFIG_TEMPLATE = {
    "mcp": {
        "servers": {
            "filesystem": {
                "command": "uv",
                "args": ["run", "dev_sentinel_filesystem_server.py"],
                "env": {}
            },
            "vcs": {
                "command": "uv",
                "args": ["run", "dev_sentinel_vcs_server.py"],
                "env": {}
            },
            "documentation": {
                "command": "uv",
                "args": ["run", "dev_sentinel_documentation_server.py"],
                "env": {}
            },
            "code_analysis": {
                "command": "uv",
                "args": ["run", "dev_sentinel_code_analysis_server.py"],
                "env": {}
            }
        }
    }
}


# Base configuration template for fastagent.secrets.yaml
FASTAGENT_SECRETS_TEMPLATE = {
    "anthropic": {
        "api_key": "${ANTHROPIC_API_KEY}"
    },
    "openai": {
        "api_key": "${OPENAI_API_KEY}"
    }
}


def generate_server_scripts(output_dir: str) -> Dict[str, str]:
    """
    Generate MCP server script files.
    
    Args:
        output_dir: Directory to write the scripts to
        
    Returns:
        Dict mapping script names to their file paths
    """
    scripts = {
        "dev_sentinel_filesystem_server.py": """
import asyncio
from mcp_server_sdk import MCPServer
from integration.fast_agent.mcp_servers import FileSystemMCPServer

# Create MCP server instance
server = MCPServer()
fs_server = FileSystemMCPServer()

# Register methods
server.register_method("read_file", fs_server.read_file)
server.register_method("write_file", fs_server.write_file)
server.register_method("list_directory", fs_server.list_directory)

# Start server
if __name__ == "__main__":
    asyncio.run(server.start())
""",
        "dev_sentinel_vcs_server.py": """
import asyncio
from mcp_server_sdk import MCPServer
from integration.fast_agent.mcp_servers import VersionControlMCPServer

# Create MCP server instance
server = MCPServer()
vcs_server = VersionControlMCPServer()

# Register methods
server.register_method("get_changes", vcs_server.get_changes)
server.register_method("commit", vcs_server.commit)
server.register_method("create_branch", vcs_server.create_branch)

# Start server
if __name__ == "__main__":
    asyncio.run(server.start())
""",
        "dev_sentinel_documentation_server.py": """
import asyncio
from mcp_server_sdk import MCPServer
from integration.fast_agent.mcp_servers import DocumentationInspectorMCPServer

# Create MCP server instance
server = MCPServer()
doc_server = DocumentationInspectorMCPServer()

# Register methods
server.register_method("inspect_documentation", doc_server.inspect_documentation)
server.register_method("generate_documentation", doc_server.generate_documentation)

# Start server
if __name__ == "__main__":
    asyncio.run(server.start())
""",
        "dev_sentinel_code_analysis_server.py": """
import asyncio
from mcp_server_sdk import MCPServer
from integration.fast_agent.mcp_servers import CodeAnalysisMCPServer

# Create MCP server instance
server = MCPServer()
code_analysis_server = CodeAnalysisMCPServer()

# Register methods
server.register_method("analyze_code", code_analysis_server.analyze_code)

# Start server
if __name__ == "__main__":
    asyncio.run(server.start())
"""
    }
    
    # Write scripts to files
    script_paths = {}
    for script_name, content in scripts.items():
        script_path = os.path.join(output_dir, script_name)
        with open(script_path, "w") as f:
            f.write(content.strip())
        script_paths[script_name] = script_path
    
    return script_paths


def generate_config_file(output_path: str, config: Dict[str, Any]) -> str:
    """
    Generate a YAML configuration file.
    
    Args:
        output_path: Path to write the YAML file to
        config: Configuration dictionary
        
    Returns:
        Path to the generated file
    """
    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return output_path


def generate_fastagent_config(output_dir: str, extra_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate fastagent.config.yaml file.
    
    Args:
        output_dir: Directory to write the config file to
        extra_config: Optional additional configuration to merge
        
    Returns:
        Path to the generated file
    """
    config = FASTAGENT_CONFIG_TEMPLATE.copy()
    
    # Merge extra configuration if provided
    if extra_config:
        # Deep merge the configurations (simplified version)
        for key, value in extra_config.items():
            if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                config[key].update(value)
            else:
                config[key] = value
    
    output_path = os.path.join(output_dir, "fastagent.config.yaml")
    return generate_config_file(output_path, config)


def generate_fastagent_secrets(output_dir: str, extra_secrets: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate fastagent.secrets.yaml file.
    
    Args:
        output_dir: Directory to write the secrets file to
        extra_secrets: Optional additional secrets to merge
        
    Returns:
        Path to the generated file
    """
    secrets = FASTAGENT_SECRETS_TEMPLATE.copy()
    
    # Merge extra secrets if provided
    if extra_secrets:
        # Deep merge the secrets (simplified version)
        for key, value in extra_secrets.items():
            if key in secrets and isinstance(secrets[key], dict) and isinstance(value, dict):
                secrets[key].update(value)
            else:
                secrets[key] = value
    
    output_path = os.path.join(output_dir, "fastagent.secrets.yaml")
    return generate_config_file(output_path, secrets)


def generate_agent_examples(output_dir: str) -> Dict[str, str]:
    """
    Generate example Python scripts for using Dev Sentinel agents with fast-agent.
    
    Args:
        output_dir: Directory to write the examples to
        
    Returns:
        Dict mapping example names to their file paths
    """
    examples = {
        "dev_sentinel_agents.py": """
import asyncio
import fast_agent_mcp as fast
from integration.fast_agent.specialized_adapters import (
    VCMAFastAdapter, VCLAFastAdapter, CDIAFastAdapter, 
    RDIAFastAdapter, SAAFastAdapter
)
from agents.vcma.vcma_agent import VersionControlMasterAgent
from agents.vcla.vcla_agent import VersionControlListenerAgent
from agents.cdia.cdia_agent import CodeDocumentationInspectorAgent
from agents.rdia.rdia_agent import ReadmeDocumentationInspectorAgent
from agents.saa.saa_agent import StaticAnalysisAgent

# Initialize Dev Sentinel agents
async def setup_agents():
    # Create Dev Sentinel agents
    vcma = VersionControlMasterAgent(agent_id="vcma")
    vcla = VersionControlListenerAgent(agent_id="vcla")
    cdia = CodeDocumentationInspectorAgent(agent_id="cdia")
    rdia = ReadmeDocumentationInspectorAgent(agent_id="rdia")
    saa = StaticAnalysisAgent(agent_id="saa")
    
    # Initialize agents
    await vcma.initialize()
    await vcla.initialize()
    await cdia.initialize()
    await rdia.initialize()
    await saa.initialize()
    
    # Create fast-agent adapters
    vcma_adapter = VCMAFastAdapter(vcma, servers=["vcs", "filesystem"])
    vcla_adapter = VCLAFastAdapter(vcla, servers=["vcs"])
    cdia_adapter = CDIAFastAdapter(cdia, servers=["documentation", "filesystem"])
    rdia_adapter = RDIAFastAdapter(rdia, servers=["documentation", "filesystem"])
    saa_adapter = SAAFastAdapter(saa, servers=["code_analysis", "filesystem"])
    
    # Create fast-agents
    vcma_fast = vcma_adapter.create_fast_agent()
    vcla_fast = vcla_adapter.create_fast_agent()
    cdia_fast = cdia_adapter.create_fast_agent()
    rdia_fast = rdia_adapter.create_fast_agent()
    saa_fast = saa_adapter.create_fast_agent()
    
    return {
        "vcma": vcma_fast,
        "vcla": vcla_fast,
        "cdia": cdia_fast,
        "rdia": rdia_fast,
        "saa": saa_fast
    }

# Define a workflow that chains documentation inspection and code analysis
@fast.chain(
    name="inspect_and_analyze",
    sequence=["rdia", "cdia", "saa"]
)
async def inspect_and_analyze_workflow():
    \"\"\"Inspect documentation and analyze code quality.\"\"\"
    pass

async def main():
    # Set up the agents
    agents = await setup_agents()
    
    # Start an interactive session
    from fast_agent_mcp import run
    async with run() as agent:
        # You can directly use specific agents
        await agent.vcma("Check if there are any changes to commit")
        
        # Or use workflows
        await agent.inspect_and_analyze("Analyze the codebase and provide improvement recommendations")

if __name__ == "__main__":
    asyncio.run(main())
""",

        "yung_command_processor.py": """
import asyncio
import re
import fast_agent_mcp as fast
from integration.fast_agent.specialized_adapters import (
    VCMAFastAdapter, VCLAFastAdapter, CDIAFastAdapter, 
    RDIAFastAdapter, SAAFastAdapter
)

# YUNG command processor for fast-agent
@fast.agent(
    name="yung_processor",
    instruction=\"\"\"
    You are the YUNG command processor agent, responsible for parsing and executing
    commands in the YUNG (YES Ultimate Net Good) universal instruction set.
    
    Command Structure:
    - $<COMMAND> [ARGS] [CHAINED_COMMANDS with ";"]
    
    Primary Commands:
    - $VIC [SCOPE] - Validate integrity of code/documentation
    - $CODE [SCOPE] [ACTIONS] [STAGE] - Code generation, patching, updates
    - $PP <PREPROCESSOR> - Preprocess external resources
    - $CLOG - Output debug logs
    - $man - Display command manual
    
    For more details, refer to the YUNG specification documentation.
    \"\"\"
    """
    }
async def yung_processor():
    """YUNG command processor agent."""
    pass

# Command parser function
async def parse_yung_command(command: str):
    """
    Parse a YUNG command string.
    
    Args:
        command: The YUNG command to parse
        
    Returns:
        Dict containing parsed command components
    """
    # Basic command regex patterns
    vic_pattern = r'\\$VIC\\s+(ALL|LAST|DOCS|FILE=([^\\s;]+))'
    code_pattern = r'\\$CODE\\s+(TIER=([^\\s,;]+)|ALL)(?:\\s+([^;]+))?(?:\\s+Stage\\s+([^;]+))?'
    pp_pattern = r'\\$PP\\s+([^\\s;]+)'
    clog_pattern = r'\\$CLOG'
    man_pattern = r'\\$man'
    
    # Split by semicolons to handle chained commands
    commands = command.split(';')
    parsed_commands = []
    
    for cmd in commands:
        cmd = cmd.strip()
        
        # Match VIC command
        vic_match = re.match(vic_pattern, cmd)
        if vic_match:
            scope = vic_match.group(1)
            file_path = vic_match.group(2) if 'FILE=' in scope else None
            parsed_commands.append({
                'command': 'VIC',
                'scope': scope.replace(f'FILE={file_path}', 'FILE') if file_path else scope,
                'file_path': file_path
            })
            continue
            
        # Match CODE command
        code_match = re.match(code_pattern, cmd)
        if code_match:
            tier = code_match.group(2) if code_match.group(2) else 'ALL'
            actions_str = code_match.group(3)
            stage = code_match.group(4)
            
            actions = []
            if actions_str:
                for action in actions_str.split(','):
                    action = action.strip()
                    if '=' in action:
                        action_type, action_value = action.split('=', 1)
                        actions.append({
                            'type': action_type,
                            'value': action_value
                        })
                    else:
                        actions.append({
                            'type': action,
                            'value': None
                        })
            
            parsed_commands.append({
                'command': 'CODE',
                'tier': tier,
                'actions': actions,
                'stage': stage
            })
            continue
            
        # Match PP command
        pp_match = re.match(pp_pattern, cmd)
        if pp_match:
            preprocessor = pp_match.group(1)
            parsed_commands.append({
                'command': 'PP',
                'preprocessor': preprocessor
            })
            continue
            
        # Match CLOG command
        if re.match(clog_pattern, cmd):
            parsed_commands.append({
                'command': 'CLOG'
            })
            continue
            
        # Match man command
        if re.match(man_pattern, cmd):
            parsed_commands.append({
                'command': 'man'
            })
            continue
    
    return parsed_commands

# # Example usage
# async def process_yung_commands():
#     """Process YUNG commands using fast-agent."""
#     async with fast.run() as agent:
#         while True:
#             command = input("Enter YUNG command (or 'exit' to quit): ")
#             if command.lower() == 'exit':
#                 break
                
#             # Parse the command
#             parsed_commands = await parse_yung_command(command)
            
#             # Process each command
#             for cmd in parsed_commands:
#                 if cmd['command'] == 'VIC':
#                     if cmd.get('scope') == 'DOCS':
#                         await agent.rdia(f"Validate documentation integrity")
#                     elif cmd.get('scope') == 'FILE' and cmd.get('file_path'):
#                         await agent.cdia(f"Validate integrity of file {cmd.get('file_path')}")
#                     else:
#                         await agent.cdia(f"Validate code integrity with scope {cmd.get('scope', 'ALL')}")
                
#                 elif cmd['command'] == 'CODE':
#                     action_types = [a['type'] for a in cmd.get('actions', [])]
#                     action_str = ', '.join(action_types) if action_types else "all actions"
#                     await agent.saa(f"Generate or modify code in tier {cmd.get('tier')} with actions: {action_str}")
                
#                 elif cmd['command'] == 'PP':
#                     preprocessor = cmd.get('preprocessor')
#                     await agent.yung_processor(f"Preprocess using {preprocessor}")
                
#                 elif cmd['command'] == 'CLOG':
#                     print("Retrieving logs...")
#                     # This would be implemented to fetch actual logs
                    
#                 elif cmd['command'] == 'man':
#                     with open("YUNG_spec.md", "r") as f:
#                         print(f.read())

if __name__ == "__main__":
    asyncio.run(main())
