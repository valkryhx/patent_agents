#!/usr/bin/env python3
"""
测试消息格式和传递
"""

import asyncio
import time
import uuid
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent
from patent_agent_demo.message_bus import Message, MessageType, message_bus_config

async def test_message_format():
    """测试消息格式和传递"""
    print("🧪 开始测试消息格式和传递...")
    
    # 初始化智能体
    coordinator = CoordinatorAgent(test_mode=True)
    searcher = SearcherAgent(test_mode=True)
    
    # 启动智能体
    await coordinator.start()
    await searcher.start()
    
    print("✅ 智能体启动完成")
    
    # 模拟searcher发送完成消息
    task_id = "test_workflow_stage_1"
    
    # 使用与base_agent.py相同的消息格式
    completion_message = Message(
        id=f"completion_{uuid.uuid4()}",
        type=MessageType.STATUS,
        sender="searcher_agent",
        recipient="coordinator_agent",
        content={
            "task_id": task_id,
            "status": "completed",
            "result": {"test": "data"},
            "execution_time": 1.5,
            "success": True
        },
        timestamp=time.time(),
        priority=5
    )
    
    print(f"📤 发送消息: {completion_message.content}")
    
    # 发送消息
    await message_bus_config.broker.send_message(completion_message)
    
    # 等待消息处理
    await asyncio.sleep(2)
    
    # 检查协调器日志
    print("📋 检查协调器日志...")
    
    # 停止智能体
    await coordinator.stop()
    await searcher.stop()
    
    print("✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(test_message_format())