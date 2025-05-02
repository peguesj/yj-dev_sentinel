"""
Terminal Manager for FORCE architecture.

This module provides terminal allocation, persistence, and management
for the FORCE architecture's subagent-specific terminals.
"""

import os
import json
import uuid
import asyncio
import subprocess
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

class TerminalSession:
    """Represents a persistent terminal session for a subagent."""
    
    def __init__(self, terminal_id: str, subagent_name: str, 
                 working_dir: Optional[str] = None):
        """
        Initialize a terminal session.
        
        Args:
            terminal_id: Unique identifier for this terminal
            subagent_name: Name of the subagent using this terminal
            working_dir: Initial working directory (defaults to current)
        """
        self.terminal_id = terminal_id
        self.subagent_name = subagent_name
        self.working_dir = working_dir or os.getcwd()
        self.process = None
        self.env_vars = {}
        self.command_history = []
        self.active = False
        self.last_active = datetime.now().isoformat()
        self.tracked_files = []
        self.cached_assets = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the terminal session.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            self.active = True
            self.last_active = datetime.now().isoformat()
            return True
        except Exception as e:
            print(f"Error initializing terminal session {self.terminal_id}: {str(e)}")
            return False
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a command in this terminal.
        
        Args:
            command: Command to execute
            
        Returns:
            Dict containing command execution results
        """
        try:
            start_time = datetime.now()
            # Use subprocess to run the command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_dir,
                env=os.environ.update(self.env_vars),
                text=True
            )
            
            # Capture output
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            end_time = datetime.now()
            
            # Update last active timestamp
            self.last_active = end_time.isoformat()
            
            # Record command in history
            command_record = {
                "command": command,
                "timestamp": start_time.isoformat(),
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "exit_code": exit_code
            }
            self.command_history.append(command_record)
            
            # Limit command history length
            if len(self.command_history) > 50:
                self.command_history = self.command_history[-50:]
                
            return {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "command": command,
                "terminal_id": self.terminal_id
            }
        except Exception as e:
            return {
                "error": str(e),
                "command": command,
                "terminal_id": self.terminal_id,
                "exit_code": -1
            }
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of this terminal session.
        
        Returns:
            Dict representing the terminal state
        """
        return {
            "terminal_id": self.terminal_id,
            "subagent": self.subagent_name,
            "state": {
                "working_directory": self.working_dir,
                "active": self.active,
                "last_active": self.last_active,
                "last_commands": self.command_history[-5:] if self.command_history else [],
                "tracked_files": self.tracked_files,
                "env_vars": self.env_vars
            }
        }
    
    def update_state(self, state_updates: Dict[str, Any]) -> None:
        """
        Update terminal state with new values.
        
        Args:
            state_updates: Dict containing state values to update
        """
        if "working_directory" in state_updates:
            self.working_dir = state_updates["working_directory"]
            
        if "env_vars" in state_updates:
            self.env_vars.update(state_updates["env_vars"])
            
        if "tracked_files" in state_updates:
            self.tracked_files = state_updates["tracked_files"]
            
        if "active" in state_updates:
            self.active = state_updates["active"]
            
        self.last_active = datetime.now().isoformat()


