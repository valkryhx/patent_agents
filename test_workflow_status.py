#!/usr/bin/env python3

import sys
import os
import asyncio
import logging

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_workflow_status():
    """检查工作流状态"""
    try:
        logger.info("🔍 检查工作流状态...")
        
        # 创建系统（测试模式）
        system = PatentAgentSystem(test_mode=True)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 检查系统状态
        status = await system.get_system_status()
        logger.info(f"系统状态: {status}")
        
        # 检查协调器
        if system.coordinator:
            logger.info("✅ 协调器可用")
            logger.info(f"协调器状态: {system.coordinator.status}")
            
            # 检查活跃的工作流
            active_workflows = system.coordinator.active_workflows
            logger.info(f"活跃工作流数量: {len(active_workflows)}")
            
            for workflow_id, workflow in active_workflows.items():
                logger.info(f"工作流ID: {workflow_id}")
                logger.info(f"  主题: {workflow.topic}")
                logger.info(f"  状态: {workflow.overall_status}")
                logger.info(f"  当前阶段: {workflow.current_stage}")
                logger.info(f"  阶段数量: {len(workflow.stages)}")
                
                for i, stage in enumerate(workflow.stages):
                    logger.info(f"    阶段 {i}: {stage.stage_name} - {stage.status}")
        else:
            logger.error("❌ 协调器不可用")
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统停止成功")
        
    except Exception as e:
        logger.error(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_workflow_status())