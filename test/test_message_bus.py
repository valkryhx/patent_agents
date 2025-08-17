#!/usr/bin/env python3
"""
Test Message Bus Functionality
测试消息总线功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.message_bus import message_bus_config, Message, MessageType
from patent_agent_demo.agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    """测试智能体"""
    
    def __init__(self, name: str):
        super().__init__(name, ["test"], test_mode=True)
        
    async def execute_task(self, task_data):
        """执行测试任务"""
        return {"success": True, "data": {"message": f"Task completed by {self.name}"}}
        
    async def _execute_test_task(self, task_data):
        """执行测试任务"""
        return {"success": True, "data": {"message": f"Test task completed by {self.name}"}}

async def test_message_bus():
    """测试消息总线功能"""
    print("🚀 开始测试消息总线功能")
    
    # 初始化消息总线
    await message_bus_config.initialize()
    
    # 创建测试智能体
    sender = TestAgent("sender_agent")
    receiver = TestAgent("receiver_agent")
    
    # 启动智能体
    await sender.start()
    await receiver.start()
    
    print("✅ 智能体启动完成")
    
    # 等待智能体完全启动
    await asyncio.sleep(2)
    
    # 发送测试消息
    print("📤 发送测试消息...")
    await sender.send_message("receiver_agent", MessageType.STATUS, {
        "test": True,
        "message": "Hello from sender!"
    })
    
    # 等待消息处理
    await asyncio.sleep(3)
    
    # 检查消息总线状态
    status = await message_bus_config.broker.get_system_status()
    print(f"📊 消息总线状态: {status}")
    
    # 停止智能体
    await sender.stop()
    await receiver.stop()
    
    print("✅ 消息总线测试完成")

if __name__ == "__main__":
    asyncio.run(test_message_bus())