#!/usr/bin/env python3
"""
Test planner agent import and creation
"""

import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_planner_import():
    """Test if planner agent can be imported and created"""
    try:
        logger.info("🚀 Testing planner agent import")
        
        # Try to import planner agent
        from patent_agent_demo.agents.planner_agent import PlannerAgent
        logger.info("✅ Planner agent imported successfully")
        
        # Try to create planner agent
        planner = PlannerAgent(test_mode=False)
        logger.info("✅ Planner agent created successfully")
        
        # Check planner agent attributes
        logger.info(f"Planner agent name: {planner.name}")
        logger.info(f"Planner agent capabilities: {planner.capabilities}")
        logger.info(f"Planner agent status: {planner.status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_planner_import()
    if success:
        print("✅ Planner agent import test passed")
    else:
        print("❌ Planner agent import test failed")