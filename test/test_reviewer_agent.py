#!/usr/bin/env python3
"""
Reviewer Agent 测试脚本
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
        logging.FileHandler('test_reviewer_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def test_reviewer_agent_glm_false():
    """测试 Reviewer Agent 在 GLM_AVAILABLE=False 时的情况"""
    logger.info("="*60)
    logger.info("🧪 测试 Reviewer Agent - GLM_AVAILABLE=False")
    logger.info("="*60)
    
    try:
        # 模拟 GLM_AVAILABLE=False 的情况
        import unified_service
        
        # 临时设置 GLM_AVAILABLE 为 False
        original_glm_available = getattr(unified_service, 'GLM_AVAILABLE', False)
        unified_service.GLM_AVAILABLE = False
        
        logger.info("🔧 设置 GLM_AVAILABLE=False")
        
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
            }
        }
        
        # 创建测试请求
        from unified_service import TaskRequest
        request = TaskRequest(
            task_id=f"test_reviewer_glm_false_{int(asyncio.get_event_loop().time())}",
            workflow_id="test_reviewer_glm_false",
            stage_name="review",
            topic=test_topic,
            description=f"测试Reviewer Agent在GLM_AVAILABLE=False模式下的表现",
            test_mode=True,
            previous_results=test_previous_results
        )
        
        logger.info(f"📋 执行 Reviewer Agent 任务")
        logger.info(f"主题: {test_topic}")
        
        # 执行任务
        start_time = asyncio.get_event_loop().time()
        result = await unified_service.execute_reviewer_task(request)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
        
        # 分析结果
        logger.info("📊 结果分析:")
        logger.info(f"  质量评分: {result.get('quality_score', 'N/A')}")
        logger.info(f"  一致性评分: {result.get('consistency_score', 'N/A')}")
        logger.info(f"  反馈数量: {len(result.get('feedback', []))}")
        logger.info(f"  建议数量: {len(result.get('recommendations', []))}")
        logger.info(f"  合规检查: {result.get('compliance_check', {})}")
        logger.info(f"  测试模式: {result.get('test_mode', 'N/A')}")
        logger.info(f"  Mock延迟: {result.get('mock_delay_applied', 'N/A')}")
        
        # 检查是否使用了mock数据
        if result.get('mock_delay_applied', 0) > 0:
            logger.info("✅ 确认使用了mock数据")
        else:
            logger.warning("⚠️ 可能没有使用mock数据")
        
        # 保存结果
        output_file = "test_reviewer_glm_false_output.json"
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 结果已保存到: {output_file}")
        
        # 恢复原始设置
        unified_service.GLM_AVAILABLE = original_glm_available
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"📋 错误详情: {traceback.format_exc()}")
        return False

async def test_reviewer_agent_glm_true():
    """测试 Reviewer Agent 在 GLM_AVAILABLE=True 时的情况"""
    logger.info("="*60)
    logger.info("🧪 测试 Reviewer Agent - GLM_AVAILABLE=True")
    logger.info("="*60)
    
    try:
        # 模拟 GLM_AVAILABLE=True 的情况
        import unified_service
        
        # 临时设置 GLM_AVAILABLE 为 True
        original_glm_available = getattr(unified_service, 'GLM_AVAILABLE', False)
        unified_service.GLM_AVAILABLE = True
        
        logger.info("🔧 设置 GLM_AVAILABLE=True")
        
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
            }
        }
        
        # 创建测试请求
        from unified_service import TaskRequest
        request = TaskRequest(
            task_id=f"test_reviewer_glm_true_{int(asyncio.get_event_loop().time())}",
            workflow_id="test_reviewer_glm_true",
            stage_name="review",
            topic=test_topic,
            description=f"测试Reviewer Agent在GLM_AVAILABLE=True模式下的表现",
            test_mode=False,  # 真实模式
            previous_results=test_previous_results
        )
        
        logger.info(f"📋 执行 Reviewer Agent 任务")
        logger.info(f"主题: {test_topic}")
        
        # 执行任务
        start_time = asyncio.get_event_loop().time()
        result = await unified_service.execute_reviewer_task(request)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
        
        # 分析结果
        logger.info("📊 结果分析:")
        logger.info(f"  质量评分: {result.get('quality_score', 'N/A')}")
        logger.info(f"  一致性评分: {result.get('consistency_score', 'N/A')}")
        logger.info(f"  反馈数量: {len(result.get('feedback', []))}")
        logger.info(f"  建议数量: {len(result.get('recommendations', []))}")
        logger.info(f"  合规检查: {result.get('compliance_check', {})}")
        logger.info(f"  测试模式: {result.get('test_mode', 'N/A')}")
        logger.info(f"  Mock延迟: {result.get('mock_delay_applied', 'N/A')}")
        
        # 检查是否调用了GLM API
        if result.get('mock_delay_applied', 0) == 0:
            logger.info("✅ 确认调用了GLM API")
        else:
            logger.warning("⚠️ 可能回退到了mock数据")
        
        # 保存结果
        output_file = "test_reviewer_glm_true_output.json"
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 结果已保存到: {output_file}")
        
        # 恢复原始设置
        unified_service.GLM_AVAILABLE = original_glm_available
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        logger.error(f"📋 错误详情: {traceback.format_exc()}")
        return False

async def main():
    """主函数"""
    logger.info("🎯 开始 Reviewer Agent 测试")
    
    # 测试 GLM_AVAILABLE=False
    success_false = await test_reviewer_agent_glm_false()
    
    # 测试 GLM_AVAILABLE=True
    success_true = await test_reviewer_agent_glm_true()
    
    # 总结
    logger.info("\n" + "="*60)
    logger.info("测试总结")
    logger.info("="*60)
    
    if success_false and success_true:
        logger.info("🎉 所有测试通过！")
        logger.info("✅ GLM_AVAILABLE=False 测试: 通过")
        logger.info("✅ GLM_AVAILABLE=True 测试: 通过")
        logger.info("💡 建议: Reviewer Agent 工作正常")
    else:
        logger.info("❌ 部分测试失败")
        logger.info(f"❌ GLM_AVAILABLE=False 测试: {'通过' if success_false else '失败'}")
        logger.info(f"❌ GLM_AVAILABLE=True 测试: {'通过' if success_true else '失败'}")
        logger.info("💡 建议: 检查 Reviewer Agent 配置和代码")

if __name__ == "__main__":
    asyncio.run(main())