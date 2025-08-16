#!/usr/bin/env python3
"""
Test system start to see if planner agent is created
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_system_start():
    """Test system start to see if planner agent is created"""
    try:
        logger.info("🚀 Testing system start")
        
        # Create system
        system = PatentAgentSystem(test_mode=False)
        logger.info("✅ System created")
        
        # Start system
        await system.start()
        logger.info("✅ System started")
        
        # Check agents
        logger.info(f"Agents in system: {list(system.agents.keys())}")
        
        # Check message bus agents
        broker = system.message_bus_config.broker
        logger.info(f"Agents in broker: {list(broker.agents.keys())}")
        
        # Check if planner agent exists
        if "planner_agent" in system.agents:
            logger.info("✅ Planner agent exists in system")
        else:
            logger.error("❌ Planner agent missing from system")
            
        if "planner_agent" in broker.agents:
            logger.info("✅ Planner agent exists in broker")
        else:
            logger.error("❌ Planner agent missing from broker")
            
        # Wait a bit to see message loops
        logger.info("Waiting 5 seconds to see message loops...")
        await asyncio.sleep(5)
        
        # Stop system
        await system.stop()
        logger.info("✅ System stopped")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_system_start())