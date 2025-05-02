"""
System initialization for the Dev Sentinel FORCE architecture.

This module handles initialization of all required components for running
the Dev Sentinel framework with FORCE integration.
"""

import os
import sys
import argparse
import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("force_initialize")

# Import Dev Sentinel core components
try:
    from core.message_bus import MessageBus
    from core.task_manager import TaskManager
    from integration.terminal_manager import TerminalManager as initialize_terminal_manager
    from integration.fast_agent.setup import setup_fast_agent_integration
    from integration.fast_agent.async_initialization import initialize_fast_agent, get_async_initializer
    from integration.diagram_generator import ArchitectureDiagramGenerator
    from integration.force.master_agent import ForceCommandProcessor
except ImportError as e:
    logger.error(f"Failed to import required components: {e}")
    logger.error("Make sure you're running from the project root directory")
    sys.exit(1)

async def initialize_force_architecture(workspace_dir: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Initialize all components of the FORCE architecture.
    
    Args:
        workspace_dir: Path to workspace directory
        config_path: Path to configuration file (optional)
        
    Returns:
        Dictionary containing initialization results
    """
    logger.info("Initializing FORCE architecture...")
    results = {}
    
    # Create required directories
    os.makedirs(os.path.join(workspace_dir, ".force"), exist_ok=True)
    os.makedirs(os.path.join(workspace_dir, "docs", "diagrams"), exist_ok=True)
    
    # Load configuration if provided, otherwise use defaults
    config = {}
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            config = {}
    
    # Initialize component: Message Bus
    try:
        logger.info("Initializing Message Bus...")
        message_bus = MessageBus()
        results["message_bus"] = {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to initialize Message Bus: {e}")
        results["message_bus"] = {"status": "error", "message": str(e)}
        return results
    
    # Initialize component: Task Manager
    try:
        logger.info("Initializing Task Manager...")
        task_manager = TaskManager(message_bus=message_bus)
        results["task_manager"] = {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to initialize Task Manager: {e}")
        results["task_manager"] = {"status": "error", "message": str(e)}
        return results
    
    # Initialize component: Terminal Manager
    try:
        logger.info("Initializing Terminal Manager...")
        terminal_manager = await initialize_terminal_manager(
            state_dir=os.path.join(workspace_dir, ".force", "terminals")
        )
        results["terminal_manager"] = {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to initialize Terminal Manager: {e}")
        results["terminal_manager"] = {"status": "error", "message": str(e)}
        return results
    
    # Initialize component: Fast-Agent Integration using the new async initialization
    try:
        logger.info("Setting up Fast-Agent Integration (async)...")
        fast_agent_config = config.get('fast_agent', {})
        
        # Start fast-agent initialization as a background task
        # This allows other components to initialize in parallel
        fast_agent_task = asyncio.create_task(
            initialize_fast_agent(
                workspace_dir=os.path.join(workspace_dir, ".force", "fast_agent"),
                config=fast_agent_config
            )
        )
        
        # We'll await this task later to ensure it completes before returning
        results["fast_agent"] = {"status": "initializing"}
    except Exception as e:
        logger.error(f"Failed to start Fast-Agent Integration: {e}")
        results["fast_agent"] = {"status": "error", "message": str(e)}
    
    # Initialize component: Diagram Generator
    try:
        logger.info("Initializing Diagram Generator...")
        diagram_generator = ArchitectureDiagramGenerator(
            output_dir=os.path.join(workspace_dir, "docs", "diagrams")
        )
        results["diagram_generator"] = {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to initialize Diagram Generator: {e}")
        results["diagram_generator"] = {"status": "error", "message": str(e)}
    
    # Initialize component: Force Command Processor
    try:
        logger.info("Initializing Force Command Processor...")
        command_processor = ForceCommandProcessor()
        await command_processor.initialize()
        results["command_processor"] = {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to initialize Force Command Processor: {e}")
        results["command_processor"] = {"status": "error", "message": str(e)}
    
    # Initialize subagent terminals
    try:
        from integration.force.master_agent import SubagentMapping
        
        logger.info("Initializing subagent terminals...")
        subagent_results = {}
        
        for subagent_name, terminal_id in SubagentMapping.SUBAGENT_TERMINALS.items():
            try:
                terminal = await terminal_manager.get_or_create_terminal(
                    subagent_name=subagent_name,
                    terminal_id=terminal_id,
                    working_dir=workspace_dir
                )
                subagent_results[subagent_name] = {"status": "success", "terminal_id": terminal_id}
            except Exception as e:
                logger.error(f"Failed to initialize terminal for {subagent_name}: {e}")
                subagent_results[subagent_name] = {"status": "error", "message": str(e)}
        
        results["subagent_terminals"] = subagent_results
    except Exception as e:
        logger.error(f"Failed to initialize subagent terminals: {e}")
        results["subagent_terminals"] = {"status": "error", "message": str(e)}
    
    # Generate initial diagrams
    try:
        logger.info("Generating system architecture diagrams...")
        await diagram_generator.generate_project_overview_diagram("svg")
        await diagram_generator.generate_force_integration_diagram("svg")
        await diagram_generator.generate_terminal_state_diagram("svg")
        results["initial_diagrams"] = {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to generate initial diagrams: {e}")
        results["initial_diagrams"] = {"status": "error", "message": str(e)}
    
    # Now wait for fast-agent initialization to complete if it was started
    if "fast_agent" in results and results["fast_agent"]["status"] == "initializing":
        try:
            fast_agent_result = await fast_agent_task
            results["fast_agent"] = {
                "status": "success" if fast_agent_result.get("status") == "success" else "error",
                "details": fast_agent_result
            }
            logger.info("Fast-Agent Integration completed asynchronously")
        except Exception as e:
            logger.error(f"Fast-Agent Integration failed asynchronously: {e}")
            results["fast_agent"] = {"status": "error", "message": str(e)}
    
    success_count = sum(1 for component in results.values() 
                      if isinstance(component, dict) and component.get("status") == "success")
    total_components = len(results)
    
    logger.info(f"FORCE architecture initialization complete: {success_count}/{total_components} components successful")
    
    return results

def print_summary(results: Dict[str, Any]) -> None:
    """Print a summary of the initialization results."""
    print("\n" + "="*80)
    print(" DEV SENTINEL FORCE ARCHITECTURE INITIALIZATION SUMMARY ")
    print("="*80)
    
    all_success = True
    
    for component, result in results.items():
        if isinstance(result, dict):
            status = result.get("status", "unknown")
            if status == "success":
                print(f"✅ {component}: Initialized successfully")
            else:
                all_success = False
                message = result.get("message", "Unknown error")
                print(f"❌ {component}: Failed - {message}")
        else:
            all_success = False
            print(f"❓ {component}: Unknown status")
    
    print("\n" + "-"*80)
    if all_success:
        print("🚀 All components initialized successfully!")
        print("\nYou can now start using Dev Sentinel with FORCE integration:")
        print("  - Run `python -m integration.force.master_agent` to start the master agent")
        print("  - Use YUNG commands to interact with the system")
    else:
        print("⚠️ Some components failed to initialize.")
        print("Please check the logs and resolve the issues before proceeding.")
    
    print("-"*80 + "\n")

async def main():
    parser = argparse.ArgumentParser(description="Initialize Dev Sentinel FORCE architecture")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--workspace", type=str, help="Path to workspace directory")
    args = parser.parse_args()
    
    # Determine workspace directory
    workspace_dir = args.workspace if args.workspace else os.getcwd()
    
    # Run initialization
    results = await initialize_force_architecture(
        workspace_dir=workspace_dir,
        config_path=args.config
    )
    
    # Print summary
    print_summary(results)
    
    return 0 if all(isinstance(r, dict) and r.get("status") == "success" for r in results.values()) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)