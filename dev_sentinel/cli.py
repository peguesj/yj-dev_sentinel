"""
Dev Sentinel CLI

Main command-line interface for Dev Sentinel package.
"""

import click
import sys
import os
from pathlib import Path

from dev_sentinel import __version__
from dev_sentinel.core.agent import BaseAgent as Agent
from dev_sentinel.force import ForceEngine


@click.group()
@click.version_option(__version__)
@click.pass_context
def main(ctx):
    """Dev Sentinel - AI-powered development sentinel with Force framework."""
    ctx.ensure_object(dict)


@main.command()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def start(config, verbose):
    """Start the Dev Sentinel system."""
    click.echo(f"Starting Dev Sentinel v{__version__}")
    
    if verbose:
        click.echo(f"Configuration: {config or 'default'}")
    
    # Initialize Force engine
    try:
        force_engine = ForceEngine()
        click.echo("✅ Force engine initialized")
    except Exception as e:
        click.echo(f"❌ Failed to initialize Force engine: {e}")
        sys.exit(1)
    
    # Start agents
    click.echo("🤖 Starting AI agents...")
    # TODO: Implement agent startup logic
    
    click.echo("✅ Dev Sentinel started successfully")


@main.command()
def status():
    """Check Dev Sentinel system status."""
    click.echo("📊 Dev Sentinel Status")
    click.echo("=" * 30)
    
    # Check Force engine
    try:
        force_engine = ForceEngine()
        tools_count = len(force_engine.list_tools())
        click.echo(f"✅ Force Engine: OK ({tools_count} tools loaded)")
    except Exception as e:
        click.echo(f"❌ Force Engine: ERROR - {e}")
    
    # Check .venv
    venv_path = Path('.venv')
    if venv_path.exists():
        click.echo("✅ Virtual Environment: OK")
    else:
        click.echo("⚠️  Virtual Environment: Not found")
    
    # Check configuration
    config_path = Path('config/fastagent.config.yaml')
    if config_path.exists():
        click.echo("✅ Configuration: OK")
    else:
        click.echo("⚠️  Configuration: Default")


@main.command()
@click.argument('tool_name')
@click.option('--params', '-p', help='Tool parameters as JSON')
def force(tool_name, params):
    """Execute a Force tool."""
    try:
        force_engine = ForceEngine()
        
        # Parse parameters
        tool_params = {}
        if params:
            import json
            tool_params = json.loads(params)
        
        # Execute tool
        click.echo(f"🔧 Executing Force tool: {tool_name}")
        result = force_engine.execute_tool(tool_name, tool_params)
        
        if result.get('success'):
            click.echo("✅ Tool executed successfully")
            if result.get('output'):
                click.echo(result['output'])
        else:
            click.echo(f"❌ Tool execution failed: {result.get('error')}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error executing tool: {e}")
        sys.exit(1)


@main.command()
def init():
    """Initialize Dev Sentinel in current directory."""
    click.echo("🚀 Initializing Dev Sentinel...")
    
    # Create .force directory
    force_dir = Path('.force')
    if not force_dir.exists():
        force_dir.mkdir()
        click.echo("✅ Created .force directory")
    
    # Initialize Force system
    try:
        force_engine = ForceEngine()
        # Use force_init_system tool if available
        result = force_engine.execute_tool('force_init_system', {})
        if result.get('success'):
            click.echo("✅ Force system initialized")
        else:
            click.echo("⚠️  Force system partially initialized")
    except Exception as e:
        click.echo(f"⚠️  Could not fully initialize Force system: {e}")
    
    # Create config directory
    config_dir = Path('config')
    if not config_dir.exists():
        config_dir.mkdir()
        click.echo("✅ Created config directory")
    
    click.echo("✅ Dev Sentinel initialization complete")


@main.command()
def servers():
    """Show information about available MCP servers."""
    click.echo("🖥️  Available MCP Servers")
    click.echo("=" * 30)
    
    servers_info = [
        ("force-mcp-stdio", "Force MCP server with stdio transport"),
        ("dev-sentinel-stdio", "Dev Sentinel MCP server with stdio transport"),
        ("force-mcp-http", "Force MCP server with HTTP transport"),
        ("dev-sentinel-http", "Dev Sentinel MCP server with HTTP transport"),
    ]
    
    for cmd, desc in servers_info:
        click.echo(f"• {cmd:<20} - {desc}")
    
    click.echo("\nUsage examples:")
    click.echo("  force-mcp-stdio --help")
    click.echo("  dev-sentinel-http --port 8080")
    click.echo("  force-mcp-http --debug --port 9000")


if __name__ == '__main__':
    main()
