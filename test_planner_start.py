#!/usr/bin/env python3
"""
Test planner agent start
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
    """Test if planner agent can start properly"""
    try:
        logger.info("🚀 Testing planner agent start")
        
        # Create planner agent
        planner = PlannerAgent(test_mode=False)
        logger.info("✅ Planner agent created")
        
        # Start planner agent
        await planner.start()
        logger.info("✅ Planner agent started")
        
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
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_planner_start())