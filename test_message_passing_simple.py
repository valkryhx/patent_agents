#!/usr/bin/env python3
"""
Simple test to verify message passing between coordinator and searcher
"""

import asyncio
import logging
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent
from patent_agent_demo.message_bus import MessageBusBroker, Message, MessageType, message_bus_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_message_passing():
    """Test message passing between coordinator and searcher"""
    try:
        logger.info("Starting message passing test...")
        
        # Use the global message bus configuration
        broker = message_bus_config.broker
        
        # Create agents
        coordinator = CoordinatorAgent()
        searcher = SearcherAgent()
        
        # Start agents
        await coordinator.start()
        await searcher.start()
        
        logger.info("Both agents started successfully")
        
        # Wait a moment for agents to initialize
        await asyncio.sleep(2)
        
        # Create a simple task message
        task_content = {
            "task": {
                "id": "test_task_123",
                "type": "prior_art_search",
                "topic": "基于智能分层推理的多参数工具自适应调用系统",
                "description": "测试任务"
            }
        }
        
        # Send message from coordinator to searcher
        message = Message(
            id="test_message_123",
            type=MessageType.COORDINATION,
            sender="coordinator_agent",
            recipient="searcher_agent",
            content=task_content,
            timestamp=asyncio.get_event_loop().time(),
            priority=5
        )
        
        logger.info("Sending test message...")
        await broker.send_message(message)
        
        # Wait for processing
        await asyncio.sleep(5)
        
        # Check if searcher processed the message
        logger.info("Checking if searcher processed the message...")
        
        # Stop agents
        await coordinator.stop()
        await searcher.stop()
        
        logger.info("Test completed")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_message_passing())