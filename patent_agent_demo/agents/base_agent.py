"""
Base Agent Class
Provides common functionality for all patent development agents
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..message_bus import (
    MessageBusBroker, Message, MessageType, AgentStatus, message_bus_config
)

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Result of a task execution"""
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class BaseAgent:
    """Base class for all patent development agents"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.broker = message_bus_config.broker
        self.task_history: List[TaskResult] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        self.agent_logger = logging.getLogger(f"agent.{name}")
        
    async def start(self):
        """Start the agent"""
        try:
            # Register with message bus
            await self.broker.register_agent(self.name, self.capabilities)
            
            # Start message processing loop and wait for it to initialize
            self.message_task = asyncio.create_task(self._message_processing_loop())
            
            # Give the message loop a moment to start
            await asyncio.sleep(0.1)
            
            self.agent_logger.info(f"{self.name} initialized with capabilities: {self.capabilities}")
            
        except Exception as e:
            logger.error(f"Error starting agent {self.name}: {e}")
            raise
            
    async def stop(self):
        """Stop the agent"""
        try:
            # Update status to stop message processing loop
            self.status = AgentStatus.OFFLINE
            
            # Cancel message processing task if it exists
            if hasattr(self, 'message_task') and self.message_task:
                self.message_task.cancel()
                try:
                    await self.message_task
                except asyncio.CancelledError:
                    pass
            
            # Unregister from message bus
            await self.broker.unregister_agent(self.name)
            
            logger.info(f"Agent {self.name} stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping agent {self.name}: {e}")
            
    async def _message_processing_loop(self):
        """Main message processing loop"""
        try:
            logger.info(f"Message processing loop started for {self.name}")
            loop_count = 0
            while self.status != AgentStatus.OFFLINE:
                loop_count += 1
                
                # Get message from broker for this specific agent
                try:
                    message = await self.broker.get_message(self.name)
                except Exception as e:
                    logger.error(f"Error getting message for {self.name}: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    message = None
                
                if message:
                    logger.info(f"Agent {self.name} received message: {message.type.value} from {message.sender}")
                    # Process message
                    try:
                        await self._process_message(message)
                    except Exception as e:
                        logger.error(f"Error processing message in {self.name}: {e}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                else:
                    # Log occasionally to show the loop is running
                    if int(time.time()) % 10 == 0:  # Log every 10 seconds
                        logger.debug(f"Agent {self.name} waiting for messages...")
                    
                # Add heartbeat to show the loop is running
                if int(time.time()) % 5 == 0:  # Log every 5 seconds
                    logger.info(f"Agent {self.name} message loop heartbeat - status: {self.status.value} - loop count: {loop_count}")
                
                # Force log every 10 loops to ensure we see activity
                if loop_count % 10 == 0:
                    logger.info(f"Agent {self.name} message loop active - loop count: {loop_count}")
                    
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in message processing loop for {self.name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
    async def _process_message(self, message: Message):
        """Process an incoming message"""
        try:
            message_type = message.type
            
            if message_type == MessageType.COORDINATION:
                await self._handle_coordination_message(message)
            elif message_type == MessageType.STATUS:
                await self._handle_status_message(message)
            elif message_type == MessageType.ERROR:
                await self._handle_error_message(message)
            else:
                await self._handle_specific_message(message)
                
        except Exception as e:
            logger.error(f"Error processing message in {self.name}: {e}")
            
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
            logger.info(f"Agent {self.name} handling coordination message")
            task_data = message.content.get("task", {})
            task_type = task_data.get("type")
            
            logger.info(f"Agent {self.name} task type: {task_type}, capabilities: {self.capabilities}")
            
            if task_type in self.capabilities:
                logger.info(f"Agent {self.name} executing task: {task_type}")
                await self._execute_task(task_data)
                logger.info(f"Agent {self.name} task execution completed")
            else:
                logger.warning(f"Agent {self.name} cannot handle task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Error handling coordination message: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
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
            self.agent_logger.info(f"EXECUTE task_id={task_id} type={task_data.get('type')} meta={{'topic': task_data.get('topic')}}")
            
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
            
            # Send completion message with correct task_id format
            completion_message = Message(
                id=f"completion_{uuid.uuid4()}",
                type=MessageType.STATUS,
                sender=self.name,
                recipient="coordinator_agent",
                content={
                    "task_id": task_id,  # Use the original task_id from task_data
                    "status": "completed",
                    "result": result.data,
                    "execution_time": execution_time,
                    "success": result.success
                },
                timestamp=time.time(),
                priority=5
            )
            await self.broker.send_message(completion_message)
            self.agent_logger.info(f"COMPLETE task_id={task_id} success={result.success} time={execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error executing task in {self.name}: {e}")
            
            # Send error message with correct task_id
            error_message = Message(
                id=f"error_{uuid.uuid4()}",
                type=MessageType.ERROR,
                sender=self.name,
                recipient="coordinator_agent",  # Fix recipient name
                content={"error": str(e), "task_id": task_data.get("id")},
                timestamp=time.time(),
                priority=10
            )
            await self.broker.send_message(error_message)
            
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a task - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute_task")
        
    def _update_performance_metrics(self, success: bool, execution_time: float):
        """Update performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
        else:
            self.performance_metrics["tasks_failed"] += 1
            
        self.performance_metrics["total_execution_time"] += execution_time
        
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        if total_tasks > 0:
            self.performance_metrics["average_execution_time"] = (
                self.performance_metrics["total_execution_time"] / total_tasks
            )
            
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "performance_metrics": self.performance_metrics,
            "task_history_length": len(self.task_history)
        }
        
    async def send_message(self, recipient: str, message_type: MessageType, 
                          content: Dict[str, Any], priority: int = 5):
        """Send a message to another agent"""
        try:
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
            
        except Exception as e:
            logger.error(f"Error sending message from {self.name}: {e}")