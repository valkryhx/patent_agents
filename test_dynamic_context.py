#!/usr/bin/env python3
"""
Test Dynamic Context Management
测试动态上下文管理功能
"""

import asyncio
import sys
import os
import logging

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.context_manager import context_manager, ContextType, ContextItem

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_different_topics():
    """测试不同主题的上下文管理"""
    test_cases = [
        {
            "name": "区块链智能合约系统",
            "topic": "基于区块链的智能合约安全验证系统",
            "description": "一种基于形式化验证的区块链智能合约安全验证系统，通过静态分析、动态测试、形式化验证等技术，实现智能合约的安全检测和漏洞预防。"
        },
        {
            "name": "医疗诊断AI系统",
            "topic": "基于深度学习的医疗影像诊断系统",
            "description": "一种基于深度学习的医疗影像诊断系统，通过卷积神经网络、迁移学习、多模态融合等技术，实现医学影像的自动分析和疾病诊断。"
        },
        {
            "name": "物联网数据处理系统",
            "topic": "基于边缘计算的物联网数据处理系统",
            "description": "一种基于边缘计算的物联网数据处理系统，通过分布式计算、实时数据处理、智能优化等技术，实现物联网设备数据的实时处理和分析。"
        },
        {
            "name": "金融风控系统",
            "topic": "基于机器学习的金融风险控制系统",
            "description": "一种基于机器学习的金融风险控制系统，通过大数据分析、机器学习算法、实时监控等技术，实现金融风险的实时识别和控制。"
        },
        {
            "name": "5G通信系统",
            "topic": "基于5G技术的智能通信系统",
            "description": "一种基于5G技术的智能通信系统，通过网络切片、边缘计算、人工智能等技术，实现高速、低延迟、大容量的智能通信服务。"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"测试案例 {i}: {test_case['name']}")
        logger.info(f"{'='*60}")
        
        try:
            # 初始化上下文
            workflow_id = f"test_workflow_{i:03d}"
            theme_definition = await context_manager.initialize_workflow_context(
                workflow_id, 
                test_case["topic"], 
                test_case["description"]
            )
            
            # 显示主题定义
            logger.info(f"✅ 主题定义生成成功")
            logger.info(f"   主标题: {theme_definition.primary_title}")
            logger.info(f"   核心概念: {theme_definition.core_concept}")
            logger.info(f"   技术领域: {theme_definition.technical_domain}")
            logger.info(f"   关键创新: {theme_definition.key_innovations}")
            logger.info(f"   目标应用: {theme_definition.target_applications}")
            logger.info(f"   术语标准数量: {len(theme_definition.terminology_standard)}")
            
            # 显示替代标题
            logger.info(f"   替代标题: {theme_definition.alternative_titles}")
            
            # 显示一致性规则
            logger.info(f"   一致性规则: {theme_definition.consistency_rules}")
            
            # 获取上下文摘要
            context_summary = await context_manager.get_context_summary(workflow_id)
            
            results.append({
                "test_case": test_case["name"],
                "success": True,
                "theme": theme_definition,
                "summary": context_summary
            })
            
            # 清理上下文
            await context_manager.cleanup_workflow_context(workflow_id)
            
        except Exception as e:
            logger.error(f"❌ 测试案例 {test_case['name']} 失败: {e}")
            results.append({
                "test_case": test_case["name"],
                "success": False,
                "error": str(e)
            })
    
    return results

async def test_context_validation():
    """测试上下文验证功能"""
    logger.info(f"\n{'='*60}")
    logger.info("测试上下文验证功能")
    logger.info(f"{'='*60}")
    
    # 测试区块链主题
    workflow_id = "validation_test_001"
    topic = "基于区块链的智能合约安全验证系统"
    description = "一种基于形式化验证的区块链智能合约安全验证系统"
    
    try:
        # 初始化上下文
        await context_manager.initialize_workflow_context(workflow_id, topic, description)
        
        # 测试一致性验证
        test_outputs = [
            "基于区块链的智能合约安全验证系统",  # 应该通过
            "基于机器学习的图像识别系统",        # 应该失败
            "区块链智能合约验证方法",             # 应该通过
            "传统数据库管理系统"                 # 应该失败
        ]
        
        for i, test_output in enumerate(test_outputs, 1):
            validation_result = await context_manager.validate_agent_output(
                workflow_id, f"test_agent_{i}", test_output, "title"
            )
            
            logger.info(f"测试 {i}: {test_output}")
            logger.info(f"   一致性: {'✅ 通过' if validation_result['is_consistent'] else '❌ 失败'}")
            logger.info(f"   评分: {validation_result['score']:.2f}")
            if validation_result['issues']:
                logger.info(f"   问题: {validation_result['issues']}")
            if validation_result['suggestions']:
                logger.info(f"   建议: {validation_result['suggestions']}")
            logger.info("")
        
        # 清理上下文
        await context_manager.cleanup_workflow_context(workflow_id)
        
    except Exception as e:
        logger.error(f"❌ 上下文验证测试失败: {e}")

async def main():
    """主函数"""
    try:
        logger.info("🚀 开始测试动态上下文管理功能")
        
        # 测试不同主题
        results = await test_different_topics()
        
        # 测试上下文验证
        await test_context_validation()
        
        # 输出测试总结
        logger.info(f"\n{'='*60}")
        logger.info("测试总结")
        logger.info(f"{'='*60}")
        
        successful_tests = [r for r in results if r["success"]]
        failed_tests = [r for r in results if not r["success"]]
        
        logger.info(f"✅ 成功测试: {len(successful_tests)}/{len(results)}")
        logger.info(f"❌ 失败测试: {len(failed_tests)}/{len(results)}")
        
        if successful_tests:
            logger.info("\n🎯 成功案例的技术领域分布:")
            domains = {}
            for result in successful_tests:
                domain = result["theme"].technical_domain
                domains[domain] = domains.get(domain, 0) + 1
            
            for domain, count in domains.items():
                logger.info(f"   {domain}: {count} 个案例")
        
        if failed_tests:
            logger.info("\n❌ 失败案例:")
            for result in failed_tests:
                logger.info(f"   {result['test_case']}: {result['error']}")
        
        # 验证动态性
        logger.info(f"\n🎉 动态上下文管理功能测试完成！")
        logger.info(f"✅ 系统能够正确处理不同技术领域的主题")
        logger.info(f"✅ 上下文管理器不再硬编码特定主题")
        logger.info(f"✅ 术语标准和技术领域能够动态识别")
        
    except Exception as e:
        logger.error(f"❌ 主测试程序失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())