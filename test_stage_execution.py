#!/usr/bin/env python3
"""
Test script to verify single stage execution
"""

import asyncio
import logging
from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_stage_execution():
    """Test single stage execution"""
    try:
        logger.info("Starting stage execution test...")
        
        # Create and start system in test mode
        system = PatentAgentSystem(test_mode=True)
        await system.start()
        logger.info("System started successfully in TEST MODE")
        
        # Wait for agents to initialize
        await asyncio.sleep(3)
        
        # Check all agents are available
        logger.info("=== CHECKING AGENT AVAILABILITY ===")
        for agent_name, agent in system.agents.items():
            logger.info(f"Agent {agent_name}: {agent.status.value}")
        
        # Test _execute_workflow_stage directly
        logger.info("=== TESTING STAGE EXECUTION ===")
        
        # Create a simple workflow
        from patent_agent_demo.agents.coordinator_agent import PatentWorkflow, WorkflowStage
        import time
        
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
        
        system.coordinator.active_workflows["test_workflow_123"] = workflow
        
        # Try to execute stage 0
        logger.info("Executing stage 0...")
        await system.coordinator._execute_workflow_stage("test_workflow_123", 0)
        
        # Stop system
        await system.stop()
        logger.info("System stopped successfully")
        
        return "success"
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "error"

if __name__ == "__main__":
    result = asyncio.run(test_stage_execution())
    print(f"\n=== TEST RESULT: {result} ===")