#!/usr/bin/env python3
"""
Quick Test Script for Patent Agent Test Mode
Run this script to quickly test all agents in test mode
"""

import asyncio
import logging
import sys
import os

# Add the patent_agent_demo directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system_test import PatentAgentSystemTestMode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def quick_test():
    """Run a quick test of all agents"""
    print("🧪 Starting Patent Agent Test Mode Quick Test")
    print("=" * 50)
    
    # Test parameters
    topic = "智能图像识别系统"
    description = "一种基于深度学习的智能图像识别系统，能够自动识别和分类图像中的物体"
    
    print(f"📝 Test Topic: {topic}")
    print(f"📄 Test Description: {description}")
    print()
    
    try:
        # Initialize test system
        print("🚀 Initializing test system...")
        system = PatentAgentSystemTestMode()
        await system.start()
        print("✅ Test system initialized successfully")
        print()
        
        # Run simple test
        print("🧪 Running simple agent test...")
        result = await system.run_simple_test(topic, description)
        
        if result["success"]:
            print("✅ Simple test completed successfully!")
            print()
            
            # Display results
            print("📊 Test Results:")
            print("-" * 30)
            for agent_name, agent_result in result["test_results"].items():
                status = "✅ PASS" if agent_result["success"] else "❌ FAIL"
                time = f"{agent_result['execution_time']:.2f}s"
                content = "✅" if agent_result["has_content"] else "❌"
                print(f"{agent_name:<20} {status:<8} {time:<8} Content: {content}")
            
            print()
            
            # Summary
            total_agents = len(result["test_results"])
            successful_agents = sum(1 for r in result["test_results"].values() if r["success"])
            total_time = sum(r["execution_time"] for r in result["test_results"].values())
            
            print("📈 Summary:")
            print(f"   • Total agents tested: {total_agents}")
            print(f"   • Successful: {successful_agents}/{total_agents}")
            print(f"   • Total execution time: {total_time:.2f}s")
            print(f"   • Average time per agent: {total_time/total_agents:.2f}s")
            
            if successful_agents == total_agents:
                print("\n🎉 All agents passed the test!")
            else:
                print(f"\n⚠️  {total_agents - successful_agents} agents failed the test")
                
        else:
            print(f"❌ Simple test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Shutdown system
        print("\n🛑 Shutting down test system...")
        try:
            await system.stop()
            print("✅ Test system shutdown complete")
        except Exception as e:
            print(f"⚠️  Error during shutdown: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed")

async def workflow_test():
    """Run a workflow test"""
    print("🔄 Starting Patent Agent Workflow Test")
    print("=" * 50)
    
    # Test parameters
    topic = "智能图像识别系统"
    description = "一种基于深度学习的智能图像识别系统，能够自动识别和分类图像中的物体"
    
    print(f"📝 Test Topic: {topic}")
    print(f"📄 Test Description: {description}")
    print()
    
    try:
        # Initialize test system
        print("🚀 Initializing test system...")
        system = PatentAgentSystemTestMode()
        await system.start()
        print("✅ Test system initialized successfully")
        print()
        
        # Execute workflow
        print("🔄 Starting test workflow...")
        result = await system.execute_workflow(topic, description)
        
        if result["success"]:
            print(f"✅ Test workflow started: {result['workflow_id']}")
            print()
            
            # Monitor workflow
            workflow_id = result["workflow_id"]
            print("📊 Monitoring workflow for 5 seconds...")
            
            for i in range(5):
                await asyncio.sleep(1)
                status = await system.get_workflow_status(workflow_id)
                if status["success"]:
                    print(f"   • {i+1}s: Workflow active")
                else:
                    print(f"   • {i+1}s: Workflow error - {status.get('error')}")
                    break
            
            print("\n✅ Workflow test completed")
            
        else:
            print(f"❌ Workflow test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during workflow test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Shutdown system
        print("\n🛑 Shutting down test system...")
        try:
            await system.stop()
            print("✅ Test system shutdown complete")
        except Exception as e:
            print(f"⚠️  Error during shutdown: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Workflow test completed")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Patent Agent Test Mode")
    parser.add_argument("--workflow", action="store_true", help="Run workflow test instead of simple test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.workflow:
        asyncio.run(workflow_test())
    else:
        asyncio.run(quick_test())

if __name__ == "__main__":
    main()