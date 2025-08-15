#!/usr/bin/env python3
"""
测试GLM API是否已从限流中恢复
"""
import asyncio
import os
import sys
sys.path.append('patent_agent_demo')

async def test_glm_recovery():
    """测试GLM API是否已恢复"""
    try:
        from patent_agent_demo.glm_client import GLMA2AClient
        
        print("🧪 测试GLM API恢复状态")
        
        # 创建GLM客户端
        client = GLMA2AClient()
        print("✅ GLM客户端创建成功")
        
        # 检查API密钥
        api_key = os.getenv('GLM_API_KEY')
        if not api_key:
            print("❌ GLM_API_KEY环境变量未设置")
            return False
        
        print(f"✅ API密钥已配置: {api_key[:10]}...")
        
        # 测试API调用
        print("📝 测试API调用...")
        start_time = asyncio.get_event_loop().time()
        
        response = await client.analyze_patent_topic("测试", "测试")
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        print(f"✅ GLM API调用成功！")
        print(f"⏱️  响应时间: {duration:.2f}秒")
        print(f"📄 响应内容长度: {len(str(response))} 字符")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            print(f"❌ GLM API仍然限流中 (HTTP 429)")
            print("💡 需要等待更长时间让API恢复")
            return False
        elif "timeout" in error_str.lower():
            print(f"❌ GLM API调用超时")
            return False
        else:
            print(f"❌ GLM API调用失败: {e}")
            return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_glm_recovery())
        if success:
            print("\n🎉 GLM API已恢复，可以重新启动工作流！")
            sys.exit(0)
        else:
            print("\n⚠️  GLM API尚未恢复，需要继续等待")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中出现错误: {e}")
        sys.exit(1)