#!/usr/bin/env python3
"""
Complete Patent Document Generation
完整的专利文档生成脚本，整合上下文管理和所有智能体功能
"""

import asyncio
import sys
import os
import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

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

class CompletePatentGenerator:
    """完整的专利文档生成器"""
    
    def __init__(self):
        self.workflow = EnhancedPatentWorkflow()
        self.workflow_id = None
        self.topic = None
        self.description = None
        self.start_time = None
        
    async def generate_patent(self, topic: str, description: str, 
                            output_dir: str = "output") -> Dict[str, Any]:
        """生成完整的专利文档"""
        try:
            self.start_time = time.time()
            self.topic = topic
            self.description = description
            
            logger.info("🚀 开始生成完整专利文档")
            logger.info(f"主题: {topic}")
            logger.info(f"输出目录: {output_dir}")
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 启动工作流
            start_result = await self.workflow.start_workflow(topic, description)
            if not start_result["success"]:
                raise RuntimeError(f"启动工作流失败: {start_result.get('error')}")
                
            self.workflow_id = start_result["workflow_id"]
            logger.info(f"✅ 工作流启动成功: {self.workflow_id}")
            
            # 监控工作流
            monitor_result = await self.workflow.monitor_workflow()
            if not monitor_result["success"]:
                raise RuntimeError(f"监控工作流失败: {monitor_result.get('error')}")
                
            logger.info(f"✅ 工作流执行完成，状态: {monitor_result.get('status')}")
            
            # 获取最终专利文档
            patent_result = await self.workflow.get_final_patent()
            if not patent_result["success"]:
                raise RuntimeError(f"获取专利文档失败: {patent_result.get('error')}")
                
            patent_document = patent_result["patent_document"]
            logger.info("✅ 获取专利文档成功")
            
            # 生成各种格式的文档
            files_generated = await self._generate_all_formats(patent_document, output_dir)
            
            # 生成执行报告
            execution_report = await self._generate_execution_report(files_generated)
            
            # 保存执行报告
            report_file = os.path.join(output_dir, f"execution_report_{self.workflow_id}.json")
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(execution_report, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ 执行报告已保存到: {report_file}")
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "files_generated": files_generated,
                "execution_report": execution_report
            }
            
        except Exception as e:
            logger.error(f"❌ 生成专利文档失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": self.workflow_id
            }
        finally:
            # 清理资源
            await self.workflow.cleanup()
            
    async def _generate_all_formats(self, patent_document: Dict[str, Any], 
                                  output_dir: str) -> Dict[str, str]:
        """生成所有格式的文档"""
        files_generated = {}
        
        try:
            # 生成Markdown格式
            markdown_content = await self.workflow.generate_markdown_document(patent_document)
            markdown_file = os.path.join(output_dir, f"patent_{self.workflow_id}.md")
            with open(markdown_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            files_generated["markdown"] = markdown_file
            logger.info(f"✅ Markdown文档已生成: {markdown_file}")
            
            # 生成JSON格式
            json_file = os.path.join(output_dir, f"patent_{self.workflow_id}.json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(patent_document, f, ensure_ascii=False, indent=2)
            files_generated["json"] = json_file
            logger.info(f"✅ JSON文档已生成: {json_file}")
            
            # 生成结构化文档
            structured_content = await self._generate_structured_document(patent_document)
            structured_file = os.path.join(output_dir, f"patent_structured_{self.workflow_id}.md")
            with open(structured_file, "w", encoding="utf-8") as f:
                f.write(structured_content)
            files_generated["structured"] = structured_file
            logger.info(f"✅ 结构化文档已生成: {structured_file}")
            
            # 生成上下文摘要
            context_summary = await context_manager.get_context_summary(self.workflow_id)
            if context_summary:
                context_file = os.path.join(output_dir, f"context_summary_{self.workflow_id}.json")
                with open(context_file, "w", encoding="utf-8") as f:
                    json.dump(context_summary, f, ensure_ascii=False, indent=2)
                files_generated["context"] = context_file
                logger.info(f"✅ 上下文摘要已生成: {context_file}")
                
        except Exception as e:
            logger.error(f"生成文档格式失败: {e}")
            
        return files_generated
        
    async def _generate_structured_document(self, patent_document: Dict[str, Any]) -> str:
        """生成结构化的专利文档"""
        try:
            content = []
            
            # 文档头部
            content.append("# 专利文档")
            content.append("")
            content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            content.append(f"**工作流ID**: {self.workflow_id}")
            content.append("")
            
            # 基本信息
            content.append("## 基本信息")
            content.append("")
            content.append(f"**标题**: {patent_document.get('title', 'N/A')}")
            content.append(f"**核心概念**: {patent_document.get('core_concept', 'N/A')}")
            content.append(f"**技术领域**: {patent_document.get('technical_domain', 'N/A')}")
            content.append("")
            
            # 关键创新点
            key_innovations = patent_document.get("key_innovations", [])
            if key_innovations:
                content.append("## 关键创新点")
                content.append("")
                for i, innovation in enumerate(key_innovations, 1):
                    content.append(f"{i}. {innovation}")
                content.append("")
                
            # 各个章节
            sections = patent_document.get("sections", {})
            
            # 策略规划
            if "strategy" in sections:
                strategy = sections["strategy"]
                content.append("## 策略规划")
                content.append("")
                if strategy.get("summary"):
                    content.append(strategy["summary"])
                if strategy.get("key_innovations"):
                    content.append("")
                    content.append("### 规划的创新点")
                    for innovation in strategy["key_innovations"]:
                        content.append(f"- {innovation}")
                content.append("")
                
            # 现有技术
            if "prior_art" in sections:
                prior_art = sections["prior_art"]
                content.append("## 现有技术分析")
                content.append("")
                if prior_art.get("summary"):
                    content.append(prior_art["summary"])
                content.append("")
                
            # 创新讨论
            if "discussion" in sections:
                discussion = sections["discussion"]
                content.append("## 创新讨论")
                content.append("")
                if discussion.get("summary"):
                    content.append(discussion["summary"])
                if discussion.get("key_points"):
                    content.append("")
                    content.append("### 关键讨论点")
                    for point in discussion["key_points"]:
                        content.append(f"- {point}")
                content.append("")
                
            # 专利草稿
            if "draft" in sections:
                draft = sections["draft"]
                content.append("## 专利草稿")
                content.append("")
                if draft.get("title"):
                    content.append(f"**标题**: {draft['title']}")
                if draft.get("abstract"):
                    content.append("")
                    content.append("### 摘要")
                    content.append(draft["abstract"])
                if draft.get("claims"):
                    content.append("")
                    content.append("### 权利要求")
                    for i, claim in enumerate(draft["claims"], 1):
                        content.append(f"{i}. {claim}")
                content.append("")
                
            # 质量审查
            if "review" in sections:
                review = sections["review"]
                content.append("## 质量审查")
                content.append("")
                if review.get("summary"):
                    content.append(review["summary"])
                if review.get("issues"):
                    content.append("")
                    content.append("### 审查问题")
                    for issue in review["issues"]:
                        content.append(f"- {issue}")
                content.append("")
                
            # 最终版本
            if "final_draft" in sections:
                final_draft = sections["final_draft"]
                content.append("## 最终版本")
                content.append("")
                if final_draft.get("title"):
                    content.append(f"**标题**: {final_draft['title']}")
                if final_draft.get("abstract"):
                    content.append("")
                    content.append("### 最终摘要")
                    content.append(final_draft["abstract"])
                content.append("")
                
            # 文档尾部
            content.append("---")
            content.append("*本文档由增强的专利撰写工作流自动生成*")
            
            return "\n".join(content)
            
        except Exception as e:
            logger.error(f"生成结构化文档失败: {e}")
            return f"# 结构化文档生成失败\n\n错误: {str(e)}"
            
    async def _generate_execution_report(self, files_generated: Dict[str, str]) -> Dict[str, Any]:
        """生成执行报告"""
        try:
            execution_time = time.time() - self.start_time
            
            # 获取上下文摘要
            context_summary = await context_manager.get_context_summary(self.workflow_id)
            
            report = {
                "workflow_id": self.workflow_id,
                "topic": self.topic,
                "description": self.description,
                "execution_time": execution_time,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.now().isoformat(),
                "files_generated": files_generated,
                "context_summary": context_summary,
                "status": "completed"
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成执行报告失败: {e}")
            return {
                "workflow_id": self.workflow_id,
                "error": str(e),
                "status": "failed"
            }

async def main():
    """主函数"""
    try:
        # 创建专利生成器
        generator = CompletePatentGenerator()
        
        # 定义专利主题
        topic = "证据图增强的检索增强生成系统"
        description = """
        一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统。
        
        技术特点：
        1. 构建多源异构信息的证据关系图
        2. 基于查询动态选择相关证据子图
        3. 利用证据图约束大语言模型的生成过程
        4. 提供完整的证据链和推理路径
        5. 显著提升生成内容的准确性和可解释性
        
        应用场景：
        - 智能问答系统
        - 决策支持系统
        - 知识管理系统
        - 内容生成系统
        - 信息检索系统
        
        技术优势：
        - 提高回答准确性
        - 增强可解释性
        - 提供证据溯源
        - 支持复杂推理
        - 降低幻觉风险
        """
        
        # 生成专利文档
        result = await generator.generate_patent(topic, description)
        
        if result["success"]:
            logger.info("🎉 专利文档生成成功！")
            logger.info(f"工作流ID: {result['workflow_id']}")
            logger.info(f"生成文件: {list(result['files_generated'].keys())}")
            
            # 显示生成的文件
            for format_type, file_path in result['files_generated'].items():
                logger.info(f"📄 {format_type}: {file_path}")
                
        else:
            logger.error(f"❌ 专利文档生成失败: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ 主程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())