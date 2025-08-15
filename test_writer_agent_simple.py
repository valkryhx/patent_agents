#!/usr/bin/env python3
"""
简化的Writer Agent测试，诊断工作流卡住的问题
"""
import asyncio
import os
import sys
import time
from datetime import datetime
sys.path.append('patent_agent_demo')

async def test_writer_agent_initialization():
    """测试Writer Agent的初始化"""
    print("🧪 测试1: Writer Agent初始化")
    
    try:
        # 导入必要的模块
        from patent_agent_demo.agents.writer_agent import WriterAgent
        from patent_agent_demo.message_bus import message_bus_config
        
        print("✅ 模块导入成功")
        
        # 检查消息总线配置
        print(f"📡 消息总线状态: {message_bus_config.broker.get_status() if message_bus_config.broker else '未初始化'}")
        
        # 创建Writer Agent (使用正确的构造函数)
        writer = WriterAgent()
        print(f"✅ Writer Agent创建成功: {writer.name}")
        print(f"✅ 能力列表: {writer.capabilities}")
        
        return True
        
    except Exception as e:
        print(f"❌ Writer Agent初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_glm_api_status():
    """测试GLM API状态"""
    print("\n🧪 测试2: GLM API状态检查")
    
    try:
        from patent_agent_demo.glm_client import GLMA2AClient
        
        # 创建GLM客户端
        glm_client = GLMA2AClient()
        print("✅ GLM客户端创建成功")
        
        # 检查API密钥
        api_key = os.getenv('GLM_API_KEY')
        if api_key:
            print(f"✅ API密钥已配置: {api_key[:10]}...")
        else:
            print("❌ API密钥未配置")
            return False
        
        # 测试简单的API调用
        test_prompt = "测试"
        print(f"📝 测试提示: {test_prompt}")
        
        start_time = time.time()
        try:
            response = await glm_client.analyze_patent_topic("测试", test_prompt)
            end_time = time.time()
            
            print(f"✅ GLM API调用成功，耗时: {end_time - start_time:.2f}秒")
            print(f"📄 响应内容长度: {len(str(response))} 字符")
            return True
            
        except Exception as api_error:
            if "429" in str(api_error):
                print(f"⚠️  GLM API限流 (HTTP 429): {api_error}")
                print("💡 这是导致工作流卡住的原因之一")
                return False
            else:
                print(f"❌ GLM API调用失败: {api_error}")
                return False
        
    except Exception as e:
        print(f"❌ GLM API状态检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_message_bus():
    """测试消息总线状态"""
    print("\n🧪 测试3: 消息总线状态")
    
    try:
        from patent_agent_demo.message_bus import message_bus_config
        
        if not message_bus_config.broker:
            print("❌ 消息总线未初始化")
            return False
        
        broker = message_bus_config.broker
        status = broker.get_status()
        print(f"✅ 消息总线状态: {status}")
        
        # 检查已注册的agent
        registered_agents = broker.get_registered_agents()
        print(f"📋 已注册的Agent: {registered_agents}")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息总线状态检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_stage():
    """测试工作流阶段状态"""
    print("\n🧪 测试4: 工作流阶段状态")
    
    try:
        # 检查输出目录
        output_dir = "output/progress"
        if not os.path.exists(output_dir):
            print("❌ 输出目录不存在")
            return False
        
        # 获取最新的进度目录
        import glob
        progress_dirs = glob.glob(f"{output_dir}/*")
        if not progress_dirs:
            print("❌ 没有找到进度目录")
            return False
        
        # 按修改时间排序
        progress_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_dir = progress_dirs[0]
        
        print(f"📁 最新进度目录: {os.path.basename(latest_dir)}")
        
        # 检查文件状态
        files = os.listdir(latest_dir)
        print(f"📄 文件数量: {len(files)}")
        
        for file in sorted(files):
            file_path = os.path.join(latest_dir, file)
            file_size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"   📄 {file} ({file_size} bytes) - {mod_time.strftime('%H:%M:%S')}")
        
        # 检查是否有新文件生成
        current_time = time.time()
        latest_file_time = max(os.path.getmtime(os.path.join(latest_dir, f)) for f in files)
        time_diff = current_time - latest_file_time
        
        print(f"⏰ 距离最后文件生成: {time_diff:.0f}秒")
        
        if time_diff > 900:  # 15分钟
            print("⚠️  文件生成已停滞超过15分钟，工作流可能卡住")
            return False
        else:
            print("✅ 文件生成时间正常")
            return True
        
    except Exception as e:
        print(f"❌ 工作流阶段状态检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Writer Agent简化诊断测试")
    print(f"⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    tests = [
        ("初始化", test_writer_agent_initialization),
        ("GLM API状态", test_glm_api_status),
        ("消息总线", test_message_bus),
        ("工作流阶段", test_workflow_stage)
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
        print("🎉 所有测试通过！系统工作正常")
    else:
        print("⚠️  部分测试失败，已识别问题")
        print("\n🔍 问题分析:")
        if not results[1][1]:  # GLM API状态测试失败
            print("   • GLM API限流 (HTTP 429) - 这是导致工作流卡住的主要原因")
        if not results[2][1]:  # 消息总线测试失败
            print("   • 消息总线问题 - 可能影响agent间通信")
        if not results[3][1]:  # 工作流阶段测试失败
            print("   • 工作流停滞 - 文件生成已停止")
    
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