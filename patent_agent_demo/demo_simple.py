#!/usr/bin/env python3
"""
Simple Patent Agent Demo
Quick demonstration of the multi-agent patent development system
"""

import asyncio
import logging
from patent_agent_system import PatentAgentSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simple_demo():
    """Run a simple demo workflow"""
    try:
        print("🚀 Starting Patent Agent Demo...")
        
        # Initialize the system
        patent_system = PatentAgentSystem()
        await patent_system.start()
        
        print("✅ System started successfully!")
        
        # Show system status
        status = await patent_system.get_system_status()
        print(f"📊 System Status: {status.system_health}")
        print(f"🤖 Active Agents: {status.active_agents}/{status.total_agents}")
        
        # Run a simple patent development workflow
        print("\n🔬 Starting Patent Development Workflow...")
        
        topic = "Quantum Computing Optimization Algorithm"
        description = "A novel algorithm for optimizing quantum circuit compilation and execution"
        
        print(f"📝 Topic: {topic}")
        print(f"📋 Description: {description}")
        
        # Start the workflow
        result = await patent_system.develop_patent(topic, description)
        
        print("\n🎯 Patent Development Complete!")
        print(f"📊 Status: {result.get('status', 'Unknown')}")
        
        if 'patent_summary' in result:
            summary = result['patent_summary']
            print(f"📄 Title: {summary.get('title', 'N/A')}")
            print(f"✅ Status: {summary.get('status', 'N/A')}")
            print(f"🎯 Confidence: {summary.get('confidence_score', 0):.1%}")
        
        # Show final system status
        final_status = await patent_system.get_system_status()
        print(f"\n📈 Final System Status: {final_status.system_health}")
        print(f"⏱️  Total Runtime: {final_status.uptime:.1f} seconds")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        logger.error(f"Demo error: {e}")
    finally:
        # Cleanup
        if 'patent_system' in locals():
            await patent_system.stop()
            print("🛑 System stopped.")

if __name__ == "__main__":
    asyncio.run(simple_demo())