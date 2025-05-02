"""
Task Manager for Dev Sentinel Agents

This module defines the task management system used by the Dev Sentinel agent ecosystem
for creating, tracking, and processing tasks.

The Task Manager provides:
- Task creation with priorities and metadata
- Task status tracking throughout the lifecycle
- Handler registration for different task types
- Concurrent task execution with controlled parallelism
- Task cancellation and error handling
- Queue statistics and monitoring

It serves as a central coordinator for work distribution within the
Dev Sentinel autonomous agent architecture.
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status states for tasks in the system"""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """
    Representation of a task in the Dev Sentinel ecosystem
    
    A Task is a unit of work that needs to be performed by an agent in the system.
    It contains all the information needed to execute the work, track its progress,
    and store the results. Tasks move through different states from creation to
    completion and maintain a complete audit trail of their execution.
    
    Tasks have priorities to determine execution order and support
    detailed logging for monitoring and debugging.
    """
    
    def __init__(self, 
                task_type: str, 
                params: Dict[str, Any], 
                creator_id: str,
                priority: int = 5,
                task_id: Optional[str] = None):
        """
        Initialize a new task.
        
        Args:
            task_type: Type of task to perform
            params: Parameters needed to perform the task
            creator_id: ID of the agent creating this task
            priority: Task priority (1-10, with 10 being highest)
            task_id: Optional task ID, generated if not provided
        """
        self.task_id = task_id or str(uuid.uuid4())
        self.task_type = task_type
        self.params = params
        self.creator_id = creator_id
        self.priority = min(max(priority, 1), 10)  # Ensure priority is between 1-10
        
        self.status = TaskStatus.CREATED
        self.assigned_to: Optional[str] = None
        self.creation_time = datetime.now()
        self.start_time: Optional[datetime] = None
        self.completion_time: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.logs: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary representation.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "params": self.params,
            "creator_id": self.creator_id,
            "priority": self.priority,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "creation_time": self.creation_time.isoformat(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "completion_time": self.completion_time.isoformat() if self.completion_time else None,
            "result": self.result,
            "error": self.error
        }
    
    def add_log(self, log_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a log entry to the task.
        
        Args:
            log_type: Type of log entry (info, warning, error, etc.)
            message: Log message
            details: Optional additional details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": log_type,
            "message": message,
            "details": details or {}
        }
        self.logs.append(log_entry)


