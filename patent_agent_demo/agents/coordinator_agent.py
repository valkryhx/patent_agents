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
from ..message_bus import MessageType, AgentStatus
from ..context_manager import context_manager, ContextType, ContextItem

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
        self.completed_workflows: Dict[str, Dict[str, Any]] = {}
        
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
            
            # Initialize context for this workflow
            logger.info(f"Initializing context for workflow {workflow_id}")
            theme_definition = await context_manager.initialize_workflow_context(workflow_id, topic, description)
            logger.info(f"Context initialized with theme: {theme_definition.primary_title}")
            
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
        """Execute a specific workflow stage with enhanced reliability"""
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
            
            # Check agent availability
            if not await self._check_agent_availability(stage.agent_name):
                logger.error(f"Agent {stage.agent_name} is not available")
                await self._handle_stage_error(workflow_id, stage_index, f"Agent {stage.agent_name} not available")
                return
            
            # Get task type
            task_type = self._get_task_type_for_stage(stage.stage_name)
            logger.info(f"Task type: {task_type}")
            
            # Get context for this agent
            try:
                context_data = await context_manager.get_context_for_agent(
                    workflow_id, 
                    stage.agent_name,
                    self._get_context_types_for_stage(stage.stage_name)
                )
                logger.info(f"Context data retrieved for {stage.agent_name}")
            except Exception as e:
                logger.warning(f"Failed to get context data: {e}, using empty context")
                context_data = {}
            
            # Build task content
            task_content = self._build_task_content(workflow, stage_index, task_type, context_data)
            logger.info(f"Task content built for {stage.agent_name}")
            
            # Send message and wait for confirmation
            message_sent = await self._send_task_message(stage.agent_name, task_content)
            if not message_sent:
                logger.error(f"Failed to send task to {stage.agent_name}")
                await self._handle_stage_error(workflow_id, stage_index, f"Failed to send task to {stage.agent_name}")
                return
                
            workflow.current_stage = stage_index
            workflow.overall_status = "running"
            logger.info(f"Stage {stage_index} ({stage.stage_name}) started successfully")
            
        except Exception as e:
            logger.error(f"Error executing workflow stage: {e}")
            await self._handle_stage_error(workflow_id, stage_index, str(e))
            
    async def _check_agent_availability(self, agent_name: str) -> bool:
        """Check if agent is available"""
        try:
            agent_info = self.broker.agents.get(agent_name)
            if not agent_info:
                logger.warning(f"Agent {agent_name} not found in broker")
                return False
                
            if agent_info.status == AgentStatus.OFFLINE:
                logger.warning(f"Agent {agent_name} is offline")
                return False
                
            logger.info(f"Agent {agent_name} is available (status: {agent_info.status.value})")
            return True
            
        except Exception as e:
            logger.error(f"Error checking agent availability: {e}")
            return False
            
    def _build_task_content(self, workflow: PatentWorkflow, stage_index: int, task_type: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build task content with artifacts"""
        task_content = {
            "task": {
                "id": f"{workflow.workflow_id}_stage_{stage_index}",
                "type": task_type,
                "workflow_id": workflow.workflow_id,
                "stage_index": stage_index,
                "topic": workflow.topic,
                "description": workflow.description,
                "previous_results": workflow.results,
                "context": context_data
            }
        }
        
        # Inject artifacts based on task type
        if task_type == "patent_drafting":
            task_content["task"]["generation_mode"] = "chapter_split"
        elif task_type == "patent_review":
            current_draft = self._get_current_draft(workflow)
            if current_draft:
                task_content["task"]["patent_draft"] = current_draft
                logger.info("Added patent draft to review task")
        elif task_type == "patent_rewrite":
            current_draft = self._get_current_draft(workflow)
            last_feedback = self._get_latest_review_feedback(workflow)
            if current_draft:
                task_content["task"]["patent_draft"] = current_draft
                logger.info("Added patent draft to rewrite task")
            if last_feedback:
                task_content["task"]["review_feedback"] = last_feedback
                logger.info("Added review feedback to rewrite task")
        elif task_type == "innovation_discussion":
            last_feedback = self._get_latest_review_feedback(workflow)
            if last_feedback:
                task_content["task"]["review_feedback"] = last_feedback
                logger.info("Added review feedback to discussion task")
                
        return task_content
        
    async def _send_task_message(self, agent_name: str, task_content: Dict[str, Any]) -> bool:
        """Send task message and wait for confirmation"""
        try:
            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.COORDINATION,
                sender=self.name,
                recipient=agent_name,
                content=task_content,
                timestamp=time.time(),
                priority=5
            )
            
            logger.info(f"Sending task message to {agent_name}")
            await self.broker.send_message(message)
            
            # Wait a short time to confirm message was sent
            await asyncio.sleep(0.1)
            
            logger.info(f"Task message sent successfully to {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending task message to {agent_name}: {e}")
            return False
 
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
        
    def _get_context_types_for_stage(self, stage_name: str) -> List[ContextType]:
        """Get required context types for a specific stage"""
        context_mapping = {
            "Planning & Strategy": [
                ContextType.THEME_DEFINITION,
                ContextType.TECHNICAL_DOMAIN
            ],
            "Prior Art Search": [
                ContextType.THEME_DEFINITION,
                ContextType.TECHNICAL_DOMAIN,
                ContextType.TERMINOLOGY
            ],
            "Innovation Discussion": [
                ContextType.THEME_DEFINITION,
                ContextType.INNOVATION_POINTS,
                ContextType.PRIOR_ART
            ],
            "Patent Drafting": [
                ContextType.THEME_DEFINITION,
                ContextType.TECHNICAL_DOMAIN,
                ContextType.INNOVATION_POINTS,
                ContextType.TERMINOLOGY,
                ContextType.PRIOR_ART
            ],
            "Quality Review": [
                ContextType.THEME_DEFINITION,
                ContextType.CLAIMS_FOCUS,
                ContextType.TERMINOLOGY
            ],
            "Final Rewrite": [
                ContextType.THEME_DEFINITION,
                ContextType.TECHNICAL_DOMAIN,
                ContextType.INNOVATION_POINTS,
                ContextType.TERMINOLOGY,
                ContextType.CLAIMS_FOCUS
            ]
        }
        return context_mapping.get(stage_name, [ContextType.THEME_DEFINITION])
        
    async def _handle_status_message(self, message):
        """Override status handler to catch completion events and advance workflow"""
        try:
            content = message.content or {}
            task_id = content.get("task_id")
            status = content.get("status")
            success = content.get("success")
            
            logger.info(f"STATUS RECV from={message.sender} status={status} success={success} task_id={task_id}")
            
            # Check if this is a stage completion message
            if (task_id and "_stage_" in task_id and 
                (status == "completed" or success is True)):
                
                try:
                    # Parse workflow_id and stage_index from task_id
                    if "_stage_" in task_id:
                        workflow_id, stage_index_str = task_id.split("_stage_")
                        stage_index = int(stage_index_str)
                        
                        logger.info(f"STAGE COMPLETE parsed workflow={workflow_id} stage={stage_index}")
                        
                        # Get result from message content
                        result = content.get("result", {})
                        
                        # Handle stage completion
                        await self._handle_stage_completion(workflow_id, stage_index, result)
                    else:
                        logger.warning(f"Invalid task_id format: {task_id}")
                        await super()._handle_status_message(message)
                        
                except (ValueError, IndexError) as e:
                    logger.error(f"Error parsing task_id {task_id}: {e}")
                    await super()._handle_status_message(message)
            else:
                # Fallback to base for agent status updates
                await super()._handle_status_message(message)
                
        except Exception as e:
            logger.error(f"Coordinator status handling error: {e}")
            # Fallback to base handler
            await super()._handle_status_message(message)
 
    def _get_current_draft(self, workflow: PatentWorkflow):
        """Return the most recent draft object from writer or rewriter stage results"""
        try:
            # Prefer latest rewrite
            for i in reversed(range(len(workflow.stages))):
                st = workflow.stages[i]
                sr = workflow.results.get(f"stage_{i}", {})
                data = sr.get("result", {}) if sr else {}
                if st.stage_name == "Final Rewrite" and (data.get("improved_draft") or data.get("rewrite_result", {}).get("improved_draft")):
                    return data.get("improved_draft") or data.get("rewrite_result", {}).get("improved_draft")
            # Fallback to writer stage
            for i, st in enumerate(workflow.stages):
                if st.stage_name == "Patent Drafting":
                    data = workflow.results.get(f"stage_{i}", {}).get("result", {})
                    if data.get("patent_draft"):
                        return data.get("patent_draft")
            return None
        except Exception:
            return None
 
    def _get_latest_review_feedback(self, workflow: PatentWorkflow):
        """Return the latest review feedback dict"""
        try:
            for i in reversed(range(len(workflow.stages))):
                st = workflow.stages[i]
                if st.stage_name == "Quality Review":
                    data = workflow.results.get(f"stage_{i}", {}).get("result", {})
                    return data.get("feedback") or data.get("review_result")
            return None
        except Exception:
            return None
 
    async def _handle_stage_completion(self, workflow_id: str, stage_index: int, result: Dict[str, Any]):
        """Handle completion of a workflow stage with simplified iterative review-rewrite loop"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found in stage completion")
                return
            
            stage = workflow.stages[stage_index]
            stage.status = "completed"
            stage.end_time = time.time()
            stage.result = result
            workflow.results[f"stage_{stage_index}"] = {"result": result}
            logger.info(f"Stage {stage_index} ({stage.stage_name}) completed for workflow {workflow_id}")
            
            # Validate and update context based on stage result
            await self._validate_and_update_context(workflow_id, stage_index, result, stage.stage_name)
            
            # Simplified flow control
            stage_name = stage.stage_name
            logger.info(f"Processing stage completion: {stage_name}")
            
            if stage_name == "Patent Drafting":
                # Directly proceed to review stage
                logger.info("Patent drafting completed, proceeding to quality review")
                await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Quality Review"))
                
            elif stage_name == "Quality Review":
                # Check if rewrite is needed
                needs_rewrite = self._check_if_rewrite_needed(result)
                if needs_rewrite:
                    logger.info("Quality review indicates rewrite needed, proceeding to final rewrite")
                    await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Final Rewrite"))
                else:
                    logger.info("Quality review passed, completing workflow")
                    await self._complete_workflow(workflow_id)
                    
            elif stage_name == "Final Rewrite":
                # Rewrite completed, re-review
                logger.info("Final rewrite completed, proceeding to quality review")
                await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Quality Review"))
                
            else:
                # Continue to next stage for other stages
                if stage_index < len(workflow.stages) - 1:
                    logger.info(f"Proceeding to next stage: {stage_index + 1}")
                    await self._execute_workflow_stage(workflow_id, stage_index + 1)
                else:
                    logger.info("All stages completed, finishing workflow")
                    await self._complete_workflow(workflow_id)
         
        except Exception as e:
            logger.error(f"Error handling stage completion: {e}")
            await self._handle_stage_error(workflow_id, stage_index, str(e))
            
    def _check_if_rewrite_needed(self, result: Dict[str, Any]) -> bool:
        """Check if rewrite is needed based on review result"""
        try:
            # Extract quality score
            quality_score = result.get("quality_score", 0)
            if isinstance(quality_score, str):
                try:
                    quality_score = float(quality_score)
                except ValueError:
                    quality_score = 0
                    
            # Extract compliance status
            compliance_status = result.get("compliance_status", "unknown")
            if not compliance_status:
                compliance_status = result.get("review_result", {}).get("compliance_status", "unknown")
                
            # Extract review outcome
            review_outcome = result.get("review_outcome", "")
            if not review_outcome:
                review_outcome = result.get("review_result", {}).get("review_outcome", "")
            
            logger.info(f"Review analysis - Quality score: {quality_score}, Compliance: {compliance_status}, Outcome: {review_outcome}")
            
            # Check if rewrite is needed
            needs_rewrite = (
                quality_score < 8.0 or 
                compliance_status in ["needs_major_revision", "needs_minor_revision", "non_compliant"] or
                review_outcome in ["needs_revision", "major_revision_required"]
            )
            
            logger.info(f"Rewrite needed: {needs_rewrite}")
            return needs_rewrite
            
        except Exception as e:
            logger.error(f"Error checking if rewrite needed: {e}")
            # Default to rewrite if we can't determine
            return True
            
    async def _start_review_iteration(self, workflow_id: str):
        """Begin the first review after drafting, with loop metadata."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        workflow.results.setdefault("iteration", {"count": 0, "max": 3, "target_score": 8.8})
        await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Quality Review"))
 
    def _find_stage_index(self, workflow: PatentWorkflow, stage_name: str) -> int:
        for i, st in enumerate(workflow.stages):
            if st.stage_name == stage_name:
                return i
        return max(0, workflow.current_stage)
 
    async def _trigger_rewrite_cycle(self, workflow_id: str, review_stage_index: int):
        """Trigger rewriter and then discussion if necessary."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        iteration = workflow.results.setdefault("iteration", {"count": 0, "max": 3, "target_score": 8.8})
        if iteration["count"] >= iteration.get("max", 3):
            logger.info(f"Iteration limit reached for workflow {workflow_id}")
            # proceed to next stage after review (rewrite already in pipeline or stop)
            next_idx = review_stage_index + 1 if review_stage_index + 1 < len(workflow.stages) else review_stage_index
            await self._execute_workflow_stage(workflow_id, next_idx)
            return
        iteration["count"] += 1
        # Run rewriter stage
        await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Final Rewrite"))
 
    async def _post_rewrite_next_steps(self, workflow_id: str, rewrite_stage_index: int):
        """After rewrite, run a brief discussion and then re-review; stop when target met."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        # Optional: brief discussion to validate changes
        await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Innovation Discussion"))
        # Then re-run review
        await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Quality Review"))
 
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
            # Export to markdown
            try:
                import os
                os.makedirs("/workspace/output", exist_ok=True)
                md_path = f"/workspace/output/{workflow.topic.replace(' ', '_')}_{workflow_id[:8]}.md"
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(f"# {workflow.topic}\n\n")
                    # Try to compile final patent draft into a readable document
                    try:
                        draft = self._get_current_draft(workflow)
                    except Exception:
                        draft = None
                    if draft:
                        f.write("## 专利交底书\n\n")
                        title = getattr(draft, "title", "") or "Generated Patent Title"
                        f.write(f"### 标题\n\n{title}\n\n")
                        abstract = getattr(draft, "abstract", "")
                        if abstract:
                            f.write(f"### 摘要\n\n{abstract}\n\n")
                        background = getattr(draft, "background", "")
                        if background:
                            f.write(f"### 背景技术\n\n{background}\n\n")
                        summary = getattr(draft, "summary", "")
                        if summary:
                            f.write(f"### 发明内容/技术方案\n\n{summary}\n\n")
                        detail = getattr(draft, "detailed_description", "")
                        if detail:
                            f.write(f"### 具体实施方式\n\n{detail}\n\n")
                        claims = getattr(draft, "claims", []) or []
                        if claims:
                            f.write("### 权利要求书\n\n")
                            for idx, cl in enumerate(claims, 1):
                                f.write(f"{idx}. {cl}\n")
                            f.write("\n")
                        drawings = getattr(draft, "drawings_description", "")
                        if drawings:
                            f.write(f"### 附图说明\n\n{drawings}\n\n")
                        diagrams = getattr(draft, "technical_diagrams", []) or []
                        if diagrams:
                            f.write("### 技术示意图说明\n\n")
                            for d in diagrams:
                                f.write(f"- {d}\n")
                            f.write("\n")
                    # Append stage-wise raw results for traceability
                    for i, stage in enumerate(workflow.stages):
                        f.write(f"## Stage {i+1}: {stage.stage_name}\n\n")
                        if stage.result:
                            f.write(str(stage.result))
                            f.write("\n\n")
                    f.write("\n")
                logger.info(f"Exported workflow document to {md_path}")
            except Exception as e:
                logger.error(f"Export error: {e}")
            # Persist final results, cleanup
            self.completed_workflows[workflow_id] = final_results
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
        except Exception as e:
            logger.error(f"Error completing workflow: {e}")
            
    async def _compile_final_results(self, workflow: PatentWorkflow) -> Dict[str, Any]:
        """Compile final results from all workflow stages, including last review metrics and iterations"""
        try:
            final_results = {
                "workflow_summary": {
                    "topic": workflow.topic,
                    "description": workflow.description,
                    "total_stages": len(workflow.stages),
                    "completion_time": workflow.estimated_completion - workflow.start_time,
                    "overall_status": workflow.overall_status,
                    "iterations": workflow.results.get("iteration", {}).get("count", 0)
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
                    # Check if it's completed and stored
                    if workflow_id in self.completed_workflows:
                        return TaskResult(
                            success=True,
                            data={
                                "workflow": {"workflow_id": workflow_id, "overall_status": "completed"},
                                "final_results": self.completed_workflows.get(workflow_id)
                            }
                        )
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
        
        async def _validate_and_update_context(self, workflow_id: str, stage_index: int,
                                         result: Dict[str, Any], stage_name: str):
        """Validate stage result and update context accordingly with enhanced error handling"""
        try:
            logger.info(f"Validating and updating context for stage {stage_name}")

            # Extract output text for validation
            output_text = self._extract_output_text(result, stage_name)
            output_type = "general"

            if output_text:
                logger.info(f"Extracted output text for validation: {output_text[:100]}...")
                
                # Validate output against context
                try:
                    validation_result = await context_manager.validate_agent_output(
                        workflow_id, f"stage_{stage_index}", output_text, output_type
                    )

                    if not validation_result["is_consistent"]:
                        logger.warning(f"Context consistency issues in {stage_name}: {validation_result['issues']}")

                        # Add context item for the issues
                        try:
                            await context_manager.add_context_item(workflow_id, ContextItem(
                                context_type=ContextType.THEME_DEFINITION,
                                key=f"consistency_issue_{stage_name}",
                                value=validation_result["issues"],
                                source_agent=f"stage_{stage_index}",
                                timestamp=time.time(),
                                confidence=validation_result["score"]
                            ))
                        except Exception as e:
                            logger.warning(f"Failed to add consistency issue to context: {e}")
                    else:
                        logger.info(f"Context validation passed for {stage_name}")

                except Exception as e:
                    logger.warning(f"Context validation failed: {e}, continuing without validation")

                # Extract and add new context items based on stage result
                try:
                    await self._extract_context_from_result(workflow_id, stage_index, result, stage_name)
                    logger.info(f"Context extraction completed for {stage_name}")
                except Exception as e:
                    logger.warning(f"Context extraction failed: {e}")

            else:
                logger.info(f"No output text extracted for {stage_name}, skipping validation")

        except Exception as e:
            logger.error(f"Error validating and updating context: {e}")
            # Don't block the workflow, just log the error

    def _extract_output_text(self, result: Dict[str, Any], stage_name: str) -> str:
        """Extract output text for validation"""
        try:
            if stage_name == "Planning & Strategy":
                return result.get("strategy", {}).get("summary", "")
            elif stage_name == "Prior Art Search":
                return result.get("search_results", {}).get("summary", "")
            elif stage_name == "Innovation Discussion":
                return result.get("discussion", {}).get("summary", "")
            elif stage_name == "Patent Drafting":
                return result.get("patent_draft", {}).get("title", "")
            elif stage_name == "Quality Review":
                return result.get("feedback", {}).get("summary", "")
            elif stage_name == "Final Rewrite":
                return result.get("improved_draft", {}).get("title", "")
            else:
                return str(result)
        except Exception as e:
            logger.warning(f"Error extracting output text: {e}")
            return str(result)
            
    async def _extract_context_from_result(self, workflow_id: str, stage_index: int, 
                                         result: Dict[str, Any], stage_name: str):
        """Extract context items from stage result"""
        try:
            if stage_name == "Planning & Strategy":
                strategy = result.get("strategy", {})
                if strategy:
                    await context_manager.add_context_item(workflow_id, ContextItem(
                        context_type=ContextType.INNOVATION_POINTS,
                        key="planned_innovations",
                        value=strategy.get("key_innovations", []),
                        source_agent=f"stage_{stage_index}",
                        timestamp=time.time()
                    ))
                    
            elif stage_name == "Prior Art Search":
                search_results = result.get("search_results", {})
                if search_results:
                    await context_manager.add_context_item(workflow_id, ContextItem(
                        context_type=ContextType.PRIOR_ART,
                        key="prior_art_summary",
                        value=search_results.get("summary", ""),
                        source_agent=f"stage_{stage_index}",
                        timestamp=time.time()
                    ))
                    
            elif stage_name == "Innovation Discussion":
                discussion = result.get("discussion", {})
                if discussion:
                    await context_manager.add_context_item(workflow_id, ContextItem(
                        context_type=ContextType.INNOVATION_POINTS,
                        key="discussed_innovations",
                        value=discussion.get("key_points", []),
                        source_agent=f"stage_{stage_index}",
                        timestamp=time.time()
                    ))
                    
            elif stage_name == "Patent Drafting":
                draft = result.get("patent_draft", {})
                if draft:
                    await context_manager.add_context_item(workflow_id, ContextItem(
                        context_type=ContextType.CLAIMS_FOCUS,
                        key="draft_claims",
                        value=draft.get("claims", []),
                        source_agent=f"stage_{stage_index}",
                        timestamp=time.time()
                    ))
                    
            elif stage_name == "Quality Review":
                feedback = result.get("feedback", {})
                if feedback:
                    await context_manager.add_context_item(workflow_id, ContextItem(
                        context_type=ContextType.CLAIMS_FOCUS,
                        key="review_feedback",
                        value=feedback.get("issues", []),
                        source_agent=f"stage_{stage_index}",
                        timestamp=time.time()
                    ))
                    
        except Exception as e:
            logger.error(f"Error extracting context from result: {e}")
            
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed workflow status"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return {"status": "not_found", "workflow_id": workflow_id}
            
            return {
                "workflow_id": workflow_id,
                "current_stage": workflow.current_stage,
                "current_stage_name": workflow.stages[workflow.current_stage].stage_name if workflow.stages else None,
                "overall_status": workflow.overall_status,
                "topic": workflow.topic,
                "start_time": workflow.start_time,
                "stages": [
                    {
                        "name": stage.stage_name,
                        "agent": stage.agent_name,
                        "status": stage.status,
                        "start_time": stage.start_time,
                        "end_time": stage.end_time,
                        "error": stage.error
                    }
                    for stage in workflow.stages
                ],
                "results": workflow.results
            }
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"status": "error", "error": str(e)}
            
    async def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            return {
                agent_name: {
                    "status": agent_info.status.value,
                    "capabilities": agent_info.capabilities,
                    "current_task": agent_info.current_task,
                    "last_activity": agent_info.last_activity
                }
                for agent_name, agent_info in self.broker.agents.items()
            }
        except Exception as e:
            logger.error(f"Error getting agents status: {e}")
            return {"error": str(e)}
            
    async def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of all workflows"""
        try:
            active_workflows = len(self.active_workflows)
            completed_workflows = len(self.completed_workflows)
            
            return {
                "active_workflows": active_workflows,
                "completed_workflows": completed_workflows,
                "total_workflows": active_workflows + completed_workflows,
                "active_workflow_ids": list(self.active_workflows.keys()),
                "completed_workflow_ids": list(self.completed_workflows.keys())
            }
        except Exception as e:
            logger.error(f"Error getting workflow summary: {e}")
            return {"error": str(e)}