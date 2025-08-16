#!/usr/bin/env python3
"""
启动多参数工具专利撰写流程
Start multi-parameter tool patent writing workflow
"""

import asyncio
import sys
import os
from patent_agent_demo.patent_agent_system import PatentAgentSystem

async def main():
    """主函数"""
    print("🚀 启动多参数工具专利撰写流程...")
    
    # 专利主题信息
    topic = "基于智能分层推理的多参数工具自适应调用系统"
    description = """
    一种基于智能分层推理的多参数工具自适应调用系统，解决现有技术中多参数工具调用成功率低的问题。
    
    技术背景：
    模型上下文协议能够方便地将不同工具集成提供给大模型使用，但是一些工具或接口需要的参数非常多（多达20个），
    此时封装之后模型很难正确或精准地调用成功，调用成功率低于30%。
    
    技术方案：
    1. 智能分层推理引擎：基于多维度评估参数重要性并进行分层推理
    2. 自适应参数收集策略：实现渐进式分层参数收集和智能默认值推断
    3. 动态调用策略优化：实时监控和自适应调整调用策略
    4. 智能错误诊断与恢复：多维度错误分析和自动恢复
    
    技术效果：
    - 调用成功率从30%提升至85%以上
    - 减少参数收集时间60%
    - 错误诊断准确率90%，自动恢复成功率80%
    - 降低系统复杂度40%
    
    应用场景：
    - API网关优化
    - 微服务集成
    - 开发工具链
    - 企业级应用
    """
    
    print(f"📝 专利主题: {topic}")
    print(f"📋 技术描述: {description[:200]}...")
    
    # 初始化专利代理系统
    system = PatentAgentSystem()
    await system.start()
    
    try:
        # 启动专利撰写工作流
        workflow_id = await system.coordinator.execute_task({
            "type": "start_patent_workflow",
            "topic": topic,
            "description": description
        })
        
        print(f"✅ 专利撰写工作流已启动，工作流ID: {workflow_id}")
        print("🔄 开始监控撰写进度...")
        
        # 监控进度
        export_path = None
        while True:
            status = await system.coordinator.execute_task({
                "type": "monitor_workflow",
                "workflow_id": workflow_id
            })
            
            if status.get("status") == "completed":
                export_path = f"/workspace/output/multi_parameter_tool_patent_{workflow_id[:8]}.md"
                print(f"🎉 专利撰写完成！导出路径: {export_path}")
                break
            elif status.get("status") == "failed":
                print(f"❌ 专利撰写失败: {status.get('error', '未知错误')}")
                break
            else:
                current_stage = status.get("current_stage", "未知")
                progress = status.get("progress", 0)
                print(f"⏳ 当前阶段: {current_stage}, 进度: {progress}%")
            
            # 等待5分钟后再次检查
            await asyncio.sleep(300)  # 5分钟 = 300秒
        
        return export_path
        
    except Exception as e:
        print(f"❌ 启动专利撰写流程时出错: {e}")
        raise
    finally:
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())