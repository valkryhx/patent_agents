# Patent Agent Prompt Optimization Guide

## Overview

This guide documents the comprehensive optimization of agent prompts in the patent writing system, following Anthropic's Prompt Engineering Best Practices. The optimization focuses on improving prompt clarity, structure, and effectiveness to enhance the quality of patent document generation.

## Optimization Principles

### 1. Clear Role Definition
Each agent has a clearly defined role with specific expertise areas, work style, and output requirements:

- **Planner Agent**: Patent strategy expert with 15+ years experience
- **Writer Agent**: Professional patent writing expert
- **Reviewer Agent**: Strict patent review expert
- **Rewriter Agent**: Patent document optimization expert

### 2. Structured Output with XML Tags
All prompts use XML tags to ensure consistent, structured output:

```xml
<task>
Task description
</task>

<context>
Context information
</context>

<output_format>
<structured_output>
  <section>
    <content>Structured content</content>
  </section>
</structured_output>
</output_format>
```

### 3. Chain-of-Thought Reasoning
Prompts include explicit thinking processes to guide step-by-step reasoning:

```
<thinking_process>
1. Analyze current situation
2. Identify opportunities
3. Develop strategy
4. Validate feasibility
</thinking_process>
```

### 4. Context Provision
Each prompt provides comprehensive context including:
- Patent topic and description
- Previous results and analysis
- Specific constraints and requirements
- Examples and templates

### 5. Complex Task Breakdown
Complex tasks are broken down into manageable steps with clear requirements for each step.

## Key Improvements

### Before Optimization
- Simple, unstructured prompts
- Limited context provision
- No clear role definition
- Inconsistent output formats
- Minimal guidance for complex tasks

### After Optimization
- Comprehensive role definitions with expertise areas
- Structured XML output formats
- Chain-of-thought reasoning processes
- Rich context provision
- Complex task breakdown
- Explicit constraints and requirements

## Usage Guide

### 1. Basic Usage

```python
from optimized_prompts_v2 import OptimizedPromptsV2, PromptManager

# Create context
context = PromptManager.create_context(
    topic="以证据图增强的rag系统",
    description="一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统",
    previous_results={"analysis": "previous analysis results"}
)

# Get optimized prompt
prompt = OptimizedPromptsV2.get_writer_outline_prompt(context)

# Combine with system role
system_role = PromptManager.get_system_role("writer")
full_prompt = PromptManager.combine_prompts(system_role, prompt)
```

### 2. Agent-Specific Prompts

#### Planner Agent
```python
# Strategy development prompt
strategy_prompt = OptimizedPromptsV2.get_planner_strategy_prompt(context)
```

#### Writer Agent
```python
# Outline generation
outline_prompt = OptimizedPromptsV2.get_writer_outline_prompt(context)

# Background section
background_prompt = OptimizedPromptsV2.get_writer_background_prompt(context)

# Summary section
summary_prompt = OptimizedPromptsV2.get_writer_summary_prompt(context)

# Implementation section
implementation_prompt = OptimizedPromptsV2.get_writer_implementation_prompt(
    context, "A", "数据获取与证据构建"
)

# Claims generation
claims_prompt = OptimizedPromptsV2.get_writer_claims_prompt(context)
```

#### Reviewer Agent
```python
# Quality review prompt
review_prompt = OptimizedPromptsV2.get_reviewer_quality_prompt(context)
```

#### Rewriter Agent
```python
# Document optimization prompt
optimization_prompt = OptimizedPromptsV2.get_rewriter_optimization_prompt(
    context, "Review feedback here"
)
```

## Output Format Examples

### 1. Patent Outline Output
```xml
<patent_outline>
  <chapter id="1">
    <title>技术领域</title>
    <key_points>
      <point id="1.1">要点1：技术领域定义</point>
      <point id="1.2">要点2：应用场景分析</point>
      <point id="1.3">要点3：技术发展趋势</point>
    </key_points>
    <estimated_words>800</estimated_words>
    <technical_depth>专业级</technical_depth>
  </chapter>
  <!-- More chapters -->
</patent_outline>
```

