#!/usr/bin/env python3
"""
Test script to verify planner_agent functionality
"""

import asyncio
import logging
from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.message_bus import message_bus_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_planner_agent():
    """Test planner agent functionality"""
    try:
        logger.info("Starting planner agent test...")
        
        # Create planner agent
        planner = PlannerAgent()
        
        # Start the agent
        await planner.start()
        logger.info("Planner agent started successfully")
        
        # Test task data
        task_data = {
            "type": "patent_planning",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种能够智能处理多参数工具调用的系统",
            "workflow_id": "test_workflow_123",
            "task": {
                "id": "test_workflow_123_stage_0"
            }
        }
        
        logger.info("Executing patent planning task...")
        
        # Execute task
        result = await planner.execute_task(task_data)
        
        logger.info(f"Task execution result: {result}")
        logger.info(f"Success: {result.success}")
        logger.info(f"Data: {result.data}")
        if result.error_message:
            logger.error(f"Error: {result.error_message}")
        
        # Stop the agent
        await planner.stop()
        logger.info("Planner agent stopped successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_planner_agent())