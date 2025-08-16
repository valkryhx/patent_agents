#!/usr/bin/env python3
"""
Debug script to find why workflow is stuck
"""

import asyncio
import logging
from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_workflow():
    """Debug the workflow to find the issue"""
    try:
        logger.info("Starting workflow debug...")
        
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
        
        # Start a patent workflow
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种能够智能处理多参数工具调用的系统"
        
        logger.info(f"Starting workflow for topic: {topic}")
        workflow_id = await system.execute_workflow(topic, description)
        logger.info(f"Workflow started with ID: {workflow_id}")
        
        # Monitor workflow progress with detailed logging
        max_wait_time = 180  # 3 minutes max
        check_interval = 5   # Check every 5 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            try:
                # Get workflow status
                status_result = await system.coordinator.get_workflow_status(workflow_id)
                workflow = status_result.get("workflow", {})
                
                if workflow:
                    logger.info(f"=== WORKFLOW STATUS UPDATE ({elapsed_time}s) ===")
                    logger.info(f"Overall status: {workflow.overall_status}")
                    logger.info(f"Current stage: {workflow.current_stage}")
                    logger.info(f"Total stages: {len(workflow.stages)}")
                    
                    # Check each stage
                    for i, stage in enumerate(workflow.stages):
                        stage_name = getattr(stage, 'name', f'Stage_{i}')
                        logger.info(f"  Stage {i} ({stage_name}): {stage.status}")
                        if stage.status == "completed" and stage.result:
                            logger.info(f"    Result type: {type(stage.result)}")
                            if hasattr(stage.result, 'data'):
                                data = stage.result.data
                                if isinstance(data, dict):
                                    logger.info(f"    Data keys: {list(data.keys())}")
                                else:
                                    logger.info(f"    Data type: {type(data)}")
                    
                    # Check if workflow is complete
                    if workflow.overall_status in ["completed", "error", "failed"]:
                        logger.info(f"Workflow finished with status: {workflow.overall_status}")
                        break
                        
                    # Check coordinator's task tracking
                    logger.info(f"Coordinator completed_tasks: {system.coordinator.completed_tasks}")
                    logger.info(f"Coordinator failed_tasks: {system.coordinator.failed_tasks}")
                    
                else:
                    logger.warning("Workflow not found")
                    break
                    
            except Exception as e:
                logger.error(f"Error getting workflow status: {e}")
                break
                
            await asyncio.sleep(check_interval)
            elapsed_time += check_interval
        
        # Get final results
        if elapsed_time >= max_wait_time:
            logger.error("Workflow timed out!")
            
        # Stop system
        await system.stop()
        logger.info("System stopped successfully")
        
        return workflow.overall_status if 'workflow' in locals() else "timeout"
        
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "error"

if __name__ == "__main__":
    result = asyncio.run(debug_workflow())
    print(f"\n=== DEBUG RESULT: {result} ===")