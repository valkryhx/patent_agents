#!/usr/bin/env python3
"""
Test system agents creation
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

async def test_system_agents():
    """Test if all agents are created and started properly"""
    try:
        logger.info("🚀 Testing system agents creation")
        
        # Create system
        system = PatentAgentSystem(test_mode=False)
        logger.info("✅ System created")
        
        # Start system
        await system.start()
        logger.info("✅ System started")
        
        # Check agents
        logger.info(f"Agents in system: {list(system.agents.keys())}")
        
        # Check if planner agent exists
        if "planner_agent" in system.agents:
            logger.info("✅ Planner agent exists in system")
            planner = system.agents["planner_agent"]
            logger.info(f"Planner agent status: {planner.status}")
            logger.info(f"Planner agent name: {planner.name}")
        else:
            logger.error("❌ Planner agent missing from system")
            
        # Check message bus agents
        broker = system.message_bus_config.broker
        logger.info(f"Agents in broker: {list(broker.agents.keys())}")
        
        # Check if planner agent exists in broker
        if "planner_agent" in broker.agents:
            logger.info("✅ Planner agent exists in broker")
            planner_info = broker.agents["planner_agent"]
            logger.info(f"Planner agent status: {planner_info.status.value}")
        else:
            logger.error("❌ Planner agent missing from broker")
            
        # Wait a bit to see message loops
        logger.info("Waiting 5 seconds to see message loops...")
        await asyncio.sleep(5)
        
        # Stop system
        await system.stop()
        logger.info("✅ System stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_system_agents())
    if success:
        print("✅ System agents test passed")
    else:
        print("❌ System agents test failed")