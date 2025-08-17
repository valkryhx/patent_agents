#!/usr/bin/env python3
"""
Test script for Anthropic-optimized prompts
Demonstrates the improved prompt engineering approach
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anthropic_optimized_prompts import PromptManager, PromptContext

class AnthropicPromptTester:
    """Test class for demonstrating optimized prompts"""
    
    def __init__(self):
        self.test_context = self._create_test_context()
        
    def _create_test_context(self) -> PromptContext:
        """Create a test context for patent writing"""
        return PromptManager.create_context(
            topic="以证据图增强的rag系统",
            description="一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统",
            previous_results={
                "analysis": {
                    "core_innovation": "证据图构建和子图选择机制",
                    "technical_features": ["跨文档关系建模", "动态证据融合", "可追溯性验证"],
                    "competitive_advantages": ["提高检索精度", "增强可解释性", "支持复杂推理"]
                }
            },
            constraints=[
                "技术描述必须准确无误",
                "符合中国专利法要求",
                "避免功能性限定",
                "确保充分公开"
            ],
            examples=[
                "证据图构建示例：基于文档实体关系构建有向图",
                "子图选择示例：使用图神经网络进行相关性评分"
            ],
            target_audience="patent_examiners",
            writing_style="technical_legal",
            quality_standards=[
                "专业术语使用准确",
                "技术方案描述充分",
                "创新点突出明确",
                "法律合规性良好"
            ]
        )
    
    def test_planner_prompt(self):
        """Test planner agent prompt"""
        print("=" * 80)
        print("TESTING PLANNER AGENT PROMPT")
        print("=" * 80)
        
        prompt = PromptManager.create_agent_prompt("planner", self.test_context)
        
        print("Generated Prompt:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)
        
        # Analyze prompt structure
        self._analyze_prompt_structure(prompt, "Planner")
        
    def test_writer_prompts(self):
        """Test writer agent prompts for different sections"""
        print("\n" + "=" * 80)
        print("TESTING WRITER AGENT PROMPTS")
        print("=" * 80)
        
        # Test outline prompt
        print("\n1. OUTLINE PROMPT:")
        print("-" * 40)
        outline_prompt = PromptManager.create_agent_prompt("writer", self.test_context, prompt_type="outline")
        print(outline_prompt[:1000] + "..." if len(outline_prompt) > 1000 else outline_prompt)
        
        # Test background prompt
        print("\n2. BACKGROUND PROMPT:")
        print("-" * 40)
        background_prompt = PromptManager.create_agent_prompt("writer", self.test_context, prompt_type="background")
        print(background_prompt[:1000] + "..." if len(background_prompt) > 1000 else background_prompt)
        
        # Test summary prompt
        print("\n3. SUMMARY PROMPT:")
        print("-" * 40)
        summary_prompt = PromptManager.create_agent_prompt("writer", self.test_context, prompt_type="summary")
        print(summary_prompt[:1000] + "..." if len(summary_prompt) > 1000 else summary_prompt)
        
        # Test detailed description prompt
        print("\n4. DETAILED DESCRIPTION PROMPT:")
        print("-" * 40)
        detail_prompt = PromptManager.create_agent_prompt("writer", self.test_context, prompt_type="detailed_description", section_id="A")
        print(detail_prompt[:1000] + "..." if len(detail_prompt) > 1000 else detail_prompt)
        
        # Test claims prompt
        print("\n5. CLAIMS PROMPT:")
        print("-" * 40)
        claims_prompt = PromptManager.create_agent_prompt("writer", self.test_context, prompt_type="claims")
        print(claims_prompt[:1000] + "..." if len(claims_prompt) > 1000 else claims_prompt)
        
    def test_reviewer_prompt(self):
        """Test reviewer agent prompt"""
        print("\n" + "=" * 80)
        print("TESTING REVIEWER AGENT PROMPT")
        print("=" * 80)
        
        # Sample patent content for review
        sample_patent_content = """
        一种以证据图增强的RAG系统，包括：
        1. 证据图构建模块，用于构建跨文档证据关系图
        2. 子图选择模块，用于选择相关证据子图
        3. 生成验证模块，用于生成和验证回答
        
        技术方案通过以下步骤实现：
        步骤1：构建证据图
        步骤2：选择相关子图
        步骤3：生成回答
        步骤4：验证结果
        """
        
        prompt = PromptManager.create_agent_prompt("reviewer", self.test_context, patent_content=sample_patent_content)
        
        print("Generated Prompt:")
        print("-" * 40)
        print(prompt[:1500] + "..." if len(prompt) > 1500 else prompt)
        print("-" * 40)
        
        # Analyze prompt structure
        self._analyze_prompt_structure(prompt, "Reviewer")
        
    def test_rewriter_prompt(self):
        """Test rewriter agent prompt"""
        print("\n" + "=" * 80)
        print("TESTING REWRITER AGENT PROMPT")
        print("=" * 80)
        
        # Sample patent content and review feedback
        sample_patent_content = """
        一种以证据图增强的RAG系统，包括证据图构建模块、子图选择模块和生成验证模块。
        系统通过构建跨文档证据关系图，选择相关证据子图，生成和验证回答。
        """
        
        sample_review_feedback = """
        审查意见：
        1. 技术方案描述不够详细，需要补充具体实现步骤
        2. 权利要求过于宽泛，需要增加具体技术特征
        3. 创新点不够突出，需要明确与现有技术的区别
        4. 技术效果描述不够具体，需要量化指标
        """
        
        prompt = PromptManager.create_agent_prompt("rewriter", self.test_context, 
                                                 patent_content=sample_patent_content,
                                                 review_feedback=sample_review_feedback)
        
        print("Generated Prompt:")
        print("-" * 40)
        print(prompt[:1500] + "..." if len(prompt) > 1500 else prompt)
        print("-" * 40)
        
        # Analyze prompt structure
        self._analyze_prompt_structure(prompt, "Rewriter")
        
    def test_searcher_prompt(self):
        """Test searcher agent prompt"""
        print("\n" + "=" * 80)
        print("TESTING SEARCHER AGENT PROMPT")
        print("=" * 80)
        
        prompt = PromptManager.create_agent_prompt("searcher", self.test_context)
        
        print("Generated Prompt:")
        print("-" * 40)
        print(prompt[:1500] + "..." if len(prompt) > 1500 else prompt)
        print("-" * 40)
        
        # Analyze prompt structure
        self._analyze_prompt_structure(prompt, "Searcher")
        
    def test_discusser_prompt(self):
        """Test discusser agent prompt"""
        print("\n" + "=" * 80)
        print("TESTING DISCUSSER AGENT PROMPT")
        print("=" * 80)
        
        # Sample analysis results
        sample_analysis_results = """
        技术分析结果：
        1. 核心创新：证据图构建和子图选择机制
        2. 技术优势：提高检索精度，增强可解释性
        3. 应用前景：适用于复杂问答和推理任务
        4. 技术风险：计算复杂度较高，需要优化算法
        """
        
        prompt = PromptManager.create_agent_prompt("discusser", self.test_context, analysis_results=sample_analysis_results)
        
        print("Generated Prompt:")
        print("-" * 40)
        print(prompt[:1500] + "..." if len(prompt) > 1500 else prompt)
        print("-" * 40)
        
        # Analyze prompt structure
        self._analyze_prompt_structure(prompt, "Discusser")
        
    def _analyze_prompt_structure(self, prompt: str, agent_type: str):
        """Analyze the structure of a generated prompt"""
        print(f"\n{agent_type} Prompt Analysis:")
        print("-" * 30)
        
        # Check for key components
        components = {
            "Role Definition": "<role>" in prompt,
            "Task Description": "<task>" in prompt,
            "Context Information": "<context>" in prompt,
            "Thinking Process": "<thinking_process>" in prompt,
            "Output Format": "<output_format>" in prompt,
            "Constraints": "<constraints>" in prompt,
            "Examples": "<example" in prompt,
            "Technical Requirements": "<technical_requirements>" in prompt
        }
        
        for component, present in components.items():
            status = "✓" if present else "✗"
            print(f"{status} {component}")
            
        # Count XML tags
        xml_tags = prompt.count("<") // 2  # Approximate count
        print(f"\nTotal XML tags: {xml_tags}")
        
        # Prompt length
        print(f"Prompt length: {len(prompt)} characters")
        
    def test_prompt_manager_functions(self):
        """Test PromptManager utility functions"""
        print("\n" + "=" * 80)
        print("TESTING PROMPT MANAGER FUNCTIONS")
        print("=" * 80)
        
        # Test system role retrieval
        print("\n1. System Role Retrieval:")
        print("-" * 30)
        for agent_type in ["planner", "writer", "reviewer", "rewriter", "searcher", "discusser"]:
            role = PromptManager.get_system_role(agent_type)
            print(f"{agent_type}: {len(role)} characters")
            
        # Test context creation
        print("\n2. Context Creation:")
        print("-" * 30)
        context = PromptManager.create_context(
            topic="测试主题",
            description="测试描述",
            previous_results={"test": "data"},
            constraints=["约束1", "约束2"]
        )
        print(f"Context created: {context.topic}, {context.description}")
        print(f"Constraints: {context.constraints}")
        
        # Test prompt combination
        print("\n3. Prompt Combination:")
        print("-" * 30)
        system_role = PromptManager.get_system_role("writer")
        task_prompt = "Test task prompt"
        combined = PromptManager.combine_prompts(system_role, task_prompt)
        print(f"Combined prompt length: {len(combined)} characters")
        
    def run_comprehensive_test(self):
        """Run all tests"""
        print("ANTHROPIC PROMPT OPTIMIZATION TEST SUITE")
        print("=" * 80)
        print("Testing optimized prompts following Anthropic's best practices...")
        
        try:
            # Test all agent prompts
            self.test_planner_prompt()
            self.test_writer_prompts()
            self.test_reviewer_prompt()
            self.test_rewriter_prompt()
            self.test_searcher_prompt()
            self.test_discusser_prompt()
            
            # Test utility functions
            self.test_prompt_manager_functions()
            
            print("\n" + "=" * 80)
            print("ALL TESTS COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print("\nKey Benefits of Optimized Prompts:")
            print("✓ Clear role definitions with expertise areas")
            print("✓ Structured XML output formats")
            print("✓ Chain-of-thought reasoning processes")
            print("✓ Rich context provision")
            print("✓ Complex task breakdown")
            print("✓ Explicit constraints and requirements")
            print("✓ Professional quality standards")
            
        except Exception as e:
            print(f"\nError during testing: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the test suite"""
    tester = AnthropicPromptTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()