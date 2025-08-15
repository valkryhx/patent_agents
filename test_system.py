#!/usr/bin/env python3
"""
测试专利代理系统启动
"""

import asyncio
import os
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def test_system():
    """测试系统启动"""
    try:
        print("开始测试专利代理系统...")
        
        # 设置环境变量
        os.environ["PATENT_TOPIC"] = "测试专利主题"
        os.environ["PATENT_DESC"] = "测试专利描述"
        
        # 创建系统
        system = PatentAgentSystem()
        print("系统创建成功")
        
        # 启动系统
        await system.start()
        print("系统启动成功")
        
        # 执行工作流
        result = await system.execute_workflow(
            topic="测试专利主题",
            description="测试专利描述"
        )
        print(f"工作流执行结果: {result}")
        
        # 停止系统
        await system.stop()
        print("系统停止成功")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_system())