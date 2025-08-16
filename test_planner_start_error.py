#!/usr/bin/env python3
"""
Test planner agent start to catch any errors
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

async def test_planner_start():
    """Test planner agent start and catch any errors"""
    try:
        logger.info("🚀 Testing planner agent start")
        
        # Create planner agent
        planner = PlannerAgent(test_mode=False)
        logger.info("✅ Planner agent created")
        
        # Try to start planner agent
        logger.info("Starting planner agent...")
        await planner.start()
        logger.info("✅ Planner agent started successfully")
        
        # Check if agent is registered in message bus
        broker = planner.broker
        logger.info(f"Available agents in broker: {list(broker.agents.keys())}")
        
        # Check planner agent status
        planner_info = broker.agents.get("planner_agent")
        if planner_info:
            logger.info(f"Planner agent status: {planner_info.status.value}")
        else:
            logger.error("❌ Planner agent not found in broker agents")
            
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
    success = asyncio.run(test_planner_start())
    if success:
        print("✅ Planner agent start test passed")
    else:
        print("❌ Planner agent start test failed")