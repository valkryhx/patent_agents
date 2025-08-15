#!/usr/bin/env python3
"""
详细监控专利撰写工作流执行过程
"""

import asyncio
import os
import sys
import time
from datetime import datetime
import glob

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def monitor_detailed():
    """详细监控工作流执行情况"""
    print("🔍 详细监控专利撰写工作流...")
    print("=" * 60)
    print("💡 实时监控工作流执行状态和进度")
    print("=" * 60)
    
    try:
        from patent_agent_demo.message_bus import MessageBusBroker
        
        # 创建消息总线
        message_bus = MessageBusBroker()
        
        # 检查日志文件
        log_file = "patent_workflow.log"
        
        # 检查输出目录
        output_dir = "output/progress"
        
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n⏰ [{current_time}] 详细检查工作流状态...")
            
            # 1. 检查日志文件
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            print("📋 最新日志 (最后20行):")
                            for line in lines[-20:]:
                                line = line.strip()
                                if line:
                                    print(f"   {line}")
                            
                            # 分析日志状态
                            last_line = lines[-1] if lines else ""
                            if "GLM API call completed successfully" in last_line:
                                print("✅ GLM API调用成功完成！")
                            elif "Creating development strategy" in last_line:
                                print("🚀 正在创建开发策略...")
                            elif "Development strategy created" in last_line:
                                print("✅ 开发策略创建完成！")
                            elif "Creating development phases" in last_line:
                                print("📋 正在创建开发阶段...")
                            elif "Development phases created" in last_line:
                                print("✅ 开发阶段创建完成！")
                            elif "Error" in last_line or "Exception" in last_line:
                                print("❌ 发现错误")
                            elif "completed" in last_line or "successfully" in last_line:
                                print("🎉 任务成功完成")
                        else:
                            print("📋 日志文件为空")
                except Exception as e:
                    print(f"❌ 读取日志文件失败: {e}")
            else:
                print("📋 日志文件不存在")
            
            # 2. 检查输出目录
            if os.path.exists(output_dir):
                try:
                    # 查找最新的进度目录
                    progress_dirs = glob.glob(f"{output_dir}/*")
                    if progress_dirs:
                        latest_dir = max(progress_dirs, key=os.path.getctime)
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
                        else:
                            print("📄 目录为空，等待文件生成...")
                    else:
                        print("📁 没有找到进度目录")
                except Exception as e:
                    print(f"❌ 检查输出目录失败: {e}")
            else:
                print("📁 输出目录不存在")
            
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
            
            # 4. 检查进程状态
            try:
                import subprocess
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
            
            print(f"\n⏳ 等待15秒后再次检查...")
            await asyncio.sleep(15)
            
    except KeyboardInterrupt:
        print("\n🛑 监控已停止")
    except Exception as e:
        print(f"❌ 监控过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(monitor_detailed())
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")