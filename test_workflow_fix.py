#!/usr/bin/env python3
"""
Test Workflow Fix
测试修复后的工作流程
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

async def test_workflow_execution():
    """测试工作流程执行"""
    try:
        logger.info("🚀 开始测试修复后的工作流程")
        
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
        logger.info(f"📝 主题描述: {description[:100]}...")
        
        # 启动工作流
        logger.info("🔄 启动专利撰写工作流...")
        start_result = await system.execute_workflow(topic, description)
        
        if not start_result["success"]:
            logger.error(f"❌ 工作流启动失败: {start_result.get('error')}")
            return False
            
        workflow_id = start_result["workflow_id"]
        logger.info(f"✅ 工作流启动成功: {workflow_id}")
        
        # 监控工作流执行
        logger.info("👀 开始监控工作流执行...")
        
        while True:
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
                
                logger.info(f"📊 工作流状态: {overall_status}, 当前阶段: {current_stage} ({current_stage_name})")
                
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
            
            # 检查是否所有阶段都执行了
            expected_stages = [
                "Planning & Strategy",
                "Prior Art Search", 
                "Innovation Discussion",
                "Patent Drafting",
                "Quality Review",
                "Final Rewrite"
            ]
            
            completed_stages = []
            for stage_name in expected_stages:
                if any(stage_name in key for key in stages_results.keys()):
                    completed_stages.append(stage_name)
            
            logger.info(f"✅ 完成的阶段: {len(completed_stages)}/{len(expected_stages)}")
            for stage in completed_stages:
                logger.info(f"  ✅ {stage}")
            
            missing_stages = [stage for stage in expected_stages if stage not in completed_stages]
            if missing_stages:
                logger.warning(f"⚠️ 缺失的阶段: {missing_stages}")
            else:
                logger.info("🎉 所有阶段都成功执行！")
                
        else:
            logger.error(f"❌ 获取工作流结果失败: {final_result.get('error')}")
            
        # 停止系统
        await system.stop()
        logger.info("🛑 专利代理系统已停止")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试工作流程执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_status():
    """测试智能体状态"""
    try:
        logger.info("🤖 测试智能体状态...")
        
        system = PatentAgentSystem()
        await system.start()
        
        # 获取所有智能体状态
        agents_status = await system.get_agents_status()
        
        logger.info("📊 智能体状态:")
        for agent_name, agent_info in agents_status.items():
            status = agent_info.get("status", "unknown")
            capabilities = agent_info.get("capabilities", [])
            
            status_icon = "✅" if status == "idle" else "🔄" if status == "working" else "❌"
            logger.info(f"  {status_icon} {agent_name}: {status}")
            logger.info(f"    能力: {capabilities}")
        
        await system.stop()
        
    except Exception as e:
        logger.error(f"❌ 测试智能体状态失败: {e}")

async def main():
    """主函数"""
    try:
        logger.info("🧪 开始工作流程修复测试")
        
        # 测试智能体状态
        await test_agent_status()
        
        # 测试工作流程执行
        success = await test_workflow_execution()
        
        if success:
            logger.info("🎉 工作流程修复测试完成！")
        else:
            logger.error("❌ 工作流程修复测试失败！")
            
    except Exception as e:
        logger.error(f"❌ 主测试程序失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())