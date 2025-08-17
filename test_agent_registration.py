#!/usr/bin/env python3
"""
测试智能体注册
"""

import asyncio
import sys
import os
import logging
import time

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.message_bus import Message, MessageType
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent_registration():
    """测试智能体注册"""
    try:
        logger.info("🚀 开始测试智能体注册")
        
        # 创建系统（测试模式）
        system = PatentAgentSystem(test_mode=True)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 等待一下让所有智能体启动
        await asyncio.sleep(5)
        
        # 获取broker
        broker = system.message_bus_config.broker
        
        # 检查所有智能体是否注册
        logger.info(f"📋 检查智能体注册状态...")
        logger.info(f"注册的智能体: {list(broker.agents.keys())}")
        logger.info(f"消息队列: {list(broker.message_queues.keys())}")
        
        # 检查planner_agent
        if "planner_agent" in broker.agents:
            logger.info("✅ planner_agent 已注册")
            agent_info = broker.agents["planner_agent"]
            logger.info(f"   状态: {agent_info.status.value}")
            logger.info(f"   能力: {agent_info.capabilities}")
        else:
            logger.error("❌ planner_agent 未注册")
            return
        
        if "planner_agent" in broker.message_queues:
            logger.info("✅ planner_agent 有消息队列")
            queue = broker.message_queues["planner_agent"]
            logger.info(f"   队列ID: {id(queue)}")
            logger.info(f"   队列大小: {queue.qsize()}")
        else:
            logger.error("❌ planner_agent 没有消息队列")
            return
        
        # 测试发送消息
        test_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.COORDINATION,
            sender="test_sender",
            recipient="planner_agent",
            content={
                "task": {
                    "id": "test_task_001",
                    "type": "patent_planning",
                    "topic": "测试主题",
                    "description": "测试描述"
                }
            },
            timestamp=time.time(),
            priority=5
        )
        
        logger.info(f"📤 发送测试消息给 planner_agent: {test_message.id}")
        logger.info(f"   消息内容: {test_message.content}")
        
        # 发送消息
        await broker.send_message(test_message)
        
        # 立即检查队列
        queue = broker.message_queues["planner_agent"]
        logger.info(f"🔍 发送后立即检查队列大小: {queue.qsize()}")
        
        # 再等待一小段时间
        await asyncio.sleep(0.1)
        logger.info(f"🔍 0.1秒后队列大小: {queue.qsize()}")
        
        # 等待一下
        logger.info("⏳ 等待3秒...")
        await asyncio.sleep(3)
        
        # 再次检查队列
        logger.info(f"🔍 3秒后队列大小: {queue.qsize()}")
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_registration())