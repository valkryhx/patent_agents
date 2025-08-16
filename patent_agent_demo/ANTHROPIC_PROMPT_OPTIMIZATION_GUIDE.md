# Anthropic Prompt Optimization Guide for Patent Agent System

## Overview

This guide documents the comprehensive optimization of agent prompts in the patent writing system, following Anthropic's Prompt Engineering Best Practices. The optimization focuses on improving prompt clarity, structure, and effectiveness to enhance the quality of patent document generation.

## Anthropic's Prompt Engineering Best Practices Implemented

### 1. Clear Role Definition and Context

Each agent has a clearly defined role with specific expertise areas, work style, and output requirements:

#### Planner Agent
- **Role**: Patent strategy expert with 15+ years experience
- **Expertise**: Patent feasibility analysis, innovation identification, strategy planning
- **Work Style**: Systematic thinking, data-driven analysis, forward-looking planning
- **Output Style**: Professional, objective, structured, actionable

#### Writer Agent
- **Role**: Professional patent writing expert
- **Expertise**: Technical documentation, patent drafting, legal compliance
- **Writing Principles**: Clear and accurate, complete structure, unified terminology
- **Output Requirements**: Patent-compliant, appropriate technical depth, professional language

#### Reviewer Agent
- **Role**: Strict patent review expert
- **Responsibilities**: Technical accuracy verification, legal compliance checking
- **Review Standards**: Technical accuracy, legal compliance, innovation significance
- **Review Process**: Systematic checking, objective evaluation, detailed feedback

#### Rewriter Agent
- **Role**: Patent document optimization expert
- **Expertise**: Document structure optimization, technical description refinement
- **Optimization Principles**: Maintain technical accuracy, improve expression clarity
- **Work Approach**: Systematic analysis, targeted improvement, iterative refinement

### 2. Structured Output with XML Tags

All prompts use XML tags to ensure consistent, structured output:

```xml
<task>
Task description
</task>

<context>
Context information
</context>

<thinking_process>
1. Step-by-step reasoning process
2. Analysis methodology
3. Decision-making framework
</thinking_process>

<output_format>
<structured_output>
  <section>
    <content>Structured content</content>
  </section>
</structured_output>
</output_format>

<constraints>
- Specific constraints and requirements
- Quality standards
- Output expectations
</constraints>

### 3. Chain-of-Thought Reasoning

Prompts include explicit thinking processes to guide step-by-step reasoning:

#### Example: Planner Agent Thinking Process
```
<thinking_process>
1. 分析技术方案的核心创新点
2. 识别关键技术特征和优势
3. 评估专利可行性和风险
4. 制定撰写策略和重点
5. 规划文档结构和内容
6. 确定质量标准和检查点
</thinking_process>
```

#### Example: Writer Agent Thinking Process
```
<thinking_process>
1. 分析技术方案的核心内容
2. 确定必要的专利章节
3. 规划各章节的内容要点
4. 确保章节间的逻辑关系
5. 预估各章节的字数要求
6. 确定重点突出的内容
</thinking_process>
```

### 4. Context Provision

Each prompt provides comprehensive context including:
- Patent topic and description
- Previous results and analysis
- Specific constraints and requirements
- Examples and templates
- Target audience and writing style

### 5. Complex Task Breakdown

Complex tasks are broken down into manageable steps with clear requirements for each step:

#### Writer Agent Task Breakdown
1. **Outline Generation**: Create detailed patent structure
2. **Background Section**: Analyze existing technology and problems
3. **Summary Section**: Overview technical solution and innovations
4. **Detailed Description**: Comprehensive technical implementation
5. **Claims Writing**: Legal-compliant patent claims
6. **Drawings Description**: Technical diagram explanations

### 6. Explicit Constraints and Requirements

All prompts include explicit constraints to ensure quality and compliance:

#### Technical Requirements
- Include specific technical elements (mermaid diagrams, algorithms, pseudocode)
- Maintain terminology consistency
- Ensure technical accuracy and completeness

#### Legal Requirements
- Comply with patent law requirements
- Avoid functional limitations
- Ensure sufficient disclosure

#### Quality Standards
- Professional language and expression
- Clear and logical structure
- Comprehensive and accurate content

## Key Improvements Over Previous Versions

### Before Optimization
- Simple, unstructured prompts
- Limited context provision
- No clear role definition
- Inconsistent output formats
- Minimal guidance for complex tasks
- Lack of systematic thinking processes

### After Optimization
- Comprehensive role definitions with expertise areas
- Structured XML output formats
- Chain-of-thought reasoning processes
- Rich context provision
- Complex task breakdown
- Explicit constraints and requirements
- Professional quality standards

## Implementation Examples

### 1. Basic Usage

```python
from anthropic_optimized_prompts import PromptManager, PromptContext

