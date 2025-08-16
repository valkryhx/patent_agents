#!/usr/bin/env python3
"""
Test script to verify agent availability checking
"""

import asyncio
import logging
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.message_bus import message_bus_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent_availability():
    """Test agent availability checking"""
    try:
        logger.info("Starting agent availability test...")
        
        # Create agents
        coordinator = CoordinatorAgent()
        planner = PlannerAgent()
        
        # Start agents
        await coordinator.start()
        await planner.start()
        logger.info("Both agents started successfully")
        
        # Wait a bit for agents to initialize
        await asyncio.sleep(2)
        
        # Test agent availability
        logger.info("Testing agent availability...")
        
        # Check planner_agent availability
        planner_available = await coordinator._check_agent_availability("planner_agent")
        logger.info(f"planner_agent available: {planner_available}")
        
        # Check searcher_agent availability (should be False since it's not started)
        searcher_available = await coordinator._check_agent_availability("searcher_agent")
        logger.info(f"searcher_agent available: {searcher_available}")
        
        # Check broker agents
        logger.info(f"Broker agents: {list(coordinator.broker.agents.keys())}")
        
        # Stop agents
        await coordinator.stop()
        await planner.stop()
        logger.info("Both agents stopped successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_agent_availability())