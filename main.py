#!/usr/bin/env python3
"""
Patent Agent System - FastAPI Server
Ultra-simple in-memory workflow management
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import time
import uuid

from workflow_manager import WorkflowManager
from models import WorkflowRequest, WorkflowResponse, WorkflowStatus

# Initialize FastAPI app
app = FastAPI(
    title="Patent Agent System",
    description="Ultra-simple patent workflow management",
    version="2.0.0"
)

# Initialize workflow manager (in-memory)
workflow_manager = WorkflowManager()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Patent Agent System v2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "active_workflows": len(workflow_manager.workflows),
        "timestamp": time.time()
    }

@app.post("/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Start a new patent workflow"""
    try:
        workflow_id = workflow_manager.create_workflow(
            topic=request.topic,
            description=request.description,
            workflow_type=request.workflow_type
        )
        
        # Start workflow execution in background
        background_tasks.add_task(workflow_manager.execute_workflow, workflow_id)
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="started",
            message="Workflow started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.get("/workflow/{workflow_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get workflow status and progress"""
    try:
        status = workflow_manager.get_workflow_status(workflow_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.get("/workflow/{workflow_id}/results")
async def get_workflow_results(workflow_id: str):
    """Get workflow results"""
    try:
        results = workflow_manager.get_workflow_results(workflow_id)
        return {"workflow_id": workflow_id, "results": results}
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@app.post("/workflow/{workflow_id}/restart")
async def restart_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    """Restart a failed workflow"""
    try:
        workflow_manager.reset_workflow(workflow_id)
        background_tasks.add_task(workflow_manager.execute_workflow, workflow_id)
        return {"workflow_id": workflow_id, "status": "restarted", "message": "Workflow restarted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart workflow: {str(e)}")

@app.get("/workflows")
async def list_workflows():
    """List all workflows"""
    try:
        workflows = workflow_manager.list_workflows()
        return {"workflows": workflows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@app.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    try:
        workflow_manager.delete_workflow(workflow_id)
        return {"workflow_id": workflow_id, "status": "deleted", "message": "Workflow deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Patent Agent System v2.0.0...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)