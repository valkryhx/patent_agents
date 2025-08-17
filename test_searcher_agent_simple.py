#!/usr/bin/env python3
"""
简单测试searcher_agent是否能正确接收和处理消息
"""

import asyncio
import sys
import os
import logging
import time

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.agents.base_agent import TaskResult
from patent_agent_demo.message_bus import Message, MessageType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_searcher_agent():
    """测试searcher_agent"""
    try:
        logger.info("🚀 开始测试searcher_agent")
        
        # 创建系统
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 获取searcher_agent
        searcher = None
        if hasattr(system, 'agents') and 'searcher_agent' in system.agents:
            searcher = system.agents['searcher_agent']
        elif hasattr(system, 'searcher_agent'):
            searcher = getattr(system, 'searcher_agent')
        
        if not searcher:
            logger.error("❌ searcher_agent 不可用")
            await system.stop()
            return False
        
        logger.info("✅ searcher_agent 可用")
        logger.info(f"   capabilities: {searcher.capabilities}")
        logger.info(f"   name: {searcher.name}")
        logger.info(f"   status: {searcher.status}")
        
        # 测试直接调用execute_task
        logger.info("🔧 测试直接调用execute_task...")
        task_data = {
            "type": "prior_art_search",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
        }
        
        start_time = time.time()
        try:
            result: TaskResult = await searcher.execute_task(task_data)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
            
            if result.success:
                logger.info("✅ searcher_agent.execute_task 成功")
                logger.info(f"   数据: {list(result.data.keys()) if result.data else 'None'}")
            else:
                logger.error(f"❌ searcher_agent.execute_task 失败: {result.error_message}")
                
        except Exception as e:
            logger.error(f"❌ searcher_agent.execute_task 出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试通过消息总线发送消息
        logger.info("🔧 测试通过消息总线发送消息...")
        try:
            # 创建消息
            message = Message(
                id=str(time.time()),
                type=MessageType.COORDINATION,
                sender="test_sender",
                recipient="searcher_agent",
                content={
                    "task": {
                        "id": f"test_task_{time.time()}",
                        "type": "prior_art_search",
                        "topic": "基于智能分层推理的多参数工具自适应调用系统",
                        "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
                    }
                },
                timestamp=time.time(),
                priority=5
            )
            
            # 发送消息
            logger.info("📤 发送消息到searcher_agent...")
            await system.message_bus_config.broker.send_message(message)
            
            # 等待一段时间
            logger.info("⏳ 等待消息处理...")
            await asyncio.sleep(10)
            
            logger.info("✅ 消息发送完成")
            
        except Exception as e:
            logger.error(f"❌ 消息发送出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    try:
        logger.info("🔍 开始测试searcher_agent")
        
        success = await test_searcher_agent()
        
        if success:
            logger.info("✅ searcher_agent测试成功")
        else:
            logger.error("❌ searcher_agent测试失败")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())