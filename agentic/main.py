#!/usr/bin/env python3
"""
智能体系统主程序
集成MCP server和智能体，提供完整的系统入口
"""

import asyncio
import json
import logging
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from mcp_server import AgenticMCPServer
from intelligent_agent import IntelligentAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgenticSystem:
    """智能体系统主类"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.mcp_server = None
        self.intelligent_agent = None
        
    async def start_mcp_server(self):
        """启动MCP服务器"""
        logger.info("正在启动MCP服务器...")
        self.mcp_server = AgenticMCPServer()
        logger.info("MCP服务器已启动")
        
    async def start_intelligent_agent(self):
        """启动智能体"""
        logger.info("正在启动智能体...")
        self.intelligent_agent = IntelligentAgent(self.api_key)
        logger.info("智能体已启动")
        
    async def run_interactive_mode(self):
        """运行交互模式"""
        print("\n" + "="*60)
        print("🤖 智能体系统 - 交互模式")
        print("="*60)
        print("可用命令:")
        print("  plan <任务描述>  - 规划任务")
        print("  execute <任务描述> - 执行任务")
        print("  tools - 查看可用工具")
        print("  status - 查看系统状态")
        print("  help - 显示帮助信息")
        print("  quit - 退出系统")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n🤖 请输入命令: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == 'quit':
                    print("👋 再见!")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() == 'tools':
                    await self._show_tools()
                elif user_input.lower() == 'status':
                    await self._show_status()
                elif user_input.startswith('plan '):
                    task_description = user_input[5:].strip()
                    await self._plan_task(task_description)
                elif user_input.startswith('execute '):
                    task_description = user_input[8:].strip()
                    await self._execute_task(task_description)
                else:
                    print("❌ 未知命令，请输入 'help' 查看帮助")
                    
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                logger.error(f"交互模式错误: {e}")
                print(f"❌ 错误: {e}")
    
    async def _show_help(self):
        """显示帮助信息"""
        help_text = """
📖 帮助信息

命令说明:
• plan <任务描述>  - 使用智能体规划任务执行步骤
• execute <任务描述> - 完整执行任务（包括规划和执行）
• tools - 查看MCP服务器提供的工具
• status - 查看系统运行状态
• help - 显示此帮助信息
• quit - 退出系统

示例:
• plan 分析用户行为数据
• execute 生成销售报告
• tools
• status

