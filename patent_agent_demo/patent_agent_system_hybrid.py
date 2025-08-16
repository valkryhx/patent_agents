"""
Patent Agent System Hybrid Mode
Mix of real agents (first 3) and test agents (remaining)
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, List

# Import real agents
from .agents.planner_agent import PlannerAgent
from .agents.searcher_agent import SearcherAgent
from .agents.writer_agent import WriterAgent

# Import test agents
from .agents.reviewer_agent_test import ReviewerAgentTestMode
from .agents.rewriter_agent_test import RewriterAgentTestMode
from .agents.discusser_agent_test import DiscusserAgentTestMode
from .agents.coordinator_agent_test import CoordinatorAgentTestMode

from .message_bus import message_bus_config
from .context_manager import context_manager

logger = logging.getLogger(__name__)

class PatentAgentSystemHybrid:
    """Hybrid mode patent agent system - mix of real and test agents"""
    
    def __init__(self):
        self.agents = {}
        self.workflow_id = None
        self.logger = logging.getLogger("hybrid_system")
        
    async def start(self):
        """Start the hybrid mode system"""
        try:
            self.logger.info("Starting Patent Agent System in HYBRID MODE")
            self.logger.info("Real agents: planner_agent, searcher_agent, writer_agent")
            self.logger.info("Test agents: reviewer_agent, rewriter_agent, discusser_agent, coordinator_agent")
            
            # Initialize message bus
            await message_bus_config.initialize()
            self.logger.info("Message bus initialized")
            
            # Initialize context manager
            await context_manager.initialize()
            self.logger.info("Context manager initialized")
            
            # Create and start real agents (first 3)
            self.logger.info("Creating real agents...")
            self.agents["planner_agent"] = PlannerAgent()
            self.agents["searcher_agent"] = SearcherAgent()
            self.agents["writer_agent"] = WriterAgent()
            
            # Create and start test agents (remaining)
            self.logger.info("Creating test agents...")
            self.agents["reviewer_agent"] = ReviewerAgentTestMode()
            self.agents["rewriter_agent"] = RewriterAgentTestMode()
            self.agents["discusser_agent"] = DiscusserAgentTestMode()
            self.agents["coordinator_agent"] = CoordinatorAgentTestMode()
            
            # Start all agents
            for name, agent in self.agents.items():
                self.logger.info(f"Starting {name}...")
                await agent.start()
                self.logger.info(f"{name} started successfully")
                
            self.logger.info("All hybrid agents started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting hybrid system: {e}")
            raise
            
    async def stop(self):
        """Stop the hybrid mode system"""
        try:
            self.logger.info("Stopping Patent Agent System Hybrid Mode")
            
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
            
            self.logger.info("Patent Agent System Hybrid Mode stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping hybrid system: {e}")
            
    async def execute_workflow(self, topic: str, description: str) -> Dict[str, Any]:
        """Execute patent development workflow in hybrid mode"""
        try:
            self.workflow_id = f"hybrid_workflow_{uuid.uuid4().hex[:8]}"
            self.logger.info(f"Starting hybrid workflow: {self.workflow_id}")
            self.logger.info(f"Topic: {topic}")
            self.logger.info(f"Description: {description}")
            
            # Create workflow context
            workflow_context = {
                "workflow_id": self.workflow_id,
                "topic": topic,
                "description": description,
                "start_time": time.time(),
                "hybrid_mode": True
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
            
            self.logger.info(f"Hybrid workflow {self.workflow_id} started successfully")
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "message": "Hybrid workflow started successfully",
                "hybrid_mode": True
            }
            
        except Exception as e:
            self.logger.error(f"Error executing hybrid workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "hybrid_mode": True
            }
            
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status in hybrid mode"""
        try:
            context = await context_manager.get_context(workflow_id)
            if not context:
                return {
                    "success": False,
                    "error": "Workflow not found",
                    "hybrid_mode": True
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
                "hybrid_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting hybrid workflow status: {e}")
            return {
                "success": False,
                "error": str(e),
                "hybrid_mode": True
            }
            
    async def run_hybrid_test(self, topic: str, description: str) -> Dict[str, Any]:
        """Run a hybrid test to verify all agents work together"""
        try:
            self.logger.info("Running hybrid test...")
            
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
                
                try:
                    result = await agent.execute_task(task_data)
                    test_results[agent_name] = {
                        "success": result.success,
                        "execution_time": result.execution_time,
                        "has_content": bool(result.data.get("content")),
                        "hybrid_mode": True,
                        "agent_type": "real" if agent_name in ["planner_agent", "searcher_agent", "writer_agent"] else "test"
                    }
                    self.logger.info(f"{agent_name} test completed: {result.success}")
                except Exception as e:
                    self.logger.error(f"Error testing {agent_name}: {e}")
                    test_results[agent_name] = {
                        "success": False,
                        "error": str(e),
                        "hybrid_mode": True,
                        "agent_type": "real" if agent_name in ["planner_agent", "searcher_agent", "writer_agent"] else "test"
                    }
                
            return {
                "success": True,
                "test_results": test_results,
                "hybrid_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in hybrid test: {e}")
            return {
                "success": False,
                "error": str(e),
                "hybrid_mode": True
            }
            
    async def test_real_agents_only(self, topic: str, description: str) -> Dict[str, Any]:
        """Test only the real agents (first 3)"""
        try:
            self.logger.info("Testing real agents only...")
            
            test_results = {}
            real_agents = ["planner_agent", "searcher_agent", "writer_agent"]
            
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
                }
            }
            
            for agent_name in real_agents:
                self.logger.info(f"Testing real agent: {agent_name}...")
                agent = self.agents[agent_name]
                
                try:
                    result = await agent.execute_task(test_tasks[agent_name])
                    test_results[agent_name] = {
                        "success": result.success,
                        "execution_time": result.execution_time,
                        "has_content": bool(result.data.get("content")),
                        "agent_type": "real"
                    }
                    self.logger.info(f"{agent_name} test completed: {result.success}")
                except Exception as e:
                    self.logger.error(f"Error testing {agent_name}: {e}")
                    test_results[agent_name] = {
                        "success": False,
                        "error": str(e),
                        "agent_type": "real"
                    }
                
            return {
                "success": True,
                "test_results": test_results,
                "agent_type": "real_only",
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in real agents test: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": "real_only"
            }