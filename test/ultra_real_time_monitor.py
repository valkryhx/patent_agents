#!/usr/bin/env python3
"""
Ultra Real-Time Workflow Monitor - Log-Based Only
超实时工作流监控系统 - 仅基于日志文件监控，不向协调器发送任何任务
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
    """超实时工作流监控器 - 仅基于日志文件"""
    
    def __init__(self, workflow_id: str = None):
        self.workflow_id = workflow_id
        # 使用相对路径，在当前项目目录下
        self.monitor_dir = os.path.dirname(__file__)
        # 使用相对路径，在当前项目目录下创建output文件夹
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        self.log_file = os.path.join(os.path.dirname(__file__), "ultra_monitor.log")
        self.monitoring = False
        self.start_time = None
        self.last_status = None
        self.status_history = []
        self.file_changes = []
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
        """启动超实时监控 - 仅基于日志文件"""
        try:
            self.logger.info("🚀 启动超实时工作流监控系统 - 仅基于日志文件")
            self.logger.info("📋 监控策略: 仅通过日志文件监控，不向协调器发送任何任务")
            self.start_time = time.time()
            self.monitoring = True
            
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
        
    async def _ultra_monitor_loop(self):
        """超实时监控主循环 - 仅基于日志文件"""
        try:
            self.logger.info("🔄 开始超实时监控循环")
            
            while self.monitoring:
                try:
                    # 检查智能体日志文件
                    await self._check_agent_logs()
                    
                    # 检查输出文件
                    await self._check_output_files()
                    
                    # 检查系统资源
                    await self._check_system_resources()
                    
                    # 检查工作流状态（基于日志文件）
                    await self._check_workflow_status_from_logs()
                    
                    # 等待下一次检查
                    await asyncio.sleep(1)  # 每秒检查一次
                    
                except Exception as e:
                    self.logger.error(f"监控循环错误: {e}")
                    await asyncio.sleep(5)  # 出错时等待5秒
                    
        except Exception as e:
            self.logger.error(f"监控循环失败: {e}")
            
    async def _check_agent_logs(self):
        """检查智能体日志文件"""
        try:
            logs_dir = os.path.join(self.output_dir, "logs")
            if not os.path.exists(logs_dir):
                return
                
            # Check each agent log file
            agent_logs = [
                "coordinator_agent.log",
                "planner_agent.log", 
                "searcher_agent.log",
                "discusser_agent.log",
                "writer_agent.log",
                "reviewer_agent.log",
                "rewriter_agent.log"
            ]
            
            for log_file in agent_logs:
                log_path = os.path.join(logs_dir, log_file)
                if os.path.exists(log_path):
                    try:
                        file_stat = os.stat(log_path)
                        file_size = file_stat.st_size
                        file_mtime = file_stat.st_mtime
                        
                        # Check if log file changed
                        file_key = log_path
                        if file_key not in self.last_modified or self.last_modified[file_key] != file_mtime:
                            self.last_modified[file_key] = file_mtime
                            
                            # Read last few lines of the log
                            try:
                                with open(log_path, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    if lines:
                                        last_line = lines[-1].strip()
                                        # Only log important events (not heartbeat messages)
                                        if any(keyword in last_line for keyword in ["✅", "❌", "⚠️", "🎯", "🚀", "📤", "📋"]):
                                            agent_name = log_file.replace("_agent.log", "")
                                            self.logger.info(f"🤖 {agent_name}: {last_line}")
                                            
                            except Exception as e:
                                pass  # Skip unreadable log files
                                
                    except Exception as e:
                        pass  # Skip files with errors
                        
        except Exception as e:
            self.logger.error(f"检查智能体日志失败: {e}")
            
    async def _check_workflow_status_from_logs(self):
        """从日志文件检查工作流状态"""
        try:
            logs_dir = os.path.join(self.output_dir, "logs")
            if not os.path.exists(logs_dir):
                return
                
            # 检查协调器日志中的工作流状态
            coordinator_log = os.path.join(logs_dir, "coordinator_agent.log")
            if os.path.exists(coordinator_log):
                try:
                    with open(coordinator_log, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # 检查最后100行
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        
                        # 分析工作流状态
                        workflow_status = self._analyze_workflow_status_from_logs(recent_lines)
                        
                        if workflow_status != self.last_status:
                            self.last_status = workflow_status
                            self.status_history.append(workflow_status)
                            self.logger.info(f"🔥 工作流状态更新: {workflow_status}")
                            
                except Exception as e:
                    pass  # Skip unreadable log files
                    
        except Exception as e:
            self.logger.error(f"从日志检查工作流状态失败: {e}")
            
    def _analyze_workflow_status_from_logs(self, log_lines: List[str]) -> Dict[str, Any]:
        """从日志行分析工作流状态"""
        try:
            status = {
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "overall_status": "running",
                "current_stage": 0,
                "total_stages": 7,  # 默认7个阶段
                "progress": "0/7"
            }
            
            # 分析日志内容
            for line in log_lines:
                line = line.strip()
                
                # 检查阶段完成情况
                if "✅ 阶段完成" in line or "🎯 阶段" in line:
                    if "planner" in line.lower():
                        status["current_stage"] = max(status["current_stage"], 1)
                    elif "searcher" in line.lower():
                        status["current_stage"] = max(status["current_stage"], 2)
                    elif "discusser" in line.lower():
                        status["current_stage"] = max(status["current_stage"], 3)
                    elif "writer" in line.lower():
                        status["current_stage"] = max(status["current_stage"], 4)
                    elif "reviewer" in line.lower():
                        status["current_stage"] = max(status["current_stage"], 5)
                    elif "rewriter" in line.lower():
                        status["current_stage"] = max(status["current_stage"], 6)
                        
                # 检查工作流完成
                if "🎉 工作流完成" in line or "✅ 工作流完成" in line:
                    status["overall_status"] = "completed"
                    status["current_stage"] = 7
                    
                # 检查工作流失败
                if "❌ 工作流失败" in line or "error" in line.lower():
                    status["overall_status"] = "failed"
                    
            # 更新进度
            status["progress"] = f"{status['current_stage']}/{status['total_stages']}"
            
            return status
            
        except Exception as e:
            return {
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "overall_status": "unknown",
                "current_stage": 0,
                "total_stages": 7,
                "progress": "0/7",
                "error": str(e)
            }
            
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
            
            # Log resource usage (less frequent)
            if int(time.time()) % 30 == 0:  # 每30秒记录一次
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
                    if int(time.time()) % 30 == 0:  # 每30秒记录一次
                        self.logger.info(f"💻 内存使用: {memory_percent:.1f}%")
                    
            except Exception as e:
                if int(time.time()) % 30 == 0:  # 每30秒记录一次
                    self.logger.info(f"💻 系统资源监控: 基础模式")
                
        except Exception as e:
            self.logger.error(f"检查系统资源失败: {e}")
            
    async def _check_output_files(self):
        """检查输出文件"""
        try:
            # Check for new output files
            output_files = []
            if os.path.exists(self.output_dir):
                for file in os.listdir(self.output_dir):
                    if file.endswith('.md') or file.endswith('.txt') or file.endswith('.json'):
                        file_path = os.path.join(self.output_dir, file)
                        output_files.append(file_path)
                        
            # Check for changes in existing files
            for file_path in output_files:
                try:
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    file_mtime = file_stat.st_mtime
                    
                    # Check if file changed
                    file_key = file_path
                    if file_key not in self.last_modified or self.last_modified[file_key] != file_mtime:
                        self.last_modified[file_key] = file_mtime
                        
                        # Get file size change
                        old_size = self.last_file_sizes.get(file_key, 0)
                        size_change = file_size - old_size
                        self.last_file_sizes[file_key] = file_size
                        
                        # Log file change
                        file_name = os.path.basename(file_path)
                        self.logger.info(f"📄 文件更新: {file_name} | 大小变化: {size_change:+d} bytes | 总大小: {file_size} bytes")
                        
                        # Record file change
                        self.file_changes.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                            "file": file_name,
                            "size_change": size_change,
                            "total_size": file_size
                        })
                        
                except Exception as e:
                    pass  # Skip files with errors
                    
        except Exception as e:
            self.logger.error(f"检查输出文件失败: {e}")
            
    def _check_all_files(self):
        """检查所有相关文件"""
        try:
            # Check log files
            logs_dir = os.path.join(self.output_dir, "logs")
            if os.path.exists(logs_dir):
                for log_file in os.listdir(logs_dir):
                    if log_file.endswith('.log'):
                        log_path = os.path.join(logs_dir, log_file)
                        try:
                            file_stat = os.stat(log_path)
                            file_size = file_stat.st_size
                            file_mtime = file_stat.st_mtime
                            
                            # Check if log file changed
                            file_key = log_path
                            if file_key not in self.last_modified or self.last_modified[file_key] != file_mtime:
                                self.last_modified[file_key] = file_mtime
                                
                                # Read last line of the log
                                try:
                                    with open(log_path, 'r', encoding='utf-8') as f:
                                        lines = f.readlines()
                                        if lines:
                                            last_line = lines[-1].strip()
                                            # Only log important events
                                            if any(keyword in last_line for keyword in ["✅", "❌", "⚠️", "🎯", "🚀", "📤", "📋"]):
                                                agent_name = log_file.replace("_agent.log", "")
                                                self.logger.info(f"🤖 {agent_name}: {last_line}")
                                                
                                except Exception as e:
                                    pass  # Skip unreadable log files
                                    
                        except Exception as e:
                            pass  # Skip files with errors
                            
        except Exception as e:
            pass  # Silent error handling for file monitoring
            
    async def _save_status_update(self, status: Dict[str, Any]):
        """保存状态更新到文件"""
        try:
            status_file = os.path.join(self.output_dir, "workflow_status.json")
            
            # Load existing status history
            status_history = []
            if os.path.exists(status_file):
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        status_history = json.load(f)
                except Exception as e:
                    self.logger.warning(f"读取状态文件失败: {e}")
                    
            # Add new status
            status_history.append(status)
            
            # Keep only last 100 status updates
            if len(status_history) > 100:
                status_history = status_history[-100:]
                
            # Save updated status history
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存状态更新失败: {e}")
            
    def stop_monitoring(self):
        """停止监控"""
        self.logger.info("🛑 停止超实时监控")
        self.monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
            
        # Save final status
        if self.status_history:
            final_status = {
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "monitoring_duration": time.time() - self.start_time if self.start_time else 0,
                "total_status_updates": len(self.status_history),
                "total_file_changes": len(self.file_changes),
                "final_status": self.status_history[-1] if self.status_history else None
            }
            
            try:
                final_status_file = os.path.join(self.output_dir, "monitoring_summary.json")
                with open(final_status_file, 'w', encoding='utf-8') as f:
                    json.dump(final_status, f, ensure_ascii=False, indent=2)
                self.logger.info("✅ 监控摘要已保存")
            except Exception as e:
                self.logger.error(f"保存监控摘要失败: {e}")
                
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        return {
            "monitoring_duration": time.time() - self.start_time if self.start_time else 0,
            "total_status_updates": len(self.status_history),
            "total_file_changes": len(self.file_changes),
            "current_status": self.last_status,
            "file_changes": self.file_changes[-10:] if self.file_changes else [],  # Last 10 changes
            "status_history": self.status_history[-10:] if self.status_history else []  # Last 10 status updates
        }

async def main():
    """主函数"""
    try:
        # 创建监控器
        monitor = UltraRealTimeMonitor()
        
        # 设置主题和描述
        topic = "智能多参数工具调用系统"
        description = "一种基于智能分层推理的多参数工具自适应调用系统，通过分层推理和自适应机制提高调用准确性"
        
        # 启动监控
        await monitor.start_monitoring(topic, description)
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断监控")
    except Exception as e:
        print(f"❌ 监控失败: {e}")
    finally:
        if 'monitor' in locals():
            monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())