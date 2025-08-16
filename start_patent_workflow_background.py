#!/usr/bin/env python3
"""
后台启动专利撰写流程并设置定期进度检查
"""
import asyncio
import os
import sys
import time
import subprocess
import signal
from datetime import datetime
import threading

# 添加项目路径
sys.path.append('patent_agent_demo')

async def run_patent_workflow():
    """在后台运行专利撰写流程"""
    print("🚀 启动专利撰写流程...")
    
    # 设置环境变量
    os.environ["PATENT_TOPIC"] = "以证据图增强的rag系统"
    os.environ["PATENT_DESC"] = "一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统"
    
    # 启动工作流进程
    process = subprocess.Popen([
        sys.executable, "run_patent_workflow.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print(f"📋 工作流进程已启动 (PID: {process.pid})")
    print(f"📝 专利主题: {os.environ.get('PATENT_TOPIC')}")
    print(f"📄 专利描述: {os.environ.get('PATENT_DESC')}")
    
    return process

async def monitor_progress_loop():
    """每10分钟检查一次进度"""
    print("📊 启动进度监控 (每10分钟检查一次)")
    
    check_count = 0
    while True:
        try:
            check_count += 1
            print(f"\n{'='*80}")
            print(f"🔍 第 {check_count} 次进度检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            
            # 运行进度检查脚本
            result = subprocess.run([
                sys.executable, "monitor_progress_10min.py"
            ], capture_output=True, text=True, timeout=300)  # 5分钟超时
            
            if result.returncode == 0:
                print("✅ 进度检查完成")
                if "工作流状态: 已完成" in result.stdout:
                    print("🎉 专利撰写工作流已完成！")
                    break
            else:
                print(f"⚠️ 进度检查出现错误: {result.stderr}")
            
            print(f"⏰ 等待10分钟后进行下一次检查...")
            await asyncio.sleep(600)  # 10分钟
            
        except subprocess.TimeoutExpired:
            print("⏰ 进度检查超时，继续监控...")
            await asyncio.sleep(600)
        except Exception as e:
            print(f"❌ 监控过程中出现错误: {e}")
            await asyncio.sleep(600)

def signal_handler(signum, frame):
    """处理中断信号"""
    print(f"\n🛑 收到中断信号，正在停止所有进程...")
    sys.exit(0)

async def main():
    """主函数"""
    print("🚀 专利撰写流程后台启动器")
    print("="*80)
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动专利撰写流程
        workflow_process = await run_patent_workflow()
        
        # 等待一下让工作流启动
        await asyncio.sleep(5)
        
        # 启动进度监控
        await monitor_progress_loop()
        
        # 工作流完成后清理
        if workflow_process.poll() is None:
            print("🔄 正在停止工作流进程...")
            workflow_process.terminate()
            try:
                workflow_process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                workflow_process.kill()
        
        print("✅ 所有进程已停止")
        
    except KeyboardInterrupt:
        print(f"\n🛑 用户中断，正在停止...")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        print("👋 程序结束")

if __name__ == "__main__":
    asyncio.run(main())