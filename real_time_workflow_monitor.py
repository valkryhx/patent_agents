#!/usr/bin/env python3
"""
Real-Time Workflow Monitor
实时工作流监控系统 - 监控工作流进度、日志变化和文件输出
"""

import asyncio
import os
import sys
import time
import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem

class RealTimeFileMonitor(FileSystemEventHandler):
    """实时文件监控器"""
    
    def __init__(self, monitor_dir: str, callback):
        self.monitor_dir = monitor_dir
        self.callback = callback
        self.file_hashes = {}
        self.last_modified = {}
        
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, "CREATED")
            
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, "MODIFIED")
            
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, "DELETED")
            
    def _handle_file_change(self, file_path: str, change_type: str):
        try:
            rel_path = os.path.relpath(file_path, self.monitor_dir)
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Calculate file hash for content change detection
            file_hash = None
            if os.path.exists(file_path) and change_type != "DELETED":
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                except:
                    pass
            
            # Check if content actually changed
            content_changed = False
            if file_hash and file_path in self.file_hashes:
                content_changed = self.file_hashes[file_path] != file_hash
            elif file_hash:
                content_changed = True
                
            self.file_hashes[file_path] = file_hash
            
            # Get file size
            file_size = 0
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
            change_info = {
                "timestamp": current_time,
                "file": rel_path,
                "change_type": change_type,
                "content_changed": content_changed,
                "size": file_size,
                "hash": file_hash
            }
            
            self.callback("FILE_CHANGE", change_info)
            
        except Exception as e:
            print(f"Error handling file change: {e}")

