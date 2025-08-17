#!/usr/bin/env python3
"""
Test Coordinator Message Handling
测试协调器消息处理
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.message_bus import message_bus_config, Message, MessageType
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent

async def test_coordinator_message_handling():
    """测试协调器消息处理"""
    print("🚀 开始测试协调器消息处理")
    
    # 初始化消息总线
    await message_bus_config.initialize()
    
    # 创建智能体
    coordinator = CoordinatorAgent(test_mode=True)
    planner = PlannerAgent(test_mode=True)
    searcher = SearcherAgent(test_mode=True)
    
    # 启动智能体
    await coordinator.start()
    await planner.start()
    await searcher.start()
    
    print("✅ 智能体启动完成")
    
    # 等待智能体完全启动
    await asyncio.sleep(3)
    
    # 发送planner完成消息给协调器
    print("📤 发送planner完成消息...")
    planner_completion_message = Message(
        id=f"completion_{asyncio.get_event_loop().time()}",
        type=MessageType.STATUS,
        sender="planner_agent",
        recipient="coordinator_agent",
        content={
            "task_id": "test_workflow_stage_0",
            "status": "completed",
            "success": True,
            "result": {"test": "planner_result"}
        },
        timestamp=asyncio.get_event_loop().time(),
        priority=5
    )
    await message_bus_config.broker.send_message(planner_completion_message)
    
    # 等待消息处理
    await asyncio.sleep(5)
    
    # 检查协调器日志
    print("📊 检查协调器日志...")
    try:
        with open("output/logs/coordinator_agent.log", "r") as f:
            coordinator_log = f.read()
            print("协调器日志内容:")
            print(coordinator_log)
    except FileNotFoundError:
        print("❌ 协调器日志文件不存在")
    
    # 检查searcher是否收到任务
    print("📊 检查searcher日志...")
    try:
        with open("output/logs/searcher_agent.log", "r") as f:
            searcher_log = f.read()
            print("Searcher日志内容:")
            print(searcher_log)
    except FileNotFoundError:
        print("❌ Searcher日志文件不存在")
    
    # 停止智能体
    await coordinator.stop()
    await planner.stop()
    await searcher.stop()
    
    print("✅ 协调器消息处理测试完成")

if __name__ == "__main__":
    asyncio.run(test_coordinator_message_handling())