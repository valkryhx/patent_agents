#!/usr/bin/env python3
"""
测试工作流问题的脚本
"""

import asyncio
import time
import uuid
from patent_agent_demo.message_bus import MessageBusBroker, Message, MessageType, message_bus_config
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent, PatentWorkflow, WorkflowStage
from patent_agent_demo.agents.searcher_agent import SearcherAgent

async def test_workflow_issue():
    """测试工作流问题"""
    print("🔍 开始测试工作流问题...")
    
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
    
    # 创建一个工作流
    workflow_id = f"test_workflow_{uuid.uuid4().hex[:8]}"
    print(f"📝 工作流ID: {workflow_id}")
    
    # 创建测试工作流
    test_workflow = PatentWorkflow(
        workflow_id=workflow_id,
        topic="测试主题",
        description="测试描述",
        stages=[
            WorkflowStage(stage_name="Planning & Strategy", agent_name="planner_agent", status="completed"),
            WorkflowStage(stage_name="Prior Art Search", agent_name="searcher_agent", status="pending")
        ],
        current_stage=1,
        overall_status="active",
        start_time=time.time(),
        results={}
    )
    
    # 将工作流添加到协调器
    coordinator.active_workflows[workflow_id] = test_workflow
    print(f"✅ 工作流已添加到协调器: {list(coordinator.active_workflows.keys())}")
    
    # 模拟searcher发送完成消息
    task_id = f"{workflow_id}_stage_1"
    completion_message = Message(
        id=f"completion_{uuid.uuid4()}",
        type=MessageType.STATUS,
        sender="searcher_agent",
        recipient="coordinator_agent",
        content={
            "task_id": task_id,
            "status": "completed",
            "result": {"test": "data"},
            "execution_time": 1.0,
            "success": True
        },
        timestamp=time.time(),
        priority=5
    )
    
    print(f"📤 发送消息: {completion_message.id}")
    print(f"   任务ID: {task_id}")
    print(f"   工作流ID: {workflow_id}")
    
    # 发送消息
    await broker.send_message(completion_message)
    
    # 等待消息处理
    await asyncio.sleep(3)
    
    # 检查协调器是否收到了消息
    print(f"🔍 检查协调器的completed_tasks: {list(coordinator.completed_tasks.keys())}")
    print(f"🔍 检查协调器的failed_tasks: {list(coordinator.failed_tasks)}")
    
    # 检查工作流状态
    workflow = coordinator.active_workflows.get(workflow_id)
    if workflow:
        print(f"🔍 工作流状态: {workflow.overall_status}")
        print(f"🔍 当前阶段: {workflow.current_stage}")
        for i, stage in enumerate(workflow.stages):
            print(f"   阶段 {i}: {stage.stage_name} - {stage.status}")
    else:
        print(f"❌ 工作流 {workflow_id} 未找到")
    
    # 停止智能体
    await coordinator.stop()
    await searcher.stop()
    
    print("✅ 工作流问题测试完成")

if __name__ == "__main__":
    asyncio.run(test_workflow_issue())