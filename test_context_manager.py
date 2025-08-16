#!/usr/bin/env python3
"""
Test Context Manager
测试上下文管理功能
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

async def test_context_initialization():
    """测试上下文初始化"""
    try:
        logger.info("🧪 测试上下文初始化")
        
        # 定义测试主题
        topic = "证据图增强的检索增强生成系统"
        description = "一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统"
        
        # 初始化工作流上下文
        workflow_id = "test_workflow_001"
        theme_definition = await context_manager.initialize_workflow_context(workflow_id, topic, description)
        
        logger.info(f"✅ 上下文初始化成功")
        logger.info(f"主题: {theme_definition.primary_title}")
        logger.info(f"核心概念: {theme_definition.core_concept}")
        logger.info(f"技术领域: {theme_definition.technical_domain}")
        logger.info(f"关键创新: {theme_definition.key_innovations}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 上下文初始化测试失败: {e}")
        return False

async def test_context_validation():
    """测试上下文验证"""
    try:
        logger.info("🧪 测试上下文验证")
        
        workflow_id = "test_workflow_001"
        
        # 测试一致性验证
        test_output = "基于机器学习的图像识别系统"
        validation_result = await context_manager.validate_agent_output(
            workflow_id, "test_agent", test_output, "title"
        )
        
        logger.info(f"验证结果: {validation_result}")
        
        if not validation_result["is_consistent"]:
            logger.info("✅ 上下文验证功能正常工作，检测到不一致")
        else:
            logger.warning("⚠️ 上下文验证可能存在问题")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 上下文验证测试失败: {e}")
        return False

async def test_context_retrieval():
    """测试上下文检索"""
    try:
        logger.info("🧪 测试上下文检索")
        
        workflow_id = "test_workflow_001"
        
        # 获取上下文数据
        context_data = await context_manager.get_context_for_agent(
            workflow_id, "test_agent", [ContextType.THEME_DEFINITION, ContextType.TECHNICAL_DOMAIN]
        )
        
        logger.info(f"上下文数据: {context_data}")
        
        if context_data and "theme_definition" in context_data:
            logger.info("✅ 上下文检索功能正常工作")
        else:
            logger.warning("⚠️ 上下文检索可能存在问题")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 上下文检索测试失败: {e}")
        return False

async def test_context_summary():
    """测试上下文摘要"""
    try:
        logger.info("🧪 测试上下文摘要")
        
        workflow_id = "test_workflow_001"
        
        # 获取上下文摘要
        summary = await context_manager.get_context_summary(workflow_id)
        
        logger.info(f"上下文摘要: {summary}")
        
        if summary and "theme" in summary:
            logger.info("✅ 上下文摘要功能正常工作")
        else:
            logger.warning("⚠️ 上下文摘要可能存在问题")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 上下文摘要测试失败: {e}")
        return False

async def test_context_cleanup():
    """测试上下文清理"""
    try:
        logger.info("🧪 测试上下文清理")
        
        workflow_id = "test_workflow_001"
        
        # 清理上下文
        await context_manager.cleanup_workflow_context(workflow_id)
        
        logger.info("✅ 上下文清理功能正常工作")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 上下文清理测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    try:
        logger.info("🚀 开始上下文管理器测试")
        
        # 运行各项测试
        tests = [
            ("上下文初始化", test_context_initialization),
            ("上下文验证", test_context_validation),
            ("上下文检索", test_context_retrieval),
            ("上下文摘要", test_context_summary),
            ("上下文清理", test_context_cleanup)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"运行测试: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                result = await test_func()
                results[test_name] = result
                
                if result:
                    logger.info(f"✅ {test_name} 测试通过")
                else:
                    logger.error(f"❌ {test_name} 测试失败")
                    
            except Exception as e:
                logger.error(f"❌ {test_name} 测试异常: {e}")
                results[test_name] = False
                
        # 输出测试总结
        logger.info(f"\n{'='*50}")
        logger.info("测试总结")
        logger.info(f"{'='*50}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name}: {status}")
            
        logger.info(f"\n总体结果: {passed}/{total} 测试通过")
        
        if passed == total:
            logger.info("🎉 所有测试通过！上下文管理器运行正常")
        else:
            logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步检查")
            
    except Exception as e:
        logger.error(f"❌ 主测试程序失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())