class TerminalManager:
    """Manager for persistent terminal sessions."""
    
    def __init__(self, state_dir: Optional[str] = None):
        """
        Initialize the terminal manager.
        
        Args:
            state_dir: Directory to store terminal state (defaults to .force/terminals)
        """
        self.terminals: Dict[str, TerminalSession] = {}
        self.state_dir = state_dir or os.path.join(os.getcwd(), ".force", "terminals")
        os.makedirs(self.state_dir, exist_ok=True)
        
    async def create_terminal(self, subagent_name: str, terminal_id: Optional[str] = None,
                             working_dir: Optional[str] = None) -> str:
        """
        Create a new terminal for a subagent.
        
        Args:
            subagent_name: Name of the subagent
            terminal_id: Optional terminal ID (generated if not provided)
            working_dir: Optional working directory
            
        Returns:
            Terminal ID
        """
        # Generate terminal ID if not provided
        if not terminal_id:
            terminal_id = f"TERMINAL-{subagent_name.upper()}"
            
        # Check if terminal already exists
        if terminal_id in self.terminals:
            return terminal_id
            
        # Create new terminal
        terminal = TerminalSession(terminal_id, subagent_name, working_dir)
        await terminal.initialize()
        self.terminals[terminal_id] = terminal
        
        # Save terminal state
        self._save_terminal_state(terminal)
        
        return terminal_id
        
    async def get_terminal(self, terminal_id: str) -> Optional[TerminalSession]:
        """
        Get a terminal by ID.
        
        Args:
            terminal_id: ID of the terminal to get
            
        Returns:
            Terminal session or None if not found
        """
        # If terminal exists in memory, return it
        if terminal_id in self.terminals:
            return self.terminals[terminal_id]
            
        # Try to load terminal from disk
        terminal = self._load_terminal_state(terminal_id)
        if terminal:
            await terminal.initialize()
            self.terminals[terminal_id] = terminal
            return terminal
            
        return None
        
    async def execute_in_terminal(self, terminal_id: str, command: str) -> Dict[str, Any]:
        """
        Execute a command in a specific terminal.
        
        Args:
            terminal_id: ID of the terminal to use
            command: Command to execute
            
        Returns:
            Dict containing command execution results
        """
        terminal = await self.get_terminal(terminal_id)
        if not terminal:
            return {
                "error": f"Terminal {terminal_id} not found",
                "command": command,
                "exit_code": -1
            }
            
        result = await terminal.execute_command(command)
        
        # Save updated terminal state
        self._save_terminal_state(terminal)
        
        return result
        
    def _save_terminal_state(self, terminal: TerminalSession) -> None:
        """
        Save terminal state to disk.
        
        Args:
            terminal: Terminal session to save
        """
        state_path = os.path.join(self.state_dir, f"{terminal.terminal_id}.json")
        with open(state_path, "w") as f:
            json.dump(terminal.get_state(), f, indent=2)
            
    def _load_terminal_state(self, terminal_id: str) -> Optional[TerminalSession]:
        """
        Load terminal state from disk.
        
        Args:
            terminal_id: ID of the terminal to load
            
        Returns:
            Terminal session or None if not found
        """
        state_path = os.path.join(self.state_dir, f"{terminal_id}.json")
        if not os.path.exists(state_path):
            return None
            
        try:
            with open(state_path, "r") as f:
                state = json.load(f)
                
            terminal = TerminalSession(
                terminal_id=state["terminal_id"],
                subagent_name=state["subagent"],
                working_dir=state["state"].get("working_directory")
            )
            
            # Restore state
            if "env_vars" in state["state"]:
                terminal.env_vars = state["state"]["env_vars"]
                
            if "tracked_files" in state["state"]:
                terminal.tracked_files = state["state"]["tracked_files"]
                
            if "last_commands" in state["state"] and state["state"]["last_commands"]:
                terminal.command_history = state["state"]["last_commands"]
                
            terminal.active = state["state"].get("active", False)
            terminal.last_active = state["state"].get("last_active", datetime.now().isoformat())
            
            return terminal
        except Exception as e:
            print(f"Error loading terminal state for {terminal_id}: {str(e)}")
            return None
            
    async def get_or_create_terminal(self, subagent_name: str) -> TerminalSession:
        """
        Get a terminal for a subagent or create one if it doesn't exist.
        
        Args:
            subagent_name: Name of the subagent
            
        Returns:
            Terminal session
        """
        terminal_id = f"TERMINAL-{subagent_name.upper()}"
        terminal = await self.get_terminal(terminal_id)
        if not terminal:
            await self.create_terminal(subagent_name, terminal_id)
            terminal = await self.get_terminal(terminal_id)
        return terminal
        
    async def list_terminals(self) -> List[Dict[str, Any]]:
        """
        List all active terminals.
        
        Returns:
            List of terminal state dictionaries
        """
        terminals = []
        
        # Get terminals from memory
        for terminal_id, terminal in self.terminals.items():
            terminals.append(terminal.get_state())
            
        # Get terminals from disk that aren't in memory
        for filename in os.listdir(self.state_dir):
            if filename.endswith(".json"):
                terminal_id = filename[:-5]  # Remove .json extension
                if terminal_id not in self.terminals:
                    terminal = self._load_terminal_state(terminal_id)
                    if terminal:
                        terminals.append(terminal.get_state())
                        
        return terminals


# Global terminal manager instance
_terminal_manager: Optional[TerminalManager] = None

async def get_terminal_manager() -> TerminalManager:
    """
    Get the global terminal manager instance.
    
    Returns:
        Terminal manager instance
    """
    global _terminal_manager
    if not _terminal_manager:
        _terminal_manager = TerminalManager()
    return _terminal_manager


async def execute_in_subagent_terminal(subagent_name: str, command: str) -> Dict[str, Any]:
    """
    Execute a command in a subagent's terminal.
    
    Args:
        subagent_name: Name of the subagent
        command: Command to execute
        
    Returns:
        Dict containing command execution results
    """
    terminal_manager = await get_terminal_manager()
    terminal = await terminal_manager.get_or_create_terminal(subagent_name)
    return await terminal_manager.execute_in_terminal(terminal.terminal_id, command)