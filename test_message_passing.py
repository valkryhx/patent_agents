#!/usr/bin/env python3
"""
Test message passing between coordinator_agent and searcher_agent
"""

import asyncio
import sys
import os
import logging
import time
import uuid

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.message_bus import Message, MessageType

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_message_passing():
    """Test message passing between agents"""
    try:
        # 初始化系统
        system = PatentAgentSystem()
        await system.start()
        
        logger.info("✅ 系统启动成功")
        
        # 获取 coordinator_agent 和 searcher_agent
        coordinator = system.coordinator
        searcher = system.agents["searcher_agent"]
        
        # 创建一个测试任务
        test_task_id = f"test_task_{uuid.uuid4()}"
        test_task = {
            "id": test_task_id,
            "type": "prior_art_search",
            "topic": "测试主题",
            "description": "测试描述"
        }
        
        logger.info(f"📤 发送测试任务: {test_task_id}")
        
        # 直接发送任务给 searcher_agent
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.COORDINATION,
            sender="coordinator_agent",
            recipient="searcher_agent",
            content={"task": test_task},
            timestamp=time.time(),
            priority=5
        )
        
        logger.info(f"📤 发送消息: {message.id} 到 {message.recipient}")
        logger.info(f"📋 消息内容: {message.content}")
        
        await coordinator.broker.send_message(message)
        
        # 等待一段时间让 searcher_agent 处理任务
        logger.info("⏳ 等待 searcher_agent 处理任务...")
        await asyncio.sleep(2)
        
        # 检查 searcher_agent 的队列
        searcher_queue_size = coordinator.broker.get_queue_size("searcher_agent")
        logger.info(f"📊 searcher_agent 队列大小: {searcher_queue_size}")
        
        # 等待更长时间
        await asyncio.sleep(8)
        
        # 检查 coordinator_agent 的队列
        coordinator_queue_size = coordinator.broker.get_queue_size("coordinator_agent")
        logger.info(f"📊 coordinator_agent 队列大小: {coordinator_queue_size}")
        
        logger.info("✅ 测试完成")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        raise
    finally:
        await system.stop()
        logger.info("🛑 系统已停止")

if __name__ == "__main__":
    asyncio.run(test_message_passing())