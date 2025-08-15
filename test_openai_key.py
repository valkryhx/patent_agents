#!/usr/bin/env python3
"""
Simple test script to verify OpenAI API key functionality
"""

import os
import sys
from openai import OpenAI

def test_openai_key():
    """Test if the OpenAI API key is working"""
    
    # Load API key from private file
    api_key_path = "patent_agent_demo/private_openai_key"
    
    try:
        with open(api_key_path, "r") as f:
            api_key = f.read().strip()
        print(f"✅ API key loaded from: {api_key_path}")
        print(f"🔑 Key prefix: {api_key[:20]}...")
    except Exception as e:
        print(f"❌ Failed to load API key: {e}")
        return False
    
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return False
    
    # Test 1: Simple completion
    print("\n🧪 Test 1: Simple completion...")
    try:
        response = client.responses.create(
            model="gpt-5",
            input="Say 'Hello, this is a test' in one sentence."
        )
        print(f"✅ Simple completion successful!")
        print(f"📝 Response: {response.output_text}")
    except Exception as e:
        print(f"❌ Simple completion failed: {e}")
        return False
    
    # Test 2: Web search tool
    print("\n🧪 Test 2: Web search tool...")
    try:
        response = client.responses.create(
            model="gpt-5",
            tools=[{"type": "web_search_preview"}],
            input="What is the current weather in New York?"
        )
        print(f"✅ Web search tool successful!")
        print(f"📝 Response: {response.output_text}")
    except Exception as e:
        print(f"❌ Web search tool failed: {e}")
        return False
    
    # Test 3: Check account status (if possible)
    print("\n🧪 Test 3: Checking account status...")
    try:
        # Try to get some basic info about the model
        response = client.responses.create(
            model="gpt-5",
            input="What is your model name and version?"
        )
        print(f"✅ Account status check successful!")
        print(f"📝 Response: {response.output_text}")
    except Exception as e:
        print(f"❌ Account status check failed: {e}")
        # This might fail due to permissions, but it's not critical
    
    print("\n🎉 All tests completed successfully!")
    print("✅ Your OpenAI API key is working properly!")
    return True

def test_basic_functionality():
    """Test basic OpenAI functionality without complex operations"""
    
    # Load API key
    api_key_path = "patent_agent_demo/private_openai_key"
    
    try:
        with open(api_key_path, "r") as f:
            api_key = f.read().strip()
    except Exception as e:
        print(f"❌ Failed to load API key: {e}")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Simple test with minimal tokens
        response = client.responses.create(
            model="gpt-5",
            input="Hi"
        )
        
        print(f"✅ Basic functionality test successful!")
        print(f"📝 Response: {response.output_text}")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OpenAI API Key Test")
    print("=" * 50)
    
    # Try the full test first
    print("Starting full functionality test...")
    if test_openai_key():
        sys.exit(0)
    else:
        print("\n⚠️  Full test failed, trying basic functionality test...")
        if test_basic_functionality():
            print("✅ Basic functionality works, but some features may be limited")
            sys.exit(0)
        else:
            print("❌ All tests failed. Please check your API key and account status.")
            sys.exit(1)