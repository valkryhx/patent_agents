#!/usr/bin/env python3
"""
测试实际工作流的task_id格式
"""

import asyncio
import time
import uuid
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent, PatentWorkflow, WorkflowStage
from patent_agent_demo.agents.searcher_agent import SearcherAgent
from patent_agent_demo.message_bus import Message, MessageType, message_bus_config

async def test_workflow_id_format():
    """测试实际工作流的task_id格式"""
    print("🧪 开始测试实际工作流的task_id格式...")
    
    # 初始化智能体
    coordinator = CoordinatorAgent(test_mode=True)
    searcher = SearcherAgent(test_mode=True)
    
    # 启动智能体
    await coordinator.start()
    await searcher.start()
    
    print("✅ 智能体启动完成")
    
    # 创建实际的工作流ID（模拟实际工作流）
    workflow_id = str(uuid.uuid4())
    print(f"🆔 生成的工作流ID: {workflow_id}")
    
    # 创建测试工作流并添加到协调器
    test_workflow = PatentWorkflow(
        workflow_id=workflow_id,
        topic="测试专利主题",
        description="测试专利描述",
        stages=[
            WorkflowStage(
                stage_name="Planning & Strategy",
                agent_name="planner_agent",
                status="completed"
            ),
            WorkflowStage(
                stage_name="Prior Art Search",
                agent_name="searcher_agent",
                status="running"
            ),
            WorkflowStage(
                stage_name="Innovation Discussion",
                agent_name="discusser_agent",
                status="pending"
            )
        ],
        current_stage=1,
        overall_status="active",
        start_time=time.time(),
        results={}
    )
    
    # 添加到协调器的活动工作流中
    coordinator.active_workflows[workflow_id] = test_workflow
    print(f"✅ 工作流已添加到协调器: {workflow_id}")
    
    # 使用实际工作流的task_id格式
    task_id = f"{workflow_id}_stage_1"
    print(f"📋 生成的task_id: {task_id}")
    
    # 模拟searcher发送完成消息
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
    await asyncio.sleep(3)
    
    # 检查协调器日志
    print("📋 检查协调器日志...")
    
    # 检查工作流状态
    workflow = coordinator.active_workflows.get(workflow_id)
    if workflow:
        print(f"✅ 工作流状态: {workflow.overall_status}")
        print(f"✅ 当前阶段: {workflow.current_stage}")
        for i, stage in enumerate(workflow.stages):
            print(f"   阶段 {i}: {stage.stage_name} - {stage.status}")
    else:
        print("❌ 工作流未找到")
    
    # 停止智能体
    await coordinator.stop()
    await searcher.stop()
    
    print("✅ 测试完成")

if __name__ == "__main__":
    asyncio.run(test_workflow_id_format())