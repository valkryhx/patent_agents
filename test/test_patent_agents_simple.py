#!/usr/bin/env python3
"""
Simple Test Script for Patent Agent Test Mode
This version only uses Python standard library
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

# Mock classes for testing
class MockMessageBus:
    """Mock message bus for testing"""
    
    def __init__(self):
        self.messages = []
        self.agents = {}
        
    async def register_agent(self, name: str, capabilities: List[str]):
        self.agents[name] = capabilities
        print(f"✅ Registered agent: {name} with capabilities: {capabilities}")
        
    async def unregister_agent(self, name: str):
        if name in self.agents:
            del self.agents[name]
            print(f"✅ Unregistered agent: {name}")
            
    async def send_message(self, message):
        self.messages.append(message)
        print(f"📨 Message sent: {message.get('type', 'unknown')} from {message.get('sender', 'unknown')}")
        
    async def get_message(self, agent_name: str):
        # Return None to simulate no messages
        return None

class MockContextManager:
    """Mock context manager for testing"""
    
    def __init__(self):
        self.contexts = {}
        
    async def initialize(self):
        print("✅ Context manager initialized")
        
    async def shutdown(self):
        print("✅ Context manager shutdown")
        
    async def store_context(self, workflow_id: str, context: Dict[str, Any]):
        self.contexts[workflow_id] = context
        print(f"✅ Context stored for workflow: {workflow_id}")
        
    async def get_context(self, workflow_id: str):
        return self.contexts.get(workflow_id)

class MockAgent:
    """Mock agent for testing"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.status = "IDLE"
        self.test_counter = 0
        self.logger = logging.getLogger(f"test_agent.{name}")
        
    async def start(self):
        self.status = "RUNNING"
        self.logger.info(f"{self.name} started in TEST MODE")
        print(f"✅ {self.name} started")
        
    async def stop(self):
        self.status = "STOPPED"
        self.logger.info(f"{self.name} stopped")
        print(f"✅ {self.name} stopped")
        
    async def execute_task(self, task_data: Dict[str, Any]):
        self.test_counter += 1
        task_type = task_data.get("type", "unknown")
        topic = task_data.get("topic", "测试主题")
        description = task_data.get("description", "测试描述")
        
        self.logger.info(f"TEST MODE: {self.name} executing task: {task_type}")
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Generate test content
        content = self._generate_test_content(task_type, topic, description)
        
        return {
            "success": True,
            "data": {
                "content": content,
                "test_mode": True,
                "agent": self.name,
                "task_type": task_type
            },
            "execution_time": 0.1,
            "metadata": {
                "test_mode": True,
                "agent": self.name,
                "counter": self.test_counter
            }
        }
        
    def _generate_test_content(self, task_type: str, topic: str, description: str) -> str:
        """Generate test content based on agent type and task"""
        base_content = f"# {self.name} 测试结果\n\n## 任务类型: {task_type}\n## 主题: {topic}\n## 描述: {description}\n\n"
        
        if "planner" in self.name:
            return base_content + "## 专利规划策略\n- 技术验证阶段: 2-3个月\n- 专利申请准备: 1-2个月\n- 专利申请提交: 1个月\n\n## 风险评估\n- 技术风险: 中等\n- 市场风险: 低\n- 成功概率: 75%"
        elif "writer" in self.name:
            return base_content + "## 专利申请文件\n### 发明名称\n{topic}\n\n### 技术领域\n本发明涉及{description}技术领域。\n\n### 权利要求书\n1. 一种{description}方法，其特征在于...\n\n2. 根据权利要求1所述的方法..."
        elif "searcher" in self.name:
            return base_content + "## 专利检索结果\n### 相关专利 (共找到15篇)\n1. CN123456789A - 一种{description}方法\n2. CN987654321B - {description}系统及装置\n3. US20230012345A1 - Method for {description}\n\n## 技术分析\n- 现有技术主要集中在基础功能\n- 智能化处理能力有待提升\n- 建议重点关注AI技术融合"
        elif "reviewer" in self.name:
            return base_content + "## 审查结果\n### 新颖性审查: ✅ 通过\n### 创造性审查: ✅ 通过\n### 实用性审查: ✅ 通过\n\n## 审查意见\n- 技术方案完整，逻辑清晰\n- 权利要求书撰写规范\n- 建议在实施例中增加具体参数"
        elif "rewriter" in self.name:
            return base_content + "## 重写结果\n### 优化后的专利申请文件\n\n### 发明名称\n一种改进的{description}方法及系统\n\n### 技术方案\n1. 引入深度学习算法\n2. 采用并行计算架构\n3. 集成自适应优化机制\n\n## 改进点\n- 技术方案更加具体\n- 权利要求更加清晰\n- 实施例更加详细"
        elif "discusser" in self.name:
            return base_content + "## 技术讨论\n### 技术发展趋势\n1. 智能化方向\n2. 集成化趋势\n3. 标准化需求\n\n### 专利申请策略\n1. 基础专利布局\n2. 应用专利保护\n3. 改进专利申请\n\n## 团队意见\n- 技术团队: 方案具有创新性\n- 法律团队: 策略合理\n- 市场团队: 前景广阔"
        elif "coordinator" in self.name:
            return base_content + "## 工作流协调状态\n### 任务分配\n1. 规划阶段: ✅ 已完成\n2. 检索阶段: ✅ 已完成\n3. 撰写阶段: 🔄 进行中 (60%)\n4. 审查阶段: ⏳ 等待中\n5. 重写阶段: ⏳ 等待中\n6. 讨论阶段: ⏳ 等待中\n\n## 协调策略\n- 并行处理\n- 依赖管理\n- 质量控制\n- 进度监控"
        else:
            return base_content + "## 测试内容\n这是一个测试模式生成的内容，用于验证智能体功能。"
        
    async def get_status(self):
        return {
            "name": self.name,
            "status": self.status,
            "capabilities": self.capabilities,
            "test_mode": True
        }

