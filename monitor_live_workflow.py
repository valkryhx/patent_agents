#!/usr/bin/env python3
"""
实时监控当前工作流执行进度
"""

import asyncio
import os
import sys
import time
from datetime import datetime
import glob
import subprocess

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def monitor_live_workflow():
    """实时监控工作流执行进度"""
    print("🔍 实时监控工作流执行进度...")
    print("=" * 60)
    print("💡 查看当前工作流执行到哪个agent环节")
    print("=" * 60)
    
    try:
        from patent_agent_demo.message_bus import MessageBusBroker
        
        # 创建消息总线
        message_bus = MessageBusBroker()
        
        # 检查输出目录
        output_dir = "output/progress"
        
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n⏰ [{current_time}] 检查工作流状态...")
            
            # 1. 检查输出目录和文件
            if os.path.exists(output_dir):
                try:
                    # 查找最新的进度目录
                    progress_dirs = glob.glob(f"{output_dir}/*")
                    if progress_dirs:
                        # 按创建时间排序，找到最新的
                        progress_dirs.sort(key=os.path.getctime, reverse=True)
                        latest_dir = progress_dirs[0]
                        print(f"📁 最新进度目录: {os.path.basename(latest_dir)}")
                        
                        # 检查目录内容
                        files = os.listdir(latest_dir)
                        if files:
                            print("📄 已生成的文件:")
                            for file in sorted(files):
                                file_path = os.path.join(latest_dir, file)
                                file_size = os.path.getsize(file_path)
                                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                                print(f"   - {file} ({file_size} bytes, {mtime.strftime('%H:%M:%S')})")
                                
                                # 分析文件名来判断当前阶段
                                if "01_strategy" in file:
                                    print("   🎯 当前阶段: 策略制定 (planner_agent)")
                                elif "02_background" in file:
                                    print("   📚 当前阶段: 背景技术 (writer_agent)")
                                elif "03_summary" in file:
                                    print("   📋 当前阶段: 发明内容 (writer_agent)")
                                elif "04_claims" in file:
                                    print("   ⚖️  当前阶段: 权利要求 (writer_agent)")
                                elif "05_desc" in file:
                                    print("   📝 当前阶段: 具体实施方式 (writer_agent)")
                                elif "06_claims" in file:
                                    print("   ⚖️  当前阶段: 权利要求书 (writer_agent)")
                                elif "07_drawings" in file:
                                    print("   🎨 当前阶段: 附图说明 (writer_agent)")
                                elif "08_review" in file:
                                    print("   🔍 当前阶段: 审查 (reviewer_agent)")
                                elif "09_rewrite" in file:
                                    print("   ✏️  当前阶段: 重写 (rewriter_agent)")
                        else:
                            print("📄 目录为空，等待文件生成...")
                    else:
                        print("📁 没有找到进度目录")
                except Exception as e:
                    print(f"❌ 检查输出目录失败: {e}")
            else:
                print("📁 输出目录不存在")
            
            # 2. 检查工作流进程状态
            try:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                python_processes = [line for line in result.stdout.split('\n') if 'python' in line and 'run_patent_workflow' in line]
                if python_processes:
                    print("🔄 工作流进程状态:")
                    for proc in python_processes:
                        print(f"   {proc}")
                else:
                    print("🔄 未找到工作流进程")
            except Exception as e:
                print(f"❌ 检查进程状态失败: {e}")
            
            # 3. 检查消息总线状态
            try:
                agent_count = len(message_bus.agents)
                print(f"🤖 已注册Agent数量: {agent_count}")
                
                if agent_count > 0:
                    print("📊 Agent状态:")
                    for agent_name in message_bus.agents:
                        print(f"   - {agent_name}")
            except Exception as e:
                print(f"❌ 检查消息总线状态失败: {e}")
            
            # 4. 检查是否有日志文件
            log_files = glob.glob("*.log")
            if log_files:
                print("📋 日志文件:")
                for log_file in log_files:
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            if lines:
                                # 显示最后5行日志
                                print(f"   {log_file} (最后5行):")
                                for line in lines[-5:]:
                                    line = line.strip()
                                    if line:
                                        print(f"     {line}")
                    except Exception as e:
                        print(f"     ❌ 读取失败: {e}")
            else:
                print("📋 没有找到日志文件")
            
            print(f"\n⏳ 等待20秒后再次检查...")
            await asyncio.sleep(20)
            
    except KeyboardInterrupt:
        print("\n🛑 监控已停止")
    except Exception as e:
        print(f"❌ 监控过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(monitor_live_workflow())
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")