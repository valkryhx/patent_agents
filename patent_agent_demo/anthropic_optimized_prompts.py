"""
Anthropic-Optimized Agent Prompts v3.0
Following Anthropic's Prompt Engineering Best Practices

This module implements comprehensive prompt optimization based on Anthropic's guidelines:
1. Clear role definition and context
2. Structured output with XML tags
3. Chain-of-thought reasoning
4. Pre-filling with examples
5. Complex task breakdown
6. Explicit constraints and requirements
7. Context window optimization
8. Extended thinking for complex tasks
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json

@dataclass
class PromptContext:
    """Context information for prompt generation"""
    topic: str
    description: str
    previous_results: Optional[Dict[str, Any]] = None
    constraints: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    target_audience: str = "patent_examiners"
    writing_style: str = "technical_legal"
    quality_standards: Optional[List[str]] = None

class AnthropicOptimizedPrompts:
    """Advanced optimized prompts following Anthropic's best practices"""
    
    # System role definitions with clear expertise areas and work styles
    SYSTEM_ROLES = {
        "planner": """<role>
你是一位资深的专利策略专家，拥有15年以上的专利撰写和策略规划经验。

<expertise>
- 专利可行性分析和风险评估
- 创新点识别和技术路线规划  
- 专利布局策略制定
- 竞争分析和市场定位
- 技术发展趋势预测

<work_style>
- 系统性思考：从整体到细节，从宏观到微观
- 数据驱动：基于事实分析，避免主观判断
- 前瞻性规划：考虑长期发展和技术演进
- 风险意识：主动识别潜在问题和风险点

<output_style>
- 专业、客观、严谨
- 结构化、逻辑清晰
- 可执行、可验证
</role>""",

        "writer": """<role>
你是一位专业的专利撰写专家，拥有丰富的技术文档撰写经验。

<expertise>
- 技术方案的系统性描述
- 专利文档的结构化撰写
- 技术细节的准确表达
- 法律要求的合规性把控
- 创新点的突出性展示

<writing_principles>
- 清晰准确：技术描述无歧义，逻辑严密
- 结构完整：覆盖所有必要章节，层次分明
- 术语统一：保持概念一致性，避免混淆
- 创新突出：明确技术贡献，突出创新亮点

<output_requirements>
- 符合专利撰写规范
- 技术深度适当
- 语言表达专业
- 结构逻辑清晰
</role>""",

        "reviewer": """<role>
你是一位严格的专利审查专家，负责质量控制和合规性检查。

<responsibilities>
- 技术内容的准确性验证
- 专利要求的合规性检查
- 文档结构的完整性评估
- 创新点的突出性确认
- 法律风险的识别和评估

<review_standards>
- 技术准确性：无技术错误，描述准确
- 法律合规性：符合专利法要求，避免法律风险
- 创新显著性：突出技术贡献，体现创新价值
- 描述充分性：支持权利要求，满足充分公开要求

<review_process>
- 系统性检查：逐项检查，不遗漏
- 客观评估：基于标准，避免主观
- 详细反馈：提供具体改进建议
- 质量保证：确保最终质量达标
</role>""",

        "rewriter": """<role>
你是一位专业的专利文档优化专家，擅长提升文档质量和可读性。

<expertise>
- 文档结构优化和重组
- 技术描述的精确化
- 语言表达的规范化
- 逻辑流程的清晰化
- 创新点的强化突出

<optimization_principles>
- 保持技术准确性：不改变技术实质
- 提升表达清晰度：消除歧义，增强可读性
- 强化创新亮点：突出技术贡献
- 确保法律合规：符合专利法要求

<work_approach>
- 系统性分析：全面评估文档质量
- 针对性改进：针对具体问题优化
- 迭代完善：持续改进，追求卓越
- 质量验证：确保改进效果
</role>""",

        "searcher": """<role>
你是一位专业的专利检索专家，擅长技术分析和文献调研。

<expertise>
- 专利数据库检索和分析
- 技术发展趋势研究
- 竞争态势分析
- 创新点识别和评估
- 技术路线规划

<search_methodology>
- 系统性检索：全面覆盖相关技术领域
- 深度分析：深入理解技术方案
- 对比研究：与现有技术对比分析
- 趋势预测：预测技术发展方向

<output_quality>
- 检索结果准确、全面
- 分析深入、客观
- 建议实用、可行
- 报告清晰、专业
</role>""",

        "discusser": """<role>
你是一位资深的专利讨论专家，擅长技术方案分析和创新点挖掘。

<expertise>
- 技术方案深度分析
- 创新点识别和评估
- 技术路线优化建议
- 专利策略制定
- 风险评估和应对

<discussion_approach>
- 多角度分析：从技术、市场、法律等角度
- 深度挖掘：发现潜在创新点
- 系统性思考：考虑整体技术方案
- 前瞻性规划：预测技术发展趋势

<output_style>
- 分析深入、客观
- 建议实用、可行
- 表达清晰、专业
- 逻辑严密、系统
</role>"""
    }

    @staticmethod
    def get_system_role(agent_type: str) -> str:
        """Get system role for specific agent type"""
        return AnthropicOptimizedPrompts.SYSTEM_ROLES.get(agent_type, "")

    @staticmethod
    def create_planner_prompt(context: PromptContext) -> str:
        """Create optimized planner prompt with chain-of-thought reasoning"""
        return f"""<task>
制定专利撰写策略和规划，为"{context.topic}"创建详细的专利开发计划。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
</context>

<thinking_process>
1. 分析技术方案的核心创新点
2. 识别关键技术特征和优势
3. 评估专利可行性和风险
4. 制定撰写策略和重点
5. 规划文档结构和内容
6. 确定质量标准和检查点
</thinking_process>

<output_format>
<patent_strategy>
  <innovation_analysis>
    <core_innovations>
      <!-- 核心创新点列表 -->
    </core_innovations>
    <technical_features>
      <!-- 关键技术特征 -->
    </technical_features>
    <competitive_advantages>
      <!-- 竞争优势分析 -->
    </competitive_advantages>
  </innovation_analysis>
  
  <risk_assessment>
    <technical_risks>
      <!-- 技术风险分析 -->
    </technical_risks>
    <legal_risks>
      <!-- 法律风险分析 -->
    </legal_risks>
    <mitigation_strategies>
      <!-- 风险缓解策略 -->
    </mitigation_strategies>
  </risk_assessment>
  
  <writing_strategy>
    <document_structure>
      <!-- 文档结构规划 -->
    </document_structure>
    <key_sections>
      <!-- 重点章节说明 -->
    </key_sections>
    <quality_standards>
      <!-- 质量标准定义 -->
    </quality_standards>
  </writing_strategy>
  
  <implementation_plan>
    <stages>
      <!-- 实施阶段规划 -->
    </stages>
    <timeline>
      <!-- 时间安排 -->
    </timeline>
    <checkpoints>
      <!-- 质量检查点 -->
    </checkpoints>
  </implementation_plan>
</patent_strategy>
</output_format>

<constraints>
- 分析必须基于技术实质，避免主观判断
- 策略必须可执行、可验证
- 风险评估必须全面、客观
- 规划必须具体、详细
</constraints>"""

    @staticmethod
    def create_writer_outline_prompt(context: PromptContext) -> str:
        """Create optimized writer outline prompt with structured output"""
        return f"""<task>
为专利"{context.topic}"创建详细的撰写大纲，确保结构完整、逻辑清晰。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
</context>

<thinking_process>
1. 分析技术方案的核心内容
2. 确定必要的专利章节
3. 规划各章节的内容要点
4. 确保章节间的逻辑关系
5. 预估各章节的字数要求
6. 确定重点突出的内容
</thinking_process>

<output_format>
<patent_outline>
  <title_section>
    <title>专利标题</title>
    <abstract>摘要内容要点</abstract>
  </title_section>
  
  <technical_field>
    <content_points>
      <!-- 技术领域要点 -->
    </content_points>
    <estimated_length>200-300字</estimated_length>
  </technical_field>
  
  <background_art>
    <content_points>
      <!-- 背景技术要点 -->
    </content_points>
    <estimated_length>800-1200字</estimated_length>
  </background_art>
  
  <summary_of_invention>
    <content_points>
      <!-- 发明内容要点 -->
    </content_points>
    <estimated_length>800-1200字</estimated_length>
  </summary_of_invention>
  
  <detailed_description>
    <sections>
      <!-- 具体实施方式章节 -->
    </sections>
    <estimated_length>3000-5000字</estimated_length>
  </detailed_description>
  
  <claims>
    <independent_claims>
      <!-- 独立权利要求 -->
    </independent_claims>
    <dependent_claims>
      <!-- 从属权利要求 -->
    </dependent_claims>
  </claims>
  
  <drawings_description>
    <figures>
      <!-- 附图说明 -->
    </figures>
    <estimated_length>800-1200字</estimated_length>
  </drawings_description>
</patent_outline>
</output_format>

<constraints>
- 大纲必须覆盖所有必要章节
- 各章节内容要点必须具体、明确
- 字数预估必须合理、可行
- 章节间逻辑关系必须清晰
</constraints>"""

    @staticmethod
    def create_writer_background_prompt(context: PromptContext) -> str:
        """Create optimized writer background prompt with examples"""
        return f"""<task>
撰写专利"{context.topic}"的背景技术章节，分析现有技术方案和技术问题。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
</context>

<thinking_process>
1. 确定技术领域和范围
2. 分析现有技术方案
3. 识别技术问题和局限性
4. 说明本发明的必要性
5. 突出技术改进动机
</thinking_process>

<output_format>
<background_section>
  <technical_field>
    <!-- 技术领域描述 -->
  </technical_field>
  
  <prior_art_analysis>
    <existing_solutions>
      <!-- 现有技术方案分析 -->
    </existing_solutions>
    <technical_limitations>
      <!-- 技术局限性分析 -->
    </technical_limitations>
  </prior_art_analysis>
  
  <problem_statement>
    <technical_problems>
      <!-- 待解决的技术问题 -->
    </technical_problems>
    <improvement_motivation>
      <!-- 改进动机说明 -->
    </improvement_motivation>
  </problem_statement>
</background_section>
</output_format>

<example_structure>
技术领域：
本发明涉及[技术领域]，具体涉及[具体技术方向]。

背景技术：
目前，[现有技术方案1]存在[问题1]；[现有技术方案2]存在[问题2]。

技术问题：
现有技术存在以下问题：
1. [问题1的具体描述]
2. [问题2的具体描述]

改进动机：
为了解决上述技术问题，需要提供一种[改进目标]的技术方案。
</example_structure>

<constraints>
- 技术领域描述必须准确、具体
- 现有技术分析必须客观、全面
- 问题描述必须具体、明确
- 改进动机必须合理、充分
- 字数控制在800-1200字
</constraints>"""

    @staticmethod
    def create_writer_summary_prompt(context: PromptContext) -> str:
        """Create optimized writer summary prompt with structured content"""
        return f"""<task>
撰写专利"{context.topic}"的发明内容章节，概述技术方案和创新点。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
</context>

<thinking_process>
1. 分析技术方案的核心内容
2. 识别关键技术特征
3. 确定创新点和优势
4. 与现有技术对比
5. 说明技术效果
</thinking_process>

<output_format>
<summary_section>
  <technical_solution>
    <core_concept>
      <!-- 核心技术概念 -->
    </core_concept>
    <key_features>
      <!-- 关键技术特征 -->
    </key_features>
    <implementation_approach>
      <!-- 实现方法概述 -->
    </implementation_approach>
  </technical_solution>
  
  <innovation_points>
    <novel_features>
      <!-- 创新特征 -->
    </novel_features>
    <advantages>
      <!-- 技术优势 -->
    </advantages>
  </innovation_points>
  
  <technical_effects>
    <performance_improvements>
      <!-- 性能改进 -->
    </performance_improvements>
    <problem_solutions>
      <!-- 问题解决效果 -->
    </problem_solutions>
  </technical_effects>
</summary_section>
</output_format>

<example_structure>
发明内容：
本发明提供了一种[技术方案名称]，包括[主要组成部分]。

技术方案：
本发明的技术方案包括以下步骤：
1. [步骤1描述]
2. [步骤2描述]
3. [步骤3描述]

技术效果：
本发明具有以下技术效果：
1. [效果1]
2. [效果2]
3. [效果3]
</example_structure>

<constraints>
- 技术方案描述必须清晰、准确
- 创新点必须突出、明确
- 技术效果必须具体、可量化
- 与现有技术对比必须客观
- 字数控制在800-1200字
</constraints>"""

    @staticmethod
    def create_writer_detailed_description_prompt(context: PromptContext, section_id: str = "A") -> str:
        """Create optimized writer detailed description prompt with technical depth"""
        return f"""<task>
撰写专利"{context.topic}"的具体实施方式章节{section_id}，详细描述技术实现方案。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
章节编号：{section_id}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
</context>

<thinking_process>
1. 分析技术实现的关键步骤
2. 确定技术参数和条件
3. 设计算法和流程
4. 考虑边界情况和异常处理
5. 确保技术描述的充分性
</thinking_process>

<output_format>
<detailed_description_section>
  <section_header>
    <!-- 章节标题和概述 -->
  </section_header>
  
  <technical_implementation>
    <system_architecture>
      <!-- 系统架构描述 -->
    </system_architecture>
    
    <process_flow>
      <steps>
        <!-- 处理步骤详细描述 -->
      </steps>
      <algorithms>
        <!-- 算法描述 -->
      </algorithms>
      <parameters>
        <!-- 参数设置 -->
      </parameters>
    </process_flow>
    
    <key_components>
      <!-- 关键组件描述 -->
    </key_components>
  </technical_implementation>
  
  <technical_details>
    <formulas>
      <!-- 数学公式 -->
    </formulas>
    <pseudocode>
      <!-- 伪代码 -->
    </pseudocode>
    <diagrams>
      <!-- 技术图表描述 -->
    </diagrams>
  </technical_details>
  
  <implementation_examples>
    <!-- 实施示例 -->
  </implementation_examples>
</detailed_description_section>
</output_format>

<technical_requirements>
- 包含至少1个mermaid流程图
- 包含2-3个算法公式
- 包含1段Python风格伪代码（≥30行）
- 描述实施步骤、输入输出、参数条件
- 保持术语一致性
</technical_requirements>

<constraints>
- 技术描述必须详细、准确
- 实现步骤必须清晰、可执行
- 算法描述必须完整、正确
- 参数设置必须合理、具体
- 字数控制在1200-2000字
</constraints>"""

    @staticmethod
    def create_writer_claims_prompt(context: PromptContext) -> str:
        """Create optimized writer claims prompt with legal compliance"""
        return f"""<task>
撰写专利"{context.topic}"的权利要求书，确保法律合规性和技术准确性。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
</context>

<thinking_process>
1. 分析技术方案的核心特征
2. 确定独立权利要求的范围
3. 设计从属权利要求的层次
4. 确保术语的一致性和准确性
5. 避免结果性限定和功能性描述
</thinking_process>

<output_format>
<patent_claims>
  <independent_claim_1>
    <!-- 独立权利要求1 -->
  </independent_claim_1>
  
  <dependent_claims>
    <dependent_claim_2>
      <!-- 从属权利要求2 -->
    </dependent_claim_2>
    <dependent_claim_3>
      <!-- 从属权利要求3 -->
    </dependent_claim_3>
    <dependent_claim_4>
      <!-- 从属权利要求4 -->
    </dependent_claim_4>
  </dependent_claims>
</patent_claims>
</output_format>

<claim_writing_principles>
- 独立权利要求覆盖核心处理链路
- 从属权利要求细化关键策略
- 术语统一、避免结果性限定
- 符合中国专利法要求
- 支持充分、描述准确
</claim_writing_principles>

<example_structure>
1. 一种[技术方案名称]，其特征在于，包括：
   [技术特征1]；
   [技术特征2]；
   [技术特征3]。

2. 根据权利要求1所述的[技术方案名称]，其特征在于，[技术特征2]包括：
   [细化特征2.1]；
   [细化特征2.2]。

3. 根据权利要求1所述的[技术方案名称]，其特征在于，[技术特征3]通过以下步骤实现：
   [步骤1]；
   [步骤2]；
   [步骤3]。
</example_structure>

<constraints>
- 权利要求必须符合专利法要求
- 技术特征必须具体、明确
- 术语使用必须一致、准确
- 避免功能性限定
- 支持充分、描述准确
</constraints>"""

    @staticmethod
    def create_reviewer_prompt(context: PromptContext, patent_content: str) -> str:
        """Create optimized reviewer prompt with comprehensive evaluation criteria"""
        return f"""<task>
对专利"{context.topic}"进行全面的质量审查和合规性检查。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
专利内容：{patent_content[:2000]}...
</context>

<thinking_process>
1. 检查技术内容的准确性
2. 评估法律合规性
3. 分析创新显著性
4. 验证描述充分性
5. 识别潜在问题和风险
6. 提供改进建议
</thinking_process>

<output_format>
<review_report>
  <overall_assessment>
    <quality_score>
      <!-- 质量评分（1-10分） -->
    </quality_score>
    <compliance_status>
      <!-- 合规状态 -->
    </compliance_status>
    <review_outcome>
      <!-- 审查结果 -->
    </review_outcome>
  </overall_assessment>
  
  <detailed_evaluation>
    <technical_accuracy>
      <!-- 技术准确性评估 -->
    </technical_accuracy>
    
    <legal_compliance>
      <!-- 法律合规性评估 -->
    </legal_compliance>
    
    <innovation_significance>
      <!-- 创新显著性评估 -->
    </innovation_significance>
    
    <description_sufficiency>
      <!-- 描述充分性评估 -->
    </description_sufficiency>
  </detailed_evaluation>
  
  <issues_and_recommendations>
    <identified_issues>
      <!-- 识别的问题 -->
    </identified_issues>
    
    <improvement_suggestions>
      <!-- 改进建议 -->
    </improvement_suggestions>
    
    <risk_assessment>
      <!-- 风险评估 -->
    </risk_assessment>
  </issues_and_recommendations>
</review_report>
</output_format>

<evaluation_criteria>
技术准确性：
- 技术描述是否准确无误
- 算法和流程是否正确
- 参数设置是否合理

法律合规性：
- 是否符合专利法要求
- 权利要求是否适当
- 是否避免法律风险

创新显著性：
- 创新点是否突出
- 技术贡献是否明确
- 与现有技术区别是否明显

描述充分性：
- 是否支持权利要求
- 技术方案是否完整
- 实施方式是否充分
</evaluation_criteria>

<constraints>
- 评估必须客观、全面
- 问题识别必须具体、准确
- 建议必须实用、可行
- 评分必须公正、合理
- 报告必须清晰、专业
</constraints>"""

    @staticmethod
    def create_rewriter_prompt(context: PromptContext, patent_content: str, review_feedback: str) -> str:
        """Create optimized rewriter prompt with targeted improvements"""
        return f"""<task>
根据审查反馈优化专利"{context.topic}"，提升文档质量和合规性。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
原始内容：{patent_content[:2000]}...
审查反馈：{review_feedback}
</context>

<thinking_process>
1. 分析审查反馈中的问题
2. 识别需要改进的具体内容
3. 制定优化策略和方案
4. 保持技术实质不变
5. 提升表达质量和合规性
6. 验证改进效果
</thinking_process>

<output_format>
<improved_patent>
  <optimization_summary>
    <!-- 优化总结 -->
  </optimization_summary>
  
  <improved_content>
    <!-- 优化后的内容 -->
  </improved_content>
  
  <improvement_details>
    <changes_made>
      <!-- 具体修改内容 -->
    </changes_made>
    
    <rationale>
      <!-- 修改理由 -->
    </rationale>
    
    <quality_improvements>
      <!-- 质量提升说明 -->
    </quality_improvements>
  </improvement_details>
</improved_patent>
</output_format>

<optimization_principles>
- 保持技术实质：不改变核心技术方案
- 提升表达质量：消除歧义，增强可读性
- 强化创新亮点：突出技术贡献
- 确保法律合规：符合专利法要求
- 针对性改进：根据反馈具体优化
</optimization_principles>

<constraints>
- 修改必须基于审查反馈
- 技术实质必须保持不变
- 表达质量必须显著提升
- 合规性必须得到改善
- 改进效果必须可验证
</constraints>"""

    @staticmethod
    def create_searcher_prompt(context: PromptContext) -> str:
        """Create optimized searcher prompt with comprehensive search strategy"""
        return f"""<task>
对专利"{context.topic}"进行全面的专利检索和技术分析。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
</context>

<thinking_process>
1. 确定检索关键词和分类
2. 设计检索策略和范围
3. 分析检索结果和相关性
4. 评估技术发展趋势
5. 识别竞争态势和风险
6. 提供策略建议
</thinking_process>

<output_format>
<search_report>
  <search_strategy>
    <keywords>
      <!-- 检索关键词 -->
    </keywords>
    <search_scope>
      <!-- 检索范围 -->
    </search_scope>
    <databases>
      <!-- 检索数据库 -->
    </databases>
  </search_strategy>
  
  <search_results>
    <relevant_patents>
      <!-- 相关专利分析 -->
    </relevant_patents>
    
    <technical_analysis>
      <!-- 技术分析 -->
    </technical_analysis>
    
    <trend_analysis>
      <!-- 趋势分析 -->
    </trend_analysis>
  </search_results>
  
  <competitive_landscape>
    <key_players>
      <!-- 主要竞争者 -->
    </key_players>
    
    <technology_gaps>
      <!-- 技术空白 -->
    </technology_gaps>
    
    <opportunities>
      <!-- 机会分析 -->
    </opportunities>
  </competitive_landscape>
  
  <strategic_recommendations>
    <!-- 策略建议 -->
  </strategic_recommendations>
</search_report>
</output_format>

<search_requirements>
- 检索范围必须全面、准确
- 分析必须深入、客观
- 结果必须相关、有价值
- 建议必须实用、可行
- 报告必须清晰、专业
</search_requirements>

<constraints>
- 检索必须系统、全面
- 分析必须客观、深入
- 结果必须准确、相关
- 建议必须实用、可行
- 报告必须清晰、专业
</constraints>"""

    @staticmethod
    def create_discusser_prompt(context: PromptContext, analysis_results: str) -> str:
        """Create optimized discusser prompt with deep analysis"""
        return f"""<task>
对专利"{context.topic}"进行深度技术讨论和创新点分析。
</task>

<context>
专利主题：{context.topic}
技术描述：{context.description}
目标受众：{context.target_audience}
写作风格：{context.writing_style}
分析结果：{analysis_results}
</context>

<thinking_process>
1. 分析技术方案的核心价值
2. 识别创新点和竞争优势
3. 评估技术可行性和风险
4. 分析市场应用前景
5. 提供优化建议和策略
</thinking_process>

<output_format>
<discussion_report>
  <technical_analysis>
    <core_value>
      <!-- 核心价值分析 -->
    </core_value>
    
    <innovation_points>
      <!-- 创新点分析 -->
    </innovation_points>
    
    <competitive_advantages>
      <!-- 竞争优势分析 -->
    </competitive_advantages>
  </technical_analysis>
  
  <feasibility_assessment>
    <technical_feasibility>
      <!-- 技术可行性 -->
    </technical_feasibility>
    
    <implementation_risks>
      <!-- 实施风险 -->
    </implementation_risks>
    
    <market_potential>
      <!-- 市场潜力 -->
    </market_potential>
  </feasibility_assessment>
  
  <strategic_recommendations>
    <optimization_suggestions>
      <!-- 优化建议 -->
    </optimization_suggestions>
    
    <development_strategy>
      <!-- 发展策略 -->
    </development_strategy>
    
    <risk_mitigation>
      <!-- 风险缓解 -->
    </risk_mitigation>
  </strategic_recommendations>
</discussion_report>
</output_format>

<discussion_focus>
- 技术方案的核心价值
- 创新点和竞争优势
- 技术可行性和风险
- 市场应用前景
- 优化建议和策略
</discussion_focus>

<constraints>
- 分析必须深入、客观
- 观点必须有理有据
- 建议必须实用、可行
- 表达必须清晰、专业
- 逻辑必须严密、系统
</constraints>"""

