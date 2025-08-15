"""
Message Bus Configuration for Patent Agent System
Provides message passing and coordination infrastructure
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import time
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Message types for inter-agent communication"""
    COORDINATION = "coordination"
    STATUS = "status"
    ERROR = "error"
    DATA = "data"
    REQUEST = "request"
    RESPONSE = "response"

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    WORKING = "working"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class AgentInfo:
    """Information about an agent"""
    name: str
    status: AgentStatus
    capabilities: List[str]
    current_task: Optional[str] = None
    last_activity: float = 0.0

@dataclass
class Message:
    """Message structure for inter-agent communication"""
    id: str
    type: MessageType
    sender: str
    recipient: str
    content: Dict[str, Any]
    timestamp: float
    priority: int = 5

class MessageBusBroker:
    """Message broker for Message Bus communication"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}  # 每个代理有自己的消息队列
        self.message_handlers: Dict[str, callable] = {}
        
    async def register_agent(self, agent_name: str, capabilities: List[str]):
        """Register an agent with the broker"""
        self.agents[agent_name] = AgentInfo(
            name=agent_name,
            status=AgentStatus.IDLE,
            capabilities=capabilities,
            last_activity=time.time()
        )
        # 为每个代理创建独立的消息队列
        self.message_queues[agent_name] = asyncio.Queue()
        logger.info(f"Agent {agent_name} registered with capabilities: {capabilities}")
        
    async def unregister_agent(self, agent_name: str):
        """Unregister an agent from the broker"""
        if agent_name in self.agents:
            del self.agents[agent_name]
        if agent_name in self.message_queues:
            del self.message_queues[agent_name]
        logger.info(f"Agent {agent_name} unregistered")
            
    async def send_message(self, message: Message):
        """Send a message to the specific agent's queue"""
        recipient = message.recipient
        logger.info(f"Attempting to send message to {recipient}")
        logger.info(f"Available recipients: {list(self.message_queues.keys())}")
        logger.info(f"MessageBusBroker instance ID: {id(self)}")
        
        if recipient in self.message_queues:
            queue = self.message_queues[recipient]
            logger.info(f"Queue instance ID for {recipient}: {id(queue)}")
            await queue.put(message)
            logger.info(f"Message sent: {message.type.value} from {message.sender} to {message.recipient}")
            logger.info(f"Queue size for {recipient}: {queue.qsize()}")
            logger.debug(f"Message content: {message.content}")
        else:
            logger.warning(f"Recipient {recipient} not found, message dropped")
            logger.warning(f"Available recipients: {list(self.message_queues.keys())}")
            
    async def broadcast_message(self, message: Message):
        """Broadcast a message to all agents"""
        for agent_name in self.agents.keys():
            broadcast_msg = Message(
                id=f"broadcast_{uuid.uuid4()}",
                type=message.type,
                sender=message.sender,
                recipient=agent_name,
                content=message.content,
                timestamp=time.time(),
                priority=message.priority
            )
            await self.send_message(broadcast_msg)
            
    async def get_message(self, agent_name: str) -> Optional[Message]:
        """Get a message from a specific agent's queue"""
        if agent_name not in self.message_queues:
            logger.warning(f"Agent {agent_name} not found in message queues")
            return None
        
        queue = self.message_queues[agent_name]
        queue_size = queue.qsize()
        logger.info(f"Agent {agent_name} queue size: {queue_size}")  # Changed from debug to info
        logger.info(f"MessageBusBroker instance ID: {id(self)}")
        logger.info(f"Queue instance ID for {agent_name}: {id(queue)}")
        
        if queue_size == 0:
            logger.info(f"Agent {agent_name} queue is empty")
            return None
            
        try:
            message = await asyncio.wait_for(queue.get(), timeout=1.0)
            if message:
                logger.info(f"Retrieved message for {agent_name}: {message.type.value} from {message.sender}")
                logger.debug(f"Message content: {message.content}")
            return message
        except asyncio.TimeoutError:
            logger.debug(f"Timeout getting message for {agent_name}")
            return None
        except Exception as e:
            logger.error(f"Error getting message for {agent_name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
            
    async def send_message_direct(self, sender: str, recipient: str, 
                                content: Dict[str, Any], priority: int = 5):
        """Send a message directly"""
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.COORDINATION,
            sender=sender,
            recipient=recipient,
            content=content,
            timestamp=asyncio.get_event_loop().time(),
            priority=priority
        )
        await self.send_message(message)
        
    async def get_agent_status(self, agent_name: str) -> Optional[AgentInfo]:
        """Get the status of a specific agent"""
        return self.agents.get(agent_name)
        
    async def update_agent_status(self, agent_name: str, status: AgentStatus, 
                                current_task: Optional[str] = None):
        """Update agent status"""
        if agent_name in self.agents:
            self.agents[agent_name].status = status
            self.agents[agent_name].current_task = current_task
            # Only log non-idle status updates to reduce log noise
            if status != AgentStatus.IDLE:
                logger.info(f"Agent {agent_name} status updated: {status.value}")
            
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status != AgentStatus.IDLE]),
            "message_queue_size": self.message_queue.qsize(),
            "agents": {name: asdict(info) for name, info in self.agents.items()}
        }

class MessageHandler:
    """Handles message processing and routing"""
    
    def __init__(self, broker: MessageBusBroker):
        self.broker = broker
        self.message_handlers: Dict[MessageType, callable] = {}
        
    def register_handler(self, message_type: MessageType, handler: callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
        
    async def process_message(self, message: Message):
        """Process an incoming message"""
        try:
            if message.type in self.message_handlers:
                await self.message_handlers[message.type](message)
            else:
                logger.warning(f"No handler registered for message type: {message.type.value}")
                
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
            
            # Send error message back to sender
            error_message = Message(
                id=f"error_{message.id}",
                type=MessageType.ERROR,
                sender="system",
                recipient=message.sender,
                content={"error": str(e), "original_message_id": message.id},
                timestamp=asyncio.get_event_loop().time(),
                priority=10
            )
            await self.broker.send_message(error_message)

class MessageBusConfig:
    """Main configuration class for Message Bus"""
    
    def __init__(self):
        self.broker = MessageBusBroker()
        self.message_handler = MessageHandler(self.broker)
        self.agent_coordinator = None
        
    async def initialize(self):
        """Initialize the Message Bus system"""
        logger.info("Initializing Message Bus system...")
        
        # Register default message handlers
        self.message_handler.register_handler(MessageType.STATUS, self._handle_status_message)
        self.message_handler.register_handler(MessageType.ERROR, self._handle_error_message)
        
        logger.info("Message Bus system initialized successfully")
        
    async def _handle_status_message(self, message: Message):
        """Handle status update messages"""
        if message.content.get("agent_name"):
            await self.broker.update_agent_status(
                message.content["agent_name"],
                AgentStatus(message.content.get("status", "idle")),
                message.content.get("current_task")
            )
            
    async def _handle_error_message(self, message: Message):
        """Handle error messages"""
        logger.error(f"Error from {message.sender}: {message.content.get('error', 'Unknown error')}")
        
    async def shutdown(self):
        """Shutdown the Message Bus system"""
        logger.info("Shutting down Message Bus system...")
        # Cleanup resources
        pass

# Global Message Bus configuration instance
message_bus_config = MessageBusConfig()