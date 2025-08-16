"""
Discusser Agent Test Mode
Test mode version of the discusser agent
"""

import logging
from typing import Dict, Any, List

from .base_agent_test import BaseAgentTestMode

logger = logging.getLogger(__name__)

class DiscusserAgentTestMode(BaseAgentTestMode):
    """Test mode version of Discusser Agent"""
    
    def __init__(self):
        super().__init__(
            name="discusser_agent",
            capabilities=["patent_discussion", "collaborative_analysis", "idea_generation", "consensus_building"]
        )
        self.logger = logging.getLogger("test_agent.discusser_agent")
        
    async def start(self):
        """Start the test mode discusser agent"""
        await super().start()
        self.logger.info("Discusser Agent Test Mode started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]):
        """Execute discussion tasks in test mode"""
        self.logger.info(f"TEST MODE: Discusser Agent executing task: {task_data.get('type')}")
        return await super().execute_task(task_data)