class PromptManager:
    """Manager class for creating and combining optimized prompts"""
    
    @staticmethod
    def create_context(
        topic: str,
        description: str,
        previous_results: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        target_audience: str = "patent_examiners",
        writing_style: str = "technical_legal",
        quality_standards: Optional[List[str]] = None
    ) -> PromptContext:
        """Create a prompt context with all necessary information"""
        return PromptContext(
            topic=topic,
            description=description,
            previous_results=previous_results,
            constraints=constraints,
            examples=examples,
            target_audience=target_audience,
            writing_style=writing_style,
            quality_standards=quality_standards
        )

    @staticmethod
    def get_system_role(agent_type: str) -> str:
        """Get system role for specific agent type"""
        return AnthropicOptimizedPrompts.get_system_role(agent_type)

    @staticmethod
    def combine_prompts(system_role: str, task_prompt: str) -> str:
        """Combine system role and task prompt into a complete prompt"""
        return f"{system_role}\n\n{task_prompt}"

    @staticmethod
    def create_agent_prompt(agent_type: str, context: PromptContext, **kwargs) -> str:
        """Create a complete prompt for a specific agent type"""
        system_role = PromptManager.get_system_role(agent_type)
        
        if agent_type == "planner":
            task_prompt = AnthropicOptimizedPrompts.create_planner_prompt(context)
        elif agent_type == "writer":
            if kwargs.get("prompt_type") == "outline":
                task_prompt = AnthropicOptimizedPrompts.create_writer_outline_prompt(context)
            elif kwargs.get("prompt_type") == "background":
                task_prompt = AnthropicOptimizedPrompts.create_writer_background_prompt(context)
            elif kwargs.get("prompt_type") == "summary":
                task_prompt = AnthropicOptimizedPrompts.create_writer_summary_prompt(context)
            elif kwargs.get("prompt_type") == "detailed_description":
                section_id = kwargs.get("section_id", "A")
                task_prompt = AnthropicOptimizedPrompts.create_writer_detailed_description_prompt(context, section_id)
            elif kwargs.get("prompt_type") == "claims":
                task_prompt = AnthropicOptimizedPrompts.create_writer_claims_prompt(context)
            else:
                task_prompt = AnthropicOptimizedPrompts.create_writer_outline_prompt(context)
        elif agent_type == "reviewer":
            patent_content = kwargs.get("patent_content", "")
            task_prompt = AnthropicOptimizedPrompts.create_reviewer_prompt(context, patent_content)
        elif agent_type == "rewriter":
            patent_content = kwargs.get("patent_content", "")
            review_feedback = kwargs.get("review_feedback", "")
            task_prompt = AnthropicOptimizedPrompts.create_rewriter_prompt(context, patent_content, review_feedback)
        elif agent_type == "searcher":
            task_prompt = AnthropicOptimizedPrompts.create_searcher_prompt(context)
        elif agent_type == "discusser":
            analysis_results = kwargs.get("analysis_results", "")
            task_prompt = AnthropicOptimizedPrompts.create_discusser_prompt(context, analysis_results)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return PromptManager.combine_prompts(system_role, task_prompt)

# Example usage
if __name__ == "__main__":
    # Create context
    context = PromptManager.create_context(
        topic="以证据图增强的rag系统",
        description="一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统",
        previous_results={"analysis": "previous analysis results"},
        constraints=["技术描述必须准确", "符合专利法要求"],
        examples=["示例1", "示例2"]
    )
    
    # Create optimized prompt
    prompt = PromptManager.create_agent_prompt("writer", context, prompt_type="outline")
    print("Optimized Writer Prompt:")
    print(prompt)