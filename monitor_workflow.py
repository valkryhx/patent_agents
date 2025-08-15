#!/usr/bin/env python3
"""
专利工作流详细监控脚本
实时跟踪每个代理的状态、消息传递和工作流执行进度
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def monitor_workflow_execution():
    """监控工作流执行"""
    print("🔍 开始详细监控专利工作流执行...")
    print("=" * 60)
    
    try:
        from patent_agent_demo.patent_agent_system import PatentAgentSystem
        
        # 启动系统
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 启动专利代理系统...")
        system = PatentAgentSystem()
        await system.start()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 系统启动成功")
        
        # 启动工作流
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📋 启动专利工作流...")
        workflow_result = await system.execute_workflow(
            topic="使用证据图来增强RAG的系统",
            description="一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统",
            workflow_type="standard"
        )
        
        if not workflow_result["success"]:
            print(f"❌ 工作流启动失败: {workflow_result.get('error')}")
            return False
            
        workflow_id = workflow_result["workflow_id"]
        print(f"✅ 工作流启动成功: {workflow_id}")
        
        # 详细监控工作流执行
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 开始详细监控...")
        print("=" * 60)
        
        max_wait = 300  # 5分钟超时
        start_time = time.time()
        last_status = None
        
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 获取工作流状态
            try:
                status_result = await system.get_workflow_status(workflow_id)
                
                if status_result.get("success"):
                    workflow_data = status_result.get("data", {})
                    overall_status = workflow_data.get("overall_status", "unknown")
                    current_stage = workflow_data.get("current_stage", "unknown")
                    stages = workflow_data.get("stages", [])
                    
                    # 检查状态变化
                    if overall_status != last_status:
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 状态变化: {last_status} → {overall_status}")
                        last_status = overall_status
                    
                    # 显示当前状态
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 工作流状态: {overall_status} | 当前阶段: {current_stage} | 已运行: {elapsed:.1f}s")
                    
                    # 显示各阶段状态
                    for i, stage in enumerate(stages):
                        stage_status = stage.get("status", "unknown")
                        stage_name = stage.get("stage_name", f"Stage {i}")
                        if hasattr(stage, 'start_time') and stage.start_time:
                            stage_duration = current_time - stage.start_time
                            print(f"  └─ {stage_name}: {stage_status} (运行: {stage_duration:.1f}s)")
                        else:
                            print(f"  └─ {stage_name}: {stage_status}")
                    
                    # 检查是否完成
                    if overall_status == "completed":
                        print(f"\n🎉 [{datetime.now().strftime('%H:%M:%S')}] 工作流完成！")
                        break
                        
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 无法获取工作流状态")
                    
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 获取状态失败: {e}")
            
            # 检查超时
            if elapsed > max_wait:
                print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] 超时等待完成 ({max_wait}s)")
                break
                
            # 每10秒检查一次
            await asyncio.sleep(10)
            
        # 获取最终状态
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📋 获取最终状态...")
        try:
            final_status = await system.get_workflow_status(workflow_id)
            if final_status.get("success"):
                workflow_data = final_status.get("data", {})
                print(f"最终状态: {workflow_data.get('overall_status')}")
                print(f"总运行时间: {time.time() - start_time:.1f}s")
                
                # 显示各阶段结果
                stages = workflow_data.get("stages", [])
                results = workflow_data.get("results", {})
                
                print("\n📊 各阶段执行结果:")
                for i, stage in enumerate(stages):
                    stage_name = stage.get("stage_name", f"Stage {i}")
                    stage_status = stage.get("status", "unknown")
                    stage_result = results.get(f"stage_{i}", {})
                    
                    print(f"  {i+1}. {stage_name}: {stage_status}")
                    if stage_result:
                        result_data = stage_result.get("result", {})
                        if result_data:
                            print(f"     结果: {list(result_data.keys())}")
                
        except Exception as e:
            print(f"获取最终状态失败: {e}")
            
        # 关闭系统
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 关闭系统...")
        await system.stop()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 系统关闭成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 监控过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def monitor_agent_communication():
    """监控代理间通信"""
    print("\n🔍 开始监控代理间通信...")
    print("=" * 60)
    
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
        
        # 启动代理
        await coordinator.start()
        await planner.start()
        print("✅ 代理启动成功")
        
        # 等待代理初始化
        await asyncio.sleep(2)
        
        # 检查代理状态
        print("\n📊 代理状态检查:")
        coordinator_status = await coordinator.get_status()
        planner_status = await planner.get_status()
        
        print(f"Coordinator: {coordinator_status}")
        print(f"Planner: {planner_status}")
        
        # 检查消息总线状态
        print("\n📡 消息总线状态:")
        bus_status = await message_bus.get_system_status()
        print(f"注册的代理: {bus_status.get('registered_agents', [])}")
        print(f"消息队列大小: {bus_status.get('message_queue_size', 'N/A')}")
        
        # 测试消息发送
        print("\n📤 测试消息发送...")
        test_message = {
            "task": {
                "id": "test_workflow_stage_0",
                "type": "patent_planning",
                "topic": "测试主题",
                "description": "测试描述"
            }
        }
        
        await coordinator.send_message(
            recipient="planner_agent",
            message_type=MessageType.COORDINATION,
            content=test_message,
            priority=5
        )
        print("✅ 测试消息发送成功")
        
        # 等待消息处理
        await asyncio.sleep(3)
        
        # 检查消息是否被处理
        if hasattr(planner, 'task_history') and planner.task_history:
            print("✅ 消息传递测试成功！planner收到了消息")
            print(f"任务历史: {len(planner.task_history)} 个任务")
        else:
            print("❌ 消息传递测试失败！planner没有收到消息")
            
        # 清理
        await coordinator.stop()
        await planner.stop()
        await message_bus.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ 通信监控失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主监控函数"""
    print("🚀 专利工作流详细监控系统")
    print("=" * 60)
    
    # 监控1: 代理间通信
    comm_result = await monitor_agent_communication()
    
    # 监控2: 完整工作流执行
    workflow_result = await monitor_workflow_execution()
    
    # 输出监控结果
    print("\n" + "=" * 60)
    print("📋 监控结果汇总:")
    print(f"   代理间通信监控: {'✅ 成功' if comm_result else '❌ 失败'}")
    print(f"   完整工作流监控: {'✅ 成功' if workflow_result else '❌ 失败'}")
    
    if comm_result and workflow_result:
        print("\n🎉 所有监控项目成功完成！")
        return 0
    else:
        print("\n⚠️  部分监控项目失败，需要进一步分析")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)