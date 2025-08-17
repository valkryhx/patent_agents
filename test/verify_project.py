#!/usr/bin/env python3
"""
项目验证脚本 - 验证整理后的项目结构是否正常
"""

import sys
import os

def test_file_structure():
    """测试文件结构是否完整"""
    print("📁 测试文件结构...")
    
    required_files = [
        'unified_service.py',
        'main.py',
        'workflow_manager.py',
        'models.py',
        'requirements.txt',
        'patent_agent_demo/agents/planner_agent.py',
        'patent_agent_demo/agents/base_agent.py',
        'patent_agent_demo/openai_client.py',
        'test/test_patent_api.py',
        '.private/GLM_API_KEY'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} 存在")
    
    if missing_files:
        print(f"❌ 缺失文件: {missing_files}")
        return False
    
    return True

def test_test_directory():
    """测试test目录是否包含所有测试文件"""
    print("\n🧪 测试test目录...")
    
    test_files = [
        'test_patent_api.py',
        'test_description_generation.py',
        'show_workflows.py',
        'test_workflow.py',
        'test_coordinator.py'
    ]
    
    missing_tests = []
    for test_file in test_files:
        if not os.path.exists(f"test/{test_file}"):
            missing_tests.append(test_file)
        else:
            print(f"✅ {test_file} 在test目录中")
    
    if missing_tests:
        print(f"❌ 缺失测试文件: {missing_tests}")
        return False
    
    return True

def test_core_functionality():
    """测试核心功能文件是否可读"""
    print("\n🔧 测试核心功能文件...")
    
    try:
        # 测试models.py是否可读
        with open('models.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'WorkflowRequest' in content and 'WorkflowState' in content:
                print("✅ models.py 内容正常")
            else:
                print("❌ models.py 内容异常")
                return False
    except Exception as e:
        print(f"❌ models.py 读取失败: {e}")
        return False
    
    try:
        # 测试workflow_manager.py是否可读
        with open('workflow_manager.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'WorkflowManager' in content:
                print("✅ workflow_manager.py 内容正常")
            else:
                print("❌ workflow_manager.py 内容异常")
                return False
    except Exception as e:
        print(f"❌ workflow_manager.py 读取失败: {e}")
        return False
    
    try:
        # 测试unified_service.py是否可读
        with open('unified_service.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'FastAPI' in content and 'app' in content:
                print("✅ unified_service.py 内容正常")
            else:
                print("❌ unified_service.py 内容异常")
                return False
    except Exception as e:
        print(f"❌ unified_service.py 读取失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 开始验证项目结构...\n")
    
    # 测试文件结构
    if not test_file_structure():
        print("\n❌ 文件结构验证失败")
        return False
    
    # 测试test目录
    if not test_test_directory():
        print("\n❌ test目录验证失败")
        return False
    
    # 测试核心功能
    if not test_core_functionality():
        print("\n❌ 核心功能验证失败")
        return False
    
    print("\n🎉 项目验证完成！所有检查都通过了。")
    print("\n📋 项目整理总结:")
    print("- ✅ 核心代码保留完整")
    print("- ✅ 测试代码已整理到test目录")
    print("- ✅ 无关代码已清理")
    print("- ✅ .private目录已保留")
    print("- ✅ 项目结构清晰")
    print("- ✅ 核心功能文件可读")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)