#!/usr/bin/env python3
"""
详细分析planner_agent的执行时间
"""

import asyncio
import sys
import os
import logging
import time
import traceback

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.agents.base_agent import TaskResult

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimingTracker:
    """时间追踪器"""
    
    def __init__(self):
        self.timings = {}
        self.start_time = None
        
    def start(self, step_name: str):
        """开始计时"""
        if step_name not in self.timings:
            self.timings[step_name] = {"start": time.time(), "end": None, "duration": None}
        else:
            self.timings[step_name]["start"] = time.time()
        logger.info(f"⏱️ 开始: {step_name}")
        
    def end(self, step_name: str):
        """结束计时"""
        if step_name in self.timings:
            self.timings[step_name]["end"] = time.time()
            self.timings[step_name]["duration"] = self.timings[step_name]["end"] - self.timings[step_name]["start"]
            logger.info(f"⏱️ 结束: {step_name} - 耗时: {self.timings[step_name]['duration']:.2f}秒")
        
    def print_summary(self):
        """打印时间总结"""
        logger.info("📊 时间分析总结:")
        logger.info("=" * 60)
        total_time = 0
        for step_name, timing in self.timings.items():
            if timing["duration"] is not None:
                logger.info(f"   {step_name}: {timing['duration']:.2f}秒")
                total_time += timing["duration"]
        logger.info("=" * 60)
        logger.info(f"   总计: {total_time:.2f}秒")
        logger.info(f"   未追踪时间: {time.time() - self.start_time - total_time:.2f}秒")

async def debug_planner_timing():
    """详细分析planner_agent的执行时间"""
    tracker = TimingTracker()
    tracker.start_time = time.time()
    
    try:
        logger.info("🚀 开始详细分析planner_agent执行时间")
        
        # 步骤1: 创建系统
        tracker.start("系统创建")
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        tracker.end("系统创建")
        
        # 步骤2: 获取planner智能体
        tracker.start("获取planner智能体")
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
        tracker.end("获取planner智能体")
        
        # 步骤3: 准备任务数据
        tracker.start("准备任务数据")
        task_data = {
            "type": "patent_planning",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        }
        tracker.end("准备任务数据")
        
        # 步骤4: 执行任务
        tracker.start("执行planner任务")
        logger.info("🔧 开始执行planner任务...")
        
        try:
            result: TaskResult = await planner.execute_task(task_data)
            tracker.end("执行planner任务")
            
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
                
                success = True
            else:
                logger.error(f"❌ planner_agent 任务失败: {result.error_message}")
                success = False
                
        except Exception as e:
            tracker.end("执行planner任务")
            logger.error(f"❌ planner_agent 任务执行出错: {e}")
            traceback.print_exc()
            success = False
        
        # 步骤5: 停止系统
        tracker.start("停止系统")
        await system.stop()
        tracker.end("停止系统")
        
        # 打印时间总结
        tracker.print_summary()
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 详细分析过程中出错: {e}")
        traceback.print_exc()
        tracker.print_summary()
        return False

async def main():
    """主函数"""
    try:
        success = await debug_planner_timing()
        
        if success:
            logger.info("✅ planner_agent 详细分析完成")
        else:
            logger.error("❌ planner_agent 详细分析失败")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())