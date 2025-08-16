#!/usr/bin/env python3
"""
Test script to verify coordinator behavior only
"""

import asyncio
import logging
import time
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.message_bus import message_bus_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coordinator():
    """Test coordinator behavior"""
    try:
        logger.info("Starting coordinator test...")
        
        # Initialize message bus
        await message_bus_config.initialize()
        
        # Create coordinator agent
        coordinator = CoordinatorAgent()
        
        # Start the agent
        await coordinator.start()
        logger.info("Coordinator agent started successfully")
        
        # Wait a bit for agent to initialize
        await asyncio.sleep(2)
        
        # Test _execute_workflow_stage directly
        logger.info("Testing _execute_workflow_stage...")
        
        # Create a simple workflow
        from patent_agent_demo.agents.coordinator_agent import PatentWorkflow, WorkflowStage
        
        workflow = PatentWorkflow(
            workflow_id="test_workflow_123",
            topic="测试主题",
            description="测试描述",
            stages=[
                WorkflowStage(
                    stage_name="Prior Art Search",
                    agent_name="searcher_agent",
                    status="pending"
                )
            ],
            current_stage=0,
            overall_status="running",
            start_time=time.time()
        )
        
        coordinator.active_workflows["test_workflow_123"] = workflow
        
        # Try to execute stage 0
        logger.info("Executing stage 0...")
        await coordinator._execute_workflow_stage("test_workflow_123", 0)
        
        # Stop the agent
        await coordinator.stop()
        logger.info("Coordinator agent stopped successfully")
        
        # Shutdown message bus
        await message_bus_config.shutdown()
        
        return "success"
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "error"

if __name__ == "__main__":
    result = asyncio.run(test_coordinator())
    print(f"\n=== TEST RESULT: {result} ===")