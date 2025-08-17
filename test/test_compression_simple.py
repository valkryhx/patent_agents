#!/usr/bin/env python3
"""
Simple Compression Test
Test the compression agent directly
"""

import asyncio
import httpx
import json

async def test_compression_agent():
    """Test compression agent directly"""
    print("🧪 Testing Compression Agent Directly")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        # Test compression agent with sample data
        compression_request = {
            "task_id": "test_compression",
            "workflow_id": "test_workflow",
            "stage_name": "compression_before_drafting",
            "topic": "Test Patent Topic",
            "description": "Test patent description",
            "previous_results": {
                "planning": {
                    "result": {
                        "strategy": {
                            "topic": "Test Patent Topic",
                            "key_innovation_areas": ["Area 1", "Area 2", "Area 3"],
                            "novelty_score": 8.5,
                            "patentability_assessment": "Strong"
                        }
                    }
                },
                "search": {
                    "result": {
                        "search_results": {
                            "results": [
                                {"patent_id": "US123", "title": "Test Patent 1"},
                                {"patent_id": "US456", "title": "Test Patent 2"}
                            ]
                        }
                    }
                },
                "discussion": {
                    "result": {
                        "innovations": ["Innovation 1", "Innovation 2"],
                        "technical_insights": ["Insight 1", "Insight 2"]
                    }
                }
            },
            "context": {
                "compression_target": "early_stages",
                "stages_to_compress": ["planning", "search", "discussion"],
                "compression_purpose": "prepare_for_drafting",
                "preserve_elements": ["core_strategy", "key_insights", "critical_findings"]
            }
        }
        
        try:
            print("📤 Sending compression request...")
            response = await client.post(
                "http://localhost:8000/agents/compressor/execute",
                json=compression_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Compression agent responded successfully")
                
                # Check compression result
                compression_result = result.get("result", {})
                compression_summary = compression_result.get("compression_summary", {})
                
                print(f"📊 Original size: {compression_summary.get('original_size', 0)}")
                print(f"📊 Compressed size: {compression_summary.get('compressed_size', 0)}")
                print(f"📊 Compression ratio: {compression_summary.get('compression_ratio', 0)}%")
                
                # Check preserved elements
                preserved_elements = compression_result.get("preserved_elements", {})
                print(f"✅ Preserved elements: {list(preserved_elements.keys())}")
                
                # Check compressed context
                compressed_context = compression_result.get("compressed_context", {})
                print(f"✅ Compressed context keys: {list(compressed_context.keys())}")
                
                return True
            else:
                print(f"❌ Compression agent failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing compression agent: {str(e)}")
            return False

async def test_workflow_with_compression():
    """Test workflow with compression"""
    print(f"\n🧪 Testing Workflow with Compression")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        # Start a simple workflow
        workflow_request = {
            "topic": "Simple Test Patent",
            "description": "A simple test patent for compression testing",
            "workflow_type": "enhanced"
        }
        
        try:
            print("📋 Starting workflow...")
            response = await client.post(
                "http://localhost:8000/coordinator/workflow/start",
                json=workflow_request,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ Workflow started: {workflow_id}")
                
                # Monitor workflow
                for i in range(15):
                    await asyncio.sleep(1)
                    
                    status_response = await client.get(
                        f"http://localhost:8000/coordinator/workflow/{workflow_id}/status",
                        timeout=5.0
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        print(f"📈 Progress: {status['progress']:.1f}% - Status: {status['status']}")
                        
                        # Check for compression stages
                        compression_stages = [stage for stage in status['stages'] if stage['name'].startswith('compression_before_')]
                        if compression_stages:
                            print(f"🗜️ Compression stages detected: {[s['name'] for s in compression_stages]}")
                        
                        if status['status'] in ['completed', 'failed']:
                            print(f"🏁 Workflow {status['status']}")
                            break
                    else:
                        print(f"❌ Failed to get status: {status_response.status_code}")
                
                return True
            else:
                print(f"❌ Failed to start workflow: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing workflow: {str(e)}")
            return False

async def main():
    """Main test function"""
    print("🧪 Simple Compression Tests")
    print("=" * 50)
    
    # Test 1: Direct compression agent
    success1 = await test_compression_agent()
    
    # Test 2: Workflow with compression
    success2 = await test_workflow_with_compression()
    
    if success1 and success2:
        print("\n✅ All compression tests passed!")
    else:
        print("\n❌ Some compression tests failed!")

if __name__ == "__main__":
    asyncio.run(main())