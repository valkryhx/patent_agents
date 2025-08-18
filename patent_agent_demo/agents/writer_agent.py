"""
Writer Agent for Patent Agent System
Drafts patent applications and technical documentation
"""

import asyncio
import logging
from typing import Dict, Any, List
import os
from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..openai_client import OpenAIClient
from ..google_a2a_client import PatentDraft
from ..telemetry import A2ALoggingProxy

logger = logging.getLogger(__name__)

@dataclass
class WritingTask:
    """Writing task definition"""
    task_id: str
    topic: str
    description: str
    requirements: Dict[str, Any]
    previous_results: Dict[str, Any]
    target_audience: str
    writing_style: str

@dataclass
class WritingOutput:
    """Output of a writing task"""
    task_id: str
    content: PatentDraft
    writing_metrics: Dict[str, Any]
    quality_score: float
    compliance_check: Dict[str, Any]

class WriterAgent(BaseAgent):
    """Agent responsible for drafting patent applications"""
    
    def __init__(self, test_mode: bool = False):
        super().__init__(
            name="writer_agent",
            capabilities=["patent_drafting", "technical_writing", "claim_writing", "legal_compliance"],
            test_mode=test_mode
        )
        self.openai_client = None
        self.writing_templates = self._load_writing_templates()
        self.legal_requirements = self._load_legal_requirements()
        
    async def start(self):
        """Start the writer agent"""
        await super().start()
        self.openai_client = OpenAIClient()
        logger.info("Writer Agent started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute writing tasks"""
        try:
            task_type = task_data.get("type")
            
            if task_type == "patent_drafting":
                return await self._draft_patent_application(task_data)
            elif task_type == "claim_writing":
                return await self._write_patent_claims_task(task_data)
            elif task_type == "technical_description":
                return await self._write_technical_description(task_data)
            elif task_type == "legal_compliance_check":
                return await self._check_legal_compliance(task_data)
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error executing task in Writer Agent: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _draft_patent_application(self, task_data: Dict[str, Any]) -> TaskResult:
        """Draft a complete patent application"""
        try:
            topic = task_data.get("topic")
            description = task_data.get("description")
            previous_results = task_data.get("previous_results", {})
            
            # Get context information if available
            context_data = getattr(self, 'current_context', {})
            theme_definition = context_data.get("theme_definition")
            terminology = context_data.get("terminology", {})
            
            if theme_definition:
                logger.info(f"Using context theme: {theme_definition.primary_title}")
                # Use context to ensure consistency
                topic = theme_definition.primary_title
                description = f"{description} 核心概念：{theme_definition.core_concept}"
                
                # Add terminology guidance
                if terminology:
                    description += f"\n术语标准：{terminology}"
            
            if not topic or not description:
                return TaskResult(
                    success=False,
                    data={},
                    error_message="Topic and description are required for patent drafting"
                )
                
            logger.info(f"Drafting patent application for: {topic}")
            
            # Create writing task
            writing_task = WritingTask(
                task_id=f"writing_{asyncio.get_event_loop().time()}",
                topic=topic,
                description=description,
                requirements=previous_results.get("requirements", {}),
                previous_results=previous_results,
                target_audience="patent_examiners",
                writing_style="technical_legal"
            )

            # Prepare progress output directory for incremental saving
            workflow_id = task_data.get("workflow_id", "") or ""
            wid8 = (workflow_id[:8] if isinstance(workflow_id, str) and workflow_id else "noid")
            topic_str = (topic or "patent").replace(" ", "_")
            # 使用相对路径，在当前项目目录下创建output文件夹
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
            progress_dir = os.path.join(output_dir, "progress", f"{topic_str}_{wid8}")
            
            # 强制创建progress目录，添加详细日志
            logger.info(f"Creating progress directory: {progress_dir}")
            try:
                os.makedirs(progress_dir, exist_ok=True)
                logger.info(f"Successfully created progress directory: {progress_dir}")
            except Exception as e:
                logger.error(f"Failed to create progress directory: {e}")
                # 尝试创建备用目录
                backup_dir = os.path.join(output_dir, "backup_progress", f"{topic_str}_{wid8}")
                try:
                    os.makedirs(backup_dir, exist_ok=True)
                    progress_dir = backup_dir
                    logger.info(f"Using backup progress directory: {progress_dir}")
                except Exception as e2:
                    logger.error(f"Failed to create backup progress directory: {e2}")
                    progress_dir = output_dir  # 使用output目录作为最后的备用
                    logger.info(f"Using output directory as progress directory: {progress_dir}")
            
            # Generate patent draft using OpenAI GPT-5
            analysis_input = self._extract_analysis(previous_results)
            patent_draft = await self.openai_client.generate_patent_draft(
                topic, description, analysis_input
            )

            # Save initial skeleton
            try:
                self._write_progress(progress_dir, "00_title_abstract.md", "标题与摘要", f"# {getattr(patent_draft, 'title', '')}\n\n{getattr(patent_draft, 'abstract', '')}\n")
                logger.info("Successfully saved initial skeleton")
            except Exception as e:
                logger.error(f"Failed to save initial skeleton: {e}")

            # Write detailed sections
            logger.info("Starting _write_detailed_sections")
            detailed_sections = await self._write_detailed_sections(writing_task, patent_draft, progress_dir)
            logger.info(f"Completed _write_detailed_sections, got keys: {list(detailed_sections.keys())}")
            
            # Generate technical diagrams
            technical_diagrams = await self.openai_client.generate_technical_diagrams(description)
            
            # Update patent draft with detailed content
            patent_draft.detailed_description = detailed_sections.get("detailed_description", "")
            patent_draft.background = detailed_sections.get("background", getattr(patent_draft, "background", ""))
            patent_draft.summary = detailed_sections.get("summary", getattr(patent_draft, "summary", ""))
            # If claims were generated in detailed sections, set them
            if isinstance(detailed_sections.get("claims"), list) and detailed_sections.get("claims"):
                patent_draft.claims = detailed_sections.get("claims")
            patent_draft.technical_diagrams = technical_diagrams
            
            logger.info(f"Updated patent_draft.detailed_description length: {len(patent_draft.detailed_description)}")
            logger.info(f"Updated patent_draft.background length: {len(patent_draft.background)}")
            logger.info(f"Updated patent_draft.summary length: {len(patent_draft.summary)}")
            
            # Check legal compliance
            compliance_check = await self._check_patent_compliance(patent_draft)
            
            # Calculate quality score
            quality_score = await self._calculate_writing_quality(patent_draft, compliance_check)
            
            # Compile writing output
            writing_output = WritingOutput(
                task_id=writing_task.task_id,
                content=patent_draft,
                writing_metrics={
                    "word_count": len(patent_draft.detailed_description.split()),
                    "sections_completed": 6,
                    "compliance_score": compliance_check.get("overall_score", 0)
                },
                quality_score=quality_score,
                compliance_check=compliance_check
            )
            
            return TaskResult(
                success=True,
                data={
                    "patent_draft": patent_draft,
                    "writing_output": writing_output,
                    "technical_diagrams": technical_diagrams,
                    "compliance_status": "compliant" if compliance_check.get("overall_score", 0) >= 8.0 else "needs_revision"
                },
                metadata={
                    "writing_type": "complete_patent_application",
                    "completion_timestamp": asyncio.get_event_loop().time()
                }
            )
            
        except Exception as e:
            logger.error(f"Error drafting patent application: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _write_detailed_sections(self, writing_task: WritingTask, 
                                     patent_draft: PatentDraft,
                                     progress_dir: str) -> Dict[str, str]:
        """Write detailed sections of the patent application using intelligent LLM prompts"""
        try:
            detailed_sections = {}
            logger.info(f"Starting _write_detailed_sections for topic: {writing_task.topic}")
            
            # 第一步：生成专利大纲（简洁提示词）
            logger.info("Step 1: Generating patent outline")
            outline_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"设计专利大纲，包含术语定义、技术领域、背景技术、技术方案、权利要求等章节。特别要求第五章包含伪代码和Mermaid图。"""
            outline_text = await self.openai_client._generate_response(outline_prompt)
            logger.info(f"Generated outline, length: {len(outline_text)}")
            try:
                self._write_progress(progress_dir, "01_outline.md", "撰写大纲", outline_text)
                logger.info("Successfully saved outline")
            except Exception as e:
                logger.error(f"Failed to save outline: {e}")

            # 第二步：生成背景技术（简洁提示词）
            logger.info("Step 2: Generating background")
            background_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写技术背景，包含技术领域、现有技术方案、技术缺点、要解决的问题。要求具体专业，≥800字。"""
            background = await self.openai_client._generate_response(background_prompt)
            detailed_sections["background"] = background
            logger.info(f"Generated background, length: {len(background)}")
            try:
                self._write_progress(progress_dir, "02_background.md", "背景技术", background)
                logger.info("Successfully saved background")
            except Exception as e:
                logger.error(f"Failed to save background: {e}")

            # 第三步：生成发明内容总述（简洁提示词）
            logger.info("Step 3: Generating summary")
            summary_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写发明内容总述，包含核心创新点、系统架构、技术优势。要求具体专业，≥800字。"""
            summary = await self.openai_client._generate_response(summary_prompt)
            detailed_sections["summary"] = summary
            logger.info(f"Generated summary, length: {len(summary)}")
            try:
                self._write_progress(progress_dir, "03_summary.md", "发明内容总述", summary)
                logger.info("Successfully saved summary")
            except Exception as e:
                logger.error(f"Failed to save summary: {e}")

            # 第四步：生成第五章技术方案（重点，分步骤生成）
            logger.info("Step 4: Generating Chapter 5 technical solution")
            
            # 4.1 生成5.0总体介绍
            logger.info("Step 4.1: Generating 5.0 overview")
            chapter5_0_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写5.0技术方案总体介绍，包含：
1. 技术方案核心思想概述
2. 整体技术架构图（Mermaid格式）
3. 技术方案创新点总结
4. 技术方案优势分析
要求≥1000字，必须包含Mermaid架构图。"""
            chapter5_0 = await self.openai_client._generate_response(chapter5_0_prompt)
            logger.info(f"Generated chapter5_0, length: {len(chapter5_0)}")

            # 4.2 生成5.1系统架构设计
            logger.info("Step 4.2: Generating 5.1 system architecture")
            chapter5_1_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写5.1系统架构设计，包含：
1. 系统整体架构图（Mermaid格式）
2. 各模块功能详细描述
3. 子功能模块架构图（Mermaid格式）
4. 核心算法伪代码（≥50行Python代码）
要求≥1500字，必须包含Mermaid图和伪代码。"""
            chapter5_1 = await self.openai_client._generate_response(chapter5_1_prompt)
            logger.info(f"Generated chapter5_1, length: {len(chapter5_1)}")

            # 4.3 生成5.2核心算法实现
            logger.info("Step 4.3: Generating 5.2 core algorithm")
            chapter5_2_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写5.2核心算法实现，包含：
1. 核心算法流程图（Mermaid格式）
2. 算法伪代码实现（≥50行Python代码）
3. 算法复杂度分析
4. 子算法模块图（Mermaid格式）
要求≥1500字，必须包含Mermaid图和伪代码。"""
            chapter5_2 = await self.openai_client._generate_response(chapter5_2_prompt)
            logger.info(f"Generated chapter5_2, length: {len(chapter5_2)}")

            # 4.4 生成5.3数据流程设计
            logger.info("Step 4.4: Generating 5.3 data flow")
            chapter5_3_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写5.3数据流程设计，包含：
1. 数据流程图（Mermaid格式）
2. 数据结构定义
3. 数据处理伪代码（≥50行Python代码）
4. 数据处理子模块图（Mermaid格式）
要求≥1500字，必须包含Mermaid图和伪代码。"""
            chapter5_3 = await self.openai_client._generate_response(chapter5_3_prompt)
            logger.info(f"Generated chapter5_3, length: {len(chapter5_3)}")

            # 4.5 生成5.4接口规范定义
            logger.info("Step 4.5: Generating 5.4 interface specification")
            chapter5_4_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写5.4接口规范定义，包含：
1. 接口架构图（Mermaid格式）
2. API接口规范
3. 接口实现伪代码（≥50行Python代码）
4. 接口调用流程图（Mermaid格式）
要求≥1500字，必须包含Mermaid图和伪代码。"""
            chapter5_4 = await self.openai_client._generate_response(chapter5_4_prompt)
            logger.info(f"Generated chapter5_4, length: {len(chapter5_4)}")

            # 4.6 整合第五章内容
            logger.info("Step 4.6: Integrating Chapter 5 content")
            chapter5_content = f"""## 第五章 技术方案详细阐述

### 5.0 技术方案总体介绍

{chapter5_0}

### 5.1 系统架构设计

{chapter5_1}

### 5.2 核心算法实现

{chapter5_2}

### 5.3 数据流程设计

{chapter5_3}

### 5.4 接口规范定义

{chapter5_4}"""

            detailed_sections["detailed_description"] = chapter5_content
            logger.info(f"Set detailed_description, length: {len(chapter5_content)}")
            try:
                self._write_progress(progress_dir, "04_chapter5.md", "第五章技术方案详细阐述", chapter5_content)
                logger.info("Successfully saved chapter5")
            except Exception as e:
                logger.error(f"Failed to save chapter5: {e}")

            # 第五步：生成权利要求书（简洁提示词）
            logger.info("Step 5: Generating claims")
            claims_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写权利要求书，包含1项独立权利要求和3-4项从属权利要求。要求具体清晰，符合专利法要求。"""
            claims_text = await self.openai_client._generate_response(claims_prompt)
            detailed_sections["claims"] = claims_text.splitlines()
            logger.info(f"Generated claims, lines: {len(claims_text.splitlines())}")
            try:
                self._write_progress(progress_dir, "05_claims.md", "权利要求书", claims_text)
                logger.info("Successfully saved claims")
            except Exception as e:
                logger.error(f"Failed to save claims: {e}")

            # 第六步：生成附图说明（简洁提示词）
            logger.info("Step 6: Generating drawings description")
            drawings_prompt = f"""你是专利撰写专家。为"{writing_task.topic}"撰写附图说明，包含系统架构图、数据流程图、核心算法图的Mermaid代码和详细说明。要求≥1000字。"""
            drawings_description = await self.openai_client._generate_response(drawings_prompt)
            detailed_sections["drawings_description"] = drawings_description
            logger.info(f"Generated drawings_description, length: {len(drawings_description)}")
            try:
                self._write_progress(progress_dir, "06_drawings.md", "附图说明", drawings_description)
                logger.info("Successfully saved drawings")
            except Exception as e:
                logger.error(f"Failed to save drawings: {e}")

            # 第七步：使用LLM进行智能质量检查和内容增强
            logger.info("Step 7: Performing content enhancement")
            enhancement_prompt = f"""你是专利质量专家。检查以下专利内容，如果发现内容简单或缺少技术细节，请进行智能增强：

主题：{writing_task.topic}

背景技术：{background}
发明内容总述：{summary}
第五章技术方案：{chapter5_content}
权利要求书：{claims_text}
附图说明：{drawings_description}

请进行智能分析和增强：
1. 如果内容过于简单，请补充技术细节
2. 如果缺少伪代码，请添加具体的算法实现
3. 如果缺少Mermaid图，请添加技术架构图
4. 如果技术描述不够深入，请深化技术内容

请直接提供增强后的完整内容。"""
            
            enhanced_content = await self.openai_client._generate_response(enhancement_prompt)
            logger.info(f"Generated enhanced_content, length: {len(enhanced_content)}")
            try:
                self._write_progress(progress_dir, "07_enhanced_content.md", "智能增强内容", enhanced_content)
                logger.info("Successfully saved enhanced content")
            except Exception as e:
                logger.error(f"Failed to save enhanced content: {e}")

            # 如果增强内容包含完整章节，则更新
            if "## 第五章" in enhanced_content and "### 5.1" in enhanced_content:
                detailed_sections["detailed_description"] = enhanced_content
                logger.info("Updated detailed_description with enhanced content")
            elif "背景技术" in enhanced_content and len(enhanced_content) > len(background):
                detailed_sections["background"] = enhanced_content
                logger.info("Updated background with enhanced content")

            logger.info(f"Final detailed_sections keys: {list(detailed_sections.keys())}")
            return detailed_sections
            
        except Exception as e:
            logger.error(f"Error writing detailed sections: {e}")
            raise
            
    async def _write_background_section(self, topic: str, description: str, 
                                      previous_results: Dict[str, Any]) -> str:
        """Write the background section"""
        try:
            # Use Google A2A to write background section
            prompt = f"""
            Write a comprehensive background section for a patent application, aligning with CN disclosure template:
            
            Topic: {topic}
            Description: {description}
            
            Previous Analysis: {previous_results.get('analysis', {})}
            Prior Art (if any): {previous_results.get('stage_1', {})}
            
            Include, in this order:
            A. 技术领域 (Technical Field) — concise statement of the domain
            B. 现有技术的技术方案 (Nearest Prior Art) — how it is implemented and workflow/components
            C. 现有技术的缺点及待解决的技术问题 — articulate technical drawbacks (not business/admin) and the objective problems
            D. 本申请的必要性/改进动机
            
            Style:
            - Formal patent language
            - 250-350 words
            - Be specific and implementation-oriented
            """
            
            response = await self.openai_client._generate_response(prompt)
            
            # Parse and format response
            background_section = f"""
            BACKGROUND OF THE INVENTION
            
            Field of the Invention
            
            The present invention relates to {topic.lower()}, and more particularly to {description.lower()}.
            
            {response}
            
            Description of the Prior Art
            
            Current solutions in the field of {topic.lower()} suffer from several limitations including [limitations identified from analysis]. There exists a need for improved methods and systems that address these limitations.
            """
            
            return background_section
            
        except Exception as e:
            logger.error(f"Error writing background section: {e}")
            return f"Background section for {topic} - [Error occurred during generation]"
            
    async def _write_summary_section(self, topic: str, abstract: str, 
                                   previous_results: Dict[str, Any]) -> str:
        """Write the summary section"""
        try:
            # Use Google A2A to write summary section
            prompt = f"""
            Write a summary section (Summary of Invention) aligned with CN disclosure handbook:
            
            Topic: {topic}
            Abstract: {abstract}
            
            Analysis Results: {previous_results.get('analysis', {})}
            
            Include:
            - 技术方案要点（Who/What/When/Where/How）
            - 与最近似现有技术的区别特征
            - 技术效果/有益效果（技术性、可量化）
            
            Constraints:
            - Formal patent language
            - 180-250 words
            - Avoid marketing claims; stay technical
            """
            
            response = await self.openai_client._generate_response(prompt)
            
            # Parse and format response
            summary_section = f"""
            SUMMARY OF THE INVENTION
            
            {response}
            
            The present invention provides significant advantages over existing solutions, including improved efficiency, enhanced performance, and novel technical approaches to {topic.lower()}.
            """
            
            return summary_section
            
        except Exception as e:
            logger.error(f"Error writing summary section: {e}")
            return f"Summary section for {topic} - [Error occurred during generation]"
            
    async def _write_detailed_description(self, topic: str, description: str, 
                                        claims: List[str], previous_results: Dict[str, Any]) -> str:
        """Write the detailed description section"""
        try:
            # Use Google A2A to write detailed description
            prompt = f"""
            Write a detailed description aligned with CN disclosure template Section 5:
            
            Topic: {topic}
            Description: {description}
            Claims: {claims}
            Previous Results: {previous_results}
            
            Structure and include:
            1. 方法/业务流程类：提供流程图/信令交互图文字版；按步骤顺序描述，每步给出Who/What/When/Where/How；
            2. 系统/设备类：提供结构图文字版；逐一说明各组成部分功能、信号处理方式、相互连接关系；
            3. 改进点：逐项展开技术方案一/二/三的不同实现；
            4. 可选实施例与变体；
            5. 技术效果与实现条件；
            
            Constraints:
            - 700-1200 words
            - 以实施方式描述为主，避免泛化描述
            - 保持术语一致
            """
            
            response = await self.openai_client._generate_response(prompt)
            
            # Parse and format response
            detailed_description = f"""
            DETAILED DESCRIPTION OF THE INVENTION
            
            {response}
            
            The invention will now be described in detail with reference to the accompanying drawings and preferred embodiments. It should be understood that the invention is not limited to the specific embodiments described herein.
            """
            
            return detailed_description
            
        except Exception as e:
            logger.error(f"Error writing detailed description: {e}")
            return f"Detailed description for {topic} - [Error occurred during generation]"
            
    async def _write_patent_claims_section(self, topic: str, description: str, 
                                 previous_results: Dict[str, Any]) -> List[str]:
        """Write patent claims"""
        try:
            # Use Google A2A to write claims
            prompt = f"""
            Draft 1 independent claim and 3-6 dependent claims in CN style:
            
            Topic: {topic}
            Description: {description}
            Analysis: {previous_results.get('analysis', {})}
            
            Requirements:
            - 独立权利要求：限定核心技术特征，包含前序部分+特征部分（采用“其特征在于/包括”结构），避免结果性限定；
            - 从属权利要求：逐项增加技术特征、参数范围、具体部件关系；
            - 术语统一、避免功能性泛化；
            - 每项以句号结束。
            
            Output numbered list.
            """
            
            response = await self.openai_client._generate_response(prompt)
            
            # Parse response to extract claims
            # This is a simplified approach
            claims = [
                f"1. A method for {topic.lower()}, comprising: {description.lower()}.",
                f"2. The method of claim 1, further comprising: additional step.",
                f"3. The method of claim 1, wherein: specific limitation.",
                f"4. A system for {topic.lower()}, comprising: system components.",
                f"5. A computer-readable medium storing instructions for {topic.lower()}."
            ]
            
            return claims
            
        except Exception as e:
            logger.error(f"Error writing patent claims: {e}")
            return [f"Claim 1: A method for {topic.lower()}."]
            
    async def _write_drawings_description(self, topic: str, description: str) -> str:
        """Write the drawings description section"""
        try:
            # Use Google A2A to write drawings description
            prompt = f"""
            Write a drawings description section for a patent application:
            
            Topic: {topic}
            Description: {description}
            
            Include descriptions for:
            1. Figure 1: Overall system architecture
            2. Figure 2: Detailed component diagram
            3. Figure 3: Process flow diagram
            4. Figure 4: Implementation example
            5. Figure 5: Alternative embodiments
            
            Write in formal patent language, 200-300 words.
            """
            
            response = await self.openai_client._generate_response(prompt)
            
            # Parse and format response
            drawings_description = f"""
            BRIEF DESCRIPTION OF THE DRAWINGS
            
            {response}
            
            The drawings illustrate preferred embodiments of the invention and are not intended to limit the scope of the invention.
            """
            
            return drawings_description
            
        except Exception as e:
            logger.error(f"Error writing drawings description: {e}")
            return f"Drawings description for {topic} - [Error occurred during generation]"
            
    async def _check_patent_compliance(self, patent_draft: PatentDraft) -> Dict[str, Any]:
        """Check legal compliance of the patent draft"""
        try:
            compliance_check = {
                "overall_score": 8.5,
                "sections": {},
                "issues": [],
                "recommendations": []
            }
            
            # Check title compliance
            title_check = await self._check_title_compliance(patent_draft.title)
            compliance_check["sections"]["title"] = title_check
            
            # Check abstract compliance
            abstract_check = await self._check_abstract_compliance(patent_draft.abstract)
            compliance_check["sections"]["abstract"] = abstract_check
            
            # Check claims compliance
            claims_check = await self._check_claims_compliance(patent_draft.claims)
            compliance_check["sections"]["claims"] = claims_check
            
            # Check description compliance
            description_check = await self._check_description_compliance(patent_draft.detailed_description)
            compliance_check["sections"]["description"] = description_check
            
            # Calculate overall compliance score
            section_scores = [check.get("score", 0) for check in compliance_check["sections"].values()]
            if section_scores:
                compliance_check["overall_score"] = sum(section_scores) / len(section_scores)
                
            # Generate recommendations
            compliance_check["recommendations"] = await self._generate_compliance_recommendations(compliance_check)
            
            return compliance_check
            
        except Exception as e:
            logger.error(f"Error checking patent compliance: {e}")
            return {"overall_score": 0, "error": str(e)}
            
    async def _check_title_compliance(self, title: str) -> Dict[str, Any]:
        """Check title compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            if len(title) < 10:
                score -= 2.0
                issues.append("Title too short")
                recommendations.append("Expand title to be more descriptive")
                
            if len(title) > 100:
                score -= 1.0
                issues.append("Title too long")
                recommendations.append("Shorten title while maintaining clarity")
                
            if not title[0].isupper():
                score -= 0.5
                issues.append("Title should start with capital letter")
                recommendations.append("Capitalize first letter of title")
                
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking title compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _check_abstract_compliance(self, abstract: str) -> Dict[str, Any]:
        """Check abstract compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            word_count = len(abstract.split())
            if word_count < 50:
                score -= 2.0
                issues.append("Abstract too short")
                recommendations.append("Expand abstract to provide comprehensive overview")
            elif word_count > 150:
                score -= 1.0
                issues.append("Abstract too long")
                recommendations.append("Condense abstract to meet word limit")
                
            if not abstract.endswith("."):
                score -= 0.5
                issues.append("Abstract should end with period")
                recommendations.append("Add period at end of abstract")
                
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking abstract compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _check_claims_compliance(self, claims: List[str]) -> Dict[str, Any]:
        """Check claims compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            if len(claims) < 3:
                score -= 2.0
                issues.append("Insufficient number of claims")
                recommendations.append("Add more claims for comprehensive protection")
                
            if len(claims) > 20:
                score -= 1.0
                issues.append("Too many claims")
                recommendations.append("Consolidate or remove redundant claims")
                
            # Check claim structure
            for i, claim in enumerate(claims):
                if not claim.strip().endswith("."):
                    score -= 0.5
                    issues.append(f"Claim {i+1} should end with period")
                    recommendations.append(f"Add period at end of claim {i+1}")
                    
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking claims compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _check_description_compliance(self, description: str) -> Dict[str, Any]:
        """Check description compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            word_count = len(description.split())
            if word_count < 500:
                score -= 2.0
                issues.append("Description too short")
                recommendations.append("Expand description with more technical details")
            elif word_count > 5000:
                score -= 1.0
                issues.append("Description too long")
                recommendations.append("Condense description to essential information")
                
            if not description:
                score -= 5.0
                issues.append("Missing description")
                recommendations.append("Add detailed description section")
                
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking description compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _generate_compliance_recommendations(self, compliance_check: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations"""
        try:
            recommendations = []
            
            overall_score = compliance_check.get("overall_score", 0)
            
            if overall_score < 7.0:
                recommendations.append("Major revisions required to meet compliance standards")
            elif overall_score < 8.5:
                recommendations.append("Minor revisions recommended for optimal compliance")
            else:
                recommendations.append("Patent draft meets compliance requirements")
                
            # Add specific recommendations from sections
            for section_name, section_check in compliance_check.get("sections", {}).items():
                section_score = section_check.get("score", 0)
                if section_score < 8.0:
                    recommendations.extend(section_check.get("recommendations", []))
                    
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating compliance recommendations: {e}")
            return ["Review patent draft for compliance issues"]
            
    async def _calculate_writing_quality(self, patent_draft: PatentDraft, 
                                       compliance_check: Dict[str, Any]) -> float:
        """Calculate overall writing quality score"""
        try:
            # Base quality score
            base_score = 8.0
            
            # Adjust based on compliance
            compliance_score = compliance_check.get("overall_score", 0)
            compliance_factor = compliance_score / 10.0
            
            # Adjust based on content completeness
            content_score = 0
            if patent_draft.title:
                content_score += 1
            if patent_draft.abstract:
                content_score += 1
            if patent_draft.claims:
                content_score += 2
            if patent_draft.detailed_description:
                content_score += 2
            if patent_draft.technical_diagrams:
                content_score += 1
                
            content_factor = content_score / 7.0
            
            # Calculate final quality score
            quality_score = base_score * 0.4 + compliance_factor * 10 * 0.4 + content_factor * 10 * 0.2
            
            return max(1.0, min(10.0, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating writing quality: {e}")
            return 7.0  # Default fallback score
            
    async def _write_patent_claims_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Write patent claims specifically"""
        try:
            topic = task_data.get("topic")
            description = task_data.get("description")
            previous_results = task_data.get("previous_results", {})
            claims = await self._write_patent_claims_section(topic, description, previous_results)
            return TaskResult(success=True, data={"claims": claims})
        except Exception as e:
            logger.error(f"Error in claim writing task: {e}")
            return TaskResult(success=False, data={}, error_message=str(e))
        
    async def _write_technical_description(self, task_data: Dict[str, Any]) -> TaskResult:
        """Write technical description"""
        # Implementation for technical description writing
        pass
        
    async def _check_legal_compliance(self, task_data: Dict[str, Any]) -> TaskResult:
        """Check legal compliance"""
        # Implementation for legal compliance checking
        pass
        
    def _load_writing_templates(self) -> Dict[str, Any]:
        """Load writing templates for different patent types"""
        return {
            "utility_patent": {
                "sections": ["Title", "Abstract", "Background", "Summary", "Description", "Claims", "Drawings"],
                "word_limits": {"abstract": 150, "description": "unlimited"}
            },
            "design_patent": {
                "sections": ["Title", "Description", "Claims", "Drawings"],
                "word_limits": {"description": 100}
            },
            "provisional_patent": {
                "sections": ["Title", "Description", "Drawings"],
                "word_limits": {"description": "unlimited"}
            }
        }
        
    def _load_legal_requirements(self) -> Dict[str, Any]:
        """Load legal requirements for patent applications"""
        return {
            "uspto": {
                "title_max_length": 500,
                "abstract_max_words": 150,
                "claims_max_count": 20,
                "drawings_required": True
            },
            "epo": {
                "title_max_length": 400,
                "abstract_max_words": 150,
                "claims_max_count": 15,
                "drawings_required": True
            },
            "wipo": {
                "title_max_length": 500,
                "abstract_max_words": 150,
                "claims_max_count": 20,
                "drawings_required": True
            }
        }

    def _extract_analysis(self, previous_results: Dict[str, Any]):
        """Best-effort extraction of a PatentAnalysis object from accumulated previous_results.
        Accepts either a dataclass instance or a dict; falls back to sane defaults if missing."""
        from ..google_a2a_client import PatentAnalysis
        def _coerce(obj: Any) -> PatentAnalysis:
            if isinstance(obj, PatentAnalysis):
                return obj
            if isinstance(obj, dict):
                return PatentAnalysis(
                    novelty_score=obj.get("novelty_score", 8.5),
                    inventive_step_score=obj.get("inventive_step_score", 7.8),
                    industrial_applicability=obj.get("industrial_applicability", True),
                    prior_art_analysis=obj.get("prior_art_analysis", []),
                    claim_analysis=obj.get("claim_analysis", {}),
                    technical_merit=obj.get("technical_merit", {}),
                    commercial_potential=obj.get("commercial_potential", "Medium to High"),
                    patentability_assessment=obj.get("patentability_assessment", "Strong"),
                    recommendations=obj.get("recommendations", ["Add more technical details"]) 
                )
            # Unknown type -> defaults
            return PatentAnalysis(
                novelty_score=8.5,
                inventive_step_score=7.8,
                industrial_applicability=True,
                prior_art_analysis=[],
                claim_analysis={},
                technical_merit={},
                commercial_potential="Medium to High",
                patentability_assessment="Strong",
                recommendations=["Improve claim specificity"]
            )
        candidates: List[Any] = []
        try:
            candidates.append(previous_results.get("analysis"))
        except Exception:
            pass
        try:
            candidates.append(previous_results.get("stage_0", {}).get("result", {}).get("analysis"))
        except Exception:
            pass
        # Scan all stages for an analysis field if not found
        if not any(candidates):
            for key, val in (previous_results or {}).items():
                try:
                    if isinstance(val, dict) and "result" in val and isinstance(val["result"], dict) and "analysis" in val["result"]:
                        candidates.append(val["result"]["analysis"])
                except Exception:
                    continue
        for cand in candidates:
            if cand:
                return _coerce(cand)
        return _coerce({})

    def _write_progress(self, progress_dir: str, filename: str, section_title: str, body: str) -> None:
        """Append incremental content to a progress file and write a section file."""
        try:
            os.makedirs(progress_dir, exist_ok=True)
        except Exception:
            pass
        # Write individual section file
        path = os.path.join(progress_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {section_title}\n\n{body.strip()}\n")
        # Append to combined progress.md
        progress_md = os.path.join(progress_dir, "progress.md")
        with open(progress_md, "a", encoding="utf-8") as f:
            f.write(f"\n\n## {section_title}\n\n{body.strip()}\n")
        self.agent_logger.info(f"WROTE_PROGRESS dir={progress_dir} file={filename} len={len(body or '')}")
        
    async def _execute_test_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a test task with mock data"""
        try:
            task_type = task_data.get("type")
            topic = task_data.get("topic", "测试专利主题")
            description = task_data.get("description", "测试专利描述")
            
            if task_type == "patent_drafting":
                # Create mock patent draft
                from ..google_a2a_client import PatentDraft
                
                mock_draft = PatentDraft(
                    title=f"{topic} - 专利申请书",
                    abstract=f"本发明涉及{topic}的技术领域，提供了一种创新的解决方案。{description}",
                    background=f"现有技术中，大语言模型在调用具有大量参数的工具时存在准确性和效率问题。本发明提供了一种创新的解决方案。",
                    summary=f"本发明的目的是提供一种能够智能处理多参数工具调用的系统，通过分层推理和自适应机制提高调用准确性。",
                    detailed_description=f"""
# 技术领域

本发明涉及{topic}的技术领域，具体涉及一种基于智能分层推理的多参数工具自适应调用系统。

# 发明内容

本发明的目的是提供一种能够智能处理多参数工具调用的系统，通过分层推理和自适应机制提高调用准确性。

# 具体实施方式

## 实施例1

本实施例提供了一种基于智能分层推理的多参数工具自适应调用系统，包括：

1. 参数分层模块：将参数按重要性和使用频率进行分类；
2. 智能推理模块：基于上下文自动推断参数值；
3. 自适应调用模块：根据工具特性动态调整调用策略。

## 实施例2

本实施例进一步优化了参数验证机制，包括：

1. 参数有效性检查；
2. 参数一致性验证；
3. 调用结果反馈优化。
                    """,
                    claims=[
                        "1. 一种基于智能分层推理的多参数工具自适应调用系统，其特征在于，包括参数分层模块、智能推理模块和自适应调用模块。",
                        "2. 根据权利要求1所述的系统，其特征在于，所述参数分层模块将参数按重要性和使用频率进行分类。",
                        "3. 根据权利要求1所述的系统，其特征在于，所述智能推理模块基于上下文自动推断参数值。"
                    ],
                    drawings_description="图1为本发明的系统架构图；图2为本发明的参数处理流程图。",
                    technical_diagrams=["图1：系统架构图", "图2：参数处理流程图"]
                )
                
                return TaskResult(
                    success=True,
                    data={
                        "patent_draft": mock_draft,
                        "writing_metrics": {
                            "word_count": 1500,
                            "claim_count": 3,
                            "compliance_score": 0.85
                        },
                        "quality_score": 0.82,
                        "compliance_check": {
                            "title_length": "OK",
                            "abstract_length": "OK",
                            "claims_count": "OK",
                            "drawings_required": "OK"
                        }
                    }
                )
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error in test task execution: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )