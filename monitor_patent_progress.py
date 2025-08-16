#!/usr/bin/env python3
"""
专利撰写进度监控脚本
Monitor patent writing progress every 5 minutes
"""

import asyncio
import time
import os
from datetime import datetime
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def monitor_progress():
    """监控专利撰写进度"""
    print("🔍 开始监控专利撰写进度...")
    
    # 初始化系统
    system = PatentAgentSystem()
    await system.start()
    
    try:
        # 查找最新的工作流
        workflows = await system.coordinator.execute_task({
            "type": "get_workflow_summary"
        })
        
        if not workflows:
            print("❌ 未找到正在进行的专利撰写工作流")
            return
        
        # 获取最新的工作流ID
        latest_workflow = workflows[-1]
        workflow_id = latest_workflow.get("workflow_id")
        
        if not workflow_id:
            print("❌ 无法获取工作流ID")
            return
        
        print(f"📋 监控工作流ID: {workflow_id}")
        
        check_count = 0
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n🕐 第{check_count}次检查 - {current_time}")
            
            try:
                # 获取工作流状态
                status = await system.coordinator.execute_task({
                    "type": "monitor_workflow",
                    "workflow_id": workflow_id
                })
                
                if status.get("status") == "completed":
                    print("🎉 专利撰写已完成！")
                    print(f"📁 导出路径: /workspace/output/multi_parameter_tool_patent_{workflow_id[:8]}.md")
                    break
                elif status.get("status") == "failed":
                    print(f"❌ 专利撰写失败: {status.get('error', '未知错误')}")
                    break
                else:
                    current_stage = status.get("current_stage", "未知")
                    progress = status.get("progress", 0)
                    total_stages = status.get("total_stages", 0)
                    current_stage_index = status.get("current_stage_index", 0)
                    
                    print(f"📊 工作流状态: {status.get('status', '进行中')}")
                    print(f"🎯 当前阶段: {current_stage} ({current_stage_index + 1}/{total_stages})")
                    print(f"📈 总体进度: {progress}%")
                    
                    # 检查是否有卡顿
                    if check_count > 1 and progress == 0:
                        print("⚠️ 警告: 进度可能卡顿，建议检查系统状态")
                    
                    # 显示详细阶段信息
                    stages = status.get("stages", [])
                    if stages:
                        print("📋 阶段详情:")
                        for i, stage in enumerate(stages):
                            stage_status = "✅" if stage.get("status") == "completed" else "⏳" if stage.get("status") == "running" else "⏸️"
                            print(f"   {stage_status} {stage.get('stage_name', '未知阶段')}: {stage.get('status', 'pending')}")
                
                # 检查输出目录
                output_dir = "/workspace/output"
                if os.path.exists(output_dir):
                    files = os.listdir(output_dir)
                    if files:
                        print(f"📁 输出目录文件: {len(files)} 个文件")
                        for file in files[:3]:  # 只显示前3个文件
                            print(f"   📄 {file}")
                        if len(files) > 3:
                            print(f"   ... 还有 {len(files) - 3} 个文件")
                
            except Exception as e:
                print(f"❌ 检查进度时出错: {e}")
            
            print(f"⏰ 等待5分钟后进行下一次检查...")
            await asyncio.sleep(300)  # 5分钟
            
    except Exception as e:
        print(f"❌ 监控过程中出错: {e}")
    finally:
        await system.stop()

if __name__ == "__main__":
    asyncio.run(monitor_progress())