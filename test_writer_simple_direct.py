#!/usr/bin/env python3
"""
独立测试简化版Writer Agent的脚本
直接测试核心功能，避免导入整个agents模块
"""

import asyncio
import logging
import sys
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_writer_simple.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_writer_agent_simple():
    """直接测试简化版Writer Agent"""
    
    try:
        logger.info("🚀 开始测试简化版Writer Agent")
        
        # 直接导入简化版Writer Agent
        sys.path.append(os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))
        from agents.writer_agent_simple import WriterAgentSimple
        
        # 创建Writer Agent实例
        writer_agent = WriterAgentSimple(test_mode=True)
        await writer_agent.start()
        
        logger.info("✅ Writer Agent初始化成功")
        
        # 准备测试数据
        test_topic = "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
        test_description = "一种智能化的函数参数推断系统，通过语义理解和分层调用机制提高参数推断的准确性和效率"
        
        # 模拟previous_results
        previous_results = {
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
                            "相关专利：智能参数优化系统"
                        ]
                    }
                }
            },
            "discussion": {
                "result": {
                    "key_insights": ["语义理解的重要性", "分层调用的优势"],
                    "technical_approach": "基于深度学习的参数推断"
                }
            }
        }
        
        # 准备任务数据
        task_data = {
            "type": "patent_drafting",
            "topic": test_topic,
            "description": test_description,
            "previous_results": previous_results,
            "workflow_id": "test_workflow_123",
            "test_mode": True
        }
        
        logger.info(f"📋 执行Writer Agent任务")
        logger.info(f"主题: {test_topic}")
        
        # 执行任务
        start_time = asyncio.get_event_loop().time()
        result = await writer_agent.execute_task(task_data)
        end_time = asyncio.get_event_loop().time()
        
        execution_time = end_time - start_time
        logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
        
        # 分析结果
        if result.success:
            logger.info("✅ Writer Agent执行成功")
            
            # 提取专利草稿
            patent_draft = result.data.get("patent_draft")
            if patent_draft:
                logger.info("📄 专利草稿生成成功")
                
                # 检查内容质量
                title = getattr(patent_draft, 'title', '')
                abstract = getattr(patent_draft, 'abstract', '')
                detailed_description = getattr(patent_draft, 'detailed_description', '')
                claims = getattr(patent_draft, 'claims', [])
                
                logger.info(f"📊 内容统计:")
                logger.info(f"  标题长度: {len(title)} 字符")
                logger.info(f"  摘要长度: {len(abstract)} 字符")
                logger.info(f"  详细描述长度: {len(detailed_description)} 字符")
                logger.info(f"  权利要求数量: {len(claims)}")
                
                # 检查是否包含伪代码和Mermaid图
                has_pseudocode = "```python" in detailed_description or "伪代码" in detailed_description
                has_mermaid = "```mermaid" in detailed_description or "graph" in detailed_description
                
                logger.info(f"🔍 内容质量检查:")
                logger.info(f"  包含伪代码: {'✅' if has_pseudocode else '❌'}")
                logger.info(f"  包含Mermaid图: {'✅' if has_mermaid else '❌'}")
                
                # 保存结果到文件
                output_file = "test_writer_simple_output.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 简化版Writer Agent测试结果\n\n")
                    f.write(f"**主题**: {test_topic}\n\n")
                    f.write(f"**执行时间**: {execution_time:.2f}秒\n\n")
                    f.write(f"**内容质量**:\n")
                    f.write(f"- 标题长度: {len(title)} 字符\n")
                    f.write(f"- 摘要长度: {len(abstract)} 字符\n")
                    f.write(f"- 详细描述长度: {len(detailed_description)} 字符\n")
                    f.write(f"- 权利要求数量: {len(claims)}\n")
                    f.write(f"- 包含伪代码: {'是' if has_pseudocode else '否'}\n")
                    f.write(f"- 包含Mermaid图: {'是' if has_mermaid else '否'}\n\n")
                    
                    f.write(f"## 专利标题\n\n{title}\n\n")
                    f.write(f"## 摘要\n\n{abstract}\n\n")
                    f.write(f"## 详细描述\n\n{detailed_description}\n\n")
                    f.write(f"## 权利要求\n\n")
                    for i, claim in enumerate(claims, 1):
                        f.write(f"{i}. {claim}\n\n")
                
                logger.info(f"💾 结果已保存到: {output_file}")
                
                return True
            else:
                logger.error("❌ 专利草稿为空")
                return False
        else:
            logger.error(f"❌ Writer Agent执行失败: {result.error_message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")
        import traceback
        logger.error(f"📋 错误详情: {traceback.format_exc()}")
        return False

async def main():
    """主函数"""
    logger.info("🎯 开始简化版Writer Agent测试")
    
    success = await test_writer_agent_simple()
    
    # 总结
    logger.info("\n" + "="*50)
    logger.info("测试总结")
    logger.info("="*50)
    
    if success:
        logger.info("🎉 测试通过！简化版Writer Agent工作正常")
        logger.info("✅ 基本功能测试: 通过")
        logger.info("💡 建议: Writer Agent可以正常使用")
    else:
        logger.info("❌ 测试失败")
        logger.info("❌ 基本功能测试: 失败")
        logger.info("💡 建议: 检查Writer Agent配置和代码")

if __name__ == "__main__":
    asyncio.run(main())