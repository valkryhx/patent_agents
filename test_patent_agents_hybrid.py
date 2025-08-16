#!/usr/bin/env python3
"""
Hybrid Test Script for Patent Agent System
Tests real agents (first 3) + test agents (remaining)
"""

import asyncio
import logging
import sys
import os
import time
import json
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Try to import the hybrid system
try:
    # Add the patent_agent_demo directory to the path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))
    
    from patent_agent_demo.patent_agent_system_hybrid import PatentAgentSystemHybrid
    HYBRID_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import hybrid system: {e}")
    print("This might be due to missing dependencies for real agents.")
    HYBRID_AVAILABLE = False

# Mock hybrid system for testing when real system is not available
class MockHybridSystem:
    """Mock hybrid system for testing when real system is not available"""
    
    def __init__(self):
        self.agents = {}
        self.logger = logging.getLogger("mock_hybrid_system")
        
    async def start(self):
        """Start the mock hybrid system"""
        self.logger.info("Starting Mock Hybrid System")
        print("✅ Mock hybrid system started")
        
    async def stop(self):
        """Stop the mock hybrid system"""
        self.logger.info("Stopping Mock Hybrid System")
        print("✅ Mock hybrid system stopped")
        
    async def run_hybrid_test(self, topic: str, description: str) -> Dict[str, Any]:
        """Run mock hybrid test"""
        self.logger.info("Running mock hybrid test")
        
        # Simulate test results
        test_results = {
            "planner_agent": {
                "success": True,
                "execution_time": 2.5,
                "has_content": True,
                "hybrid_mode": True,
                "agent_type": "real",
                "note": "Mock result - would be real API call"
            },
            "searcher_agent": {
                "success": True,
                "execution_time": 1.8,
                "has_content": True,
                "hybrid_mode": True,
                "agent_type": "real",
                "note": "Mock result - would be real API call"
            },
            "writer_agent": {
                "success": True,
                "execution_time": 3.2,
                "has_content": True,
                "hybrid_mode": True,
                "agent_type": "real",
                "note": "Mock result - would be real API call"
            },
            "reviewer_agent": {
                "success": True,
                "execution_time": 0.1,
                "has_content": True,
                "hybrid_mode": True,
                "agent_type": "test",
                "note": "Test mode result"
            },
            "rewriter_agent": {
                "success": True,
                "execution_time": 0.1,
                "has_content": True,
                "hybrid_mode": True,
                "agent_type": "test",
                "note": "Test mode result"
            },
            "discusser_agent": {
                "success": True,
                "execution_time": 0.1,
                "has_content": True,
                "hybrid_mode": True,
                "agent_type": "test",
                "note": "Test mode result"
            },
            "coordinator_agent": {
                "success": True,
                "execution_time": 0.1,
                "has_content": True,
                "hybrid_mode": True,
                "agent_type": "test",
                "note": "Test mode result"
            }
        }
        
        return {
            "success": True,
            "test_results": test_results,
            "hybrid_mode": True,
            "timestamp": time.time(),
            "note": "Mock results - real system not available"
        }
        
    async def test_real_agents_only(self, topic: str, description: str) -> Dict[str, Any]:
        """Test only real agents (mock)"""
        self.logger.info("Testing real agents only (mock)")
        
        test_results = {
            "planner_agent": {
                "success": True,
                "execution_time": 2.5,
                "has_content": True,
                "agent_type": "real",
                "note": "Mock result - would be real API call"
            },
            "searcher_agent": {
                "success": True,
                "execution_time": 1.8,
                "has_content": True,
                "agent_type": "real",
                "note": "Mock result - would be real API call"
            },
            "writer_agent": {
                "success": True,
                "execution_time": 3.2,
                "has_content": True,
                "agent_type": "real",
                "note": "Mock result - would be real API call"
            }
        }
        
        return {
            "success": True,
            "test_results": test_results,
            "agent_type": "real_only",
            "timestamp": time.time(),
            "note": "Mock results - real system not available"
        }

