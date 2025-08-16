#!/usr/bin/env python3
"""
Test script to verify the complete workflow using test mode
"""

import asyncio
import logging
from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_complete_workflow():
    """Test the complete workflow using test mode"""
    try:
        logger.info("Starting complete workflow test in TEST MODE...")
        
        # Create and start system in test mode
        system = PatentAgentSystem(test_mode=True)
        await system.start()
        logger.info("System started successfully in TEST MODE")
        
        # Wait for agents to initialize
        await asyncio.sleep(3)
        
        # Start a patent workflow
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种能够智能处理多参数工具调用的系统"
        
        logger.info(f"Starting workflow for topic: {topic}")
        workflow_id = await system.execute_workflow(topic, description)
        logger.info(f"Workflow started with ID: {workflow_id}")
        
        # Monitor workflow progress
        max_wait_time = 60  # 60 seconds max
        check_interval = 5  # Check every 5 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            # Get workflow status
            workflow = system.coordinator.active_workflows.get(workflow_id)
            if workflow:
                logger.info(f"Workflow status: {workflow.overall_status}")
                logger.info(f"Current stage: {workflow.current_stage}")
                logger.info(f"Completed stages: {len([s for s in workflow.stages if s.status == 'completed'])}")
                
                # Check if workflow is complete
                if workflow.overall_status in ["completed", "error", "failed"]:
                    logger.info(f"Workflow finished with status: {workflow.overall_status}")
                    break
            else:
                logger.warning("Workflow not found")
                break
                
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
        
        # Get final results
        if workflow:
            logger.info("=== FINAL WORKFLOW RESULTS ===")
            logger.info(f"Overall status: {workflow.overall_status}")
            logger.info(f"Total stages: {len(workflow.stages)}")
            
            for i, stage in enumerate(workflow.stages):
                logger.info(f"Stage {i}: {getattr(stage, 'name', 'Unknown')} - {stage.status}")
                if stage.status == "completed" and stage.result:
                    logger.info(f"  Result type: {type(stage.result)}")
                    if hasattr(stage.result, 'data'):
                        logger.info(f"  Data keys: {list(stage.result.data.keys()) if isinstance(stage.result.data, dict) else 'Not a dict'}")
        
        # Stop system
        await system.stop()
        logger.info("System stopped successfully")
        
        return workflow.overall_status if workflow else "unknown"
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "error"

if __name__ == "__main__":
    result = asyncio.run(test_complete_workflow())
    print(f"\n=== TEST RESULT: {result} ===")