#!/usr/bin/env python3
"""
Generate Multimodal RAG Patent Example
生成多模态RAG专利文档示例
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from enhanced_patent_workflow import EnhancedPatentWorkflow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def generate_multimodal_rag_patent():
    """生成多模态RAG专利文档"""
    try:
        # 创建增强工作流实例
        workflow = EnhancedPatentWorkflow()
        
        # 定义多模态RAG专利主题
        topic = "基于多模态检索增强生成的智能问答系统"
        description = """
        一种基于多模态检索增强生成技术的智能问答系统，通过跨模态信息融合、多模态检索策略、视觉-语言对齐、音频-文本理解等核心技术，实现智能客服系统、多媒体内容生成、跨模态问答、视觉文档理解等功能。
        
        技术特点：
        1. 跨模态信息融合：同时处理文本、图像、音频、视频等多种模态信息
        2. 多模态检索策略：针对不同模态设计专门的检索算法和策略
        3. 视觉-语言对齐：实现视觉信息与语言信息的语义对齐和融合
        4. 音频-文本理解：将音频信息转换为文本并进行深度理解
        5. 多模态生成：基于多模态信息生成综合性的回答和内容
        
        创新点：
        1. 跨模态检索技术：同时检索多种模态的相关信息，提高信息获取的全面性
        2. 模态对齐算法：实现不同模态信息之间的语义对齐和有效融合
        3. 多模态生成机制：基于多模态信息生成更加丰富和准确的回答
        4. 实时处理能力：支持实时多模态信息的处理和响应
        
        应用场景：
        - 智能客服系统：支持文字、语音、图像等多种交互方式
        - 多媒体内容生成：基于多模态信息生成图文并茂的内容
        - 跨模态问答：支持基于图像、音频等非文本信息的问答
        - 视觉文档理解：自动理解和分析包含图像、表格的文档
        
        技术优势：
        - 信息获取更全面：通过多模态检索获取更丰富的信息
        - 理解能力更强：能够理解多种类型的信息和内容
        - 用户体验更好：支持多种交互方式，用户体验更自然
        - 应用场景更广：适用于更多样化的应用场景
        """
        
        logger.info("🚀 开始生成多模态RAG专利文档")
        logger.info(f"主题: {topic}")
        
        # 启动工作流
        start_result = await workflow.start_workflow(topic, description)
        if not start_result["success"]:
            logger.error(f"启动工作流失败: {start_result.get('error')}")
            return
            
        workflow_id = start_result["workflow_id"]
        logger.info(f"✅ 工作流启动成功: {workflow_id}")
        
        # 监控工作流（设置较短的超时时间用于演示）
        monitor_result = await workflow.monitor_workflow(max_wait=300)  # 5分钟超时
        if not monitor_result["success"]:
            logger.error(f"监控工作流失败: {monitor_result.get('error')}")
            return
            
        logger.info(f"✅ 工作流执行完成，状态: {monitor_result.get('status')}")
        
        # 获取专利文档
        patent_result = await workflow.get_final_patent()
        if not patent_result["success"]:
            logger.error(f"获取专利文档失败: {patent_result.get('error')}")
            return
            
        patent_document = patent_result["patent_document"]
        logger.info("✅ 获取专利文档成功")
        
        # 生成Markdown文档
        markdown_content = await workflow.generate_markdown_document(patent_document)
        
        # 保存文档
        output_file = f"multimodal_rag_patent_{workflow_id}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        logger.info(f"✅ 多模态RAG专利文档已保存到: {output_file}")
        
        # 清理资源
        await workflow.cleanup()
        
        return output_file
        
    except Exception as e:
        logger.error(f"❌ 生成多模态RAG专利文档失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """主函数"""
    try:
        logger.info("🎯 开始生成多模态RAG专利文档示例")
        
        # 生成专利文档
        output_file = await generate_multimodal_rag_patent()
        
        if output_file:
            logger.info(f"🎉 多模态RAG专利文档生成成功: {output_file}")
            
            # 显示文档内容预览
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                preview_lines = content.split('\n')[:50]
                preview = '\n'.join(preview_lines)
                
            print(f"\n📄 文档预览:")
            print("="*80)
            print(preview)
            print("="*80)
            print(f"\n完整文档已保存到: {output_file}")
            
        else:
            logger.error("❌ 专利文档生成失败")
            
    except Exception as e:
        logger.error(f"❌ 主程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())