#!/usr/bin/env python3
"""
综合测试脚本 - 测试所有智能体的 GLM 调用情况
分别测试 GLM_AVAILABLE 为 false 和 true 的情况
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_all_agents_glm.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_agent_glm_mode(agent_name: str, execute_func, glm_available: bool, test_mode: bool = True):
    """测试单个智能体在指定GLM模式下的表现"""
    logger.info("="*60)
    logger.info(f"🧪 测试 {agent_name} - GLM_AVAILABLE={glm_available}")
    logger.info("="*60)
    
    try:
        # 模拟 GLM_AVAILABLE 的情况
        import unified_service
        
        # 临时设置 GLM_AVAILABLE
        original_glm_available = getattr(unified_service, 'GLM_AVAILABLE', False)
        unified_service.GLM_AVAILABLE = glm_available
        
        logger.info(f"🔧 设置 GLM_AVAILABLE={glm_available}")
        
        # 准备测试数据
        test_topic = "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
        test_previous_results = {
            "planning": {
                "result": {
                    "strategy": {
                        "key_innovation_areas": ["语义理解", "参数推断", "分层调用", "重试优化"],
                        "novelty_score": 8.5
                    }
                }
            },
            "search": {
                "result": {
                    "search_results": {
                        "results": [
                            "现有技术：传统参数推断方法",
                            "相关专利：智能参数优化系统",
                            "技术趋势：语义理解在参数推断中的应用"
                        ]
                    }
                }
            },
            "discussion": {
                "result": {
                    "innovations": ["增强的语义理解架构", "改进的参数推断优化"],
                    "technical_insights": ["新颖的参数推断方法", "独特的系统集成方法"],
                    "recommendations": ["专注于语义理解作为关键差异化因素"]
                }
            },
            "drafting": {
                "result": {
                    "title": f"专利申请书: {test_topic}",
                    "abstract": "一种智能化的函数参数推断系统",
                    "claims": ["权利要求1", "权利要求2"],
                    "detailed_description": "详细的技术描述内容"
                }
            },
            "review": {
                "result": {
                    "quality_score": 8.5,
                    "consistency_score": 9.0,
                    "feedback": ["技术描述清晰", "权利要求结构良好"],
                    "recommendations": ["可以添加更多技术示例", "建议优化摘要描述"]
                }
            }
        }
        
        # 创建测试请求
        from unified_service import TaskRequest
        request = TaskRequest(
            task_id=f"test_{agent_name.lower().replace(' ', '_')}_glm_{glm_available}_{int(asyncio.get_event_loop().time())}",
            workflow_id=f"test_{agent_name.lower().replace(' ', '_')}_glm_{glm_available}",
            stage_name=agent_name.lower().replace(' agent', ''),
            topic=test_topic,
            description=f"测试{agent_name}在GLM_AVAILABLE={glm_available}模式下的表现",
            test_mode=test_mode,
            previous_results=test_previous_results
        )
        
        logger.info(f"📋 执行 {agent_name} 任务")
        logger.info(f"主题: {test_topic}")
        
        # 执行任务
        start_time = asyncio.get_event_loop().time()
        result = await execute_func(request)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
        
        # 分析结果
        logger.info("📊 结果分析:")
        
        # 根据智能体类型分析不同的结果字段
        if agent_name == "Discussion Agent":
            logger.info(f"  创新点数量: {len(result.get('innovations', []))}")
            logger.info(f"  技术洞察数量: {len(result.get('technical_insights', []))}")
            logger.info(f"  建议数量: {len(result.get('recommendations', []))}")
            logger.info(f"  新颖性评分: {result.get('novelty_score', 'N/A')}")
        elif agent_name == "Reviewer Agent":
            logger.info(f"  质量评分: {result.get('quality_score', 'N/A')}")
            logger.info(f"  一致性评分: {result.get('consistency_score', 'N/A')}")
            logger.info(f"  反馈数量: {len(result.get('feedback', []))}")
            logger.info(f"  建议数量: {len(result.get('recommendations', []))}")
        elif agent_name == "Rewriter Agent":
            logger.info(f"  标题: {result.get('title', 'N/A')}")
            logger.info(f"  摘要长度: {len(result.get('abstract', ''))} 字符")
            logger.info(f"  权利要求数量: {len(result.get('claims', []))}")
            logger.info(f"  改进点数量: {len(result.get('improvements', []))}")
        
        logger.info(f"  测试模式: {result.get('test_mode', 'N/A')}")
        logger.info(f"  Mock延迟: {result.get('mock_delay_applied', 'N/A')}")
        
        # 检查是否使用了正确的模式
        if glm_available:
            if result.get('mock_delay_applied', 0) == 0:
                logger.info("✅ 确认调用了GLM API")
            else:
                logger.warning("⚠️ 可能回退到了mock数据")
        else:
            if result.get('mock_delay_applied', 0) > 0:
                logger.info("✅ 确认使用了mock数据")
            else:
                logger.warning("⚠️ 可能没有使用mock数据")
        
        # 保存结果
        output_file = f"test_{agent_name.lower().replace(' ', '_')}_glm_{glm_available}_output.json"
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 结果已保存到: {output_file}")
        
        # 恢复原始设置
        unified_service.GLM_AVAILABLE = original_glm_available
        
        return True, result
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"📋 错误详情: {traceback.format_exc()}")
        return False, None

async def test_all_agents():
    """测试所有智能体"""
    logger.info("🎯 开始所有智能体测试")
    
    # 导入智能体函数
    import unified_service
    
    # 定义智能体配置
    agents = [
        {
            "name": "Discussion Agent",
            "func": unified_service.execute_discussion_task,
            "description": "创新讨论分析"
        },
        {
            "name": "Reviewer Agent", 
            "func": unified_service.execute_reviewer_task,
            "description": "专利质量审查"
        },
        {
            "name": "Rewriter Agent",
            "func": unified_service.execute_rewriter_task,
            "description": "专利内容重写"
        }
    ]
    
    # 测试结果存储
    test_results = {}
    
    # 测试每个智能体在两种GLM模式下的表现
    for agent in agents:
        agent_name = agent["name"]
        execute_func = agent["func"]
        
        logger.info(f"\n🔍 开始测试 {agent_name} ({agent['description']})")
        
        # 测试 GLM_AVAILABLE=False
        success_false, result_false = await test_agent_glm_mode(
            agent_name, execute_func, glm_available=False, test_mode=True
        )
        
        # 测试 GLM_AVAILABLE=True
        success_true, result_true = await test_agent_glm_mode(
            agent_name, execute_func, glm_available=True, test_mode=False
        )
        
        test_results[agent_name] = {
            "glm_false": {"success": success_false, "result": result_false},
            "glm_true": {"success": success_true, "result": result_true}
        }
    
    return test_results

async def generate_test_report(test_results: Dict[str, Any]):
    """生成测试报告"""
    logger.info("\n" + "="*80)
    logger.info("📋 综合测试报告")
    logger.info("="*80)
    
    total_agents = len(test_results)
    total_tests = total_agents * 2  # 每个智能体2个测试
    passed_tests = 0
    
    for agent_name, results in test_results.items():
        logger.info(f"\n🤖 {agent_name}:")
        
        glm_false_success = results["glm_false"]["success"]
        glm_true_success = results["glm_true"]["success"]
        
        if glm_false_success:
            passed_tests += 1
            logger.info("  ✅ GLM_AVAILABLE=False 测试: 通过")
        else:
            logger.info("  ❌ GLM_AVAILABLE=False 测试: 失败")
            
        if glm_true_success:
            passed_tests += 1
            logger.info("  ✅ GLM_AVAILABLE=True 测试: 通过")
        else:
            logger.info("  ❌ GLM_AVAILABLE=True 测试: 失败")
    
    logger.info(f"\n📊 总体统计:")
    logger.info(f"  智能体数量: {total_agents}")
    logger.info(f"  总测试数: {total_tests}")
    logger.info(f"  通过测试: {passed_tests}")
    logger.info(f"  失败测试: {total_tests - passed_tests}")
    logger.info(f"  通过率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 所有测试通过！所有智能体工作正常")
    else:
        logger.info(f"\n⚠️ 有 {total_tests - passed_tests} 个测试失败，需要进一步检查")
    
    # 保存详细报告
    report_file = "test_all_agents_glm_report.json"
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total_agents": total_agents,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "pass_rate": passed_tests/total_tests*100
            },
            "detailed_results": test_results
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 详细报告已保存到: {report_file}")

async def main():
    """主函数"""
    logger.info("🚀 开始综合智能体测试")
    
    # 执行所有测试
    test_results = await test_all_agents()
    
    # 生成测试报告
    await generate_test_report(test_results)

if __name__ == "__main__":
    asyncio.run(main())