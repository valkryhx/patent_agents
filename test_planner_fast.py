#!/usr/bin/env python3
"""
使用测试模式快速测试planner_agent
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

async def test_planner_fast():
    """使用测试模式快速测试planner_agent"""
    try:
        logger.info("🚀 开始快速测试 planner_agent（测试模式）")
        
        # 创建系统（测试模式）
        system = PatentAgentSystem(test_mode=True)
        await system.start()
        logger.info("✅ 系统启动成功（测试模式）")
        
        # 获取planner智能体
        planner = None
        if hasattr(system, 'agents') and 'planner_agent' in system.agents:
            planner = system.agents['planner_agent']
        elif hasattr(system, 'planner_agent'):
            planner = getattr(system, 'planner_agent')
        
        if not planner:
            logger.error("❌ planner_agent 不可用")
            await system.stop()
            return False
        
        logger.info("✅ planner_agent 可用")
        
        # 测试数据
        task_data = {
            "type": "patent_planning",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        }
        
        # 执行任务
        start_time = time.time()
        logger.info("🔧 开始执行任务（测试模式）...")
        
        result: TaskResult = await planner.execute_task(task_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
        
        if result.success:
            logger.info("✅ planner_agent 任务成功")
            logger.info(f"   结果类型: {type(result.data)}")
            if result.data:
                if isinstance(result.data, dict):
                    logger.info(f"   数据键: {list(result.data.keys())}")
                else:
                    logger.info(f"   数据内容: {str(result.data)[:200]}...")
            else:
                logger.info("   数据为空")
            
            # 检查是否有新的专利内容生成
            patent_files = [f for f in os.listdir('.') if f.startswith('enhanced_patent_') and f.endswith('.md')]
            if patent_files:
                logger.info(f"📄 发现专利文件: {patent_files}")
                for file in patent_files:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        logger.info(f"   文件大小: {len(content)} 字节")
                        logger.info(f"   内容预览: {content[:100]}...")
            else:
                logger.info("📄 没有发现新的专利文件")
            
            success = True
        else:
            logger.error(f"❌ planner_agent 任务失败: {result.error_message}")
            success = False
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 测试 planner_agent 时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    try:
        logger.info("🔍 开始快速测试 planner_agent")
        
        success = await test_planner_fast()
        
        if success:
            logger.info("✅ planner_agent 快速测试成功")
        else:
            logger.error("❌ planner_agent 快速测试失败")
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())