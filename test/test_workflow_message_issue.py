#!/usr/bin/env python3
"""
测试工作流中的消息传递问题
"""

import asyncio
import time
import uuid
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent
from patent_agent_demo.message_bus import message_bus_config, Message, MessageType

async def test_workflow_message_issue():
    """测试工作流中的消息传递问题"""
    print("🚀 开始测试工作流消息传递问题...")
    
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
    
    # 模拟工作流启动
    workflow_id = "7dc2b063-b4ae-4654-bd95-c468df663f61"  # 使用实际工作流ID
    
    # 创建测试工作流并添加到coordinator
    from patent_agent_demo.agents.coordinator_agent import PatentWorkflow, WorkflowStage
    
    test_workflow = PatentWorkflow(
        workflow_id=workflow_id,
        topic="测试主题",
        description="测试描述",
        stages=[
            WorkflowStage(stage_name="Planning & Strategy", agent_name="planner_agent", status="completed"),
            WorkflowStage(stage_name="Prior Art Search", agent_name="searcher_agent", status="running"),
            WorkflowStage(stage_name="Innovation Discussion", agent_name="discusser_agent", status="pending")
        ],
        current_stage=1,
        overall_status="active",
        start_time=time.time(),
        results={}
    )
    
    coordinator.active_workflows[workflow_id] = test_workflow
    print(f"✅ 工作流已添加到coordinator: {workflow_id}")
    
    # 模拟searcher发送完成消息
    task_id = f"{workflow_id}_stage_1"
    
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
                if "STATUS RECV" in line or "searcher_agent" in line or task_id in line or "Workflow.*not found" in line:
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
    
    print("\n✅ 工作流消息传递问题测试完成")

if __name__ == "__main__":
    asyncio.run(test_workflow_message_issue())