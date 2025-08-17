#!/usr/bin/env python3
"""
测试修改后的工作流程，确保所有6个智能体都能依次执行
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
        logger.info("🚀 开始测试修改后的工作流程执行")
        
        # 创建系统
        system = PatentAgentSystem(test_mode=False)
        await system.start()
        logger.info("✅ 系统启动成功")
        
        # 测试数据
        task_data = {
            "type": "start_patent_workflow",
            "topic": "基于智能分层推理的多参数工具自适应调用系统",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        }
        
        # 获取coordinator智能体
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
        
        # 执行工作流
        start_time = time.time()
        logger.info("🔧 开始执行专利撰写工作流...")
        
        try:
            result: TaskResult = await coordinator.execute_task(task_data)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(f"⏱️ 工作流启动时间: {execution_time:.2f}秒")
            
            if result.success:
                logger.info("✅ 工作流启动成功")
                workflow_id = result.data.get('workflow_id', 'N/A')
                logger.info(f"   工作流ID: {workflow_id}")
                
                # 监控工作流执行
                logger.info("⏳ 开始监控工作流执行...")
                await monitor_workflow_progress(coordinator, workflow_id, max_wait_time=600)  # 10分钟超时
                
                success = True
            else:
                logger.error(f"❌ 工作流启动失败: {result.error_message}")
                success = False
                
        except Exception as e:
            logger.error(f"❌ 工作流执行出错: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        # 停止系统
        await system.stop()
        logger.info("✅ 系统已停止")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def monitor_workflow_progress(coordinator, workflow_id: str, max_wait_time: int = 600):
    """监控工作流进度"""
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait_time:
        try:
            # 检查工作流状态
            workflow = coordinator.active_workflows.get(workflow_id)
            if not workflow:
                logger.warning("⚠️ 工作流未找到，可能已完成")
                break
                
            current_status = workflow.overall_status
            current_stage = workflow.current_stage
            
            # 如果状态发生变化，记录日志
            if current_status != last_status:
                logger.info(f"📊 工作流状态变化: {last_status} -> {current_status}")
                last_status = current_status
            
            # 检查每个阶段的执行情况
            stage_statuses = []
            for i, stage in enumerate(workflow.stages):
                stage_statuses.append(f"{i}:{stage.stage_name}({stage.status})")
            
            logger.info(f"📍 当前阶段: {current_stage}, 阶段状态: {' | '.join(stage_statuses)}")
            
            # 检查迭代状态
            if hasattr(workflow, 'results') and workflow.results:
                iteration = workflow.results.get('iteration', {})
                if iteration:
                    review_count = iteration.get('review_count', 0)
                    rewrite_count = iteration.get('rewrite_count', 0)
                    logger.info(f"🔄 迭代状态: 审核{review_count}次, 重写{rewrite_count}次")
            
            # 检查是否完成
            if current_status == "completed":
                logger.info("✅ 工作流已完成")
                break
            elif current_status == "failed":
                logger.error("❌ 工作流失败")
                break
            elif current_status == "error":
                logger.error("❌ 工作流出错")
                break
            
            # 检查生成的文件
            import glob
            patent_files = glob.glob("output/progress/*/")
            if patent_files:
                total_size = 0
                file_count = 0
                for dir_path in patent_files:
                    files = os.listdir(dir_path)
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(dir_path, file)
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            file_count += 1
                
                logger.info(f"📄 已生成文件: {file_count}个, 总大小: {total_size}字节")
            
            # 等待一段时间再检查
            await asyncio.sleep(30)  # 每30秒检查一次
            
        except Exception as e:
            logger.error(f"❌ 监控过程中出错: {e}")
            await asyncio.sleep(10)
    
    # 最终检查
    logger.info("🔍 最终检查工作流状态...")
    workflow = coordinator.active_workflows.get(workflow_id)
    if workflow:
        logger.info(f"📊 最终状态: {workflow.overall_status}")
        logger.info(f"📍 最终阶段: {workflow.current_stage}")
        
        # 检查每个阶段的最终状态
        for i, stage in enumerate(workflow.stages):
            logger.info(f"   阶段{i}: {stage.stage_name} - {stage.status}")
            if stage.error:
                logger.error(f"   错误: {stage.error}")
        
        # 检查迭代状态
        if hasattr(workflow, 'results') and workflow.results:
            iteration = workflow.results.get('iteration', {})
            if iteration:
                review_count = iteration.get('review_count', 0)
                rewrite_count = iteration.get('rewrite_count', 0)
                logger.info(f"🔄 最终迭代状态: 审核{review_count}次, 重写{rewrite_count}次")
    
    # 检查生成的文件
    import glob
    patent_files = glob.glob("output/progress/*/")
    if patent_files:
        logger.info(f"📄 最终文件统计:")
        for dir_path in patent_files:
            files = os.listdir(dir_path)
            logger.info(f"   目录 {dir_path}: {len(files)}个文件")
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(dir_path, file)
                    file_size = os.path.getsize(file_path)
                    logger.info(f"     {file}: {file_size}字节")

async def main():
    """主函数"""
    try:
        logger.info("🔍 开始测试修改后的工作流程")
        
        success = await test_workflow_execution()
        
        if success:
            logger.info("✅ 工作流程执行测试成功")
        else:
            logger.error("❌ 工作流程执行测试失败")
        
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())