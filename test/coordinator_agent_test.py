"""
Coordinator Agent Test Mode
Test mode version of the coordinator agent
"""

import logging
from typing import Dict, Any, List

from .base_agent_test import BaseAgentTestMode

logger = logging.getLogger(__name__)

class CoordinatorAgentTestMode(BaseAgentTestMode):
    """Test mode version of Coordinator Agent"""
    
    def __init__(self):
        super().__init__(
            name="coordinator_agent",
            capabilities=["workflow_coordination", "task_scheduling", "progress_monitoring", "resource_management"]
        )
        self.logger = logging.getLogger("test_agent.coordinator_agent")
        
    async def start(self):
        """Start the test mode coordinator agent"""
        await super().start()
        self.logger.info("Coordinator Agent Test Mode started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]):
        """Execute coordination tasks in test mode"""
        self.logger.info(f"TEST MODE: Coordinator Agent executing task: {task_data.get('type')}")
        return await super().execute_task(task_data)