#!/usr/bin/env python3
"""
Enhanced Patent Workflow with Progress Monitoring
This script runs the patent writing workflow with detailed progress updates every 5 minutes.
"""

import asyncio
import time
import os
import json
from datetime import datetime
from patent_agent_demo.patent_agent_system import PatentAgentSystem

class ProgressMonitor:
    def __init__(self, workflow_id, topic, description):
        self.workflow_id = workflow_id
        self.topic = topic
        self.description = description
        self.start_time = time.time()
        self.last_update = time.time()
        self.update_interval = 300  # 5 minutes in seconds
        
    def should_update(self):
        """Check if it's time for a progress update"""
        return time.time() - self.last_update >= self.update_interval
    
    def update_progress(self, stage_name, status, details=None):
        """Update progress and print status if interval has passed"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.should_update():
            print(f"\n{'='*80}")
            print(f"📊 专利撰写进度更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  已运行时间: {elapsed/60:.1f} 分钟")
            print(f"📋 工作流ID: {self.workflow_id}")
            print(f"🎯 专利主题: {self.topic}")
            print(f"📝 当前阶段: {stage_name}")
            print(f"📈 状态: {status}")
            if details:
                print(f"📋 详细信息: {details}")
            print(f"{'='*80}\n")
            
            self.last_update = current_time
            
            # Save progress to file
            progress_data = {
                "timestamp": datetime.now().isoformat(),
                "elapsed_minutes": elapsed/60,
                "stage": stage_name,
                "status": status,
                "details": details
            }
            
            progress_file = f"output/progress/{self.workflow_id}_progress.json"
            os.makedirs(os.path.dirname(progress_file), exist_ok=True)
            
            try:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"⚠️  保存进度文件失败: {e}")

async def run_patent_workflow_with_progress(topic, description):
    """Run patent workflow with detailed progress monitoring"""
    
    print(f"🚀 启动专利撰写工作流")
    print(f"📋 主题: {topic}")
    print(f"📝 描述: {description}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Initialize the patent agent system
    system = PatentAgentSystem()
    await system.start()
    
    try:
        # Start the workflow
        workflow_id = await system.execute_workflow(topic, description)
        
        if not workflow_id:
            print("❌ 工作流启动失败")
            return None
            
        print(f"✅ 工作流启动成功，ID: {workflow_id}")
        
        # Initialize progress monitor
        monitor = ProgressMonitor(workflow_id, topic, description)
        
        # Monitor workflow progress
        while True:
            try:
                # Get workflow status
                status_result = await system.coordinator.execute_task({
                    "type": "monitor_workflow",
                    "workflow_id": workflow_id
                })
                
                if status_result.success:
                    status_data = status_result.data
                    current_stage = status_data.get("current_stage", "未知")
                    overall_status = status_data.get("overall_status", "运行中")
                    stage_results = status_data.get("stage_results", {})
                    
                    # Check if workflow is completed
                    if overall_status == "completed":
                        monitor.update_progress(
                            "完成", 
                            "工作流已完成",
                            f"所有阶段已完成，共 {len(stage_results)} 个阶段"
                        )
                        
                        # Get final patent document
                        final_result = await system.coordinator.execute_task({
                            "type": "get_final_patent",
                            "workflow_id": workflow_id
                        })
                        
                        if final_result.success:
                            patent_content = final_result.data.get("patent_content", "")
                            
                            # Save patent document
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            patent_filename = f"output/多参数工具自适应调用系统专利_{timestamp}.md"
                            
                            os.makedirs(os.path.dirname(patent_filename), exist_ok=True)
                            
                            with open(patent_filename, 'w', encoding='utf-8') as f:
                                f.write(f"# {topic}\n\n")
                                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"**工作流ID**: {workflow_id}\n\n")
                                f.write(patent_content)
                            
                            print(f"✅ 专利文档已保存到: {patent_filename}")
                            
                            # Save completion report
                            completion_report = {
                                "workflow_id": workflow_id,
                                "topic": topic,
                                "description": description,
                                "completion_time": datetime.now().isoformat(),
                                "total_stages": len(stage_results),
                                "patent_file": patent_filename,
                                "stage_results": stage_results
                            }
                            
                            report_filename = f"output/专利完成报告_{timestamp}.json"
                            with open(report_filename, 'w', encoding='utf-8') as f:
                                json.dump(completion_report, f, ensure_ascii=False, indent=2)
                            
                            print(f"📊 完成报告已保存到: {report_filename}")
                            print(f"🎉 专利撰写工作流完成！")
                            
                        else:
                            print(f"❌ 获取最终专利文档失败: {final_result.error_message}")
                        
                        break
                    
                    elif overall_status == "failed":
                        monitor.update_progress(
                            current_stage,
                            "工作流失败",
                            f"阶段 {current_stage} 执行失败"
                        )
                        print(f"❌ 工作流执行失败")
                        break
                    
                    else:
                        # Workflow is still running
                        stage_detail = f"阶段 {current_stage} 执行中"
                        if stage_results:
                            completed_stages = len([s for s in stage_results.values() if s.get("status") == "completed"])
                            stage_detail = f"已完成 {completed_stages}/{len(stage_results)} 个阶段"
                        
                        monitor.update_progress(
                            current_stage,
                            "运行中",
                            stage_detail
                        )
                
                else:
                    print(f"⚠️  获取工作流状态失败: {status_result.error_message}")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"⚠️  监控过程中出现错误: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    except Exception as e:
        print(f"❌ 工作流执行过程中出现错误: {e}")
    
    finally:
        # Stop the system
        await system.stop()
        print(f"🛑 系统已停止")

def main():
    """Main function to run the patent workflow"""
    
    # Patent topic and description
    topic = "基于智能分层推理的多参数工具自适应调用系统"
    description = """一种基于智能分层推理的多参数工具自适应调用系统，解决现有技术中多参数工具调用成功率低的问题。技术方案包括智能分层推理引擎、自适应参数收集策略、动态调用策略优化和智能错误诊断与恢复。技术效果：调用成功率从30%提升至85%以上，减少参数收集时间60%，错误诊断准确率90%。"""
    
    print(f"🎯 专利主题: {topic}")
    print(f"📝 技术描述: {description}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 进度更新间隔: 5分钟")
    print(f"{'='*80}")
    
    # Run the workflow
    asyncio.run(run_patent_workflow_with_progress(topic, description))

if __name__ == "__main__":
    main()