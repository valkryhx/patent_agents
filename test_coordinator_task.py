#!/usr/bin/env python3
"""
Test coordinator task sending
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.base_agent import TaskResult

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coordinator_task():
    """Test coordinator task sending"""
    try:
        logger.info("🚀 Testing coordinator task sending...")
        
        # Create coordinator agent
        coordinator = CoordinatorAgent()
        await coordinator.start()
        logger.info("✅ Coordinator agent started")
        
        # Test workflow start
        task_data = {
            "type": "start_patent_workflow",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种基于智能分层推理的多参数工具自适应调用系统，通过智能参数推断、分层参数管理、对话式参数收集、参数模板预设和智能参数验证优化等技术，解决大语言模型在调用高参数数量工具时的准确性和精确性问题。"
        }
        
        logger.info("📤 Sending start_patent_workflow task to coordinator")
        result: TaskResult = await coordinator.execute_task(task_data)
        logger.info(f"📥 Coordinator result: {result}")
        
        if result.success:
            workflow_id = result.data.get("workflow_id")
            logger.info(f"✅ Workflow started with ID: {workflow_id}")
            
            # Wait a bit to see if tasks are sent
            await asyncio.sleep(10)
            
            # Check if any tasks were sent
            logger.info(f"📊 Completed tasks: {coordinator.completed_tasks}")
            logger.info(f"📊 Failed tasks: {coordinator.failed_tasks}")
            
            # Check active workflows
            logger.info(f"📊 Active workflows: {list(coordinator.active_workflows.keys())}")
            
            if workflow_id in coordinator.active_workflows:
                workflow = coordinator.active_workflows[workflow_id]
                logger.info(f"📊 Current stage: {workflow.current_stage}")
                logger.info(f"📊 Overall status: {workflow.overall_status}")
                logger.info(f"📊 Stages: {[stage.stage_name for stage in workflow.stages]}")
                
                # Check if first stage was executed
                if workflow.stages:
                    first_stage = workflow.stages[0]
                    logger.info(f"📊 First stage status: {first_stage.status}")
                    logger.info(f"📊 First stage agent: {first_stage.agent_name}")
        else:
            logger.error(f"❌ Failed to start workflow: {result.error_message}")
        
        # Stop coordinator
        await coordinator.stop()
        logger.info("✅ Coordinator stopped")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coordinator_task())