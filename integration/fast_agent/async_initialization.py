"""
Asynchronous Initialization for Dev Sentinel with fast-agent Integration.

This module provides asynchronous initialization capabilities for Dev Sentinel's
integration with fast-agent, supporting lazy loading, concurrent agent initialization,
and resilient error handling.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Set, Tuple
import time
import os
import sys

# Ensure proper path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Also add parent directory to handle imports from sibling modules
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import Dev Sentinel components
from core.agent import BaseAgent
from core.message_bus import get_message_bus
from integration.fast_agent.adapter import FastAgentAdapter
from integration.fast_agent.setup import setup_fast_agent_integration, FastAgentSetup

logger = logging.getLogger(__name__)

class AsyncFastAgentInitializer:
    """
    Manages asynchronous initialization of fast-agent integration with Dev Sentinel.
    
    This class implements lazy loading, concurrent initialization, and resilient startup
    for fast-agent integration with Dev Sentinel agents.
    """
    
    def __init__(self, workspace_dir: str = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the async initializer.
        
        Args:
            workspace_dir: Directory where fast-agent integration files will be stored
            config: Optional configuration for the initializer
        """
        self.workspace_dir = workspace_dir or os.getcwd()
        self.config = config or {}
        self.initialization_complete = False
        self.adapters: Dict[str, FastAgentAdapter] = {}
        self.initialization_lock = asyncio.Lock()
        self.initialization_tasks: Dict[str, asyncio.Task] = {}
        self.setup_instance: Optional[FastAgentSetup] = None
        self.max_retry_attempts = self.config.get('max_retry_attempts', 3)
        self.retry_delay = self.config.get('retry_delay', 2.0)  # seconds
        self.concurrent_limit = self.config.get('concurrent_limit', 5)
        self.semaphore = asyncio.Semaphore(self.concurrent_limit)
        self.message_bus = get_message_bus()
        
    async def initialize(self, force_reinstall: bool = False) -> Dict[str, Any]:
        """
        Initialize the fast-agent integration asynchronously.
        
        Args:
            force_reinstall: If True, reinstall dependencies even if already installed
            
        Returns:
            Dictionary containing initialization results
        """
        async with self.initialization_lock:
            if self.initialization_complete and not force_reinstall:
                logger.info("Fast-agent integration already initialized")
                return {"status": "success", "message": "Already initialized"}
            
            try:
                # Create integration directory if needed
                integration_dir = os.path.join(self.workspace_dir, ".fast_agent")
                
                # Run setup with retry logic
                setup_result = await self._retry_operation(
                    lambda: setup_fast_agent_integration(
                        output_dir=integration_dir,
                        install_dependencies=True
                    ),
                    max_attempts=self.max_retry_attempts,
                    operation_name="fast-agent integration setup"
                )
                
                # Create setup instance for later use
                self.setup_instance = FastAgentSetup(integration_dir)
                
                # Mark initialization as complete
                self.initialization_complete = True
                
                # Notify via message bus
                await self._publish_initialization_event("initialized", None)
                
                return {
                    "status": "success", 
                    "details": setup_result,
                    "integration_dir": integration_dir
                }
                
            except Exception as e:
                logger.error(f"Failed to initialize fast-agent integration: {e}")
                await self._publish_initialization_event("failed", str(e))
                return {"status": "error", "message": str(e)}
    
    async def get_adapter(self, agent: BaseAgent, adapter_type: str = None) -> FastAgentAdapter:
        """
        Get or create a fast-agent adapter for the given Dev Sentinel agent.
        
        Args:
            agent: The Dev Sentinel agent to adapt
            adapter_type: Optional adapter type to create a specialized adapter
            
        Returns:
            The fast-agent adapter for the agent
        """
        # Ensure initialization is complete
        if not self.initialization_complete:
            await self.initialize()
        
        # Use agent ID as key for adapter cache
        adapter_key = f"{agent.agent_id}_{adapter_type or 'base'}"
        
        # Return existing adapter if available
        if adapter_key in self.adapters:
            return self.adapters[adapter_key]
        
        # If initialization is in progress for this adapter, wait for it
        if adapter_key in self.initialization_tasks:
            try:
                return await self.initialization_tasks[adapter_key]
            except Exception as e:
                logger.error(f"Failed to initialize adapter {adapter_key}: {e}")
                # Fall through to create a new adapter
        
        # Create initialization task
        task = asyncio.create_task(self._create_adapter(agent, adapter_type))
        self.initialization_tasks[adapter_key] = task
        
        try:
            # Wait for adapter creation
            adapter = await task
            self.adapters[adapter_key] = adapter
            return adapter
        except Exception as e:
            logger.error(f"Failed to create adapter for {agent.agent_id}: {e}")
            raise
        finally:
            # Clean up task reference
            if adapter_key in self.initialization_tasks:
                del self.initialization_tasks[adapter_key]
    
    async def _create_adapter(self, agent: BaseAgent, adapter_type: str = None) -> FastAgentAdapter:
        """
        Create a fast-agent adapter for the given agent.
        
        Args:
            agent: The Dev Sentinel agent to adapt
            adapter_type: Optional adapter type to create a specialized adapter
            
        Returns:
            The created adapter
        """
        # Limit concurrent adapter creation
        async with self.semaphore:
            # Import specialized adapters if needed
            adapter: FastAgentAdapter
            
            if adapter_type:
                try:
                    # Dynamically import the specialized adapter class
                    from integration.fast_agent.specialized_adapters import (
                        VCMAFastAdapter, VCLAFastAdapter, CDIAFastAdapter, 
                        RDIAFastAdapter, SAAFastAdapter
                    )
                    
                    # Select appropriate adapter class based on type
                    adapter_class = {
                        'vcma': VCMAFastAdapter,
                        'vcla': VCLAFastAdapter,
                        'cdia': CDIAFastAdapter,
                        'rdia': RDIAFastAdapter,
                        'saa': SAAFastAdapter
                    }.get(adapter_type.lower())
                    
                    if adapter_class:
                        # Determine appropriate servers based on adapter type
                        servers = self._get_servers_for_adapter(adapter_type)
                        adapter = adapter_class(agent, servers=servers)
                    else:
                        logger.warning(f"Unknown adapter type: {adapter_type}, using base adapter")
                        adapter = FastAgentAdapter(agent)
                        
                except ImportError as e:
                    logger.error(f"Failed to import specialized adapter: {e}")
                    adapter = FastAgentAdapter(agent)
            else:
                adapter = FastAgentAdapter(agent)
            
            # Create the fast-agent
            adapter.create_fast_agent()
            
            return adapter
    
    def _get_servers_for_adapter(self, adapter_type: str) -> List[str]:
        """
        Get appropriate server list for an adapter type.
        
        Args:
            adapter_type: The type of adapter
            
        Returns:
            List of server names appropriate for the adapter
        """
        # Default server mappings
        server_mappings = {
            'vcma': ["vcs", "filesystem"],
            'vcla': ["vcs"],
            'cdia': ["documentation", "filesystem"],
            'rdia': ["documentation", "filesystem"],
            'saa': ["code_analysis", "filesystem"],
        }
        
        # Return configured servers or default mapping
        adapter_config = self.config.get('adapters', {}).get(adapter_type, {})
        return adapter_config.get('servers', server_mappings.get(adapter_type.lower(), []))
    
    async def _retry_operation(self, operation: Callable, max_attempts: int, operation_name: str) -> Any:
        """
        Retry an async operation with exponential backoff.
        
        Args:
            operation: The async operation to retry
            max_attempts: Maximum number of retry attempts
            operation_name: Name of the operation for logging
            
        Returns:
            The result of the operation
            
        Raises:
            Exception: If all retry attempts fail
        """
        attempt = 0
        last_exception = None
        
        while attempt < max_attempts:
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt} for {operation_name}")
                    
                return await operation()
                
            except Exception as e:
                last_exception = e
                attempt += 1
                
                if attempt < max_attempts:
                    wait_time = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(f"{operation_name} failed (attempt {attempt}/{max_attempts}): {e}")
                    logger.info(f"Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"{operation_name} failed after {max_attempts} attempts: {e}")
                    
        raise last_exception
    
    async def _publish_initialization_event(self, status: str, error: Optional[str]) -> None:
        """
        Publish initialization status event to message bus.
        
        Args:
            status: Status of initialization ('initialized', 'failed', etc.)
            error: Optional error message if status is 'failed'
        """
        event_data = {
            "event_type": "fast_agent.initialization",
            "status": status,
            "timestamp": time.time(),
        }
        
        if error:
            event_data["error"] = error
            
        try:
            await self.message_bus.publish("fast_agent.initialization", event_data)
        except Exception as e:
            logger.error(f"Failed to publish initialization event: {e}")


# Singleton instance for the initializer
_initializer_instance: Optional[AsyncFastAgentInitializer] = None

def get_async_initializer(workspace_dir: str = None, config: Dict[str, Any] = None) -> AsyncFastAgentInitializer:
    """
    Get or create the singleton initializer instance.
    
    Args:
        workspace_dir: Directory where fast-agent integration files will be stored
        config: Optional configuration for the initializer
        
    Returns:
        The singleton initializer instance
    """
    global _initializer_instance
    
    if _initializer_instance is None:
        _initializer_instance = AsyncFastAgentInitializer(workspace_dir, config)
        
    return _initializer_instance

async def initialize_fast_agent(workspace_dir: str = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Initialize fast-agent integration asynchronously.
    
    Args:
        workspace_dir: Directory where fast-agent integration files will be stored
        config: Optional configuration for the initializer
        
    Returns:
        Dictionary containing initialization results
    """
    initializer = get_async_initializer(workspace_dir, config)
    return await initializer.initialize()