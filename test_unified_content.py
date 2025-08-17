#!/usr/bin/env python3
"""
Test Unified Content Mechanism
Verifies that all agents maintain consistent topic and idea throughout the workflow
"""

import asyncio
import httpx
import time
import json
from typing import Dict, Any

# Service URL (single port)
BASE_URL = "http://localhost:8000"

async def test_unified_content_workflow():
    """Test complete workflow with unified content verification"""
    print("🎯 Testing Unified Content Mechanism")
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
            print("📋 Starting workflow with unified content...")
            response = await client.post(
                f"{BASE_URL}/coordinator/workflow/start",
                json=workflow_request,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ Workflow started: {workflow_id}")
                
                # 2. Monitor workflow and verify unified content
                print("📊 Monitoring workflow with content verification...")
                stage_results = {}
                
                for i in range(20):  # Monitor for up to 20 iterations
                    await asyncio.sleep(1)  # Check every second
                    
                    status_response = await client.get(
                        f"{BASE_URL}/coordinator/workflow/{workflow_id}/status",
                        timeout=5.0
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        
                        print(f"📈 Progress: {status['progress']:.1f}% - Status: {status['status']}")
                        
                        # Check each completed stage for unified content
                        for stage in status['stages']:
                            if stage['status'] == 'completed' and stage['name'] not in stage_results:
                                stage_results[stage['name']] = stage['result']
                                await verify_stage_unified_content(stage['name'], stage['result'], workflow_request)
                        
                        # Check if completed
                        if status['status'] == 'completed':
                            print("🎉 Workflow completed! Verifying final unified content...")
                            await verify_final_unified_content(stage_results, workflow_request)
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

async def verify_stage_unified_content(stage_name: str, stage_result: Dict[str, Any], original_request: Dict[str, Any]):
    """Verify that a stage maintains unified content"""
    print(f"\n🔍 Verifying {stage_name} stage unified content...")
    
    topic = original_request["topic"]
    description = original_request["description"]
    
    # Extract result data
    result_data = stage_result.get("result", {})
    
    # Verify topic consistency
    if "topic" in result_data:
        stage_topic = result_data["topic"]
        if stage_topic == topic:
            print(f"   ✅ Topic consistency: {stage_topic}")
        else:
            print(f"   ❌ Topic mismatch: expected '{topic}', got '{stage_topic}'")
    
    # Stage-specific content verification
    if stage_name == "planning":
        await verify_planning_content(result_data, topic)
    elif stage_name == "search":
        await verify_search_content(result_data, topic)
    elif stage_name == "discussion":
        await verify_discussion_content(result_data, topic)
    elif stage_name == "drafting":
        await verify_drafting_content(result_data, topic)
    elif stage_name == "review":
        await verify_review_content(result_data, topic)
    elif stage_name == "rewrite":
        await verify_rewrite_content(result_data, topic)

async def verify_planning_content(result_data: Dict[str, Any], topic: str):
    """Verify planning stage maintains core strategy"""
    strategy = result_data.get("strategy", {})
    strategy_topic = strategy.get("topic", "")
    
    if strategy_topic == topic:
        print(f"   ✅ Planning strategy topic: {strategy_topic}")
    else:
        print(f"   ❌ Planning strategy topic mismatch: expected '{topic}', got '{strategy_topic}'")
    
    innovation_areas = strategy.get("key_innovation_areas", [])
    if innovation_areas:
        print(f"   ✅ Core innovation areas defined: {innovation_areas}")
    else:
        print(f"   ⚠️ No core innovation areas defined")

async def verify_search_content(result_data: Dict[str, Any], topic: str):
    """Verify search stage incorporates topic"""
    search_results = result_data.get("search_results", {})
    query_topic = search_results.get("query", {}).get("topic", "")
    
    if query_topic == topic:
        print(f"   ✅ Search query topic: {query_topic}")
    else:
        print(f"   ❌ Search query topic mismatch: expected '{topic}', got '{query_topic}'")
    
    keywords = search_results.get("query", {}).get("keywords", [])
    if keywords:
        print(f"   ✅ Search keywords extracted: {keywords[:3]}...")  # Show first 3
    else:
        print(f"   ⚠️ No search keywords extracted")

async def verify_discussion_content(result_data: Dict[str, Any], topic: str):
    """Verify discussion stage builds on previous stages"""
    discussion_topic = result_data.get("topic", "")
    
    if discussion_topic == topic:
        print(f"   ✅ Discussion topic: {discussion_topic}")
    else:
        print(f"   ❌ Discussion topic mismatch: expected '{topic}', got '{discussion_topic}'")
    
    # Check if discussion builds on planning strategy
    core_strategy = result_data.get("core_strategy", {})
    if core_strategy:
        print(f"   ✅ Discussion incorporates planning strategy")
    else:
        print(f"   ⚠️ Discussion missing planning strategy")
    
    innovations = result_data.get("innovations", [])
    if innovations:
        print(f"   ✅ Discussion innovations: {innovations[:2]}...")  # Show first 2
    else:
        print(f"   ⚠️ No discussion innovations")

async def verify_drafting_content(result_data: Dict[str, Any], topic: str):
    """Verify drafting stage uses unified content"""
    draft_title = result_data.get("title", "")
    if topic in draft_title:
        print(f"   ✅ Draft title incorporates topic: {draft_title}")
    else:
        print(f"   ❌ Draft title missing topic: {draft_title}")
    
    # Check unified content structure
    unified_content = result_data.get("unified_content", {})
    if unified_content:
        print(f"   ✅ Draft includes unified content structure")
        core_strategy = unified_content.get("core_strategy", {})
        if core_strategy:
            print(f"   ✅ Draft incorporates planning strategy")
        search_context = unified_content.get("search_context", {})
        if search_context:
            print(f"   ✅ Draft incorporates search context")
        discussion_insights = unified_content.get("discussion_insights", {})
        if discussion_insights:
            print(f"   ✅ Draft incorporates discussion insights")
    else:
        print(f"   ❌ Draft missing unified content structure")
    
    claims = result_data.get("claims", [])
    if claims:
        print(f"   ✅ Draft claims generated: {len(claims)} claims")
    else:
        print(f"   ⚠️ No draft claims generated")

async def verify_review_content(result_data: Dict[str, Any], topic: str):
    """Verify review stage checks unified content consistency"""
    quality_score = result_data.get("quality_score", 0)
    print(f"   ✅ Review quality score: {quality_score}")
    
    consistency_score = result_data.get("consistency_score", 0)
    print(f"   ✅ Review consistency score: {consistency_score}")
    
    unified_content_review = result_data.get("unified_content_review", {})
    if unified_content_review:
        print(f"   ✅ Review includes unified content assessment")
        strategy_alignment = unified_content_review.get("strategy_alignment", "")
        print(f"   ✅ Strategy alignment: {strategy_alignment}")
        topic_coherence = unified_content_review.get("topic_coherence", "")
        print(f"   ✅ Topic coherence: {topic_coherence}")
    else:
        print(f"   ❌ Review missing unified content assessment")

async def verify_rewrite_content(result_data: Dict[str, Any], topic: str):
    """Verify rewrite stage incorporates all unified content"""
    rewrite_title = result_data.get("title", "")
    if topic in rewrite_title:
        print(f"   ✅ Rewrite title incorporates topic: {rewrite_title}")
    else:
        print(f"   ❌ Rewrite title missing topic: {rewrite_title}")
    
    # Check unified content summary
    unified_content_summary = result_data.get("unified_content_summary", {})
    if unified_content_summary:
        print(f"   ✅ Rewrite includes unified content summary")
        core_strategy = unified_content_summary.get("core_strategy", {})
        if core_strategy:
            print(f"   ✅ Rewrite incorporates planning strategy")
        search_integration = unified_content_summary.get("search_integration", {})
        if search_integration:
            print(f"   ✅ Rewrite incorporates search integration")
        discussion_insights = unified_content_summary.get("discussion_insights", {})
        if discussion_insights:
            print(f"   ✅ Rewrite incorporates discussion insights")
        review_incorporation = unified_content_summary.get("review_incorporation", {})
        if review_incorporation:
            print(f"   ✅ Rewrite incorporates review feedback")
    else:
        print(f"   ❌ Rewrite missing unified content summary")
    
    improvements = result_data.get("improvements", [])
    if improvements:
        print(f"   ✅ Rewrite improvements: {improvements[:2]}...")  # Show first 2
    else:
        print(f"   ⚠️ No rewrite improvements")

async def verify_final_unified_content(stage_results: Dict[str, Any], original_request: Dict[str, Any]):
    """Verify final unified content across all stages"""
    print(f"\n🎯 Final Unified Content Verification")
    print("=" * 40)
    
    topic = original_request["topic"]
    description = original_request["description"]
    
    # Check topic consistency across all stages
    topic_consistent = True
    for stage_name, stage_result in stage_results.items():
        result_data = stage_result.get("result", {})
        stage_topic = result_data.get("topic", "")
        if stage_topic and stage_topic != topic:
            print(f"   ❌ {stage_name} topic mismatch: '{stage_topic}' vs '{topic}'")
            topic_consistent = False
    
    if topic_consistent:
        print(f"   ✅ Topic consistency maintained across all stages: {topic}")
    
    # Check strategy continuity
    planning_strategy = stage_results.get("planning", {}).get("result", {}).get("strategy", {})
    if planning_strategy:
        innovation_areas = planning_strategy.get("key_innovation_areas", [])
        print(f"   ✅ Core innovation areas established: {innovation_areas}")
        
        # Check if later stages use these innovation areas
        strategy_used = True
        for stage_name in ["discussion", "drafting", "review", "rewrite"]:
            if stage_name in stage_results:
                stage_data = stage_results[stage_name].get("result", {})
                if "unified_content" in stage_data or "unified_content_summary" in stage_data:
                    print(f"   ✅ {stage_name} uses unified content structure")
                else:
                    print(f"   ⚠️ {stage_name} missing unified content structure")
                    strategy_used = False
        
        if strategy_used:
            print(f"   ✅ Strategy continuity maintained throughout workflow")
    else:
        print(f"   ❌ No planning strategy found")
    
    # Check content integration
    print(f"\n📋 Content Integration Summary:")
    stages_with_unified_content = []
    for stage_name in ["discussion", "drafting", "review", "rewrite"]:
        if stage_name in stage_results:
            stage_data = stage_results[stage_name].get("result", {})
            if any(key in stage_data for key in ["unified_content", "unified_content_summary", "core_strategy"]):
                stages_with_unified_content.append(stage_name)
    
    print(f"   ✅ Stages with unified content: {stages_with_unified_content}")
    
    if len(stages_with_unified_content) >= 3:
        print(f"   ✅ Strong unified content integration achieved")
    elif len(stages_with_unified_content) >= 1:
        print(f"   ⚠️ Partial unified content integration")
    else:
        print(f"   ❌ No unified content integration found")

async def main():
    """Main test function"""
    print("🧪 Testing Unified Content Mechanism")
    print("=" * 50)
    
    # Test unified content workflow
    await test_unified_content_workflow()
    
    print("\n✅ Unified content testing completed!")

if __name__ == "__main__":
    asyncio.run(main())