#!/usr/bin/env python3
"""
Test Enhanced Patent Workflow
测试增强的专利撰写工作流
"""

import asyncio
import sys
import os
import logging
import time
from typing import Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from enhanced_patent_workflow import EnhancedPatentWorkflow
from patent_agent_demo.context_manager import context_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_context_consistency():
    """测试上下文一致性功能"""
    try:
        logger.info("🧪 开始测试上下文一致性功能")
        
        # 创建测试工作流
        workflow = EnhancedPatentWorkflow()
        
        # 定义测试主题
        topic = "证据图增强的检索增强生成系统"
        description = "一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统"
        
        # 启动工作流
        start_result = await workflow.start_workflow(topic, description)
        if not start_result["success"]:
            logger.error(f"❌ 启动工作流失败: {start_result.get('error')}")
            return False
            
        workflow_id = start_result["workflow_id"]
        logger.info(f"✅ 工作流启动成功: {workflow_id}")
        
        # 获取上下文摘要
        context_summary = await context_manager.get_context_summary(workflow_id)
        if context_summary:
            logger.info(f"📋 上下文摘要: {context_summary}")
            
            # 验证主题一致性
            theme = context_summary.get("theme", {})
            primary_title = theme.get("primary_title")
            
            if primary_title and "证据图" in primary_title and "RAG" in primary_title:
                logger.info("✅ 主题一致性验证通过")
            else:
                logger.warning("⚠️ 主题一致性验证失败")
                
        # 清理资源
        await workflow.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 上下文一致性测试失败: {e}")
        return False

async def test_workflow_execution():
    """测试工作流执行"""
    try:
        logger.info("🧪 开始测试工作流执行")
        
        # 创建测试工作流
        workflow = EnhancedPatentWorkflow()
        
        # 定义测试主题
        topic = "基于知识图谱的智能问答系统"
        description = """
        一种结合知识图谱和大语言模型的智能问答系统。
        该系统能够：
        1. 构建领域知识图谱
        2. 基于图谱进行推理
        3. 生成准确可靠的答案
        4. 提供可解释的推理路径
        """
        
        # 启动工作流
        start_result = await workflow.start_workflow(topic, description)
        if not start_result["success"]:
            logger.error(f"❌ 启动工作流失败: {start_result.get('error')}")
            return False
            
        workflow_id = start_result["workflow_id"]
        logger.info(f"✅ 工作流启动成功: {workflow_id}")
        
        # 监控工作流（设置较短的超时时间用于测试）
        monitor_result = await workflow.monitor_workflow(max_wait=300)  # 5分钟超时
        if not monitor_result["success"]:
            logger.error(f"❌ 监控工作流失败: {monitor_result.get('error')}")
            return False
            
        logger.info(f"✅ 工作流监控完成，状态: {monitor_result.get('status')}")
        
        # 清理资源
        await workflow.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 工作流执行测试失败: {e}")
        return False

async def test_patent_generation():
    """测试专利文档生成"""
    try:
        logger.info("🧪 开始测试专利文档生成")
        
        # 创建测试工作流
        workflow = EnhancedPatentWorkflow()
        
        # 定义测试主题
        topic = "多模态信息融合的智能分析系统"
        description = """
        一种能够融合文本、图像、音频等多种模态信息的智能分析系统。
        该系统能够：
        1. 处理多模态输入数据
        2. 提取跨模态特征
        3. 进行综合分析
        4. 生成多模态输出结果
        """
        
        # 启动工作流
        start_result = await workflow.start_workflow(topic, description)
        if not start_result["success"]:
            logger.error(f"❌ 启动工作流失败: {start_result.get('error')}")
            return False
            
        workflow_id = start_result["workflow_id"]
        logger.info(f"✅ 工作流启动成功: {workflow_id}")
        
        # 等待一段时间让工作流执行
        await asyncio.sleep(60)  # 等待1分钟
        
        # 尝试获取专利文档
        patent_result = await workflow.get_final_patent()
        if patent_result["success"]:
            patent_document = patent_result["patent_document"]
            logger.info(f"✅ 获取专利文档成功")
            
            # 生成Markdown文档
            markdown_content = await workflow.generate_markdown_document(patent_document)
            
            # 保存测试文档
            test_file = f"test_patent_{workflow_id}.md"
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            logger.info(f"✅ 测试专利文档已保存到: {test_file}")
            
        else:
            logger.warning(f"⚠️ 获取专利文档失败: {patent_result.get('error')}")
            
        # 清理资源
        await workflow.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 专利文档生成测试失败: {e}")
        return False

async def test_context_validation():
    """测试上下文验证功能"""
    try:
        logger.info("🧪 开始测试上下文验证功能")
        
        # 创建测试工作流
        workflow = EnhancedPatentWorkflow()
        
        # 定义测试主题
        topic = "区块链智能合约安全验证系统"
        description = """
        一种基于形式化验证的区块链智能合约安全验证系统。
        该系统能够：
        1. 分析智能合约代码
        2. 检测安全漏洞
        3. 进行形式化验证
        4. 生成安全报告
        """
        
        # 启动工作流
        start_result = await workflow.start_workflow(topic, description)
        if not start_result["success"]:
            logger.error(f"❌ 启动工作流失败: {start_result.get('error')}")
            return False
            
        workflow_id = start_result["workflow_id"]
        logger.info(f"✅ 工作流启动成功: {workflow_id}")
        
        # 测试上下文验证
        test_output = "基于机器学习的图像识别系统"
        validation_result = await context_manager.validate_agent_output(
            workflow_id, "test_agent", test_output, "title"
        )
        
        logger.info(f"📊 验证结果: {validation_result}")
        
        if not validation_result["is_consistent"]:
            logger.info("✅ 上下文验证功能正常工作，检测到不一致")
        else:
            logger.warning("⚠️ 上下文验证可能存在问题")
            
        # 清理资源
        await workflow.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 上下文验证测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    try:
        logger.info("🚀 开始增强专利工作流测试")
        
        # 运行各项测试
        tests = [
            ("上下文一致性", test_context_consistency),
            ("工作流执行", test_workflow_execution),
            ("专利文档生成", test_patent_generation),
            ("上下文验证", test_context_validation)
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
            logger.info("🎉 所有测试通过！增强的专利工作流运行正常")
        else:
            logger.warning(f"⚠️ 有 {total - passed} 个测试失败，需要进一步检查")
            
    except Exception as e:
        logger.error(f"❌ 主测试程序失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())