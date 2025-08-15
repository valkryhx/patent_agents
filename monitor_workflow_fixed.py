#!/usr/bin/env python3
"""
监控修复后的专利撰写工作流执行情况
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# 添加patent_agent_demo到路径
sys.path.append('patent_agent_demo')

async def monitor_workflow():
    """监控工作流执行情况"""
    print("🔍 监控修复后的专利撰写工作流...")
    print("=" * 60)
    print("💡 这次应该不会因为GLM并发限制而卡住了")
    print("=" * 60)
    
    try:
        from patent_agent_demo.message_bus import MessageBusBroker
        
        # 创建消息总线
        message_bus = MessageBusBroker()
        
        # 检查日志文件
        log_file = "patent_workflow.log"
        
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n⏰ [{current_time}] 检查工作流状态...")
            
            # 检查日志文件
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if lines:
                            # 显示最后10行日志
                            print("📋 最新日志:")
                            for line in lines[-10:]:
                                line = line.strip()
                                if line:
                                    print(f"   {line}")
                            
                            # 检查是否有错误或卡住的情况
                            last_line = lines[-1] if lines else ""
                            if "GLM API call completed successfully" in last_line:
                                print("✅ GLM API调用成功完成！")
                            elif "GLM API call" in last_line and "timeout" in last_line:
                                print("⚠️  GLM API调用超时")
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
            
            # 检查消息总线状态
            try:
                agent_count = len(message_bus.agents)
                print(f"🤖 已注册Agent数量: {agent_count}")
                
                if agent_count > 0:
                    print("📊 Agent状态:")
                    for agent_name in message_bus.agents:
                        print(f"   - {agent_name}")
            except Exception as e:
                print(f"❌ 检查消息总线状态失败: {e}")
            
            print(f"\n⏳ 等待10秒后再次检查...")
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 监控已停止")
    except Exception as e:
        print(f"❌ 监控过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(monitor_workflow())
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")