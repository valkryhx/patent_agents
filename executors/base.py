#!/usr/bin/env python3
"""
Base Executor - Foundation for all stage executors
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseExecutor(ABC):
    """Base class for all stage executors"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        logger.info(f"🔧 Initialized {self.name}")
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the stage logic"""
        pass
    
    async def execute_test_mode(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute in test mode with mock results"""
        logger.info(f"🧪 {self.name} executing in test mode")
        
        # Mock execution delay
        import asyncio
        await asyncio.sleep(1.0)
        
        # Return mock result
        return self._get_mock_result(context)
    
    def _get_mock_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get mock result for test mode"""
        return {
            "status": "completed",
            "test_mode": True,
            "executor": self.name,
            "message": f"Mock execution completed for {self.name}"
        }