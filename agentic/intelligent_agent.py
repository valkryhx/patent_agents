#!/usr/bin/env python3
"""
智能体客户端
使用GLM-4.5-flash模型进行任务规划和自动工具调用
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import uuid
import httpx
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GLMClient:
    """GLM API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn/api/paas/v4"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def chat_completion(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """调用GLM聊天完成API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "glm-4.5-flash",
            "messages": messages,
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"GLM API调用失败: {e}")
            raise
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

class TaskPlanner:
    """任务规划器"""
    
    def __init__(self, glm_client: GLMClient):
        self.glm_client = glm_client
        
    async def plan_task(self, user_request: str) -> Dict[str, Any]:
        """规划任务执行步骤"""
        
        planning_prompt = f"""你是一个智能任务规划专家。请分析用户请求并制定详细的执行计划。

用户请求: {user_request}

可用工具:
1. data_collector - 数据收集工具，用于收集和预处理数据
2. data_analyzer - 数据分析工具，用于分析已收集的数据
3. report_generator - 报告生成工具，用于生成综合报告

工具依赖关系:
- data_analyzer 必须在 data_collector 之后执行
- report_generator 必须在 data_collector 和 data_analyzer 之后执行

请制定详细的执行计划，包括:
1. 任务分解
2. 工具调用顺序
3. 每个工具的参数配置
4. 预期结果

请以JSON格式返回执行计划。"""

        messages = [
            {"role": "system", "content": "你是一个专业的任务规划专家，擅长制定详细的执行计划。"},
            {"role": "user", "content": planning_prompt}
        ]
        
        try:
            response = await self.glm_client.chat_completion(messages)
            content = response["choices"][0]["message"]["content"]
            
            # 尝试解析JSON响应
            try:
                plan = json.loads(content)
                return plan
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取JSON部分
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group(1))
                    return plan
                else:
                    # 如果仍然无法解析，返回默认计划
                    return self._generate_default_plan(user_request)
                    
        except Exception as e:
            logger.error(f"任务规划失败: {e}")
            return self._generate_default_plan(user_request)
    
    def _generate_default_plan(self, user_request: str) -> Dict[str, Any]:
        """生成默认执行计划"""
        return {
            "task_description": user_request,
            "execution_steps": [
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
                        "report_sections": ["summary", "analysis", "recommendations"],
                        "visualization": True
                    }
                }
            ],
            "expected_outcome": "完成数据收集、分析和报告生成的完整流程"
        }

class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, glm_client: GLMClient):
        self.glm_client = glm_client
        self.execution_history = []
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个工具"""
        
        execution_prompt = f"""你是一个工具执行专家。请根据工具名称和参数，生成最优的工具调用配置。

工具名称: {tool_name}
工具参数: {json.dumps(parameters, ensure_ascii=False, indent=2)}

请分析参数并优化配置，确保:
1. 参数值合理且有效
2. 符合工具的使用规范
3. 能够产生最佳结果

