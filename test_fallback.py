#!/usr/bin/env python3
"""
Test script to verify OpenAI client fallback to GLM functionality
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append('.')

async def test_fallback():
    """Test the fallback functionality"""
    
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
        
        # Test a simple call that should trigger fallback
        print("\n🧪 Testing fallback functionality...")
        
        # This should fail with OpenAI (quota exceeded) and fall back to GLM
        result = await client.analyze_patent_topic(
            "Test Topic", 
            "Test Description"
        )
        
        print(f"✅ Fallback test successful!")
        print(f"📝 Result type: {type(result)}")
        print(f"📝 Novelty score: {getattr(result, 'novelty_score', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OpenAI Client Fallback Test")
    print("=" * 50)
    
    success = asyncio.run(test_fallback())
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)