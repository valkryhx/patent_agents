#!/usr/bin/env python3
"""
测试消息传递问题的脚本
"""

import asyncio
import time
import uuid
from patent_agent_demo.message_bus import MessageBusBroker, Message, MessageType, message_bus_config
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent

async def test_message_issue():
    """测试消息传递问题"""
    print("🔍 开始测试消息传递问题...")
    
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
    
    # 创建一个测试任务
    task_id = f"test_task_{uuid.uuid4().hex[:8]}"
    task_content = {
        "task": {
            "id": task_id,
            "type": "prior_art_search",
            "workflow_id": "test_workflow",
            "stage_index": 1,
            "topic": "测试主题",
            "description": "测试描述"
        }
    }
    
    # 发送任务给searcher
    task_message = Message(
        id=str(uuid.uuid4()),
        type=MessageType.COORDINATION,
        sender="coordinator_agent",
        recipient="searcher_agent",
        content=task_content,
        timestamp=time.time(),
        priority=5
    )
    
    print(f"📤 发送任务消息: {task_message.id}")
    print(f"   任务ID: {task_id}")
    
    # 发送消息
    await broker.send_message(task_message)
    
    # 等待searcher处理任务
    await asyncio.sleep(5)
    
    # 检查searcher是否发送了完成消息
    print(f"🔍 检查协调器的completed_tasks: {list(coordinator.completed_tasks.keys())}")
    print(f"🔍 检查协调器的failed_tasks: {list(coordinator.failed_tasks)}")
    
    # 停止智能体
    await coordinator.stop()
    await searcher.stop()
    
    print("✅ 消息传递问题测试完成")

if __name__ == "__main__":
    asyncio.run(test_message_issue())