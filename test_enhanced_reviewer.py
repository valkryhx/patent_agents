#!/usr/bin/env python3
"""
测试增强版审核智能体功能
"""

import asyncio
import logging
from patent_agent_demo.agents.reviewer_agent import EnhancedReviewerAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_reviewer():
    """测试增强版审核智能体"""
    
    # 初始化增强版审核智能体
    enhanced_reviewer = EnhancedReviewerAgent()
    
    # 测试数据
    topic = "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
    
    # 模拟第三章内容（现有技术）
    chapter_3_content = """
    第三章 现有技术
    
    目前，在智能函数调用领域存在以下主要技术：
    
    1. 传统函数调用方法
    - 基于固定参数列表的调用方式
    - 缺乏智能推断能力
    - 错误处理机制简单
    
    2. 现有智能调用技术
    - 基于规则的模式匹配
    - 简单的参数推断
    - 有限的错误恢复能力
    
    3. 相关专利技术
    - US12345678: 智能函数调用系统
    - CN98765432: 参数推断方法
    """
    
    # 模拟第四章内容（技术问题）
    chapter_4_content = """
    第四章 技术问题
    
    现有技术存在以下主要问题：
    
    1. 参数推断准确率低
    - 复杂参数类型推断困难
    - 上下文理解能力有限
    - 多参数组合推断效果差
    
    2. 错误处理机制不完善
    - 失败重试策略简单
    - 缺乏智能诊断能力
    - 恢复成功率低
    
    3. 系统性能问题
    - 调用延迟高
    - 资源消耗大
    - 扩展性差
    """
    
    # 模拟第五章内容（技术方案）
    chapter_5_content = """
    第五章 技术方案详细阐述
    
    5.1 系统架构设计
    
    本发明采用分层架构设计，包括：
    - 语义理解层：负责自然语言解析
    - 参数推断层：实现智能参数推断
    - 调用执行层：执行函数调用
    - 重试优化层：处理失败重试
    
    5.2 核心算法实现
    
    创新算法包括：
    - 语义理解算法：基于深度学习的自然语言处理
    - 参数推断算法：多维度参数智能推断
    - 重试优化算法：自适应重试策略
    
    5.3 数据流程设计
    
    数据处理流程：
    - 输入预处理
    - 语义分析
    - 参数推断
    - 调用执行
    - 结果验证
    - 失败重试
    """
    
    # 模拟检索结果
    search_results = {
        "智能函数调用": [
            {"title": "智能函数调用技术", "content": "相关技术内容"},
            {"title": "参数推断方法", "content": "现有推断技术"}
        ],
        "重试机制": [
            {"title": "失败重试策略", "content": "现有重试技术"},
            {"title": "错误恢复方法", "content": "恢复机制研究"}
        ]
    }
    
    try:
        logger.info("🚀 开始测试增强版审核智能体")
        
        # 执行综合审核
        review_results = await enhanced_reviewer.comprehensive_review(
            chapter_3_content=chapter_3_content,
            chapter_4_content=chapter_4_content,
            chapter_5_content=chapter_5_content,
            topic=topic,
            search_results=search_results
        )
        
        logger.info("✅ 综合审核完成")
        
        # 输出审核结果
        print("\n" + "="*80)
        print("增强版审核智能体测试结果")
        print("="*80)
        
        # 深度检索结果
        print("\n🔍 深度检索结果:")
        deep_search = review_results.get("deep_search_results", {})
        for keyword, results in deep_search.items():
            print(f"  - {keyword}: {len(results)} 条结果")
        
        # 新颖性分析
        print("\n📋 新颖性分析:")
        novelty = review_results.get("novelty_analysis", {})
        print(f"  - 评分: {novelty.get('novelty_score', 'N/A')}")
        print(f"  - 风险等级: {novelty.get('risk_level', 'N/A')}")
        
        # 创造性分析
        print("\n💡 创造性分析:")
        inventiveness = review_results.get("inventiveness_analysis", {})
        print(f"  - 评分: {inventiveness.get('inventiveness_score', 'N/A')}")
        print(f"  - 问题难度: {inventiveness.get('problem_difficulty', 'N/A')}")
        
        # 实用性分析
        print("\n🔧 实用性分析:")
        utility = review_results.get("utility_analysis", {})
        print(f"  - 评分: {utility.get('utility_score', 'N/A')}")
        print(f"  - 可行性: {utility.get('feasibility', 'N/A')}")
        
        # 批判性分析
        print("\n🤔 批判性分析:")
        critical = review_results.get("critical_analysis", {})
        print(f"  - 评分: {critical.get('critical_score', 'N/A')}")
        print(f"  - 风险等级: {critical.get('risk_level', 'N/A')}")
        
        # 总体评估
        print("\n📊 总体评估:")
        overall = review_results.get("overall_assessment", {})
        print(f"  - 综合评分: {overall.get('overall_score', 'N/A')}")
        print(f"  - 质量等级: {overall.get('quality_grade', 'N/A')}")
        print(f"  - 申请建议: {overall.get('application_recommendation', 'N/A')}")
        
        # 改进建议
        print("\n💡 改进建议:")
        improvements = review_results.get("improvement_suggestions", {})
        suggestions = improvements.get("suggestions", "暂无具体建议")
        print(f"  - {suggestions}")
        
        print("\n" + "="*80)
        print("测试完成")
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        print(f"测试失败: {e}")
    
    finally:
        # 关闭资源
        await enhanced_reviewer.close()

async def test_duckduckgo_search():
    """测试DuckDuckGo检索功能"""
    
    from patent_agent_demo.agents.reviewer_agent import EnhancedDuckDuckGoSearcher
    
    searcher = EnhancedDuckDuckGoSearcher()
    
    try:
        logger.info("🔍 测试DuckDuckGo检索功能")
        
        # 测试检索
        query = "智能函数调用 专利 技术方案"
        results = await searcher.search(query, max_results=5)
        
        print(f"\n检索查询: {query}")
        print(f"检索结果数量: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"  标题: {result.get('title', 'N/A')}")
            print(f"  来源: {result.get('source', 'N/A')}")
            print(f"  内容: {result.get('content', 'N/A')[:100]}...")
        
    except Exception as e:
        logger.error(f"❌ DuckDuckGo检索测试失败: {e}")
        print(f"DuckDuckGo检索测试失败: {e}")
    
    finally:
        await searcher.close()

if __name__ == "__main__":
    print("🧪 开始测试增强版审核智能体")
    
    # 运行测试
    asyncio.run(test_enhanced_reviewer())
    
    print("\n" + "-"*80)
    
    # 测试DuckDuckGo检索
    asyncio.run(test_duckduckgo_search())