#!/usr/bin/env python3
"""
Test script to verify message passing between coordinator and planner
"""

import asyncio
import logging
import time
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.message_bus import message_bus_config, Message, MessageType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coordinator_planner():
    """Test message passing between coordinator and planner"""
    try:
        logger.info("Starting coordinator-planner test...")
        
        # Create agents
        coordinator = CoordinatorAgent()
        planner = PlannerAgent()
        
        # Start agents
        await coordinator.start()
        await planner.start()
        logger.info("Both agents started successfully")
        
        # Wait a bit for agents to initialize
        await asyncio.sleep(2)
        
        # Start a workflow
        logger.info("Starting workflow...")
        start_result = await coordinator.execute_task({
            "type": "start_patent_workflow",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种能够智能处理多参数工具调用的系统"
        })
        
        logger.info(f"Workflow start result: {start_result}")
        logger.info(f"Success: {start_result.success}")
        
        if start_result.success:
            workflow_id = start_result.data.get("workflow_id")
            logger.info(f"Workflow ID: {workflow_id}")
            
            # Wait for workflow to complete or timeout
            timeout = 60  # 60 seconds timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check workflow status
                status_result = await coordinator.execute_task({
                    "type": "get_workflow_summary",
                    "workflow_id": workflow_id
                })
                
                if status_result.success:
                    workflow_data = status_result.data
                    overall_status = workflow_data.get("overall_status", "unknown")
                    current_stage = workflow_data.get("current_stage", -1)
                    
                    logger.info(f"Workflow status: {overall_status}, current stage: {current_stage}")
                    
                    if overall_status in ["completed", "error"]:
                        logger.info("Workflow finished")
                        break
                
                await asyncio.sleep(5)  # Check every 5 seconds
            
            logger.info("Test completed")
        else:
            logger.error(f"Failed to start workflow: {start_result.error_message}")
        
        # Stop agents
        await coordinator.stop()
        await planner.stop()
        logger.info("Both agents stopped successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_coordinator_planner())