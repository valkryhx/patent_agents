#!/usr/bin/env python3
"""
Test planner agent message reception
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.message_bus import MessageType, Message
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_planner_message():
    """Test if planner agent can receive messages"""
    try:
        logger.info("🚀 Starting planner agent message test")
        
        # Create planner agent
        planner = PlannerAgent(test_mode=False)
        await planner.start()
        
        logger.info("✅ Planner agent started successfully")
        
        # Wait for agent to initialize
        await asyncio.sleep(2)
        
        # Check if agent is registered in message bus
        broker = planner.broker
        logger.info(f"Available agents in broker: {list(broker.agents.keys())}")
        logger.info(f"Available message queues: {list(broker.message_queues.keys())}")
        
        # Check planner agent status
        planner_info = broker.agents.get("planner_agent")
        if planner_info:
            logger.info(f"Planner agent status: {planner_info.status.value}")
        else:
            logger.error("❌ Planner agent not found in broker agents")
            return
            
        # Check planner agent queue
        planner_queue = broker.message_queues.get("planner_agent")
        if planner_queue:
            logger.info(f"Planner agent queue found, size: {planner_queue.qsize()}")
        else:
            logger.error("❌ Planner agent queue not found")
            return
            
        # Send a test message
        test_message = Message(
            id="test_planner_msg_001",
            type=MessageType.COORDINATION,
            sender="test_sender",
            recipient="planner_agent",
            content={
                "task": {
                    "id": "test_planner_task_001",
                    "type": "patent_planning",
                    "topic": "Test Patent Topic",
                    "description": "Test Patent Description"
                }
            },
            timestamp=time.time(),
            priority=5
        )
        
        logger.info("Sending test message to planner_agent...")
        await broker.send_message(test_message)
        
        # Wait a bit and check queue
        await asyncio.sleep(1)
        queue_size = planner_queue.qsize()
        logger.info(f"Planner agent queue size after sending: {queue_size}")
        
        if queue_size > 0:
            logger.info("✅ Message was sent successfully to planner agent")
            
            # Try to get the message
            try:
                received_message = await asyncio.wait_for(planner_queue.get(), timeout=2.0)
                logger.info(f"✅ Message received from queue: {received_message.type.value}")
                logger.info(f"Message content: {received_message.content}")
            except asyncio.TimeoutError:
                logger.error("❌ Timeout getting message from queue")
        else:
            logger.error("❌ Message queue is empty - message not sent or already consumed")
            
        # Stop planner agent
        await planner.stop()
        logger.info("✅ Planner agent stopped successfully")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_planner_message())