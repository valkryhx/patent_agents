#!/usr/bin/env python3
"""
测试消息传递 - 模拟searcher发送消息给coordinator
"""

import asyncio
import time
import uuid
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent
from patent_agent_demo.message_bus import message_bus_config, Message, MessageType

async def test_message_delivery():
    """测试searcher到coordinator的消息传递"""
    print("🚀 开始消息传递测试...")
    
    # 初始化消息总线
    await message_bus_config.initialize()
    
    # 创建智能体（测试模式）
    coordinator = CoordinatorAgent(test_mode=True)
    searcher = SearcherAgent(test_mode=True)
    
    # 启动智能体
    await coordinator.start()
    await searcher.start()
    
    # 等待智能体初始化
    await asyncio.sleep(2)
    
    print(f"📊 可用智能体: {list(message_bus_config.broker.agents.keys())}")
    
    # 模拟searcher发送完成消息
    task_id = f"test_workflow_{uuid.uuid4().hex[:8]}_stage_1"
    
    completion_message = Message(
        id=str(uuid.uuid4()),
        type=MessageType.STATUS,
        sender="searcher_agent",
        recipient="coordinator_agent",
        content={
            "task_id": task_id,
            "status": "completed",
            "result": {"search_report": "test_result"},
            "execution_time": 1.0,
            "success": True
        },
        timestamp=time.time(),
        priority=5
    )
    
    print(f"📤 发送消息: {task_id}")
    print(f"   发送者: {completion_message.sender}")
    print(f"   接收者: {completion_message.recipient}")
    print(f"   消息类型: {completion_message.type.value}")
    
    # 发送消息
    await message_bus_config.broker.send_message(completion_message)
    
    # 等待消息处理
    await asyncio.sleep(3)
    
    # 检查coordinator的日志
    print("\n📋 Coordinator日志检查:")
    try:
        with open("output/logs/coordinator_agent.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-20:]:  # 最后20行
                if "STATUS RECV" in line or "searcher_agent" in line or task_id in line:
                    print(f"   {line.strip()}")
    except FileNotFoundError:
        print("   ❌ Coordinator日志文件不存在")
    
    # 检查searcher的日志
    print("\n📋 Searcher日志检查:")
    try:
        with open("output/logs/searcher_agent.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-10:]:  # 最后10行
                if "发送完成消息" in line or task_id in line:
                    print(f"   {line.strip()}")
    except FileNotFoundError:
        print("   ❌ Searcher日志文件不存在")
    
    # 停止智能体
    await coordinator.stop()
    await searcher.stop()
    
    print("\n✅ 消息传递测试完成")

if __name__ == "__main__":
    asyncio.run(test_message_delivery())