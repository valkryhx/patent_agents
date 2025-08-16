#!/usr/bin/env python3
"""
Debug script to test workflow creation and monitoring
"""

import asyncio
import time
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def debug_workflow():
    """Debug workflow creation and monitoring"""
    
    print("🔍 调试工作流创建和监控")
    
    # Initialize the patent agent system
    system = PatentAgentSystem()
    await system.start()
    
    try:
        print("✅ 系统启动成功")
        
        # Test topic and description
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = """一种基于智能分层推理的多参数工具自适应调用系统，解决现有技术中多参数工具调用成功率低的问题。技术方案包括智能分层推理引擎、自适应参数收集策略、动态调用策略优化和智能错误诊断与恢复。技术效果：调用成功率从30%提升至85%以上，减少参数收集时间60%，错误诊断准确率90%。"""
        
        print(f"📋 主题: {topic}")
        print(f"📝 描述: {description}")
        
        # Try to start the workflow
        print("🔄 尝试启动工作流...")
        workflow_id = await system.execute_workflow(topic, description)
        
        print(f"📊 工作流ID类型: {type(workflow_id)}")
        print(f"📊 工作流ID值: {workflow_id}")
        
        if workflow_id:
            print(f"✅ 工作流启动成功，ID: {workflow_id}")
            
            # Wait a bit
            await asyncio.sleep(2)
            
            # Check workflow status with explicit workflow_id
            print(f"🔍 检查工作流状态，ID: {workflow_id}")
            status_result = await system.coordinator.execute_task({
                "type": "monitor_workflow",
                "workflow_id": workflow_id
            })
            
            print(f"📊 状态结果类型: {type(status_result)}")
            print(f"📊 状态结果: {status_result}")
            
            if status_result.success:
                print(f"✅ 获取工作流状态成功: {status_result.data}")
            else:
                print(f"❌ 获取工作流状态失败: {status_result.error_message}")
        else:
            print("❌ 工作流启动失败")
            
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop the system
        await system.stop()
        print("🛑 系统已停止")

if __name__ == "__main__":
    asyncio.run(debug_workflow())