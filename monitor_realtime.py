#!/usr/bin/env python3
"""
实时监控专利撰写进度，检查新文件产生和内容变化
"""
import os
import sys
import time
import glob
import subprocess
from datetime import datetime
from pathlib import Path

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

def check_glm_api_status():
    """检查GLM API状态"""
    try:
        # 检查GLM API密钥
        glm_key_file = "patent_agent_demo/glm_api_key"
        if os.path.exists(glm_key_file):
            with open(glm_key_file, 'r') as f:
                key_content = f.read().strip()
                if key_content.startswith('GLM_API_KEY='):
                    print(f"✅ GLM API密钥已配置")
                    return True
                else:
                    print(f"⚠️ GLM API密钥格式可能有问题")
                    return False
        else:
            print(f"❌ GLM API密钥文件不存在")
            return False
    except Exception as e:
        print(f"❌ 检查GLM API状态时出错: {e}")
        return False

def check_workflow_process():
    """检查工作流进程状态"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'run_patent_workflow.py' in result.stdout:
            print(f"🔄 工作流进程正在运行")
            return True
        else:
            print(f"❌ 工作流进程未运行")
            return False
    except Exception as e:
        print(f"⚠️ 无法检查进程状态: {e}")
        return False

def monitor_progress():
    """监控进度"""
    print("🚀 开始实时监控专利撰写进度")
    print("按 Ctrl+C 停止监控")
    print("="*80)
    
    # 初始化文件状态
    last_file_states = {}
    check_count = 0
    
    while True:
        try:
            check_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"\n{'='*80}")
            print(f"🔍 第 {check_count} 次检查 - {current_time}")
            print(f"{'='*80}")
            
            # 检查GLM API状态
            print(f"\n🔑 GLM API状态:")
            glm_ok = check_glm_api_status()
            
            # 检查工作流进程
            print(f"\n🔄 工作流进程状态:")
            process_ok = check_workflow_process()
            
            # 检查最新进度目录
            latest_dir = get_latest_progress_dir()
            if latest_dir:
                dir_name = os.path.basename(latest_dir)
                print(f"\n📁 最新进度目录: {dir_name}")
                
                # 检查目录中的文件
                files = os.listdir(latest_dir)
                print(f"📄 文件数量: {len(files)}")
                
                # 检查文件变化
                current_file_states = {}
                new_files = []
                modified_files = []
                
                for file in sorted(files):
                    file_path = os.path.join(latest_dir, file)
                    file_info = get_file_info(file_path)
                    
                    if file_info:
                        current_file_states[file] = file_info
                        
                        if file not in last_file_states:
                            new_files.append(file)
                        elif last_file_states[file]['size'] != file_info['size'] or \
                             last_file_states[file]['mtime'] != file_info['mtime']:
                            modified_files.append(file)
                
                # 显示新文件
                if new_files:
                    print(f"\n🆕 新生成的文件:")
                    for file in new_files:
                        info = current_file_states[file]
                        print(f"   📄 {file} ({info['size']} bytes) - {info['mtime_str']}")
                
                # 显示修改的文件
                if modified_files:
                    print(f"\n📝 修改的文件:")
                    for file in modified_files:
                        info = current_file_states[file]
                        old_info = last_file_states[file]
                        print(f"   📄 {file} ({old_info['size']} → {info['size']} bytes) - {info['mtime_str']}")
                
                # 显示所有文件状态
                if files:
                    print(f"\n📄 当前文件列表:")
                    for file in sorted(files):
                        info = current_file_states[file]
                        print(f"   📄 {file} ({info['size']} bytes) - {info['mtime_str']}")
                
                # 更新文件状态
                last_file_states = current_file_states
                
                # 分析进度
                stage_files = {
                    "00_title_abstract.md": "策略制定",
                    "01_outline.md": "大纲生成",
                    "02_background.md": "背景技术",
                    "03_invention.md": "发明内容",
                    "04_implementation.md": "具体实施方式",
                    "05_claims.md": "权利要求书",
                    "06_drawings.md": "附图说明",
                    "07_review.md": "审查",
                    "08_final.md": "最终版本"
                }
                
                completed_stages = [stage for file, stage in stage_files.items() if file in files]
                progress_percent = (len(completed_stages) / len(stage_files)) * 100
                
                print(f"\n📊 进度分析:")
                print(f"   已完成阶段: {len(completed_stages)}/{len(stage_files)}")
                print(f"   进度百分比: {progress_percent:.1f}%")
                if completed_stages:
                    print(f"   已完成: {', '.join(completed_stages)}")
                
                # 检查是否卡住
                if not new_files and not modified_files and process_ok:
                    print(f"\n⚠️ 警告: 没有检测到新文件生成或修改，可能卡住了")
                    print(f"   建议检查GLM API并发限制或网络连接")
                
            else:
                print(f"\n❌ 没有找到进度目录")
            
            print(f"\n⏰ 等待30秒后进行下一次检查...")
            time.sleep(30)  # 30秒检查一次
            
        except KeyboardInterrupt:
            print(f"\n🛑 用户停止监控")
            break
        except Exception as e:
            print(f"\n❌ 监控过程中出现错误: {e}")
            print(f"⏰ 30秒后重试...")
            time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_progress()
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")