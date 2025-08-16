#!/usr/bin/env python3
"""
Detailed workflow monitor to diagnose issues
"""

import asyncio
import sys
import os
import logging
import time
import subprocess
import psutil
from datetime import datetime

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from enhanced_patent_workflow import EnhancedPatentWorkflow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/detailed_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DetailedWorkflowMonitor:
    def __init__(self):
        self.workflow = None
        self.start_time = None
        self.last_check = None
        
    async def start_workflow(self):
        """Start the patent workflow"""
        try:
            logger.info("🚀 Starting detailed workflow monitor")
            
            # Create workflow
            self.workflow = EnhancedPatentWorkflow(test_mode=False)
            logger.info("✅ Workflow created")
            
            # Start workflow
            self.start_time = datetime.now()
            workflow_id = await self.workflow.start_workflow()
            logger.info(f"✅ Workflow started with ID: {workflow_id}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"❌ Error starting workflow: {e}")
            return None
    
    async def monitor_progress(self):
        """Monitor workflow progress"""
        try:
            logger.info("📊 Starting progress monitoring")
            
            while True:
                current_time = datetime.now()
                
                # Check workflow status
                if self.workflow:
                    try:
                        status = await self.workflow.get_workflow_status()
                        logger.info(f"📈 Workflow Status: {status}")
                    except Exception as e:
                        logger.error(f"❌ Error getting status: {e}")
                
                # Check for new files
                self._check_new_files()
                
                # Check system resources
                self._check_system_resources()
                
                # Check for stuck processes
                self._check_stuck_processes()
                
                # Wait 30 seconds
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
    
    def _check_new_files(self):
        """Check for new patent files"""
        try:
            # Find all patent files
            result = subprocess.run(
                ['find', '.', '-name', 'enhanced_patent_*.md', '-type', 'f'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                if files and files[0]:
                    latest_file = max(files, key=os.path.getctime)
                    file_size = os.path.getsize(latest_file)
                    file_time = datetime.fromtimestamp(os.path.getctime(latest_file))
                    
                    logger.info(f"📄 Latest patent file: {latest_file}")
                    logger.info(f"📏 File size: {file_size} bytes")
                    logger.info(f"⏰ File time: {file_time}")
                    
                    # Check if file is growing
                    if self.last_check and latest_file == getattr(self, '_last_file', None):
                        if file_size > getattr(self, '_last_size', 0):
                            logger.info("✅ File is growing - workflow is active")
                        else:
                            logger.warning("⚠️ File not growing - workflow may be stuck")
                    
                    self._last_file = latest_file
                    self._last_size = file_size
                    
        except Exception as e:
            logger.error(f"❌ Error checking files: {e}")
    
    def _check_system_resources(self):
        """Check system resources"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Python processes
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            logger.info(f"💻 CPU: {cpu_percent}%, Memory: {memory.percent}%")
            logger.info(f"🐍 Python processes: {len(python_processes)}")
            
            # Check for high CPU processes
            high_cpu = [p for p in python_processes if p['cpu_percent'] > 10]
            if high_cpu:
                logger.info(f"🔥 High CPU processes: {high_cpu}")
                
        except Exception as e:
            logger.error(f"❌ Error checking resources: {e}")
    
    def _check_stuck_processes(self):
        """Check for stuck processes"""
        try:
            # Check for processes that have been running too long
            current_time = time.time()
            
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    if 'python' in proc.info['name'].lower():
                        runtime = current_time - proc.info['create_time']
                        if runtime > 300:  # 5 minutes
                            logger.warning(f"⚠️ Long-running process: PID {proc.info['pid']}, Runtime: {runtime:.1f}s")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            logger.error(f"❌ Error checking stuck processes: {e}")

async def main():
    """Main function"""
    monitor = DetailedWorkflowMonitor()
    
    # Start workflow
    workflow_id = await monitor.start_workflow()
    
    if workflow_id:
        # Monitor progress
        await monitor.monitor_progress()
    else:
        logger.error("❌ Failed to start workflow")

if __name__ == "__main__":
    asyncio.run(main())