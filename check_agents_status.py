#!/usr/bin/env python3
"""
Check agents status
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

async def check_agents_status():
    """Check all agents status"""
    try:
        logger.info("🔍 Checking agents status...")
        
        # Create system
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ System started")
        
        # Check message bus
        if system.broker:
            logger.info(f"📡 Message bus status: Active")
            logger.info(f"📊 Available agents: {list(system.broker.agents.keys())}")
            
            # Check each agent
            for agent_name in ['planner_agent', 'searcher_agent', 'discusser_agent', 'writer_agent', 'reviewer_agent', 'rewriter_agent', 'coordinator_agent']:
                agent_info = system.broker.agents.get(agent_name)
                if agent_info:
                    logger.info(f"✅ {agent_name}: {agent_info.status.value}")
                else:
                    logger.warning(f"❌ {agent_name}: Not found")
        else:
            logger.error("❌ Message bus not available")
        
        # Stop system
        await system.stop()
        logger.info("✅ System stopped")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_agents_status())