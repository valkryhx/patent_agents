#!/usr/bin/env python3
"""
测试消息发送功能
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

async def test_message_sending():
    """测试消息发送功能"""
    try:
        logger.info("🚀 开始测试消息发送功能")
        
        # 创建系统（测试模式）
        system = PatentAgentSystem(test_mode=True)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 等待一下让所有智能体启动
        await asyncio.sleep(3)
        
        # 获取broker
        broker = system.message_bus_config.broker
        
        # 检查planner_agent是否在队列中
        logger.info(f"📋 检查planner_agent是否在消息队列中...")
        logger.info(f"可用队列: {list(broker.message_queues.keys())}")
        
        if "planner_agent" not in broker.message_queues:
            logger.error("❌ planner_agent 不在消息队列中")
            return
        
        # 测试发送消息给planner_agent
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
        logger.info(f"   消息类型: {test_message.type.value}")
        logger.info(f"   发送者: {test_message.sender}")
        logger.info(f"   接收者: {test_message.recipient}")
        logger.info(f"   内容: {test_message.content}")
        
        await broker.send_message(test_message)
        
        # 立即检查队列
        logger.info("🔍 立即检查planner_agent队列...")
        queue = broker.message_queues["planner_agent"]
        logger.info(f"   队列大小: {queue.qsize()}")
        
        # 等待一下
        logger.info("⏳ 等待5秒...")
        await asyncio.sleep(5)
        
        # 再次检查队列
        logger.info("🔍 5秒后检查planner_agent队列...")
        logger.info(f"   队列大小: {queue.qsize()}")
        
        # 尝试获取消息
        try:
            message = await broker.get_message("planner_agent")
            if message:
                logger.info(f"✅ planner_agent 收到了消息: {message.id}")
                logger.info(f"   消息类型: {message.type.value}")
                logger.info(f"   发送者: {message.sender}")
                logger.info(f"   内容: {message.content}")
            else:
                logger.warning("⚠️ planner_agent 队列为空")
        except Exception as e:
            logger.error(f"❌ 检查planner_agent队列时出错: {e}")
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_message_sending())