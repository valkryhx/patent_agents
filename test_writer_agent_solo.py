#!/usr/bin/env python3
"""
独立测试Writer Agent的脚本
验证Writer Agent是否能正常调用LLM服务并生成高质量内容
"""

import asyncio
import logging
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_writer_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_writer_agent():
    """测试Writer Agent的独立功能"""
    
    try:
        logger.info("🚀 开始独立测试Writer Agent")
        
        # 导入简化版Writer Agent
        from patent_agent_demo.agents.writer_agent_simple import WriterAgentSimple
        
        # 创建简化版Writer Agent实例（测试模式）
        logger.info("📋 创建简化版Writer Agent实例")
        writer_agent = WriterAgentSimple(test_mode=True)
        
        # 手动初始化OpenAI客户端，避免启动消息处理循环
        logger.info("🔧 初始化OpenAI客户端")
        writer_agent.openai_client = writer_agent.openai_client or None
        if not writer_agent.openai_client:
            from patent_agent_demo.openai_client import OpenAIClient
            writer_agent.openai_client = OpenAIClient()
        
        logger.info("✅ Writer Agent初始化完成")
        
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
        logger.info(f"描述: {test_description}")
        
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
                output_file = "test_writer_agent_output.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Writer Agent测试结果\n\n")
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
                
                # 检查progress目录
                progress_dir = os.path.join("output", "progress", f"{test_topic.replace(' ', '_')}_test_wo")
                if os.path.exists(progress_dir):
                    logger.info(f"📁 Progress目录已创建: {progress_dir}")
                    progress_files = os.listdir(progress_dir)
                    logger.info(f"📄 Progress文件数量: {len(progress_files)}")
                    for file in progress_files:
                        logger.info(f"  - {file}")
                else:
                    logger.warning(f"⚠️ Progress目录未创建: {progress_dir}")
                
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

async def test_writer_agent_llm_calls():
    """测试Writer Agent的LLM调用功能"""
    
    try:
        logger.info("🧪 测试Writer Agent的LLM调用功能")
        
        # 导入简化版Writer Agent
        from patent_agent_demo.agents.writer_agent_simple import WriterAgentSimple
        
        # 创建简化版Writer Agent实例（真实模式）
        writer_agent = WriterAgentSimple(test_mode=False)
        
        # 手动初始化OpenAI客户端
        from patent_agent_demo.openai_client import OpenAIClient
        writer_agent.openai_client = OpenAIClient()
        
        # 测试简单的LLM调用
        test_prompt = "请为'智能参数推断系统'写一个简短的专利摘要，包含技术特点和创新点。"
        
        logger.info(f"📝 测试LLM调用: {test_prompt}")
        
        if hasattr(writer_agent, 'openai_client') and writer_agent.openai_client:
            response = await writer_agent.openai_client._generate_response(test_prompt)
            logger.info(f"✅ LLM调用成功，响应长度: {len(response)} 字符")
            logger.info(f"📄 响应内容: {response[:200]}...")
            return True
        else:
            logger.error("❌ OpenAI客户端未初始化")
            return False
            
    except Exception as e:
        logger.error(f"❌ LLM调用测试失败: {e}")
        return False

