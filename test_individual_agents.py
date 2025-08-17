#!/usr/bin/env python3
"""
测试各个智能体的脚本
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
    """测试各个智能体"""
    try:
        logger.info("🚀 开始测试各个智能体")
        
        # 创建系统
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 定义每个智能体的任务类型
        agent_tasks = {
            'planner_agent': {
                "type": "patent_planning",
                "topic": "基于智能分层推理的多参数工具自适应调用系统",
                "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
            },
            'searcher_agent': {
                "type": "prior_art_search",
                "topic": "基于智能分层推理的多参数工具自适应调用系统",
                "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
            },
            'discusser_agent': {
                "type": "innovation_discussion",
                "topic": "基于智能分层推理的多参数工具自适应调用系统",
                "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
            },
            'writer_agent': {
                "type": "patent_drafting",
                "topic": "基于智能分层推理的多参数工具自适应调用系统",
                "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
            },
            'reviewer_agent': {
                "type": "patent_review",
                "topic": "基于智能分层推理的多参数工具自适应调用系统",
                "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
            },
            'rewriter_agent': {
                "type": "patent_rewriting",
                "topic": "基于智能分层推理的多参数工具自适应调用系统",
                "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
            }
        }
        
        # 依次测试每个智能体
        results = {}
        for agent_name, task_data in agent_tasks.items():
            try:
                logger.info(f"🔧 测试 {agent_name}...")
                start_time = time.time()
                
                # 获取智能体
                agent = None
                if hasattr(system, 'agents') and agent_name in system.agents:
                    agent = system.agents[agent_name]
                elif hasattr(system, agent_name):
                    agent = getattr(system, agent_name)
                
                if not agent:
                    logger.error(f"❌ {agent_name} 不可用")
                    results[agent_name] = {"success": False, "error": "Agent not found"}
                    continue
                
                # 执行任务（设置5分钟超时）
                try:
                    result: TaskResult = await asyncio.wait_for(
                        agent.execute_task(task_data), 
                        timeout=300
                    )
                    
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    if result.success:
                        logger.info(f"✅ {agent_name} 成功 - 耗时: {execution_time:.2f}秒")
                        results[agent_name] = {
                            "success": True, 
                            "execution_time": execution_time,
                            "data_keys": list(result.data.keys()) if result.data and isinstance(result.data, dict) else []
                        }
                    else:
                        logger.error(f"❌ {agent_name} 失败: {result.error_message}")
                        results[agent_name] = {"success": False, "error": result.error_message}
                        
                except asyncio.TimeoutError:
                    logger.error(f"❌ {agent_name} 超时（5分钟）")
                    results[agent_name] = {"success": False, "error": "Timeout"}
                    
            except Exception as e:
                logger.error(f"❌ 测试 {agent_name} 时出错: {e}")
                results[agent_name] = {"success": False, "error": str(e)}
            
            # 等待5秒再测试下一个智能体
            await asyncio.sleep(5)
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
        # 输出结果统计
        success_count = sum(1 for r in results.values() if r.get("success", False))
        total_count = len(results)
        logger.info(f"📊 测试结果: {success_count}/{total_count} 成功")
        
        for agent_name, result in results.items():
            if result.get("success"):
                logger.info(f"✅ {agent_name}: {result.get('execution_time', 0):.2f}秒")
            else:
                logger.error(f"❌ {agent_name}: {result.get('error', 'Unknown error')}")
        
        return success_count == total_count
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    try:
        success = await test_individual_agents()
        
        if success:
            logger.info("✅ 所有智能体测试成功")
        else:
            logger.error("❌ 部分智能体测试失败")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())