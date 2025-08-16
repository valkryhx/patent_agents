#!/usr/bin/env python3
"""
Test script to verify workflow start process
"""

import asyncio
import logging
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.message_bus import message_bus_config
from patent_agent_demo.context_manager import context_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow_start():
    """Test workflow start process"""
    try:
        logger.info("Starting workflow start test...")
        
        # Create agents
        coordinator = CoordinatorAgent()
        planner = PlannerAgent()
        
        # Start agents
        await coordinator.start()
        await planner.start()
        logger.info("Both agents started successfully")
        
        # Wait a bit for agents to initialize
        await asyncio.sleep(2)
        
        # Test context manager initialization
        logger.info("Testing context manager initialization...")
        try:
            workflow_id = "test_workflow_123"
            topic = "基于智能分层推理的多参数工具自适应调用系统"
            description = "一种能够智能处理多参数工具调用的系统"
            
            theme_definition = await context_manager.initialize_workflow_context(workflow_id, topic, description)
            logger.info(f"Context initialized successfully: {theme_definition.primary_title}")
        except Exception as e:
            logger.error(f"Context initialization failed: {e}")
            return
        
        # Test workflow stages creation
        logger.info("Testing workflow stages creation...")
        try:
            stages = await coordinator._create_workflow_stages(topic, description)
            logger.info(f"Workflow stages created: {len(stages)} stages")
            for i, stage in enumerate(stages):
                logger.info(f"Stage {i}: {stage.stage_name} -> {stage.agent_name}")
        except Exception as e:
            logger.error(f"Workflow stages creation failed: {e}")
            return
        
        # Test workflow start
        logger.info("Testing workflow start...")
        try:
            start_result = await coordinator._start_patent_workflow({
                "topic": topic,
                "description": description
            })
            
            logger.info(f"Workflow start result: {start_result}")
            logger.info(f"Success: {start_result.success}")
            
            if start_result.success:
                workflow_id = start_result.data.get("workflow_id")
                logger.info(f"Workflow ID: {workflow_id}")
                
                # Check workflow status
                workflow = coordinator.active_workflows.get(workflow_id)
                if workflow:
                    logger.info(f"Workflow status: {workflow.overall_status}")
                    logger.info(f"Current stage: {workflow.current_stage}")
                    logger.info(f"Number of stages: {len(workflow.stages)}")
                else:
                    logger.error("Workflow not found in active_workflows")
            else:
                logger.error(f"Workflow start failed: {start_result.error_message}")
                
        except Exception as e:
            logger.error(f"Workflow start test failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Stop agents
        await coordinator.stop()
        await planner.stop()
        logger.info("Both agents stopped successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_workflow_start())