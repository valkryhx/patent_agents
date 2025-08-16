#!/usr/bin/env python3
"""
依次单独测试每个智能体
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

async def test_single_agent(agent_name: str, task_type: str, task_data: dict):
    """单独测试一个智能体"""
    try:
        logger.info(f"🚀 开始测试智能体: {agent_name}")
        logger.info(f"   任务类型: {task_type}")
        
        # 创建系统
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 获取智能体
        agent = None
        if hasattr(system, 'agents') and agent_name in system.agents:
            agent = system.agents[agent_name]
        elif hasattr(system, agent_name):
            agent = getattr(system, agent_name)
        
        if not agent:
            logger.error(f"❌ 智能体 {agent_name} 不可用")
            await system.stop()
            return {"success": False, "error": "Agent not available"}
        
        logger.info(f"✅ 智能体 {agent_name} 可用")
        
        # 执行任务
        start_time = time.time()
        logger.info(f"🔧 开始执行任务...")
        
        result: TaskResult = await agent.execute_task(task_data)
        
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
        
        if result.success:
            logger.info(f"✅ {agent_name} 任务成功")
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
            
            result_data = {"success": True, "execution_time": execution_time, "data": result.data}
        else:
            logger.error(f"❌ {agent_name} 任务失败: {result.error_message}")
            result_data = {"success": False, "error": result.error_message, "execution_time": execution_time}
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
        return result_data
        
    except Exception as e:
        logger.error(f"❌ 测试 {agent_name} 时出错: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def main():
    """主函数 - 依次测试每个智能体"""
    try:
        logger.info("🔍 开始依次测试每个智能体")
        
        # 测试主题
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        
        # 定义要测试的智能体
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
        
        # 依次测试每个智能体
        for i, (agent_name, task_type, task_data) in enumerate(agents_to_test, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"📋 测试进度: {i}/{len(agents_to_test)}")
            logger.info(f"{'='*60}")
            
            result = await test_single_agent(agent_name, task_type, task_data)
            results[agent_name] = result
            
            # 等待一下再测试下一个
            if i < len(agents_to_test):
                logger.info("⏳ 等待5秒后测试下一个智能体...")
                await asyncio.sleep(5)
        
        # 输出总结
        logger.info(f"\n{'='*60}")
        logger.info("📊 测试总结:")
        logger.info(f"{'='*60}")
        
        success_count = 0
        for agent_name, result in results.items():
            status = "✅ 成功" if result["success"] else "❌ 失败"
            logger.info(f"   {agent_name}: {status}")
            if not result["success"]:
                logger.info(f"      错误: {result.get('error', 'Unknown error')}")
            else:
                logger.info(f"      执行时间: {result.get('execution_time', 0):.2f}秒")
                success_count += 1
        
        logger.info(f"\n📈 总体结果: {success_count}/{len(agents_to_test)} 个智能体测试成功")
        
        # 检查是否有专利文件生成
        patent_files = [f for f in os.listdir('.') if f.startswith('enhanced_patent_') and f.endswith('.md')]
        if patent_files:
            logger.info(f"📄 最终发现专利文件: {patent_files}")
        else:
            logger.info("📄 最终没有发现专利文件")
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())