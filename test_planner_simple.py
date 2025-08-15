#!/usr/bin/env python3
"""
简单测试planner_agent的任务执行
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def test_planner_simple():
    """简单测试planner_agent"""
    print("🧪 开始简单测试planner_agent...")
    
    try:
        from patent_agent_demo.agents.planner_agent import PlannerAgent
        
        # 创建planner_agent
        planner = PlannerAgent()
        await planner.start()
        print("✅ planner_agent启动成功")
        
        # 测试执行任务
        print("\n📋 测试执行任务...")
        task_data = {
            "id": "test_task_001",
            "type": "patent_planning",
            "topic": "使用证据图来增强RAG的系统",
            "description": "测试描述"
        }
        
        print("⏳ 开始执行任务...")
        result = await planner.execute_task(task_data)
        
        if result.success:
            print("✅ 任务执行成功！")
            print(f"结果数据: {list(result.data.keys())}")
        else:
            print(f"❌ 任务执行失败: {result.error_message}")
            
        await planner.stop()
        return result.success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_planner_simple())
    print(f"\n测试结果: {'✅ 成功' if success else '❌ 失败'}")
    sys.exit(0 if success else 1)