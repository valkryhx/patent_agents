#!/usr/bin/env python3
"""
测试GLM API状态
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def test_glm():
    """测试GLM API状态"""
    
    try:
        from patent_agent_demo.glm_client import GLMA2AClient
        
        print("🔍 测试GLM API状态...")
        
        client = GLMA2AClient()
        response = await client._generate_response('测试GLM API是否可用')
        
        print(f"✅ GLM API测试成功，响应长度: {len(response)}")
        print(f"📝 响应内容: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ GLM API测试失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_glm())
    if success:
        print("✅ GLM API可用")
        sys.exit(0)
    else:
        print("❌ GLM API不可用")
        sys.exit(1)