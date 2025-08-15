#!/usr/bin/env python3
"""
每10分钟检查一次专利撰写进度并汇报
"""
import asyncio
import os
import sys
import time
from datetime import datetime
import glob
import subprocess
sys.path.append('patent_agent_demo')

async def check_progress():
    """检查撰写进度"""
    print(f"\n{'='*80}")
    print(f"📊 进度检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # 检查输出目录
    output_dir = "output/progress"
    if not os.path.exists(output_dir):
        print("❌ 输出目录不存在")
        return False
    
    # 获取所有进度目录
    progress_dirs = glob.glob(f"{output_dir}/*")
    if not progress_dirs:
        print("❌ 没有找到进度目录")
        return False
    
    # 按修改时间排序，获取最新的目录
    progress_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_dir = progress_dirs[0]
    dir_name = os.path.basename(latest_dir)
    
    print(f"📁 最新进度目录: {dir_name}")
    print(f"🕒 最后修改时间: {datetime.fromtimestamp(os.path.getmtime(latest_dir)).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查目录内容
    files = os.listdir(latest_dir)
    print(f"📄 生成的文件数量: {len(files)}")
    
    # 分析已完成的阶段
    completed_stages = []
    if "00_title_abstract.md" in files:
        completed_stages.append("策略制定 (planner_agent)")
    if "01_outline.md" in files:
        completed_stages.append("大纲生成 (writer_agent)")
    if "02_background.md" in files:
        completed_stages.append("背景技术撰写")
    if "03_invention.md" in files:
        completed_stages.append("发明内容撰写")
    if "04_implementation.md" in files:
        completed_stages.append("具体实施方式撰写")
    if "05_claims.md" in files:
        completed_stages.append("权利要求书撰写")
    if "06_drawings.md" in files:
        completed_stages.append("附图说明撰写")
    if "07_review.md" in files:
        completed_stages.append("审查 (reviewer_agent)")
    if "08_final.md" in files:
        completed_stages.append("最终版本 (rewriter_agent)")
    
    print(f"\n✅ 已完成的阶段:")
    for i, stage in enumerate(completed_stages, 1):
        print(f"   {i}. {stage}")
    
    # 计算进度百分比
    total_stages = 8
    progress_percent = (len(completed_stages) / total_stages) * 100
    print(f"\n📊 总体进度: {progress_percent:.1f}% ({len(completed_stages)}/{total_stages})")
    
    # 检查是否有新文件生成
    print(f"\n📄 当前文件列表:")
    for file in sorted(files):
        file_path = os.path.join(latest_dir, file)
        file_size = os.path.getsize(file_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        print(f"   📄 {file} ({file_size} bytes) - {mod_time.strftime('%H:%M:%S')}")
    
    # 检查工作流是否还在运行
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'run_patent_workflow.py' in result.stdout:
            print(f"\n🔄 工作流状态: 正在运行")
            return False  # 继续监控
        else:
            print(f"\n✅ 工作流状态: 已完成")
            return True   # 停止监控
    except Exception as e:
        print(f"\n⚠️  无法检查进程状态: {e}")
        return False
    
    return False

async def monitor_progress():
    """每10分钟监控一次进度"""
    print("🚀 开始监控专利撰写进度 (每10分钟检查一次)")
    print("按 Ctrl+C 停止监控")
    
    check_count = 0
    while True:
        try:
            check_count += 1
            print(f"\n{'='*80}")
            print(f"🔍 第 {check_count} 次检查")
            print(f"{'='*80}")
            
            # 检查进度
            is_completed = await check_progress()
            
            if is_completed:
                print(f"\n🎉 专利撰写工作流已完成！")
                print(f"📁 最终结果保存在: output/progress/")
                break
            
            print(f"\n⏰ 等待10分钟后进行下一次检查...")
            print(f"下次检查时间: {(datetime.now().timestamp() + 600):.0f}")
            
            # 等待10分钟
            await asyncio.sleep(600)  # 10分钟 = 600秒
            
        except KeyboardInterrupt:
            print(f"\n🛑 用户停止监控")
            break
        except Exception as e:
            print(f"\n❌ 监控过程中出现错误: {e}")
            print(f"⏰ 10分钟后重试...")
            await asyncio.sleep(600)

if __name__ == "__main__":
    try:
        asyncio.run(monitor_progress())
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")