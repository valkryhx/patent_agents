#!/usr/bin/env python3
"""
更详细的planner_agent调试脚本
"""

import asyncio
import sys
import os
import logging
import time
import traceback
import uuid

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.agents.base_agent import TaskResult
from patent_agent_demo.message_bus import Message, MessageType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_planner_detailed():
    """更详细的planner_agent调试"""
    try:
        logger.info("🚀 开始详细调试planner_agent")
        
        # 记录开始时间
        start_time = time.time()
        
        # 步骤1: 创建系统
        logger.info("⏱️ 开始: 创建系统")
        system_start = time.time()
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        system_end = time.time()
        logger.info(f"⏱️ 结束: 创建系统 - 耗时: {system_end - system_start:.2f}秒")
        
        # 步骤2: 获取所有智能体
        logger.info("⏱️ 开始: 获取所有智能体")
        agents_start = time.time()
        
        agents = {}
        agent_names = ['planner_agent', 'searcher_agent', 'discusser_agent', 'writer_agent', 'reviewer_agent', 'rewriter_agent']
        
        for agent_name in agent_names:
            if hasattr(system, 'agents') and agent_name in system.agents:
                agents[agent_name] = system.agents[agent_name]
            elif hasattr(system, agent_name):
                agents[agent_name] = getattr(system, agent_name)
            else:
                logger.error(f"❌ {agent_name} 不可用")
        
        agents_end = time.time()
        logger.info(f"⏱️ 结束: 获取所有智能体 - 耗时: {agents_end - agents_start:.2f}秒")
        logger.info(f"   可用智能体: {list(agents.keys())}")
        
        # 步骤3: 准备任务数据
        logger.info("⏱️ 开始: 准备任务数据")
        data_start = time.time()
        
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
        
        data_end = time.time()
        logger.info(f"⏱️ 结束: 准备任务数据 - 耗时: {data_end - data_start:.2f}秒")
        
        # 步骤4: 通过消息总线发送任务
        logger.info("⏱️ 开始: 通过消息总线发送任务")
        task_start = time.time()
        
        try:
            # 获取消息总线
            broker = system.message_bus_config.broker
            
            # 测试所有智能体
            results = {}
            for agent_name, task_data in agent_tasks.items():
                if agent_name not in agents:
                    logger.error(f"❌ {agent_name} 不可用，跳过")
                    continue
                    
                try:
                    logger.info(f"🔧 测试 {agent_name}...")
                    agent_start = time.time()
                    
                    # 创建任务消息
                    task_message = Message(
                        id=str(uuid.uuid4()),
                        type=MessageType.COORDINATION,
                        sender="test_script",
                        recipient=agent_name,
                        content={
                            "task": task_data,
                            "task_id": str(uuid.uuid4())
                        },
                        timestamp=time.time(),
                        priority=5
                    )
                    
                    # 发送消息
                    await broker.send_message(task_message)
                    logger.info(f"✅ 任务消息已发送到 {agent_name}")
                    
                    # 等待任务完成（最多等待5分钟）
                    wait_start = time.time()
                    max_wait_time = 300  # 5分钟
                    
                    while time.time() - wait_start < max_wait_time:
                        # 检查智能体是否有输出
                        if hasattr(agents[agent_name], 'last_result') and agents[agent_name].last_result:
                            break
                        
                        # 检查消息队列状态
                        if hasattr(agents[agent_name], 'message_queue'):
                            queue_size = agents[agent_name].message_queue.qsize()
                            if queue_size == 0:
                                logger.info(f"    {agent_name} 消息队列为空，可能已完成")
                                break
                        
                        await asyncio.sleep(1)
                    
                    agent_end = time.time()
                    agent_execution_time = agent_end - agent_start
                    
                    if time.time() - wait_start < max_wait_time:
                        logger.info(f"✅ {agent_name} 完成 - 耗时: {agent_execution_time:.2f}秒")
                        results[agent_name] = {"success": True, "execution_time": agent_execution_time}
                    else:
                        logger.error(f"❌ {agent_name} 超时")
                        results[agent_name] = {"success": False, "error": "Timeout"}
                    
                except Exception as e:
                    logger.error(f"❌ 测试 {agent_name} 时出错: {e}")
                    results[agent_name] = {"success": False, "error": str(e)}
                
                # 等待2秒再测试下一个智能体
                await asyncio.sleep(2)
            
            task_end = time.time()
            logger.info(f"⏱️ 结束: 测试所有智能体 - 耗时: {task_end - task_start:.2f}秒")
            
            # 输出测试结果
            success_count = sum(1 for r in results.values() if r.get("success", False))
            total_count = len(results)
            logger.info(f"📊 测试结果: {success_count}/{total_count} 成功")
            
            for agent_name, result in results.items():
                if result.get("success"):
                    logger.info(f"✅ {agent_name}: {result.get('execution_time', 0):.2f}秒")
                else:
                    logger.error(f"❌ {agent_name}: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"❌ 任务执行出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 步骤5: 停止系统
        logger.info("⏱️ 开始: 停止系统")
        stop_start = time.time()
        await system.stop()
        stop_end = time.time()
        logger.info(f"⏱️ 结束: 停止系统 - 耗时: {stop_end - stop_start:.2f}秒")
        
        # 分析哪个步骤耗时最长
        steps = {
            "系统创建": system_end - system_start,
            "获取所有智能体": agents_end - agents_start,
            "准备任务数据": data_end - data_start,
            "测试所有智能体": task_end - task_start,
            "停止系统": stop_end - stop_start
        }
        
        max_step = max(steps, key=steps.get)
        logger.info(f"   耗时最长的步骤: {max_step} ({steps[max_step]:.2f}秒)")
        
        total_time = time.time() - start_time
        logger.info(f"⏱️ 总耗时: {total_time:.2f}秒")
        
        return success_count == total_count
        
    except Exception as e:
        logger.error(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    try:
        logger.info("🔍 开始详细调试")
        
        success = await debug_planner_detailed()
        
        if success:
            logger.info("✅ 调试完成，所有智能体正常")
        else:
            logger.error("❌ 调试完成，部分智能体异常")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())