class RealTimeWorkflowMonitor:
    """实时工作流监控器"""
    
    def __init__(self, workflow_id: str = None):
        self.workflow_id = workflow_id
        self.monitor_dir = "/workspace"
        self.output_dir = "/workspace/output"
        self.log_file = "/workspace/workflow_monitor.log"
        self.monitoring = False
        self.start_time = None
        self.last_status = None
        self.status_history = []
        self.file_changes = []
        self.process_monitor = None
        self.file_observer = None
        self.system = None
        
        # Create output directory if not exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    async def start_monitoring(self, topic: str, description: str):
        """启动实时监控"""
        try:
            self.logger.info("🚀 启动实时工作流监控系统")
            self.start_time = time.time()
            self.monitoring = True
            
            # Start file monitoring
            await self._start_file_monitoring()
            
            # Start workflow
            await self._start_workflow(topic, description)
            
            # Start real-time monitoring loop
            await self._monitor_loop()
            
        except Exception as e:
            self.logger.error(f"监控启动失败: {e}")
            raise
            
    async def _start_file_monitoring(self):
        """启动文件监控"""
        try:
            # Create file monitor
            event_handler = RealTimeFileMonitor(self.monitor_dir, self._handle_file_change)
            self.file_observer = Observer()
            self.file_observer.schedule(event_handler, self.monitor_dir, recursive=True)
            self.file_observer.start()
            
            self.logger.info(f"✅ 文件监控启动成功 - 监控目录: {self.monitor_dir}")
            
        except Exception as e:
            self.logger.error(f"文件监控启动失败: {e}")
            
    async def _start_workflow(self, topic: str, description: str):
        """启动工作流"""
        try:
            self.logger.info("🔧 启动专利撰写工作流")
            self.logger.info(f"主题: {topic}")
            self.logger.info(f"描述: {description}")
            
            # Initialize system
            self.system = PatentAgentSystem(test_mode=False)
            await self.system.start()
            
            # Start workflow
            self.workflow_id = await self.system.execute_workflow(
                topic=topic,
                description=description,
                workflow_type="enhanced"
            )
            
            self.logger.info(f"✅ 工作流启动成功 - ID: {self.workflow_id}")
            
        except Exception as e:
            self.logger.error(f"工作流启动失败: {e}")
            raise
            
    async def _monitor_loop(self):
        """实时监控循环"""
        try:
            self.logger.info("📊 开始实时监控循环")
            
            while self.monitoring:
                current_time = time.time()
                
                # Monitor workflow status (every 2 seconds)
                if current_time - getattr(self, '_last_status_check', 0) >= 2:
                    await self._check_workflow_status()
                    self._last_status_check = current_time
                
                # Monitor system resources (every 5 seconds)
                if current_time - getattr(self, '_last_resource_check', 0) >= 5:
                    await self._check_system_resources()
                    self._last_resource_check = current_time
                
                # Monitor output files (every 1 second)
                if current_time - getattr(self, '_last_output_check', 0) >= 1:
                    await self._check_output_files()
                    self._last_output_check = current_time
                
                # Check for workflow completion
                if self._is_workflow_completed():
                    self.logger.info("✅ 工作流完成")
                    break
                
                # Short sleep to prevent excessive CPU usage
                await asyncio.sleep(0.5)
                
        except Exception as e:
            self.logger.error(f"监控循环错误: {e}")
            
    async def _check_workflow_status(self):
        """检查工作流状态"""
        try:
            if not self.system or not self.workflow_id:
                return
                
            status_result = await self.system.get_workflow_status(self.workflow_id)
            
            if status_result.get("success"):
                workflow_data = status_result.get("workflow", {})
                
                # Extract status information
                if hasattr(workflow_data, 'overall_status'):
                    overall_status = workflow_data.overall_status
                    current_stage = getattr(workflow_data, 'current_stage', 0)
                    total_stages = len(getattr(workflow_data, 'stages', []))
                elif isinstance(workflow_data, dict):
                    overall_status = workflow_data.get("overall_status", "unknown")
                    current_stage = workflow_data.get("current_stage", 0)
                    total_stages = len(workflow_data.get("stages", []))
                else:
                    overall_status = "unknown"
                    current_stage = 0
                    total_stages = 0
                
                # Check if status changed
                new_status = {
                    "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "overall_status": overall_status,
                    "current_stage": current_stage,
                    "total_stages": total_stages,
                    "progress": f"{current_stage}/{total_stages}" if total_stages > 0 else "0/0"
                }
                
                if new_status != self.last_status:
                    self.last_status = new_status
                    self.status_history.append(new_status)
                    
                    # Log status change
                    self.logger.info(f"📈 状态更新: {overall_status} | 阶段: {current_stage}/{total_stages}")
                    
                    # Save status to file
                    await self._save_status_update(new_status)
                    
        except Exception as e:
            self.logger.error(f"检查工作流状态失败: {e}")
            
    async def _check_system_resources(self):
        """检查系统资源"""
        try:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Get process information
            current_process = psutil.Process()
            process_cpu = current_process.cpu_percent()
            process_memory = current_process.memory_info().rss / 1024 / 1024  # MB
            
            resource_info = {
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "system_cpu": cpu_percent,
                "system_memory_percent": memory.percent,
                "process_cpu": process_cpu,
                "process_memory_mb": round(process_memory, 2)
            }
            
            # Log resource usage
            self.logger.info(f"💻 资源使用: CPU {cpu_percent}% | 内存 {memory.percent}% | 进程内存 {process_memory:.1f}MB")
            
        except Exception as e:
            self.logger.error(f"检查系统资源失败: {e}")
            
    async def _check_output_files(self):
        """检查输出文件"""
        try:
            # Check for new patent files
            patent_files = list(Path(self.monitor_dir).glob("enhanced_patent_*.md"))
            
            for file_path in patent_files:
                file_stat = file_path.stat()
                file_size = file_stat.st_size
                file_mtime = file_stat.st_mtime
                
                # Check if this is a new or updated file
                file_key = str(file_path)
                if file_key not in self.last_modified or self.last_modified[file_key] != file_mtime:
                    self.last_modified[file_key] = file_mtime
                    
                    # Read file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        output_info = {
                            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                            "file": file_path.name,
                            "size": file_size,
                            "content_length": len(content),
                            "content_preview": content[:200] + "..." if len(content) > 200 else content
                        }
                        
                        self.logger.info(f"📄 输出文件更新: {file_path.name} ({file_size} bytes)")
                        
                        # Save output info
                        await self._save_output_update(output_info)
                        
                    except Exception as e:
                        self.logger.error(f"读取文件失败 {file_path}: {e}")
                        
        except Exception as e:
            self.logger.error(f"检查输出文件失败: {e}")
            
    def _handle_file_change(self, change_type: str, change_info: Dict[str, Any]):
        """处理文件变化"""
        try:
            self.file_changes.append(change_info)
            
            # Log significant changes
            if change_info["content_changed"] and change_info["size"] > 100:
                self.logger.info(f"📝 文件变化: {change_info['file']} ({change_info['change_type']}) - {change_info['size']} bytes")
                
        except Exception as e:
            self.logger.error(f"处理文件变化失败: {e}")
            
    def _is_workflow_completed(self) -> bool:
        """检查工作流是否完成"""
        if not self.last_status:
            return False
            
        return self.last_status["overall_status"] in ["completed", "finished", "success"]
        
    async def _save_status_update(self, status: Dict[str, Any]):
        """保存状态更新"""
        try:
            status_file = os.path.join(self.output_dir, f"workflow_status_{self.workflow_id}.json")
            
            # Load existing status or create new
            if os.path.exists(status_file):
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
            else:
                status_data = {"workflow_id": self.workflow_id, "status_history": []}
                
            # Add new status
            status_data["status_history"].append(status)
            status_data["last_update"] = status["timestamp"]
            
            # Save to file
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存状态更新失败: {e}")
            
    async def _save_output_update(self, output_info: Dict[str, Any]):
        """保存输出更新"""
        try:
            output_file = os.path.join(self.output_dir, f"workflow_output_{self.workflow_id}.json")
            
            # Load existing output or create new
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    output_data = json.load(f)
            else:
                output_data = {"workflow_id": self.workflow_id, "outputs": []}
                
            # Add new output
            output_data["outputs"].append(output_info)
            output_data["last_update"] = output_info["timestamp"]
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存输出更新失败: {e}")
            
    async def stop_monitoring(self):
        """停止监控"""
        try:
            self.logger.info("🛑 停止实时监控")
            self.monitoring = False
            
            # Stop file observer
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
                
            # Stop system
            if self.system:
                await self.system.stop()
                
            # Generate final report
            await self._generate_final_report()
            
        except Exception as e:
            self.logger.error(f"停止监控失败: {e}")
            
    async def _generate_final_report(self):
        """生成最终报告"""
        try:
            report = {
                "workflow_id": self.workflow_id,
                "start_time": self.start_time,
                "end_time": time.time(),
                "duration": time.time() - self.start_time if self.start_time else 0,
                "total_status_updates": len(self.status_history),
                "total_file_changes": len(self.file_changes),
                "final_status": self.last_status,
                "status_history": self.status_history[-10:],  # Last 10 updates
                "file_changes": self.file_changes[-20:]  # Last 20 changes
            }
            
            report_file = os.path.join(self.output_dir, f"monitoring_report_{self.workflow_id}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"📊 监控报告已生成: {report_file}")
            
        except Exception as e:
            self.logger.error(f"生成最终报告失败: {e}")

async def main():
    """主函数"""
    try:
        # 定义专利主题
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        
        print("=" * 80)
        print("🚀 启动实时工作流监控系统")
        print("=" * 80)
        print(f"主题: {topic}")
        print(f"描述: {description}")
        print("=" * 80)
        
        # 创建监控器
        monitor = RealTimeWorkflowMonitor()
        
        # 启动监控
        await monitor.start_monitoring(topic, description)
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在停止监控...")
        if 'monitor' in locals():
            await monitor.stop_monitoring()
    except Exception as e:
        print(f"❌ 监控系统错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())