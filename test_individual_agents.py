#!/usr/bin/env python3
"""
单独测试每个智能体
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

async def test_individual_agents():
    """单独测试每个智能体"""
    try:
        logger.info("🚀 开始单独测试每个智能体")
        
        # 创建系统
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 测试主题
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        
        # 测试每个智能体
        agents_to_test = [
            ("planner_agent", "patent_planning", {
                "type": "patent_planning",
                "topic": topic,
                "description": description
            }),
            ("searcher_agent", "prior_art_search", {
                "type": "prior_art_search",
                "topic": topic,
                "description": description
            }),
            ("discusser_agent", "innovation_discussion", {
                "type": "innovation_discussion",
                "topic": topic,
                "description": description
            }),
            ("writer_agent", "patent_drafting", {
                "type": "patent_drafting",
                "topic": topic,
                "description": description
            }),
            ("reviewer_agent", "patent_review", {
                "type": "patent_review",
                "topic": topic,
                "description": description
            }),
            ("rewriter_agent", "patent_rewrite", {
                "type": "patent_rewrite",
                "topic": topic,
                "description": description
            })
        ]
        
        results = {}
        
        for agent_name, task_type, task_data in agents_to_test:
            logger.info(f"🔍 测试智能体: {agent_name}")
            logger.info(f"   任务类型: {task_type}")
            
            try:
                # 获取智能体
                agent = None
                if hasattr(system, 'agents') and agent_name in system.agents:
                    agent = system.agents[agent_name]
                elif hasattr(system, agent_name):
                    agent = getattr(system, agent_name)
                
                if not agent:
                    logger.error(f"❌ 智能体 {agent_name} 不可用")
                    results[agent_name] = {"success": False, "error": "Agent not available"}
                    continue
                
                logger.info(f"✅ 智能体 {agent_name} 可用")
                
                # 执行任务
                start_time = time.time()
                result: TaskResult = await agent.execute_task(task_data)
                end_time = time.time()
                
                execution_time = end_time - start_time
                logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
                
                if result.success:
                    logger.info(f"✅ {agent_name} 任务成功")
                    logger.info(f"   结果类型: {type(result.data)}")
                    if result.data:
                        logger.info(f"   数据键: {list(result.data.keys()) if isinstance(result.data, dict) else 'Not a dict'}")
                    results[agent_name] = {"success": True, "execution_time": execution_time, "data": result.data}
                else:
                    logger.error(f"❌ {agent_name} 任务失败: {result.error_message}")
                    results[agent_name] = {"success": False, "error": result.error_message, "execution_time": execution_time}
                
            except Exception as e:
                logger.error(f"❌ 测试 {agent_name} 时出错: {e}")
                import traceback
                traceback.print_exc()
                results[agent_name] = {"success": False, "error": str(e)}
            
            logger.info("-" * 50)
        
        # 输出总结
        logger.info("📊 测试总结:")
        for agent_name, result in results.items():
            status = "✅ 成功" if result["success"] else "❌ 失败"
            logger.info(f"   {agent_name}: {status}")
            if not result["success"]:
                logger.info(f"      错误: {result.get('error', 'Unknown error')}")
            else:
                logger.info(f"      执行时间: {result.get('execution_time', 0):.2f}秒")
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    asyncio.run(test_individual_agents())