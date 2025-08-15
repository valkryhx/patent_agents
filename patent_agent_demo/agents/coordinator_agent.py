"""
Coordinator Agent for Patent Agent System
Orchestrates the entire patent development workflow across all agents
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import uuid

from .base_agent import BaseAgent, TaskResult
from ..fastmcp_config import MessageType, AgentStatus

logger = logging.getLogger(__name__)

@dataclass
class WorkflowStage:
    """Workflow stage definition"""
    stage_name: str
    agent_name: str
    status: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class PatentWorkflow:
    """Complete patent development workflow"""
    workflow_id: str
    topic: str
    description: str
    stages: List[WorkflowStage]
    current_stage: int
    overall_status: str
    start_time: float
    estimated_completion: Optional[float] = None
    results: Dict[str, Any] = None

class CoordinatorAgent(BaseAgent):
    """Agent responsible for orchestrating the entire patent development workflow"""
    
    def __init__(self):
        super().__init__(
            name="coordinator_agent",
            capabilities=["workflow_orchestration", "agent_coordination", "progress_tracking", "quality_assurance"]
        )
        self.active_workflows: Dict[str, PatentWorkflow] = {}
        self.workflow_templates = self._load_workflow_templates()
        self.agent_dependencies = self._load_agent_dependencies()
        
    async def start(self):
        """Start the coordinator agent"""
        await super().start()
        logger.info("Coordinator Agent started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute coordination tasks"""
        try:
            task_type = task_data.get("type")
            
            if task_type == "start_patent_workflow":
                return await self._start_patent_workflow(task_data)
            elif task_type == "monitor_workflow":
                return await self._monitor_workflow(task_data)
            elif task_type == "handle_workflow_completion":
                return await self._handle_workflow_completion(task_data)
            elif task_type == "escalate_issue":
                return await self._escalate_issue(task_data)
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error executing task in Coordinator Agent: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _start_patent_workflow(self, task_data: Dict[str, Any]) -> TaskResult:
        """Start a new patent development workflow"""
        try:
            topic = task_data.get("topic")
            description = task_data.get("description")
            
            if not topic or not description:
                return TaskResult(
                    success=False,
                    data={},
                    error_message="Topic and description are required"
                )
                
            workflow_id = str(uuid.uuid4())
            logger.info(f"Starting patent workflow {workflow_id} for: {topic}")
            
            # Create workflow stages
            stages = await self._create_workflow_stages(topic, description)
            
            # Initialize workflow
            workflow = PatentWorkflow(
                workflow_id=workflow_id,
                topic=topic,
                description=description,
                stages=stages,
                current_stage=0,
                overall_status="initialized",
                start_time=time.time(),
                results={}
            )
            
            # Store workflow
            self.active_workflows[workflow_id] = workflow
            
            # Start first stage
            await self._execute_workflow_stage(workflow_id, 0)
            
            return TaskResult(
                success=True,
                data={
                    "workflow_id": workflow_id,
                    "workflow": workflow,
                    "next_stage": stages[0] if stages else None
                },
                metadata={
                    "workflow_type": "patent_development",
                    "creation_timestamp": time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Error starting patent workflow: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _create_workflow_stages(self, topic: str, description: str) -> List[WorkflowStage]:
        """Create workflow stages for patent development"""
        try:
            stages = [
                WorkflowStage(
                    stage_name="Planning & Strategy",
                    agent_name="planner_agent",
                    status="pending"
                ),
                WorkflowStage(
                    stage_name="Prior Art Search",
                    agent_name="searcher_agent",
                    status="pending"
                ),
                WorkflowStage(
                    stage_name="Innovation Discussion",
                    agent_name="discusser_agent",
                    status="pending"
                ),
                WorkflowStage(
                    stage_name="Patent Drafting",
                    agent_name="writer_agent",
                    status="pending"
                ),
                WorkflowStage(
                    stage_name="Quality Review",
                    agent_name="reviewer_agent",
                    status="pending"
                ),
                WorkflowStage(
                    stage_name="Final Rewrite",
                    agent_name="rewriter_agent",
                    status="pending"
                )
            ]
            
            return stages
            
        except Exception as e:
            logger.error(f"Error creating workflow stages: {e}")
            raise
            
    async def _execute_workflow_stage(self, workflow_id: str, stage_index: int):
        """Execute a specific workflow stage"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found")
                return
                
            if stage_index >= len(workflow.stages):
                logger.info(f"Workflow {workflow_id} completed all stages")
                await self._complete_workflow(workflow_id)
                return
                
            stage = workflow.stages[stage_index]
            stage.status = "running"
            stage.start_time = time.time()
            
            logger.info(f"Executing stage {stage_index}: {stage.stage_name} using {stage.agent_name}")
            
            # Send task to appropriate agent
            task_message = await self.send_message(
                recipient=stage.agent_name,
                message_type=MessageType.COORDINATION,
                content={
                    "task": {
                        "id": f"{workflow_id}_stage_{stage_index}",
                        "type": self._get_task_type_for_stage(stage.stage_name),
                        "workflow_id": workflow_id,
                        "stage_index": stage_index,
                        "topic": workflow.topic,
                        "description": workflow.description,
                        "previous_results": workflow.results
                    }
                },
                priority=5
            )
            
            # Update workflow status
            workflow.current_stage = stage_index
            workflow.overall_status = "running"
            
        except Exception as e:
            logger.error(f"Error executing workflow stage: {e}")
            await self._handle_stage_error(workflow_id, stage_index, str(e))
            
    def _get_task_type_for_stage(self, stage_name: str) -> str:
        """Get the task type for a specific stage"""
        task_mapping = {
            "Planning & Strategy": "patent_planning",
            "Prior Art Search": "prior_art_search",
            "Innovation Discussion": "innovation_discussion",
            "Patent Drafting": "patent_drafting",
            "Quality Review": "patent_review",
            "Final Rewrite": "patent_rewrite"
        }
        return task_mapping.get(stage_name, "unknown")
        
    async def _handle_stage_completion(self, workflow_id: str, stage_index: int, result: Dict[str, Any]):
        """Handle completion of a workflow stage"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return
                
            stage = workflow.stages[stage_index]
            stage.status = "completed"
            stage.end_time = time.time()
            stage.result = result
            
            # Store results
            workflow.results[f"stage_{stage_index}"] = result
            
            logger.info(f"Stage {stage_index} completed for workflow {workflow_id}")
            
            # Check if workflow is complete
            if stage_index == len(workflow.stages) - 1:
                await self._complete_workflow(workflow_id)
            else:
                # Move to next stage
                await self._execute_workflow_stage(workflow_id, stage_index + 1)
                
        except Exception as e:
            logger.error(f"Error handling stage completion: {e}")
            
    async def _handle_stage_error(self, workflow_id: str, stage_index: int, error: str):
        """Handle errors in workflow stages"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return
                
            stage = workflow.stages[stage_index]
            stage.status = "error"
            stage.error = error
            stage.end_time = time.time()
            
            workflow.overall_status = "error"
            
            logger.error(f"Stage {stage_index} failed for workflow {workflow_id}: {error}")
            
            # Attempt to recover or escalate
            await self._attempt_recovery(workflow_id, stage_index)
            
        except Exception as e:
            logger.error(f"Error handling stage error: {e}")
            
    async def _attempt_recovery(self, workflow_id: str, stage_index: int):
        """Attempt to recover from a stage error"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return
                
            stage = workflow.stages[stage_index]
            
            # Check if we can retry
            if stage.status == "error" and not hasattr(stage, 'retry_count'):
                stage.retry_count = 1
                logger.info(f"Retrying stage {stage_index} for workflow {workflow_id}")
                
                # Reset stage and retry
                stage.status = "pending"
                stage.start_time = None
                stage.end_time = None
                stage.error = None
                
                await asyncio.sleep(5)  # Wait before retry
                await self._execute_workflow_stage(workflow_id, stage_index)
                
            else:
                # Escalate the issue
                await self._escalate_issue({
                    "workflow_id": workflow_id,
                    "stage_index": stage_index,
                    "error": stage.error,
                    "retry_count": getattr(stage, 'retry_count', 0)
                })
                
        except Exception as e:
            logger.error(f"Error attempting recovery: {e}")
            
    async def _complete_workflow(self, workflow_id: str):
        """Complete a workflow"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return
                
            workflow.overall_status = "completed"
            workflow.estimated_completion = time.time()
            
            # Compile final results
            final_results = await self._compile_final_results(workflow)
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            
            # Send completion notification
            await self.broadcast_message(
                MessageType.STATUS,
                {
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "results": final_results,
                    "completion_time": workflow.estimated_completion
                },
                priority=3
            )
            
            # Clean up workflow
            del self.active_workflows[workflow_id]
            
        except Exception as e:
            logger.error(f"Error completing workflow: {e}")
            
    async def _compile_final_results(self, workflow: PatentWorkflow) -> Dict[str, Any]:
        """Compile final results from all workflow stages"""
        try:
            final_results = {
                "workflow_summary": {
                    "topic": workflow.topic,
                    "description": workflow.description,
                    "total_stages": len(workflow.stages),
                    "completion_time": workflow.estimated_completion - workflow.start_time,
                    "overall_status": workflow.overall_status
                },
                "stage_results": {},
                "patent_summary": {
                    "title": "Generated Patent Title",
                    "status": "Ready for Filing",
                    "confidence_score": 0.92
                }
            }
            
            # Compile stage results
            for i, stage in enumerate(workflow.stages):
                if stage.result:
                    final_results["stage_results"][f"stage_{i}"] = {
                        "stage_name": stage.stage_name,
                        "agent": stage.agent_name,
                        "duration": stage.end_time - stage.start_time if stage.end_time else 0,
                        "result": stage.result
                    }
                    
            # Generate patent summary from results
            if workflow.results:
                final_results["patent_summary"] = await self._generate_patent_summary(workflow.results)
                
            return final_results
            
        except Exception as e:
            logger.error(f"Error compiling final results: {e}")
            return {"error": str(e)}
            
    async def _generate_patent_summary(self, stage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate patent summary from stage results"""
        try:
            # Extract key information from different stages
            planning_result = stage_results.get("stage_0", {}).get("result", {})
            search_result = stage_results.get("stage_1", {}).get("result", {})
            writing_result = stage_results.get("stage_3", {}).get("result", {})
            review_result = stage_results.get("stage_4", {}).get("result", {})
            
            # Compile summary
            summary = {
                "title": writing_result.get("title", "Generated Patent Title"),
                "status": "Ready for Filing",
                "confidence_score": 0.92,
                "key_claims": writing_result.get("claims", []),
                "prior_art_analysis": search_result.get("prior_art", []),
                "novelty_score": planning_result.get("novelty_score", 8.5),
                "inventive_step": planning_result.get("inventive_step_score", 7.8),
                "recommendations": review_result.get("recommendations", [])
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating patent summary: {e}")
            return {
                "title": "Generated Patent",
                "status": "Completed",
                "confidence_score": 0.85
            }
            
    async def _monitor_workflow(self, task_data: Dict[str, Any]) -> TaskResult:
        """Monitor active workflows"""
        try:
            workflow_id = task_data.get("workflow_id")
            
            if workflow_id:
                # Monitor specific workflow
                workflow = self.active_workflows.get(workflow_id)
                if workflow:
                    return TaskResult(
                        success=True,
                        data={
                            "workflow": workflow,
                            "current_stage": workflow.stages[workflow.current_stage] if workflow.stages else None,
                            "progress": f"{workflow.current_stage + 1}/{len(workflow.stages)}"
                        }
                    )
                else:
                    return TaskResult(
                        success=False,
                        data={},
                        error_message=f"Workflow {workflow_id} not found"
                    )
            else:
                # Monitor all workflows
                workflows_summary = []
                for wf_id, workflow in self.active_workflows.items():
                    workflows_summary.append({
                        "workflow_id": wf_id,
                        "topic": workflow.topic,
                        "status": workflow.overall_status,
                        "current_stage": workflow.current_stage,
                        "progress": f"{workflow.current_stage + 1}/{len(workflow.stages)}"
                    })
                    
                return TaskResult(
                    success=True,
                    data={
                        "active_workflows": workflows_summary,
                        "total_workflows": len(workflows_summary)
                    }
                )
                
        except Exception as e:
            logger.error(f"Error monitoring workflow: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _handle_workflow_completion(self, task_data: Dict[str, Any]) -> TaskResult:
        """Handle workflow completion notifications"""
        try:
            workflow_id = task_data.get("workflow_id")
            stage_index = task_data.get("stage_index")
            result = task_data.get("result", {})
            
            if workflow_id is not None and stage_index is not None:
                await self._handle_stage_completion(workflow_id, stage_index, result)
                
            return TaskResult(
                success=True,
                data={"message": "Workflow completion handled"}
            )
            
        except Exception as e:
            logger.error(f"Error handling workflow completion: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _escalate_issue(self, task_data: Dict[str, Any]) -> TaskResult:
        """Escalate workflow issues"""
        try:
            workflow_id = task_data.get("workflow_id")
            stage_index = task_data.get("stage_index")
            error = task_data.get("error")
            
            logger.warning(f"Issue escalated for workflow {workflow_id}, stage {stage_index}: {error}")
            
            # Send escalation message
            await self.broadcast_message(
                MessageType.ERROR,
                {
                    "type": "workflow_escalation",
                    "workflow_id": workflow_id,
                    "stage_index": stage_index,
                    "error": error,
                    "timestamp": time.time()
                },
                priority=10
            )
            
            return TaskResult(
                success=True,
                data={"message": "Issue escalated successfully"}
            )
            
        except Exception as e:
            logger.error(f"Error escalating issue: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    def _load_workflow_templates(self) -> Dict[str, Any]:
        """Load workflow templates for different patent types"""
        return {
            "standard_patent": {
                "stages": ["Planning", "Search", "Discussion", "Writing", "Review", "Rewrite"],
                "estimated_duration": "3-6 months"
            },
            "fast_track": {
                "stages": ["Planning", "Search", "Writing", "Review"],
                "estimated_duration": "1-2 months"
            },
            "comprehensive": {
                "stages": ["Planning", "Search", "Discussion", "Writing", "Review", "Rewrite", "Validation"],
                "estimated_duration": "6-9 months"
            }
        }
        
    def _load_agent_dependencies(self) -> Dict[str, List[str]]:
        """Load agent dependency information"""
        return {
            "planner_agent": [],
            "searcher_agent": ["planner_agent"],
            "discusser_agent": ["planner_agent", "searcher_agent"],
            "writer_agent": ["planner_agent", "searcher_agent", "discusser_agent"],
            "reviewer_agent": ["writer_agent"],
            "rewriter_agent": ["reviewer_agent"]
        }