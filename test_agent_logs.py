#!/usr/bin/env python3
"""
测试智能体独立日志功能
验证每个智能体是否都有独立的日志文件和详细的日志记录
"""

import asyncio
import os
import time
from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.logging_utils import setup_root_file_logging

async def test_agent_logs():
    """测试智能体日志功能"""
    print("🧪 开始测试智能体独立日志功能...")
    
    # 设置日志
    setup_root_file_logging()
    
    # 创建系统实例（测试模式）
    system = PatentAgentSystem(test_mode=True)
    
    try:
        # 启动系统
        print("🚀 启动专利智能体系统...")
        await system.start()
        
        # 等待系统初始化
        await asyncio.sleep(3)
        
        # 检查日志文件是否创建
        log_dir = os.path.join("output", "logs")
        print(f"📁 检查日志目录: {log_dir}")
        
        if os.path.exists(log_dir):
            log_files = os.listdir(log_dir)
            print(f"✅ 日志目录存在，包含 {len(log_files)} 个文件:")
            for log_file in log_files:
                file_path = os.path.join(log_dir, log_file)
                file_size = os.path.getsize(file_path)
                print(f"   📄 {log_file} ({file_size} 字节)")
                
                # 显示日志文件的前几行
                if file_size > 0:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"   📝 前3行内容:")
                        for i, line in enumerate(lines[:3]):
                            print(f"      {i+1}: {line.strip()}")
        else:
            print("❌ 日志目录不存在")
        
        # 测试发送一个简单任务给协调器
        print("🔧 测试协调器任务执行...")
        if system.coordinator:
            result = await system.coordinator.execute_task({
                "type": "get_workflow_summary",
                "test": True
            })
            print(f"✅ 协调器任务执行结果: {result.success}")
        
        # 等待一段时间让日志写入
        await asyncio.sleep(2)
        
        # 再次检查日志文件
        print("\n📊 任务执行后的日志状态:")
        if os.path.exists(log_dir):
            log_files = os.listdir(log_dir)
            for log_file in log_files:
                file_path = os.path.join(log_dir, log_file)
                file_size = os.path.getsize(file_path)
                print(f"   📄 {log_file} ({file_size} 字节)")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 停止系统
        print("🛑 停止系统...")
        await system.stop()
        
    print("✅ 智能体日志功能测试完成")

if __name__ == "__main__":
    asyncio.run(test_agent_logs())