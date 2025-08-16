#!/usr/bin/env python3
"""
Real Mode Debug Script for Patent Agent System
Diagnoses issues with real API calls and dependencies
"""

import asyncio
import logging
import sys
import os
import time
import json
import importlib
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking Dependencies...")
    print("=" * 50)
    
    required_packages = [
        "openai",
        "anthropic", 
        "requests",
        "aiohttp",
        "asyncio",
        "json",
        "logging",
        "typing",
        "uuid",
        "time"
    ]
    
    missing_packages = []
    available_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            available_packages.append(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    print()
    print("📊 Dependency Summary:")
    print(f"   • Available: {len(available_packages)}/{len(required_packages)}")
    print(f"   • Missing: {len(missing_packages)}")
    
    if missing_packages:
        print(f"   • Missing packages: {', '.join(missing_packages)}")
        print()
        print("💡 To install missing packages:")
        print("   pip install " + " ".join(missing_packages))
    
    return len(missing_packages) == 0

def check_api_config():
    """Check API configuration"""
    print("\n🔍 Checking API Configuration...")
    print("=" * 50)
    
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "ZHIPU_API_KEY": os.getenv("ZHIPU_API_KEY")
    }
    
    configured_apis = []
    missing_apis = []
    
    for api_name, api_key in api_keys.items():
        if api_key:
            configured_apis.append(api_name)
            print(f"✅ {api_name} - Configured")
        else:
            missing_apis.append(api_name)
            print(f"❌ {api_name} - Not configured")
    
    print()
    print("📊 API Configuration Summary:")
    print(f"   • Configured: {len(configured_apis)}/{len(api_keys)}")
    print(f"   • Missing: {len(missing_apis)}")
    
    if missing_apis:
        print(f"   • Missing APIs: {', '.join(missing_apis)}")
        print()
        print("💡 To configure API keys:")
        print("   export OPENAI_API_KEY='your-openai-key'")
        print("   export ANTHROPIC_API_KEY='your-anthropic-key'")
        print("   export GOOGLE_API_KEY='your-google-key'")
        print("   export ZHIPU_API_KEY='your-zhipu-key'")
    
    return len(configured_apis) > 0

