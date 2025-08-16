#!/usr/bin/env python3
"""
Test script to verify all agents are started correctly
"""

import asyncio
import logging
from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_all_agents():
    """Test that all agents are started correctly"""
    try:
        logger.info("Starting all agents test...")
        
        # Create and start system
        system = PatentAgentSystem()
        await system.start()
        logger.info("System started successfully")
        
        # Wait a bit for agents to initialize
        await asyncio.sleep(3)
        
        # Check all agents
        expected_agents = [
            "planner_agent",
            "searcher_agent", 
            "discusser_agent",
            "writer_agent",
            "reviewer_agent",
            "rewriter_agent",
            "coordinator_agent"
        ]
        
        logger.info("Checking all agents...")
        for agent_name in expected_agents:
            if agent_name in system.agents:
                agent = system.agents[agent_name]
                logger.info(f"✅ {agent_name}: Found in system.agents")
                
                # Check if agent is in message bus
                if agent_name in system.message_bus_config.broker.agents:
                    broker_agent = system.message_bus_config.broker.agents[agent_name]
                    logger.info(f"✅ {agent_name}: Found in message bus (status: {broker_agent.status.value})")
                else:
                    logger.warning(f"⚠️ {agent_name}: Not found in message bus")
            else:
                logger.error(f"❌ {agent_name}: Not found in system.agents")
        
        # Check message bus agents
        logger.info(f"Message bus agents: {list(system.message_bus_config.broker.agents.keys())}")
        
        # Stop system
        await system.stop()
        logger.info("System stopped successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_all_agents())