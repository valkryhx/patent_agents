#!/usr/bin/env python3
"""
简化的协调器测试脚本
"""

import asyncio
import time
import uuid
from patent_agent_demo.message_bus import MessageBusBroker, Message, MessageType, message_bus_config
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent

async def test_coordinator_simple():
    """简化的协调器测试"""
    print("🔍 开始简化协调器测试...")
    
    # 初始化消息总线
    broker = message_bus_config.broker
    
    # 创建协调器
    coordinator = CoordinatorAgent(test_mode=True)
    
    # 启动协调器
    await coordinator.start()
    
    # 等待协调器初始化
    await asyncio.sleep(2)
    
    # 创建一个简单的状态消息
    status_message = Message(
        id=str(uuid.uuid4()),
        type=MessageType.STATUS,
        sender="planner_agent",
        recipient="coordinator_agent",
        content={
            "task_id": "test_workflow_stage_0",
            "status": "completed",
            "result": {"test": "data"},
            "success": True
        },
        timestamp=time.time(),
        priority=5
    )
    
    print(f"📤 发送状态消息: {status_message.id}")
    
    # 发送消息
    await broker.send_message(status_message)
    
    # 等待消息处理
    await asyncio.sleep(5)
    
    # 检查协调器的状态
    print(f"🔍 检查协调器的completed_tasks: {list(coordinator.completed_tasks.keys())}")
    print(f"🔍 检查协调器的failed_tasks: {list(coordinator.failed_tasks)}")
    
    # 停止协调器
    await coordinator.stop()
    
    print("✅ 简化协调器测试完成")

if __name__ == "__main__":
    asyncio.run(test_coordinator_simple())