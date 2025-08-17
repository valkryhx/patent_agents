#!/usr/bin/env python3
"""
Test Workflow ID Context Isolation
Verifies that multiple workflows have isolated contexts and don't mix
"""

import asyncio
import httpx
import time
import json
from typing import Dict, Any

# Service URL (single port)
BASE_URL = "http://localhost:8000"

async def test_multiple_workflows_isolation():
    """Test multiple concurrent workflows with context isolation"""
    print("🎯 Testing Workflow ID Context Isolation")
    print("=" * 50)
    
    # Test data for multiple workflows
    workflow_requests = [
        {
            "topic": "Workflow A: AI-Powered Patent Analysis System",
            "description": "A system for AI-powered patent analysis and evaluation",
            "workflow_type": "enhanced"
        },
        {
            "topic": "Workflow B: Blockchain-Based IP Management",
            "description": "A blockchain-based intellectual property management system",
            "workflow_type": "enhanced"
        },
        {
            "topic": "Workflow C: Quantum Computing Patent Framework",
            "description": "A framework for quantum computing patent applications",
            "workflow_type": "enhanced"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        workflow_ids = []
        workflow_results = {}
        
        # Start multiple workflows concurrently
        print("📋 Starting multiple workflows concurrently...")
        for i, request in enumerate(workflow_requests):
            try:
                response = await client.post(
                    f"{BASE_URL}/coordinator/workflow/start",
                    json=request,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    workflow_id = result["workflow_id"]
                    workflow_ids.append(workflow_id)
                    workflow_results[workflow_id] = {
                        "topic": request["topic"],
                        "stages": {},
                        "completed": False
                    }
                    print(f"✅ Started workflow {i+1}: {workflow_id}")
                    print(f"   Topic: {request['topic']}")
                else:
                    print(f"❌ Failed to start workflow {i+1}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error starting workflow {i+1}: {str(e)}")
        
        if not workflow_ids:
            print("❌ No workflows started successfully")
            return
        
        # Monitor all workflows concurrently
        print(f"\n📊 Monitoring {len(workflow_ids)} workflows concurrently...")
        
        for iteration in range(30):  # Monitor for up to 30 iterations
            await asyncio.sleep(1)
            
            completed_count = 0
            for workflow_id in workflow_ids:
                try:
                    status_response = await client.get(
                        f"{BASE_URL}/coordinator/workflow/{workflow_id}/status",
                        timeout=5.0
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        
                        # Track completed stages for this workflow
                        for stage in status['stages']:
                            if stage['status'] == 'completed' and stage['name'] not in workflow_results[workflow_id]['stages']:
                                workflow_results[workflow_id]['stages'][stage['name']] = {
                                    'result': stage.get('result', {}),
                                    'timestamp': time.time()
                                }
                                print(f"✅ Workflow {workflow_id[:8]}... completed stage: {stage['name']}")
                        
                        # Check if workflow completed
                        if status['status'] == 'completed':
                            if not workflow_results[workflow_id]['completed']:
                                workflow_results[workflow_id]['completed'] = True
                                completed_count += 1
                                print(f"🎉 Workflow {workflow_id[:8]}... completed!")
                                
                                # Get final results
                                results_response = await client.get(
                                    f"{BASE_URL}/coordinator/workflow/{workflow_id}/results",
                                    timeout=5.0
                                )
                                
                                if results_response.status_code == 200:
                                    results = results_response.json()
                                    workflow_results[workflow_id]['final_results'] = results
                        
                        elif status['status'] == 'failed':
                            if not workflow_results[workflow_id]['completed']:
                                workflow_results[workflow_id]['completed'] = True
                                print(f"❌ Workflow {workflow_id[:8]}... failed!")
                    
                    else:
                        print(f"❌ Failed to get status for workflow {workflow_id[:8]}...: {status_response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error monitoring workflow {workflow_id[:8]}...: {str(e)}")
            
            # Check if all workflows completed
            if completed_count == len(workflow_ids):
                print(f"\n🎉 All {len(workflow_ids)} workflows completed!")
                break
        
        # Verify workflow isolation
        print(f"\n🔍 Verifying workflow context isolation...")
        await verify_workflow_isolation(workflow_results)

async def verify_workflow_isolation(workflow_results: Dict[str, Any]):
    """Verify that workflows have isolated contexts"""
    print("=" * 40)
    
    isolation_issues = []
    
    for workflow_id, workflow_data in workflow_results.items():
        topic = workflow_data['topic']
        stages = workflow_data['stages']
        
        print(f"\n📋 Workflow {workflow_id[:8]}...: {topic}")
        
        # Check each stage for workflow ID consistency
        for stage_name, stage_data in stages.items():
            result = stage_data.get('result', {})
            
            # Check if result contains workflow ID
            if 'workflow_id' in result:
                result_workflow_id = result['workflow_id']
                if result_workflow_id != workflow_id:
                    isolation_issues.append({
                        'workflow_id': workflow_id,
                        'stage': stage_name,
                        'expected': workflow_id,
                        'found': result_workflow_id,
                        'issue': 'workflow_id_mismatch'
                    })
                    print(f"   ❌ Stage {stage_name}: Workflow ID mismatch - expected {workflow_id[:8]}..., got {result_workflow_id[:8]}...")
                else:
                    print(f"   ✅ Stage {stage_name}: Workflow ID consistent")
            else:
                isolation_issues.append({
                    'workflow_id': workflow_id,
                    'stage': stage_name,
                    'issue': 'missing_workflow_id'
                })
                print(f"   ⚠️ Stage {stage_name}: Missing workflow ID")
            
            # Check for isolation timestamp
            if 'isolation_timestamp' in result:
                print(f"   ✅ Stage {stage_name}: Has isolation timestamp")
            else:
                print(f"   ⚠️ Stage {stage_name}: Missing isolation timestamp")
    
    # Summary
    print(f"\n📊 Workflow Isolation Summary:")
    print(f"   Total workflows: {len(workflow_results)}")
    print(f"   Isolation issues found: {len(isolation_issues)}")
    
    if isolation_issues:
        print(f"   ❌ Workflow isolation issues detected!")
        for issue in isolation_issues:
            print(f"      - {issue['issue']} in workflow {issue['workflow_id'][:8]}... stage {issue['stage']}")
    else:
        print(f"   ✅ All workflows properly isolated!")
    
    # Verify topic consistency
    print(f"\n🎯 Topic Consistency Verification:")
    for workflow_id, workflow_data in workflow_results.items():
        topic = workflow_data['topic']
        stages = workflow_data['stages']
        
        topic_consistent = True
        for stage_name, stage_data in stages.items():
            result = stage_data.get('result', {})
            
            # Check if stage result contains the correct topic
            if 'strategy' in result:
                strategy_topic = result['strategy'].get('topic', '')
                if strategy_topic and strategy_topic != topic:
                    topic_consistent = False
                    print(f"   ❌ Workflow {workflow_id[:8]}... stage {stage_name}: Topic mismatch")
                    print(f"      Expected: {topic}")
                    print(f"      Found: {strategy_topic}")
        
        if topic_consistent:
            print(f"   ✅ Workflow {workflow_id[:8]}...: Topic consistent across all stages")

async def test_workflow_id_validation():
    """Test workflow ID validation in agent responses"""
    print(f"\n🧪 Testing Workflow ID Validation")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        # Test direct agent calls with workflow ID
        test_workflow_id = "test-workflow-123"
        
        # Test planner agent
        planner_request = {
            "task_id": f"{test_workflow_id}_planning_test",
            "workflow_id": test_workflow_id,
            "stage_name": "planning",
            "topic": "Test Patent Topic",
            "description": "Test patent description",
            "previous_results": {},
            "context": {
                "workflow_id": test_workflow_id,
                "isolation_level": "workflow_specific",
                "context_timestamp": time.time()
            }
        }
        
        try:
            print("📤 Testing planner agent with workflow ID...")
            response = await client.post(
                f"{BASE_URL}/agents/planner/execute",
                json=planner_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                result_data = result.get("result", {})
                
                if result_data.get("workflow_id") == test_workflow_id:
                    print(f"   ✅ Planner agent returned correct workflow ID")
                else:
                    print(f"   ❌ Planner agent workflow ID mismatch")
                    print(f"      Expected: {test_workflow_id}")
                    print(f"      Found: {result_data.get('workflow_id')}")
                
                if "isolation_timestamp" in result_data:
                    print(f"   ✅ Planner agent includes isolation timestamp")
                else:
                    print(f"   ⚠️ Planner agent missing isolation timestamp")
            else:
                print(f"   ❌ Planner agent failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing planner agent: {str(e)}")

async def main():
    """Main test function"""
    print("🧪 Testing Workflow ID Context Isolation")
    print("=" * 50)
    
    # Test 1: Multiple concurrent workflows
    await test_multiple_workflows_isolation()
    
    # Test 2: Workflow ID validation
    await test_workflow_id_validation()
    
    print("\n✅ Workflow isolation testing completed!")

if __name__ == "__main__":
    asyncio.run(main())