async def test_writer_agent_direct():
    """直接测试Writer Agent的核心方法"""
    
    try:
        logger.info("🔧 直接测试Writer Agent核心方法")
        
        # 导入简化版Writer Agent
        from patent_agent_demo.agents.writer_agent_simple import WriterAgentSimple
        
        # 创建简化版Writer Agent实例（测试模式）
        writer_agent = WriterAgentSimple(test_mode=True)
        
        # 手动初始化OpenAI客户端
        from patent_agent_demo.openai_client import OpenAIClient
        writer_agent.openai_client = OpenAIClient()
        
        # 测试_write_detailed_sections方法
        test_topic = "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
        
        # 创建测试数据
        from patent_agent_demo.google_a2a_client import PatentDraft
        test_patent_draft = PatentDraft(
            title=f"Patent Application: {test_topic}",
            abstract=f"An innovative system for {test_topic.lower()}",
            claims=[],
            detailed_description="",
            background="",
            summary="",
            drawings_description="",
            technical_diagrams=[]
        )
        
        from patent_agent_demo.agents.writer_agent import WritingTask
        writing_task = WritingTask(
            task_id="test_task_123",
            topic=test_topic,
            description=f"Patent application for {test_topic}",
            requirements={},
            previous_results={},
            target_audience="patent_examiners",
            writing_style="technical_legal"
        )
        
        # 创建progress目录
        progress_dir = os.path.join("output", "progress", "test_direct")
        os.makedirs(progress_dir, exist_ok=True)
        
        logger.info("📝 测试_write_detailed_sections方法")
        start_time = asyncio.get_event_loop().time()
        
        detailed_sections = await writer_agent._write_detailed_sections(
            writing_task, test_patent_draft, progress_dir
        )
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        
        logger.info(f"⏱️ _write_detailed_sections执行时间: {execution_time:.2f}秒")
        logger.info(f"📊 生成的章节数量: {len(detailed_sections)}")
        
        for section_name, content in detailed_sections.items():
            logger.info(f"  - {section_name}: {len(content)} 字符")
        
        # 检查是否包含伪代码和Mermaid图
        detailed_description = detailed_sections.get("detailed_description", "")
        has_pseudocode = "```python" in detailed_description or "伪代码" in detailed_description
        has_mermaid = "```mermaid" in detailed_description or "graph" in detailed_description
        
        logger.info(f"🔍 内容质量检查:")
        logger.info(f"  包含伪代码: {'✅' if has_pseudocode else '❌'}")
        logger.info(f"  包含Mermaid图: {'✅' if has_mermaid else '❌'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 直接测试失败: {e}")
        import traceback
        logger.error(f"📋 错误详情: {traceback.format_exc()}")
        return False

async def main():
    """主函数"""
    logger.info("🎯 开始Writer Agent独立测试")
    
    # 测试1: 基本功能测试
    logger.info("\n" + "="*50)
    logger.info("测试1: Writer Agent基本功能")
    logger.info("="*50)
    
    success1 = await test_writer_agent()
    
    # 测试2: LLM调用测试
    logger.info("\n" + "="*50)
    logger.info("测试2: LLM调用功能")
    logger.info("="*50)
    
    success2 = await test_writer_agent_llm_calls()
    
    # 测试3: 直接测试核心方法
    logger.info("\n" + "="*50)
    logger.info("测试3: 直接测试核心方法")
    logger.info("="*50)
    
    success3 = await test_writer_agent_direct()
    
    # 总结
    logger.info("\n" + "="*50)
    logger.info("测试总结")
    logger.info("="*50)
    
    if success1 and success2 and success3:
        logger.info("🎉 所有测试通过！Writer Agent工作正常")
        logger.info("✅ 基本功能测试: 通过")
        logger.info("✅ LLM调用测试: 通过")
        logger.info("✅ 核心方法测试: 通过")
        logger.info("💡 建议: Writer Agent可以正常使用")
    elif success2 and success3:
        logger.info("⚠️ 部分测试通过")
        logger.info("❌ 基本功能测试: 失败")
        logger.info("✅ LLM调用测试: 通过")
        logger.info("✅ 核心方法测试: 通过")
        logger.info("💡 建议: Writer Agent核心功能正常，但集成有问题")
    elif success2:
        logger.info("⚠️ 部分测试通过")
        logger.info("❌ 基本功能测试: 失败")
        logger.info("✅ LLM调用测试: 通过")
        logger.info("❌ 核心方法测试: 失败")
        logger.info("💡 建议: 检查Writer Agent内部逻辑")
    else:
        logger.info("❌ 所有测试失败")
        logger.info("❌ 基本功能测试: 失败")
        logger.info("❌ LLM调用测试: 失败")
        logger.info("❌ 核心方法测试: 失败")
        logger.info("💡 建议: 全面检查Writer Agent配置和代码")

if __name__ == "__main__":
    asyncio.run(main())