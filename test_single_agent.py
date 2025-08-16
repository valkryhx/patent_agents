#!/usr/bin/env python3
"""
Test script to verify single agent test mode
"""

import asyncio
import logging
from patent_agent_demo.agents.searcher_agent import SearcherAgent
from patent_agent_demo.message_bus import message_bus_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_single_agent():
    """Test single agent in test mode"""
    try:
        logger.info("Starting single agent test...")
        
        # Initialize message bus
        await message_bus_config.initialize()
        
        # Create searcher agent in test mode
        searcher = SearcherAgent(test_mode=True)
        
        # Start the agent
        await searcher.start()
        logger.info("Searcher agent started successfully")
        
        # Wait a bit for agent to initialize
        await asyncio.sleep(2)
        
        # Test task data
        task_data = {
            "id": "test_task_123",
            "type": "prior_art_search",
            "topic": "测试专利主题",
            "description": "测试专利描述"
        }
        
        # Execute the task
        logger.info(f"Executing task: {task_data['id']}")
        result = await searcher._execute_test_task(task_data)
        
        logger.info(f"Task result: success={result.success}")
        if result.success:
            logger.info(f"Data keys: {list(result.data.keys())}")
        else:
            logger.error(f"Error: {result.error_message}")
        
        # Stop the agent
        await searcher.stop()
        logger.info("Searcher agent stopped successfully")
        
        # Shutdown message bus
        await message_bus_config.shutdown()
        
        return result.success
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_single_agent())
    print(f"\n=== TEST RESULT: {'SUCCESS' if success else 'FAILED'} ===")