#!/usr/bin/env python3
"""
检查工作流程状态
"""

import os
import time
import glob

def check_workflow_status():
    """检查工作流程状态"""
    print("🔍 检查工作流程状态...")
    
    # 检查output目录
    output_dir = "./output"
    if os.path.exists(output_dir):
        print(f"✅ output目录存在: {output_dir}")
        
        # 检查是否有文件生成
        md_files = glob.glob(os.path.join(output_dir, "**/*.md"), recursive=True)
        if md_files:
            print(f"✅ 找到 {len(md_files)} 个markdown文件:")
            for file in md_files[:5]:  # 只显示前5个
                file_size = os.path.getsize(file)
                mtime = time.ctime(os.path.getmtime(file))
                print(f"   {file}: {file_size} 字节, 修改时间: {mtime}")
        else:
            print("⚠️ 未找到markdown文件")
    else:
        print("❌ output目录不存在")
    
    # 检查日志文件
    log_files = glob.glob("*.log")
    if log_files:
        print(f"\n📋 找到 {len(log_files)} 个日志文件:")
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    print(f"   {log_file}: {len(lines)} 行")
                    if lines:
                        print(f"      最后一行: {lines[-1].strip()}")
            except Exception as e:
                print(f"   {log_file}: 无法读取 - {e}")
    else:
        print("\n❌ 未找到日志文件")
    
    # 检查进程
    print("\n🔧 检查相关进程...")
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        python_processes = [line for line in lines if 'python3' in line and ('enhanced' in line or 'ultra' in line)]
        if python_processes:
            print(f"✅ 找到 {len(python_processes)} 个相关Python进程:")
            for proc in python_processes[:3]:  # 只显示前3个
                print(f"   {proc.strip()}")
        else:
            print("❌ 未找到相关Python进程")
    except Exception as e:
        print(f"❌ 无法检查进程: {e}")

if __name__ == "__main__":
    check_workflow_status()