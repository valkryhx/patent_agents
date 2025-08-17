#!/usr/bin/env python3
"""
通过消息总线正确测试planner_agent
"""

import asyncio
import sys
import os
import logging
import time
import uuid

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.message_bus import Message, MessageType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_planner_correct():
    """通过消息总线正确测试planner_agent"""
    try:
        logger.info("🚀 开始通过消息总线测试planner_agent")
        
        # 记录开始时间
        start_time = time.time()
        
        # 步骤1: 创建系统
        logger.info("⏱️ 开始: 创建系统")
        system_start = time.time()
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        system_end = time.time()
        logger.info(f"⏱️ 结束: 创建系统 - 耗时: {system_end - system_start:.2f}秒")
        
        # 步骤2: 获取消息总线
        logger.info("⏱️ 开始: 获取消息总线")
        broker_start = time.time()
        broker = system.message_bus_config.broker
        broker_end = time.time()
        logger.info(f"⏱️ 结束: 获取消息总线 - 耗时: {broker_end - broker_start:.2f}秒")
        
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
        
        # 步骤4: 通过消息总线发送任务
        logger.info("⏱️ 开始: 通过消息总线发送任务")
        send_start = time.time()
        
        # 创建任务消息
        task_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.COORDINATION,
            sender="test_script",
            recipient="planner_agent",
            content={
                "task": task_data,
                "task_id": str(uuid.uuid4())
            },
            timestamp=time.time(),
            priority=5
        )
        
        # 发送消息
        await broker.send_message(task_message)
        send_end = time.time()
        logger.info(f"⏱️ 结束: 通过消息总线发送任务 - 耗时: {send_end - send_start:.2f}秒")
        
        # 步骤5: 等待任务完成
        logger.info("⏱️ 开始: 等待任务完成")
        wait_start = time.time()
        
        # 等待最多5分钟
        max_wait_time = 300  # 5分钟
        wait_time = 0
        check_interval = 5  # 每5秒检查一次
        
        while wait_time < max_wait_time:
            await asyncio.sleep(check_interval)
            wait_time += check_interval
            
            # 检查planner_agent的状态
            planner_status = await broker.get_agent_status("planner_agent")
            if planner_status:
                logger.info(f"planner_agent状态: {planner_status.status.value}")
                if planner_status.status.value == "idle":
                    logger.info("planner_agent已完成任务")
                    break
            else:
                logger.warning("无法获取planner_agent状态")
        
        wait_end = time.time()
        logger.info(f"⏱️ 结束: 等待任务完成 - 耗时: {wait_end - wait_start:.2f}秒")
        
        # 步骤6: 停止系统
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
        logger.info(f"   获取消息总线: {broker_end - broker_start:.2f}秒")
        logger.info(f"   准备任务数据: {data_end - data_start:.2f}秒")
        logger.info(f"   通过消息总线发送任务: {send_end - send_start:.2f}秒")
        logger.info(f"   等待任务完成: {wait_end - wait_start:.2f}秒")
        logger.info(f"   停止系统: {stop_end - stop_start:.2f}秒")
        logger.info("=" * 60)
        logger.info(f"   总计: {total_time:.2f}秒")
        
        if wait_time >= max_wait_time:
            logger.warning("⚠️ 等待超时，planner_agent可能没有正确完成任务")
            return False
        else:
            logger.info("✅ planner_agent任务完成")
            return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    try:
        success = await test_planner_correct()
        
        if success:
            logger.info("✅ planner_agent消息总线测试完成")
        else:
            logger.error("❌ planner_agent消息总线测试失败")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())