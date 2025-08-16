#!/usr/bin/env python3
"""
检查专利撰写系统状态
Check patent writing system status
"""

import asyncio
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def check_system_status():
    """检查系统状态"""
    print("🔍 检查专利撰写系统状态...")
    
    try:
        # 初始化系统
        system = PatentAgentSystem()
        await system.start()
        
        print("✅ 系统初始化成功")
        
        # 检查所有代理状态
        agents_status_result = await system.coordinator.execute_task({
            "type": "get_all_agents_status"
        })
        
        if agents_status_result.success:
            print(f"📊 代理状态: {agents_status_result.data}")
        else:
            print(f"❌ 获取代理状态失败: {agents_status_result.error_message}")
        
        # 检查工作流摘要
        workflows_result = await system.coordinator.execute_task({
            "type": "get_workflow_summary"
        })
        
        if workflows_result.success:
            workflows_data = workflows_result.data
            print(f"📋 工作流摘要: {workflows_data}")
            
            # 检查是否有活跃工作流
            if workflows_data.get("active_workflows", 0) > 0:
                latest_workflow = workflows_data.get("latest_workflow")
                if latest_workflow:
                    print(f"📋 最新工作流: {latest_workflow}")
                    
                    # 检查最新工作流状态
                    workflow_id = latest_workflow.get("workflow_id")
                    if workflow_id:
                        status_result = await system.coordinator.execute_task({
                            "type": "monitor_workflow",
                            "workflow_id": workflow_id
                        })
                        if status_result.success:
                            print(f"📊 工作流状态: {status_result.data}")
                        else:
                            print(f"❌ 获取工作流状态失败: {status_result.error_message}")
            else:
                print("📋 当前没有活跃的工作流")
        else:
            print(f"❌ 获取工作流摘要失败: {workflows_result.error_message}")
        
        await system.stop()
        print("✅ 系统状态检查完成")
        
    except Exception as e:
        print(f"❌ 系统状态检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_system_status())