"""
Patent Agent System Test Mode
Test mode version of the patent agent system
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, List

from .agents.planner_agent_test import PlannerAgentTestMode
from .agents.writer_agent_test import WriterAgentTestMode
from .agents.searcher_agent_test import SearcherAgentTestMode
from .agents.reviewer_agent_test import ReviewerAgentTestMode
from .agents.rewriter_agent_test import RewriterAgentTestMode
from .agents.discusser_agent_test import DiscusserAgentTestMode
from .agents.coordinator_agent_test import CoordinatorAgentTestMode
from .message_bus import message_bus_config
from .context_manager import context_manager

logger = logging.getLogger(__name__)

class PatentAgentSystemTestMode:
    """Test mode version of the patent agent system"""
    
    def __init__(self):
        self.agents = {}
        self.workflow_id = None
        self.logger = logging.getLogger("test_system")
        
    async def start(self):
        """Start the test mode system"""
        try:
            self.logger.info("Starting Patent Agent System in TEST MODE")
            
            # Initialize message bus
            await message_bus_config.initialize()
            self.logger.info("Message bus initialized")
            
            # Initialize context manager
            await context_manager.initialize()
            self.logger.info("Context manager initialized")
            
            # Create and start all test mode agents
            self.agents = {
                "planner_agent": PlannerAgentTestMode(),
                "writer_agent": WriterAgentTestMode(),
                "searcher_agent": SearcherAgentTestMode(),
                "reviewer_agent": ReviewerAgentTestMode(),
                "rewriter_agent": RewriterAgentTestMode(),
                "discusser_agent": DiscusserAgentTestMode(),
                "coordinator_agent": CoordinatorAgentTestMode()
            }
            
            # Start all agents
            for name, agent in self.agents.items():
                self.logger.info(f"Starting {name} in test mode...")
                await agent.start()
                self.logger.info(f"{name} started successfully")
                
            self.logger.info("All test mode agents started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting test mode system: {e}")
            raise
            
    async def stop(self):
        """Stop the test mode system"""
        try:
            self.logger.info("Stopping Patent Agent System Test Mode")
            
            # Stop all agents
            for name, agent in self.agents.items():
                self.logger.info(f"Stopping {name}...")
                await agent.stop()
                self.logger.info(f"{name} stopped")
                
            # Shutdown message bus
            await message_bus_config.shutdown()
            self.logger.info("Message bus shutdown")
            
            # Shutdown context manager
            await context_manager.shutdown()
            self.logger.info("Context manager shutdown")
            
            self.logger.info("Patent Agent System Test Mode stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping test mode system: {e}")
            
    async def execute_workflow(self, topic: str, description: str) -> Dict[str, Any]:
        """Execute patent development workflow in test mode"""
        try:
            self.workflow_id = f"test_workflow_{uuid.uuid4().hex[:8]}"
            self.logger.info(f"Starting test workflow: {self.workflow_id}")
            self.logger.info(f"Topic: {topic}")
            self.logger.info(f"Description: {description}")
            
            # Create workflow context
            workflow_context = {
                "workflow_id": self.workflow_id,
                "topic": topic,
                "description": description,
                "start_time": time.time(),
                "test_mode": True
            }
            
            # Store context
            await context_manager.store_context(self.workflow_id, workflow_context)
            
            # Start workflow by sending initial task to coordinator
            initial_task = {
                "id": f"task_{uuid.uuid4().hex[:8]}",
                "type": "workflow_coordination",
                "topic": topic,
                "description": description,
                "workflow_id": self.workflow_id,
                "context": workflow_context
            }
            
            # Send task to coordinator agent
            coordinator = self.agents["coordinator_agent"]
            await coordinator.send_message(
                recipient="coordinator_agent",
                message_type=coordinator.broker.message_types.COORDINATION,
                content={"task": initial_task},
                priority=10
            )
            
            self.logger.info(f"Test workflow {self.workflow_id} started successfully")
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "message": "Test workflow started successfully",
                "test_mode": True
            }
            
        except Exception as e:
            self.logger.error(f"Error executing test workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_mode": True
            }
            
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status in test mode"""
        try:
            context = await context_manager.get_context(workflow_id)
            if not context:
                return {
                    "success": False,
                    "error": "Workflow not found",
                    "test_mode": True
                }
                
            # Get agent statuses
            agent_statuses = {}
            for name, agent in self.agents.items():
                status = await agent.get_status()
                agent_statuses[name] = status
                
            return {
                "success": True,
                "workflow_id": workflow_id,
                "context": context,
                "agent_statuses": agent_statuses,
                "test_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting test workflow status: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_mode": True
            }
            
    async def run_simple_test(self, topic: str, description: str) -> Dict[str, Any]:
        """Run a simple test to verify all agents work"""
        try:
            self.logger.info("Running simple test...")
            
            test_results = {}
            
            # Test each agent individually
            test_tasks = {
                "planner_agent": {
                    "type": "patent_planning",
                    "topic": topic,
                    "description": description
                },
                "searcher_agent": {
                    "type": "patent_search",
                    "topic": topic,
                    "description": description
                },
                "writer_agent": {
                    "type": "patent_drafting",
                    "topic": topic,
                    "description": description
                },
                "reviewer_agent": {
                    "type": "patent_review",
                    "topic": topic,
                    "description": description
                },
                "rewriter_agent": {
                    "type": "patent_rewriting",
                    "topic": topic,
                    "description": description
                },
                "discusser_agent": {
                    "type": "patent_discussion",
                    "topic": topic,
                    "description": description
                },
                "coordinator_agent": {
                    "type": "workflow_coordination",
                    "topic": topic,
                    "description": description
                }
            }
            
            for agent_name, task_data in test_tasks.items():
                self.logger.info(f"Testing {agent_name}...")
                agent = self.agents[agent_name]
                result = await agent.execute_task(task_data)
                test_results[agent_name] = {
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "has_content": bool(result.data.get("content")),
                    "test_mode": True
                }
                self.logger.info(f"{agent_name} test completed: {result.success}")
                
            return {
                "success": True,
                "test_results": test_results,
                "test_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in simple test: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_mode": True
            }