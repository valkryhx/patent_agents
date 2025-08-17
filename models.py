#!/usr/bin/env python3
"""
Simple Pydantic models for Patent Agent System
Ultra-simple data structures
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
import time

class WorkflowStatusEnum(str, Enum):
    """Workflow status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class StageStatusEnum(str, Enum):
    """Stage status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowRequest(BaseModel):
    """Request model for starting a workflow"""
    topic: str = Field(..., description="Patent topic")
    description: str = Field(..., description="Patent description")
    workflow_type: str = Field(default="enhanced", description="Workflow type")
    test_mode: bool = Field(default=False, description="Enable test mode for faster execution")

class WorkflowResponse(BaseModel):
    """Response model for workflow operations"""
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")

class StageInfo(BaseModel):
    """Stage information model"""
    name: str = Field(..., description="Stage name")
    status: StageStatusEnum = Field(default=StageStatusEnum.PENDING, description="Stage status")
    start_time: Optional[float] = Field(default=None, description="Stage start time")
    end_time: Optional[float] = Field(default=None, description="Stage end time")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Stage result")
    error: Optional[str] = Field(default=None, description="Stage error message")

class WorkflowStatus(BaseModel):
    """Workflow status model"""
    workflow_id: str = Field(..., description="Unique workflow ID")
    topic: str = Field(..., description="Patent topic")
    status: WorkflowStatusEnum = Field(..., description="Overall workflow status")
    test_mode: bool = Field(..., description="Test mode enabled")
    current_stage: int = Field(..., description="Current stage index")
    total_stages: int = Field(..., description="Total number of stages")
    progress: float = Field(..., description="Progress percentage (0-100)")
    stages: List[StageInfo] = Field(..., description="Stage information")
    created_at: float = Field(..., description="Creation timestamp")
    updated_at: float = Field(..., description="Last update timestamp")
    estimated_completion: Optional[float] = Field(default=None, description="Estimated completion time")

class WorkflowState(BaseModel):
    """Internal workflow state model"""
    workflow_id: str = Field(..., description="Unique workflow ID")
    topic: str = Field(..., description="Patent topic")
    description: str = Field(..., description="Patent description")
    workflow_type: str = Field(default="enhanced", description="Workflow type")
    test_mode: bool = Field(default=False, description="Test mode enabled")
    status: WorkflowStatusEnum = Field(default=WorkflowStatusEnum.PENDING, description="Workflow status")
    current_stage: int = Field(default=0, description="Current stage index")
    stages: List[str] = Field(default=[
        "planning", "search", "discussion", "drafting", "review", "rewrite"
    ], description="Stage names")
    stage_results: Dict[str, Any] = Field(default_factory=dict, description="Stage results")
    stage_statuses: Dict[str, StageStatusEnum] = Field(default_factory=dict, description="Stage statuses")
    stage_times: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Stage timing")
    errors: Dict[str, str] = Field(default_factory=dict, description="Stage errors")
    created_at: float = Field(default_factory=time.time, description="Creation timestamp")
    updated_at: float = Field(default_factory=time.time, description="Last update timestamp")

class TestModeConfig(BaseModel):
    """Test mode configuration"""
    enabled: bool = Field(default=True, description="Test mode enabled")
    mock_delay: float = Field(default=1.0, description="Mock execution delay in seconds")
    mock_results: bool = Field(default=True, description="Use mock results")