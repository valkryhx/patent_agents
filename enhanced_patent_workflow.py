#!/usr/bin/env python3
"""
Enhanced Patent Workflow with Context Management
整合上下文管理功能的专利撰写工作流
"""

import asyncio
import sys
import os
import logging
import time
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.context_manager import context_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedPatentWorkflow:
    """增强的专利撰写工作流，整合上下文管理"""
    
    def __init__(self):
        self.system = PatentAgentSystem()
        self.workflow_id = None
        self.topic = None
        self.description = None
        
    async def start_workflow(self, topic: str, description: str) -> Dict[str, Any]:
        """启动增强的专利撰写工作流"""
        try:
            logger.info("🚀 启动增强的专利撰写工作流")
            logger.info(f"主题: {topic}")
            logger.info(f"描述: {description}")
            
            self.topic = topic
            self.description = description
            
            # 启动系统
            await self.system.start()
            logger.info("✅ 专利代理系统启动成功")
            
            # 启动工作流
            start_result = await self.system.execute_workflow(
                topic=topic,
                description=description,
                workflow_type="enhanced"
            )
            
            if not start_result["success"]:
                raise RuntimeError(f"启动工作流失败: {start_result.get('error')}")
                
            self.workflow_id = start_result["workflow_id"]
            logger.info(f"✅ 工作流启动成功: {self.workflow_id}")
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "message": "工作流启动成功"
            }
            
        except Exception as e:
            logger.error(f"❌ 启动工作流失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def monitor_workflow(self, max_wait: int = 1800) -> Dict[str, Any]:
        """监控工作流进度"""
        try:
            if not self.workflow_id:
                raise ValueError("工作流ID未设置")
                
            logger.info(f"📊 开始监控工作流: {self.workflow_id}")
            start_time = time.time()
            
            while True:
                # 获取工作流状态
                status_result = await self.system.get_workflow_status(self.workflow_id)
                
                if not status_result["success"]:
                    logger.error(f"获取工作流状态失败: {status_result.get('error')}")
                    break
                    
                workflow_data = status_result.get("workflow", {})
                overall_status = workflow_data.get("overall_status", "unknown")
                
                logger.info(f"📈 工作流状态: {overall_status}")
                
                # 获取上下文摘要
                context_summary = await context_manager.get_context_summary(self.workflow_id)
                if context_summary:
                    logger.info(f"📋 上下文摘要: {context_summary.get('theme', {}).get('primary_title')}")
                    
                # 检查是否完成
                if overall_status == "completed":
                    logger.info("🎉 工作流完成！")
                    break
                elif overall_status in ["failed", "error"]:
                    logger.error(f"❌ 工作流失败: {overall_status}")
                    break
                    
                # 检查超时
                elapsed = time.time() - start_time
                if elapsed > max_wait:
                    logger.warning(f"⏰ 监控超时 ({max_wait}s)")
                    break
                    
                await asyncio.sleep(30)  # 每30秒检查一次
                
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "status": overall_status
            }
            
        except Exception as e:
            logger.error(f"❌ 监控工作流失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def get_final_patent(self) -> Dict[str, Any]:
        """获取最终的专利文档"""
        try:
            if not self.workflow_id:
                raise ValueError("工作流ID未设置")
                
            logger.info(f"📄 获取最终专利文档: {self.workflow_id}")
            
            # 获取工作流状态
            status_result = await self.system.get_workflow_status(self.workflow_id)
            if not status_result["success"]:
                raise RuntimeError(f"获取工作流状态失败: {status_result.get('error')}")
                
            workflow_data = status_result.get("workflow", {})
            results = workflow_data.get("results", {})
            
            # 构建完整的专利文档
            patent_document = await self._build_patent_document(results)
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "patent_document": patent_document
            }
            
        except Exception as e:
            logger.error(f"❌ 获取最终专利文档失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _build_patent_document(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """构建完整的专利文档"""
        try:
            # 获取主题定义
            theme_definition = await context_manager.get_context_summary(self.workflow_id)
            theme = theme_definition.get("theme", {})
            
            patent_document = {
                "title": theme.get("primary_title", self.topic),
                "core_concept": theme.get("core_concept", ""),
                "technical_domain": theme.get("technical_domain", ""),
                "key_innovations": theme.get("key_innovations", []),
                "sections": {}
            }
            
            # 提取各个阶段的结果
            for stage_key, stage_result in results.items():
                if stage_key.startswith("stage_"):
                    stage_data = stage_result.get("result", {})
                    stage_name = self._get_stage_name(stage_key)
                    
                    if stage_name == "Planning & Strategy":
                        patent_document["sections"]["strategy"] = stage_data.get("strategy", {})
                    elif stage_name == "Prior Art Search":
                        patent_document["sections"]["prior_art"] = stage_data.get("search_results", {})
                    elif stage_name == "Innovation Discussion":
                        patent_document["sections"]["discussion"] = stage_data.get("discussion", {})
                    elif stage_name == "Patent Drafting":
                        patent_document["sections"]["draft"] = stage_data.get("patent_draft", {})
                    elif stage_name == "Quality Review":
                        patent_document["sections"]["review"] = stage_data.get("feedback", {})
                    elif stage_name == "Final Rewrite":
                        patent_document["sections"]["final_draft"] = stage_data.get("improved_draft", {})
                        
            return patent_document
            
        except Exception as e:
            logger.error(f"构建专利文档失败: {e}")
            return {}
            
    def _get_stage_name(self, stage_key: str) -> str:
        """获取阶段名称"""
        stage_mapping = {
            "stage_0": "Planning & Strategy",
            "stage_1": "Prior Art Search", 
            "stage_2": "Innovation Discussion",
            "stage_3": "Patent Drafting",
            "stage_4": "Quality Review",
            "stage_5": "Final Rewrite"
        }
        return stage_mapping.get(stage_key, "Unknown Stage")
        
    async def generate_markdown_document(self, patent_document: Dict[str, Any]) -> str:
        """生成Markdown格式的专利文档"""
        try:
            markdown_content = []
            
            # 标题
            markdown_content.append(f"# {patent_document.get('title', '专利文档')}")
            markdown_content.append("")
            
            # 核心概念
            core_concept = patent_document.get("core_concept")
            if core_concept:
                markdown_content.append("## 核心概念")
                markdown_content.append(core_concept)
                markdown_content.append("")
                
            # 技术领域
            technical_domain = patent_document.get("technical_domain")
            if technical_domain:
                markdown_content.append("## 技术领域")
                markdown_content.append(technical_domain)
                markdown_content.append("")
                
            # 关键创新点
            key_innovations = patent_document.get("key_innovations", [])
            if key_innovations:
                markdown_content.append("## 关键创新点")
                for i, innovation in enumerate(key_innovations, 1):
                    markdown_content.append(f"{i}. {innovation}")
                markdown_content.append("")
                
            # 各个章节
            sections = patent_document.get("sections", {})
            
            # 策略规划
            if "strategy" in sections:
                strategy = sections["strategy"]
                markdown_content.append("## 策略规划")
                if strategy.get("summary"):
                    markdown_content.append(strategy["summary"])
                markdown_content.append("")
                
            # 现有技术
            if "prior_art" in sections:
                prior_art = sections["prior_art"]
                markdown_content.append("## 现有技术")
                if prior_art.get("summary"):
                    markdown_content.append(prior_art["summary"])
                markdown_content.append("")
                
            # 创新讨论
            if "discussion" in sections:
                discussion = sections["discussion"]
                markdown_content.append("## 创新讨论")
                if discussion.get("summary"):
                    markdown_content.append(discussion["summary"])
                markdown_content.append("")
                
            # 专利草稿
            if "draft" in sections:
                draft = sections["draft"]
                markdown_content.append("## 专利草稿")
                if draft.get("title"):
                    markdown_content.append(f"**标题**: {draft['title']}")
                if draft.get("abstract"):
                    markdown_content.append(f"**摘要**: {draft['abstract']}")
                markdown_content.append("")
                
            # 质量审查
            if "review" in sections:
                review = sections["review"]
                markdown_content.append("## 质量审查")
                if review.get("summary"):
                    markdown_content.append(review["summary"])
                markdown_content.append("")
                
            # 最终版本
            if "final_draft" in sections:
                final_draft = sections["final_draft"]
                markdown_content.append("## 最终版本")
                if final_draft.get("title"):
                    markdown_content.append(f"**标题**: {final_draft['title']}")
                if final_draft.get("abstract"):
                    markdown_content.append(f"**摘要**: {final_draft['abstract']}")
                markdown_content.append("")
                
            return "\n".join(markdown_content)
            
        except Exception as e:
            logger.error(f"生成Markdown文档失败: {e}")
            return f"# 专利文档生成失败\n\n错误: {str(e)}"
            
    async def cleanup(self):
        """清理资源"""
        try:
            if self.workflow_id:
                await context_manager.cleanup_workflow_context(self.workflow_id)
                
            await self.system.stop()
            logger.info("✅ 资源清理完成")
            
        except Exception as e:
            logger.error(f"❌ 清理资源失败: {e}")


async def main():
    """主函数"""
    try:
        # 创建增强工作流实例
        workflow = EnhancedPatentWorkflow()
        
        # 定义专利主题
        topic = "证据图增强的检索增强生成系统"
        description = """
        一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统。
        该系统能够：
        1. 构建多源异构信息的证据关系图
        2. 基于查询动态选择相关证据子图
        3. 利用证据图约束大语言模型的生成过程
        4. 提供完整的证据链和推理路径
        5. 显著提升生成内容的准确性和可解释性
        """
        
        # 启动工作流
        start_result = await workflow.start_workflow(topic, description)
        if not start_result["success"]:
            logger.error(f"启动工作流失败: {start_result.get('error')}")
            return
            
        # 监控工作流
        monitor_result = await workflow.monitor_workflow()
        if not monitor_result["success"]:
            logger.error(f"监控工作流失败: {monitor_result.get('error')}")
            return
            
        # 获取最终专利文档
        patent_result = await workflow.get_final_patent()
        if not patent_result["success"]:
            logger.error(f"获取专利文档失败: {patent_result.get('error')}")
            return
            
        # 生成Markdown文档
        markdown_content = await workflow.generate_markdown_document(patent_result["patent_document"])
        
        # 保存到文件
        output_file = f"enhanced_patent_{workflow.workflow_id}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        logger.info(f"✅ 专利文档已保存到: {output_file}")
        
        # 清理资源
        await workflow.cleanup()
        
    except Exception as e:
        logger.error(f"❌ 主程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())