class TaskManager:
    """
    Manages tasks across the Dev Sentinel ecosystem
    
    The TaskManager is a central coordinator for the execution of tasks within
    the agent ecosystem. It maintains queues of pending tasks, matches them with
    appropriate handlers, and ensures they are executed efficiently.
    
    Features:
    - Priority-based task scheduling
    - Task type-specific handler registration
    - Concurrent task execution with controlled parallelism
    - Task lifecycle tracking and status management
    - Comprehensive logging and error handling
    - Task cancellation support
    - Queue monitoring and statistics
    
    Tasks flow through the system in the following lifecycle:
    1. Creation (CREATED status)
    2. Queueing (QUEUED status) 
    3. Processing (RUNNING status)
    4. Completion (COMPLETED, FAILED, or CANCELLED status)
    """
    
    def __init__(self):
        """Initialize the task manager with empty task collections."""
        self._tasks: Dict[str, Task] = {}
        self._task_queue: List[Task] = []
        self._processing_tasks: Dict[str, Task] = {}
        self._task_handlers: Dict[str, List[Callable[[Task], Awaitable[Dict[str, Any]]]]] = {}
        logger.info("Task Manager initialized")
    
    def create_task(self, 
                   task_type: str, 
                   params: Dict[str, Any], 
                   creator_id: str,
                   priority: int = 5) -> Task:
        """
        Create a new task in the system.
        
        Args:
            task_type: Type of task to create
            params: Parameters for the task
            creator_id: ID of agent creating the task
            priority: Task priority (1-10)
            
        Returns:
            The created Task object
        """
        task = Task(task_type, params, creator_id, priority)
        self._tasks[task.task_id] = task
        self._task_queue.append(task)
        
        # Sort queue by priority
        self._task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        logger.info(f"Created task {task.task_id} of type {task_type}")
        return task
    
    def register_handler(self, 
                        task_type: str, 
                        handler: Callable[[Task], Awaitable[Dict[str, Any]]]) -> None:
        """
        Register a handler function for a specific task type.
        
        Args:
            task_type: The type of task this handler can process
            handler: Async function that processes tasks of this type
        """
        if task_type not in self._task_handlers:
            self._task_handlers[task_type] = []
            
        self._task_handlers[task_type].append(handler)
        logger.debug(f"Registered handler for task type {task_type}")
    
    def unregister_handler(self, 
                          task_type: str, 
                          handler: Callable[[Task], Awaitable[Dict[str, Any]]]) -> bool:
        """
        Unregister a handler function.
        
        Args:
            task_type: The task type to unregister from
            handler: The handler function to remove
            
        Returns:
            True if successfully unregistered, False otherwise
        """
        if task_type not in self._task_handlers:
            logger.warning(f"Attempted to unregister handler for non-existent task type: {task_type}")
            return False
        
        try:
            self._task_handlers[task_type].remove(handler)
            logger.debug(f"Unregistered handler from task type {task_type}")
            
            # Clean up empty handler lists
            if not self._task_handlers[task_type]:
                del self._task_handlers[task_type]
                
            return True
        except ValueError:
            logger.warning(f"Attempted to unregister non-existent handler from task type: {task_type}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            Task object if found, None otherwise
        """
        return self._tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get all tasks with a specific status.
        
        Args:
            status: The status to filter by
            
        Returns:
            List of tasks with the specified status
        """
        return [task for task in self._tasks.values() if task.status == status]
    
    def get_tasks_by_creator(self, creator_id: str) -> List[Task]:
        """
        Get all tasks created by a specific agent.
        
        Args:
            creator_id: The ID of the creator agent
            
        Returns:
            List of tasks created by the specified agent
        """
        return [task for task in self._tasks.values() if task.creator_id == creator_id]
    
    async def process_next_task(self) -> Optional[Task]:
        """
        Process the next task in the queue if handlers are available.
        
        Returns:
            The task that was processed, or None if no tasks were processed
        """
        if not self._task_queue:
            return None
            
        # Find the first task that has a registered handler
        task_to_process = None
        for i, task in enumerate(self._task_queue):
            if task.task_type in self._task_handlers and self._task_handlers[task.task_type]:
                task_to_process = task
                del self._task_queue[i]
                break
        
        if not task_to_process:
            logger.warning("No handlers available for any tasks in queue")
            return None
            
        # Update task status
        task_to_process.status = TaskStatus.RUNNING
        task_to_process.start_time = datetime.now()
        self._processing_tasks[task_to_process.task_id] = task_to_process
        
        try:
            # Get the first registered handler for this task type
            handler = self._task_handlers[task_to_process.task_type][0]
            
            # Execute the handler
            result = await handler(task_to_process)
            
            # Update task with result
            task_to_process.result = result
            task_to_process.status = TaskStatus.COMPLETED
            task_to_process.completion_time = datetime.now()
            task_to_process.add_log("info", "Task completed successfully", {"result": result})
            logger.info(f"Task {task_to_process.task_id} completed successfully")
            
        except Exception as e:
            # Handle errors
            error_message = str(e)
            task_to_process.status = TaskStatus.FAILED
            task_to_process.error = error_message
            task_to_process.completion_time = datetime.now()
            task_to_process.add_log("error", "Task failed", {"error": error_message})
            logger.error(f"Task {task_to_process.task_id} failed: {error_message}")
            
        # Remove from processing list
        del self._processing_tasks[task_to_process.task_id]
        
        return task_to_process
    
    async def process_tasks_continuously(self, 
                                        interval: float = 0.1, 
                                        max_concurrent: int = 5) -> None:
        """
        Process tasks continuously in the background.
        
        Args:
            interval: Time in seconds to wait between processing batches
            max_concurrent: Maximum number of tasks to process concurrently
        """
        logger.info(f"Starting continuous task processing (interval={interval}s, max_concurrent={max_concurrent})")
        
        while True:
            # Don't exceed max_concurrent processing tasks
            if len(self._processing_tasks) >= max_concurrent:
                await asyncio.sleep(interval)
                continue
                
            # Process as many tasks as we can up to max_concurrent
            available_slots = max_concurrent - len(self._processing_tasks)
            if available_slots > 0 and self._task_queue:
                # Create tasks for processing
                process_tasks = []
                for _ in range(min(available_slots, len(self._task_queue))):
                    process_task = asyncio.create_task(self.process_next_task())
                    process_tasks.append(process_task)
                
                # Wait for all tasks to complete
                if process_tasks:
                    await asyncio.gather(*process_tasks, return_exceptions=True)
            
            # Sleep before checking again
            await asyncio.sleep(interval)
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task if it hasn't started processing yet.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if successfully cancelled, False otherwise
        """
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Attempted to cancel non-existent task: {task_id}")
            return False
            
        # Can only cancel tasks that haven't started
        if task.status != TaskStatus.CREATED and task.status != TaskStatus.QUEUED:
            logger.warning(f"Cannot cancel task {task_id} with status {task.status.value}")
            return False
            
        # Remove from queue if present
        for i, queued_task in enumerate(self._task_queue):
            if queued_task.task_id == task_id:
                del self._task_queue[i]
                break
                
        # Update status
        task.status = TaskStatus.CANCELLED
        task.completion_time = datetime.now()
        task.add_log("info", "Task was cancelled")
        logger.info(f"Task {task_id} was cancelled")
        
        return True
    
    def get_queue_info(self) -> Dict[str, Any]:
        """
        Get information about the current task queue.
        
        Returns:
            Dictionary with queue statistics
        """
        return {
            "total_tasks": len(self._tasks),
            "queued_tasks": len(self._task_queue),
            "processing_tasks": len(self._processing_tasks),
            "task_types": list(self._task_handlers.keys()),
            "status_counts": {
                status.value: len(self.get_tasks_by_status(status))
                for status in TaskStatus
            }
        }

# Global instance
task_manager = TaskManager()

def get_task_manager() -> TaskManager:
    """
    Get the global task manager instance.
    
    Returns:
        The global TaskManager instance
    """
    return task_manager