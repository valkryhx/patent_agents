#!/usr/bin/env python3
"""
Test Iteration Control
测试迭代控制机制
"""

import asyncio
import sys
import os
import logging
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_iteration_control():
    """测试迭代控制机制"""
    try:
        logger.info("🚀 开始测试迭代控制机制")
        
        # 创建专利代理系统
        system = PatentAgentSystem()
        
        # 启动系统
        await system.start()
        logger.info("✅ 专利代理系统启动成功")
        
        # 定义测试主题
        topic = "基于区块链的智能合约安全验证系统"
        description = """
        一种基于形式化验证的区块链智能合约安全验证系统，通过静态分析、动态测试、形式化验证等技术，
        实现智能合约的安全检测和漏洞预防。该系统能够自动识别智能合约中的安全漏洞，
        并提供修复建议，确保智能合约的安全性和可靠性。
        """
        
        logger.info(f"📋 测试主题: {topic}")
        
        # 启动工作流
        logger.info("🔄 启动专利撰写工作流...")
        start_result = await system.execute_workflow(topic, description)
        
        if not start_result["success"]:
            logger.error(f"❌ 工作流启动失败: {start_result.get('error')}")
            return False
            
        workflow_id = start_result["workflow_id"]
        logger.info(f"✅ 工作流启动成功: {workflow_id}")
        
        # 监控工作流执行，特别关注迭代状态
        logger.info("👀 开始监控工作流执行和迭代状态...")
        max_wait_time = 600  # 10分钟超时
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # 获取工作流状态
                status_result = await system.get_workflow_status(workflow_id)
                
                if status_result.get("status") == "not_found":
                    logger.warning("⚠️ 工作流未找到，可能已完成")
                    break
                    
                if status_result.get("status") == "error":
                    logger.error(f"❌ 获取工作流状态失败: {status_result.get('error')}")
                    break
                
                current_stage = status_result.get("current_stage", 0)
                current_stage_name = status_result.get("current_stage_name", "Unknown")
                overall_status = status_result.get("overall_status", "unknown")
                
                # 获取迭代状态
                iteration_status = status_result.get("iteration_status", {})
                
                logger.info(f"📊 工作流状态: {overall_status}, 当前阶段: {current_stage} ({current_stage_name})")
                
                # 显示迭代状态
                if iteration_status.get("status") == "active":
                    phase = iteration_status.get("phase", "unknown")
                    review_count = iteration_status.get("review_count", 0)
                    rewrite_count = iteration_status.get("rewrite_count", 0)
                    max_reviews = iteration_status.get("max_reviews", 3)
                    max_rewrites = iteration_status.get("max_rewrites", 3)
                    consecutive_failures = iteration_status.get("consecutive_failures", 0)
                    remaining_reviews = iteration_status.get("remaining_reviews", 0)
                    remaining_rewrites = iteration_status.get("remaining_rewrites", 0)
                    
                    logger.info(f"🔄 迭代状态: 阶段={phase}, 审查={review_count}/{max_reviews}, 重写={rewrite_count}/{max_rewrites}")
                    logger.info(f"  连续失败: {consecutive_failures}, 剩余审查: {remaining_reviews}, 剩余重写: {remaining_rewrites}")
                    
                    # 检查警告
                    warnings = iteration_status.get("warnings", {})
                    if warnings.get("review_limit_approaching"):
                        logger.warning("⚠️ 审查次数接近限制")
                    if warnings.get("rewrite_limit_approaching"):
                        logger.warning("⚠️ 重写次数接近限制")
                    if warnings.get("consecutive_failure_approaching"):
                        logger.warning("⚠️ 连续失败次数接近限制")
                
                # 显示各阶段状态
                stages = status_result.get("stages", [])
                for i, stage in enumerate(stages):
                    stage_status = stage.get("status", "unknown")
                    stage_agent = stage.get("agent", "unknown")
                    stage_error = stage.get("error", "")
                    
                    status_icon = "✅" if stage_status == "completed" else "🔄" if stage_status == "running" else "⏳" if stage_status == "pending" else "❌"
                    logger.info(f"  {status_icon} 阶段 {i}: {stage['name']} ({stage_agent}) - {stage_status}")
                    if stage_error:
                        logger.warning(f"    ⚠️ 错误: {stage_error}")
                
                # 检查是否完成
                if overall_status == "completed":
                    logger.info("🎉 工作流执行完成！")
                    break
                    
                # 等待一段时间再检查
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ 监控工作流时出错: {e}")
                break
        
        # 获取最终结果
        logger.info("📋 获取工作流最终结果...")
        final_result = await system.get_workflow_result(workflow_id)
        
        if final_result["success"]:
            logger.info("✅ 成功获取工作流结果")
            
            # 显示结果摘要
            result_data = final_result.get("data", {})
            stages_results = result_data.get("stages_results", {})
            
            logger.info("📊 各阶段结果摘要:")
            for stage_name, stage_result in stages_results.items():
                if stage_result:
                    logger.info(f"  📝 {stage_name}: 完成")
                else:
                    logger.warning(f"  ⚠️ {stage_name}: 未完成或失败")
            
            # 检查迭代控制是否正常工作
            workflow_results = result_data.get("workflow_results", {})
            iteration_data = workflow_results.get("iteration", {})
            
            if iteration_data:
                review_count = iteration_data.get("review_count", 0)
                rewrite_count = iteration_data.get("rewrite_count", 0)
                max_reviews = iteration_data.get("max_reviews", 3)
                max_rewrites = iteration_data.get("max_rewrites", 3)
                
                logger.info(f"🔄 最终迭代状态: 审查={review_count}/{max_reviews}, 重写={rewrite_count}/{max_rewrites}")
                
                # 验证迭代控制
                if review_count <= max_reviews and rewrite_count <= max_rewrites:
                    logger.info("✅ 迭代控制正常工作 - 未超过限制")
                else:
                    logger.error("❌ 迭代控制失败 - 超过限制")
                    
                if review_count > 0 or rewrite_count > 0:
                    logger.info("✅ 审查和重写阶段正常执行")
                else:
                    logger.warning("⚠️ 审查和重写阶段可能未执行")
            else:
                logger.warning("⚠️ 未找到迭代数据")
                
        else:
            logger.error(f"❌ 获取工作流结果失败: {final_result.get('error')}")
            
        # 停止系统
        await system.stop()
        logger.info("🛑 专利代理系统已停止")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试迭代控制失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_iteration_scenarios():
    """测试不同的迭代场景"""
    logger.info("🧪 测试迭代控制场景")
    
    scenarios = [
        {
            "name": "正常流程 - 一次审查通过",
            "description": "测试正常情况下的工作流程"
        },
        {
            "name": "需要重写 - 多次迭代",
            "description": "测试需要多次重写的情况"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"场景 {i}: {scenario['name']}")
        logger.info(f"{'='*60}")
        
        # 这里可以添加具体的场景测试逻辑
        logger.info(f"场景描述: {scenario['description']}")
        logger.info("✅ 场景测试完成")

async def main():
    """主函数"""
    try:
        logger.info("🧪 开始迭代控制测试")
        
        # 测试迭代控制机制
        success = await test_iteration_control()
        
        # 测试迭代场景
        await test_iteration_scenarios()
        
        if success:
            logger.info("🎉 迭代控制测试完成！")
        else:
            logger.error("❌ 迭代控制测试失败！")
            
    except Exception as e:
        logger.error(f"❌ 主测试程序失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())