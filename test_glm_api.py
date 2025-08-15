#!/usr/bin/env python3
"""
测试GLM API是否正常工作
"""

import asyncio
import os
import sys

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def test_glm_api():
    """测试GLM API连接"""
    try:
        print("🔍 测试GLM API连接...")
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ GLM API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_patent_analysis():
    """测试专利分析功能"""
    try:
        print("\n🔍 测试专利分析功能...")
        
        from patent_agent_demo.glm_client import GLMA2AClient
        
        api_key = "f80163335a3749509ae1ecfa79f3f343.cNIEBuoFBDhkDpqZ"
        client = GLMA2AClient(api_key)
        
        topic = "证据图增强的RAG系统"
        description = "构建证据图以提升RAG可验证性与准确性"
        
        print(f"📝 分析主题: {topic}")
        print(f"📝 描述: {description}")
        print("⏳ 等待分析结果...")
        
        analysis = await client.analyze_patent_topic(topic, description)
        
        print(f"✅ 专利分析完成:")
        print(f"   - 新颖性评分: {analysis.novelty_score}/10")
        print(f"   - 创造性评分: {analysis.inventive_step_score}/10")
        print(f"   - 工业适用性: {analysis.industrial_applicability}")
        print(f"   - 专利性评估: {analysis.patentability_assessment}")
        
        return True
        
    except Exception as e:
        print(f"❌ 专利分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始GLM API测试...")
    print("=" * 50)
    
    # 测试1: 基本API连接
    test1_success = await test_glm_api()
    
    # 测试2: 专利分析功能
    test2_success = await test_patent_analysis()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   - 基本API连接: {'✅ 成功' if test1_success else '❌ 失败'}")
    print(f"   - 专利分析功能: {'✅ 成功' if test2_success else '❌ 失败'}")
    
    if test1_success and test2_success:
        print("🎉 所有测试通过！GLM API工作正常")
        return True
    else:
        print("⚠️  部分测试失败，需要检查API配置")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)