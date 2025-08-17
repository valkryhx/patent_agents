"""
Base Agent Test Mode
Provides test mode functionality for all patent development agents
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..test_mode_base import TestModeFactory, TestModeResponse

logger = logging.getLogger(__name__)

class BaseAgentTestMode(BaseAgent):
    """Base class for test mode agents"""
    
    def __init__(self, name: str, capabilities: List[str]):
        super().__init__(name, capabilities)
        self.test_mode = TestModeFactory.create_test_mode(name)
        self.logger = logging.getLogger(f"test_agent.{name}")
        
    async def start(self):
        """Start the test mode agent"""
        await super().start()
        self.logger.info(f"{self.name} started in TEST MODE")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute task using test mode"""
        try:
            task_type = task_data.get("type", "unknown")
            self.logger.info(f"TEST MODE: {self.name} executing task: {task_type}")
            
            # Get test mode response
            test_response = self.test_mode.get_test_response(task_type, task_data)
            
            # Convert test response to task result
            result = TaskResult(
                success=test_response.success,
                data={
                    "content": test_response.content,
                    "test_mode": True,
                    "agent": self.name,
                    "task_type": task_type,
                    "metadata": test_response.metadata
                },
                error_message=None if test_response.success else test_response.content,
                execution_time=test_response.execution_time,
                metadata=test_response.metadata
            )
            
            self.logger.info(f"TEST MODE: {self.name} completed task: {task_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"TEST MODE: Error in {self.name}: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=f"Test mode error: {str(e)}"
            )