#!/usr/bin/env python3
"""
Show Workflows with Topic Information
Displays workflow IDs and their corresponding topics in a friendly format
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def show_workflows_summary():
    """Show all workflows with topic summary"""
    print("🔍 Fetching all workflows...")
    try:
        response = requests.get(f"{BASE_URL}/workflows")
        if response.status_code == 200:
            data = response.json()
            workflows = data.get("workflows", [])
            summary = data.get("summary", {})
            
            print(f"\n📊 Workflows Summary:")
            print(f"   Total workflows: {summary.get('total_workflows', 0)}")
            
            # Show by topic
            by_topic = summary.get("by_topic", {})
            if by_topic:
                print(f"\n📝 By Topic:")
                for topic, count in by_topic.items():
                    print(f"   • {topic}: {count} workflow(s)")
            
            # Show by status
            by_status = summary.get("by_status", {})
            if by_status:
                print(f"\n📈 By Status:")
                for status, count in by_status.items():
                    print(f"   • {status}: {count} workflow(s)")
            
            # Show by test mode
            by_test_mode = summary.get("by_test_mode", {})
            if by_test_mode:
                print(f"\n🧪 By Test Mode:")
                print(f"   • Test mode: {by_test_mode.get('test', 0)} workflow(s)")
                print(f"   • Real mode: {by_test_mode.get('real', 0)} workflow(s)")
            
            # Show detailed workflow list
            if workflows:
                print(f"\n📋 Detailed Workflow List:")
                print("-" * 100)
                print(f"{'ID (Short)':<15} {'Topic':<15} {'Description':<40} {'Status':<10} {'Test Mode':<10} {'Type':<10}")
                print("-" * 100)
                
                for workflow in workflows:
                    workflow_id = workflow.get("workflow_id", "")[:8] + "..."
                    topic = workflow.get("topic", "Unknown")
                    description = workflow.get("description", "No description")
                    # Truncate description if too long
                    if len(description) > 37:
                        description = description[:34] + "..."
                    status = workflow.get("status", "Unknown")
                    test_mode = "✅ Test" if workflow.get("test_mode", False) else "🚀 Real"
                    workflow_type = workflow.get("workflow_type", "Unknown")
                    
                    print(f"{workflow_id:<15} {topic:<15} {description:<40} {status:<10} {test_mode:<10} {workflow_type:<10}")
                
                print("-" * 100)
            else:
                print("\n📭 No workflows found.")
                
        else:
            print(f"❌ Failed to fetch workflows: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def show_patent_workflows():
    """Show patent workflows specifically"""
    print("\n🔍 Fetching patent workflows...")
    try:
        response = requests.get(f"{BASE_URL}/patents")
        if response.status_code == 200:
            data = response.json()
            patent_workflows = data.get("patent_workflows", [])
            summary = data.get("summary", {})
            
            print(f"\n📊 Patent Workflows Summary:")
            print(f"   Total patents: {summary.get('total_patents', 0)}")
            
            # Show by topic
            by_topic = summary.get("by_topic", {})
            if by_topic:
                print(f"\n📝 By Topic:")
                for topic, count in by_topic.items():
                    print(f"   • {topic}: {count} patent(s)")
            
            # Show by status
            by_status = summary.get("by_status", {})
            if by_status:
                print(f"\n📈 By Status:")
                for status, count in by_status.items():
                    print(f"   • {status}: {count} patent(s)")
            
            # Show by test mode
            by_test_mode = summary.get("by_test_mode", {})
            if by_test_mode:
                print(f"\n🧪 By Test Mode:")
                print(f"   • Test mode: {by_test_mode.get('test', 0)} patent(s)")
                print(f"   • Real mode: {by_test_mode.get('real', 0)} patent(s)")
            
            # Show detailed patent list
            if patent_workflows:
                print(f"\n📋 Detailed Patent List:")
                print("-" * 100)
                print(f"{'ID (Short)':<15} {'Topic':<15} {'Description':<40} {'Status':<10} {'Test Mode':<10} {'Stages':<10}")
                print("-" * 100)
                
                for workflow in patent_workflows:
                    workflow_id = workflow.get("workflow_id", "")[:8] + "..."
                    topic = workflow.get("topic", "Unknown")
                    description = workflow.get("description", "No description")
                    # Truncate description if too long
                    if len(description) > 37:
                        description = description[:34] + "..."
                    status = workflow.get("status", "Unknown")
                    test_mode = "✅ Test" if workflow.get("test_mode", False) else "🚀 Real"
                    stages = f"{workflow.get('current_stage', 0)}/{workflow.get('total_stages', 0)}"
                    
                    print(f"{workflow_id:<15} {topic:<15} {description:<40} {status:<10} {test_mode:<10} {stages:<10}")
                
                print("-" * 100)
            else:
                print("\n📭 No patent workflows found.")
                
        else:
            print(f"❌ Failed to fetch patent workflows: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def show_workflow_by_id(workflow_id: str):
    """Show specific workflow details by ID"""
    print(f"\n🔍 Fetching workflow details for: {workflow_id}")
    try:
        response = requests.get(f"{BASE_URL}/workflow/{workflow_id}/status")
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📋 Workflow Details:")
            print(f"   ID: {data.get('workflow_id')}")
            print(f"   Topic: {data.get('topic')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Test Mode: {'✅ Enabled' if data.get('test_mode') else '🚀 Disabled'}")
            print(f"   Progress: {data.get('progress')}%")
            print(f"   Current Stage: {data.get('current_stage')}/{data.get('total_stages')}")
            print(f"   Created: {data.get('created_at')}")
            print(f"   Updated: {data.get('updated_at')}")
            
            # Show stages
            stages = data.get("stages", [])
            if stages:
                print(f"\n📊 Stages:")
                for stage in stages:
                    status_icon = {
                        "pending": "⏳",
                        "running": "🔄",
                        "completed": "✅",
                        "failed": "❌"
                    }.get(stage.get("status"), "❓")
                    
                    print(f"   {status_icon} {stage.get('name')}: {stage.get('status')}")
                    if stage.get("error"):
                        print(f"      Error: {stage.get('error')}")
                        
        else:
            print(f"❌ Failed to fetch workflow: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    print("🧪 Patent Agent System - Workflow Viewer")
    print("=" * 50)
    
    # Show all workflows summary
    show_workflows_summary()
    
    # Show patent workflows specifically
    show_patent_workflows()
    
    # Show specific workflow details if available
    print(f"\n🔍 To view specific workflow details, use:")
    print(f"   python3 show_workflows.py <workflow_id>")
    
    # If command line argument provided, show specific workflow
    import sys
    if len(sys.argv) > 1:
        workflow_id = sys.argv[1]
        show_workflow_by_id(workflow_id)

if __name__ == "__main__":
    main()