#!/usr/bin/env python3
"""
Comprehensive Test Mode Testing Script
Tests all test mode functionality in the Unified Patent Agent System
"""

import asyncio
import httpx
import time
import json
from typing import Dict, Any

# Service URL (single port)
BASE_URL = "http://localhost:8000"

async def test_test_mode_configuration():
    """Test test mode configuration endpoints"""
    print("🔧 Testing test mode configuration...")
    
    async with httpx.AsyncClient() as client:
        # 1. Get current test mode status
        try:
            response = await client.get(f"{BASE_URL}/test-mode", timeout=5.0)
            if response.status_code == 200:
                test_config = response.json()
                print(f"✅ Current test mode config: {test_config['test_mode']}")
                
                # Check if test mode is enabled
                if test_config['test_mode']['enabled']:
                    print(f"   🔧 Test mode: ENABLED")
                    print(f"   ⏱️ Mock delay: {test_config['test_mode']['mock_delay']}s")
                    print(f"   🎭 Mock results: {test_config['test_mode']['mock_results']}")
                    print(f"   🚫 Skip LLM calls: {test_config['test_mode']['skip_llm_calls']}")
                else:
                    print(f"   🔧 Test mode: DISABLED")
            else:
                print(f"❌ Failed to get test mode config: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting test mode config: {str(e)}")
        
        # 2. Test changing test mode settings
        print("\n🔄 Testing test mode configuration changes...")
        
        # Test 1: Change delay to 2 seconds
        try:
            new_config = {"mock_delay": 2.0}
            response = await client.post(f"{BASE_URL}/test-mode", json=new_config, timeout=5.0)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Updated test mode delay to 2.0s: {result['test_mode']['mock_delay']}s")
            else:
                print(f"❌ Failed to update test mode: {response.status_code}")
        except Exception as e:
            print(f"❌ Error updating test mode: {str(e)}")
        
        # Test 2: Disable test mode
        try:
            new_config = {"enabled": False}
            response = await client.post(f"{BASE_URL}/test-mode", json=new_config, timeout=5.0)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Disabled test mode: {result['test_mode']['enabled']}")
            else:
                print(f"❌ Failed to disable test mode: {response.status_code}")
        except Exception as e:
            print(f"❌ Error disabling test mode: {str(e)}")
        
        # Test 3: Re-enable test mode with 0.5s delay
        try:
            new_config = {"enabled": True, "mock_delay": 0.5}
            response = await client.post(f"{BASE_URL}/test-mode", json=new_config, timeout=5.0)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Re-enabled test mode with 0.5s delay: {result['test_mode']}")
            else:
                print(f"❌ Failed to re-enable test mode: {response.status_code}")
        except Exception as e:
            print(f"❌ Error re-enabling test mode: {str(e)}")

async def test_agent_test_mode():
    """Test agent test mode functionality"""
    print("\n🤖 Testing agent test mode...")
    
    agents = ["planner", "searcher", "discussion", "writer", "reviewer", "rewriter"]
    
    async with httpx.AsyncClient() as client:
        for agent in agents:
            print(f"\n📋 Testing {agent} agent test mode...")
            
            # 1. Check agent health (should show test mode status)
            try:
                response = await client.get(f"{BASE_URL}/agents/{agent}/health", timeout=5.0)
                if response.status_code == 200:
                    health_data = response.json()
                    test_mode_status = "ENABLED" if health_data.get('test_mode') else "DISABLED"
                    print(f"   ✅ {agent} agent health: {test_mode_status}")
                else:
                    print(f"   ❌ {agent} agent health failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error checking {agent} health: {str(e)}")
            
            # 2. Test agent execution with timing
            try:
                task_data = {
                    "task_id": f"test_{agent}_task",
                    "workflow_id": "test_workflow",
                    "stage_name": agent,
                    "topic": f"Test {agent.title()} Topic",
                    "description": f"Test {agent} description",
                    "previous_results": {},
                    "context": {}
                }
                
                start_time = time.time()
                response = await client.post(
                    f"{BASE_URL}/agents/{agent}/execute",
                    json=task_data,
                    timeout=30.0
                )
                end_time = time.time()
                execution_time = end_time - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    test_mode = result.get('test_mode', False)
                    mock_delay = result.get('result', {}).get('mock_delay_applied', 0)
                    
                    print(f"   ✅ {agent} execution completed in {execution_time:.2f}s")
                    print(f"   🔧 Test mode: {test_mode}")
                    print(f"   ⏱️ Mock delay applied: {mock_delay}s")
                    print(f"   📝 Message: {result.get('message', 'N/A')}")
                else:
                    print(f"   ❌ {agent} execution failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error executing {agent}: {str(e)}")

