#!/usr/bin/env python3
"""
Test script for Description Generation Logic
Tests the automatic description generation from topic using AI model
"""

import asyncio
import sys
import os

# Add the patent_agent_demo directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def test_ai_description_generation():
    """Test the AI-based description generation functionality"""
    print("🧪 Testing AI-Based Description Generation")
    print("=" * 50)
    
    try:
        # Import and test OpenAIClient
        from openai_client import OpenAIClient
        
        print("🔧 Initializing OpenAI Client...")
        client = OpenAIClient()
        
        # Test topics
        test_topics = [
            "量子计算",
            "区块链技术",
            "人工智能系统",
            "物联网平台",
            "云计算架构"
        ]
        
        for topic in test_topics:
            print(f"\n🔍 Testing topic: {topic}")
            print("-" * 30)
            
            try:
                # Build prompt
                prompt = f"""
请为以下专利主题生成一个详细的技术描述，要求：

1. 描述要专业、准确，体现技术深度
2. 包含主要技术特点、技术优势和应用领域
3. 语言要符合专利文档的规范
4. 长度控制在200-300字左右

专利主题：{topic}

请生成详细的技术描述：
"""
                
                print(f"   📝 Sending prompt to AI model...")
                
                # Generate description using AI model
                description = await client._generate_response(prompt)
                
                if description and len(description.strip()) > 50:
                    print(f"✅ Generated description ({len(description)} chars):")
                    print(f"   {description[:200]}...")
                else:
                    print(f"❌ Failed to generate description or too short")
                    print(f"   Raw response: {description}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print(f"\n✅ AI-based description generation test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the correct directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

async def test_specific_topic():
    """Test a specific topic in detail"""
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        print(f"\n🔍 Detailed test for topic: {topic}")
        print("=" * 50)
        
        try:
            from openai_client import OpenAIClient
            
            client = OpenAIClient()
            
            prompt = f"""
请为以下专利主题生成一个详细的技术描述，要求：

1. 描述要专业、准确，体现技术深度
2. 包含主要技术特点、技术优势和应用领域
3. 语言要符合专利文档的规范
4. 长度控制在200-300字左右

专利主题：{topic}

请生成详细的技术描述：
"""
            
            print(f"📝 Sending prompt to AI model...")
            description = await client._generate_response(prompt)
            
            if description:
                print(f"\n🔧 Generated description:")
                print(f"   {description}")
            else:
                print(f"❌ Failed to generate description")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """Main test function"""
    if len(sys.argv) > 1:
        await test_specific_topic()
    else:
        await test_ai_description_generation()

if __name__ == "__main__":
    asyncio.run(main())