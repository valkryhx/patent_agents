#!/usr/bin/env python3
"""
Test real search functionality (non-test mode)
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

async def test_real_search():
    """Test real search functionality"""
    try:
        logger.info("🚀 Testing real search functionality")
        
        # Create searcher agent in REAL mode (not test mode)
        searcher = SearcherAgent(test_mode=False)
        await searcher.start()
        logger.info("✅ Searcher agent started in REAL mode")
        
        # Test data
        task_data = {
            "type": "prior_art_search",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
        }
        
        # Time the search
        start_time = time.time()
        logger.info("⏱️ Starting real search...")
        
        result = await searcher.execute_task(task_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"⏱️ Real search completed in {duration:.2f} seconds")
        
        if result.success:
            logger.info("✅ Real search successful")
            
            # Check different result fields
            search_report = result.data.get('search_report')
            if search_report:
                logger.info(f"📊 Search report results: {len(search_report.results)} items")
                for i, res in enumerate(search_report.results):
                    logger.info(f"  Result {i+1}: {res.title}")
                    logger.info(f"    Abstract: {res.abstract[:100]}...")
                    logger.info(f"    Relevance: {res.relevance_score}")
            else:
                logger.warning("⚠️ No search report in results")
            
            # Check direct results field
            direct_results = result.data.get('results', [])
            logger.info(f"📊 Direct results: {len(direct_results)} items")
            
            # Check prior art count
            prior_art_count = result.data.get('prior_art_count', 0)
            logger.info(f"📊 Prior art count: {prior_art_count}")
            
            logger.info(f"📈 Novelty score: {result.data.get('novelty_score', 'N/A')}")
            logger.info(f"⚠️ Risk level: {result.data.get('risk_level', 'N/A')}")
        else:
            logger.error(f"❌ Real search failed: {result.error_message}")
        
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
    success = asyncio.run(test_real_search())
    if success:
        print("✅ Real search test passed")
    else:
        print("❌ Real search test failed")