#!/usr/bin/env python3
"""
Start Patent Writing Workflow
Easy script to start workflows with different topics
"""

import asyncio
import httpx
import json
import sys

# Service URL
BASE_URL = "http://localhost:8000"

# Predefined workflow templates
WORKFLOW_TEMPLATES = {
    "ai": {
        "topic": "AI-Powered Patent Analysis System",
        "description": "A system for AI-powered patent analysis and evaluation using machine learning algorithms",
        "workflow_type": "enhanced"
    },
    "blockchain": {
        "topic": "Blockchain-Based IP Management System", 
        "description": "A blockchain-based intellectual property management system for secure patent tracking",
        "workflow_type": "enhanced"
    },
    "quantum": {
        "topic": "Quantum Computing Patent Framework",
        "description": "A framework for quantum computing patent applications and quantum algorithm protection",
        "workflow_type": "enhanced"
    },
    "medical": {
        "topic": "Smart Medical Device Monitoring System",
        "description": "An intelligent medical device monitoring system with real-time health data analysis",
        "workflow_type": "enhanced"
    },
    "iot": {
        "topic": "IoT Smart Home Security System",
        "description": "An Internet of Things smart home security system with AI-powered threat detection",
        "workflow_type": "enhanced"
    },
    "cybersecurity": {
        "topic": "Advanced Cybersecurity Threat Detection",
        "description": "An advanced cybersecurity system for real-time threat detection and response",
        "workflow_type": "enhanced"
    }
}

async def start_workflow(topic, description, workflow_type="enhanced"):
    """Start a workflow with custom topic and description"""
    async with httpx.AsyncClient() as client:
        workflow_request = {
            "topic": topic,
            "description": description,
            "workflow_type": workflow_type
        }
        
        try:
            print(f"📋 Starting workflow: {topic}")
            print(f"📝 Description: {description}")
            
            response = await client.post(
                f"{BASE_URL}/coordinator/workflow/start",
                json=workflow_request,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ Workflow started successfully!")
                print(f"🆔 Workflow ID: {workflow_id}")
                print(f"📊 Status: {result['status']}")
                return workflow_id
            else:
                print(f"❌ Failed to start workflow: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting workflow: {str(e)}")
            return None

async def start_template_workflow(template_name):
    """Start a workflow using a predefined template"""
    if template_name not in WORKFLOW_TEMPLATES:
        print(f"❌ Template '{template_name}' not found!")
        print(f"Available templates: {list(WORKFLOW_TEMPLATES.keys())}")
        return None
    
    template = WORKFLOW_TEMPLATES[template_name]
    return await start_workflow(template["topic"], template["description"], template["workflow_type"])

async def monitor_workflow(workflow_id):
    """Monitor workflow progress"""
    async with httpx.AsyncClient() as client:
        print(f"\n📊 Monitoring workflow {workflow_id}...")
        
        for i in range(30):  # Monitor for up to 30 iterations
            await asyncio.sleep(2)  # Check every 2 seconds
            
            try:
                status_response = await client.get(
                    f"{BASE_URL}/coordinator/workflow/{workflow_id}/status",
                    timeout=5.0
                )
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"📈 Progress: {status['progress']:.1f}% - Status: {status['status']}")
                    
                    # Show completed stages
                    for stage in status['stages']:
                        if stage['status'] == 'completed':
                            print(f"   ✅ {stage['name']} completed")
                    
                    if status['status'] in ['completed', 'failed']:
                        print(f"🏁 Workflow {status['status']}!")
                        break
                else:
                    print(f"❌ Failed to get status: {status_response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error monitoring: {str(e)}")

def print_usage():
    """Print usage instructions"""
    print("🎯 Patent Writing Workflow Starter")
    print("=" * 40)
    print("Usage:")
    print("  python3 start_workflow.py template <template_name>")
    print("  python3 start_workflow.py custom <topic> <description>")
    print("  python3 start_workflow.py list")
    print("\nExamples:")
    print("  python3 start_workflow.py template ai")
    print("  python3 start_workflow.py template blockchain")
    print("  python3 start_workflow.py custom 'My Patent Topic' 'My patent description'")
    print("\nAvailable templates:")
    for name, template in WORKFLOW_TEMPLATES.items():
        print(f"  {name}: {template['topic']}")

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    if command == "list":
        print("📋 Available workflow templates:")
        for name, template in WORKFLOW_TEMPLATES.items():
            print(f"\n🔹 {name.upper()}:")
            print(f"   Topic: {template['topic']}")
            print(f"   Description: {template['description']}")
    
    elif command == "template":
        if len(sys.argv) < 3:
            print("❌ Please specify a template name!")
            print("Available templates:", list(WORKFLOW_TEMPLATES.keys()))
            return
        
        template_name = sys.argv[2]
        workflow_id = await start_template_workflow(template_name)
        
        if workflow_id:
            # Ask if user wants to monitor
            monitor = input("\n📊 Do you want to monitor this workflow? (y/n): ").lower()
            if monitor in ['y', 'yes']:
                await monitor_workflow(workflow_id)
    
    elif command == "custom":
        if len(sys.argv) < 4:
            print("❌ Please provide topic and description!")
            print("Usage: python3 start_workflow.py custom <topic> <description>")
            return
        
        topic = sys.argv[2]
        description = sys.argv[3]
        workflow_id = await start_workflow(topic, description)
        
        if workflow_id:
            # Ask if user wants to monitor
            monitor = input("\n📊 Do you want to monitor this workflow? (y/n): ").lower()
            if monitor in ['y', 'yes']:
                await monitor_workflow(workflow_id)
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    asyncio.run(main())