# Create context
context = PromptManager.create_context(
    topic="以证据图增强的rag系统",
    description="一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统",
    previous_results={"analysis": "previous analysis results"},
    constraints=["技术描述必须准确", "符合专利法要求"],
    examples=["示例1", "示例2"]
)

# Get optimized prompt
prompt = PromptManager.create_agent_prompt("writer", context, prompt_type="outline")

# Combine with system role
system_role = PromptManager.get_system_role("writer")
full_prompt = PromptManager.combine_prompts(system_role, prompt)
```

### 2. Agent-Specific Prompts

#### Planner Agent
```python
prompt = PromptManager.create_agent_prompt("planner", context)
```

#### Writer Agent (Different Types)
```python
# Outline generation
outline_prompt = PromptManager.create_agent_prompt("writer", context, prompt_type="outline")

# Background section
background_prompt = PromptManager.create_agent_prompt("writer", context, prompt_type="background")

# Summary section
summary_prompt = PromptManager.create_agent_prompt("writer", context, prompt_type="summary")

# Detailed description
detail_prompt = PromptManager.create_agent_prompt("writer", context, prompt_type="detailed_description", section_id="A")

# Claims writing
claims_prompt = PromptManager.create_agent_prompt("writer", context, prompt_type="claims")
```

#### Reviewer Agent
```python
prompt = PromptManager.create_agent_prompt("reviewer", context, patent_content="patent content...")
```

#### Rewriter Agent
```python
prompt = PromptManager.create_agent_prompt("rewriter", context, 
                                         patent_content="original content...", 
                                         review_feedback="review feedback...")
```

## Quality Assurance Features

### 1. Structured Output Validation
- XML tag structure ensures consistent output format
- Required sections are explicitly defined
- Output validation against expected structure

### 2. Quality Standards Enforcement
- Explicit quality criteria in each prompt
- Professional standards for language and expression
- Technical accuracy requirements

### 3. Compliance Checking
- Legal compliance requirements built into prompts
- Patent law considerations integrated
- Risk assessment and mitigation strategies

## Performance Benefits

### 1. Improved Output Quality
- More structured and professional content
- Better technical accuracy and completeness
- Enhanced legal compliance

### 2. Increased Consistency
- Standardized output formats across agents
- Consistent terminology and style
- Uniform quality standards

### 3. Enhanced Efficiency
- Clear task breakdown reduces complexity
- Structured thinking processes improve reasoning
- Explicit constraints reduce errors

### 4. Better Collaboration
- Clear role definitions improve agent coordination
- Structured outputs facilitate information exchange
- Consistent formats enable seamless integration

## Best Practices for Using Optimized Prompts

### 1. Context Preparation
- Provide comprehensive context information
- Include relevant previous results
- Specify clear constraints and requirements

### 2. Prompt Selection
- Choose appropriate agent type for the task
- Select specific prompt type when available
- Consider task complexity and requirements

### 3. Output Processing
- Validate output against expected structure
- Check for required sections and content
- Ensure quality standards are met

### 4. Iterative Improvement
- Use feedback to refine prompts
- Update context based on results
- Continuously improve prompt effectiveness

## Integration with Patent Agent System

### 1. Agent Integration
The optimized prompts are integrated into the existing agent system:

```python
# In agent classes
from anthropic_optimized_prompts import PromptManager

async def execute_task(self, task_data):
    context = PromptManager.create_context(
        topic=task_data.get("topic"),
        description=task_data.get("description"),
        previous_results=task_data.get("previous_results")
    )
    
    prompt = PromptManager.create_agent_prompt(
        self.agent_type, 
        context, 
        **task_data.get("prompt_kwargs", {})
    )
    
    # Use optimized prompt for generation
    result = await self.generate_content(prompt)
    return result
```

### 2. Workflow Integration
The prompts are designed to work seamlessly with the existing workflow:

- **Planner Agent**: Creates comprehensive patent strategy
- **Writer Agent**: Generates high-quality patent content
- **Reviewer Agent**: Ensures quality and compliance
- **Rewriter Agent**: Optimizes content based on feedback

### 3. Quality Control
The optimized prompts include built-in quality control mechanisms:

- Structured output validation
- Quality standards enforcement
- Compliance checking
- Risk assessment

## Conclusion

The Anthropic-optimized prompts represent a significant improvement in the patent agent system's capabilities. By implementing these best practices, the system can generate higher quality, more consistent, and more compliant patent documents. The structured approach ensures that all agents work effectively together while maintaining the highest standards of quality and professionalism.

The optimization follows Anthropic's proven methodologies and adapts them specifically for patent writing, creating a robust and effective system for automated patent document generation.