工具依赖关系:
1. data_collector → 数据收集
2. data_analyzer → 数据分析（依赖数据收集）
3. report_generator → 报告生成（依赖数据收集和分析）
        """
        print(help_text)
    
    async def _show_tools(self):
        """显示可用工具"""
        if not self.mcp_server:
            print("❌ MCP服务器未启动")
            return
            
        print("\n🔧 可用工具:")
        print("-" * 40)
        
        tools = [
            ("data_collector", "数据收集工具", "收集和预处理数据"),
            ("data_analyzer", "数据分析工具", "分析已收集的数据"),
            ("report_generator", "报告生成工具", "生成综合报告")
        ]
        
        for tool_name, tool_title, tool_desc in tools:
            print(f"📊 {tool_title} ({tool_name})")
            print(f"   描述: {tool_desc}")
            print()
    
    async def _show_status(self):
        """显示系统状态"""
        print("\n📊 系统状态:")
        print("-" * 40)
        
        mcp_status = "✅ 运行中" if self.mcp_server else "❌ 未启动"
        agent_status = "✅ 运行中" if self.intelligent_agent else "❌ 未启动"
        
        print(f"MCP服务器: {mcp_status}")
        print(f"智能体: {agent_status}")
        
        if self.intelligent_agent and hasattr(self.intelligent_agent.tool_executor, 'execution_history'):
            history_count = len(self.intelligent_agent.tool_executor.execution_history)
            print(f"工具执行历史: {history_count} 条记录")
    
    async def _plan_task(self, task_description: str):
        """规划任务"""
        if not self.intelligent_agent:
            print("❌ 智能体未启动")
            return
            
        print(f"\n🧠 正在规划任务: {task_description}")
        print("⏳ 请稍候...")
        
        try:
            plan = await self.intelligent_agent.task_planner.plan_task(task_description)
            
            print("\n📋 任务执行计划:")
            print("-" * 50)
            print(f"任务描述: {plan.get('task_description', 'N/A')}")
            print(f"预期结果: {plan.get('expected_outcome', 'N/A')}")
            print("\n执行步骤:")
            
            for step in plan.get('execution_steps', []):
                print(f"  {step['step']}. {step['tool']} - {step['description']}")
                print(f"     参数: {json.dumps(step['parameters'], ensure_ascii=False, indent=6)}")
                print()
                
        except Exception as e:
            logger.error(f"任务规划失败: {e}")
            print(f"❌ 任务规划失败: {e}")
    
    async def _execute_task(self, task_description: str):
        """执行任务"""
        if not self.intelligent_agent:
            print("❌ 智能体未启动")
            return
            
        print(f"\n🚀 开始执行任务: {task_description}")
        print("⏳ 请稍候，这可能需要几分钟...")
        
        try:
            result = await self.intelligent_agent.execute_task(task_description)
            
            print("\n✅ 任务执行完成!")
            print("=" * 50)
            print(f"状态: {result['status']}")
            print(f"执行时间: {result['execution_time']}")
            
            if result['status'] == 'success':
                print(f"\n📋 执行计划: {result['execution_plan']['task_description']}")
                print(f"\n📊 执行结果:")
                
                for step_result in result['results']:
                    status_icon = "✅" if step_result['result']['status'] == 'success' else "❌"
                    print(f"  {status_icon} 步骤 {step_result['step']}: {step_result['tool']}")
                    print(f"     状态: {step_result['result']['status']}")
                    print(f"     时间: {step_result['timestamp']}")
                    print()
                
                print("📝 执行总结:")
                print("-" * 30)
                print(result['summary'])
            else:
                print(f"❌ 错误: {result['error']}")
                
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            print(f"❌ 任务执行失败: {e}")
    
    async def run_demo_mode(self):
        """运行演示模式"""
        print("\n🎬 智能体系统 - 演示模式")
        print("="*50)
        
        demo_tasks = [
            "分析电商网站用户行为数据并生成洞察报告",
            "收集社交媒体数据并生成趋势分析报告",
            "分析销售数据并生成业务建议报告"
        ]
        
        for i, task in enumerate(demo_tasks, 1):
            print(f"\n🎯 演示任务 {i}: {task}")
            print("-" * 40)
            
            try:
                result = await self.intelligent_agent.execute_task(task)
                
                if result['status'] == 'success':
                    print(f"✅ 任务 {i} 执行成功")
                    print(f"   执行步骤数: {len(result['results'])}")
                    print(f"   执行时间: {result['execution_time']}")
                else:
                    print(f"❌ 任务 {i} 执行失败: {result['error']}")
                    
            except Exception as e:
                print(f"❌ 任务 {i} 执行异常: {e}")
            
            # 任务间暂停
            if i < len(demo_tasks):
                print("\n⏳ 等待3秒后继续下一个任务...")
                await asyncio.sleep(3)
        
        print("\n🎉 演示模式完成!")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("正在清理资源...")
        
        if self.intelligent_agent:
            await self.intelligent_agent.close()
            logger.info("智能体已关闭")
        
        logger.info("资源清理完成")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能体系统")
    parser.add_argument("--mode", choices=["interactive", "demo"], default="interactive",
                       help="运行模式: interactive(交互模式) 或 demo(演示模式)")
    parser.add_argument("--api-key", help="GLM API密钥")
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key
    if not api_key:
        # 尝试从环境变量获取
        api_key = os.getenv("GLM_API_KEY")
        if not api_key:
            # 尝试从.private目录读取
            private_key_file = Path("../.private/GLM_API_KEY")
            if private_key_file.exists():
                api_key = private_key_file.read_text().strip()
            else:
                print("❌ 错误: 未找到GLM API密钥")
                print("请通过以下方式之一提供API密钥:")
                print("1. 命令行参数: --api-key <your-key>")
                print("2. 环境变量: GLM_API_KEY")
                print("3. 在.private/GLM_API_KEY文件中")
                sys.exit(1)
    
    # 创建智能体系统
    system = AgenticSystem(api_key)
    
    try:
        # 启动系统组件
        await system.start_mcp_server()
        await system.start_intelligent_agent()
        
        print("🚀 智能体系统启动成功!")
        
        # 根据模式运行
        if args.mode == "demo":
            await system.run_demo_mode()
        else:
            await system.run_interactive_mode()
            
    except Exception as e:
        logger.error(f"系统运行错误: {e}")
        print(f"❌ 系统运行错误: {e}")
    finally:
        await system.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 系统已退出")
    except Exception as e:
        print(f"❌ 系统异常退出: {e}")
        sys.exit(1)