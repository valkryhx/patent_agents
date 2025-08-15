"""
Patent Agent System - Main System Class
Manages all agents and provides the main interface for patent development
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import uuid

from .fastmcp_config import fastmcp_config, MessageType
from .agents import (
    PlannerAgent, SearcherAgent, DiscusserAgent, 
    WriterAgent, ReviewerAgent, RewriterAgent, CoordinatorAgent
)

logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """System status information"""
    total_agents: int
    active_agents: int
    active_workflows: int
    system_health: str
    uptime: float
    performance_metrics: Dict[str, Any]

class PatentAgentSystem:
    """Main system class for the Patent Agent System"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.coordinator: Optional[CoordinatorAgent] = None
        self.system_start_time = time.time()
        self.is_running = False
        
        # Initialize FastMCP
        self.fastmcp_config = fastmcp_config
        
        logger.info("Patent Agent System initialized")
        
    async def start(self):
        """Start the entire patent agent system"""
        try:
            logger.info("Starting Patent Agent System...")
            
            # Initialize FastMCP
            await self.fastmcp_config.initialize()
            
            # Create and start all agents
            await self._create_agents()
            await self._start_agents()
            
            self.is_running = True
            logger.info("Patent Agent System started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Patent Agent System: {e}")
            raise
            
    async def stop(self):
        """Stop the entire patent agent system"""
        try:
            logger.info("Stopping Patent Agent System...")
            
            # Stop all agents
            for agent in self.agents.values():
                await agent.stop()
                
            # Stop FastMCP
            await self.fastmcp_config.shutdown()
            
            self.is_running = False
            logger.info("Patent Agent System stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Patent Agent System: {e}")
            
    async def _create_agents(self):
        """Create all agents"""
        try:
            # Create specialized agents
            self.agents["planner_agent"] = PlannerAgent()
            self.agents["searcher_agent"] = SearcherAgent()
            self.agents["discusser_agent"] = DiscusserAgent()
            self.agents["writer_agent"] = WriterAgent()
            self.agents["reviewer_agent"] = ReviewerAgent()
            self.agents["rewriter_agent"] = RewriterAgent()
            
            # Create coordinator agent
            self.coordinator = CoordinatorAgent()
            self.agents["coordinator_agent"] = self.coordinator
            
            logger.info(f"Created {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Error creating agents: {e}")
            raise
            
    async def _start_agents(self):
        """Start all agents"""
        try:
            # Start all agents concurrently
            start_tasks = [agent.start() for agent in self.agents.values()]
            await asyncio.gather(*start_tasks)
            
            logger.info("All agents started successfully")
            
        except Exception as e:
            logger.error(f"Error starting agents: {e}")
            raise
            
    async def develop_patent(self, topic: str, description: str, 
                           workflow_type: str = "standard") -> Dict[str, Any]:
        """Start a patent development workflow"""
        try:
            if not self.is_running:
                raise RuntimeError("Patent Agent System is not running")
                
            if not topic or not description:
                raise ValueError("Topic and description are required")
                
            logger.info(f"Starting patent development for: {topic}")
            
            # Send task to coordinator to start workflow
            result = await self.coordinator.execute_task({
                "type": "start_patent_workflow",
                "topic": topic,
                "description": description,
                "workflow_type": workflow_type
            })
            
            if not result.success:
                raise RuntimeError(f"Failed to start workflow: {result.error_message}")
                
            workflow_data = result.data
            workflow_id = workflow_data.get("workflow_id")
            
            # Wait for workflow completion
            final_result = await self._wait_for_workflow_completion(workflow_id)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error developing patent: {e}")
            raise
            
    async def _wait_for_workflow_completion(self, workflow_id: str) -> Dict[str, Any]:
        """Wait for a workflow to complete and return results"""
        try:
            max_wait_time = 300  # 5 minutes max wait
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                # Check workflow status
                status_result = await self.coordinator.execute_task({
                    "type": "monitor_workflow",
                    "workflow_id": workflow_id
                })
                
                if status_result.success:
                    workflow_data = status_result.data.get("workflow")
                    if workflow_data and workflow_data.get("overall_status") == "completed":
                        # Workflow completed, get final results
                        return await self._get_workflow_results(workflow_id)
                        
                # Wait before checking again
                await asyncio.sleep(2)
                
            # Timeout reached
            raise TimeoutError(f"Workflow {workflow_id} did not complete within {max_wait_time} seconds")
            
        except Exception as e:
            logger.error(f"Error waiting for workflow completion: {e}")
            raise
            
    async def _get_workflow_results(self, workflow_id: str) -> Dict[str, Any]:
        """Get final results from a completed workflow"""
        try:
            # This would typically involve querying the coordinator for final results
            # For now, we'll return a mock result structure
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "patent_summary": {
                    "title": "Generated Patent Title",
                    "status": "Ready for Filing",
                    "confidence_score": 0.92
                },
                "completion_time": time.time(),
                "message": "Patent development workflow completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow results: {e}")
            raise
            
    async def get_system_status(self) -> SystemStatus:
        """Get overall system status"""
        try:
            # Get FastMCP system status
            fastmcp_status = await self.fastmcp_config.broker.get_system_status()
            
            # Calculate system health
            total_agents = len(self.agents)
            active_agents = fastmcp_status.get("active_agents", 0)
            active_workflows = len(self.coordinator.active_workflows) if self.coordinator else 0
            
            # Determine system health
            if active_agents == total_agents and active_workflows > 0:
                system_health = "healthy"
            elif active_agents == total_agents:
                system_health = "idle"
            elif active_agents > total_agents * 0.8:
                system_health = "degraded"
            else:
                system_health = "unhealthy"
                
            # Calculate uptime
            uptime = time.time() - self.system_start_time
            
            # Compile performance metrics
            performance_metrics = {
                "message_queue_size": fastmcp_status.get("message_queue_size", 0),
                "agent_performance": {},
                "workflow_success_rate": 0.95  # Mock value
            }
            
            # Get individual agent performance
            for agent_name, agent in self.agents.items():
                try:
                    agent_status = await agent.get_status()
                    performance_metrics["agent_performance"][agent_name] = {
                        "status": agent_status.get("status"),
                        "tasks_completed": agent_status.get("performance_metrics", {}).get("tasks_completed", 0),
                        "average_execution_time": agent_status.get("performance_metrics", {}).get("average_execution_time", 0)
                    }
                except Exception as e:
                    logger.warning(f"Could not get status for agent {agent_name}: {e}")
                    
            return SystemStatus(
                total_agents=total_agents,
                active_agents=active_agents,
                active_workflows=active_workflows,
                system_health=system_health,
                uptime=uptime,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise
            
    async def monitor_workflows(self) -> List[Dict[str, Any]]:
        """Monitor all active workflows"""
        try:
            if not self.coordinator:
                return []
                
            result = await self.coordinator.execute_task({
                "type": "monitor_workflow"
            })
            
            if result.success:
                return result.data.get("active_workflows", [])
            else:
                logger.error(f"Failed to monitor workflows: {result.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Error monitoring workflows: {e}")
            return []
            
    async def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        try:
            agent = self.agents.get(agent_name)
            if agent:
                return await agent.get_status()
            else:
                logger.warning(f"Agent {agent_name} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return None
            
    async def send_agent_message(self, agent_name: str, message_type: MessageType, 
                               content: Dict[str, Any], priority: int = 1):
        """Send a message to a specific agent"""
        try:
            agent = self.agents.get(agent_name)
            if agent:
                await agent.send_message(agent_name, message_type, content, priority)
            else:
                logger.warning(f"Agent {agent_name} not found")
                
        except Exception as e:
            logger.error(f"Error sending message to agent: {e}")
            
    async def broadcast_system_message(self, message_type: MessageType, 
                                    content: Dict[str, Any], priority: int = 1):
        """Broadcast a message to all agents"""
        try:
            await self.fastmcp_config.broker.broadcast_message(
                message_type, content, "system", priority
            )
        except Exception as e:
            logger.error(f"Error broadcasting system message: {e}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check of the system"""
        try:
            health_status = {
                "system": "healthy",
                "agents": {},
                "fastmcp": "healthy",
                "workflows": "healthy",
                "timestamp": time.time()
            }
            
            # Check FastMCP health
            try:
                fastmcp_status = await self.fastmcp_config.broker.get_system_status()
                if fastmcp_status.get("total_agents", 0) == 0:
                    health_status["fastmcp"] = "unhealthy"
            except Exception as e:
                health_status["fastmcp"] = "error"
                health_status["fastmcp_error"] = str(e)
                
            # Check individual agent health
            for agent_name, agent in self.agents.items():
                try:
                    agent_status = await agent.get_status()
                    health_status["agents"][agent_name] = {
                        "status": agent_status.get("status"),
                        "health": "healthy" if agent_status.get("status") != "error" else "unhealthy"
                    }
                except Exception as e:
                    health_status["agents"][agent_name] = {
                        "status": "unknown",
                        "health": "error",
                        "error": str(e)
                    }
                    
            # Check workflow health
            try:
                workflows = await self.monitor_workflows()
                if any(wf.get("status") == "error" for wf in workflows):
                    health_status["workflows"] = "degraded"
            except Exception as e:
                health_status["workflows"] = "error"
                health_status["workflow_error"] = str(e)
                
            # Determine overall system health
            if any(status == "error" for status in health_status.values() if isinstance(status, str)):
                health_status["system"] = "unhealthy"
            elif any(status == "unhealthy" for status in health_status.values() if isinstance(status, str)):
                health_status["system"] = "degraded"
                
            return health_status
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            return {
                "system": "error",
                "error": str(e),
                "timestamp": time.time()
            }
            
    async def restart_agent(self, agent_name: str) -> bool:
        """Restart a specific agent"""
        try:
            agent = self.agents.get(agent_name)
            if not agent:
                logger.warning(f"Agent {agent_name} not found")
                return False
                
            logger.info(f"Restarting agent {agent_name}")
            
            # Stop agent
            await agent.stop()
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Start agent
            await agent.start()
            
            logger.info(f"Agent {agent_name} restarted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restarting agent {agent_name}: {e}")
            return False
            
    async def emergency_shutdown(self):
        """Emergency shutdown of the system"""
        try:
            logger.critical("EMERGENCY SHUTDOWN INITIATED")
            
            # Stop all agents immediately
            stop_tasks = [agent.stop() for agent in self.agents.values()]
            await asyncio.gather(*stop_tasks, return_exceptions=True)
            
            # Stop FastMCP
            await self.fastmcp_config.shutdown()
            
            self.is_running = False
            logger.critical("Emergency shutdown completed")
            
        except Exception as e:
            logger.critical(f"Error during emergency shutdown: {e}")
            
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.is_running:
            asyncio.create_task(self.stop())