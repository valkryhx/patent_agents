#!/usr/bin/env python3
"""
Test script to verify each workflow stage executes correctly
"""

import asyncio
import logging
from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow_stages():
    """Test that each workflow stage executes correctly"""
    try:
        logger.info("Starting workflow stages test...")
        
        # Create and start system
        system = PatentAgentSystem()
        await system.start()
        logger.info("System started successfully")
        
        # Wait for agents to initialize
        await asyncio.sleep(3)
        
        # Test each stage individually
        stages = [
            ("planner_agent", "patent_planning"),
            ("searcher_agent", "prior_art_search"),
            ("discusser_agent", "innovation_discussion"),
            ("writer_agent", "patent_drafting"),
            ("reviewer_agent", "patent_review"),
            ("rewriter_agent", "patent_rewrite")
        ]
        
        for agent_name, task_type in stages:
            logger.info(f"Testing {agent_name} with task type {task_type}")
            
            # Check agent availability
            available = await system.coordinator._check_agent_availability(agent_name)
            if not available:
                logger.error(f"❌ {agent_name} is not available")
                continue
                
            logger.info(f"✅ {agent_name} is available")
            
            # Test task execution
            try:
                task_content = {
                    "task": {
                        "id": f"test_{agent_name}_{task_type}",
                        "type": task_type,
                        "workflow_id": "test_workflow",
                        "stage_index": 0,
                        "topic": "测试主题",
                        "description": "测试描述",
                        "previous_results": {},
                        "context": {}
                    }
                }
                
                # Send task and wait for completion
                success = await system.coordinator._send_task_message(agent_name, task_content)
                if success:
                    logger.info(f"✅ {agent_name} task completed successfully")
                else:
                    logger.error(f"❌ {agent_name} task failed")
                    
            except Exception as e:
                logger.error(f"❌ Error testing {agent_name}: {e}")
        
        # Stop system
        await system.stop()
        logger.info("System stopped successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_workflow_stages())