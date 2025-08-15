#!/usr/bin/env python3
"""
调试coordinator_agent的消息发送功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def debug_coordinator():
    """调试coordinator_agent"""
    print("🔍 开始调试coordinator_agent...")
    
    try:
        from patent_agent_demo.message_bus import MessageType, MessageBusBroker
        from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
        from patent_agent_demo.agents.planner_agent import PlannerAgent
        
        # 创建消息总线
        message_bus = MessageBusBroker()
        print("✅ 消息总线创建成功")
        
        # 创建代理
        coordinator = CoordinatorAgent()
        planner = PlannerAgent()
        
        # 启动代理
        await coordinator.start()
        await planner.start()
        print("✅ 代理启动成功")
        
        # 等待代理初始化
        await asyncio.sleep(2)
        
        # 检查消息总线状态
        print("\n📡 消息总线状态:")
        print(f"注册的代理: {list(message_bus.agents.keys())}")
        print(f"消息队列: {list(message_bus.message_queues.keys())}")
        
        # 检查coordinator是否有send_message方法
        print(f"\n🔍 Coordinator方法检查:")
        print(f"has send_message: {hasattr(coordinator, 'send_message')}")
        print(f"send_message type: {type(getattr(coordinator, 'send_message', None))}")
        
        # 检查coordinator的broker
        print(f"has broker: {hasattr(coordinator, 'broker')}")
        if hasattr(coordinator, 'broker'):
            print(f"broker type: {type(coordinator.broker)}")
            print(f"broker methods: {[m for m in dir(coordinator.broker) if not m.startswith('_')]}")
        
        # 测试启动工作流
        print(f"\n🧪 测试启动工作流...")
        start_result = await coordinator.execute_task({
            "type": "start_patent_workflow",
            "topic": "使用证据图来增强RAG的系统",
            "description": "测试描述",
            "workflow_type": "standard"
        })
        
        if start_result.success:
            workflow_id = start_result.data.get("workflow_id")
            print(f"✅ 工作流启动成功: {workflow_id}")
            
            # 检查工作流状态
            if hasattr(coordinator, 'active_workflows') and workflow_id in coordinator.active_workflows:
                workflow = coordinator.active_workflows[workflow_id]
                print(f"✅ 工作流已创建，当前阶段: {workflow.current_stage}")
                print(f"✅ 工作流状态: {workflow.overall_status}")
                
                # 检查第一阶段状态
                if workflow.stages:
                    first_stage = workflow.stages[0]
                    print(f"✅ 第一阶段: {first_stage.stage_name} - {first_stage.status}")
                    
                    # 等待一段时间看是否有消息发送
                    print(f"\n⏳ 等待消息发送...")
                    await asyncio.sleep(5)
                    
                    # 检查planner是否收到消息
                    if hasattr(planner, 'task_history') and planner.task_history:
                        print(f"✅ Planner收到了消息: {len(planner.task_history)} 个任务")
                    else:
                        print(f"❌ Planner没有收到消息")
                        
                        # 检查coordinator的队列
                        if hasattr(coordinator, 'message_queue'):
                            queue_size = coordinator.message_queue.qsize()
                            print(f"Coordinator队列大小: {queue_size}")
                        else:
                            print("Coordinator没有message_queue属性")
            else:
                print("❌ 工作流未正确创建")
        else:
            print(f"❌ 工作流启动失败: {start_result.error_message}")
            
        # 清理
        await coordinator.stop()
        await planner.stop()
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_coordinator())