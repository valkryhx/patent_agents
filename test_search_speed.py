#!/usr/bin/env python3
"""
Test search speed and functionality
"""

import asyncio
import sys
import os
import logging
import time

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.agents.searcher_agent import SearcherAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search_speed():
    """Test search speed"""
    try:
        logger.info("🚀 Testing search speed")
        
        # Create searcher agent in test mode
        searcher = SearcherAgent(test_mode=True)
        await searcher.start()
        logger.info("✅ Searcher agent started")
        
        # Test data
        task_data = {
            "type": "prior_art_search",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
        }
        
        # Time the search
        start_time = time.time()
        logger.info("⏱️ Starting search...")
        
        result = await searcher.execute_task(task_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"⏱️ Search completed in {duration:.2f} seconds")
        
        if result.success:
            logger.info("✅ Search successful")
            logger.info(f"📊 Results: {len(result.data.get('results', []))} items")
            logger.info(f"📈 Novelty score: {result.data.get('novelty_score', 'N/A')}")
        else:
            logger.error(f"❌ Search failed: {result.error_message}")
        
        # Stop agent
        await searcher.stop()
        logger.info("✅ Searcher agent stopped")
        
        return result.success
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_search_speed())
    if success:
        print("✅ Search speed test passed")
    else:
        print("❌ Search speed test failed")