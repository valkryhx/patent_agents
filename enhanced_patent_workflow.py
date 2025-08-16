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
            try:
                self.workflow_id = await self.system.execute_workflow(
                    topic=topic,
                    description=description,
                    workflow_type="enhanced"
                )
                logger.info(f"✅ 工作流启动成功: {self.workflow_id}")
            except Exception as e:
                logger.error(f"启动工作流失败: {e}")
                import traceback
                traceback.print_exc()
                raise RuntimeError(f"启动工作流失败: {e}")
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "message": "工作流启动成功"
            }
            
        except Exception as e:
            logger.error(f"❌ 启动工作流失败: {e}")
            import traceback
            traceback.print_exc()
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
            last_status = None
            
            while True:
                # 获取工作流状态
                try:
                    status_result = await self.system.get_workflow_status(self.workflow_id)
                    workflow_data = status_result.get("workflow", {})
                    
                    # Handle both dictionary and object cases
                    if hasattr(workflow_data, 'overall_status'):
                        overall_status = workflow_data.overall_status
                    elif isinstance(workflow_data, dict):
                        overall_status = workflow_data.get("overall_status", "unknown")
                    else:
                        overall_status = "unknown"
                        
                    # Get current stage info
                    current_stage = None
                    if hasattr(workflow_data, 'current_stage'):
                        current_stage = workflow_data.current_stage
                    elif isinstance(workflow_data, dict):
                        current_stage = workflow_data.get("current_stage", 0)
                        
                    # Get stages info
                    stages = []
                    if hasattr(workflow_data, 'stages'):
                        stages = workflow_data.stages
                    elif isinstance(workflow_data, dict):
                        stages = workflow_data.get("stages", [])
                        
                except Exception as e:
                    logger.error(f"获取工作流状态失败: {e}")
                    import traceback
                    traceback.print_exc()
                    break
                
                # Log status changes
                if overall_status != last_status:
                    logger.info(f"📈 工作流状态变化: {last_status} -> {overall_status}")
                    last_status = overall_status
                
                logger.info(f"📈 工作流状态: {overall_status}, 当前阶段: {current_stage}")
                
                # Log stage details
                if stages and current_stage is not None and current_stage < len(stages):
                    stage = stages[current_stage]
                    if hasattr(stage, 'status'):
                        stage_status = stage.status
                        stage_name = stage.stage_name
                        logger.info(f"📋 当前阶段: {stage_name} - {stage_status}")
                        
                        # If stage is running for too long, log more details
                        if stage_status == 'running' and hasattr(stage, 'start_time') and stage.start_time:
                            elapsed = time.time() - stage.start_time
                            if elapsed > 300:  # 5 minutes
                                logger.warning(f"⚠️ 阶段 {stage_name} 运行时间过长: {elapsed:.1f}秒")
                
                # 获取上下文摘要
                try:
                    context_summary = await context_manager.get_context_summary(self.workflow_id)
                    if context_summary:
                        logger.info(f"📋 上下文摘要: {context_summary.get('theme', {}).get('primary_title')}")
                except Exception as e:
                    logger.warning(f"获取上下文摘要失败: {e}")
                    
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
            import traceback
            traceback.print_exc()
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
            try:
                status_result = await self.system.get_workflow_status(self.workflow_id)
                workflow_data = status_result.get("workflow", {})
                
                # Handle both dictionary and object cases
                if hasattr(workflow_data, 'results'):
                    results = workflow_data.results
                elif isinstance(workflow_data, dict):
                    results = workflow_data.get("results", {})
                else:
                    results = {}
            except Exception as e:
                raise RuntimeError(f"获取工作流状态失败: {e}")
            
            # 构建完整的专利文档
            patent_document = await self._build_patent_document(results)
            
            return {
                "success": True,
                "workflow_id": self.workflow_id,
                "patent_document": patent_document
            }
            
        except Exception as e:
            logger.error(f"❌ 获取最终专利文档失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _build_patent_document(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """构建完整的专利文档"""
        try:
            # 获取主题定义
            theme_definition = await context_manager.get_context_summary(self.workflow_id)
            
            # Handle both dictionary and object cases for theme_definition
            if isinstance(theme_definition, dict):
                theme = theme_definition.get("theme", {})
                patent_document = {
                    "title": theme.get("primary_title", self.topic),
                    "core_concept": theme.get("core_concept", ""),
                    "technical_domain": theme.get("technical_domain", ""),
                    "key_innovations": theme.get("key_innovations", []),
                    "sections": {}
                }
            else:
                # Handle object case
                patent_document = {
                    "title": self.topic,
                    "core_concept": "",
                    "technical_domain": "",
                    "key_innovations": [],
                    "sections": {}
                }
            
            # 提取各个阶段的结果
            for stage_key, stage_result in results.items():
                if stage_key.startswith("stage_"):
                    # Handle both dictionary and object cases
                    if isinstance(stage_result, dict):
                        stage_data = stage_result.get("result", {})
                    elif hasattr(stage_result, 'result'):
                        stage_data = stage_result.result
                    elif hasattr(stage_result, 'topic'):
                        # This is a PatentStrategy object
                        stage_data = stage_result
                    else:
                        stage_data = {}
                        
                    stage_name = self._get_stage_name(stage_key)
                    
                    if stage_name == "Planning & Strategy":
                        # Handle PatentStrategy object
                        if hasattr(stage_data, 'topic'):
                            # This is a PatentStrategy object
                            patent_document["sections"]["strategy"] = {
                                "summary": f"专利主题: {stage_data.topic}",
                                "description": stage_data.description,
                                "novelty_score": stage_data.novelty_score,
                                "inventive_step_score": stage_data.inventive_step_score,
                                "patentability_assessment": stage_data.patentability_assessment,
                                "key_innovation_areas": stage_data.key_innovation_areas,
                                "development_phases": stage_data.development_phases,
                                "competitive_analysis": stage_data.competitive_analysis,
                                "risk_assessment": stage_data.risk_assessment,
                                "timeline_estimate": stage_data.timeline_estimate,
                                "resource_requirements": stage_data.resource_requirements,
                                "success_probability": stage_data.success_probability
                            }
                        elif hasattr(stage_data, 'strategy'):
                            patent_document["sections"]["strategy"] = stage_data.strategy
                        elif isinstance(stage_data, dict):
                            patent_document["sections"]["strategy"] = stage_data.get("strategy", {})
                        else:
                            patent_document["sections"]["strategy"] = {"summary": str(stage_data)}
                    elif stage_name == "Prior Art Search":
                        if hasattr(stage_data, 'search_results'):
                            patent_document["sections"]["prior_art"] = stage_data.search_results
                        elif isinstance(stage_data, dict):
                            patent_document["sections"]["prior_art"] = stage_data.get("search_results", {})
                        else:
                            patent_document["sections"]["prior_art"] = {"summary": str(stage_data)}
                    elif stage_name == "Innovation Discussion":
                        if hasattr(stage_data, 'discussion'):
                            patent_document["sections"]["discussion"] = stage_data.discussion
                        elif isinstance(stage_data, dict):
                            patent_document["sections"]["discussion"] = stage_data.get("discussion", {})
                        else:
                            patent_document["sections"]["discussion"] = {"summary": str(stage_data)}
                    elif stage_name == "Patent Drafting":
                        if hasattr(stage_data, 'patent_draft'):
                            patent_document["sections"]["draft"] = stage_data.patent_draft
                        elif isinstance(stage_data, dict):
                            patent_document["sections"]["draft"] = stage_data.get("patent_draft", {})
                        else:
                            patent_document["sections"]["draft"] = {"summary": str(stage_data)}
                    elif stage_name == "Quality Review":
                        if hasattr(stage_data, 'feedback'):
                            patent_document["sections"]["review"] = stage_data.feedback
                        elif isinstance(stage_data, dict):
                            patent_document["sections"]["review"] = stage_data.get("feedback", {})
                        else:
                            patent_document["sections"]["review"] = {"summary": str(stage_data)}
                    elif stage_name == "Final Rewrite":
                        if hasattr(stage_data, 'improved_draft'):
                            patent_document["sections"]["final_draft"] = stage_data.improved_draft
                        elif isinstance(stage_data, dict):
                            patent_document["sections"]["final_draft"] = stage_data.get("improved_draft", {})
                        else:
                            patent_document["sections"]["final_draft"] = {"summary": str(stage_data)}
                        
            return patent_document
            
        except Exception as e:
            logger.error(f"构建专利文档失败: {e}")
            import traceback
            traceback.print_exc()
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
        
    def _safe_get(self, obj, key, default=None):
        """Safely get a value from either a dictionary or an object"""
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            elif hasattr(obj, key):
                return getattr(obj, key, default)
            else:
                return default
        except Exception:
            return default
        
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
                if hasattr(strategy, 'summary'):
                    markdown_content.append(strategy.summary)
                elif isinstance(strategy, dict) and strategy.get("summary"):
                    markdown_content.append(strategy["summary"])
                elif hasattr(strategy, 'topic'):
                    markdown_content.append(f"专利主题: {strategy.topic}")
                markdown_content.append("")
                
            # 现有技术
            if "prior_art" in sections:
                prior_art = sections["prior_art"]
                markdown_content.append("## 现有技术")
                if hasattr(prior_art, 'summary'):
                    markdown_content.append(prior_art.summary)
                elif isinstance(prior_art, dict) and prior_art.get("summary"):
                    markdown_content.append(prior_art["summary"])
                markdown_content.append("")
                
            # 创新讨论
            if "discussion" in sections:
                discussion = sections["discussion"]
                markdown_content.append("## 创新讨论")
                if hasattr(discussion, 'summary'):
                    markdown_content.append(discussion.summary)
                elif isinstance(discussion, dict) and discussion.get("summary"):
                    markdown_content.append(discussion["summary"])
                markdown_content.append("")
                
            # 专利草稿
            if "draft" in sections:
                draft = sections["draft"]
                markdown_content.append("## 专利草稿")
                if hasattr(draft, 'title'):
                    markdown_content.append(f"**标题**: {draft.title}")
                elif isinstance(draft, dict) and draft.get("title"):
                    markdown_content.append(f"**标题**: {draft['title']}")
                if hasattr(draft, 'abstract'):
                    markdown_content.append(f"**摘要**: {draft.abstract}")
                elif isinstance(draft, dict) and draft.get("abstract"):
                    markdown_content.append(f"**摘要**: {draft['abstract']}")
                markdown_content.append("")
                
            # 质量审查
            if "review" in sections:
                review = sections["review"]
                markdown_content.append("## 质量审查")
                if hasattr(review, 'summary'):
                    markdown_content.append(review.summary)
                elif isinstance(review, dict) and review.get("summary"):
                    markdown_content.append(review["summary"])
                markdown_content.append("")
                
            # 最终版本
            if "final_draft" in sections:
                final_draft = sections["final_draft"]
                markdown_content.append("## 最终版本")
                if hasattr(final_draft, 'title'):
                    markdown_content.append(f"**标题**: {final_draft.title}")
                elif isinstance(final_draft, dict) and final_draft.get("title"):
                    markdown_content.append(f"**标题**: {final_draft['title']}")
                if hasattr(final_draft, 'abstract'):
                    markdown_content.append(f"**摘要**: {final_draft.abstract}")
                elif isinstance(final_draft, dict) and final_draft.get("abstract"):
                    markdown_content.append(f"**摘要**: {final_draft['abstract']}")
                markdown_content.append("")
                
            return "\n".join(markdown_content)
            
        except Exception as e:
            logger.error(f"生成Markdown文档失败: {e}")
            import traceback
            traceback.print_exc()
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
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = """
        一种基于智能分层推理的多参数工具自适应调用系统，解决现有技术中多参数工具调用成功率低的问题。
        技术方案包括智能分层推理引擎、自适应参数收集策略、动态调用策略优化和智能错误诊断与恢复。
        技术效果：调用成功率从30%提升至85%以上，减少参数收集时间60%，错误诊断准确率90%。
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