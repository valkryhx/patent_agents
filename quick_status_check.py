#!/usr/bin/env python3
"""
快速状态检查脚本
Quick status check script
"""

import asyncio
import os
from datetime import datetime
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def quick_check():
    """快速检查系统状态"""
    print(f"🔍 快速状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 初始化系统
        system = PatentAgentSystem()
        await system.start()
        
        # 检查工作流摘要
        workflows_result = await system.coordinator.execute_task({
            "type": "get_workflow_summary"
        })
        
        if workflows_result.success:
            workflows_data = workflows_result.data
            print(f"📋 工作流状态: {workflows_data}")
            
            # 检查是否有活跃工作流
            if workflows_data.get("active_workflows", 0) > 0:
                latest_workflow = workflows_data.get("latest_workflow")
                if latest_workflow:
                    print(f"🎯 最新工作流: {latest_workflow}")
                    
                    # 检查最新工作流状态
                    workflow_id = latest_workflow.get("workflow_id")
                    if workflow_id:
                        status_result = await system.coordinator.execute_task({
                            "type": "monitor_workflow",
                            "workflow_id": workflow_id
                        })
                        if status_result.success:
                            status_data = status_result.data
                            print(f"📊 工作流详情: {status_data}")
                        else:
                            print(f"❌ 获取工作流状态失败: {status_result.error_message}")
            else:
                print("📋 当前没有活跃的工作流")
        else:
            print(f"❌ 获取工作流摘要失败: {workflows_result.error_message}")
        
        # 检查输出目录
        output_dir = "/workspace/output"
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            print(f"📁 输出目录文件: {len(files)} 个")
            
            progress_dir = os.path.join(output_dir, "progress")
            if os.path.exists(progress_dir):
                progress_dirs = [d for d in os.listdir(progress_dir) if os.path.isdir(os.path.join(progress_dir, d))]
                print(f"📂 进度目录: {len(progress_dirs)} 个")
                for i, dir_name in enumerate(progress_dirs[-3:], 1):  # 显示最新的3个
                    print(f"   {i}. {dir_name}")
        
        await system.stop()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    asyncio.run(quick_check())