#!/usr/bin/env python3
"""
Test system start with error catching to see why planner agent is missing
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

async def test_system_start_with_error_catching():
    """Test system start and catch any errors during agent startup"""
    try:
        logger.info("🚀 Testing system start with error catching")
        
        # Create system
        system = PatentAgentSystem(test_mode=False)
        logger.info("✅ System created")
        
        # Start system with detailed error catching
        try:
            logger.info("Starting Patent Agent System...")
            
            # Initialize Message Bus
            await system.message_bus_config.initialize()
            logger.info("✅ Message bus initialized")
            
            # Create and start agents with individual error catching
            logger.info("Creating agents...")
            from patent_agent_demo.agents.planner_agent import PlannerAgent
            from patent_agent_demo.agents.searcher_agent import SearcherAgent
            from patent_agent_demo.agents.discusser_agent import DiscusserAgent
            from patent_agent_demo.agents.writer_agent import WriterAgent
            from patent_agent_demo.agents.reviewer_agent import ReviewerAgent
            from patent_agent_demo.agents.rewriter_agent import RewriterAgent
            from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
            
            system.agents = {
                "planner_agent": PlannerAgent(test_mode=system.test_mode),
                "searcher_agent": SearcherAgent(test_mode=system.test_mode),
                "discusser_agent": DiscusserAgent(test_mode=system.test_mode),
                "writer_agent": WriterAgent(test_mode=system.test_mode),
                "reviewer_agent": ReviewerAgent(test_mode=system.test_mode),
                "rewriter_agent": RewriterAgent(test_mode=system.test_mode),
                "coordinator_agent": CoordinatorAgent()
            }
            logger.info("✅ Agents created")
            
            # Start all agents with individual error catching
            logger.info("Starting agents individually...")
            for agent_name, agent in system.agents.items():
                try:
                    logger.info(f"Starting {agent_name}...")
                    await agent.start()
                    logger.info(f"✅ Agent {agent_name} started successfully")
                except Exception as e:
                    logger.error(f"❌ Error starting agent {agent_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    
            # Set coordinator reference
            system.coordinator = system.agents["coordinator_agent"]
            logger.info("✅ Coordinator reference set")
            
            # Wait for all agents to fully initialize their message processing loops
            logger.info("Waiting for all agents to initialize message processing loops...")
            await asyncio.sleep(2)  # Give agents time to start their message loops
            
            logger.info("All agents started successfully")
            logger.info("Patent Agent System started successfully")
            
        except Exception as e:
            logger.error(f"❌ Error starting Patent Agent System: {e}")
            import traceback
            traceback.print_exc()
            raise
            
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
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_system_start_with_error_catching())
    if success:
        print("✅ System start test passed")
    else:
        print("❌ System start test failed")