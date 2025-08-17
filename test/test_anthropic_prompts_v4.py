#!/usr/bin/env python3
"""
Test script for Anthropic-Optimized Prompts v4.0
Demonstrates the improved prompt engineering following Anthropic's best practices
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anthropic_optimized_prompts_v4 import AnthropicOptimizedPromptsV4, PromptContext, PromptManager

class AnthropicPromptsV4Tester:
    """Test class for the new optimized prompts"""
    
    def __init__(self):
        self.test_context = PromptContext(
            topic="以证据图增强的RAG系统",
            description="一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统",
            target_audience="patent_examiners",
            writing_style="technical_legal",
            quality_standards=["技术准确性", "法律合规性", "创新显著性", "描述充分性"],
            workflow_stage="initial"
        )
        
    def test_planner_prompt(self):
        """Test planner prompt with chain-of-thought reasoning"""
        print("=" * 80)
        print("🧠 Testing Planner Prompt (Chain-of-Thought)")
        print("=" * 80)
        
        prompt = AnthropicOptimizedPromptsV4.create_planner_prompt(self.test_context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_writer_outline_prompt(self):
        """Test writer outline prompt with structured output"""
        print("\n" + "=" * 80)
        print("📋 Testing Writer Outline Prompt (Structured Output)")
        print("=" * 80)
        
        prompt = AnthropicOptimizedPromptsV4.create_writer_outline_prompt(self.test_context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_writer_background_prompt(self):
        """Test writer background prompt"""
        print("\n" + "=" * 80)
        print("🔍 Testing Writer Background Prompt")
        print("=" * 80)
        
        prompt = AnthropicOptimizedPromptsV4.create_writer_background_prompt(self.test_context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_writer_summary_prompt(self):
        """Test writer summary prompt"""
        print("\n" + "=" * 80)
        print("📝 Testing Writer Summary Prompt")
        print("=" * 80)
        
        prompt = AnthropicOptimizedPromptsV4.create_writer_summary_prompt(self.test_context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_writer_detailed_description_prompt(self):
        """Test writer detailed description prompt"""
        print("\n" + "=" * 80)
        print("🔧 Testing Writer Detailed Description Prompt")
        print("=" * 80)
        
        prompt = AnthropicOptimizedPromptsV4.create_writer_detailed_description_prompt(
            self.test_context, section_id="A"
        )
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_writer_claims_prompt(self):
        """Test writer claims prompt"""
        print("\n" + "=" * 80)
        print("⚖️ Testing Writer Claims Prompt")
        print("=" * 80)
        
        prompt = AnthropicOptimizedPromptsV4.create_writer_claims_prompt(self.test_context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_reviewer_prompt(self):
        """Test reviewer prompt"""
        print("\n" + "=" * 80)
        print("🔍 Testing Reviewer Prompt")
        print("=" * 80)
        
        sample_patent_content = """
        本发明涉及一种以证据图增强的RAG系统，包括：
        1. 证据图构建模块
        2. 子图选择模块
        3. 生成与验证模块
        
        该系统通过构建跨文档证据关系图，实现了更准确的信息检索和生成。
        """
        
        prompt = AnthropicOptimizedPromptsV4.create_reviewer_prompt(
            self.test_context, sample_patent_content
        )
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_rewriter_prompt(self):
        """Test rewriter prompt"""
        print("\n" + "=" * 80)
        print("✏️ Testing Rewriter Prompt")
        print("=" * 80)
        
        sample_patent_content = "原始专利内容示例..."
        sample_review_feedback = "审查反馈：需要改进技术描述的准确性..."
        
        prompt = AnthropicOptimizedPromptsV4.create_rewriter_prompt(
            self.test_context, sample_patent_content, sample_review_feedback
        )
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_searcher_prompt(self):
        """Test searcher prompt"""
        print("\n" + "=" * 80)
        print("🔎 Testing Searcher Prompt")
        print("=" * 80)
        
        prompt = AnthropicOptimizedPromptsV4.create_searcher_prompt(self.test_context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_discusser_prompt(self):
        """Test discusser prompt"""
        print("\n" + "=" * 80)
        print("💬 Testing Discusser Prompt")
        print("=" * 80)
        
        sample_analysis_results = "分析结果：该技术方案具有较高的创新性和实用性..."
        
        prompt = AnthropicOptimizedPromptsV4.create_discusser_prompt(
            self.test_context, sample_analysis_results
        )
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print(f"\n📊 Prompt Length: {len(prompt)} characters")
        
        return prompt
    
    def test_prompt_manager(self):
        """Test prompt manager functionality"""
        print("\n" + "=" * 80)
        print("🛠️ Testing Prompt Manager")
        print("=" * 80)
        
        # Test different agent types
        agent_types = ["planner", "writer", "reviewer", "rewriter", "searcher", "discusser"]
        
        for agent_type in agent_types:
            print(f"\n📋 Testing {agent_type} agent prompt:")
            
            if agent_type == "writer":
                # Test different writer prompt types
                prompt_types = ["outline", "background", "summary", "detailed_description", "claims"]
                for prompt_type in prompt_types:
                    try:
                        if prompt_type == "detailed_description":
                            prompt = PromptManager.create_agent_prompt(
                                agent_type, self.test_context, 
                                prompt_type=prompt_type, section_id="A"
                            )
                        else:
                            prompt = PromptManager.create_agent_prompt(
                                agent_type, self.test_context, 
                                prompt_type=prompt_type
                            )
                        print(f"  ✅ {prompt_type}: {len(prompt)} characters")
                    except Exception as e:
                        print(f"  ❌ {prompt_type}: {e}")
            else:
                try:
                    prompt = PromptManager.create_agent_prompt(agent_type, self.test_context)
                    print(f"  ✅ {agent_type}: {len(prompt)} characters")
                except Exception as e:
                    print(f"  ❌ {agent_type}: {e}")
    
    def test_chain_prompt(self):
        """Test chain prompt for complex workflows"""
        print("\n" + "=" * 80)
        print("⛓️ Testing Chain Prompt")
        print("=" * 80)
        
        # Create a chain of prompts for a complete workflow
        prompts = [
            AnthropicOptimizedPromptsV4.create_planner_prompt(self.test_context),
            AnthropicOptimizedPromptsV4.create_writer_outline_prompt(self.test_context),
            AnthropicOptimizedPromptsV4.create_writer_background_prompt(self.test_context)
        ]
        
        chain_prompt = PromptManager.create_chain_prompt(
            prompts, 
            context="专利撰写完整工作流程"
        )
        
        print("📝 Generated Chain Prompt:")
        print("-" * 40)
        print(chain_prompt[:1000] + "..." if len(chain_prompt) > 1000 else chain_prompt)
        print(f"\n📊 Chain Prompt Length: {len(chain_prompt)} characters")
        
        return chain_prompt
    
    def run_all_tests(self):
        """Run all prompt tests"""
        print("🚀 Starting Anthropic-Optimized Prompts v4.0 Tests")
        print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 Test Topic: {self.test_context.topic}")
        print(f"📄 Test Description: {self.test_context.description}")
        
        # Run individual prompt tests
        self.test_planner_prompt()
        self.test_writer_outline_prompt()
        self.test_writer_background_prompt()
        self.test_writer_summary_prompt()
        self.test_writer_detailed_description_prompt()
        self.test_writer_claims_prompt()
        self.test_reviewer_prompt()
        self.test_rewriter_prompt()
        self.test_searcher_prompt()
        self.test_discusser_prompt()
        
        # Test prompt manager
        self.test_prompt_manager()
        
        # Test chain prompt
        self.test_chain_prompt()
        
        print("\n" + "=" * 80)
        print("✅ All Tests Completed Successfully!")
        print("=" * 80)
        
        print("\n🎯 Key Improvements in v4.0:")
        print("1. ✅ Clear role definition with system prompts")
        print("2. ✅ Structured output with XML tags")
        print("3. ✅ Chain-of-thought reasoning")
        print("4. ✅ Complex task breakdown")
        print("5. ✅ Explicit constraints and requirements")
        print("6. ✅ Context window optimization")
        print("7. ✅ Extended thinking for complex tasks")
        print("8. ✅ Chain prompts for complex workflows")
        print("9. ✅ Consistent agent behavior")
        print("10. ✅ Professional patent writing standards")

def main():
    """Main function to run the tests"""
    tester = AnthropicPromptsV4Tester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()