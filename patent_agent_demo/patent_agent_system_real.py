"""
Patent Agent System Real Mode
All agents use real mode with actual API calls
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, List

# Import all real agents
from .agents.planner_agent import PlannerAgent
from .agents.searcher_agent import SearcherAgent
from .agents.writer_agent import WriterAgent
from .agents.reviewer_agent import ReviewerAgent
from .agents.rewriter_agent import RewriterAgent
from .agents.discusser_agent import DiscusserAgent
from .agents.coordinator_agent import CoordinatorAgent

from .message_bus import message_bus_config
from .context_manager import context_manager

logger = logging.getLogger(__name__)

class PatentAgentSystemReal:
    """Real mode patent agent system - all agents use real APIs"""
    
    def __init__(self):
        self.agents = {}
        self.workflow_id = None
        self.logger = logging.getLogger("real_system")
        
    async def start(self):
        """Start the real mode system"""
        try:
            self.logger.info("Starting Patent Agent System in REAL MODE")
            self.logger.info("All agents will use real API calls")
            
            # Initialize message bus
            await message_bus_config.initialize()
            self.logger.info("Message bus initialized")
            
            # Initialize context manager
            await context_manager.initialize()
            self.logger.info("Context manager initialized")
            
            # Create and start all real agents
            self.logger.info("Creating real agents...")
            self.agents = {
                "planner_agent": PlannerAgent(),
                "searcher_agent": SearcherAgent(),
                "writer_agent": WriterAgent(),
                "reviewer_agent": ReviewerAgent(),
                "rewriter_agent": RewriterAgent(),
                "discusser_agent": DiscusserAgent(),
                "coordinator_agent": CoordinatorAgent()
            }
            
            # Start all agents
            for name, agent in self.agents.items():
                self.logger.info(f"Starting {name}...")
                await agent.start()
                self.logger.info(f"{name} started successfully")
                
            self.logger.info("All real agents started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting real system: {e}")
            raise
            
    async def stop(self):
        """Stop the real mode system"""
        try:
            self.logger.info("Stopping Patent Agent System Real Mode")
            
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
            
            self.logger.info("Patent Agent System Real Mode stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping real system: {e}")
            
    async def execute_workflow(self, topic: str, description: str) -> Dict[str, Any]:
        """Execute patent development workflow in real mode"""
        try:
            self.workflow_id = f"real_workflow_{uuid.uuid4().hex[:8]}"
            self.logger.info(f"Starting real workflow: {self.workflow_id}")
            self.logger.info(f"Topic: {topic}")
            self.logger.info(f"Description: {description}")
            
            # Create workflow context
            workflow_context = {
                "workflow_id": self.workflow_id,
                "topic": topic,
                "description": description,
                "start_time": time.time(),
                "real_mode": True
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
            
            self.logger.info(f"Real workflow {self.workflow_id} started successfully")
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "message": "Real workflow started successfully",
                "real_mode": True
            }
            
        except Exception as e:
            self.logger.error(f"Error executing real workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "real_mode": True
            }
            
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status in real mode"""
        try:
            context = await context_manager.get_context(workflow_id)
            if not context:
                return {
                    "success": False,
                    "error": "Workflow not found",
                    "real_mode": True
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
                "real_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real workflow status: {e}")
            return {
                "success": False,
                "error": str(e),
                "real_mode": True
            }
            
    async def run_real_test(self, topic: str, description: str) -> Dict[str, Any]:
        """Run a real test to verify all agents work with real APIs"""
        try:
            self.logger.info("Running real test with all agents...")
            
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
                self.logger.info(f"Testing real agent: {agent_name}...")
                agent = self.agents[agent_name]
                
                try:
                    result = await agent.execute_task(task_data)
                    test_results[agent_name] = {
                        "success": result.success,
                        "execution_time": result.execution_time,
                        "has_content": bool(result.data.get("content")),
                        "real_mode": True,
                        "agent_type": "real",
                        "content_preview": result.data.get("content", "")[:200] + "..." if result.data.get("content") else ""
                    }
                    self.logger.info(f"{agent_name} test completed: {result.success}")
                except Exception as e:
                    self.logger.error(f"Error testing {agent_name}: {e}")
                    test_results[agent_name] = {
                        "success": False,
                        "error": str(e),
                        "real_mode": True,
                        "agent_type": "real"
                    }
                
            return {
                "success": True,
                "test_results": test_results,
                "real_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in real test: {e}")
            return {
                "success": False,
                "error": str(e),
                "real_mode": True
            }
            
    async def run_patent_writing_workflow(self, topic: str, description: str) -> Dict[str, Any]:
        """Run a complete patent writing workflow"""
        try:
            self.logger.info("Starting complete patent writing workflow...")
            
            workflow_results = {}
            workflow_start_time = time.time()
            
            # Step 1: Planning
            self.logger.info("Step 1: Patent Planning...")
            planner = self.agents["planner_agent"]
            planning_result = await planner.execute_task({
                "type": "patent_planning",
                "topic": topic,
                "description": description
            })
            workflow_results["planning"] = {
                "success": planning_result.success,
                "execution_time": planning_result.execution_time,
                "content": planning_result.data.get("content", ""),
                "error": planning_result.error_message
            }
            
            if not planning_result.success:
                return {
                    "success": False,
                    "error": f"Planning failed: {planning_result.error_message}",
                    "workflow_results": workflow_results
                }
            
            # Step 2: Searching
            self.logger.info("Step 2: Patent Searching...")
            searcher = self.agents["searcher_agent"]
            search_result = await searcher.execute_task({
                "type": "patent_search",
                "topic": topic,
                "description": description
            })
            workflow_results["searching"] = {
                "success": search_result.success,
                "execution_time": search_result.execution_time,
                "content": search_result.data.get("content", ""),
                "error": search_result.error_message
            }
            
            if not search_result.success:
                return {
                    "success": False,
                    "error": f"Searching failed: {search_result.error_message}",
                    "workflow_results": workflow_results
                }
            
            # Step 3: Writing
            self.logger.info("Step 3: Patent Writing...")
            writer = self.agents["writer_agent"]
            writing_result = await writer.execute_task({
                "type": "patent_drafting",
                "topic": topic,
                "description": description,
                "previous_results": {
                    "planning": planning_result.data,
                    "searching": search_result.data
                }
            })
            workflow_results["writing"] = {
                "success": writing_result.success,
                "execution_time": writing_result.execution_time,
                "content": writing_result.data.get("content", ""),
                "error": writing_result.error_message
            }
            
            if not writing_result.success:
                return {
                    "success": False,
                    "error": f"Writing failed: {writing_result.error_message}",
                    "workflow_results": workflow_results
                }
            
            # Step 4: Reviewing
            self.logger.info("Step 4: Patent Reviewing...")
            reviewer = self.agents["reviewer_agent"]
            review_result = await reviewer.execute_task({
                "type": "patent_review",
                "topic": topic,
                "description": description,
                "patent_draft": writing_result.data.get("content", "")
            })
            workflow_results["reviewing"] = {
                "success": review_result.success,
                "execution_time": review_result.execution_time,
                "content": review_result.data.get("content", ""),
                "error": review_result.error_message
            }
            
            if not review_result.success:
                return {
                    "success": False,
                    "error": f"Reviewing failed: {review_result.error_message}",
                    "workflow_results": workflow_results
                }
            
            # Step 5: Rewriting (if needed)
            self.logger.info("Step 5: Patent Rewriting...")
            rewriter = self.agents["rewriter_agent"]
            rewrite_result = await rewriter.execute_task({
                "type": "patent_rewriting",
                "topic": topic,
                "description": description,
                "original_draft": writing_result.data.get("content", ""),
                "review_comments": review_result.data.get("content", "")
            })
            workflow_results["rewriting"] = {
                "success": rewrite_result.success,
                "execution_time": rewrite_result.execution_time,
                "content": rewrite_result.data.get("content", ""),
                "error": rewrite_result.error_message
            }
            
            if not rewrite_result.success:
                return {
                    "success": False,
                    "error": f"Rewriting failed: {rewrite_result.error_message}",
                    "workflow_results": workflow_results
                }
            
            # Step 6: Discussion
            self.logger.info("Step 6: Patent Discussion...")
            discusser = self.agents["discusser_agent"]
            discussion_result = await discusser.execute_task({
                "type": "patent_discussion",
                "topic": topic,
                "description": description,
                "final_draft": rewrite_result.data.get("content", "")
            })
            workflow_results["discussion"] = {
                "success": discussion_result.success,
                "execution_time": discussion_result.execution_time,
                "content": discussion_result.data.get("content", ""),
                "error": discussion_result.error_message
            }
            
            # Calculate total workflow time
            total_workflow_time = time.time() - workflow_start_time
            
            return {
                "success": True,
                "workflow_results": workflow_results,
                "total_workflow_time": total_workflow_time,
                "real_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in patent writing workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "real_mode": True
            }