#!/usr/bin/env python3
"""
测试GLM信号量并发控制
"""

import asyncio
import os
import sys
import time

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def test_glm_semaphore():
    """测试GLM信号量并发控制"""
    try:
        print("🔍 测试GLM信号量并发控制...")
        
        # 设置API key
        api_key = "f80163335a3749509ae1ecfa79f3f343.cNIEBuoFBDhkDpqZ"
        os.environ["ZHIPUAI_API_KEY"] = api_key
        
        from patent_agent_demo.glm_client import GLMA2AClient
        
        client = GLMA2AClient(api_key)
        
        # 创建5个并发任务
        tasks = []
        for i in range(5):
            task = asyncio.create_task(
                test_single_call_with_delay(client, f"任务{i+1}", i * 0.5)
            )
            tasks.append(task)
        
        print(f"🚀 启动5个并发任务...")
        start_time = time.time()
        print(f"⏰ 开始时间: {time.strftime('%H:%M:%S')}")
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        print(f"\n📊 并发测试结果:")
        print(f"⏱️  总耗时: {total_duration:.2f}秒")
        print(f"⏰ 结束时间: {time.strftime('%H:%M:%S')}")
        
        success_count = sum(1 for r in results if isinstance(r, tuple) and r[0])
        print(f"✅ 成功: {success_count}/5")
        
        return success_count == 5
        
    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_single_call_with_delay(client, name, delay):
    """单个调用的包装函数，带延迟"""
    try:
        # 添加延迟来模拟不同的启动时间
        await asyncio.sleep(delay)
        
        start_time = time.time()
        print(f"  📝 {name} 开始... (延迟: {delay}s)")
        
        test_prompt = f"请用一句话回答：{name} - 什么是深度学习？"
        response = await client._generate_response(test_prompt)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"  ✅ {name} 完成: {duration:.2f}秒")
        return True, duration
        
    except Exception as e:
        print(f"  ❌ {name} 失败: {e}")
        return False, 0

async def main():
    """主测试函数"""
    print("🚀 开始GLM信号量并发控制测试...")
    print("=" * 60)
    print("💡 这个测试会验证GLM客户端是否正确控制了并发数量")
    print("💡 GLM-4.5-flash只能支持2个并发请求")
    print("=" * 60)
    
    success = await test_glm_semaphore()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试通过！信号量并发控制工作正常")
        print("💡 现在GLM API调用不会因为并发限制而卡住了")
    else:
        print("❌ 测试失败，需要检查信号量实现")

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)