async def test_workflow_test_mode():
    """Test complete workflow with test mode"""
    print("\n🚀 Testing complete workflow with test mode...")
    
    # Test data
    workflow_request = {
        "topic": "Test Mode Patent System",
        "description": "A system for testing patent workflows in test mode with configurable delays",
        "workflow_type": "enhanced"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Start workflow
            print("📋 Starting workflow in test mode...")
            start_time = time.time()
            
            response = await client.post(
                f"{BASE_URL}/coordinator/workflow/start",
                json=workflow_request,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ Workflow started: {workflow_id}")
                print(f"📝 Message: {result.get('message', 'N/A')}")
                
                # 2. Monitor workflow progress with timing
                print("📊 Monitoring workflow progress...")
                stage_times = {}
                
                for i in range(20):  # Monitor for up to 20 iterations
                    await asyncio.sleep(1)  # Check every second
                    
                    status_response = await client.get(
                        f"{BASE_URL}/coordinator/workflow/{workflow_id}/status",
                        timeout=5.0
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        current_time = time.time()
                        
                        print(f"📈 Progress: {status['progress']:.1f}% - Status: {status['status']}")
                        print(f"   Current stage: {status['current_stage'] + 1}/{status['total_stages']}")
                        
                        # Track stage completion times
                        for stage in status['stages']:
                            if stage['status'] == 'completed' and stage['name'] not in stage_times:
                                stage_times[stage['name']] = current_time - start_time
                                print(f"   ✅ {stage['name']} completed at {stage_times[stage['name']]:.2f}s")
                        
                        # Check if completed
                        if status['status'] == 'completed':
                            total_time = time.time() - start_time
                            print(f"🎉 Workflow completed in {total_time:.2f}s!")
                            
                            # Get final results
                            results_response = await client.get(
                                f"{BASE_URL}/coordinator/workflow/{workflow_id}/results",
                                timeout=5.0
                            )
                            
                            if results_response.status_code == 200:
                                results = results_response.json()
                                print("📋 Final Results:")
                                for stage, result in results['results'].items():
                                    test_mode = result.get('test_mode', False)
                                    execution_time = result.get('execution_time', 0)
                                    print(f"   {stage}: completed (test_mode={test_mode}, time={execution_time}s)")
                                
                                print(f"🔧 Overall test mode: {results.get('test_mode', False)}")
                            break
                        elif status['status'] == 'failed':
                            print("❌ Workflow failed!")
                            break
                    else:
                        print(f"❌ Failed to get status: {status_response.status_code}")
                        
            else:
                print(f"❌ Failed to start workflow: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during workflow execution: {str(e)}")

async def test_test_mode_performance():
    """Test performance differences with different test mode settings"""
    print("\n⚡ Testing test mode performance...")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Fast test mode (0.1s delay)
        print("\n🔧 Testing fast test mode (0.1s delay)...")
        try:
            await client.post(f"{BASE_URL}/test-mode", json={"enabled": True, "mock_delay": 0.1}, timeout=5.0)
            
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/agents/planner/execute",
                json={
                    "task_id": "fast_test",
                    "workflow_id": "test_workflow",
                    "stage_name": "planning",
                    "topic": "Fast Test",
                    "description": "Fast test description",
                    "previous_results": {},
                    "context": {}
                },
                timeout=10.0
            )
            fast_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Fast test mode completed in {fast_time:.2f}s")
            else:
                print(f"   ❌ Fast test mode failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error in fast test mode: {str(e)}")
        
        # Test 2: Slow test mode (2.0s delay)
        print("\n🔧 Testing slow test mode (2.0s delay)...")
        try:
            await client.post(f"{BASE_URL}/test-mode", json={"enabled": True, "mock_delay": 2.0}, timeout=5.0)
            
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/agents/planner/execute",
                json={
                    "task_id": "slow_test",
                    "workflow_id": "test_workflow",
                    "stage_name": "planning",
                    "topic": "Slow Test",
                    "description": "Slow test description",
                    "previous_results": {},
                    "context": {}
                },
                timeout=10.0
            )
            slow_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Slow test mode completed in {slow_time:.2f}s")
            else:
                print(f"   ❌ Slow test mode failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error in slow test mode: {str(e)}")
        
        # Test 3: Disable test mode
        print("\n🔧 Testing disabled test mode...")
        try:
            await client.post(f"{BASE_URL}/test-mode", json={"enabled": False}, timeout=5.0)
            
            start_time = time.time()
            response = await client.post(
                f"{BASE_URL}/agents/planner/execute",
                json={
                    "task_id": "disabled_test",
                    "workflow_id": "test_workflow",
                    "stage_name": "planning",
                    "topic": "Disabled Test",
                    "description": "Disabled test description",
                    "previous_results": {},
                    "context": {}
                },
                timeout=10.0
            )
            disabled_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Disabled test mode completed in {disabled_time:.2f}s")
            else:
                print(f"   ❌ Disabled test mode failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error in disabled test mode: {str(e)}")
        
        # Reset to default test mode
        try:
            await client.post(f"{BASE_URL}/test-mode", json={"enabled": True, "mock_delay": 1.0}, timeout=5.0)
            print("\n🔄 Reset to default test mode (1.0s delay)")
        except Exception as e:
            print(f"   ❌ Error resetting test mode: {str(e)}")

async def main():
    """Main test function"""
    print("🧪 Comprehensive Test Mode Testing")
    print("=" * 50)
    
    # Test 1: Test mode configuration
    await test_test_mode_configuration()
    
    # Test 2: Agent test mode
    await test_agent_test_mode()
    
    # Test 3: Workflow test mode
    await test_workflow_test_mode()
    
    # Test 4: Performance testing
    await test_test_mode_performance()
    
    print("\n✅ Test mode testing completed!")

if __name__ == "__main__":
    asyncio.run(main())