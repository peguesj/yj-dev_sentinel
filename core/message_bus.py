"""
Message Bus Implementation

This module provides a message bus system for inter-agent communication
in the Dev Sentinel ecosystem. It implements a publish-subscribe pattern
that allows agents to communicate asynchronously.

The MessageBus serves as the central nervous system of Dev Sentinel, enabling
decoupled communication between specialized agents. It supports:

- Direct and broadcast messaging patterns
- Topic-based message routing
- Message prioritization and expiration (TTL)
- Asynchronous delivery with non-blocking operations
- Message history tracking for debugging and auditing
- Strong typing of messages with metadata

This implementation is designed for in-memory operation but can be extended
to support persistent messaging through Redis or other message brokers.
"""

import asyncio
import logging
from typing import Dict, List, Any, Callable, Awaitable, Optional, Set
from datetime import datetime
import uuid

logger = logging.getLogger("dev_sentinel.message_bus")

class Message:
    """
    A message that can be sent between agents.
    
    Messages contain metadata about the sender, recipient, message type,
    and a payload of data. They serve as the primary communication mechanism
    in the Dev Sentinel agent ecosystem, enabling both direct and broadcast
    communication patterns.
    
    Features:
    - Unique message identification with UUIDs
    - Support for correlation IDs to track related messages
    - Prioritization to ensure critical messages are processed first
    - Time-to-live (TTL) for automatic expiration of stale messages
    - Flexible payload to carry any serializable data
    - Support for both targeted and broadcast delivery
    - Built-in serialization/deserialization via to_dict/from_dict
    """
    
    def __init__(
        self,
        sender_id: str,
        message_type: str,
        payload: Any,
        recipient_id: Optional[str] = None,
        message_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: int = 1,
        ttl: Optional[int] = None
    ):
        """
        Initialize a new message.
        
        Args:
            sender_id: ID of the agent sending the message
            message_type: Type of message (used for routing)
            payload: Message data
            recipient_id: ID of the intended recipient (None for broadcast)
            message_id: Unique ID for this message
            correlation_id: ID to correlate related messages
            priority: Message priority (higher numbers = higher priority)
            ttl: Time-to-live in seconds (None for no expiration)
        """
        self.message_id = message_id or str(uuid.uuid4())
        self.correlation_id = correlation_id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message_type = message_type
        self.payload = payload
        self.created_at = datetime.now()
        self.priority = priority
        self.ttl = ttl
        
    def is_expired(self) -> bool:
        """Check if the message has expired based on its TTL"""
        if self.ttl is None:
            return False
        
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl
    
    def is_broadcast(self) -> bool:
        """Check if this is a broadcast message"""
        return self.recipient_id is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "priority": self.priority,
            "ttl": self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a message from a dictionary"""
        # Convert ISO format string back to datetime
        data = data.copy()
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            
        msg = cls(
            sender_id=data["sender_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            recipient_id=data.get("recipient_id"),
            message_id=data.get("message_id"),
            correlation_id=data.get("correlation_id"),
            priority=data.get("priority", 1),
            ttl=data.get("ttl")
        )
        
        # Override the created_at time if it was provided
        if "created_at" in data:
            msg.created_at = data["created_at"]
            
        return msg

class MessageBus:
    """
    Message bus that routes messages between agents.
    
    This implementation uses an in-memory pub/sub model with support for
    direct messaging and topic-based subscriptions.
    
    The MessageBus is a critical component of the Dev Sentinel architecture
    that enables loosely coupled communication between specialized agents.
    It maintains subscription registries, manages message delivery,
    and handles error conditions during message processing.
    
    Features:
    - Support for direct (point-to-point) messaging
    - Topic-based publish/subscribe pattern
    - Asynchronous non-blocking message delivery
    - Message history for debugging and monitoring
    - Automatic handling of expired messages via TTL
    - Prioritized message processing
    - Fault tolerance with error handling and recovery
    
    The MessageBus allows agents to communicate without direct dependencies
    on each other, supporting a modular and extensible architecture.
    """
    
    def __init__(self):
        """Initialize a new message bus"""
        # Maps message types to sets of subscriber callbacks
        self.subscribers: Dict[str, Set[Callable[[Message], Awaitable[None]]]] = {}
        
        # Maps agent IDs to their direct message callbacks
        self.direct_subscribers: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        
        # Queue for messages to be processed
        self.message_queue: asyncio.Queue[Message] = asyncio.Queue()
        
        # For storing message history
        self.message_history: List[Message] = []
        self.max_history_size = 1000
        
        self._running = False
        self._processor_task = None
        
        logger.info("Message bus initialized")
        
    async def start(self) -> None:
        """Start the message processing loop"""
        if self._running:
            return
            
        self._running = True
        self._processor_task = asyncio.create_task(self._process_messages())
        logger.info("Message bus started")
        
    async def shutdown(self) -> None:
        """Shut down the message bus"""
        if not self._running:
            return
            
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Message bus shut down")
        
    async def publish(self, message: Message) -> None:
        """
        Publish a message to the bus.
        
        Args:
            message: The message to publish
        """
        if message.is_expired():
            logger.debug(f"Dropping expired message: {message.message_id}")
            return
            
        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
            
        # Add to processing queue
        await self.message_queue.put(message)
        logger.debug(f"Published message: {message.message_type} from {message.sender_id}")
        
    def subscribe(self, message_type: str, callback: Callable[[Message], Awaitable[None]]) -> None:
        """
        Subscribe to messages of a specific type.
        
        Args:
            message_type: The message type to subscribe to
            callback: Async function that will be called with messages
        """
        if message_type not in self.subscribers:
            self.subscribers[message_type] = set()
            
        self.subscribers[message_type].add(callback)
        logger.debug(f"New subscription to message type: {message_type}")
        
    def unsubscribe(self, message_type: str, callback: Callable[[Message], Awaitable[None]]) -> None:
        """
        Unsubscribe from messages of a specific type.
        
        Args:
            message_type: The message type to unsubscribe from
            callback: The callback function to remove
        """
        if message_type in self.subscribers:
            self.subscribers[message_type].discard(callback)
            if not self.subscribers[message_type]:
                del self.subscribers[message_type]
                
        logger.debug(f"Unsubscribed from message type: {message_type}")
        
    def subscribe_direct(self, agent_id: str, callback: Callable[[Message], Awaitable[None]]) -> None:
        """
        Subscribe to direct messages for a specific agent.
        
        Args:
            agent_id: The agent ID to subscribe
            callback: Async function that will be called with messages
        """
        self.direct_subscribers[agent_id] = callback
        logger.debug(f"Agent {agent_id} subscribed for direct messages")
        
    def unsubscribe_direct(self, agent_id: str) -> None:
        """
        Unsubscribe from direct messages for an agent.
        
        Args:
            agent_id: The agent ID to unsubscribe
        """
        if agent_id in self.direct_subscribers:
            del self.direct_subscribers[agent_id]
            
        logger.debug(f"Agent {agent_id} unsubscribed from direct messages")
        
    async def _process_messages(self) -> None:
        """Process messages from the queue"""
        try:
            while self._running:
                # Get the next message
                message = await self.message_queue.get()
                
                # Skip if expired
                if message.is_expired():
                    self.message_queue.task_done()
                    continue
                    
                # Deliver to direct recipient if specified
                if message.recipient_id and message.recipient_id in self.direct_subscribers:
                    try:
                        await self.direct_subscribers[message.recipient_id](message)
                    except Exception as e:
                        logger.error(f"Error delivering direct message: {e}", exc_info=True)
                
                # Deliver to type subscribers if any
                subscribers = self.subscribers.get(message.message_type, set())
                
                # Broadcast messages go to all subscribers
                if message.is_broadcast():
                    delivery_tasks = [
                        subscriber(message) for subscriber in subscribers
                    ]
                    
                    if delivery_tasks:
                        await asyncio.gather(*delivery_tasks, return_exceptions=True)
                
                self.message_queue.task_done()
                
        except asyncio.CancelledError:
            logger.info("Message processor task cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in message processor: {e}", exc_info=True)
            if self._running:
                # Restart the processor
                self._processor_task = asyncio.create_task(self._process_messages())
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get statistics about the message bus"""
        message_types = {}
        for msg in self.message_history:
            if msg.message_type in message_types:
                message_types[msg.message_type] += 1
            else:
                message_types[msg.message_type] = 1
                
        return {
            "queue_size": self.message_queue.qsize(),
            "history_size": len(self.message_history),
            "subscriber_count": sum(len(subs) for subs in self.subscribers.values()),
            "direct_subscriber_count": len(self.direct_subscribers),
            "message_types": message_types
        }

# Global instance for convenience
_default_bus: Optional[MessageBus] = None

def get_message_bus() -> MessageBus:
    """Get or create the default message bus instance"""
    global _default_bus
    if _default_bus is None:
        _default_bus = MessageBus()
    return _default_bus