class MockPatentAgentSystem:
    """Mock patent agent system for testing"""
    
    def __init__(self):
        self.agents = {}
        self.workflow_id = None
        self.message_bus = MockMessageBus()
        self.context_manager = MockContextManager()
        self.logger = logging.getLogger("test_system")
        
    async def start(self):
        """Start the test system"""
        try:
            self.logger.info("Starting Patent Agent System in TEST MODE")
            
            # Initialize components
            await self.context_manager.initialize()
            
            # Create mock agents
            agent_configs = [
                ("planner_agent", ["patent_planning", "strategy_development"]),
                ("writer_agent", ["patent_drafting", "technical_writing"]),
                ("searcher_agent", ["patent_search", "prior_art_analysis"]),
                ("reviewer_agent", ["patent_review", "quality_assessment"]),
                ("rewriter_agent", ["patent_rewriting", "content_optimization"]),
                ("discusser_agent", ["patent_discussion", "collaborative_analysis"]),
                ("coordinator_agent", ["workflow_coordination", "task_scheduling"])
            ]
            
            for name, capabilities in agent_configs:
                self.agents[name] = MockAgent(name, capabilities)
                await self.agents[name].start()
                
            self.logger.info("All test agents started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting test system: {e}")
            raise
            
    async def stop(self):
        """Stop the test system"""
        try:
            self.logger.info("Stopping Patent Agent System Test Mode")
            
            # Stop all agents
            for name, agent in self.agents.items():
                await agent.stop()
                
            # Shutdown components
            await self.context_manager.shutdown()
            
            self.logger.info("Patent Agent System Test Mode stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping test system: {e}")
            
    async def run_simple_test(self, topic: str, description: str) -> Dict[str, Any]:
        """Run simple test of all agents"""
        try:
            self.logger.info("Running simple test...")
            
            test_results = {}
            
            # Test each agent individually
            test_tasks = {
                "planner_agent": {
                    "type": "patent_planning",
                    "topic": topic,
                    "description": description
                },
                "searcher_agent": {
                    "type": "patent_search",
                    "topic": topic,
                    "description": description
                },
                "writer_agent": {
                    "type": "patent_drafting",
                    "topic": topic,
                    "description": description
                },
                "reviewer_agent": {
                    "type": "patent_review",
                    "topic": topic,
                    "description": description
                },
                "rewriter_agent": {
                    "type": "patent_rewriting",
                    "topic": topic,
                    "description": description
                },
                "discusser_agent": {
                    "type": "patent_discussion",
                    "topic": topic,
                    "description": description
                },
                "coordinator_agent": {
                    "type": "workflow_coordination",
                    "topic": topic,
                    "description": description
                }
            }
            
            for agent_name, task_data in test_tasks.items():
                self.logger.info(f"Testing {agent_name}...")
                agent = self.agents[agent_name]
                result = await agent.execute_task(task_data)
                test_results[agent_name] = {
                    "success": result["success"],
                    "execution_time": result["execution_time"],
                    "has_content": bool(result["data"].get("content")),
                    "test_mode": True
                }
                self.logger.info(f"{agent_name} test completed: {result['success']}")
                
            return {
                "success": True,
                "test_results": test_results,
                "test_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in simple test: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_mode": True
            }

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
        system = MockPatentAgentSystem()
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

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Patent Agent Test Mode (Simple)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    asyncio.run(quick_test())

if __name__ == "__main__":
    main()