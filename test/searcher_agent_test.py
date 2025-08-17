"""
Searcher Agent Test Mode
Test mode version of the searcher agent
"""

import logging
from typing import Dict, Any, List

from .base_agent_test import BaseAgentTestMode

logger = logging.getLogger(__name__)

class SearcherAgentTestMode(BaseAgentTestMode):
    """Test mode version of Searcher Agent"""
    
    def __init__(self):
        super().__init__(
            name="searcher_agent",
            capabilities=["patent_search", "prior_art_analysis", "competitive_analysis", "technology_mapping"]
        )
        self.logger = logging.getLogger("test_agent.searcher_agent")
        
    async def start(self):
        """Start the test mode searcher agent"""
        await super().start()
        self.logger.info("Searcher Agent Test Mode started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]):
        """Execute search tasks in test mode"""
        self.logger.info(f"TEST MODE: Searcher Agent executing task: {task_data.get('type')}")
        return await super().execute_task(task_data)