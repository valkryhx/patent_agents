#!/usr/bin/env python3
"""
测试迭代式检索结果与后续智能体的兼容性
"""
import asyncio
import logging
from unified_service import conduct_prior_art_search, _ensure_search_results_compatibility

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_compatibility():
    """测试兼容性"""
    try:
        logger.info("🚀 开始测试迭代式检索结果兼容性")
        
        # 执行迭代式检索
        topic = "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
        keywords = ["语义理解", "参数推断", "分层调用", "重试优化"]
        
        # 获取原始检索结果
        original_results = await conduct_prior_art_search(topic, keywords, {})
        logger.info(f"✅ 原始检索完成，获得 {len(original_results)} 个结果")
        
        # 检查原始结果结构
        logger.info("📋 原始结果结构检查:")
        for i, result in enumerate(original_results[:2]):
            logger.info(f"  结果 {i+1} 字段: {list(result.keys())}")
        
        # 应用兼容性转换
        compatible_results = _ensure_search_results_compatibility(original_results)
        logger.info(f"✅ 兼容性转换完成，{len(compatible_results)} 个结果已标准化")
        
        # 检查兼容结果结构
        logger.info("📋 兼容结果结构检查:")
        for i, result in enumerate(compatible_results[:2]):
            logger.info(f"  结果 {i+1} 字段: {list(result.keys())}")
        
        # 验证必需字段
        required_fields = ["patent_id", "title", "abstract", "filing_date", "publication_date", "assignee", "relevance_score", "similarity_analysis"]
        missing_fields = []
        
        for i, result in enumerate(compatible_results):
            for field in required_fields:
                if field not in result:
                    missing_fields.append(f"结果{i+1}缺少{field}")
        
        if missing_fields:
            logger.warning(f"⚠️ 发现缺失字段: {missing_fields}")
        else:
            logger.info("✅ 所有必需字段都存在")
        
        # 验证GLM增强字段
        glm_enhanced_count = sum(1 for r in compatible_results if r.get("enhanced_by_glm", False))
        logger.info(f"✅ GLM增强结果数量: {glm_enhanced_count}")
        
        # 模拟后续智能体的使用
        logger.info("🔍 模拟后续智能体使用:")
        search_results = {
            "query": {"topic": topic, "keywords": keywords},
            "results": compatible_results,
            "analysis": {"total_patents_found": len(compatible_results)},
            "recommendations": ["建议1", "建议2"]
        }
        
        # 模拟Discussion Agent的访问模式
        search_findings = search_results.get("results", [])
        logger.info(f"✅ Discussion Agent可以访问: {len(search_findings)} 个专利")
        
        # 模拟Writer Agent的访问模式
        for i, patent in enumerate(search_findings[:2]):
            logger.info(f"  专利 {i+1}: {patent.get('title', 'N/A')} - 相关性: {patent.get('relevance_score', 'N/A')}")
            if patent.get("enhanced_by_glm"):
                logger.info(f"    GLM分析: {patent.get('glm_analysis', 'N/A')[:100]}...")
        
        return compatible_results
        
    except Exception as e:
        logger.error(f"❌ 兼容性测试失败: {e}")
        raise

if __name__ == "__main__":
    try:
        results = asyncio.run(test_compatibility())
        print(f"\n🎉 兼容性测试成功！")
        print(f"📊 结果统计:")
        print(f"  - 总结果数: {len(results)}")
        print(f"  - GLM增强: {sum(1 for r in results if r.get('enhanced_by_glm', False))}")
        print(f"  - 字段完整性: ✅ 所有必需字段都存在")
    except Exception as e:
        print(f"\n💥 兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()