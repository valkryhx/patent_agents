#!/usr/bin/env python3
"""
Test Optional Compression Mechanism
Verifies that compression is only used when context size exceeds thresholds
"""

import asyncio
import httpx
import time
import json
from typing import Dict, Any

# Service URL (single port)
BASE_URL = "http://localhost:8000"

async def test_optional_compression_workflow():
    """Test workflow with optional compression verification"""
    print("🎯 Testing Optional Compression Mechanism")
    print("=" * 50)
    
    # Test data with specific topic and description
    workflow_request = {
        "topic": "基于智能分层推理的多参数工具自适应调用系统",
        "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。",
        "workflow_type": "enhanced"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Start workflow
            print("📋 Starting workflow with optional compression...")
            response = await client.post(
                f"{BASE_URL}/coordinator/workflow/start",
                json=workflow_request,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ Workflow started: {workflow_id}")
                
                # 2. Monitor workflow and verify compression usage
                print("📊 Monitoring workflow with compression verification...")
                stage_results = {}
                compression_used = False
                
                for i in range(30):  # Monitor for up to 30 iterations
                    await asyncio.sleep(1)  # Check every second
                    
                    status_response = await client.get(
                        f"{BASE_URL}/coordinator/workflow/{workflow_id}/status",
                        timeout=5.0
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        
                        print(f"📈 Progress: {status['progress']:.1f}% - Status: {status['status']}")
                        
                        # Check each completed stage for compression usage
                        for stage in status['stages']:
                            if stage['status'] == 'completed' and stage['name'] not in stage_results:
                                stage_results[stage['name']] = stage['result']
                                
                                # Check if this is a compression stage
                                if stage['name'].startswith('compression_before_'):
                                    compression_used = True
                                    await verify_compression_stage(stage['name'], stage['result'])
                                else:
                                    await verify_stage_with_compression_check(stage['name'], stage['result'], stage_results)
                        
                        # Check if completed
                        if status['status'] == 'completed':
                            print("🎉 Workflow completed! Verifying compression usage...")
                            await verify_final_compression_usage(stage_results, compression_used)
                            break
                        elif status['status'] == 'failed':
                            print("❌ Workflow failed!")
                            break
                    else:
                        print(f"❌ Failed to get status: {status_response.status_code}")
                        
            else:
                print(f"❌ Failed to start workflow: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error during workflow execution: {str(e)}")

async def verify_compression_stage(stage_name: str, stage_result: Dict[str, Any]):
    """Verify compression stage functionality"""
    print(f"\n🗜️ Verifying compression stage: {stage_name}")
    
    result_data = stage_result.get("result", {})
    
    # Check compression summary
    compression_summary = result_data.get("compression_summary", {})
    if compression_summary:
        original_size = compression_summary.get("original_size", 0)
        compressed_size = compression_summary.get("compressed_size", 0)
        compression_ratio = compression_summary.get("compression_ratio", 0)
        
        print(f"   📊 Original size: {original_size} characters")
        print(f"   📊 Compressed size: {compressed_size} characters")
        print(f"   📊 Compression ratio: {compression_ratio}%")
        
        if compression_ratio > 0:
            print(f"   ✅ Compression successful: {compression_ratio}% reduction")
        else:
            print(f"   ⚠️ No compression achieved")
    
    # Check preserved elements
    preserved_elements = result_data.get("preserved_elements", {})
    if preserved_elements:
        print(f"   ✅ Preserved elements: {list(preserved_elements.keys())}")
        
        core_strategy = preserved_elements.get("core_strategy", {})
        if core_strategy:
            print(f"   ✅ Core strategy preserved")
        
        key_insights = preserved_elements.get("key_insights", [])
        if key_insights:
            print(f"   ✅ Key insights preserved: {len(key_insights)} items")
    else:
        print(f"   ❌ No preserved elements found")

async def verify_stage_with_compression_check(stage_name: str, stage_result: Dict[str, Any], stage_results: Dict[str, Any]):
    """Verify stage and check if it used compressed context"""
    print(f"\n🔍 Verifying {stage_name} stage...")
    
    result_data = stage_result.get("result", {})
    
    # Check if this stage used compressed context
    used_compression = False
    for key in stage_results.keys():
        if key.startswith("compression_before_") and key.endswith(stage_name):
            used_compression = True
            break
    
    if used_compression:
        print(f"   🗜️ {stage_name} used compressed context")
        
        # Verify the stage still has essential information
        if stage_name == "drafting":
            title = result_data.get("title", "")
            if title:
                print(f"   ✅ Draft title generated: {title[:50]}...")
            
            claims = result_data.get("claims", [])
            if claims:
                print(f"   ✅ Claims generated: {len(claims)} claims")
        
        elif stage_name == "review":
            quality_score = result_data.get("quality_score", 0)
            print(f"   ✅ Review quality score: {quality_score}")
        
        elif stage_name == "rewrite":
            improvements = result_data.get("improvements", [])
            if improvements:
                print(f"   ✅ Rewrite improvements: {len(improvements)} items")
    else:
        print(f"   📋 {stage_name} used full context (no compression needed)")

async def verify_final_compression_usage(stage_results: Dict[str, Any], compression_used: bool):
    """Verify final compression usage summary"""
    print(f"\n🎯 Final Compression Usage Verification")
    print("=" * 40)
    
    # Count compression stages
    compression_stages = [key for key in stage_results.keys() if key.startswith("compression_before_")]
    
    print(f"📊 Compression stages used: {len(compression_stages)}")
    for stage in compression_stages:
        target_stage = stage.replace("compression_before_", "")
        print(f"   🗜️ Compression before: {target_stage}")
    
    if compression_used:
        print(f"✅ Optional compression mechanism working correctly")
        
        # Verify compression effectiveness
        total_compression_ratio = 0
        compression_count = 0
        
        for stage_name, stage_result in stage_results.items():
            if stage_name.startswith("compression_before_"):
                compression_summary = stage_result.get("result", {}).get("compression_summary", {})
                compression_ratio = compression_summary.get("compression_ratio", 0)
                total_compression_ratio += compression_ratio
                compression_count += 1
        
        if compression_count > 0:
            avg_compression_ratio = total_compression_ratio / compression_count
            print(f"📊 Average compression ratio: {avg_compression_ratio:.1f}%")
            
            if avg_compression_ratio > 20:
                print(f"✅ Good compression effectiveness achieved")
            else:
                print(f"⚠️ Low compression effectiveness")
    else:
        print(f"📋 No compression needed - context size remained manageable")
    
    # Verify workflow completion
    essential_stages = ["planning", "search", "discussion", "drafting", "review", "rewrite"]
    completed_stages = [stage for stage in essential_stages if stage in stage_results]
    
    print(f"\n📋 Workflow completion: {len(completed_stages)}/{len(essential_stages)} stages completed")
    
    if len(completed_stages) == len(essential_stages):
        print(f"✅ All essential stages completed successfully")
    else:
        missing_stages = [stage for stage in essential_stages if stage not in stage_results]
        print(f"❌ Missing stages: {missing_stages}")

async def test_compression_thresholds():
    """Test different compression thresholds"""
    print(f"\n🧪 Testing Compression Thresholds")
    print("=" * 40)
    
    # Test with different context sizes
    test_cases = [
        {
            "name": "Small Context",
            "topic": "Simple Patent",
            "description": "A simple patent with minimal context",
            "expected_compression": False
        },
        {
            "name": "Large Context", 
            "topic": "Complex Multi-Layer System with Advanced Features and Comprehensive Analysis",
            "description": "A very complex patent system with extensive technical details, multiple layers of abstraction, comprehensive analysis of prior art, detailed implementation strategies, advanced optimization techniques, and thorough documentation requirements that would generate substantial context for processing",
            "expected_compression": True
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for test_case in test_cases:
            print(f"\n📋 Testing: {test_case['name']}")
            
            workflow_request = {
                "topic": test_case["topic"],
                "description": test_case["description"],
                "workflow_type": "enhanced"
            }
            
            try:
                # Start workflow
                response = await client.post(
                    f"{BASE_URL}/coordinator/workflow/start",
                    json=workflow_request,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    workflow_id = result["workflow_id"]
                    
                    # Monitor for compression usage
                    compression_detected = False
                    for i in range(10):  # Monitor briefly
                        await asyncio.sleep(1)
                        
                        status_response = await client.get(
                            f"{BASE_URL}/coordinator/workflow/{workflow_id}/status",
                            timeout=5.0
                        )
                        
                        if status_response.status_code == 200:
                            status = status_response.json()
                            
                            # Check for compression stages
                            for stage in status['stages']:
                                if stage['name'].startswith('compression_before_'):
                                    compression_detected = True
                                    break
                            
                            if status['status'] in ['completed', 'failed']:
                                break
                    
                    # Verify expectation
                    if compression_detected == test_case["expected_compression"]:
                        print(f"   ✅ Compression usage as expected: {compression_detected}")
                    else:
                        print(f"   ❌ Unexpected compression usage: {compression_detected} (expected: {test_case['expected_compression']})")
                
                else:
                    print(f"   ❌ Failed to start workflow: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

async def main():
    """Main test function"""
    print("🧪 Testing Optional Compression Mechanism")
    print("=" * 50)
    
    # Test 1: Full workflow with compression verification
    await test_optional_compression_workflow()
    
    # Test 2: Compression thresholds
    await test_compression_thresholds()
    
    print("\n✅ Optional compression testing completed!")

if __name__ == "__main__":
    asyncio.run(main())