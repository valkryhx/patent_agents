#!/usr/bin/env python3
"""
Ultra Real-Time Workflow Monitor
超实时工作流监控系统 - 无需外部依赖，实时监控工作流进度
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
import glob

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.patent_agent_system import PatentAgentSystem

class UltraRealTimeMonitor:
    """超实时工作流监控器"""
    
    def __init__(self, workflow_id: str = None):
        self.workflow_id = workflow_id
        self.monitor_dir = "/workspace"
        self.output_dir = "/workspace/output"
        self.log_file = "/workspace/ultra_monitor.log"
        self.monitoring = False
        self.start_time = None
        self.last_status = None
        self.status_history = []
        self.file_changes = []
        self.system = None
        self.last_file_sizes = {}
        self.last_file_hashes = {}
        self.last_modified = {}
        self.monitor_thread = None
        
        # Create output directory if not exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging with millisecond precision
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
        """启动超实时监控"""
        try:
            self.logger.info("🚀 启动超实时工作流监控系统")
            self.start_time = time.time()
            self.monitoring = True
            
            # Start workflow
            await self._start_workflow(topic, description)
            
            # Start file monitoring thread
            self._start_file_monitoring_thread()
            
            # Start real-time monitoring loop
            await self._ultra_monitor_loop()
            
        except Exception as e:
            self.logger.error(f"监控启动失败: {e}")
            raise
            
    def _start_file_monitoring_thread(self):
        """启动文件监控线程"""
        def file_monitor_loop():
            while self.monitoring:
                try:
                    self._check_all_files()
                    time.sleep(0.5)  # Check every 500ms
                except Exception as e:
                    self.logger.error(f"文件监控错误: {e}")
                    
        self.monitor_thread = threading.Thread(target=file_monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("✅ 文件监控线程启动成功")
        
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
            
    async def _ultra_monitor_loop(self):
        """超实时监控循环"""
        try:
            self.logger.info("📊 开始超实时监控循环")
            
            while self.monitoring:
                current_time = time.time()
                
                # Monitor workflow status (every 1 second)
                if current_time - getattr(self, '_last_status_check', 0) >= 1:
                    await self._check_workflow_status()
                    self._last_status_check = current_time
                
                # Monitor system resources (every 3 seconds)
                if current_time - getattr(self, '_last_resource_check', 0) >= 3:
                    await self._check_system_resources()
                    self._last_resource_check = current_time
                
                # Monitor output files (every 0.5 seconds)
                if current_time - getattr(self, '_last_output_check', 0) >= 0.5:
                    await self._check_output_files()
                    self._last_output_check = current_time
                
                # Check for workflow completion
                if self._is_workflow_completed():
                    self.logger.info("✅ 工作流完成")
                    break
                
                # Ultra short sleep for maximum responsiveness
                await asyncio.sleep(0.2)  # 200ms intervals
                
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
                    
                    # Log status change with high visibility
                    self.logger.info(f"🔥 状态更新: {overall_status} | 阶段: {current_stage}/{total_stages} | 时间: {new_status['timestamp']}")
                    
                    # Save status to file
                    await self._save_status_update(new_status)
                    
        except Exception as e:
            self.logger.error(f"检查工作流状态失败: {e}")
            
    async def _check_system_resources(self):
        """检查系统资源"""
        try:
            # Get basic system info
            import psutil
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
            
        except ImportError:
            # Fallback without psutil
            try:
                # Get basic memory info from /proc
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    
                # Parse memory info
                total_mem = 0
                free_mem = 0
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        total_mem = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        free_mem = int(line.split()[1])
                        
                if total_mem > 0:
                    memory_percent = ((total_mem - free_mem) / total_mem) * 100
                    self.logger.info(f"💻 内存使用: {memory_percent:.1f}%")
                    
            except Exception as e:
                self.logger.info(f"💻 系统资源监控: 基础模式")
                
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
                        
                        self.logger.info(f"📄 输出文件更新: {file_path.name} ({file_size} bytes) - {output_info['timestamp']}")
                        
                        # Save output info
                        await self._save_output_update(output_info)
                        
                    except Exception as e:
                        self.logger.error(f"读取文件失败 {file_path}: {e}")
                        
        except Exception as e:
            self.logger.error(f"检查输出文件失败: {e}")
            
    def _check_all_files(self):
        """检查所有相关文件的变化"""
        try:
            # Check for various file types
            file_patterns = [
                "*.md", "*.log", "*.json", "*.txt", "*.py"
            ]
            
            for pattern in file_patterns:
                files = glob.glob(os.path.join(self.monitor_dir, pattern))
                
                for file_path in files:
                    try:
                        if os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            file_mtime = os.path.getmtime(file_path)
                            
                            # Check if file changed
                            file_key = file_path
                            if file_key not in self.last_file_sizes or self.last_file_sizes[file_key] != file_size:
                                self.last_file_sizes[file_key] = file_size
                                
                                # Calculate file hash for content change detection
                                try:
                                    with open(file_path, 'rb') as f:
                                        file_hash = hashlib.md5(f.read()).hexdigest()[:8]
                                        
                                    if file_key not in self.last_file_hashes or self.last_file_hashes[file_key] != file_hash:
                                        self.last_file_hashes[file_key] = file_hash
                                        
                                        # Log significant changes
                                        if file_size > 100:  # Only log files larger than 100 bytes
                                            rel_path = os.path.relpath(file_path, self.monitor_dir)
                                            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                            
                                            change_info = {
                                                "timestamp": current_time,
                                                "file": rel_path,
                                                "size": file_size,
                                                "hash": file_hash
                                            }
                                            
                                            self.file_changes.append(change_info)
                                            
                                            # Log important file changes
                                            if "enhanced_patent" in rel_path or "workflow" in rel_path:
                                                self.logger.info(f"📝 重要文件变化: {rel_path} ({file_size} bytes) - {current_time}")
                                                
                                except Exception as e:
                                    pass  # Skip files that can't be read
                                    
                    except Exception as e:
                        pass  # Skip files with errors
                        
        except Exception as e:
            pass  # Don't let file monitoring errors stop the main loop
            
    def _is_workflow_completed(self) -> bool:
        """检查工作流是否完成"""
        if not self.last_status:
            return False
            
        return self.last_status["overall_status"] in ["completed", "finished", "success"]
        
    async def _save_status_update(self, status: Dict[str, Any]):
        """保存状态更新"""
        try:
            status_file = os.path.join(self.output_dir, f"ultra_status_{self.workflow_id}.json")
            
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
            output_file = os.path.join(self.output_dir, f"ultra_output_{self.workflow_id}.json")
            
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
            self.logger.info("🛑 停止超实时监控")
            self.monitoring = False
            
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
                "status_history": self.status_history[-20:],  # Last 20 updates
                "file_changes": self.file_changes[-50:]  # Last 50 changes
            }
            
            report_file = os.path.join(self.output_dir, f"ultra_report_{self.workflow_id}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"📊 超实时监控报告已生成: {report_file}")
            
        except Exception as e:
            self.logger.error(f"生成最终报告失败: {e}")

async def main():
    """主函数"""
    try:
        # 定义专利主题
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种通过智能分层推理技术实现多参数工具自适应调用的系统，能够根据上下文和用户意图自动推断工具参数，提高大语言模型调用复杂工具的准确性和效率。"
        
        print("=" * 80)
        print("🚀 启动超实时工作流监控系统")
        print("=" * 80)
        print(f"主题: {topic}")
        print(f"描述: {description}")
        print("=" * 80)
        print("📊 监控间隔: 状态检查 1秒 | 资源检查 3秒 | 文件检查 0.5秒")
        print("=" * 80)
        
        # 创建监控器
        monitor = UltraRealTimeMonitor()
        
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