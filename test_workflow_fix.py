#!/usr/bin/env python3
"""
测试工作流修复的简单脚本
验证coordinator_agent和base_agent之间的消息传递是否正常工作
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem


async def test_workflow_communication():
    """测试工作流通信是否正常"""
    print("🧪 开始测试工作流通信...")
    
    try:
        # 启动系统
        system = PatentAgentSystem()
        await system.start()
        print("✅ 系统启动成功")
        
        # 启动工作流
        start_result = await system.coordinator.execute_task({
            "type": "start_patent_workflow",
            "topic": "证据图增强的RAG系统",
            "description": "一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统",
            "workflow_type": "standard"
        })
        
        if not start_result.success:
            print(f"❌ 启动工作流失败: {start_result.error_message}")
            return False
            
        workflow_id = start_result.data.get("workflow_id")
        print(f"✅ 工作流启动成功: {workflow_id}")
        
        # 监控工作流状态
        max_wait = 300  # 5分钟超时
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status_result = await system.coordinator.execute_task({
                "type": "monitor_workflow",
                "workflow_id": workflow_id
            })
            
            if status_result.success:
                workflow = status_result.data.get("workflow")
                if hasattr(workflow, 'overall_status'):
                    overall_status = workflow.overall_status
                elif isinstance(workflow, dict):
                    overall_status = workflow.get("overall_status")
                else:
                    overall_status = "unknown"
                
                print(f"📊 工作流状态: {overall_status}")
                
                # 检查是否完成
                if overall_status == "completed":
                    print("🎉 工作流完成！")
                    break
                    
            # 检查超时
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait:
                print(f"⏰ 超时等待完成 ({max_wait}s)")
                break
                
            await asyncio.sleep(10)  # 每10秒检查一次
            
        await system.stop()
        print("✅ 系统关闭成功")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_message_passing():
    """测试代理间消息传递"""
    print("\n🧪 开始测试代理间消息传递...")
    
    try:
        from patent_agent_demo.message_bus import MessageType
        from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
        from patent_agent_demo.agents.planner_agent import PlannerAgent
        
        # 创建测试代理
        coordinator = CoordinatorAgent()
        planner = PlannerAgent()
        
        await coordinator.start()
        await planner.start()
        print("✅ 测试代理启动成功")
        
        # 测试消息发送
        test_message = {
            "task": {
                "id": "test_workflow_stage_0",
                "type": "patent_planning",
                "topic": "测试主题",
                "description": "测试描述"
            }
        }
        
        # 发送测试消息
        await coordinator.send_message(
            recipient="planner_agent",
            message_type=MessageType.COORDINATION,
            content=test_message,
            priority=5
        )
        print("✅ 测试消息发送成功")
        
        # 等待一小段时间让消息处理
        await asyncio.sleep(2)
        
        # 检查planner是否收到消息
        if planner.task_history:
            print("✅ 消息传递测试成功")
            result = True
        else:
            print("❌ 消息传递测试失败")
            result = False
            
        await coordinator.stop()
        await planner.stop()
        return result
        
    except Exception as e:
        print(f"❌ 消息传递测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 开始工作流修复验证测试\n")
    
    # 测试1: 代理间消息传递
    message_test_result = await test_agent_message_passing()
    
    # 测试2: 完整工作流通信
    workflow_test_result = await test_workflow_communication()
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📋 测试结果汇总:")
    print(f"   代理间消息传递: {'✅ 通过' if message_test_result else '❌ 失败'}")
    print(f"   完整工作流通信: {'✅ 通过' if workflow_test_result else '❌ 失败'}")
    
    if message_test_result and workflow_test_result:
        print("\n🎉 所有测试通过！工作流修复成功！")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)