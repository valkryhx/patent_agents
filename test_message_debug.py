#!/usr/bin/env python3
"""
Debug message passing between coordinator and agents
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.message_bus import MessageType, Message
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_message_passing():
    """Test message passing between coordinator and agents"""
    try:
        logger.info("🚀 Starting message passing test")
        
        # Create and start system
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        
        logger.info("✅ System started successfully")
        
        # Wait for agents to initialize
        await asyncio.sleep(3)
        
        # Check agent availability
        logger.info("=== CHECKING AGENT AVAILABILITY ===")
        for agent_name, agent in system.agents.items():
            logger.info(f"Agent {agent_name}: {agent.status.value}")
            
        # Test direct message sending
        logger.info("=== TESTING DIRECT MESSAGE SENDING ===")
        
        # Send a test message to planner agent
        test_message = Message(
            id="test_msg_001",
            type=MessageType.COORDINATION,
            sender="coordinator_agent",
            recipient="planner_agent",
            content={
                "task": {
                    "id": "test_task_001",
                    "type": "test_task",
                    "workflow_id": "test_workflow",
                    "topic": "Test Topic",
                    "description": "Test Description"
                }
            },
            timestamp=time.time(),
            priority=5
        )
        
        logger.info("Sending test message to planner_agent...")
        await system.message_bus_config.broker.send_message(test_message)
        
        # Wait a bit and check if message was received
        await asyncio.sleep(2)
        
        # Check message queue
        planner_queue = system.message_bus_config.broker.message_queues.get("planner_agent")
        if planner_queue:
            queue_size = planner_queue.qsize()
            logger.info(f"Planner agent queue size: {queue_size}")
            
            if queue_size > 0:
                logger.info("✅ Message was sent successfully")
                # Try to get the message
                try:
                    received_message = await asyncio.wait_for(planner_queue.get(), timeout=1.0)
                    logger.info(f"✅ Message received: {received_message.type.value}")
                except asyncio.TimeoutError:
                    logger.error("❌ Timeout getting message")
            else:
                logger.error("❌ Message queue is empty - message not sent or already consumed")
        else:
            logger.error("❌ Planner agent queue not found")
            
        # Test workflow start
        logger.info("=== TESTING WORKFLOW START ===")
        
        try:
            workflow_id = await system.execute_workflow(
                topic="Test Patent Topic",
                description="Test Patent Description",
                workflow_type="enhanced"
            )
            
            logger.info(f"✅ Workflow started with ID: {workflow_id}")
            
            # Wait a bit and check status
            await asyncio.sleep(5)
            
            status_result = await system.get_workflow_status(workflow_id)
            logger.info(f"Workflow status: {status_result}")
            
        except Exception as e:
            logger.error(f"❌ Workflow start failed: {e}")
            import traceback
            traceback.print_exc()
            
        # Stop system
        await system.stop()
        logger.info("✅ System stopped successfully")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_message_passing())