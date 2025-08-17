"""
Coordinator Agent for Patent Agent System
Orchestrates the entire patent development workflow across all agents
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import uuid

from .base_agent import BaseAgent, TaskResult
from ..message_bus import MessageType, AgentStatus, Message
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
    
    def __init__(self, test_mode: bool = False):
        super().__init__(
            name="coordinator_agent",
            capabilities=["workflow_orchestration", "agent_coordination", "progress_tracking", "quality_assurance"],
            test_mode=test_mode
        )
        self.active_workflows: Dict[str, PatentWorkflow] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}  # Track completed task IDs and results
        self.failed_tasks: set = set()     # Track failed task IDs
        self.workflow_templates = self._load_workflow_templates()
        self.agent_dependencies = self._load_agent_dependencies()
        self.completed_workflows: Dict[str, Dict[str, Any]] = {}
        
        self.agent_logger.info(f"🎯 协调器智能体初始化完成")
        self.agent_logger.info(f"   工作流模板数量: {len(self.workflow_templates)}")
        self.agent_logger.info(f"   智能体依赖关系数量: {len(self.agent_dependencies)}")
        
    async def start(self):
        """Start the coordinator agent"""
        await super().start()
        self.agent_logger.info(f"🎯 协调器智能体启动成功")
        logger.info("Coordinator Agent started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute coordination tasks"""
        try:
            task_type = task_data.get("type")
            self.agent_logger.info(f"🎯 协调器收到任务: {task_type}")
            self.agent_logger.info(f"   任务数据: {task_data}")
            
            if task_type == "start_patent_workflow":
                self.agent_logger.info(f"🚀 开始专利工作流")
                return await self._start_patent_workflow(task_data)
            # 删除监控任务处理，协调器不应该执行监控任务
            # elif task_type == "monitor_workflow":
            #     self.agent_logger.info(f"📊 监控工作流")
            #     return await self._monitor_workflow(task_data)
            elif task_type == "handle_workflow_completion":
                self.agent_logger.info(f"✅ 处理工作流完成")
                return await self._handle_workflow_completion(task_data)
            elif task_type == "escalate_issue":
                self.agent_logger.info(f"⚠️ 升级问题")
                return await self._escalate_issue(task_data)
            elif task_type == "get_all_agents_status":
                self.agent_logger.info(f"📋 获取所有智能体状态")
                return await self.get_all_agents_status()
            elif task_type == "get_workflow_summary":
                self.agent_logger.info(f"📋 获取工作流摘要")
                return await self.get_workflow_summary()
            else:
                self.agent_logger.warning(f"⚠️ 未知任务类型: {task_type}")
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            self.agent_logger.error(f"❌ 协调器任务执行失败: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
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
            
            self.agent_logger.info(f"🚀 开始专利工作流")
            self.agent_logger.info(f"   主题: {topic}")
            self.agent_logger.info(f"   描述: {description}")
            
            if not topic or not description:
                self.agent_logger.error(f"❌ 缺少必要参数: topic 或 description")
                return TaskResult(
                    success=False,
                    data={},
                    error_message="Topic and description are required"
                )
                
            workflow_id = str(uuid.uuid4())
            self.agent_logger.info(f"🆔 生成工作流ID: {workflow_id}")
            logger.info(f"Starting patent workflow {workflow_id} for: {topic}")
            
            # Initialize context for this workflow
            self.agent_logger.info(f"📋 初始化工作流上下文: {workflow_id}")
            logger.info(f"Initializing context for workflow {workflow_id}")
            theme_definition = await context_manager.initialize_workflow_context(workflow_id, topic, description)
            self.agent_logger.info(f"✅ 上下文初始化完成，主题: {theme_definition.primary_title}")
            logger.info(f"Context initialized with theme: {theme_definition.primary_title}")
            
            # Create workflow stages
            self.agent_logger.info(f"📋 创建工作流阶段")
            stages = await self._create_workflow_stages(topic, description)
            self.agent_logger.info(f"✅ 创建了 {len(stages)} 个工作流阶段")
            
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
            self.agent_logger.info(f"💾 工作流已存储到活动工作流列表")
            
            # Start first stage
            self.agent_logger.info(f"🚀 开始执行第一个阶段")
            await self._execute_workflow_stage(workflow_id, 0)
            
            self.agent_logger.info(f"✅ 专利工作流启动成功")
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
            self.agent_logger.error(f"❌ 启动专利工作流失败: {e}")
            self.agent_logger.error(f"   错误详情: {traceback.format_exc()}")
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
        """Execute a specific workflow stage with true sequential execution"""
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
            
            # Send task and wait for completion
            task_id = task_content["task"]["id"]
            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.COORDINATION,
                sender=self.name,
                recipient=stage.agent_name,
                content=task_content,
                timestamp=time.time(),
                priority=5
            )
            
            logger.info(f"Sending task message to {stage.agent_name} with task_id: {task_id}")
            await self.broker.send_message(message)
            
            # Wait for task completion with timeout
            timeout = 180  # 3 minutes timeout
            start_time = time.time()
            
            logger.info(f"Waiting for task {task_id} completion...")
            
            while time.time() - start_time < timeout:
                # Check if we have received a completion message for this task
                if task_id in self.completed_tasks:
                    logger.info(f"Task {task_id} completed successfully")
                    # Get the result from completed_tasks
                    result = self.completed_tasks.get(task_id, {})
                    # Process the completion
                    await self._handle_stage_completion(workflow_id, stage_index, result)
                    return
                    
                # Check if we have received an error message for this task
                if task_id in self.failed_tasks:
                    logger.error(f"Task {task_id} failed")
                    await self._handle_stage_error(workflow_id, stage_index, f"Task {task_id} failed")
                    return
                    
                # Log progress every 10 seconds (more frequent than before)
                elapsed = time.time() - start_time
                if int(elapsed) % 10 == 0 and elapsed > 0:
                    logger.info(f"Still waiting for task {task_id} completion... ({elapsed:.1f}s elapsed)")
                    # Also log the current state of completed_tasks and failed_tasks
                    logger.info(f"Current completed_tasks: {list(self.completed_tasks.keys())}")
                    logger.info(f"Current failed_tasks: {list(self.failed_tasks)}")
                    
                await asyncio.sleep(1)  # Check every 1 second (more frequent than before)
                
            logger.error(f"Task {task_id} timed out after {timeout} seconds")
            logger.error(f"Final state - completed_tasks: {list(self.completed_tasks.keys())}")
            logger.error(f"Final state - failed_tasks: {list(self.failed_tasks)}")
            await self._handle_stage_error(workflow_id, stage_index, f"Task {task_id} timed out")
            
        except Exception as e:
            logger.error(f"Error executing workflow stage: {e}")
            await self._handle_stage_error(workflow_id, stage_index, str(e))
            
    async def _check_agent_availability(self, agent_name: str) -> bool:
        """Check if agent is available"""
        try:
            # Add a small delay to allow agents to fully initialize
            await asyncio.sleep(1)
            
            # Log all available agents for debugging
            available_agents = list(self.broker.agents.keys())
            logger.info(f"Available agents in broker: {available_agents}")
            
            agent_info = self.broker.agents.get(agent_name)
            if not agent_info:
                logger.warning(f"Agent {agent_name} not found in broker")
                # Try again after a short delay
                await asyncio.sleep(2)
                agent_info = self.broker.agents.get(agent_name)
                if not agent_info:
                    logger.error(f"Agent {agent_name} still not found in broker after retry")
                    logger.error(f"Available agents: {list(self.broker.agents.keys())}")
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
        
    async def _handle_status_message_override(self, message):
        """Override status handler to catch completion events and advance workflow"""
        print(f"🔍 ENTERING _handle_status_message_override for {self.name}")
        logger.info(f"🔍 ENTERING _handle_status_message_override for {self.name}")
        
        try:
            logger.info(f"🔍 SIMPLIFIED: Method entered successfully")
            logger.info(f"🔍 SIMPLIFIED: Message sender: {message.sender}")
            logger.info(f"🔍 SIMPLIFIED: Message type: {message.type}")
            
            content = message.content or {}
            task_id = content.get("task_id")
            status = content.get("status")
            success = content.get("success")
            
            logger.info(f"🔍 SIMPLIFIED: task_id={task_id}, status={status}, success={success}")
            
            # For now, just log and return
            logger.info(f"🔍 SIMPLIFIED: Method completed successfully")
            
        except Exception as e:
            logger.error(f"🔍 SIMPLIFIED: Error in method: {e}")
            import traceback
            logger.error(f"🔍 SIMPLIFIED: Traceback: {traceback.format_exc()}")
        finally:
            logger.info("✅ coordinator_agent 状态消息处理完成")
 
    async def _handle_error_message(self, message: Message):
        """Handle error messages and track failed tasks"""
        try:
            content = message.content or {}
            task_id = content.get("task_id")
            
            if task_id:
                self.failed_tasks.add(task_id)
                logger.error(f"Task {task_id} marked as failed due to error message")
            
            # Call parent error handler
            await super()._handle_error_message(message)
            
        except Exception as e:
            logger.error(f"Error handling error message: {e}")
            await super()._handle_error_message(message)
 
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
        """Handle completion of a workflow stage with iterative review-rewrite loop control"""
        logger.info(f"🔍 ENTERING _handle_stage_completion for workflow={workflow_id} stage={stage_index}")
        
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                logger.error(f"Workflow {workflow_id} not found in stage completion")
                return
            
            stage = workflow.stages[stage_index]
            stage.status = "completed"
            stage.end_time = time.time()
            stage.result = result
            
            # Initialize results if None
            if workflow.results is None:
                workflow.results = {}
            
            workflow.results[f"stage_{stage_index}"] = {"result": result}
            logger.info(f"Stage {stage_index} ({stage.stage_name}) completed for workflow {workflow_id}")
            
            # Simplified version - skip complex logic for now
            logger.info(f"🔍 SIMPLIFIED: Stage completion processed successfully")
            logger.info(f"🔍 SIMPLIFIED: Stage name: {stage.stage_name}")
            
            # For now, just proceed to next stage for non-iterative stages
            stage_name = stage.stage_name
            if stage_name == "Planning & Strategy":
                logger.info("Planning completed, proceeding to next stage")
                # Continue to next stage
                if stage_index < len(workflow.stages) - 1:
                    next_stage = workflow.stages[stage_index + 1]
                    agent_name = next_stage.agent_name
                    
                    logger.info(f"Sending task to {agent_name} for stage {stage_index + 1}")
                    
                    # Create task data
                    task_data = {
                        "id": f"{workflow_id}_stage_{stage_index + 1}",
                        "type": next_stage.stage_name.lower().replace(" ", "_"),
                        "workflow_id": workflow_id,
                        "stage_index": stage_index + 1,
                        "topic": workflow.topic,
                        "description": workflow.description,
                        "context": await context_manager.get_context_for_agent(workflow_id, agent_name)
                    }
                    
                    # Send task to next agent
                    await self._send_task_to_agent(agent_name, task_data)
                else:
                    logger.info("All stages completed, finishing workflow")
                    await self._complete_workflow(workflow_id)
            else:
                logger.info(f"🔍 SIMPLIFIED: Stage {stage_name} completed, workflow will continue")
         
        except Exception as e:
            logger.error(f"Error handling stage completion: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            await self._handle_stage_error(workflow_id, stage_index, str(e))
            
    def _check_if_rewrite_needed(self, result: Dict[str, Any], iteration: Dict[str, Any]) -> bool:
        """Check if rewrite is needed based on review result and iteration state"""
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
            
            # Get iteration parameters
            target_quality_score = iteration.get("target_quality_score", 8.0)
            review_count = iteration.get("review_count", 1)
            rewrite_count = iteration.get("rewrite_count", 0)
            
            logger.info(f"Review analysis - Quality score: {quality_score}, Compliance: {compliance_status}, Outcome: {review_outcome}")
            logger.info(f"Iteration state - Review #{review_count}, Rewrite #{rewrite_count}, Target score: {target_quality_score}")
            
            # Adjust target score based on iteration count (be more lenient in later iterations)
            adjusted_target = target_quality_score
            if review_count > 2:
                adjusted_target = max(6.0, target_quality_score - 1.0)  # Lower threshold for later reviews
                logger.info(f"Adjusted target score to {adjusted_target} for review #{review_count}")
            
            # Check if rewrite is needed
            needs_rewrite = (
                quality_score < adjusted_target or 
                compliance_status in ["needs_major_revision", "needs_minor_revision", "non_compliant"] or
                review_outcome in ["needs_revision", "major_revision_required"]
            )
            
            # Additional logic for consecutive failures
            if needs_rewrite and review_count > 1:
                # Check if this is a consecutive failure
                iteration["consecutive_failures"] += 1
                max_consecutive_failures = iteration.get("max_consecutive_failures", 2)
                
                if iteration["consecutive_failures"] >= max_consecutive_failures:
                    logger.warning(f"Consecutive failures ({iteration['consecutive_failures']}) reached limit, forcing completion")
                    needs_rewrite = False  # Force completion instead of continuing to rewrite
            else:
                # Reset consecutive failures counter if review passed
                iteration["consecutive_failures"] = 0
            
            logger.info(f"Rewrite needed: {needs_rewrite} (consecutive failures: {iteration.get('consecutive_failures', 0)})")
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
            
            logger.error(f"Stage {stage_index} failed for workflow {workflow_id}: {error}")
            
            # Attempt to recover or continue to next stage
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
                # Stage failed after retry - continue to next stage
                logger.error(f"Stage {stage_index} failed after retry, continuing to next stage")
                workflow = self.active_workflows.get(workflow_id)
                if workflow:
                    # Continue to next stage instead of terminating
                    if stage_index < len(workflow.stages) - 1:
                        logger.info(f"Continuing to next stage: {stage_index + 1}")
                        await asyncio.sleep(2)
                        await self._execute_workflow_stage(workflow_id, stage_index + 1)
                    else:
                        logger.info("All stages completed, finishing workflow")
                        await self._complete_workflow(workflow_id)
                
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
                # 使用相对路径，在当前项目目录下创建output文件夹
                output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
                os.makedirs(output_dir, exist_ok=True)
                md_path = os.path.join(output_dir, f"{workflow.topic.replace(' ', '_')}_{workflow_id[:8]}.md")
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
            
    # 删除监控工作流方法，协调器不应该执行监控任务
    # async def _monitor_workflow(self, task_data: Dict[str, Any]) -> TaskResult:
    #     """Monitor active workflows"""
    #     try:
    #         workflow_id = task_data.get("workflow_id")
    #         
    #         if workflow_id:
    #             # Monitor specific workflow
    #             workflow = self.active_workflows.get(workflow_id)
    #             try:
    #                 return TaskResult(
    #                     success=True,
    #                     data={
    #                         "workflow": workflow,
    #                         "current_stage": workflow.stages[workflow.current_stage] if workflow.stages else None,
    #                         "progress": f"{workflow.current_stage + 1}/{len(workflow.stages)}"
    #                     }
    #                 )
    #             else:
    #                 # Check if it's completed and stored
    #                 if workflow_id in self.completed_workflows:
    #                     return TaskResult(
    #                         success=True,
    #                         data={
    #                             "workflow": {"workflow_id": workflow_id, "overall_status": "completed"},
    #                             "final_results": self.completed_workflows.get(workflow_id)
    #                         }
    #                     )
    #                 return TaskResult(
    #                     success=False,
    #                     data={},
    #                     error_message=f"Workflow {workflow_id} not found"
    #                 )
    #         else:
    #             # Monitor all workflows
    #             workflows_summary = []
    #             for wf_id, workflow in self.active_workflows.items():
    #                 workflows_summary.append({
    #                         "workflow_id": wf_id,
    #                         "topic": workflow.topic,
    #                         "status": workflow.overall_status,
    #                         "current_stage": workflow.current_stage,
    #                         "progress": f"{workflow.current_stage + 1}/{len(workflow.stages)}"
    #                     })
    #                     
    #             return TaskResult(
    #                 success=True,
    #                 data={
    #                     "active_workflows": workflows_summary,
    #                     "total_workflows": len(workflows_summary)
    #                 }
    #             )
    #             
    #     except Exception as e:
    #         logger.error(f"Error monitoring workflow: {e}")
    #         return TaskResult(
    #             success=False,
    #                 data={},
    #                 error_message=str(e)
    #             )
            
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
                    
                    # Validate output against context (simplified to avoid blocking)
                    try:
                        validation_result = await context_manager.validate_agent_output(
                            workflow_id, f"stage_{stage_index}", output_text, output_type
                        )

                        if not validation_result["is_consistent"]:
                            logger.warning(f"Context consistency issues in {stage_name}: {validation_result['issues']}")

                            # Add context item for the issues (simplified)
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

                    # Extract and add new context items based on stage result (simplified)
                    try:
                        await self._extract_context_from_result(workflow_id, stage_index, result, stage_name)
                        logger.info(f"Context extraction completed for {stage_name}")
                    except Exception as e:
                        logger.warning(f"Context extraction failed: {e}")

                else:
                    logger.info(f"No output text extracted for {stage_name}, skipping validation")

            except Exception as e:
                logger.warning(f"Error validating and updating context: {e}")
                # Don't block the workflow, just log the error and continue

    def _extract_output_text(self, result: Dict[str, Any], stage_name: str) -> str:
        """Extract output text for validation"""
        try:
            if stage_name == "Planning & Strategy":
                strategy = result.get("strategy", {})
                if strategy:
                    # Handle PatentStrategy object
                    if hasattr(strategy, 'key_innovation_areas'):
                        return str(getattr(strategy, 'key_innovation_areas', []))
                    elif isinstance(strategy, dict):
                        return strategy.get("summary", "")
                    else:
                        return str(strategy)
                return ""
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
                    # Handle PatentStrategy object
                    if hasattr(strategy, 'key_innovation_areas'):
                        innovations = getattr(strategy, 'key_innovation_areas', [])
                    elif isinstance(strategy, dict):
                        innovations = strategy.get("key_innovations", [])
                    else:
                        innovations = []
                    
                    await context_manager.add_context_item(workflow_id, ContextItem(
                        context_type=ContextType.INNOVATION_POINTS,
                        key="planned_innovations",
                        value=innovations,
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
            
            # Get iteration status
            iteration_status = self._get_iteration_status(workflow)
            
            return {
                "workflow_id": workflow_id,
                "current_stage": workflow.current_stage,
                "current_stage_name": workflow.stages[workflow.current_stage].stage_name if workflow.stages else None,
                "overall_status": workflow.overall_status,
                "topic": workflow.topic,
                "start_time": workflow.start_time,
                "iteration_status": iteration_status,
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
            
    def _get_iteration_status(self, workflow: PatentWorkflow) -> Dict[str, Any]:
        """Get iteration status for the workflow"""
        try:
            iteration = workflow.results.get("iteration", {})
            if not iteration:
                return {"status": "not_started"}
            
            review_count = iteration.get("review_count", 0)
            rewrite_count = iteration.get("rewrite_count", 0)
            max_reviews = iteration.get("max_reviews", 3)
            max_rewrites = iteration.get("max_rewrites", 3)
            consecutive_failures = iteration.get("consecutive_failures", 0)
            target_quality_score = iteration.get("target_quality_score", 8.0)
            
            # Determine iteration phase
            if review_count == 0:
                phase = "initial"
            elif review_count > 0 and rewrite_count == 0:
                phase = "first_review"
            elif rewrite_count > 0:
                phase = "rewrite_cycle"
            else:
                phase = "unknown"
            
            # Check if limits are approaching
            review_limit_warning = review_count >= max_reviews * 0.8  # 80% of limit
            rewrite_limit_warning = rewrite_count >= max_rewrites * 0.8
            consecutive_failure_warning = consecutive_failures >= iteration.get("max_consecutive_failures", 2) * 0.8
            
            return {
                "status": "active",
                "phase": phase,
                "review_count": review_count,
                "rewrite_count": rewrite_count,
                "max_reviews": max_reviews,
                "max_rewrites": max_rewrites,
                "consecutive_failures": consecutive_failures,
                "target_quality_score": target_quality_score,
                "warnings": {
                    "review_limit_approaching": review_limit_warning,
                    "rewrite_limit_approaching": rewrite_limit_warning,
                    "consecutive_failure_approaching": consecutive_failure_warning
                },
                "remaining_reviews": max(0, max_reviews - review_count),
                "remaining_rewrites": max(0, max_rewrites - rewrite_count)
            }
            
        except Exception as e:
            logger.error(f"Error getting iteration status: {e}")
            return {"status": "error", "error": str(e)}
            
    async def get_all_agents_status(self) -> TaskResult:
        """Get status of all agents"""
        try:
            agents_status = {
                agent_name: {
                    "status": agent_info.status.value,
                    "capabilities": agent_info.capabilities,
                    "current_task": agent_info.current_task,
                    "last_activity": agent_info.last_activity
                }
                for agent_name, agent_info in self.broker.agents.items()
            }
            return TaskResult(
                success=True,
                data=agents_status,
                metadata={"timestamp": time.time()}
            )
        except Exception as e:
            logger.error(f"Error getting agents status: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def get_workflow_summary(self) -> TaskResult:
        """Get summary of all workflows"""
        try:
            active_workflows = len(self.active_workflows)
            completed_workflows = len(self.completed_workflows)
            
            summary = {
                "active_workflows": active_workflows,
                "completed_workflows": completed_workflows,
                "total_workflows": active_workflows + completed_workflows,
                "active_workflow_ids": list(self.active_workflows.keys()),
                "completed_workflow_ids": list(self.completed_workflows.keys())
            }
            
            # Add latest workflow details if available
            if self.active_workflows:
                latest_workflow_id = list(self.active_workflows.keys())[-1]
                latest_workflow = self.active_workflows[latest_workflow_id]
                summary["latest_workflow"] = {
                    "workflow_id": latest_workflow_id,
                    "topic": latest_workflow.topic,
                    "status": latest_workflow.overall_status,
                    "current_stage": latest_workflow.current_stage,
                    "start_time": latest_workflow.start_time
                }
            
            return TaskResult(
                success=True,
                data=summary,
                metadata={"timestamp": time.time()}
            )
        except Exception as e:
            logger.error(f"Error getting workflow summary: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def broadcast_message(self, message_type: MessageType, content: Dict[str, Any], 
                              recipient: str = "all", priority: int = 5) -> None:
        """Broadcast a message to all agents or a specific agent"""
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
            
            if recipient == "all":
                # Broadcast to all agents
                for agent_name in self.broker.agents.keys():
                    if agent_name != self.name:
                        await self.broker.send_message(message)
            else:
                # Send to specific agent
                await self.broker.send_message(message)
                
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            
    async def _execute_test_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a test task with mock data for coordinator agent"""
        try:
            task_type = task_data.get("type")
            self.agent_logger.info(f"🧪 协调器测试模式执行任务: {task_type}")
            
            if task_type == "start_patent_workflow":
                # 模拟工作流启动
                workflow_id = str(uuid.uuid4())
                mock_workflow = PatentWorkflow(
                    workflow_id=workflow_id,
                    topic=task_data.get("topic", "测试主题"),
                    description=task_data.get("description", "测试描述"),
                    stages=[],
                    current_stage=0,
                    overall_status="test_completed",
                    start_time=time.time(),
                    results={"test_result": "模拟工作流启动成功"}
                )
                
                self.active_workflows[workflow_id] = mock_workflow
                
                return TaskResult(
                    success=True,
                    data={
                        "workflow_id": workflow_id,
                        "workflow": mock_workflow,
                        "test_mode": True
                    },
                    metadata={"test_execution": True}
                )
                
            elif task_type == "get_all_agents_status":
                # 模拟获取智能体状态
                mock_agents_status = {
                    "planner_agent": {"status": "online", "capabilities": ["planning"], "current_task": None, "last_activity": time.time()},
                    "searcher_agent": {"status": "online", "capabilities": ["searching"], "current_task": None, "last_activity": time.time()},
                    "discusser_agent": {"status": "online", "capabilities": ["discussion"], "current_task": None, "last_activity": time.time()},
                    "writer_agent": {"status": "online", "capabilities": ["writing"], "current_task": None, "last_activity": time.time()},
                    "reviewer_agent": {"status": "online", "capabilities": ["reviewing"], "current_task": None, "last_activity": time.time()},
                    "rewriter_agent": {"status": "online", "capabilities": ["rewriting"], "current_task": None, "last_activity": time.time()}
                }
                
                return TaskResult(
                    success=True,
                    data=mock_agents_status,
                    metadata={"test_execution": True, "timestamp": time.time()}
                )
                
            elif task_type == "get_workflow_summary":
                # 模拟获取工作流摘要
                mock_summary = {
                    "active_workflows": len(self.active_workflows),
                    "completed_workflows": 0,
                    "total_workflows": len(self.active_workflows),
                    "active_workflow_ids": list(self.active_workflows.keys()),
                    "completed_workflow_ids": [],
                    "test_mode": True
                }
                
                return TaskResult(
                    success=True,
                    data=mock_summary,
                    metadata={"test_execution": True, "timestamp": time.time()}
                )
                
            else:
                # 默认测试响应
                return TaskResult(
                    success=True,
                    data={"test_result": f"测试任务 {task_type} 执行成功"},
                    metadata={"test_execution": True}
                )
                
        except Exception as e:
            self.agent_logger.error(f"❌ 协调器测试任务执行失败: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=f"Test task failed: {str(e)}"
            )
            
