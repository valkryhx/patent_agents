#!/usr/bin/env python3
"""
Direct test of workflow start
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
    """Test workflow start directly"""
    try:
        logger.info("🚀 Testing workflow start directly")
        
        # Create system
        system = PatentAgentSystem(test_mode=False)
        logger.info("✅ System created")
        
        # Start system
        await system.start()
        logger.info("✅ System started")
        
        # Start workflow
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种基于智能分层推理的多参数工具自适应调用系统，通过智能参数推断、分层参数管理、对话式参数收集、参数模板预设和智能参数验证优化等技术，解决大语言模型在调用高参数数量工具时的准确性和精确性问题。"
        
        workflow_id = await system.execute_workflow(topic, description)
        logger.info(f"✅ Workflow started with ID: {workflow_id}")
        
        # Wait a bit to see if tasks are sent
        await asyncio.sleep(10)
        
        # Check message queues
        for agent_name in ['planner_agent', 'searcher_agent', 'discusser_agent', 'writer_agent', 'reviewer_agent', 'rewriter_agent']:
            queue_size = system.broker.get_queue_size(agent_name)
            logger.info(f"📊 {agent_name} queue size: {queue_size}")
        
        # Stop system
        await system.stop()
        logger.info("✅ System stopped")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow_start())