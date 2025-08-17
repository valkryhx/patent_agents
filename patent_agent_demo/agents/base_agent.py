"""
Base Agent Class
Provides common functionality for all patent development agents
"""

import asyncio
import logging
import time
import uuid
import traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..message_bus import (
    MessageBusBroker, Message, MessageType, AgentStatus, message_bus_config
)
from ..context_manager import context_manager
from ..logging_utils import attach_agent_file_logger

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
    
    def __init__(self, name: str, capabilities: List[str], test_mode: bool = False):
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
        
        # 为每个智能体创建独立的日志记录器
        self.agent_logger = attach_agent_file_logger(name)
        self.test_mode = test_mode
        
        # 记录智能体初始化信息
        self.agent_logger.info(f"🚀 {self.name} 智能体初始化开始")
        self.agent_logger.info(f"   能力: {self.capabilities}")
        self.agent_logger.info(f"   测试模式: {test_mode}")
        self.agent_logger.info(f"   状态: {self.status.value}")
        
        if test_mode:
            self.agent_logger.info(f"🧪 {self.name} 以测试模式初始化")
        
    async def start(self):
        """Start the agent"""
        try:
            self.agent_logger.info(f"🔄 {self.name} 开始启动...")
            
            # Register with message bus
            await self.broker.register_agent(self.name, self.capabilities)
            self.agent_logger.info(f"✅ {self.name} 已注册到消息总线")
            
            # Start message processing loop and wait for it to initialize
            self.message_task = asyncio.create_task(self._message_processing_loop())
            
            # Give the message loop a moment to start
            await asyncio.sleep(0.1)
            
            self.status = AgentStatus.IDLE
            self.agent_logger.info(f"✅ {self.name} 启动成功，状态: {self.status.value}")
            self.agent_logger.info(f"   能力: {self.capabilities}")
            
        except Exception as e:
            self.agent_logger.error(f"❌ {self.name} 启动失败: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
            logger.error(f"Error starting agent {self.name}: {e}")
            raise
            
    async def stop(self):
        """Stop the agent"""
        try:
            self.agent_logger.info(f"🔄 {self.name} 开始停止...")
            
            # Update status to stop message processing loop
            self.status = AgentStatus.OFFLINE
            self.agent_logger.info(f"📊 {self.name} 状态更新为: {self.status.value}")
            
            # Cancel message processing task if it exists
            if hasattr(self, 'message_task') and self.message_task:
                self.message_task.cancel()
                try:
                    await self.message_task
                except asyncio.CancelledError:
                    self.agent_logger.info(f"✅ {self.name} 消息处理任务已取消")
            
            # Unregister from message bus
            await self.broker.unregister_agent(self.name)
            self.agent_logger.info(f"✅ {self.name} 已从消息总线注销")
            
            # 记录性能统计
            self.agent_logger.info(f"📊 {self.name} 性能统计:")
            self.agent_logger.info(f"   完成任务: {self.performance_metrics['tasks_completed']}")
            self.agent_logger.info(f"   失败任务: {self.performance_metrics['tasks_failed']}")
            self.agent_logger.info(f"   平均执行时间: {self.performance_metrics['average_execution_time']:.2f}秒")
            self.agent_logger.info(f"   总执行时间: {self.performance_metrics['total_execution_time']:.2f}秒")
            
            logger.info(f"Agent {self.name} stopped successfully")
            
        except Exception as e:
            self.agent_logger.error(f"❌ {self.name} 停止失败: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
            logger.error(f"Error stopping agent {self.name}: {e}")
            
    async def _message_processing_loop(self):
        """Main message processing loop"""
        try:
            self.agent_logger.info(f"🔄 {self.name} 消息处理循环开始")
            loop_count = 0
            while self.status != AgentStatus.OFFLINE:
                loop_count += 1
                
                # Get message from broker for this specific agent
                try:
                    message = await self.broker.get_message(self.name)
                    if message:
                        self.agent_logger.info(f"📨 {self.name} 收到消息: {message.type.value} 来自 {message.sender}")
                        self.agent_logger.info(f"   消息ID: {message.id}")
                        self.agent_logger.info(f"   内容: {message.content}")
                        await self._process_message(message)
                    else:
                        # Log occasionally to show the loop is running
                        if int(time.time()) % 30 == 0:  # Log every 30 seconds
                            self.agent_logger.debug(f"⏳ {self.name} 等待消息中... (循环次数: {loop_count})")
                except Exception as e:
                    self.agent_logger.error(f"❌ {self.name} 获取消息失败: {e}")
                    self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
                    message = None
                
                # Add heartbeat to show the loop is running (every minute)
                current_time = int(time.time())
                if current_time % 60 == 0 and not hasattr(self, '_last_heartbeat_time') or current_time - getattr(self, '_last_heartbeat_time', 0) >= 60:
                    self.agent_logger.info(f"💓 {self.name} 心跳 - 状态: {self.status.value} - 循环次数: {loop_count}")
                    self._last_heartbeat_time = current_time
                
                # Log activity every 1000 loops (much less frequent)
                if loop_count % 1000 == 0:
                    self.agent_logger.info(f"🔄 {self.name} 消息循环活跃 - 循环次数: {loop_count}")
                    
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.agent_logger.error(f"❌ {self.name} 消息处理循环错误: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
            logger.error(f"Error in message processing loop for {self.name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
    async def _process_message(self, message: Message):
        """Process an incoming message"""
        try:
            self.agent_logger.info(f"🔄 {self.name} 开始处理消息: {message.type.value}")
            self.agent_logger.info(f"   消息ID: {message.id}")
            self.agent_logger.info(f"   发送者: {message.sender}")
            self.agent_logger.info(f"   内容: {message.content}")
            
            message_type = message.type
            
            if message_type == MessageType.COORDINATION:
                self.agent_logger.info(f"🔄 {self.name} 路由到协调处理器")
                await self._handle_coordination_message(message)
            elif message_type == MessageType.STATUS:
                self.agent_logger.info(f"🔄 {self.name} 路由到状态处理器")
                try:
                    await self._handle_status_message(message)
                    self.agent_logger.info(f"✅ {self.name} 状态消息处理完成")
                except Exception as e:
                    self.agent_logger.error(f"❌ {self.name} 状态消息处理失败: {e}")
                    self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
                    raise
            elif message_type == MessageType.ERROR:
                self.agent_logger.info(f"🔄 {self.name} 路由到错误处理器")
                await self._handle_error_message(message)
            else:
                self.agent_logger.info(f"🔄 {self.name} 路由到特定处理器")
                await self._handle_specific_message(message)
                
        except Exception as e:
            self.agent_logger.error(f"❌ {self.name} 处理消息失败: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
            logger.error(f"🔄 Error processing message in {self.name}: {e}")
            import traceback
            logger.error(f"🔄 Traceback: {traceback.format_exc()}")
            
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
            self.agent_logger.info(f"🔧 {self.name} 处理协调消息")
            self.agent_logger.info(f"   消息内容: {message.content}")
            
            task_data = message.content.get("task", {})
            task_type = task_data.get("type")
            
            self.agent_logger.info(f"🔧 {self.name} 任务类型: {task_type}")
            self.agent_logger.info(f"   可用能力: {self.capabilities}")
            
            if task_type in self.capabilities:
                self.agent_logger.info(f"✅ {self.name} 开始执行任务: {task_type}")
                await self._execute_task(task_data)
                self.agent_logger.info(f"✅ {self.name} 任务执行完成: {task_type}")
            else:
                self.agent_logger.warning(f"⚠️ {self.name} 无法处理任务类型: {task_type}")
                self.agent_logger.warning(f"   可用能力: {self.capabilities}")
                
        except Exception as e:
            self.agent_logger.error(f"❌ {self.name} 处理协调消息失败: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
            logger.error(f"🔧 Error handling coordination message: {e}")
            import traceback
            logger.error(f"🔧 Traceback: {traceback.format_exc()}")
            
    async def _handle_status_message(self, message: Message):
        """Handle status update messages"""
        try:
            # Update local status if needed
            if message.content.get("agent_name") == self.name:
                new_status = message.content.get("status")
                if new_status:
                    self.status = AgentStatus(new_status)
            
            # Call subclass implementation if it exists
            self.agent_logger.info(f"🔍 {self.name} 状态消息处理 - 类名: {self.__class__.__name__}")
            self.agent_logger.info(f"🔍 {self.name} 状态消息处理 - 是否有_handle_status_message_override: {hasattr(self, '_handle_status_message_override')}")
            self.agent_logger.info(f"🔍 {self.name} 状态消息处理 - 类名不是BaseAgent: {self.__class__.__name__ != 'BaseAgent'}")
            
            if hasattr(self, '_handle_status_message_override') and self.__class__.__name__ != 'BaseAgent':
                self.agent_logger.info(f"🔍 {self.name} 调用子类状态消息处理器")
                self.agent_logger.info(f"🔍 {self.name} 准备调用 _handle_status_message_override")
                try:
                    self.agent_logger.info(f"🔍 {self.name} 开始调用 _handle_status_message_override")
                    await self._handle_status_message_override(message)
                    self.agent_logger.info(f"🔍 {self.name} 子类状态消息处理器调用完成")
                except Exception as e:
                    self.agent_logger.error(f"🔍 {self.name} 子类状态消息处理器调用失败: {e}")
                    import traceback
                    self.agent_logger.error(f"🔍 {self.name} 子类状态消息处理器调用失败堆栈: {traceback.format_exc()}")
                    raise
            else:
                self.agent_logger.info(f"🔍 {self.name} 使用基础状态消息处理器")
                    
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
            task_type = task_data.get("type", "unknown")
            
            self.agent_logger.info(f"🚀 {self.name} 开始执行任务")
            self.agent_logger.info(f"   任务ID: {task_id}")
            self.agent_logger.info(f"   任务类型: {task_type}")
            self.agent_logger.info(f"   任务数据: {task_data}")
            
            # Extract context information if available
            context_data = task_data.get("context", {})
            workflow_id = task_data.get("workflow_id")
            
            if context_data and workflow_id:
                self.agent_logger.info(f"📋 {self.name} 收到工作流 {workflow_id} 的上下文数据")
                # Store context for use during task execution
                self.current_context = context_data
                self.current_workflow_id = workflow_id
            else:
                self.agent_logger.info(f"📋 {self.name} 无上下文数据")
                self.current_context = {}
                self.current_workflow_id = None
            
            # Execute the task using the abstract method
            if self.test_mode:
                self.agent_logger.info(f"🧪 {self.name} 使用测试模式执行")
                # In test mode, use mock execution
                result = await self._execute_test_task(task_data)
            else:
                self.agent_logger.info(f"🔧 {self.name} 使用正常模式执行")
                # Normal execution
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
            
            # Log execution result
            if result.success:
                self.agent_logger.info(f"✅ {self.name} 任务执行成功")
                self.agent_logger.info(f"   执行时间: {execution_time:.2f}秒")
                self.agent_logger.info(f"   结果数据: {result.data}")
            else:
                self.agent_logger.warning(f"⚠️ {self.name} 任务执行失败")
                self.agent_logger.warning(f"   执行时间: {execution_time:.2f}秒")
                self.agent_logger.warning(f"   错误信息: {result.error_message}")
            
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
            self.agent_logger.info(f"📤 {self.name} 发送完成消息到协调器")
            
        except Exception as e:
            self.agent_logger.error(f"❌ {self.name} 任务执行异常: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
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
            self.agent_logger.info(f"📤 {self.name} 发送错误消息到协调器")
            
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a task - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute_task")
        
    async def _execute_test_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a test task with mock data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_test_task")
        
    def _update_performance_metrics(self, success: bool, execution_time: float):
        """Update performance metrics"""
        if success:
            self.performance_metrics["tasks_completed"] += 1
            self.agent_logger.info(f"📊 {self.name} 性能统计更新 - 完成任务: {self.performance_metrics['tasks_completed']}")
        else:
            self.performance_metrics["tasks_failed"] += 1
            self.agent_logger.warning(f"📊 {self.name} 性能统计更新 - 失败任务: {self.performance_metrics['tasks_failed']}")
            
        self.performance_metrics["total_execution_time"] += execution_time
        
        # 计算平均执行时间
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        if total_tasks > 0:
            self.performance_metrics["average_execution_time"] = self.performance_metrics["total_execution_time"] / total_tasks
            
        self.agent_logger.debug(f"📊 {self.name} 性能统计 - 平均执行时间: {self.performance_metrics['average_execution_time']:.2f}秒")
            
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        status_info = {
            "name": self.name,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "performance_metrics": self.performance_metrics,
            "task_history_length": len(self.task_history),
            "test_mode": self.test_mode,
            "current_workflow_id": getattr(self, 'current_workflow_id', None),
            "has_context": bool(getattr(self, 'current_context', {}))
        }
        
        self.agent_logger.debug(f"📊 {self.name} 状态查询: {status_info}")
        return status_info
        
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
            self.agent_logger.info(f"📤 {self.name} 发送消息到 {recipient}: {message_type.value}")
            
        except Exception as e:
            self.agent_logger.error(f"❌ {self.name} 发送消息失败: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
            logger.error(f"Error sending message from {self.name}: {e}")