def check_network_connectivity():
    """Check network connectivity to API endpoints"""
    print("\n🔍 Checking Network Connectivity...")
    print("=" * 50)
    
    try:
        import requests
    except ImportError:
        print("❌ requests module not available - cannot check network connectivity")
        print("💡 Install requests: pip install requests")
        return False
    
    endpoints = {
        "OpenAI API": "https://api.openai.com/v1/models",
        "Anthropic API": "https://api.anthropic.com/v1/messages",
        "Google API": "https://generativelanguage.googleapis.com/v1beta/models",
        "Zhipu API": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    }
    
    accessible_endpoints = []
    inaccessible_endpoints = []
    
    for endpoint_name, endpoint_url in endpoints.items():
        try:
            response = requests.get(endpoint_url, timeout=5)
            if response.status_code in [200, 401, 403]:  # 401/403 means endpoint is reachable but needs auth
                accessible_endpoints.append(endpoint_name)
                print(f"✅ {endpoint_name} - Accessible")
            else:
                inaccessible_endpoints.append(endpoint_name)
                print(f"⚠️  {endpoint_name} - Unexpected status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            inaccessible_endpoints.append(endpoint_name)
            print(f"❌ {endpoint_name} - Not accessible: {e}")
    
    print()
    print("📊 Network Connectivity Summary:")
    print(f"   • Accessible: {len(accessible_endpoints)}/{len(endpoints)}")
    print(f"   • Inaccessible: {len(inaccessible_endpoints)}")
    
    if inaccessible_endpoints:
        print(f"   • Inaccessible endpoints: {', '.join(inaccessible_endpoints)}")
    
    return len(accessible_endpoints) > 0

def check_patent_agent_demo_structure():
    """Check if patent_agent_demo directory structure is correct"""
    print("\n🔍 Checking Patent Agent Demo Structure...")
    print("=" * 50)
    
    required_files = [
        "patent_agent_demo/__init__.py",
        "patent_agent_demo/agents/__init__.py",
        "patent_agent_demo/agents/base_agent.py",
        "patent_agent_demo/agents/planner_agent.py",
        "patent_agent_demo/agents/searcher_agent.py",
        "patent_agent_demo/agents/writer_agent.py",
        "patent_agent_demo/agents/reviewer_agent.py",
        "patent_agent_demo/agents/rewriter_agent.py",
        "patent_agent_demo/agents/discusser_agent.py",
        "patent_agent_demo/agents/coordinator_agent.py",
        "patent_agent_demo/message_bus.py",
        "patent_agent_demo/context_manager.py"
    ]
    
    existing_files = []
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - Missing")
    
    print()
    print("📊 File Structure Summary:")
    print(f"   • Existing: {len(existing_files)}/{len(required_files)}")
    print(f"   • Missing: {len(missing_files)}")
    
    if missing_files:
        print(f"   • Missing files: {', '.join(missing_files)}")
    
    return len(missing_files) == 0

def check_imports():
    """Check if we can import the patent agent system"""
    print("\n🔍 Checking Imports...")
    print("=" * 50)
    
    try:
        # Add the patent_agent_demo directory to the path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))
        
        # Try to import the real system
        from patent_agent_demo.patent_agent_system_real import PatentAgentSystemReal
        print("✅ PatentAgentSystemReal - Import successful")
        
        # Try to import individual agents
        from patent_agent_demo.agents.planner_agent import PlannerAgent
        print("✅ PlannerAgent - Import successful")
        
        from patent_agent_demo.agents.searcher_agent import SearcherAgent
        print("✅ SearcherAgent - Import successful")
        
        from patent_agent_demo.agents.writer_agent import WriterAgent
        print("✅ WriterAgent - Import successful")
        
        from patent_agent_demo.agents.reviewer_agent import ReviewerAgent
        print("✅ ReviewerAgent - Import successful")
        
        from patent_agent_demo.agents.rewriter_agent import RewriterAgent
        print("✅ RewriterAgent - Import successful")
        
        from patent_agent_demo.agents.discusser_agent import DiscusserAgent
        print("✅ DiscusserAgent - Import successful")
        
        from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
        print("✅ CoordinatorAgent - Import successful")
        
        print()
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print()
        print("💡 Common import issues:")
        print("   • Missing dependencies (run: pip install -r requirements.txt)")
        print("   • Incorrect file structure")
        print("   • Python path issues")
        return False

async def test_individual_agent(agent_name: str, agent_class):
    """Test individual agent"""
    print(f"\n🔍 Testing {agent_name}...")
    print("-" * 30)
    
    try:
        # Create agent instance
        agent = agent_class()
        print(f"✅ {agent_name} - Created successfully")
        
        # Start agent
        await agent.start()
        print(f"✅ {agent_name} - Started successfully")
        
        # Test simple task
        test_task = {
            "type": "test",
            "topic": "test topic",
            "description": "test description"
        }
        
        result = await agent.execute_task(test_task)
        print(f"✅ {agent_name} - Task executed successfully")
        print(f"   • Success: {result.success}")
        print(f"   • Execution time: {result.execution_time:.2f}s")
        print(f"   • Has content: {bool(result.data.get('content'))}")
        
        # Stop agent
        await agent.stop()
        print(f"✅ {agent_name} - Stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ {agent_name} - Failed: {e}")
        return False

async def test_all_agents():
    """Test all agents individually"""
    print("\n🔍 Testing All Agents Individually...")
    print("=" * 50)
    
    try:
        # Add the patent_agent_demo directory to the path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))
        
        # Import agents
        from patent_agent_demo.agents.planner_agent import PlannerAgent
        from patent_agent_demo.agents.searcher_agent import SearcherAgent
        from patent_agent_demo.agents.writer_agent import WriterAgent
        from patent_agent_demo.agents.reviewer_agent import ReviewerAgent
        from patent_agent_demo.agents.rewriter_agent import RewriterAgent
        from patent_agent_demo.agents.discusser_agent import DiscusserAgent
        from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent
        
        agents = {
            "PlannerAgent": PlannerAgent,
            "SearcherAgent": SearcherAgent,
            "WriterAgent": WriterAgent,
            "ReviewerAgent": ReviewerAgent,
            "RewriterAgent": RewriterAgent,
            "DiscusserAgent": DiscusserAgent,
            "CoordinatorAgent": CoordinatorAgent
        }
        
        successful_agents = []
        failed_agents = []
        
        for agent_name, agent_class in agents.items():
            success = await test_individual_agent(agent_name, agent_class)
            if success:
                successful_agents.append(agent_name)
            else:
                failed_agents.append(agent_name)
        
        print()
        print("📊 Agent Test Summary:")
        print(f"   • Successful: {len(successful_agents)}/{len(agents)}")
        print(f"   • Failed: {len(failed_agents)}")
        
        if successful_agents:
            print(f"   • Successful agents: {', '.join(successful_agents)}")
        
        if failed_agents:
            print(f"   • Failed agents: {', '.join(failed_agents)}")
        
        return len(failed_agents) == 0
        
    except Exception as e:
        print(f"❌ Agent testing failed: {e}")
        return False

def generate_debug_report():
    """Generate a comprehensive debug report"""
    print("🔍 Patent Agent System Debug Report")
    print("=" * 60)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Run all checks
    deps_ok = check_dependencies()
    api_ok = check_api_config()
    network_ok = check_network_connectivity()
    structure_ok = check_patent_agent_demo_structure()
    imports_ok = check_imports()
    
    print("\n" + "=" * 60)
    print("📊 OVERALL DIAGNOSIS")
    print("=" * 60)
    
    issues = []
    if not deps_ok:
        issues.append("Missing dependencies")
    if not api_ok:
        issues.append("No API keys configured")
    if not network_ok:
        issues.append("Network connectivity issues")
    if not structure_ok:
        issues.append("Missing files in patent_agent_demo")
    if not imports_ok:
        issues.append("Import failures")
    
    if not issues:
        print("✅ All checks passed! System should work correctly.")
        print()
        print("🚀 Next steps:")
        print("   1. Run: python3 test_patent_agents_real.py")
        print("   2. Run: python3 test_patent_agents_real.py --workflow")
    else:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   • {issue}")
        print()
        print("🔧 Recommended fixes:")
        if not deps_ok:
            print("   1. Install missing dependencies: pip install openai anthropic requests aiohttp")
        if not api_ok:
            print("   2. Configure API keys in environment variables")
        if not network_ok:
            print("   3. Check network connectivity and firewall settings")
        if not structure_ok:
            print("   4. Ensure patent_agent_demo directory structure is correct")
        if not imports_ok:
            print("   5. Fix import issues by installing dependencies and checking file structure")
    
    return len(issues) == 0

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Patent Agent Real Mode Debug")
    parser.add_argument("--agents", action="store_true", help="Test individual agents")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Generate debug report
    all_ok = generate_debug_report()
    
    # Test individual agents if requested
    if args.agents and all_ok:
        print("\n" + "=" * 60)
        print("🧪 TESTING INDIVIDUAL AGENTS")
        print("=" * 60)
        await test_all_agents()

if __name__ == "__main__":
    asyncio.run(main())