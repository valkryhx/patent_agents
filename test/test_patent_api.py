#!/usr/bin/env python3
"""
Test script for Patent Generation API
Tests all endpoints with different topics and test modes
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Active workflows: {data.get('active_workflows')}")
        print(f"   Agent services: {data.get('agent_services')}")
    print()

def test_patent_generation(topic: str, description: str, test_mode: bool):
    """Test patent generation endpoint"""
    print(f"🚀 Testing patent generation for topic: {topic}")
    print(f"   Description: {description}")
    print(f"   Test mode: {test_mode}")
    
    payload = {
        "topic": topic,
        "description": description,
        "test_mode": test_mode
    }
    
    response = requests.post(f"{BASE_URL}/patent/generate", json=payload)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        workflow_id = data.get("workflow_id")
        print(f"   Workflow ID: {workflow_id}")
        print(f"   Message: {data.get('message')}")
        return workflow_id
    else:
        print(f"   Error: {response.text}")
        return None

def test_workflow_status(workflow_id: str):
    """Test workflow status endpoint"""
    print(f"📊 Testing workflow status for: {workflow_id}")
    
    response = requests.get(f"{BASE_URL}/patent/{workflow_id}/status")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Topic: {data.get('topic')}")
        print(f"   Status: {data.get('status')}")
        print(f"   Test mode: {data.get('test_mode')}")
        print(f"   Progress: {data.get('progress')}%")
        print(f"   Current stage: {data.get('current_stage')}/{data.get('total_stages')}")
    else:
        print(f"   Error: {response.text}")
    print()

def test_list_patents():
    """Test list patents endpoint"""
    print("📋 Testing list patents...")
    
    response = requests.get(f"{BASE_URL}/patents")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        patents = data.get("patent_workflows", [])
        print(f"   Total patents: {data.get('total')}")
        for patent in patents:
            print(f"     - {patent.get('topic')} (ID: {patent.get('workflow_id')[:8]}...) - {patent.get('status')}")
    else:
        print(f"   Error: {response.text}")
    print()

def test_list_all_workflows():
    """Test list all workflows endpoint"""
    print("📋 Testing list all workflows...")
    
    response = requests.get(f"{BASE_URL}/workflows")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        workflows = data.get("workflows", [])
        print(f"   Total workflows: {len(workflows)}")
        for workflow in workflows:
            print(f"     - {workflow.get('topic')} (ID: {workflow.get('workflow_id')[:8]}...) - {workflow.get('status')} - Test: {workflow.get('test_mode')}")
    else:
        print(f"   Error: {response.text}")
    print()

def main():
    """Main test function"""
    print("🧪 Starting Patent API Tests")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test patent generation with blockchain topic (test mode)
    print("🔗 Testing Blockchain Patent Generation (Test Mode)")
    print("-" * 50)
    blockchain_id = test_patent_generation(
        topic="区块链",
        description="基于区块链技术的知识产权管理系统",
        test_mode=True
    )
    
    if blockchain_id:
        test_workflow_status(blockchain_id)
    
    # Test patent generation with AI topic (real mode)
    print("🤖 Testing AI Patent Generation (Real Mode)")
    print("-" * 50)
    ai_id = test_patent_generation(
        topic="人工智能",
        description="基于深度学习的智能图像识别系统",
        test_mode=False
    )
    
    if ai_id:
        test_workflow_status(ai_id)
    
    # Test list endpoints
    print("📋 Testing List Endpoints")
    print("-" * 50)
    test_list_patents()
    test_list_all_workflows()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()