#!/usr/bin/env python3

import sys
import os
import asyncio
import logging
import time

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.message_bus import Message, MessageType

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_system_startup():
    """测试系统启动"""
    try:
        logger.info("🚀 开始系统启动测试")
        
        # 1. 创建系统（测试模式）
        logger.info("📦 创建专利代理系统...")
        system = PatentAgentSystem(test_mode=True)
        
        # 2. 启动系统
        logger.info("🚀 启动系统...")
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 3. 检查系统状态
        logger.info("🔍 检查系统状态...")
        status = await system.get_system_status()
        logger.info(f"系统状态: {status}")
        
        # 4. 检查协调器
        logger.info("🔍 检查协调器...")
        if system.coordinator:
            logger.info("✅ 协调器可用")
            logger.info(f"协调器状态: {system.coordinator.status}")
        else:
            logger.error("❌ 协调器不可用")
            return False
        
        # 5. 检查智能体
        logger.info("🔍 检查智能体...")
        logger.info(f"智能体数量: {len(system.agents)}")
        for agent_name, agent in system.agents.items():
            logger.info(f"  - {agent_name}: {type(agent).__name__}, 状态: {agent.status}")
        
        # 6. 测试消息总线
        logger.info("🔍 测试消息总线...")
        broker = system.message_bus_config.broker
        logger.info(f"消息总线状态: {await broker.get_system_status()}")
        
        # 7. 测试工作流启动
        logger.info("🔍 测试工作流启动...")
        try:
            workflow_id = await system.execute_workflow(
                topic="测试主题",
                description="测试描述",
                workflow_type="enhanced"
            )
            logger.info(f"✅ 工作流启动成功: {workflow_id}")
            
            # 8. 检查工作流状态
            logger.info("🔍 检查工作流状态...")
            workflow_status = await system.get_workflow_status(workflow_id)
            logger.info(f"工作流状态: {workflow_status}")
            
        except Exception as e:
            logger.error(f"❌ 工作流启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 9. 停止系统
        logger.info("🛑 停止系统...")
        await system.stop()
        logger.info("✅ 系统停止成功")
        
        logger.info("🎉 所有测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_system_startup())
    if success:
        print("✅ 系统启动测试成功")
    else:
        print("❌ 系统启动测试失败")
        sys.exit(1)