#!/usr/bin/env python3
"""
性能测试脚本 - 验证agent优化效果
"""

import asyncio
import time
import os
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def test_writer_agent_performance():
    """测试writer_agent的性能"""
    print("🚀 开始测试writer_agent性能...")
    
    # 设置测试环境
    os.environ["PATENT_TOPIC"] = "测试专利主题"
    os.environ["PATENT_DESC"] = "测试专利描述"
    
    system = PatentAgentSystem()
    await system.start()
    
    start_time = time.time()
    
    try:
        # 启动工作流
        start = await system.coordinator.execute_task({
            "type": "start_patent_workflow",
            "topic": "测试专利主题",
            "description": "测试专利描述",
            "workflow_type": "standard"
        })
        
        if not start.success:
            print(f"❌ 启动工作流失败: {start.error_message}")
            return
            
        workflow_id = start.data.get("workflow_id")
        print(f"✅ 工作流启动成功: {workflow_id}")
        
        # 监控进度
        stage_times = {}
        current_stage = 0
        
        while True:
            status = await system.coordinator.execute_task({
                "type": "monitor_workflow",
                "workflow_id": workflow_id
            })
            
            if status.success:
                wf = status.data.get("workflow")
                overall_status = None
                if hasattr(wf, "overall_status"):
                    overall_status = getattr(wf, "overall_status", None)
                elif isinstance(wf, dict):
                    overall_status = wf.get("overall_status")
                    
                # 检查阶段变化
                if hasattr(wf, "current_stage"):
                    new_stage = getattr(wf, "current_stage", 0)
                    if new_stage != current_stage:
                        stage_time = time.time() - start_time
                        stage_times[f"stage_{current_stage}"] = stage_time
                        print(f"⏱️  阶段 {current_stage} 完成，耗时: {stage_time:.2f}秒")
                        current_stage = new_stage
                        
                if overall_status == "completed":
                    total_time = time.time() - start_time
                    print(f"🎉 工作流完成！总耗时: {total_time:.2f}秒")
                    print("📊 各阶段耗时:")
                    for stage, stage_time in stage_times.items():
                        print(f"   {stage}: {stage_time:.2f}秒")
                    break
                    
            elapsed = time.time() - start_time
            if elapsed > 1800:  # 30分钟超时
                print("⏰ 测试超时")
                break
                
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        
    finally:
        await system.stop()

async def test_api_response_time():
    """测试API响应时间"""
    print("🔍 测试API响应时间...")
    
    try:
        from patent_agent_demo.glm_client import GLMA2AClient
        
        client = GLMA2AClient()
        
        # 测试简单查询
        start_time = time.time()
        response = await client._generate_response("你好")
        response_time = time.time() - start_time
        
        print(f"✅ API响应时间: {response_time:.2f}秒")
        print(f"📝 响应内容长度: {len(response)} 字符")
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")

async def main():
    """主测试函数"""
    print("🧪 开始性能测试...")
    
    # 测试API响应时间
    await test_api_response_time()
    
    # 测试writer_agent性能
    await test_writer_agent_performance()
    
    print("✅ 性能测试完成")

if __name__ == "__main__":
    asyncio.run(main())