#!/usr/bin/env python3
"""
简单的DuckDuckGo测试
"""

import asyncio
import aiohttp
import json

async def test_duckduckgo():
    """测试DuckDuckGo API"""
    
    async with aiohttp.ClientSession() as session:
        # 测试英文查询
        print("=== 测试英文查询 ===")
        params = {
            "q": "artificial intelligence",
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        url = "https://api.duckduckgo.com/"
        
        async with session.get(url, params=params) as response:
            print(f"状态码: {response.status}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            text = await response.text()
            print(f"响应长度: {len(text)}")
            
            try:
                data = json.loads(text)
                print(f"JSON解析成功")
                print(f"Abstract: {data.get('Abstract', 'N/A')[:100]}...")
                print(f"RelatedTopics数量: {len(data.get('RelatedTopics', []))}")
                
                # 解析相关主题
                for i, topic in enumerate(data.get('RelatedTopics', [])[:3]):
                    if isinstance(topic, dict) and 'Text' in topic:
                        print(f"主题 {i+1}: {topic['Text']}")
                
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        
        print("\n=== 测试中文查询 ===")
        # 测试中文查询
        params = {
            "q": "人工智能",
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        async with session.get(url, params=params) as response:
            print(f"状态码: {response.status}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            text = await response.text()
            print(f"响应长度: {len(text)}")
            
            try:
                data = json.loads(text)
                print(f"JSON解析成功")
                print(f"Abstract: {data.get('Abstract', 'N/A')[:100]}...")
                print(f"RelatedTopics数量: {len(data.get('RelatedTopics', []))}")
                
                # 解析相关主题
                for i, topic in enumerate(data.get('RelatedTopics', [])[:3]):
                    if isinstance(topic, dict) and 'Text' in topic:
                        print(f"主题 {i+1}: {topic['Text']}")
                
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        
        print("\n=== 测试简单中文查询 ===")
        # 测试简单中文查询
        params = {
            "q": "算法",
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        async with session.get(url, params=params) as response:
            print(f"状态码: {response.status}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            text = await response.text()
            print(f"响应长度: {len(text)}")
            
            try:
                data = json.loads(text)
                print(f"JSON解析成功")
                print(f"Abstract: {data.get('Abstract', 'N/A')[:100]}...")
                print(f"RelatedTopics数量: {len(data.get('RelatedTopics', []))}")
                
                # 解析相关主题
                for i, topic in enumerate(data.get('RelatedTopics', [])[:3]):
                    if isinstance(topic, dict) and 'Text' in topic:
                        print(f"主题 {i+1}: {topic['Text']}")
                
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_duckduckgo())