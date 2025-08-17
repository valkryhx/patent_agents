"""
Reviewer Agent Test Mode
Test mode version of the reviewer agent
"""

import logging
from typing import Dict, Any, List

from .base_agent_test import BaseAgentTestMode

logger = logging.getLogger(__name__)

class ReviewerAgentTestMode(BaseAgentTestMode):
    """Test mode version of Reviewer Agent"""
    
    def __init__(self):
        super().__init__(
            name="reviewer_agent",
            capabilities=["patent_review", "quality_assessment", "compliance_check", "technical_validation"]
        )
        self.logger = logging.getLogger("test_agent.reviewer_agent")
        
    async def start(self):
        """Start the test mode reviewer agent"""
        await super().start()
        self.logger.info("Reviewer Agent Test Mode started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]):
        """Execute review tasks in test mode"""
        self.logger.info(f"TEST MODE: Reviewer Agent executing task: {task_data.get('type')}")
        return await super().execute_task(task_data)