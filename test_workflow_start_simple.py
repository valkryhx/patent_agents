#!/usr/bin/env python3
"""
Simple test to start workflow
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

async def test_workflow_start():
    """Test workflow start"""
    try:
        logger.info("🚀 Testing workflow start")
        
        # Create system
        system = PatentAgentSystem(test_mode=False)
        logger.info("✅ System created")
        
        # Start system
        await system.start()
        logger.info("✅ System started")
        
        # Wait for agents to initialize
        await asyncio.sleep(3)
        
        # Try to start workflow
        logger.info("Starting workflow...")
        workflow_id = await system.execute_workflow(
            topic="基于智能分层推理的多参数工具自适应调用系统",
            description="一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。",
            workflow_type="enhanced"
        )
        
        logger.info(f"✅ Workflow started with ID: {workflow_id}")
        
        # Wait a bit to see if workflow progresses
        logger.info("Waiting 30 seconds to see workflow progress...")
        await asyncio.sleep(30)
        
        # Get workflow status
        status = await system.get_workflow_status(workflow_id)
        logger.info(f"Workflow status: {status}")
        
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
    success = asyncio.run(test_workflow_start())
    if success:
        print("✅ Workflow start test passed")
    else:
        print("❌ Workflow start test failed")