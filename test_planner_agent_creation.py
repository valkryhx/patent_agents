#!/usr/bin/env python3
"""
Test planner agent creation
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.agents.planner_agent import PlannerAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_planner_agent_creation():
    """Test planner agent creation"""
    try:
        logger.info("🚀 Testing planner agent creation")
        
        # Create planner agent
        planner = PlannerAgent(test_mode=False)
        logger.info("✅ Planner agent created")
        
        # Start planner agent
        await planner.start()
        logger.info("✅ Planner agent started")
        
        # Wait a bit to see if it's working
        await asyncio.sleep(5)
        
        # Check if agent is running
        logger.info(f"Agent status: {planner.status}")
        logger.info(f"Agent name: {planner.name}")
        
        # Stop planner agent
        await planner.stop()
        logger.info("✅ Planner agent stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_planner_agent_creation())
    if success:
        print("✅ Planner agent creation test passed")
    else:
        print("❌ Planner agent creation test failed")