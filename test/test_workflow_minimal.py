#!/usr/bin/env python3
"""
Minimal Workflow Test
Debug workflow failure
"""

import asyncio
import httpx
import json

async def test_minimal_workflow():
    """Test minimal workflow"""
    print("🧪 Testing Minimal Workflow")
    print("=" * 30)
    
    async with httpx.AsyncClient() as client:
        # Start workflow
        workflow_request = {
            "topic": "Simple Test",
            "description": "Simple test description",
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
                
                # Monitor workflow step by step
                for i in range(20):
                    await asyncio.sleep(1)
                    
                    status_response = await client.get(
                        f"http://localhost:8000/coordinator/workflow/{workflow_id}/status",
                        timeout=5.0
                    )
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        print(f"📈 Progress: {status['progress']:.1f}% - Status: {status['status']}")
                        
                        # Check each stage
                        for stage in status['stages']:
                            if stage['status'] == 'failed':
                                print(f"❌ Stage {stage['name']} failed: {stage.get('error', 'Unknown error')}")
                                return
                            elif stage['status'] == 'completed':
                                print(f"✅ Stage {stage['name']} completed")
                        
                        if status['status'] in ['completed', 'failed']:
                            print(f"🏁 Workflow {status['status']}")
                            break
                    else:
                        print(f"❌ Failed to get status: {status_response.status_code}")
                        break
            else:
                print(f"❌ Failed to start workflow: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_minimal_workflow())