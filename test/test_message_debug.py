#!/usr/bin/env python3
"""
简单的消息调试测试脚本
"""

import asyncio
import time
import uuid
from patent_agent_demo.message_bus import MessageBusBroker, Message, MessageType, message_bus_config
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent

async def test_message_debug():
    """测试消息传递的调试"""
    print("🔍 开始消息调试测试...")
    
    # 初始化消息总线
    broker = message_bus_config.broker
    
    # 创建智能体
    coordinator = CoordinatorAgent(test_mode=True)
    searcher = SearcherAgent(test_mode=True)
    
    # 启动智能体
    await coordinator.start()
    await searcher.start()
    
    # 等待智能体初始化
    await asyncio.sleep(2)
    
    # 创建一个测试任务ID
    test_task_id = f"test_workflow_{uuid.uuid4().hex[:8]}_stage_1"
    print(f"📝 测试任务ID: {test_task_id}")
    
    # 模拟searcher发送完成消息
    completion_message = Message(
        id=f"completion_{uuid.uuid4()}",
        type=MessageType.STATUS,
        sender="searcher_agent",
        recipient="coordinator_agent",
        content={
            "task_id": test_task_id,
            "status": "completed",
            "result": {"test": "data"},
            "execution_time": 1.0,
            "success": True
        },
        timestamp=time.time(),
        priority=5
    )
    
    print(f"📤 发送消息: {completion_message.id}")
    print(f"   发送者: {completion_message.sender}")
    print(f"   接收者: {completion_message.recipient}")
    print(f"   任务ID: {test_task_id}")
    
    # 发送消息
    await broker.send_message(completion_message)
    
    # 等待消息处理
    await asyncio.sleep(3)
    
    # 检查协调器是否收到了消息
    print(f"🔍 检查协调器的completed_tasks: {list(coordinator.completed_tasks.keys())}")
    print(f"🔍 检查协调器的failed_tasks: {list(coordinator.failed_tasks)}")
    
    # 停止智能体
    await coordinator.stop()
    await searcher.stop()
    
    print("✅ 消息调试测试完成")

if __name__ == "__main__":
    asyncio.run(test_message_debug())