async def hybrid_test():
    """Run hybrid test of real + test agents"""
    print("🧪 Starting Patent Agent Hybrid Test Mode")
    print("=" * 60)
    
    # Test parameters
    topic = "智能图像识别系统"
    description = "一种基于深度学习的智能图像识别系统，能够自动识别和分类图像中的物体"
    
    print(f"📝 Test Topic: {topic}")
    print(f"📄 Test Description: {description}")
    print()
    
    # Choose system based on availability
    if HYBRID_AVAILABLE:
        print("🔧 Using REAL hybrid system")
        system = PatentAgentSystemHybrid()
    else:
        print("🔧 Using MOCK hybrid system (real system not available)")
        system = MockHybridSystem()
    
    try:
        # Initialize system
        print("🚀 Initializing hybrid system...")
        await system.start()
        print("✅ Hybrid system initialized successfully")
        print()
        
        # Run hybrid test
        print("🧪 Running hybrid agent test...")
        result = await system.run_hybrid_test(topic, description)
        
        if result["success"]:
            print("✅ Hybrid test completed successfully!")
            print()
            
            # Display results
            print("📊 Hybrid Test Results:")
            print("-" * 60)
            
            real_agents = []
            test_agents = []
            
            for agent_name, agent_result in result["test_results"].items():
                status = "✅ PASS" if agent_result["success"] else "❌ FAIL"
                time = f"{agent_result['execution_time']:.2f}s"
                agent_type = agent_result.get("agent_type", "unknown")
                note = agent_result.get("note", "")
                
                if agent_type == "real":
                    real_agents.append((agent_name, status, time, note))
                else:
                    test_agents.append((agent_name, status, time, note))
            
            # Display real agents
            print("🤖 REAL AGENTS (API calls):")
            for agent_name, status, time, note in real_agents:
                print(f"  {agent_name:<20} {status:<8} {time:<8} {note}")
            
            print()
            
            # Display test agents
            print("🧪 TEST AGENTS (mock responses):")
            for agent_name, status, time, note in test_agents:
                print(f"  {agent_name:<20} {status:<8} {time:<8} {note}")
            
            print()
            
            # Summary
            total_agents = len(result["test_results"])
            successful_agents = sum(1 for r in result["test_results"].values() if r["success"])
            total_time = sum(r["execution_time"] for r in result["test_results"].values())
            
            real_agent_count = len(real_agents)
            test_agent_count = len(test_agents)
            real_time = sum(r["execution_time"] for r in result["test_results"].values() if r.get("agent_type") == "real")
            test_time = sum(r["execution_time"] for r in result["test_results"].values() if r.get("agent_type") == "test")
            
            print("📈 Summary:")
            print(f"   • Total agents tested: {total_agents}")
            print(f"   • Real agents: {real_agent_count} (API calls)")
            print(f"   • Test agents: {test_agent_count} (mock responses)")
            print(f"   • Successful: {successful_agents}/{total_agents}")
            print(f"   • Total execution time: {total_time:.2f}s")
            print(f"   • Real agents time: {real_time:.2f}s")
            print(f"   • Test agents time: {test_time:.2f}s")
            
            if successful_agents == total_agents:
                print("\n🎉 All agents passed the hybrid test!")
            else:
                print(f"\n⚠️  {total_agents - successful_agents} agents failed the test")
                
        else:
            print(f"❌ Hybrid test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during hybrid test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Shutdown system
        print("\n🛑 Shutting down hybrid system...")
        try:
            await system.stop()
            print("✅ Hybrid system shutdown complete")
        except Exception as e:
            print(f"⚠️  Error during shutdown: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Hybrid test completed")

async def real_agents_only_test():
    """Test only real agents"""
    print("🤖 Starting Real Agents Only Test")
    print("=" * 60)
    
    # Test parameters
    topic = "智能图像识别系统"
    description = "一种基于深度学习的智能图像识别系统，能够自动识别和分类图像中的物体"
    
    print(f"📝 Test Topic: {topic}")
    print(f"📄 Test Description: {description}")
    print()
    
    # Choose system based on availability
    if HYBRID_AVAILABLE:
        print("🔧 Using REAL hybrid system")
        system = PatentAgentSystemHybrid()
    else:
        print("🔧 Using MOCK hybrid system (real system not available)")
        system = MockHybridSystem()
    
    try:
        # Initialize system
        print("🚀 Initializing system...")
        await system.start()
        print("✅ System initialized successfully")
        print()
        
        # Run real agents only test
        print("🤖 Testing real agents only...")
        result = await system.test_real_agents_only(topic, description)
        
        if result["success"]:
            print("✅ Real agents test completed successfully!")
            print()
            
            # Display results
            print("📊 Real Agents Test Results:")
            print("-" * 40)
            
            for agent_name, agent_result in result["test_results"].items():
                status = "✅ PASS" if agent_result["success"] else "❌ FAIL"
                time = f"{agent_result['execution_time']:.2f}s"
                note = agent_result.get("note", "")
                
                print(f"{agent_name:<20} {status:<8} {time:<8} {note}")
            
            print()
            
            # Summary
            total_agents = len(result["test_results"])
            successful_agents = sum(1 for r in result["test_results"].values() if r["success"])
            total_time = sum(r["execution_time"] for r in result["test_results"].values())
            
            print("📈 Summary:")
            print(f"   • Real agents tested: {total_agents}")
            print(f"   • Successful: {successful_agents}/{total_agents}")
            print(f"   • Total execution time: {total_time:.2f}s")
            print(f"   • Average time per agent: {total_time/total_agents:.2f}s")
            
            if successful_agents == total_agents:
                print("\n🎉 All real agents passed the test!")
            else:
                print(f"\n⚠️  {total_agents - successful_agents} real agents failed the test")
                
        else:
            print(f"❌ Real agents test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during real agents test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Shutdown system
        print("\n🛑 Shutting down system...")
        try:
            await system.stop()
            print("✅ System shutdown complete")
        except Exception as e:
            print(f"⚠️  Error during shutdown: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Real agents test completed")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Patent Agent Hybrid Test Mode")
    parser.add_argument("--real-only", action="store_true", help="Test only real agents")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.real_only:
        asyncio.run(real_agents_only_test())
    else:
        asyncio.run(hybrid_test())

if __name__ == "__main__":
    main()