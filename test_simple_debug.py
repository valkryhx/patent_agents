#!/usr/bin/env python3

import sys
import os
import asyncio
import logging
import time
import uuid

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.message_bus import Message, MessageType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_debug():
    """简单的调试测试"""
    try:
        logger.info("🚀 开始简单调试测试")
        
        # 创建系统（测试模式）
        logger.info("📦 创建系统...")
        system = PatentAgentSystem(test_mode=True)
        
        logger.info("🚀 启动系统...")
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 等待一下让所有智能体启动
        logger.info("⏳ 等待5秒让智能体启动...")
        await asyncio.sleep(5)
        
        # 获取broker
        logger.info("🔍 获取消息总线...")
        broker = system.message_bus_config.broker
        
        # 检查planner_agent
        logger.info("🔍 检查planner_agent...")
        if "planner_agent" in broker.message_queues:
            logger.info("✅ planner_agent 有消息队列")
            queue = broker.message_queues["planner_agent"]
            logger.info(f"   队列大小: {queue.qsize()}")
        else:
            logger.error("❌ planner_agent 没有消息队列")
            return
        
        # 测试发送消息
        logger.info("📤 准备发送测试消息...")
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
        
        logger.info(f"📤 发送测试消息: {test_message.id}")
        logger.info(f"   消息内容: {test_message.content}")
        
        # 发送消息
        await broker.send_message(test_message)
        logger.info("✅ 消息发送完成")
        
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
        logger.info("🛑 停止系统...")
        await system.stop()
        logger.info("✅ 系统已停止")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_debug())