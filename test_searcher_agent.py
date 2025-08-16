#!/usr/bin/env python3
"""
Test script to verify searcher_agent functionality
"""

import asyncio
import logging
from patent_agent_demo.agents.searcher_agent import SearcherAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_searcher_agent():
    """Test searcher agent functionality"""
    try:
        logger.info("Starting searcher agent test...")
        
        # Create searcher agent
        searcher = SearcherAgent()
        
        # Start the agent
        await searcher.start()
        logger.info("Searcher agent started successfully")
        
        # Test task data
        task_data = {
            "type": "prior_art_search",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种能够智能处理多参数工具调用的系统",
            "workflow_id": "test_workflow_123"
        }
        
        logger.info("Executing prior art search task...")
        
        # Execute task
        result = await searcher.execute_task(task_data)
        
        logger.info(f"Task execution result: {result}")
        logger.info(f"Success: {result.success}")
        logger.info(f"Data: {result.data}")
        if result.error_message:
            logger.error(f"Error: {result.error_message}")
        
        # Stop the agent
        await searcher.stop()
        logger.info("Searcher agent stopped successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_searcher_agent())