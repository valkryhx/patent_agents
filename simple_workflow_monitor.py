#!/usr/bin/env python3
"""
Simple workflow monitor without external dependencies
"""

import asyncio
import sys
import os
import logging
import time
import subprocess
from datetime import datetime

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from enhanced_patent_workflow import EnhancedPatentWorkflow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/simple_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleWorkflowMonitor:
    def __init__(self):
        self.workflow = None
        self.start_time = None
        self.last_check = None
        
    async def start_workflow(self):
        """Start the patent workflow"""
        try:
            logger.info("🚀 Starting simple workflow monitor")
            
            # Create workflow
            self.workflow = EnhancedPatentWorkflow(test_mode=False)
            logger.info("✅ Workflow created")
            
            # Start workflow
            self.start_time = datetime.now()
            topic = "基于智能分层推理的多参数工具自适应调用系统"
            description = "一种基于智能分层推理的多参数工具自适应调用系统，通过智能参数推断、分层参数管理、对话式参数收集、参数模板预设和智能参数验证优化等技术，解决大语言模型在调用高参数数量工具时的准确性和精确性问题。"
            workflow_id = await self.workflow.start_workflow(topic, description)
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
    
    def _check_stuck_processes(self):
        """Check for stuck processes"""
        try:
            # Check for Python processes
            result = subprocess.run(
                ['ps', 'aux', '|', 'grep', 'python', '|', 'grep', '-v', 'grep'],
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                logger.info(f"🐍 Python processes: {len(lines)}")
                
                # Check for long-running processes
                for line in lines:
                    if 'enhanced_patent_workflow' in line or 'ultra_real_time_monitor' in line:
                        logger.info(f"🔍 Found workflow process: {line[:100]}...")
                        
        except Exception as e:
            logger.error(f"❌ Error checking processes: {e}")

async def main():
    """Main function"""
    monitor = SimpleWorkflowMonitor()
    
    # Start workflow
    workflow_id = await monitor.start_workflow()
    
    if workflow_id:
        # Monitor progress
        await monitor.monitor_progress()
    else:
        logger.error("❌ Failed to start workflow")

if __name__ == "__main__":
    asyncio.run(main())