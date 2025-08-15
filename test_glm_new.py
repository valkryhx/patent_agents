#!/usr/bin/env python3
"""
测试修改后的GLM客户端
"""

import asyncio
import os
import sys

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def test_glm_new():
    """测试修改后的GLM客户端"""
    try:
        print("🔍 测试修改后的GLM客户端...")
        
        # 设置API key
        api_key = "f80163335a3749509ae1ecfa79f3f343.cNIEBuoFBDhkDpqZ"
        os.environ["ZHIPUAI_API_KEY"] = api_key
        
        print(f"✅ API Key已设置: {api_key[:20]}...")
        
        # 导入GLM客户端
        from patent_agent_demo.glm_client import GLMA2AClient
        
        print("✅ GLM客户端导入成功")
        
        # 创建客户端
        client = GLMA2AClient(api_key)
        print("✅ GLM客户端创建成功")
        
        # 测试简单对话
        print("🔄 测试简单对话...")
        test_prompt = "请用一句话回答：什么是人工智能？"
        
        print(f"📝 发送请求: {test_prompt}")
        print("⏳ 等待响应...")
        
        response = await client._generate_response(test_prompt)
        
        print(f"✅ 收到响应: {response}")
        print("🎉 GLM API测试成功！")
        
        # 测试专利分析
        print("\n🔍 测试专利分析功能...")
        topic = "证据图增强的RAG系统"
        description = "构建证据图以提升RAG可验证性与准确性"
        
        print(f"📝 分析主题: {topic}")
        analysis = await client.analyze_patent_topic(topic, description)
        
        print(f"✅ 专利分析完成:")
        print(f"   - 新颖性评分: {analysis.novelty_score}/10")
        print(f"   - 创造性评分: {analysis.inventive_step_score}/10")
        print(f"   - 工业适用性: {analysis.industrial_applicability}")
        print(f"   - 专利性评估: {analysis.patentability_assessment}")
        
        # 测试专利撰写
        print("\n🔍 测试专利撰写功能...")
        draft = await client.generate_patent_draft(topic, description, analysis)
        
        print(f"✅ 专利撰写完成:")
        print(f"   - 标题: {draft.title}")
        print(f"   - 摘要: {draft.abstract[:100]}...")
        print(f"   - 权利要求数量: {len(draft.claims)}")
        print(f"   - 技术示意图数量: {len(draft.technical_diagrams)}")
        
        return True
        
    except Exception as e:
        print(f"❌ GLM客户端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试修改后的GLM客户端...")
    print("=" * 50)
    
    success = await test_glm_new()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！修改后的GLM客户端工作正常")
    else:
        print("⚠️  测试失败，需要检查代码")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)