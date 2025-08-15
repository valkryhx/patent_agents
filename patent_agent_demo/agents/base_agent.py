"""
Base Agent Class for Patent Agent System
Provides common functionality and interface for all agents
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import uuid

from ..fastmcp_config import (
    FastMCPBroker, Message, MessageType, AgentStatus, fastmcp_config
)

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Result of a task execution"""
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None

class BaseAgent(ABC):
    """Base class for all patent agents"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.broker = fastmcp_config.broker
        self.status = AgentStatus.IDLE
        self.current_task = None
        self.task_history: List[TaskResult] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        self.is_running = False
        
        logger.info(f"Initialized agent: {name} with capabilities: {capabilities}")
        
    async def start(self):
        """Start the agent"""
        try:
            await self.broker.register_agent(self.name, self.capabilities)
            self.is_running = True
            logger.info(f"Agent {self.name} started successfully")
            
            # Start the main agent loop
            asyncio.create_task(self._agent_loop())
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.name}: {e}")
            raise
            
    async def stop(self):
        """Stop the agent"""
        try:
            self.is_running = False
            await self.broker.unregister_agent(self.name)
            logger.info(f"Agent {self.name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping agent {self.name}: {e}")
            
    async def _agent_loop(self):
        """Main agent loop for processing messages and tasks"""
        while self.is_running:
            try:
                # Check for incoming messages
                message = await self.broker.receive_message(self.name)
                
                if message:
                    await self._process_message(message)
                    
                # Update status
                await self.broker.update_agent_status(
                    self.name, self.status, self.current_task
                )
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in agent loop for {self.name}: {e}")
                await asyncio.sleep(1.0)  # Longer delay on error
                
    async def _process_message(self, message: Message):
        """Process an incoming message"""
        try:
            logger.info(f"Agent {self.name} processing message: {message.type.value}")
            
            # Update status to busy
            self.status = AgentStatus.BUSY
            await self.broker.update_agent_status(self.name, self.status)
            
            # Process based on message type
            if message.type == MessageType.COORDINATION:
                await self._handle_coordination_message(message)
            elif message.type == MessageType.STATUS:
                await self._handle_status_message(message)
            else:
                # Delegate to specific message handler
                await self._handle_specific_message(message)
                
            # Update status back to idle
            self.status = AgentStatus.IDLE
            await self.broker.update_agent_status(self.name, self.status)
            
        except Exception as e:
            logger.error(f"Error processing message in {self.name}: {e}")
            self.status = AgentStatus.ERROR
            await self.broker.update_agent_status(self.name, self.status)
            
            # Send error response
            error_message = Message(
                id=f"error_{uuid.uuid4()}",
                type=MessageType.ERROR,
                sender=self.name,
                recipient=message.sender,
                content={"error": str(e), "original_message_id": message.id},
                timestamp=time.time(),
                priority=10
            )
            await self.broker.send_message(error_message)
            
    async def _handle_coordination_message(self, message: Message):
        """Handle coordination messages"""
        try:
            task_data = message.content.get("task", {})
            task_type = task_data.get("type")
            
            if task_type in self.capabilities:
                await self._execute_task(task_data)
            else:
                logger.warning(f"Agent {self.name} cannot handle task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Error handling coordination message: {e}")
            
    async def _handle_status_message(self, message: Message):
        """Handle status update messages"""
        try:
            # Update local status if needed
            if message.content.get("agent_name") == self.name:
                new_status = message.content.get("status")
                if new_status:
                    self.status = AgentStatus(new_status)
                    
        except Exception as e:
            logger.error(f"Error handling status message: {e}")
            
    async def _handle_specific_message(self, message: Message):
        """Handle specific message types - to be implemented by subclasses"""
        try:
            # This method should be overridden by specific agents
            logger.info(f"Agent {self.name} received specific message: {message.type.value}")
            
        except Exception as e:
            logger.error(f"Error handling specific message: {e}")
            
    async def _execute_task(self, task_data: Dict[str, Any]):
        """Execute a specific task"""
        try:
            start_time = time.time()
            task_id = task_data.get("id", str(uuid.uuid4()))
            
            logger.info(f"Agent {self.name} executing task: {task_id}")
            
            # Execute the task using the abstract method
            result = await self.execute_task(task_data)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(result.success, execution_time)
            
            # Store task result
            task_result = TaskResult(
                success=result.success,
                data=result.data,
                error_message=result.error_message,
                execution_time=execution_time,
                metadata=result.metadata
            )
            self.task_history.append(task_result)
            
            # Send completion message
            completion_message = Message(
                id=f"completion_{uuid.uuid4()}",
                type=MessageType.STATUS,
                sender=self.name,
                recipient="coordinator",
                content={
                    "task_id": task_id,
                    "status": "completed",
                    "result": result.data,
                    "execution_time": execution_time,
                    "success": result.success
                },
                timestamp=time.time(),
                priority=5
            )
            await self.broker.send_message(completion_message)
            
            logger.info(f"Agent {self.name} completed task {task_id} in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error executing task in {self.name}: {e}")
            
            # Send error message
            error_message = Message(
                id=f"error_{uuid.uuid4()}",
                type=MessageType.ERROR,
                sender=self.name,
                recipient="coordinator",
                content={"error": str(e), "task_id": task_data.get("id")},
                timestamp=time.time(),
                priority=10
            )
            await self.broker.send_message(error_message)
            
    def _update_performance_metrics(self, success: bool, execution_time: float):
        """Update agent performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
            
        self.performance_metrics["total_execution_time"] += execution_time
        self.performance_metrics["average_execution_time"] = (
            self.performance_metrics["total_execution_time"] / 
            (self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"])
        )
        
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a specific task - must be implemented by subclasses"""
        pass
        
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task,
            "capabilities": self.capabilities,
            "performance_metrics": self.performance_metrics,
            "task_history_count": len(self.task_history)
        }
        
    async def send_message(self, recipient: str, message_type: MessageType, 
                          content: Dict[str, Any], priority: int = 1):
        """Send a message to another agent"""
        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            sender=self.name,
            recipient=recipient,
            content=content,
            timestamp=time.time(),
            priority=priority
        )
        await self.broker.send_message(message)
        
    async def broadcast_message(self, message_type: MessageType, 
                              content: Dict[str, Any], priority: int = 1):
        """Broadcast a message to all agents"""
        await self.broker.broadcast_message(message_type, content, self.name, priority)