#!/usr/bin/env python3
"""
每15分钟自动汇报专利撰写进度，持续运行直到所有阶段结束
"""
import os
import sys
import time
import glob
import subprocess
from datetime import datetime, timedelta

def get_latest_progress_dir():
    """获取最新的进度目录"""
    output_dir = "output/progress"
    if not os.path.exists(output_dir):
        return None
    
    progress_dirs = glob.glob(f"{output_dir}/*")
    if not progress_dirs:
        return None
    
    # 按修改时间排序，获取最新的目录
    progress_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return progress_dirs[0]

def get_file_info(file_path):
    """获取文件信息"""
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    return {
        'size': stat.st_size,
        'mtime': stat.st_mtime,
        'mtime_str': datetime.fromtimestamp(stat.st_mtime).strftime('%H:%M:%S')
    }

def check_workflow_process():
    """检查工作流进程状态"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'run_patent_workflow.py' in result.stdout:
            return True
        else:
            return False
    except Exception:
        return False

def analyze_progress(files):
    """分析撰写进度"""
    stage_files = {
        "00_title_abstract.md": "策略制定",
        "01_outline.md": "大纲生成", 
        "02_background.md": "背景技术",
        "03_summary.md": "发明内容",
        "04_implementation.md": "具体实施方式",
        "05_claims.md": "权利要求书",
        "06_drawings.md": "附图说明",
        "07_review.md": "审查阶段",
        "08_final.md": "最终版本"
    }
    
    completed_stages = []
    for file, stage_name in stage_files.items():
        if file in files:
            completed_stages.append(stage_name)
    
    total_stages = len(stage_files)
    progress_percent = (len(completed_stages) / total_stages) * 100
    
    return {
        'completed': completed_stages,
        'total': total_stages,
        'percent': progress_percent,
        'remaining': total_stages - len(completed_stages)
    }

def generate_report():
    """生成进度报告"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n{'='*100}")
    print(f"📊 专利撰写进度报告 - {current_time}")
    print(f"{'='*100}")
    
    # 检查工作流进程
    process_running = check_workflow_process()
    print(f"🔄 工作流状态: {'正在运行' if process_running else '已停止'}")
    
    # 检查最新进度目录
    latest_dir = get_latest_progress_dir()
    if not latest_dir:
        print("❌ 没有找到进度目录")
        return False
    
    dir_name = os.path.basename(latest_dir)
    print(f"📁 当前工作目录: {dir_name}")
    
    # 检查文件
    files = os.listdir(latest_dir)
    print(f"📄 已生成文件数量: {len(files)}")
    
    # 分析进度
    progress = analyze_progress(files)
    print(f"\n📊 撰写进度: {progress['percent']:.1f}% ({len(progress['completed'])}/{progress['total']})")
    print(f"⏳ 剩余阶段: {progress['remaining']} 个")
    
    # 显示已完成阶段
    if progress['completed']:
        print(f"\n✅ 已完成阶段:")
        for i, stage in enumerate(progress['completed'], 1):
            print(f"   {i}. {stage}")
    
    # 显示待完成阶段
    stage_files = {
        "00_title_abstract.md": "策略制定",
        "01_outline.md": "大纲生成", 
        "02_background.md": "背景技术",
        "03_summary.md": "发明内容",
        "04_implementation.md": "具体实施方式",
        "05_claims.md": "权利要求书",
        "06_drawings.md": "附图说明",
        "07_review.md": "审查阶段",
        "08_final.md": "最终版本"
    }
    
    remaining_stages = []
    for file, stage_name in stage_files.items():
        if file not in files:
            remaining_stages.append(stage_name)
    
    if remaining_stages:
        print(f"\n⏳ 待完成阶段:")
        for i, stage in enumerate(remaining_stages, 1):
            print(f"   {i}. {stage}")
    
    # 显示最新文件
    if files:
        print(f"\n📄 最新文件状态:")
        for file in sorted(files):
            file_path = os.path.join(latest_dir, file)
            file_info = get_file_info(file_path)
            if file_info:
                print(f"   📄 {file} ({file_info['size']} bytes) - {file_info['mtime_str']}")
    
    # 检查是否完成
    if progress['percent'] >= 100:
        print(f"\n🎉 恭喜！专利撰写工作流已完成！")
        print(f"📁 最终结果保存在: {latest_dir}")
        return True
    
    # 检查是否卡住
    if not process_running and progress['percent'] < 100:
        print(f"\n⚠️ 警告: 工作流已停止但未完成，可能出现了问题")
    
    return False

def main():
    """主函数"""
    print("🚀 启动专利撰写进度监控 (每15分钟汇报一次)")
    print("📋 专利主题: 以证据图增强的rag系统")
    print("⏰ 监控间隔: 15分钟")
    print("🛑 按 Ctrl+C 停止监控")
    print("="*100)
    
    check_count = 0
    start_time = datetime.now()
    
    while True:
        try:
            check_count += 1
            elapsed_time = datetime.now() - start_time
            
            print(f"\n{'='*100}")
            print(f"🔍 第 {check_count} 次检查 (运行时间: {elapsed_time})")
            print(f"{'='*100}")
            
            # 生成报告
            is_completed = generate_report()
            
            if is_completed:
                print(f"\n🎉 专利撰写工作流已完成！监控结束。")
                break
            
            # 计算下次检查时间
            next_check = datetime.now() + timedelta(minutes=15)
            print(f"\n⏰ 下次检查时间: {next_check.strftime('%H:%M:%S')}")
            print(f"⏳ 等待15分钟...")
            
            # 等待15分钟
            time.sleep(900)  # 15分钟 = 900秒
            
        except KeyboardInterrupt:
            print(f"\n🛑 用户停止监控")
            break
        except Exception as e:
            print(f"\n❌ 监控过程中出现错误: {e}")
            print(f"⏰ 15分钟后重试...")
            time.sleep(900)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")