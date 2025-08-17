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
    "rewrite": "http://localhost:8000/agents/rewriter"
}

class WorkflowManager:
    """Task assignment workflow manager"""
    
    def __init__(self):
        # In-memory storage
        self.workflows: Dict[str, WorkflowState] = {}
        self.test_mode = TestModeConfig(enabled=True)
        
        logger.info("🚀 WorkflowManager initialized with task assignment to agent services")
    
    def create_workflow(self, topic: str, description: str, workflow_type: str = "enhanced") -> str:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = WorkflowState(
            workflow_id=workflow_id,
            topic=topic,
            description=description,
            workflow_type=workflow_type
        )
        
        # Initialize stage statuses
        for stage in workflow.stages:
            workflow.stage_statuses[stage] = StageStatusEnum.PENDING
        
        self.workflows[workflow_id] = workflow
        
        logger.info(f"📋 Created workflow {workflow_id}: {topic}")
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
                    
                    # Assign task to agent service
                    result = await self._assign_task_to_agent(workflow_id, stage_name, workflow)
                    
                    # Update stage result
                    workflow.stage_results[stage_name] = result
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
    
    async def _assign_task_to_agent(self, workflow_id: str, stage_name: str, workflow: WorkflowState) -> Dict[str, Any]:
        """Assign task to agent service"""
        try:
            agent_url = AGENT_SERVICES.get(stage_name)
            if not agent_url:
                raise Exception(f"Agent service not found for stage: {stage_name}")
            
            # Prepare task data
            task_data = {
                "task_id": f"{workflow_id}_{stage_name}",
                "workflow_id": workflow_id,
                "stage_name": stage_name,
                "topic": workflow.topic,
                "description": workflow.description,
                "previous_results": workflow.stage_results,
                "context": {
                    "workflow_type": workflow.workflow_type,
                    "current_stage": workflow.current_stage,
                    "total_stages": len(workflow.stages)
                }
            }
            
            logger.info(f"📤 Assigning task to {stage_name} agent at {agent_url}")
            logger.info(f"📋 Task data: {task_data}")
            
            # Send task to agent service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{agent_url}/execute",
                    json=task_data,
                    timeout=300.0  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Agent {stage_name} completed task successfully")
                    return result
                else:
                    error_msg = f"Agent {stage_name} failed with status {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"❌ Failed to assign task to agent {stage_name}: {str(e)}")
            raise
    
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