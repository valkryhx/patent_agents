#!/usr/bin/env python3
"""
Debug coordinator agent
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coordinator():
    """Test coordinator agent directly"""
    try:
        logger.info("🚀 Testing coordinator agent directly")
        
        # Create coordinator agent
        coordinator = CoordinatorAgent()
        await coordinator.start()
        logger.info("✅ Coordinator agent started")
        
        # Test workflow start
        task_data = {
            "type": "start_patent_workflow",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种基于智能分层推理的多参数工具自适应调用系统，通过智能参数推断、分层参数管理、对话式参数收集、参数模板预设和智能参数验证优化等技术，解决大语言模型在调用高参数数量工具时的准确性和精确性问题。"
        }
        
        logger.info("📤 Sending task to coordinator")
        result = await coordinator.execute_task(task_data)
        logger.info(f"📥 Coordinator result: {result}")
        
        if result.success:
            workflow_id = result.data.get("workflow_id")
            logger.info(f"✅ Workflow started with ID: {workflow_id}")
            
            # Wait a bit to see if tasks are sent
            await asyncio.sleep(5)
            
            # Check message queues
            for agent_name in ['planner_agent', 'searcher_agent', 'discusser_agent', 'writer_agent', 'reviewer_agent', 'rewriter_agent']:
                queue_size = coordinator.broker.get_queue_size(agent_name)
                logger.info(f"📊 {agent_name} queue size: {queue_size}")
        else:
            logger.error(f"❌ Failed to start workflow: {result.error_message}")
        
        # Stop coordinator
        await coordinator.stop()
        logger.info("✅ Coordinator stopped")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_coordinator())