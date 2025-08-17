#!/usr/bin/env python3
"""
Workflow Manager - In-Memory Workflow Orchestration
Ultra-simple workflow management without infinite loops
"""

import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
import logging

from models import (
    WorkflowState, WorkflowStatus, StageInfo, 
    WorkflowStatusEnum, StageStatusEnum, TestModeConfig
)
from executors.planning import PlanningExecutor
from executors.search import SearchExecutor
from executors.discussion import DiscussionExecutor
from executors.drafting import DraftingExecutor
from executors.review import ReviewExecutor
from executors.rewrite import RewriteExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowManager:
    """In-memory workflow manager"""
    
    def __init__(self):
        # In-memory storage
        self.workflows: Dict[str, WorkflowState] = {}
        self.test_mode = TestModeConfig(enabled=True)
        
        # Initialize stage executors
        self.executors = {
            "planning": PlanningExecutor(),
            "search": SearchExecutor(),
            "discussion": DiscussionExecutor(),
            "drafting": DraftingExecutor(),
            "review": ReviewExecutor(),
            "rewrite": RewriteExecutor()
        }
        
        logger.info("🚀 WorkflowManager initialized with in-memory storage")
    
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
    
    async def execute_workflow(self, workflow_id: str):
        """Execute a workflow sequentially"""
        try:
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatusEnum.RUNNING
            workflow.updated_at = time.time()
            
            logger.info(f"🚀 Starting workflow execution: {workflow_id}")
            logger.info(f"📝 Topic: {workflow.topic}")
            logger.info(f"📋 Stages: {workflow.stages}")
            
            # Execute stages sequentially
            for stage_index, stage_name in enumerate(workflow.stages):
                try:
                    logger.info(f"🔄 Executing stage {stage_index + 1}/{len(workflow.stages)}: {stage_name}")
                    
                    # Update workflow state
                    workflow.current_stage = stage_index
                    workflow.stage_statuses[stage_name] = StageStatusEnum.RUNNING
                    workflow.stage_times[stage_name] = {"start": time.time()}
                    workflow.updated_at = time.time()
                    
                    # Execute stage
                    result = await self._execute_stage(workflow_id, stage_name, workflow)
                    
                    # Update stage result
                    workflow.stage_results[stage_name] = result
                    workflow.stage_statuses[stage_name] = StageStatusEnum.COMPLETED
                    workflow.stage_times[stage_name]["end"] = time.time()
                    workflow.updated_at = time.time()
                    
                    logger.info(f"✅ Stage {stage_name} completed successfully")
                    
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
    
    async def _execute_stage(self, workflow_id: str, stage_name: str, workflow: WorkflowState) -> Dict[str, Any]:
        """Execute a single stage"""
        try:
            executor = self.executors[stage_name]
            
            # Prepare context
            context = {
                "workflow_id": workflow_id,
                "topic": workflow.topic,
                "description": workflow.description,
                "previous_results": workflow.stage_results,
                "test_mode": self.test_mode.enabled
            }
            
            # Execute stage
            result = await executor.execute(context)
            
            # Add test mode delay if enabled
            if self.test_mode.enabled:
                await asyncio.sleep(self.test_mode.mock_delay)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Stage {stage_name} execution failed: {str(e)}")
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