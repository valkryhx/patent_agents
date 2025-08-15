#!/usr/bin/env python3
"""
简单的修复验证测试
只测试coordinator_agent和planner_agent之间的基本通信
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def test_basic_communication():
    """测试基本的代理间通信"""
    print("🧪 开始基本通信测试...")
    
    try:
        from patent_agent_demo.message_bus import MessageBus, MessageType
        from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
        from patent_agent_demo.agents.planner_agent import PlannerAgent
        
        # 创建消息总线
        message_bus = MessageBus()
        await message_bus.start()
        print("✅ 消息总线启动成功")
        
        # 创建代理
        coordinator = CoordinatorAgent()
        planner = PlannerAgent()
        
        # 启动代理（这会自动注册到消息总线）
        await coordinator.start()
        await planner.start()
        print("✅ 代理启动成功")
        
        # 等待代理初始化
        await asyncio.sleep(2)
        
        # 测试发送消息
        test_message = {
            "task": {
                "id": "test_workflow_stage_0",
                "type": "patent_planning",
                "topic": "测试主题",
                "description": "测试描述"
            }
        }
        
        print("📤 发送测试消息...")
        await coordinator.send_message(
            recipient="planner_agent",
            message_type=MessageType.COORDINATION,
            content=test_message,
            priority=5
        )
        
        # 等待消息处理
        await asyncio.sleep(3)
        
        # 检查planner是否收到消息
        if hasattr(planner, 'task_history') and planner.task_history:
            print("✅ 消息传递测试成功！planner收到了消息")
            result = True
        else:
            print("❌ 消息传递测试失败！planner没有收到消息")
            result = False
            
        # 清理
        await coordinator.stop()
        await planner.stop()
        await message_bus.stop()
        
        return result
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_coordinator_workflow_start():
    """测试coordinator是否能启动工作流"""
    print("\n🧪 开始工作流启动测试...")
    
    try:
        from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
        
        coordinator = CoordinatorAgent()
        await coordinator.start()
        print("✅ coordinator启动成功")
        
        # 测试启动工作流
        start_result = await coordinator.execute_task({
            "type": "start_patent_workflow",
            "topic": "证据图增强的RAG系统",
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
                result = True
            else:
                print("❌ 工作流未正确创建")
                result = False
        else:
            print(f"❌ 工作流启动失败: {start_result.error_message}")
            result = False
            
        await coordinator.stop()
        return result
        
    except Exception as e:
        print(f"❌ 工作流启动测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_system_workflow():
    """测试完整系统的工作流"""
    print("\n🧪 开始完整系统工作流测试...")
    
    try:
        from patent_agent_demo.patent_agent_system import PatentAgentSystem
        
        # 启动完整系统
        system = PatentAgentSystem()
        await system.start()
        print("✅ 完整系统启动成功")
        
        # 启动工作流
        workflow_result = await system.execute_workflow(
            topic="证据图增强的RAG系统",
            description="测试描述",
            workflow_type="standard"
        )
        
        if workflow_result["success"]:
            workflow_id = workflow_result["workflow_id"]
            print(f"✅ 工作流启动成功: {workflow_id}")
            
            # 监控工作流状态
            max_wait = 60  # 1分钟超时
            start_time = asyncio.get_event_loop().time()
            
            while True:
                status = await system.get_workflow_status(workflow_id)
                if status.get("success"):
                    workflow_data = status.get("data", {})
                    overall_status = workflow_data.get("overall_status", "unknown")
                    print(f"📊 工作流状态: {overall_status}")
                    
                    if overall_status == "completed":
                        print("🎉 工作流完成！")
                        result = True
                        break
                        
                # 检查超时
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait:
                    print(f"⏰ 超时等待完成 ({max_wait}s)")
                    result = False
                    break
                    
                await asyncio.sleep(5)  # 每5秒检查一次
        else:
            print(f"❌ 工作流启动失败: {workflow_result.get('error')}")
            result = False
            
        await system.stop()
        return result
        
    except Exception as e:
        print(f"❌ 完整系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 开始修复验证测试\n")
    
    # 测试1: 基本通信
    comm_test_result = await test_basic_communication()
    
    # 测试2: 工作流启动
    workflow_test_result = await test_coordinator_workflow_start()
    
    # 测试3: 完整系统工作流
    full_system_test_result = await test_full_system_workflow()
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📋 测试结果汇总:")
    print(f"   基本通信测试: {'✅ 通过' if comm_test_result else '❌ 失败'}")
    print(f"   工作流启动测试: {'✅ 通过' if workflow_test_result else '❌ 失败'}")
    print(f"   完整系统工作流测试: {'✅ 通过' if full_system_test_result else '❌ 失败'}")
    
    if comm_test_result and workflow_test_result and full_system_test_result:
        print("\n🎉 所有测试通过！工作流修复完全成功！")
        return 0
    elif workflow_test_result:
        print("\n⚠️  部分修复成功，但仍有问题需要解决")
        return 1
    else:
        print("\n❌ 修复失败，需要进一步检查")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)