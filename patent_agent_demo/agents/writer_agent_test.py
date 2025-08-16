"""
Writer Agent Test Mode
Test mode version of the writer agent
"""

import logging
from typing import Dict, Any, List

from .base_agent_test import BaseAgentTestMode

logger = logging.getLogger(__name__)

class WriterAgentTestMode(BaseAgentTestMode):
    """Test mode version of Writer Agent"""
    
    def __init__(self):
        super().__init__(
            name="writer_agent",
            capabilities=["patent_drafting", "technical_writing", "claim_writing", "legal_compliance"]
        )
        self.logger = logging.getLogger("test_agent.writer_agent")
        
    async def start(self):
        """Start the test mode writer agent"""
        await super().start()
        self.logger.info("Writer Agent Test Mode started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]):
        """Execute writing tasks in test mode"""
        self.logger.info(f"TEST MODE: Writer Agent executing task: {task_data.get('type')}")
        return await super().execute_task(task_data)