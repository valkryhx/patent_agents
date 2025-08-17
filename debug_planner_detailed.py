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
            agent = None
            if hasattr(system, 'agents') and agent_name in system.agents:
                agent = system.agents[agent_name]
            elif hasattr(system, agent_name):
                agent = getattr(system, agent_name)
            
            if agent:
                agents[agent_name] = agent
                logger.info(f"✅ {agent_name} 可用")
            else:
                logger.error(f"❌ {agent_name} 不可用")
        
        agents_end = time.time()
        logger.info(f"⏱️ 结束: 获取所有智能体 - 耗时: {agents_end - agents_start:.2f}秒")
        
        if not agents:
            logger.error("❌ 没有可用的智能体")
            await system.stop()
            return False
        
        # 步骤3: 准备任务数据
        logger.info("⏱️ 开始: 准备任务数据")
        data_start = time.time()
        task_data = {
            "type": "patent_planning",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        }
        data_end = time.time()
        logger.info(f"⏱️ 结束: 准备任务数据 - 耗时: {data_end - data_start:.2f}秒")
        
        # 步骤4: 测试所有智能体
        logger.info("⏱️ 开始: 测试所有智能体")
        task_start = time.time()
        
        try:
            # 获取消息总线
            broker = system.message_bus_config.broker
            
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
            
            # 测试每个智能体
            results = {}
            for agent_name in agents.keys():
                if agent_name in agent_tasks:
                    logger.info(f"🔧 开始测试 {agent_name}")
                    agent_start = time.time()
                    
                    # 创建任务消息
                    task_message = Message(
                        id=str(uuid.uuid4()),
                        type=MessageType.COORDINATION,
                        sender="test_script",
                        recipient=agent_name,
                        content={
                            "task": agent_tasks[agent_name],
                            "task_id": str(uuid.uuid4())
                        },
                        timestamp=time.time(),
                        priority=5
                    )
                    
                    # 发送消息
                    await broker.send_message(task_message)
                    logger.info(f"✅ 任务消息已发送到 {agent_name}")
                    
                    # 等待任务完成
                    max_wait_time = 300  # 5分钟
                    wait_time = 0
                    check_interval = 5  # 每5秒检查一次
                    
                    while wait_time < max_wait_time:
                        await asyncio.sleep(check_interval)
                        wait_time += check_interval
                        
                        # 检查智能体状态
                        agent_status = await broker.get_agent_status(agent_name)
                        if agent_status:
                            logger.info(f"{agent_name}状态: {agent_status.status.value}")
                            if agent_status.status.value == "idle":
                                logger.info(f"{agent_name} 已完成任务")
                                break
                        else:
                            logger.warning(f"无法获取 {agent_name} 状态")
                    
                    agent_end = time.time()
                    agent_time = agent_end - agent_start
                    logger.info(f"⏱️ {agent_name} 测试完成 - 耗时: {agent_time:.2f}秒")
                    
                    if wait_time >= max_wait_time:
                        logger.warning(f"⚠️ {agent_name} 等待超时")
                        results[agent_name] = {"success": False, "time": agent_time, "timeout": True}
                    else:
                        logger.info(f"✅ {agent_name} 任务完成")
                        results[agent_name] = {"success": True, "time": agent_time, "timeout": False}
            
            task_end = time.time()
            logger.info(f"⏱️ 结束: 测试所有智能体 - 耗时: {task_end - task_start:.2f}秒")
            
            # 分析结果
            success_count = sum(1 for r in results.values() if r["success"])
            timeout_count = sum(1 for r in results.values() if r["timeout"])
            total_count = len(results)
            
            logger.info(f"📊 测试结果: {success_count}/{total_count} 成功, {timeout_count} 超时")
            
            for agent_name, result in results.items():
                status = "✅" if result["success"] else "❌"
                timeout_info = " (超时)" if result["timeout"] else ""
                logger.info(f"   {status} {agent_name}: {result['time']:.2f}秒{timeout_info}")
            
            success = success_count > 0  # 至少有一个智能体成功
                
        except Exception as e:
            task_end = time.time()
            logger.info(f"⏱️ 结束: 测试所有智能体 - 耗时: {task_end - task_start:.2f}秒")
            logger.error(f"❌ 测试过程中出错: {e}")
            traceback.print_exc()
            success = False
        
        # 步骤5: 停止系统
        logger.info("⏱️ 开始: 停止系统")
        stop_start = time.time()
        await system.stop()
        stop_end = time.time()
        logger.info(f"⏱️ 结束: 停止系统 - 耗时: {stop_end - stop_start:.2f}秒")
        
        # 计算总时间
        total_time = time.time() - start_time
        
        # 打印详细的时间分析
        logger.info("📊 详细时间分析:")
        logger.info("=" * 60)
        logger.info(f"   系统创建: {system_end - system_start:.2f}秒")
        logger.info(f"   获取所有智能体: {agents_end - agents_start:.2f}秒")
        logger.info(f"   准备任务数据: {data_end - data_start:.2f}秒")
        logger.info(f"   测试所有智能体: {task_end - task_start:.2f}秒")
        logger.info(f"   停止系统: {stop_end - stop_start:.2f}秒")
        logger.info("=" * 60)
        logger.info(f"   总计: {total_time:.2f}秒")
        
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
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 详细调试过程中出错: {e}")
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    try:
        success = await debug_planner_detailed()
        
        if success:
            logger.info("✅ planner_agent 详细调试完成")
        else:
            logger.error("❌ planner_agent 详细调试失败")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())