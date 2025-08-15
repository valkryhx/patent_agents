#!/usr/bin/env python3
"""
测试GLM API的并发限制
"""

import asyncio
import os
import sys
import time

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def test_single_glm_call():
    """测试单个GLM调用"""
    try:
        print("🔍 测试单个GLM调用...")
        
        # 设置API key
        api_key = "f80163335a3749509ae1ecfa79f3f343.cNIEBuoFBDhkDpqZ"
        os.environ["ZHIPUAI_API_KEY"] = api_key
        
        from patent_agent_demo.glm_client import GLMA2AClient
        
        client = GLMA2AClient(api_key)
        
        start_time = time.time()
        print(f"⏰ 开始时间: {time.strftime('%H:%M:%S')}")
        
        # 测试简单对话
        test_prompt = "请用一句话回答：什么是人工智能？"
        print(f"📝 发送请求: {test_prompt}")
        
        response = await client._generate_response(test_prompt)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 收到响应: {response}")
        print(f"⏱️  耗时: {duration:.2f}秒")
        print(f"⏰ 结束时间: {time.strftime('%H:%M:%S')}")
        
        return True, duration
        
    except Exception as e:
        print(f"❌ 单个调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

async def test_concurrent_glm_calls():
    """测试并发GLM调用"""
    try:
        print("\n🔍 测试并发GLM调用...")
        
        api_key = "f80163335a3749509ae1ecfa79f3f343.cNIEBuoFBDhkDpqZ"
        os.environ["ZHIPUAI_API_KEY"] = api_key
        
        from patent_agent_demo.glm_client import GLMA2AClient
        
        client = GLMA2AClient(api_key)
        
        # 创建3个并发任务
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                test_concurrent_single_call(client, f"测试{i+1}")
            )
            tasks.append(task)
        
        print(f"🚀 启动3个并发任务...")
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
        print(f"✅ 成功: {success_count}/3")
        
        return success_count == 3
        
    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_concurrent_single_call(client, name):
    """单个并发调用的包装函数"""
    try:
        start_time = time.time()
        print(f"  📝 {name} 开始...")
        
        test_prompt = f"请用一句话回答：{name} - 什么是机器学习？"
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
    print("🚀 开始GLM并发测试...")
    print("=" * 60)
    
    # 测试1: 单个调用
    print("🔍 测试1: 单个GLM调用")
    single_success, single_duration = await test_single_glm_call()
    
    # 测试2: 并发调用
    print("\n🔍 测试2: 并发GLM调用")
    concurrent_success = await test_concurrent_glm_calls()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   - 单个调用: {'✅ 成功' if single_success else '❌ 失败'} (耗时: {single_duration:.2f}秒)")
    print(f"   - 并发调用: {'✅ 成功' if concurrent_success else '❌ 失败'}")
    
    if single_success and concurrent_success:
        print("🎉 所有测试通过！")
    elif single_success and not concurrent_success:
        print("⚠️  单个调用成功，但并发调用失败 - 可能是并发限制问题")
    else:
        print("❌ 测试失败，需要检查API配置")

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)