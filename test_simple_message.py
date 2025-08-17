#!/usr/bin/env python3
"""
简单的消息发送测试
"""

import asyncio
import sys
import os
import logging
import time

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.message_bus import MessageBusBroker, Message, MessageType
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_message():
    """简单的消息发送测试"""
    try:
        logger.info("🚀 开始简单消息发送测试")
        
        # 创建消息总线
        broker = MessageBusBroker()
        logger.info("✅ 消息总线创建成功")
        
        # 注册一个测试队列
        test_queue = asyncio.Queue()
        broker.message_queues["test_agent"] = test_queue
        logger.info("✅ 测试队列注册成功")
        
        # 创建测试消息
        test_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.COORDINATION,
            sender="test_sender",
            recipient="test_agent",
            content={"test": "data"},
            timestamp=time.time(),
            priority=5
        )
        
        logger.info(f"📤 准备发送消息: {test_message.id}")
        logger.info(f"   接收者: {test_message.recipient}")
        logger.info(f"   可用队列: {list(broker.message_queues.keys())}")
        
        # 发送消息
        try:
            await broker.send_message(test_message)
            logger.info("✅ 消息发送成功")
        except Exception as e:
            logger.error(f"❌ 消息发送失败: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 检查队列
        logger.info(f"🔍 检查队列大小: {test_queue.qsize()}")
        
        # 获取消息
        try:
            received_message = await broker.get_message("test_agent")
            if received_message:
                logger.info(f"✅ 成功接收消息: {received_message.id}")
                logger.info(f"   内容: {received_message.content}")
            else:
                logger.warning("⚠️ 没有接收到消息")
        except Exception as e:
            logger.error(f"❌ 获取消息失败: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("✅ 测试完成")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_message())