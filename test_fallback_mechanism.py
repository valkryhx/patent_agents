#!/usr/bin/env python3
"""
Test fallback mechanism from OpenAI to DuckDuckGo
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.openai_client import OpenAIClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_fallback_mechanism():
    """Test fallback mechanism from OpenAI to DuckDuckGo"""
    try:
        logger.info("🚀 Testing fallback mechanism")
        
        # Create OpenAI client
        client = OpenAIClient()
        logger.info("✅ OpenAI client created")
        
        # Test search with fallback
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        keywords = ["人工智能", "机器学习", "工具调用"]
        
        logger.info("🔍 Testing search_prior_art with fallback...")
        
        try:
            results = await client.search_prior_art(topic, keywords, max_results=5)
            logger.info(f"✅ Search completed successfully")
            logger.info(f"📊 Found {len(results)} results")
            
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}: {result.title}")
                logger.info(f"  Abstract: {result.abstract[:100]}...")
                logger.info(f"  Relevance: {result.relevance_score}")
                
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fallback_mechanism())
    if success:
        print("✅ Fallback mechanism test passed")
    else:
        print("❌ Fallback mechanism test failed")