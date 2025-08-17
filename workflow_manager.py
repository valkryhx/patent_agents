#!/usr/bin/env python3
"""
Workflow Manager - Task Assignment to Agent Services
Assigns tasks to agent services and manages workflow progression
"""

import asyncio
import time
import uuid
import httpx
from typing import Dict, Any, List, Optional
import logging

from models import (
    WorkflowState, WorkflowStatus, StageInfo, 
    WorkflowStatusEnum, StageStatusEnum, TestModeConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent service URLs (all on same port with different paths)
AGENT_SERVICES = {
    "planning": "http://localhost:8000/agents/planner",
    "search": "http://localhost:8000/agents/searcher", 
    "discussion": "http://localhost:8000/agents/discussion",
    "drafting": "http://localhost:8000/agents/writer",
    "review": "http://localhost:8000/agents/reviewer",
    "rewrite": "http://localhost:8000/agents/rewriter",
    "compressor": "http://localhost:8000/agents/compressor"  # Optional compression agent
}

class WorkflowManager:
    """Task assignment workflow manager"""
    
    def __init__(self):
        # In-memory storage
        self.workflows: Dict[str, WorkflowState] = {}
        self.test_mode = TestModeConfig(enabled=True)
        
        logger.info("🚀 WorkflowManager initialized with task assignment to agent services")
    
    def create_workflow(self, topic: str, description: str, workflow_type: str = "enhanced", test_mode: bool = False) -> str:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = WorkflowState(
            workflow_id=workflow_id,
            topic=topic,
            description=description,
            workflow_type=workflow_type,
            test_mode=test_mode
        )
        
        # Initialize stage statuses
        for stage in workflow.stages:
            workflow.stage_statuses[stage] = StageStatusEnum.PENDING
        
        self.workflows[workflow_id] = workflow
        
        logger.info(f"📋 Created workflow {workflow_id}: {topic} (test_mode: {test_mode})")
        return workflow_id
    
    async def execute_workflow_with_agents(self, workflow_id: str):
        """Execute workflow by assigning tasks to agent services"""
        try:
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatusEnum.RUNNING
            workflow.updated_at = time.time()
            
            logger.info(f"🚀 Starting workflow execution with agent services: {workflow_id}")
            logger.info(f"📝 Topic: {workflow.topic}")
            logger.info(f"📋 Stages: {workflow.stages}")
            
            # Execute stages sequentially by assigning tasks to agents
            for stage_index, stage_name in enumerate(workflow.stages):
                try:
                    logger.info(f"🔄 Assigning task to agent {stage_index + 1}/{len(workflow.stages)}: {stage_name}")
                    
                    # Update workflow state
                    workflow.current_stage = stage_index
                    workflow.stage_statuses[stage_name] = StageStatusEnum.RUNNING
                    workflow.stage_times[stage_name] = {"start": time.time()}
                    workflow.updated_at = time.time()
                    
                    # Check if compression is needed before this stage
                    if self._should_compress_context(stage_name, workflow):
                        logger.info(f"🗜️ Context size large, triggering optional compression before {stage_name}")
                        try:
                            compression_result = await self._assign_compression_task(workflow_id, f"compression_before_{stage_name}", workflow)
                            # Store compression result for later use with isolation
                            isolated_compression_result = self._isolate_stage_result(workflow_id, f"compression_before_{stage_name}", compression_result)
                            workflow.stage_results[f"compression_before_{stage_name}"] = isolated_compression_result
                            logger.info(f"✅ Compression completed successfully before {stage_name}")
                        except Exception as e:
                            logger.warning(f"⚠️ Compression failed before {stage_name}, continuing with full context: {str(e)}")
                    
                    # Assign task to agent service
                    result = await self._assign_task_to_agent(workflow_id, stage_name, workflow)
                    
                    # Update stage result with workflow isolation
                    isolated_result = self._isolate_stage_result(workflow_id, stage_name, result)
                    workflow.stage_results[stage_name] = isolated_result
                    workflow.stage_statuses[stage_name] = StageStatusEnum.COMPLETED
                    workflow.stage_times[stage_name]["end"] = time.time()
                    workflow.updated_at = time.time()
                    
                    logger.info(f"✅ Stage {stage_name} completed by agent service")
                    
                except Exception as e:
                    logger.error(f"❌ Stage {stage_name} failed: {str(e)}")
                    workflow.stage_statuses[stage_name] = StageStatusEnum.FAILED
                    workflow.errors[stage_name] = str(e)
                    workflow.status = WorkflowStatusEnum.FAILED
                    workflow.updated_at = time.time()
                    return
            
            # All stages completed
            workflow.status = WorkflowStatusEnum.COMPLETED
            workflow.updated_at = time.time()
            logger.info(f"🎉 Workflow {workflow_id} completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Workflow {workflow_id} execution failed: {str(e)}")
            if workflow_id in self.workflows:
                self.workflows[workflow_id].status = WorkflowStatusEnum.FAILED
                self.workflows[workflow_id].updated_at = time.time()
    
    async def _assign_compression_task(self, workflow_id: str, stage_name: str, workflow: WorkflowState) -> Dict[str, Any]:
        """Assign compression task to compression agent with workflow isolation"""
        try:
            agent_url = AGENT_SERVICES.get("compressor")  # Use compression agent URL
            
            # Validate workflow ID and ensure context isolation
            if workflow.workflow_id != workflow_id:
                raise Exception(f"Workflow ID mismatch: expected {workflow_id}, got {workflow.workflow_id}")
            
            # Determine compression context based on stage
            compression_context = self._prepare_compression_context(stage_name, workflow)
            
            # Add workflow isolation to compression context
            compression_context["workflow_id"] = workflow_id
            compression_context["isolation_level"] = "workflow_specific"
            compression_context["context_timestamp"] = time.time()
            
            # Prepare task data for compression with workflow isolation
            task_data = {
                "task_id": f"{workflow_id}_{stage_name}_{int(time.time())}",  # Add timestamp for uniqueness
                "workflow_id": workflow_id,  # Ensure workflow ID is passed
                "stage_name": stage_name,
                "topic": workflow.topic,
                "description": workflow.description,
                "previous_results": self._isolate_workflow_results(workflow_id, workflow.stage_results),
                "context": compression_context
            }
            
            logger.info(f"🗜️ Assigning compression task to compression agent at {agent_url}")
            logger.info(f"📋 Compression context: {compression_context}")
            
            # Send task to compression agent service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{agent_url}/execute",
                    json=task_data,
                    timeout=300.0  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Compression agent completed task successfully")
                    return result
                else:
                    error_msg = f"Compression agent failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"❌ Failed to assign compression task: {str(e)}")
            raise
    
    def _should_compress_context(self, stage_name: str, workflow: WorkflowState) -> bool:
        """Intelligently decide if compression is needed before a stage"""
        # Calculate current context size
        context_size = len(str(workflow.stage_results))
        
        # Define compression thresholds
        COMPRESSION_THRESHOLDS = {
            "drafting": 8000,  # Compress before drafting if context > 8KB
            "review": 12000,   # Compress before review if context > 12KB
            "rewrite": 15000   # Compress before rewrite if context > 15KB
        }
        
        threshold = COMPRESSION_THRESHOLDS.get(stage_name, float('inf'))
        
        if context_size > threshold:
            logger.info(f"📊 Context size {context_size} exceeds threshold {threshold} for {stage_name}")
            return True
        
        return False
    
    def _prepare_compression_context(self, stage_name: str, workflow: WorkflowState) -> Dict[str, Any]:
        """Prepare compression context based on stage"""
        # Extract stage name from compression stage name
        target_stage = stage_name.replace("compression_before_", "")
        
        if target_stage == "drafting":
            # Compress before drafting - focus on planning, search, discussion
            return {
                "compression_target": "early_stages",
                "stages_to_compress": ["planning", "search", "discussion"],
                "compression_purpose": "prepare_for_drafting",
                "preserve_elements": ["core_strategy", "key_insights", "critical_findings"],
                "target_stage": target_stage
            }
        elif target_stage == "review":
            # Compress before review - focus on all previous stages
            return {
                "compression_target": "all_stages",
                "stages_to_compress": ["planning", "search", "discussion", "drafting"],
                "compression_purpose": "prepare_for_review",
                "preserve_elements": ["core_strategy", "key_insights", "critical_findings", "draft_summary"],
                "target_stage": target_stage
            }
        elif target_stage == "rewrite":
            # Compress before rewrite - focus on all previous stages
            return {
                "compression_target": "all_stages",
                "stages_to_compress": ["planning", "search", "discussion", "drafting", "review"],
                "compression_purpose": "prepare_for_rewrite",
                "preserve_elements": ["core_strategy", "key_insights", "critical_findings", "draft_summary", "review_feedback"],
                "target_stage": target_stage
            }
        else:
            return {
                "compression_target": "unknown",
                "stages_to_compress": [],
                "compression_purpose": "general",
                "preserve_elements": [],
                "target_stage": target_stage
            }
    
    async def _assign_task_to_agent(self, workflow_id: str, stage_name: str, workflow: WorkflowState) -> Dict[str, Any]:
        """Assign task to agent service with workflow context isolation"""
        try:
            agent_url = AGENT_SERVICES.get(stage_name)
            if not agent_url:
                raise Exception(f"Agent service not found for stage: {stage_name}")
            
            # Validate workflow ID and ensure context isolation
            if workflow.workflow_id != workflow_id:
                raise Exception(f"Workflow ID mismatch: expected {workflow_id}, got {workflow.workflow_id}")
            
            # Create isolated context for this specific workflow
            isolated_context = self._create_isolated_context(workflow_id, workflow, stage_name)
            
            # Prepare task data with workflow isolation
            task_data = {
                "task_id": f"{workflow_id}_{stage_name}_{int(time.time())}",  # Add timestamp for uniqueness
                "workflow_id": workflow_id,  # Ensure workflow ID is passed
                "stage_name": stage_name,
                "topic": workflow.topic,
                "description": workflow.description,
                "test_mode": workflow.test_mode,  # Add test mode to task data
                "previous_results": self._isolate_workflow_results(workflow_id, workflow.stage_results),
                "context": isolated_context
            }
            
            logger.info(f"📤 Assigning task to {stage_name} agent for workflow {workflow_id}")
            logger.info(f"🔒 Using isolated context for workflow {workflow_id}")
            
            # Send task to agent service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{agent_url}/execute",
                    json=task_data,
                    timeout=300.0  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Validate that the response belongs to the correct workflow
                    if result.get("workflow_id") != workflow_id:
                        logger.warning(f"⚠️ Response workflow ID mismatch: expected {workflow_id}, got {result.get('workflow_id')}")
                    
                    logger.info(f"✅ Agent {stage_name} completed task successfully for workflow {workflow_id}")
                    return result
                else:
                    error_msg = f"Agent {stage_name} failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"❌ Failed to assign task to agent {stage_name} for workflow {workflow_id}: {str(e)}")
            raise
    
    def _create_isolated_context(self, workflow_id: str, workflow: WorkflowState, stage_name: str) -> Dict[str, Any]:
        """Create isolated context for a specific workflow"""
        return {
            "workflow_id": workflow_id,  # Include workflow ID in context
            "workflow_type": workflow.workflow_type,
            "current_stage": workflow.current_stage,
            "total_stages": len(workflow.stages),
            "stage_name": stage_name,
            "isolation_level": "workflow_specific",
            "context_timestamp": time.time(),
            "workflow_created_at": workflow.created_at,
            "workflow_updated_at": workflow.updated_at
        }
    
    def _isolate_workflow_results(self, workflow_id: str, stage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Isolate workflow results to prevent cross-contamination"""
        isolated_results = {}
        
        for stage_name, stage_result in stage_results.items():
            # Add workflow ID to each stage result for isolation
            if isinstance(stage_result, dict):
                isolated_stage_result = stage_result.copy()
                isolated_stage_result["workflow_id"] = workflow_id
                isolated_stage_result["isolation_timestamp"] = time.time()
                isolated_results[stage_name] = isolated_stage_result
            else:
                isolated_results[stage_name] = {
                    "workflow_id": workflow_id,
                    "result": stage_result,
                    "isolation_timestamp": time.time()
                }
        
        return isolated_results
    
    def _isolate_stage_result(self, workflow_id: str, stage_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Isolate a single stage result with workflow ID"""
        isolated_result = result.copy() if isinstance(result, dict) else {"result": result}
        
        # Ensure workflow ID is included
        isolated_result["workflow_id"] = workflow_id
        isolated_result["stage_name"] = stage_name
        isolated_result["isolation_timestamp"] = time.time()
        isolated_result["isolation_level"] = "workflow_specific"
        
        return isolated_result
    
    def get_workflow_status(self, workflow_id: str) -> WorkflowStatus:
        """Get workflow status"""
        if workflow_id not in self.workflows:
            raise KeyError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        # Build stage information
        stages = []
        for stage_name in workflow.stages:
            stage_info = StageInfo(
                name=stage_name,
                status=workflow.stage_statuses.get(stage_name, StageStatusEnum.PENDING),
                start_time=workflow.stage_times.get(stage_name, {}).get("start"),
                end_time=workflow.stage_times.get(stage_name, {}).get("end"),
                result=workflow.stage_results.get(stage_name),
                error=workflow.errors.get(stage_name)
            )
            stages.append(stage_info)
        
        # Calculate progress
        completed_stages = sum(1 for stage in stages if stage.status == StageStatusEnum.COMPLETED)
        progress = (completed_stages / len(stages)) * 100 if stages else 0
        
        return WorkflowStatus(
            workflow_id=workflow.workflow_id,
            topic=workflow.topic,
            status=workflow.status,
            test_mode=workflow.test_mode,
            current_stage=workflow.current_stage,
            total_stages=len(workflow.stages),
            progress=progress,
            stages=stages,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )
    
    def get_workflow_results(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow results"""
        if workflow_id not in self.workflows:
            raise KeyError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        return workflow.stage_results
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows"""
        workflows = []
        for workflow_id, workflow in self.workflows.items():
            workflows.append({
                "workflow_id": workflow_id,
                "topic": workflow.topic,
                "status": workflow.status,
                "test_mode": workflow.test_mode,
                "workflow_type": workflow.workflow_type,
                "current_stage": workflow.current_stage,
                "total_stages": len(workflow.stages),
                "created_at": workflow.created_at,
                "updated_at": workflow.updated_at
            })
        return workflows
    
    def reset_workflow(self, workflow_id: str):
        """Reset a workflow to start over"""
        if workflow_id not in self.workflows:
            raise KeyError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatusEnum.PENDING
        workflow.current_stage = 0
        workflow.stage_results.clear()
        workflow.stage_statuses.clear()
        workflow.stage_times.clear()
        workflow.errors.clear()
        workflow.updated_at = time.time()
        
        # Reset stage statuses
        for stage in workflow.stages:
            workflow.stage_statuses[stage] = StageStatusEnum.PENDING
        
        logger.info(f"🔄 Reset workflow {workflow_id}")
    
    def delete_workflow(self, workflow_id: str):
        """Delete a workflow"""
        if workflow_id not in self.workflows:
            raise KeyError(f"Workflow {workflow_id} not found")
        
        del self.workflows[workflow_id]
        logger.info(f"🗑️ Deleted workflow {workflow_id}")