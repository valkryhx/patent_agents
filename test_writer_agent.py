#!/usr/bin/env python3
"""
测试writer agent的功能，诊断工作流卡住的问题
"""
import asyncio
import os
import sys
import time
from datetime import datetime
sys.path.append('patent_agent_demo')

from patent_agent_demo.agents.writer_agent import WriterAgent
from patent_agent_demo.agents.base_agent import MessageBusBroker
from patent_agent_demo.glm_client import GLMA2AClient

async def test_writer_agent_basic():
    """测试writer agent的基本功能"""
    print("🧪 测试1: Writer Agent基本功能")
    
    try:
        # 创建消息总线
        broker = MessageBusBroker()
        
        # 创建GLM客户端
        glm_client = GLMA2AClient()
        
        # 创建writer agent
        writer = WriterAgent(broker, glm_client)
        
        print(f"✅ Writer Agent创建成功: {writer.name}")
        print(f"✅ 消息总线状态: {broker.get_status()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Writer Agent基本功能测试失败: {e}")
        return False

async def test_writer_agent_glm_call():
    """测试writer agent的GLM调用功能"""
    print("\n🧪 测试2: Writer Agent GLM调用功能")
    
    try:
        # 创建GLM客户端
        glm_client = GLMA2AClient()
        
        # 测试简单的GLM调用
        test_prompt = "请简要描述证据图增强RAG系统的核心优势"
        print(f"📝 测试提示: {test_prompt}")
        
        start_time = time.time()
        response = await glm_client.analyze_patent_topic("证据图增强RAG系统", test_prompt)
        end_time = time.time()
        
        print(f"✅ GLM调用成功，耗时: {end_time - start_time:.2f}秒")
        print(f"📄 响应内容: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Writer Agent GLM调用测试失败: {e}")
        return False

async def test_writer_agent_content_generation():
    """测试writer agent的内容生成功能"""
    print("\n🧪 测试3: Writer Agent内容生成功能")
    
    try:
        # 创建消息总线
        broker = MessageBusBroker()
        
        # 创建GLM客户端
        glm_client = GLMA2AClient()
        
        # 创建writer agent
        writer = WriterAgent(broker, glm_client)
        
        # 模拟任务数据
        task_data = {
            "id": "test_content_generation",
            "type": "content_generation",
            "topic": "证据图增强的检索增强RAG系统",
            "outline": {
                "background": "传统RAG系统的局限性",
                "invention": "证据图增强方法",
                "implementation": "具体实现细节"
            }
        }
        
        print(f"📋 测试任务: {task_data['type']}")
        print(f"🎯 主题: {task_data['topic']}")
        
        # 测试内容生成
        start_time = time.time()
        result = await writer._execute_task(task_data)
        end_time = time.time()
        
        print(f"✅ 内容生成成功，耗时: {end_time - start_time:.2f}秒")
        print(f"📊 结果状态: {result.success}")
        print(f"📄 生成内容长度: {len(str(result.data))} 字符")
        
        return True
        
    except Exception as e:
        print(f"❌ Writer Agent内容生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_writer_agent_concurrent():
    """测试writer agent的并发处理能力"""
    print("\n🧪 测试4: Writer Agent并发处理能力")
    
    try:
        # 创建消息总线
        broker = MessageBusBroker()
        
        # 创建GLM客户端
        glm_client = GLMA2AClient()
        
        # 创建writer agent
        writer = WriterAgent(broker, glm_client)
        
        # 创建多个并发任务
        tasks = []
        for i in range(3):
            task_data = {
                "id": f"concurrent_test_{i}",
                "type": "content_generation",
                "topic": f"测试主题{i}",
                "section": f"测试章节{i}"
            }
            tasks.append(writer._execute_task(task_data))
        
        print(f"🚀 启动 {len(tasks)} 个并发任务...")
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        print(f"✅ 并发任务完成，总耗时: {end_time - start_time:.2f}秒")
        
        success_count = sum(1 for r in results if hasattr(r, 'success') and r.success)
        print(f"📊 成功任务数: {success_count}/{len(tasks)}")
        
        return success_count == len(tasks)
        
    except Exception as e:
        print(f"❌ Writer Agent并发处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_glm_concurrency_limit():
    """测试GLM并发限制"""
    print("\n🧪 测试5: GLM并发限制测试")
    
    try:
        # 创建GLM客户端
        glm_client = GLMA2AClient()
        
        # 创建多个并发GLM调用
        async def single_glm_call(name, delay=0):
            await asyncio.sleep(delay)
            start_time = time.time()
            response = await glm_client.analyze_patent_topic(f"测试主题{name}", f"测试提示{name}")
            end_time = time.time()
            return f"{name}: {end_time - start_time:.2f}s"
        
        print("🚀 启动5个并发GLM调用...")
        
        start_time = time.time()
        results = await asyncio.gather(
            single_glm_call("A"),
            single_glm_call("B"),
            single_glm_call("C"),
            single_glm_call("D"),
            single_glm_call("E")
        )
        end_time = time.time()
        
        print(f"✅ 并发GLM调用完成，总耗时: {end_time - start_time:.2f}秒")
        for result in results:
            print(f"   {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ GLM并发限制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Writer Agent诊断测试")
    print(f"⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    tests = [
        ("基本功能", test_writer_agent_basic),
        ("GLM调用", test_writer_agent_glm_call),
        ("内容生成", test_writer_agent_content_generation),
        ("并发处理", test_writer_agent_concurrent),
        ("GLM并发限制", test_glm_concurrency_limit)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"🧪 执行测试: {test_name}")
            print(f"{'='*60}")
            
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
                
        except Exception as e:
            print(f"💥 {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print(f"\n{'='*80}")
    print("📊 测试结果总结")
    print(f"{'='*80}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Writer Agent工作正常")
    else:
        print("⚠️  部分测试失败，需要进一步诊断")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中出现未预期错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)