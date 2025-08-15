#!/usr/bin/env python3
"""
Test script to verify DuckDuckGo search functionality in the fallback system
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

async def test_duckduckgo_search():
    """Test the DuckDuckGo search functionality"""
    
    try:
        from patent_agent_demo.openai_client import OpenAIClient
        print("✅ OpenAIClient imported successfully")
    except Exception as e:
        print(f"❌ Failed to import OpenAIClient: {e}")
        return False
    
    try:
        # Initialize client
        client = OpenAIClient()
        print("✅ OpenAIClient initialized successfully")
        
        # Check if GLM fallback is available
        if client.glm_client:
            print("✅ GLM fallback client is available")
        else:
            print("⚠️  GLM fallback client is not available")
            return False
        
        # Test DuckDuckGo search directly
        print("\n🧪 Testing DuckDuckGo search functionality...")
        
        result = await client._search_with_duckduckgo(
            "证据图增强的检索增强RAG系统",
            ["evidence", "graph", "RAG", "retrieval"],
            5
        )
        
        print(f"✅ DuckDuckGo search successful!")
        print(f"📝 Found {len(result)} results")
        
        for i, item in enumerate(result):
            print(f"  {i+1}. {item.title} (Score: {item.relevance_score})")
            print(f"     {item.abstract[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ DuckDuckGo search test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DuckDuckGo Search Test")
    print("=" * 50)
    
    success = asyncio.run(test_duckduckgo_search())
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)