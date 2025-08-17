"""
Patent Agent System
Main system for coordinating patent development agents
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time

from .agents.planner_agent import PlannerAgent
from .agents.searcher_agent import SearcherAgent
from .agents.discusser_agent import DiscusserAgent
from .agents.writer_agent import WriterAgent
from .agents.reviewer_agent import ReviewerAgent
from .agents.rewriter_agent import RewriterAgent
from .agents.coordinator_agent import CoordinatorAgent
from .message_bus import message_bus_config, MessageType

logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """System status information"""
    total_agents: int
    active_agents: int
    message_queue_size: int
    system_health: str
    uptime: float
    performance_metrics: Dict[str, Any]

class PatentAgentSystem:
    """Main system for coordinating patent development agents"""
    
    def __init__(self, test_mode: bool = False):
        self.agents: Dict[str, Any] = {}
        self.coordinator: Optional[CoordinatorAgent] = None
        self.system_start_time = time.time()
        self.test_mode = test_mode
        
        # Initialize Message Bus
        self.message_bus_config = message_bus_config
        
    async def start(self):
        """Start the patent agent system"""
        try:
            logger.info("Starting Patent Agent System...")
            
            # Initialize Message Bus
            await self.message_bus_config.initialize()
            
            # Create and start agents
            self.agents = {
                "planner_agent": PlannerAgent(test_mode=self.test_mode),
                "searcher_agent": SearcherAgent(test_mode=self.test_mode),
                "discusser_agent": DiscusserAgent(test_mode=self.test_mode),
                "writer_agent": WriterAgent(test_mode=self.test_mode),
                "reviewer_agent": ReviewerAgent(test_mode=self.test_mode),
                "rewriter_agent": RewriterAgent(test_mode=self.test_mode),
                "coordinator_agent": CoordinatorAgent(test_mode=self.test_mode)
            }
            
            # Start all agents
            for agent_name, agent in self.agents.items():
                await agent.start()
                logger.info(f"Agent {agent_name} started successfully")
                
            # Set coordinator reference
            self.coordinator = self.agents["coordinator_agent"]
            
            # Wait for all agents to fully initialize their message processing loops
            logger.info("Waiting for all agents to initialize message processing loops...")
            await asyncio.sleep(2)  # Give agents time to start their message loops
            
            logger.info("All agents started successfully")
            logger.info("Patent Agent System started successfully")
            
        except Exception as e:
            logger.error(f"Error starting Patent Agent System: {e}")
            raise
            
    async def stop(self):
        """Stop the patent agent system"""
        try:
            logger.info("Stopping Patent Agent System...")
            
            # Stop all agents
            for agent_name, agent in self.agents.items():
                try:
                    await agent.stop()
                    logger.info(f"Agent {agent_name} stopped successfully")
                except Exception as e:
                    logger.error(f"Error stopping agent {agent_name}: {e}")
                    
            # Stop Message Bus
            await self.message_bus_config.shutdown()
            
            logger.info("Patent Agent System stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Patent Agent System: {e}")
            raise
            
    async def execute_workflow(self, topic: str, description: str, 
                             workflow_type: str = "standard") -> str:
        """Execute a patent development workflow"""
        try:
            if not self.coordinator:
                raise RuntimeError("Coordinator agent not available")
                
            # Start workflow via coordinator
            result = await self.coordinator.execute_task({
                "type": "start_patent_workflow",
                "topic": topic,
                "description": description,
                "workflow_type": workflow_type
            })
            
            if not result.success:
                raise RuntimeError(f"Failed to start workflow: {result.error_message}")
                
            workflow_id = result.data.get("workflow_id")
            logger.info(f"Started workflow: {workflow_id}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise
            
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow"""
        try:
            if not self.coordinator:
                raise RuntimeError("Coordinator agent not available")
                
            result = await self.coordinator.execute_task({
                "type": "monitor_workflow",
                "workflow_id": workflow_id
            })
            
            if not result.success:
                raise RuntimeError(f"Failed to get workflow status: {result.error_message}")
                
            return result.data
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def get_system_status(self) -> SystemStatus:
        """Get overall system status"""
        try:
            # Get Message Bus system status
            message_bus_status = await self.message_bus_config.broker.get_system_status()
            
            # Calculate system health
            total_agents = message_bus_status.get("total_agents", 0)
            active_agents = message_bus_status.get("active_agents", 0)
            
            if total_agents == 0:
                system_health = "unhealthy"
            elif active_agents == 0:
                system_health = "idle"
            else:
                system_health = "healthy"
                
            # Calculate uptime
            uptime = time.time() - self.system_start_time
            
            # Get performance metrics
            performance_metrics = {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "message_queue_size": message_bus_status.get("message_queue_size", 0),
                "agent_statuses": message_bus_status.get("agents", {})
            }
            
            return SystemStatus(
                total_agents=total_agents,
                active_agents=active_agents,
                message_queue_size=message_bus_status.get("message_queue_size", 0),
                system_health=system_health,
                uptime=uptime,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return SystemStatus(
                total_agents=0,
                active_agents=0,
                message_queue_size=0,
                system_health="error",
                uptime=time.time() - self.system_start_time,
                performance_metrics={"error": str(e)}
            )
            
    async def broadcast_message(self, message_type: MessageType, 
                              content: Dict[str, Any], sender: str = "system"):
        """Broadcast a message to all agents"""
        try:
            await self.message_bus_config.broker.broadcast_message(
                message_type=message_type,
                content=content,
                sender=sender
            )
            logger.info(f"Broadcast message sent: {message_type.value}")
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check"""
        try:
            health_status = {
                "system": "healthy",
                "message_bus": "healthy",
                "agents": {},
                "timestamp": time.time()
            }
            
            # Check Message Bus health
            try:
                message_bus_status = await self.message_bus_config.broker.get_system_status()
                if message_bus_status.get("total_agents", 0) == 0:
                    health_status["message_bus"] = "unhealthy"
            except Exception as e:
                health_status["message_bus"] = "error"
                health_status["message_bus_error"] = str(e)
                
            # Check individual agents
            for agent_name, agent in self.agents.items():
                try:
                    agent_status = await agent.get_status()
                    health_status["agents"][agent_name] = agent_status
                except Exception as e:
                    health_status["agents"][agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    
            # Overall system health
            if health_status["message_bus"] != "healthy":
                health_status["system"] = "unhealthy"
                
            return health_status
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {
                "system": "error",
                "error": str(e),
                "timestamp": time.time()
            }
            
    async def shutdown(self):
        """Shutdown the system"""
        try:
            await self.stop()
            logger.info("Patent Agent System shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise