#!/usr/bin/env python3
"""
测试智能体日志频率修改
验证心跳检测和循环日志的频率是否已调整
"""

import asyncio
import os
import time
from patent_agent_demo.patent_agent_system import PatentAgentSystem
from patent_agent_demo.logging_utils import setup_root_file_logging

async def test_logging_frequency():
    """测试智能体日志频率"""
    print("🧪 开始测试智能体日志频率修改...")

    # 设置日志
    setup_root_file_logging()

    # 创建系统实例（测试模式）
    system = PatentAgentSystem(test_mode=True)

    try:
        # 启动系统
        print("🚀 启动专利智能体系统...")
        await system.start()

        # 等待系统初始化
        await asyncio.sleep(5)

        # 监控日志文件变化
        log_dir = os.path.join("output", "logs")
        print(f"📁 监控日志目录: {log_dir}")

        if os.path.exists(log_dir):
            log_files = os.listdir(log_dir)
            print(f"✅ 日志目录存在，包含 {len(log_files)} 个文件:")
            
            # 记录初始文件大小
            initial_sizes = {}
            for log_file in log_files:
                if log_file.endswith("_agent.log"):
                    file_path = os.path.join(log_dir, log_file)
                    initial_sizes[log_file] = os.path.getsize(file_path)
                    print(f"   📄 {log_file} (初始大小: {initial_sizes[log_file]} 字节)")

            # 监控60秒，检查日志增长情况
            print("\n⏰ 开始60秒监控，检查日志频率...")
            start_time = time.time()
            
            while time.time() - start_time < 60:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # 每10秒检查一次日志增长
                if int(elapsed) % 10 == 0 and elapsed > 0:
                    print(f"\n📊 第 {int(elapsed)} 秒 - 日志状态:")
                    
                    for log_file in log_files:
                        if log_file.endswith("_agent.log"):
                            file_path = os.path.join(log_dir, log_file)
                            current_size = os.path.getsize(file_path)
                            growth = current_size - initial_sizes[log_file]
                            
                            print(f"   📄 {log_file}: 增长 {growth} 字节")
                            
                            # 显示最后几行日志
                            if growth > 0:
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        lines = f.readlines()
                                        if lines:
                                            last_lines = lines[-3:]  # 最后3行
                                            print(f"      最新日志:")
                                            for line in last_lines:
                                                print(f"        {line.strip()}")
                                except Exception as e:
                                    print(f"      读取日志失败: {e}")
                
                await asyncio.sleep(1)

            print("\n✅ 60秒监控完成")
            
            # 最终统计
            print("\n📈 最终统计:")
            for log_file in log_files:
                if log_file.endswith("_agent.log"):
                    file_path = os.path.join(log_dir, log_file)
                    final_size = os.path.getsize(file_path)
                    total_growth = final_size - initial_sizes[log_file]
                    print(f"   📄 {log_file}: 总增长 {total_growth} 字节")

        else:
            print("❌ 日志目录不存在")

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 停止系统
        print("🛑 停止系统...")
        await system.stop()

    print("✅ 智能体日志频率测试完成")

if __name__ == "__main__":
    asyncio.run(test_logging_frequency())