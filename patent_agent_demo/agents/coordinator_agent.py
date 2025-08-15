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
            # Build task content with latest artifacts
            task_type = self._get_task_type_for_stage(stage.stage_name)
            task_content = {
                "task": {
                    "id": f"{workflow_id}_stage_{stage_index}",
                    "type": task_type,
                    "workflow_id": workflow_id,
                    "stage_index": stage_index,
                    "topic": workflow.topic,
                    "description": workflow.description,
                    "previous_results": workflow.results
                }
            }
            # Inject artifacts
            if task_type == "patent_drafting":
                # Hint writer to split large content into chapters in its internal prompts
                task_content["task"]["generation_mode"] = "chapter_split"
            elif task_type == "patent_review":
                current_draft = self._get_current_draft(workflow)
                if current_draft:
                    task_content["task"]["patent_draft"] = current_draft
            elif task_type == "patent_rewrite":
                current_draft = self._get_current_draft(workflow)
                last_feedback = self._get_latest_review_feedback(workflow)
                if current_draft:
                    task_content["task"]["patent_draft"] = current_draft
                if last_feedback:
                    task_content["task"]["review_feedback"] = last_feedback
            elif task_type == "innovation_discussion":
                last_feedback = self._get_latest_review_feedback(workflow)
                if last_feedback:
                    task_content["task"]["review_feedback"] = last_feedback
            await self.send_message(
                recipient=stage.agent_name,
                message_type=MessageType.COORDINATION,
                content=task_content,
                priority=5
            )
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
        
    async def _handle_status_message(self, message):
        """Override status handler to catch completion events and advance workflow"""
        try:
            content = message.content or {}
            if content.get("status") == "completed" and content.get("task_id") and "_stage_" in content.get("task_id"):
                task_id = content.get("task_id")
                result = content.get("result", {})
                workflow_id, stage_index_str = task_id.split("_stage_")
                await self._handle_stage_completion(workflow_id, int(stage_index_str), result)
            else:
                # fallback to base for agent status updates
                await super()._handle_status_message(message)
        except Exception as e:
            logger.error(f"Coordinator status handling error: {e}")
 
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
        """Handle completion of a workflow stage with iterative review-rewrite loop"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return
            
            stage = workflow.stages[stage_index]
            stage.status = "completed"
            stage.end_time = time.time()
            stage.result = result
            workflow.results[f"stage_{stage_index}"] = {"result": result}
            logger.info(f"Stage {stage_index} completed for workflow {workflow_id}")
            
            # If writer stage completed, start review/rewriter iterative loop
            stage_name = stage.stage_name
            if stage_name == "Patent Drafting":
                workflow.results.setdefault("iteration", {"count": 0, "max": 3, "target_score": 8.8})
                await self._start_review_iteration(workflow_id)
                return
            
            # If review result suggests revisions OR below target quality, trigger rewrite
            if stage_name == "Quality Review":
                compliance = result.get("compliance_status") or result.get("review_result", {}).get("compliance_status")
                outcome = result.get("review_outcome")
                quality_score = result.get("quality_score") or result.get("review_result", {}).get("overall_score")
                iteration = workflow.results.setdefault("iteration", {"count": 0, "max": 3, "target_score": 8.8})
                if (compliance in ("needs_major_revision", "needs_minor_revision", "non_compliant")
                    or outcome in ("needs_revision", "major_revision_required")
                    or (quality_score is not None and quality_score < iteration.get("target_score", 8.8))):
                    await self._trigger_rewrite_cycle(workflow_id, stage_index)
                    return
                # Meets target -> proceed
            
            # If rewrite completed, then re-discuss and re-review
            if stage_name == "Final Rewrite":
                await self._post_rewrite_next_steps(workflow_id, stage_index)
                return
            
            # Default: proceed to next stage
            if stage_index == len(workflow.stages) - 1:
                await self._complete_workflow(workflow_id)
            else:
                await self._execute_workflow_stage(workflow_id, stage_index + 1)
         
        except Exception as e:
            logger.error(f"Error handling stage completion: {e}")
            
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
                os.makedirs("/output", exist_ok=True)
                md_path = f"/output/{workflow.topic.replace(' ', '_')}_{workflow_id[:8]}.md"
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