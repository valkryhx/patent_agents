"""
FastMCP Configuration for Patent Agent System
Handles message passing, agent coordination, and system communication
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages in the system"""
    PLANNING = "planning"
    SEARCH = "search"
    DISCUSSION = "discussion"
    WRITING = "writing"
    REVIEW = "review"
    REWRITE = "rewrite"
    COORDINATION = "coordination"
    STATUS = "status"
    ERROR = "error"

class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class Message:
    """Message structure for agent communication"""
    id: str
    type: MessageType
    sender: str
    recipient: str
    content: Dict[str, Any]
    timestamp: float
    priority: int = 1
    correlation_id: Optional[str] = None

@dataclass
class AgentInfo:
    """Information about an agent"""
    name: str
    status: AgentStatus
    capabilities: List[str]
    current_task: Optional[str] = None
    performance_metrics: Dict[str, float] = None

class FastMCPBroker:
    """Message broker for FastMCP communication"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscribers: Dict[str, List[str]] = {}
        self.message_history: List[Message] = []
        self.max_history = 1000
        
    async def register_agent(self, agent_name: str, capabilities: List[str]):
        """Register a new agent"""
        self.agents[agent_name] = AgentInfo(
            name=agent_name,
            status=AgentStatus.IDLE,
            capabilities=capabilities,
            performance_metrics={}
        )
        logger.info(f"Agent {agent_name} registered with capabilities: {capabilities}")
        
    async def unregister_agent(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Agent {agent_name} unregistered")
            
    async def send_message(self, message: Message):
        """Send a message to the broker"""
        await self.message_queue.put(message)
        self.message_history.append(message)
        
        # Maintain message history size
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
            
        logger.info(f"Message sent: {message.type.value} from {message.sender} to {message.recipient}")
        
    async def receive_message(self, agent_name: str) -> Optional[Message]:
        """Receive a message for a specific agent"""
        try:
            # Check if there are messages for this agent
            messages = [msg for msg in self.message_history 
                       if msg.recipient == agent_name or msg.recipient == "broadcast"]
            
            if messages:
                # Return the highest priority message
                messages.sort(key=lambda x: x.priority, reverse=True)
                return messages.pop(0)
                
        except Exception as e:
            logger.error(f"Error receiving message for {agent_name}: {e}")
            
        return None
        
    async def broadcast_message(self, message_type: MessageType, content: Dict[str, Any], 
                              sender: str, priority: int = 1):
        """Broadcast a message to all agents"""
        message = Message(
            id=f"broadcast_{asyncio.get_event_loop().time()}",
            type=message_type,
            sender=sender,
            recipient="broadcast",
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
    
    def __init__(self, broker: FastMCPBroker):
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

class FastMCPConfig:
    """Main configuration class for FastMCP"""
    
    def __init__(self):
        self.broker = FastMCPBroker()
        self.message_handler = MessageHandler(self.broker)
        self.agent_coordinator = None
        
    async def initialize(self):
        """Initialize the FastMCP system"""
        logger.info("Initializing FastMCP system...")
        
        # Register default message handlers
        self.message_handler.register_handler(MessageType.STATUS, self._handle_status_message)
        self.message_handler.register_handler(MessageType.ERROR, self._handle_error_message)
        
        logger.info("FastMCP system initialized successfully")
        
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
        """Shutdown the FastMCP system"""
        logger.info("Shutting down FastMCP system...")
        # Cleanup resources
        pass

# Global FastMCP configuration instance
fastmcp_config = FastMCPConfig()