请以JSON格式返回优化后的参数配置。"""

        messages = [
            {"role": "system", "content": "你是一个工具执行专家，擅长优化工具参数配置。"},
            {"role": "user", "content": execution_prompt}
        ]
        
        try:
            response = await self.glm_client.chat_completion(messages)
            content = response["choices"][0]["message"]["content"]
            
            # 尝试解析JSON响应
            try:
                optimized_params = json.loads(content)
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用原始参数
                optimized_params = parameters
            
            # 记录执行历史
            execution_record = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "tool": tool_name,
                "parameters": optimized_params,
                "status": "executing"
            }
            self.execution_history.append(execution_record)
            
            # 模拟工具执行（在实际环境中，这里会调用MCP server）
            await asyncio.sleep(1)  # 模拟执行时间
            
            # 更新执行状态
            execution_record["status"] = "completed"
            execution_record["result"] = {
                "status": "success",
                "message": f"{tool_name} 执行完成",
                "output": f"模拟输出: {tool_name} 已成功执行，参数: {optimized_params}"
            }
            
            return execution_record["result"]
            
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
            return {"status": "error", "message": str(e)}

class IntelligentAgent:
    """智能体主类"""
    
    def __init__(self, api_key: str):
        self.glm_client = GLMClient(api_key)
        self.task_planner = TaskPlanner(self.glm_client)
        self.tool_executor = ToolExecutor(self.glm_client)
        self.execution_context = {}
        
    async def execute_task(self, user_request: str) -> Dict[str, Any]:
        """执行完整任务"""
        
        logger.info(f"开始执行任务: {user_request}")
        
        try:
            # 1. 任务规划
            logger.info("正在规划任务...")
            execution_plan = await self.task_planner.plan_task(user_request)
            logger.info(f"任务规划完成: {execution_plan.get('task_description', 'N/A')}")
            
            # 2. 按计划执行工具
            results = []
            for step in execution_plan.get("execution_steps", []):
                logger.info(f"执行步骤 {step['step']}: {step['tool']}")
                
                # 检查依赖关系
                if not self._check_dependencies(step, results):
                    logger.warning(f"步骤 {step['step']} 的依赖未满足，跳过执行")
                    continue
                
                # 执行工具
                result = await self.tool_executor.execute_tool(
                    step["tool"], 
                    step["parameters"]
                )
                
                results.append({
                    "step": step["step"],
                    "tool": step["tool"],
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"步骤 {step['step']} 执行完成")
                
                # 更新执行上下文
                self.execution_context[step["tool"]] = result
            
            # 3. 生成执行总结
            summary = await self._generate_execution_summary(user_request, results)
            
            return {
                "status": "success",
                "user_request": user_request,
                "execution_plan": execution_plan,
                "results": results,
                "summary": summary,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            return {
                "status": "error",
                "user_request": user_request,
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            }
    
    def _check_dependencies(self, step: Dict[str, Any], completed_results: List[Dict]) -> bool:
        """检查步骤依赖是否满足"""
        tool_name = step["tool"]
        
        if tool_name == "data_analyzer":
            # 需要先执行 data_collector
            return any(r["tool"] == "data_collector" for r in completed_results)
        elif tool_name == "report_generator":
            # 需要先执行 data_collector 和 data_analyzer
            has_collection = any(r["tool"] == "data_collector" for r in completed_results)
            has_analysis = any(r["tool"] == "data_analyzer" for r in completed_results)
            return has_collection and has_analysis
        
        return True
    
    async def _generate_execution_summary(self, user_request: str, results: List[Dict]) -> str:
        """生成执行总结"""
        
        summary_prompt = f"""请为以下任务执行生成详细的总结报告。

用户请求: {user_request}

执行结果:
{json.dumps(results, ensure_ascii=False, indent=2)}

请生成一个包含以下内容的总结:
1. 任务完成情况
2. 各步骤执行结果
3. 关键发现和洞察
4. 建议和下一步行动

请以markdown格式返回总结报告。"""

        messages = [
            {"role": "system", "content": "你是一个专业的任务总结专家，擅长生成清晰、全面的执行总结。"},
            {"role": "user", "content": summary_prompt}
        ]
        
        try:
            response = await self.glm_client.chat_completion(messages)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"生成总结失败: {e}")
            return f"任务执行完成，但生成总结时出现错误: {e}"
    
    async def close(self):
        """关闭智能体"""
        await self.glm_client.close()

async def main():
    """主函数 - 演示智能体使用"""
    
    # 从环境变量或配置文件获取API key
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        # 尝试从.private目录读取
        private_key_file = Path("../.private/GLM_API_KEY")
        if private_key_file.exists():
            api_key = private_key_file.read_text().strip()
        else:
            print("错误: 未找到GLM API key")
            sys.exit(1)
    
    # 创建智能体
    agent = IntelligentAgent(api_key)
    
    try:
        # 示例任务
        user_request = "请帮我分析用户行为数据并生成洞察报告"
        
        print(f"开始执行任务: {user_request}")
        print("=" * 50)
        
        result = await agent.execute_task(user_request)
        
        print("\n任务执行完成!")
        print("=" * 50)
        print(f"状态: {result['status']}")
        print(f"执行时间: {result['execution_time']}")
        
        if result['status'] == 'success':
            print(f"\n执行计划: {result['execution_plan']['task_description']}")
            print(f"\n执行结果:")
            for step_result in result['results']:
                print(f"  步骤 {step_result['step']}: {step_result['tool']} - {step_result['result']['status']}")
            
            print(f"\n执行总结:")
            print(result['summary'])
        else:
            print(f"错误: {result['error']}")
            
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())