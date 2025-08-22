#!/usr/bin/env python3
"""
测试修复后的Writer Agent
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def test_fixed_writer_agent():
    """测试修复后的Writer Agent"""
    
    try:
        print("🔍 测试修复后的Writer Agent...")
        
        # 导入必要的组件
        from patent_agent_demo.agents.writer_agent_simple import WriterAgentSimple
        from patent_agent_demo.google_a2a_client import PatentAnalysis
        
        # 创建Writer Agent
        writer_agent = WriterAgentSimple(test_mode=False)
        await writer_agent.start()
        
        # 创建模拟的PatentAnalysis
        mock_analysis = PatentAnalysis(
            novelty_score=8.5,
            inventive_step_score=7.8,
            industrial_applicability=True,
            prior_art_analysis=[],
            claim_analysis={},
            technical_merit={},
            commercial_potential="Medium to High",
            patentability_assessment="Strong",
            recommendations=["Improve claim specificity", "Add more technical details"]
        )
        
        # 准备任务数据
        task_data = {
            "type": "patent_drafting",
            "topic": "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统",
            "previous_results": {
                "planning": {"strategy": mock_analysis},
                "search": {"search_results": mock_analysis},
                "discussion": {"core_strategy": mock_analysis, "search_context": mock_analysis}
            },
            "workflow_id": "test_fixed_writer",
            "test_mode": False
        }
        
        print("📋 开始执行Writer Agent任务...")
        
        # 执行任务
        result = await writer_agent.execute_task(task_data)
        
        print(f"✅ Writer Agent执行完成！")
        print(f"📊 执行结果: {result.success}")
        
        if result.success:
            print(f"📄 专利草稿生成成功！")
            data = result.data
            if "patent_draft" in data:
                patent_draft = data["patent_draft"]
                print(f"   - 标题: {getattr(patent_draft, 'title', 'N/A')}")
                print(f"   - 摘要: {getattr(patent_draft, 'abstract', 'N/A')[:100]}...")
                print(f"   - 权利要求数量: {len(getattr(patent_draft, 'claims', []))}")
                print(f"   - 详细描述长度: {len(getattr(patent_draft, 'detailed_description', ''))}")
                print(f"   - 背景技术长度: {len(getattr(patent_draft, 'background', ''))}")
                print(f"   - 发明内容长度: {len(getattr(patent_draft, 'summary', ''))}")
            else:
                print(f"⚠️ 没有找到patent_draft，完整数据: {data}")
        else:
            print(f"❌ Writer Agent执行失败: {result.error_message}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"📋 详细错误: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_writer_agent())
    if success:
        print("✅ Writer Agent修复测试成功")
        sys.exit(0)
    else:
        print("❌ Writer Agent修复测试失败")
        sys.exit(1)