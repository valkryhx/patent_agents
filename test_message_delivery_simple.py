#!/usr/bin/env python3
"""
简单消息传递测试
测试searcher发送消息给coordinator是否能正常接收
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from patent_agent_demo.message_bus import message_bus_config, Message, MessageType
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent
import time

async def test_message_delivery():
    """测试消息传递"""
    print("🚀 开始简单消息传递测试...")
    
    # 初始化消息总线
    await message_bus_config.initialize()
    
    # 创建智能体
    coordinator = CoordinatorAgent(test_mode=True)
    searcher = SearcherAgent(test_mode=True)
    
    # 启动智能体
    await coordinator.start()
    await searcher.start()
    
    print("✅ 智能体启动完成")
    
    # 等待智能体初始化
    await asyncio.sleep(2)
    
    # 模拟searcher发送完成消息
    task_id = "test_workflow_stage_1"
    completion_message = Message(
        id=f"completion_{time.time()}",
        type=MessageType.STATUS,
        sender="searcher_agent",
        recipient="coordinator_agent",
        content={
            "task_id": task_id,
            "status": "completed",
            "result": {"test_result": "success"},
            "execution_time": 0.1,
            "success": True
        },
        timestamp=time.time(),
        priority=5
    )
    
    print(f"📤 发送消息: {task_id}")
    await message_bus_config.broker.send_message(completion_message)
    
    # 等待消息处理
    await asyncio.sleep(3)
    
    # 检查coordinator是否收到消息
    print("🔍 检查coordinator日志...")
    
    # 停止智能体
    await coordinator.stop()
    await searcher.stop()
    
    print("✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(test_message_delivery())