### 2. Quality Review Output
```xml
<quality_review>
  <review_summary>
    <overall_score>85/100</overall_score>
    <overall_assessment>总体质量良好，需要部分改进</overall_assessment>
  </review_summary>
  
  <technical_review>
    <accuracy_score>90/100</accuracy_score>
    <accuracy_issues>
      <issue>技术问题1</issue>
    </accuracy_issues>
    <accuracy_suggestions>
      <suggestion>改进建议1</suggestion>
    </accuracy_suggestions>
  </technical_review>
  <!-- More review sections -->
</quality_review>
```

## Integration with Existing System

### 1. Update Agent Classes
To integrate the optimized prompts, update the agent classes to use the new prompt system:

```python
# In writer_agent.py
from optimized_prompts_v2 import OptimizedPromptsV2, PromptManager

class WriterAgent(BaseAgent):
    async def _write_outline(self, topic: str, description: str):
        context = PromptManager.create_context(topic, description)
        prompt = OptimizedPromptsV2.get_writer_outline_prompt(context)
        system_role = PromptManager.get_system_role("writer")
        full_prompt = PromptManager.combine_prompts(system_role, prompt)
        
        response = await self.openai_client._generate_response(full_prompt)
        return response
```

### 2. XML Response Parsing
Add XML parsing utilities to extract structured content:

```python
import xml.etree.ElementTree as ET

def parse_xml_response(response: str):
    """Parse XML response from optimized prompts"""
    try:
        root = ET.fromstring(response)
        return root
    except ET.ParseError:
        # Fallback to text processing if XML parsing fails
        return response
```

## Benefits of Optimization

### 1. Improved Quality
- More consistent and structured outputs
- Better technical accuracy
- Enhanced legal compliance
- Clearer innovation highlighting

### 2. Better Consistency
- Standardized output formats
- Unified terminology usage
- Consistent document structure
- Predictable response patterns

### 3. Enhanced Efficiency
- Clearer task requirements
- Reduced need for clarification
- Faster content generation
- Better error handling

### 4. Easier Maintenance
- Modular prompt structure
- Clear separation of concerns
- Easy to update and extend
- Better documentation

## Best Practices for Using Optimized Prompts

### 1. Context Management
- Always provide comprehensive context
- Include relevant previous results
- Specify clear constraints
- Provide examples when needed

### 2. Output Processing
- Use XML parsing for structured outputs
- Implement fallback mechanisms
- Validate output completeness
- Handle parsing errors gracefully

### 3. Prompt Customization
- Adapt prompts for specific use cases
- Add domain-specific constraints
- Customize output formats as needed
- Maintain consistency across agents

### 4. Quality Assurance
- Validate prompt effectiveness
- Monitor output quality
- Collect feedback for improvements
- Iterate based on results

## Future Enhancements

### 1. Dynamic Prompt Generation
- Context-aware prompt selection
- Adaptive prompt modification
- Learning from previous interactions
- Personalized prompt optimization

### 2. Advanced XML Processing
- Schema validation
- Automated content extraction
- Quality scoring
- Error correction

### 3. Multi-Modal Prompts
- Integration with visual elements
- Support for diagrams and charts
- Enhanced formatting options
- Rich media content

### 4. Collaborative Prompting
- Multi-agent coordination
- Shared context management
- Cross-agent validation
- Unified output generation

## Conclusion

The optimized prompts represent a significant improvement in the patent writing system's effectiveness and reliability. By following Anthropic's best practices, the system now provides:

- Clear role definitions and expertise areas
- Structured, consistent outputs
- Comprehensive context provision
- Step-by-step reasoning guidance
- Complex task breakdown
- Explicit constraints and requirements

These improvements lead to higher quality patent documents, better consistency, and more efficient operation of the multi-agent system.