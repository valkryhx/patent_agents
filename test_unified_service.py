#!/usr/bin/env python3
"""
Test script for the Unified Patent Agent System
Tests single service with all agents on different URL paths
"""

import asyncio
import httpx
import time
import json
from typing import Dict, Any

# Service URL (single port)
BASE_URL = "http://localhost:8000"

async def test_service_health():
    """Test health of unified service"""
    print("🔍 Testing unified service health...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Unified service is healthy")
                print(f"   Version: {health_data.get('version')}")
                print(f"   Active workflows: {health_data.get('active_workflows')}")
                print(f"   Services: {health_data.get('services')}")
            else:
                print(f"❌ Service returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Service is unreachable: {str(e)}")

async def test_agent_health():
    """Test health of all agents"""
    print("\n🤖 Testing agent health...")
    
    agents = ["planner", "searcher", "discussion", "writer", "reviewer", "rewriter"]
    
    async with httpx.AsyncClient() as client:
        for agent in agents:
            try:
                response = await client.get(f"{BASE_URL}/agents/{agent}/health", timeout=5.0)
                if response.status_code == 200:
                    health_data = response.json()
                    print(f"✅ {agent} agent is healthy")
                    print(f"   Capabilities: {health_data.get('capabilities')}")
                else:
                    print(f"❌ {agent} agent returned status {response.status_code}")
            except Exception as e:
                print(f"❌ {agent} agent is unreachable: {str(e)}")

async def test_direct_agent_calls():
    """Test direct calls to agent services"""
    print("\n🤖 Testing direct agent calls...")
    
    # Test planner agent
    print("📋 Testing planner agent...")
    planner_task = {
        "task_id": "test_planner_task",
        "workflow_id": "test_workflow",
        "stage_name": "planning",
        "topic": "Test Patent Topic",
        "description": "Test patent description",
        "previous_results": {},
        "context": {}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/agents/planner/execute",
                json=planner_task,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Planner agent completed task: {result['status']}")
                print(f"   Strategy: {result['result'].get('strategy', {}).get('topic', 'N/A')}")
            else:
                print(f"❌ Planner agent failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error calling planner agent: {str(e)}")
    
    # Test searcher agent
    print("🔍 Testing searcher agent...")
    searcher_task = {
        "task_id": "test_searcher_task",
        "workflow_id": "test_workflow",
        "stage_name": "search",
        "topic": "Test Patent Topic",
        "description": "Test patent description",
        "previous_results": {},
        "context": {}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/agents/searcher/execute",
                json=searcher_task,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Searcher agent completed task: {result['status']}")
                print(f"   Patents found: {result['result'].get('patents_found', 0)}")
            else:
                print(f"❌ Searcher agent failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error calling searcher agent: {str(e)}")

async def test_complete_workflow():
    """Test complete workflow execution"""
    print("\n🚀 Testing complete workflow execution...")
    
    # Test data
    workflow_request = {
        "topic": "基于智能分层推理的多参数工具自适应调用系统",
        "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。",
        "workflow_type": "enhanced"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Start workflow
            print("📋 Starting workflow...")
            response = await client.post(
                f"{BASE_URL}/coordinator/workflow/start",
                json=workflow_request,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ Workflow started: {workflow_id}")
                
                # 2. Monitor workflow progress
                print("📊 Monitoring workflow progress...")
                for i in range(15):  # Monitor for up to 15 iterations (all 6 stages)
                    await asyncio.sleep(2)  # Wait 2 seconds between checks
                    
                    status_response = await client.get(
                        f"{BASE_URL}/coordinator/workflow/{workflow_id}/status",
                        timeout=5.0
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        print(f"📈 Progress: {status['progress']:.1f}% - Status: {status['status']}")
                        print(f"   Current stage: {status['current_stage'] + 1}/{status['total_stages']}")
                        
                        # Show completed stages
                        completed_stages = [stage for stage in status['stages'] if stage['status'] == 'completed']
                        if completed_stages:
                            print(f"   Completed: {[stage['name'] for stage in completed_stages]}")
                        
                        # Check if completed
                        if status['status'] == 'completed':
                            print("🎉 Workflow completed successfully!")
                            
                            # Get final results
                            results_response = await client.get(
                                f"{BASE_URL}/coordinator/workflow/{workflow_id}/results",
                                timeout=5.0
                            )
                            
                            if results_response.status_code == 200:
                                results = results_response.json()
                                print("📋 Final Results:")
                                for stage, result in results['results'].items():
                                    print(f"   {stage}: {result.get('status', 'completed')}")
                            break
                        elif status['status'] == 'failed':
                            print("❌ Workflow failed!")
                            # Show which stage failed
                            failed_stages = [stage for stage in status['stages'] if stage['status'] == 'failed']
                            if failed_stages:
                                print(f"   Failed stages: {[stage['name'] for stage in failed_stages]}")
                                for stage in failed_stages:
                                    if stage.get('error'):
                                        print(f"   Error in {stage['name']}: {stage['error']}")
                            break
                    else:
                        print(f"❌ Failed to get status: {status_response.status_code}")
                        
            else:
                print(f"❌ Failed to start workflow: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during workflow execution: {str(e)}")

async def main():
    """Main test function"""
    print("🧪 Testing Unified Patent Agent System")
    print("=" * 50)
    
    # Test 1: Service health
    await test_service_health()
    
    # Test 2: Agent health
    await test_agent_health()
    
    # Test 3: Direct agent calls
    await test_direct_agent_calls()
    
    # Test 4: Complete workflow
    await test_complete_workflow()
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    asyncio.run(main())