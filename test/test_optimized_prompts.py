#!/usr/bin/env python3
"""
Test script for optimized prompts v2.0
Demonstrates the improved prompt engineering following Anthropic's best practices
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimized_prompts_v2 import OptimizedPromptsV2, PromptManager, PromptContext

class OptimizedPromptTester:
    """Test class for optimized prompts"""
    
    def __init__(self):
        self.test_topic = "以证据图增强的rag系统"
        self.test_description = "一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统"
        self.test_results = {
            "analysis": {
                "novelty_score": 8.5,
                "inventive_step_score": 8.0,
                "technical_feasibility": "高",
                "market_potential": "高"
            },
            "prior_art": [
                "传统RAG系统",
                "图神经网络技术",
                "证据推理方法"
            ]
        }
    
    def create_test_context(self) -> PromptContext:
        """Create test context"""
        return PromptManager.create_context(
            topic=self.test_topic,
            description=self.test_description,
            previous_results=self.test_results
        )
    
    def test_planner_prompt(self):
        """Test planner strategy prompt"""
        print("=" * 80)
        print("🧠 TESTING PLANNER STRATEGY PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        prompt = OptimizedPromptsV2.get_planner_strategy_prompt(context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_writer_outline_prompt(self):
        """Test writer outline prompt"""
        print("=" * 80)
        print("📋 TESTING WRITER OUTLINE PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        prompt = OptimizedPromptsV2.get_writer_outline_prompt(context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_writer_background_prompt(self):
        """Test writer background prompt"""
        print("=" * 80)
        print("🔬 TESTING WRITER BACKGROUND PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        prompt = OptimizedPromptsV2.get_writer_background_prompt(context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_writer_summary_prompt(self):
        """Test writer summary prompt"""
        print("=" * 80)
        print("💡 TESTING WRITER SUMMARY PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        prompt = OptimizedPromptsV2.get_writer_summary_prompt(context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_writer_implementation_prompt(self):
        """Test writer implementation prompt"""
        print("=" * 80)
        print("⚙️ TESTING WRITER IMPLEMENTATION PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        prompt = OptimizedPromptsV2.get_writer_implementation_prompt(
            context, "A", "数据获取与证据构建"
        )
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_writer_claims_prompt(self):
        """Test writer claims prompt"""
        print("=" * 80)
        print("⚖️ TESTING WRITER CLAIMS PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        prompt = OptimizedPromptsV2.get_writer_claims_prompt(context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_reviewer_quality_prompt(self):
        """Test reviewer quality prompt"""
        print("=" * 80)
        print("🔍 TESTING REVIEWER QUALITY PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        prompt = OptimizedPromptsV2.get_reviewer_quality_prompt(context)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_rewriter_optimization_prompt(self):
        """Test rewriter optimization prompt"""
        print("=" * 80)
        print("✨ TESTING REWRITER OPTIMIZATION PROMPT")
        print("=" * 80)
        
        context = self.create_test_context()
        feedback = "技术描述需要更详细，创新点需要更突出，权利要求需要更明确"
        prompt = OptimizedPromptsV2.get_rewriter_optimization_prompt(context, feedback)
        
        print("📝 Generated Prompt:")
        print("-" * 40)
        print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
        print("\n" + "=" * 80)
        
        return prompt
    
    def test_system_roles(self):
        """Test system role definitions"""
        print("=" * 80)
        print("🎭 TESTING SYSTEM ROLE DEFINITIONS")
        print("=" * 80)
        
        for agent_type in ["planner", "writer", "reviewer", "rewriter"]:
            print(f"\n🤖 {agent_type.upper()} AGENT ROLE:")
            print("-" * 40)
            role = PromptManager.get_system_role(agent_type)
            print(role[:500] + "..." if len(role) > 500 else role)
        
        print("\n" + "=" * 80)
    
    def test_prompt_combination(self):
        """Test prompt combination"""
        print("=" * 80)
        print("🔗 TESTING PROMPT COMBINATION")
        print("=" * 80)
        
        context = self.create_test_context()
        task_prompt = OptimizedPromptsV2.get_writer_outline_prompt(context)
        system_role = PromptManager.get_system_role("writer")
        combined_prompt = PromptManager.combine_prompts(system_role, task_prompt)
        
        print("📝 Combined Prompt Length:", len(combined_prompt))
        print("📝 System Role Length:", len(system_role))
        print("📝 Task Prompt Length:", len(task_prompt))
        print("✅ Prompt combination successful!")
        
        print("\n" + "=" * 80)
    
    def compare_with_old_prompts(self):
        """Compare with old prompt style"""
        print("=" * 80)
        print("📊 COMPARISON WITH OLD PROMPT STYLE")
        print("=" * 80)
        
        # Old style prompt (simplified)
        old_prompt = f"""
创建专利撰写大纲（中文），主题：{self.test_topic}
- 章节：技术领域、背景技术、发明内容、具体实施方式、权利要求书、附图说明
- 每章给出3-5个要点
- 预计字数：每章≥800字
仅输出分章要点清单。
"""
        
        # New style prompt
        context = self.create_test_context()
        new_prompt = OptimizedPromptsV2.get_writer_outline_prompt(context)
        
        print("📝 OLD STYLE PROMPT:")
        print("-" * 40)
        print(old_prompt)
        print(f"📏 Length: {len(old_prompt)} characters")
        
        print("\n📝 NEW STYLE PROMPT:")
        print("-" * 40)
        print(new_prompt[:800] + "..." if len(new_prompt) > 800 else new_prompt)
        print(f"📏 Length: {len(new_prompt)} characters")
        
        print(f"\n📈 IMPROVEMENTS:")
        print(f"   - Length increase: {len(new_prompt) - len(old_prompt)} characters")
        print(f"   - Structure: XML tags for consistent output")
        print(f"   - Context: Comprehensive context provision")
        print(f"   - Reasoning: Chain-of-thought process")
        print(f"   - Constraints: Explicit requirements")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 STARTING OPTIMIZED PROMPTS V2.0 TESTS")
        print("=" * 80)
        
        try:
            # Test system roles
            self.test_system_roles()
            
            # Test individual prompts
            self.test_planner_prompt()
            self.test_writer_outline_prompt()
            self.test_writer_background_prompt()
            self.test_writer_summary_prompt()
            self.test_writer_implementation_prompt()
            self.test_writer_claims_prompt()
            self.test_reviewer_quality_prompt()
            self.test_rewriter_optimization_prompt()
            
            # Test prompt combination
            self.test_prompt_combination()
            
            # Compare with old style
            self.compare_with_old_prompts()
            
            print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print("🎉 Optimized prompts v2.0 are ready for use!")
            print("📚 See PROMPT_OPTIMIZATION_GUIDE.md for detailed usage instructions")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    tester = OptimizedPromptTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()