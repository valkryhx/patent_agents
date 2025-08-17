#!/usr/bin/env python3
"""
GLM 4.5 Flash API 测试脚本
用于验证API key是否正常，以及API调用是否成功
"""

import os
import json
import asyncio
import urllib.request
from typing import Optional

# GLM API配置
GLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4/"
GLM_CHAT_COMPLETIONS = GLM_API_BASE + "chat/completions"
GLM_MODEL = "glm-4.5-flash"

def _load_glm_key() -> Optional[str]:
    """加载GLM API key"""
    # 环境变量优先级
    env_key = os.getenv("ZHIPUAI_API_KEY") or os.getenv("GLM_API_KEY")
    if env_key:
        return env_key.strip()
    
    # 从文件加载
    key_paths = [
        "/workspace/glm_api_key",
        "/workspace/.private/GLM_API_KEY",
        os.path.expanduser("~/.private/GLM_API_KEY"),
        "glm_api_key",
        ".private/GLM_API_KEY"
    ]
    
    for path in key_paths:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    # 支持多种格式
                    if "=" in content:
                        for line in content.splitlines():
                            if "=" in line:
                                k, v = line.split("=", 1)
                                k = k.strip().upper()
                                v = v.strip()
                                if k in ("GLM_API_KEY", "ZHIPUAI_API_KEY", "API_KEY") and v:
                                    return v
                    else:
                        # 原始key
                        return content
        except Exception as e:
            print(f"尝试加载 {path} 失败: {e}")
            continue
    
    return None

def test_glm_api_simple(api_key: str) -> bool:
    """测试GLM API简单调用"""
    try:
        payload = {
            "model": GLM_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个专业的AI助手"},
                {"role": "user", "content": "请简单回复'Hello World'"}
            ],
            "temperature": 0.1,
            "stream": False,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        print("🔄 正在测试GLM API...")
        print(f"📡 API地址: {GLM_CHAT_COMPLETIONS}")
        print(f"🤖 模型: {GLM_MODEL}")
        print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
        
        req = urllib.request.Request(
            GLM_CHAT_COMPLETIONS,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            
            print(f"✅ API调用成功!")
            print(f"📊 响应状态: {resp.status}")
            print(f"📄 响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 检查响应格式
            choices = data.get("choices") or []
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "")
                print(f"🤖 AI回复: {content}")
                return True
            else:
                print(f"⚠️ 响应格式异常: {data}")
                return False
                
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return False

def test_glm_api_patent(api_key: str) -> bool:
    """测试GLM API专利相关调用"""
    try:
        payload = {
            "model": GLM_MODEL,
            "messages": [
                {"role": "system", "content": "你是一个专业的专利分析师和专利撰写专家"},
                {"role": "user", "content": "请分析一下'基于语义理解的复杂函数参数智能推断与分层调用重试优化方法'这个专利主题的新颖性，用1-2句话简单回答。"}
            ],
            "temperature": 0.3,
            "stream": False,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        print("\n🔄 正在测试专利分析功能...")
        
        req = urllib.request.Request(
            GLM_CHAT_COMPLETIONS,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            
            print(f"✅ 专利分析API调用成功!")
            
            choices = data.get("choices") or []
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "")
                print(f"🤖 专利分析结果: {content}")
                return True
            else:
                print(f"⚠️ 专利分析响应格式异常: {data}")
                return False
                
    except Exception as e:
        print(f"❌ 专利分析API调用失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 GLM 4.5 Flash API 测试脚本")
    print("=" * 50)
    
    # 加载API key
    api_key = _load_glm_key()
    if not api_key:
        print("❌ 无法加载GLM API key")
        print("请确保以下任一方式可用:")
        print("1. 设置环境变量 ZHIPUAI_API_KEY 或 GLM_API_KEY")
        print("2. 在以下路径放置API key文件:")
        for path in ["/workspace/glm_api_key", "/workspace/.private/GLM_API_KEY", "~/.private/GLM_API_KEY"]:
            print(f"   - {path}")
        print("3. 在当前目录放置 glm_api_key 文件")
        return
    
    print(f"✅ 成功加载API key: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    # 测试简单API调用
    simple_test = test_glm_api_simple(api_key)
    if not simple_test:
        print("❌ 简单API测试失败，请检查API key和网络连接")
        return
    
    # 测试专利分析功能
    patent_test = test_glm_api_patent(api_key)
    if not patent_test:
        print("❌ 专利分析API测试失败")
        return
    
    print("\n🎉 所有测试通过！GLM 4.5 Flash API工作正常")
    print("✅ 简单对话功能正常")
    print("✅ 专利分析功能正常")
    print("✅ API key有效")
    print("✅ 网络连接正常")

if __name__ == "__main__":
    asyncio.run(main())