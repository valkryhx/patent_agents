"""
Planner Agent Test Mode
Test mode version of the planner agent
"""

import logging
from typing import Dict, Any, List

from .base_agent_test import BaseAgentTestMode

logger = logging.getLogger(__name__)

class PlannerAgentTestMode(BaseAgentTestMode):
    """Test mode version of Planner Agent"""
    
    def __init__(self):
        super().__init__(
            name="planner_agent",
            capabilities=["patent_planning", "strategy_development", "risk_assessment", "timeline_planning"]
        )
        self.logger = logging.getLogger("test_agent.planner_agent")
        
    async def start(self):
        """Start the test mode planner agent"""
        await super().start()
        self.logger.info("Planner Agent Test Mode started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]):
        """Execute patent planning tasks in test mode"""
        self.logger.info(f"TEST MODE: Planner Agent executing task: {task_data.get('type')}")
        return await super().execute_task(task_data)