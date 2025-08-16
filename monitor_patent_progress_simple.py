#!/usr/bin/env python3
"""
简化的专利撰写进度监控脚本
Simple patent writing progress monitor
"""

import os
import time
from datetime import datetime

def check_progress():
    """检查专利撰写进度"""
    print(f"\n{'='*80}")
    print(f"📊 进度检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # 检查输出目录
    output_dir = "/workspace/output"
    if not os.path.exists(output_dir):
        print("❌ 输出目录不存在")
        return False
    
    # 获取所有专利文件
    patent_files = [f for f in os.listdir(output_dir) if f.startswith("multi_parameter_tool_patent_")]
    
    if not patent_files:
        print("❌ 没有找到专利文件")
        return False
    
    # 按修改时间排序，获取最新的文件
    patent_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
    latest_file = patent_files[0]
    file_path = os.path.join(output_dir, latest_file)
    
    print(f"📁 最新专利文件: {latest_file}")
    print(f"🕒 最后修改时间: {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📄 文件大小: {os.path.getsize(file_path)} bytes")
    
    # 检查文件内容
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 分析专利完成度
        sections = {
            "技术领域": "技术领域" in content,
            "背景技术": "背景技术" in content,
            "发明内容": "发明内容" in content,
            "具体实施方式": "具体实施方式" in content,
            "权利要求书": "权利要求书" in content,
            "摘要": "摘要" in content
        }
        
        completed_sections = [section for section, exists in sections.items() if exists]
        total_sections = len(sections)
        progress_percent = (len(completed_sections) / total_sections) * 100
        
        print(f"\n✅ 已完成的章节:")
        for i, section in enumerate(completed_sections, 1):
            print(f"   {i}. {section}")
        
        print(f"\n📊 专利完成度: {progress_percent:.1f}% ({len(completed_sections)}/{total_sections})")
        
        # 检查内容质量
        word_count = len(content.split())
        print(f"📝 专利字数: {word_count:,} 字")
        
        if word_count > 5000:
            print("🎉 专利内容已基本完成！")
            return True
        else:
            print("⏳ 专利撰写仍在进行中...")
            return False
            
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始监控专利撰写进度 (每5分钟检查一次)")
    print("按 Ctrl+C 停止监控")
    
    check_count = 0
    while True:
        try:
            check_count += 1
            print(f"\n{'='*80}")
            print(f"🔍 第 {check_count} 次检查")
            print(f"{'='*80}")
            
            # 检查进度
            is_completed = check_progress()
            
            if is_completed:
                print(f"\n🎉 专利撰写已完成！")
                print(f"📁 最终结果保存在: /workspace/output/")
                break
            
            print(f"\n⏰ 等待5分钟后进行下一次检查...")
            print(f"下次检查时间: {datetime.fromtimestamp(time.time() + 300).strftime('%H:%M:%S')}")
            
            # 等待5分钟
            time.sleep(300)  # 5分钟 = 300秒
            
        except KeyboardInterrupt:
            print(f"\n🛑 用户停止监控")
            break
        except Exception as e:
            print(f"\n❌ 监控过程中出现错误: {e}")
            print(f"⏰ 5分钟后重试...")
            time.sleep(300)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 程序已停止")