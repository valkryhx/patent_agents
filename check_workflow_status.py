#!/usr/bin/env python3
"""
检查工作流状态
"""

import asyncio
import os
import sys

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def check_workflow_status():
    """检查工作流状态"""
    try:
        print("🔍 检查工作流状态...")
        
        from patent_agent_demo.patent_agent_system import PatentAgentSystem
        
        # 创建系统实例
        system = PatentAgentSystem()
        
        print("🚀 启动专利代理系统...")
        await system.start()
        
        print("✅ 系统启动成功")
        print(f"🤖 已启动的Agent数量: {len(system.agents)}")
        
        # 检查coordinator状态
        if system.coordinator:
            print("📋 Coordinator状态: 正常")
            
            # 尝试启动一个简单的工作流
            print("🔄 尝试启动测试工作流...")
            start_result = await system.coordinator.execute_task({
                "type": "start_patent_workflow",
                "topic": "测试主题",
                "description": "测试描述",
                "workflow_type": "standard"
            })
            
            if start_result.success:
                print(f"✅ 测试工作流启动成功: {start_result.data.get('workflow_id')}")
            else:
                print(f"❌ 测试工作流启动失败: {start_result.error_message}")
        else:
            print("❌ Coordinator未找到")
        
        # 停止系统
        await system.stop()
        print("🛑 系统已停止")
        
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_workflow_status())