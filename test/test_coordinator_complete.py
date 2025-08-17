#!/usr/bin/env python3
"""
Complete Test Coordinator Workflow Handling
完整测试协调器工作流处理
"""

import asyncio
import sys
import os
import uuid

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.message_bus import message_bus_config, Message, MessageType
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent, PatentWorkflow, WorkflowStage
from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.agents.searcher_agent import SearcherAgent

async def test_coordinator_workflow_handling():
    """测试协调器工作流处理"""
    print("🚀 开始测试协调器工作流处理")
    
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
    
    # 创建一个测试工作流
    workflow_id = f"test_workflow_{uuid.uuid4().hex[:8]}"
    print(f"📋 创建测试工作流: {workflow_id}")
    
    # 创建简单的工作流阶段
    stages = [
        WorkflowStage(
            stage_name="Patent Planning",
            agent_name="planner_agent",
            status="pending"
        ),
        WorkflowStage(
            stage_name="Prior Art Search",
            agent_name="searcher_agent", 
            status="pending"
        ),
        WorkflowStage(
            stage_name="Discussion",
            agent_name="discusser_agent",
            status="pending"
        )
    ]
    
    # 创建测试工作流
    test_workflow = PatentWorkflow(
        workflow_id=workflow_id,
        topic="Test Patent",
        description="Test workflow for coordinator",
        stages=stages,
        current_stage=0,
        overall_status="active",
        start_time=asyncio.get_event_loop().time()
    )
    
    # 将工作流添加到协调器的active_workflows中
    coordinator.active_workflows[workflow_id] = test_workflow
    print(f"✅ 工作流已添加到协调器: {workflow_id}")
    print(f"📊 协调器活动工作流数量: {len(coordinator.active_workflows)}")
    
    # 发送planner完成消息给协调器
    print("📤 发送planner完成消息...")
    planner_completion_message = Message(
        id=f"completion_{asyncio.get_event_loop().time()}",
        type=MessageType.STATUS,
        sender="planner_agent",
        recipient="coordinator_agent",
        content={
            "task_id": f"{workflow_id}_stage_0",
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
    
    # 检查工作流状态
    print("📊 检查工作流状态...")
    if workflow_id in coordinator.active_workflows:
        workflow = coordinator.active_workflows[workflow_id]
        print(f"工作流状态: {workflow.overall_status}")
        print(f"当前阶段: {workflow.current_stage}")
        print(f"阶段数量: {len(workflow.stages)}")
        for i, stage in enumerate(workflow.stages):
            print(f"  阶段 {i}: {stage.stage_name} - {stage.status}")
    else:
        print("❌ 工作流不在active_workflows中")
    
    # 停止智能体
    await coordinator.stop()
    await planner.stop()
    await searcher.stop()
    
    print("✅ 协调器工作流处理测试完成")

if __name__ == "__main__":
    asyncio.run(test_coordinator_workflow_handling())