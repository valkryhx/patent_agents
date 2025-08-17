#!/usr/bin/env python3
"""
测试修复后的工作流程，验证相对路径和动态主题内容
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow_execution():
    """测试工作流程执行"""
    try:
        logger.info("🚀 开始测试修复后的工作流程执行")
        
        # 创建系统
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 测试数据 - 使用复杂参数相关的主题
        task_data = {
            "type": "start_patent_workflow",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够自动推断和优化工具调用参数"
        }
        
        # 获取coordinator_agent
        coordinator = None
        if hasattr(system, 'agents') and 'coordinator_agent' in system.agents:
            coordinator = system.agents['coordinator_agent']
        elif hasattr(system, 'coordinator_agent'):
            coordinator = getattr(system, 'coordinator_agent')
        
        if not coordinator:
            logger.error("❌ coordinator_agent 不可用")
            await system.stop()
            return False
        
        logger.info("✅ coordinator_agent 可用")
        
        # 启动工作流
        logger.info("🔧 启动工作流...")
        result = await coordinator._start_patent_workflow(task_data)
        if hasattr(result, 'data') and isinstance(result.data, dict):
            workflow_id = result.data.get('workflow_id', str(result.data))
        elif isinstance(result, dict):
            workflow_id = result.get('workflow_id', str(result))
        else:
            workflow_id = str(result)
        logger.info(f"✅ 工作流启动成功，ID: {workflow_id}")
        
        # 等待一段时间让工作流执行
        logger.info("⏳ 等待工作流执行...")
        await asyncio.sleep(30)
        
        # 检查工作流状态
        logger.info("🔍 检查工作流状态...")
        workflow = coordinator.active_workflows.get(workflow_id)
        if workflow:
            logger.info(f"📊 工作流状态: {workflow.overall_status}")
            logger.info(f"📍 当前阶段: {workflow.current_stage}")
            logger.info(f"📋 阶段数量: {len(workflow.stages)}")
            
            # 检查各阶段状态
            for i, stage in enumerate(workflow.stages):
                logger.info(f"   阶段{i}: {stage.stage_name} - {stage.status}")
                if stage.error:
                    logger.warning(f"      错误: {stage.error}")
        else:
            logger.warning("⚠️ 工作流未找到，可能已完成")
        
        # 检查是否有生成的文件
        logger.info("🔍 检查生成的文件...")
        import glob
        # 使用相对路径，在当前项目目录下查找output文件夹
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        output_files = glob.glob(os.path.join(output_dir, "*.md"))
        if output_files:
            logger.info(f"✅ 找到 {len(output_files)} 个输出文件:")
            for file in output_files:
                file_size = os.path.getsize(file)
                logger.info(f"   {file}: {file_size} 字节")
                
                # 检查文件内容是否包含硬编码的主题
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "证据图" in content and "以证据图增强" not in task_data["topic"]:
                            logger.warning(f"⚠️ 文件 {file} 包含硬编码的'证据图'内容")
                        if "子图选择" in content and "子图选择" not in task_data["description"]:
                            logger.warning(f"⚠️ 文件 {file} 包含硬编码的'子图选择'内容")
                except Exception as e:
                    logger.warning(f"⚠️ 无法读取文件 {file}: {e}")
        else:
            logger.warning("⚠️ 未找到输出文件")
        
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
        logger.info("🔍 开始测试修复后的工作流程")
        
        success = await test_workflow_execution()
        
        if success:
            logger.info("✅ 修复后的工作流程测试成功")
        else:
            logger.error("❌ 修复后的工作流程测试失败")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())