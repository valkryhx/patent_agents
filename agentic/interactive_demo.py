#!/usr/bin/env python3
"""
智能体系统交互式演示
用户可以输入自定义任务，系统会智能规划并执行
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List

class InteractiveMCPServer:
    """交互式MCP服务器"""
    
    def __init__(self):
        self.tools = {
            "data_collector": {
                "name": "data_collector",
                "description": "收集和预处理数据，为后续分析做准备",
                "dependencies": [],
                "parameters": {
                    "data_source": "数据源描述",
                    "collection_method": ["api", "scraping", "file_upload", "manual_input"],
                    "data_type": ["text", "numeric", "categorical", "mixed"]
                }
            },
            "data_analyzer": {
                "name": "data_analyzer", 
                "description": "分析已收集的数据，生成统计信息和洞察",
                "dependencies": ["data_collector"],
                "parameters": {
                    "analysis_type": ["descriptive", "exploratory", "statistical", "ml_prediction"],
                    "target_variables": "目标分析变量列表",
                    "analysis_parameters": "分析参数配置"
                }
            },
            "report_generator": {
                "name": "report_generator",
                "description": "基于数据收集和分析结果生成综合报告",
                "dependencies": ["data_collector", "data_analyzer"],
                "parameters": {
                    "report_format": ["markdown", "html", "pdf", "json"],
                    "report_sections": "报告包含的章节",
                    "visualization": "是否包含可视化图表"
                }
            }
        }
        self.execution_history = []
    
    def list_tools(self):
        """列出所有可用工具"""
        print("\n🔧 可用工具:")
        print("-" * 40)
        for tool_name, tool_info in self.tools.items():
            print(f"📊 {tool_info['name']}")
            print(f"   描述: {tool_info['description']}")
            if tool_info['dependencies']:
                print(f"   依赖: {', '.join(tool_info['dependencies'])}")
            else:
                print(f"   依赖: 无")
            print()
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        if tool_name not in self.tools:
            return {"status": "error", "message": f"未知工具: {tool_name}"}
        
        # 检查依赖
        dependencies = self.tools[tool_name]["dependencies"]
        for dep in dependencies:
            if not any(h["tool"] == dep for h in self.execution_history):
                return {"status": "error", "message": f"依赖未满足: {dep}"}
        
        # 模拟工具执行
        print(f"🔧 执行工具: {tool_name}")
        print(f"   参数: {json.dumps(parameters, ensure_ascii=False, indent=4)}")
        
        # 模拟处理时间
        if tool_name == "data_collector":
            time.sleep(1)
            result = self._simulate_data_collection(parameters)
        elif tool_name == "data_analyzer":
            time.sleep(2)
            result = self._simulate_data_analysis(parameters)
        elif tool_name == "report_generator":
            time.sleep(1.5)
            result = self._simulate_report_generation(parameters)
        
        # 记录执行历史
        self.execution_history.append({
            "tool": tool_name,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _simulate_data_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟数据收集"""
        return {
            "status": "success",
            "message": "数据收集完成",
            "data": {
                "source": params.get("data_source", "未知"),
                "method": params.get("collection_method", "api"),
                "data_points": 100,
                "quality": "high",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _simulate_data_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟数据分析"""
        return {
            "status": "success", 
            "message": "数据分析完成",
            "analysis": {
                "type": params.get("analysis_type", "descriptive"),
                "insights": [
                    "数据质量良好，无缺失值",
                    "分布相对均匀",
                    "适合进行进一步分析"
                ],
                "recommendations": [
                    "建议增加数据采样频率",
                    "考虑扩展特征维度",
                    "可以进行机器学习建模"
                ]
            }
        }
    
    def _simulate_report_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟报告生成"""
        return {
            "status": "success",
            "message": "报告生成完成", 
            "report": {
                "format": params.get("report_format", "markdown"),
                "content": f"# 数据分析报告\n\n基于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}的数据收集和分析结果生成的综合报告...",
                "sections": params.get("report_sections", ["摘要", "分析", "建议"]),
                "visualization": params.get("visualization", True)
            }
        }

class InteractiveIntelligentAgent:
    """交互式智能体"""
    
    def __init__(self):
        self.mcp_server = InteractiveMCPServer()
        self.task_planner = InteractiveTaskPlanner()
    
    def execute_task(self, user_request: str) -> Dict[str, Any]:
        """执行任务"""
        print(f"\n🧠 智能体收到任务: {user_request}")
        
        # 1. 任务规划
        print("\n📋 正在规划任务...")
        plan = self.task_planner.plan_task(user_request)
        print(f"✅ 任务规划完成: {plan['description']}")
        
        # 显示执行计划
        print(f"\n📋 执行计划:")
        for step in plan["steps"]:
            print(f"  {step['step']}. {step['tool']} - {step['description']}")
        
        # 2. 执行计划
        print(f"\n🚀 开始执行计划...")
        results = []
        
        for step in plan["steps"]:
            print(f"\n📊 执行步骤 {step['step']}: {step['tool']}")
            
            # 执行工具
            result = self.mcp_server.execute_tool(step["tool"], step["parameters"])
            
            if result["status"] == "success":
                print(f"✅ 步骤 {step['step']} 执行成功")
                results.append({
                    "step": step["step"],
                    "tool": step["tool"],
                    "result": result,
                    "status": "success"
                })
            else:
                print(f"❌ 步骤 {step['step']} 执行失败: {result['message']}")
                results.append({
                    "step": step["step"],
                    "tool": step["tool"],
                    "result": result,
                    "status": "failed"
                })
                break
        
        # 3. 生成总结
        summary = self._generate_summary(user_request, results)
        
        return {
            "status": "success",
            "user_request": user_request,
            "plan": plan,
            "results": results,
            "summary": summary,
            "execution_time": datetime.now().isoformat()
        }
    
    def _generate_summary(self, request: str, results: List[Dict]) -> str:
        """生成执行总结"""
        success_count = sum(1 for r in results if r["status"] == "success")
        total_count = len(results)
        
        summary = f"""
# 任务执行总结

## 任务描述
{request}

## 执行结果
- 总步骤数: {total_count}
- 成功步骤: {success_count}
- 失败步骤: {total_count - success_count}

## 执行详情
"""
        
        for result in results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            summary += f"- {status_icon} 步骤 {result['step']}: {result['tool']}\n"
        
        if success_count == total_count:
            summary += "\n🎉 所有步骤执行成功！任务完成。"
        else:
            summary += f"\n⚠️  部分步骤执行失败，任务未完成。"
        
        return summary

class InteractiveTaskPlanner:
    """交互式任务规划器"""
    
    def plan_task(self, user_request: str) -> Dict[str, Any]:
        """规划任务"""
        # 基于用户请求智能生成执行计划
        if any(word in user_request for word in ["数据", "分析", "统计"]):
            return {
                "description": "数据分析任务",
                "steps": [
                    {
                        "step": 1,
                        "tool": "data_collector",
                        "description": "收集相关数据",
                        "parameters": {
                            "data_source": "根据用户请求确定",
                            "collection_method": "api",
                            "data_type": "mixed"
                        }
                    },
                    {
                        "step": 2,
                        "tool": "data_analyzer",
                        "description": "分析收集的数据",
                        "parameters": {
                            "analysis_type": "descriptive",
                            "target_variables": ["value", "category"],
                            "analysis_parameters": {}
                        }
                    },
                    {
                        "step": 3,
                        "tool": "report_generator",
                        "description": "生成分析报告",
                        "parameters": {
                            "report_format": "markdown",
                            "report_sections": ["摘要", "分析", "建议"],
                            "visualization": True
                        }
                    }
                ]
            }
        elif any(word in user_request for word in ["报告", "总结", "文档"]):
            return {
                "description": "报告生成任务",
                "steps": [
                    {
                        "step": 1,
                        "tool": "data_collector",
                        "description": "收集必要信息",
                        "parameters": {
                            "data_source": "用户需求",
                            "collection_method": "manual_input",
                            "data_type": "text"
                        }
                    },
                    {
                        "step": 2,
                        "tool": "report_generator",
                        "description": "生成报告",
                        "parameters": {
                            "report_format": "markdown",
                            "report_sections": ["摘要", "内容", "结论"],
                            "visualization": False
                        }
                    }
                ]
            }
        else:
            # 通用任务计划
            return {
                "description": "通用任务",
                "steps": [
                    {
                        "step": 1,
                        "tool": "data_collector",
                        "description": "收集必要信息",
                        "parameters": {
                            "data_source": "用户需求",
                            "collection_method": "manual_input",
                            "data_type": "mixed"
                        }
                    },
                    {
                        "step": 2,
                        "tool": "report_generator",
                        "description": "生成结果报告",
                        "parameters": {
                            "report_format": "markdown",
                            "report_sections": ["摘要", "结果"],
                            "visualization": False
                        }
                    }
                ]
            }

def show_menu():
    """显示主菜单"""
    menu = """
🤖 智能体系统交互式演示
==================================================

可用命令:
1. 🎯 执行任务 - 输入任务描述，系统自动规划并执行
2. 🔧 查看工具 - 显示所有可用工具及其依赖关系
3. 📊 执行历史 - 查看已执行的任务历史
4. 📖 帮助信息 - 显示使用说明和示例
5. 🚪 退出系统

请输入命令 (1-5): """
    
    while True:
        try:
            choice = input(menu).strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("❌ 无效选项，请输入1-5")
        except KeyboardInterrupt:
            print("\n👋 再见!")
            return '5'

def show_help():
    """显示帮助信息"""
    help_text = """
📖 智能体系统帮助信息

系统概述:
这是一个基于MCP (Model Context Protocol) 的智能体系统，
能够自动规划任务并调用工具完成复杂工作流程。

核心功能:
• 智能任务规划 - 自动分析需求并制定执行计划
• 自动工具调用 - 按计划自动执行MCP工具
• 依赖关系管理 - 智能检查工具执行顺序
• 结果汇总分析 - 生成执行总结和洞察

可用工具:
1. data_collector - 数据收集工具（无依赖）
2. data_analyzer - 数据分析工具（依赖数据收集）
3. report_generator - 报告生成工具（依赖前两个工具）

任务示例:
• "分析电商网站用户行为数据并生成洞察报告"
• "收集销售数据并生成业务分析"
• "生成市场调研报告"
• "分析客户满意度数据"
• "创建季度业绩总结"

工具依赖关系:
data_collector → data_analyzer → report_generator

使用技巧:
• 描述越详细，规划越准确
• 系统会自动选择最合适的工具组合
• 支持中文和英文任务描述
    """
    print(help_text)

def main():
    """主函数"""
    print("🚀 启动智能体系统...")
    
    # 创建智能体
    agent = InteractiveIntelligentAgent()
    
    print("✅ 系统启动完成!")
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            # 执行任务
            print("\n🎯 请输入任务描述:")
            print("示例: 分析用户行为数据并生成洞察报告")
            print("     收集销售数据并生成业务分析")
            print("     生成市场调研报告")
            print("-" * 50)
            
            try:
                user_request = input("请输入任务: ").strip()
                if user_request:
                    print(f"\n🚀 开始执行任务: {user_request}")
                    result = agent.execute_task(user_request)
                    
                    if result["status"] == "success":
                        print(f"\n✅ 任务执行完成!")
                        print(f"📝 执行总结:")
                        print(result["summary"])
                    else:
                        print(f"❌ 任务执行失败")
                else:
                    print("❌ 任务描述不能为空")
            except KeyboardInterrupt:
                print("\n⏹️  任务被中断")
            except Exception as e:
                print(f"❌ 任务执行异常: {e}")
                
        elif choice == '2':
            # 查看工具
            agent.mcp_server.list_tools()
            
        elif choice == '3':
            # 查看执行历史
            history = agent.mcp_server.execution_history
            if history:
                print(f"\n📊 执行历史 (共{len(history)}条):")
                print("-" * 40)
                for i, record in enumerate(history, 1):
                    print(f"{i}. {record['tool']} - {record['timestamp']}")
                    print(f"   状态: {record['result']['status']}")
                    print(f"   消息: {record['result']['message']}")
                    print()
            else:
                print("\n📊 暂无执行历史")
                
        elif choice == '4':
            # 显示帮助
            show_help()
            
        elif choice == '5':
            # 退出
            print("👋 感谢使用智能体系统，再见!")
            break
        
        # 等待用户确认继续
        if choice != '5':
            input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 系统被中断，再见!")
    except Exception as e:
        print(f"❌ 系统异常: {e}")