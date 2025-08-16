#!/usr/bin/env python3
"""
Test ultra real-time monitor system creation
"""

import asyncio
import sys
import os
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from ultra_real_time_monitor import UltraRealTimeMonitor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ultra_monitor_system_creation():
    """Test ultra real-time monitor system creation"""
    try:
        logger.info("🚀 Testing ultra real-time monitor system creation")
        
        # Create ultra real-time monitor
        monitor = UltraRealTimeMonitor()
        logger.info("✅ Ultra real-time monitor created")
        
        # Start workflow
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        
        await monitor._start_workflow(topic, description)
        logger.info("✅ Workflow started")
        
        # Check if system is created
        if monitor.system:
            logger.info("✅ System created")
            
            # Check if all agents are created
            logger.info(f"Agents in system: {list(monitor.system.agents.keys())}")
            
            # Check if planner agent exists
            if "planner_agent" in monitor.system.agents:
                logger.info("✅ Planner agent exists in system")
                planner = monitor.system.agents["planner_agent"]
                logger.info(f"Planner agent status: {planner.status}")
                logger.info(f"Planner agent name: {planner.name}")
            else:
                logger.error("❌ Planner agent missing from system")
                return False
            
            # Check message bus agents
            broker = monitor.system.message_bus_config.broker
            logger.info(f"Agents in broker: {list(broker.agents.keys())}")
            
            if "planner_agent" in broker.agents:
                logger.info("✅ Planner agent exists in broker")
            else:
                logger.error("❌ Planner agent missing from broker")
                return False
        else:
            logger.error("❌ System not created")
            return False
        
        # Stop monitor
        await monitor.stop_monitoring()
        logger.info("✅ Monitor stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ultra_monitor_system_creation())
    if success:
        print("✅ Ultra real-time monitor system creation test passed")
    else:
        print("❌ Ultra real-time monitor system creation test failed")