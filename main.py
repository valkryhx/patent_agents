#!/usr/bin/env python3
"""
Patent Agent System - FastAPI Coordinator Service
Coordinates workflow execution by assigning tasks to agent services
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import time
import uuid
import httpx
import asyncio

from workflow_manager import WorkflowManager
from models import WorkflowRequest, WorkflowResponse, WorkflowStatus

# Initialize FastAPI app
app = FastAPI(
    title="Patent Agent System - Coordinator",
    description="Coordinates workflow execution by assigning tasks to agent services",
    version="2.0.0"
)

# Initialize workflow manager (in-memory)
workflow_manager = WorkflowManager()

# Agent service URLs (these would be the actual agent services)
AGENT_SERVICES = {
    "planner": "http://localhost:8001",
    "searcher": "http://localhost:8002", 
    "discusser": "http://localhost:8003",
    "writer": "http://localhost:8004",
    "reviewer": "http://localhost:8005",
    "rewriter": "http://localhost:8006"
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Patent Agent System - Coordinator v2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "active_workflows": len(workflow_manager.workflows),
        "agent_services": list(AGENT_SERVICES.keys()),
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
        background_tasks.add_task(workflow_manager.execute_workflow_with_agents, workflow_id)
        
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
        background_tasks.add_task(workflow_manager.execute_workflow_with_agents, workflow_id)
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

@app.get("/agents/status")
async def get_agent_status():
    """Check status of all agent services"""
    agent_status = {}
    
    async with httpx.AsyncClient() as client:
        for agent_name, agent_url in AGENT_SERVICES.items():
            try:
                response = await client.get(f"{agent_url}/health", timeout=5.0)
                agent_status[agent_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": agent_url
                }
            except Exception as e:
                agent_status[agent_name] = {
                    "status": "unreachable",
                    "url": agent_url,
                    "error": str(e)
                }
    
    return {"agent_services": agent_status}

if __name__ == "__main__":
    print("🚀 Starting Patent Agent System - Coordinator v2.0.0...")
    print("📡 Coordinator will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🤖 Agent services expected at:")
    for agent, url in AGENT_SERVICES.items():
        print(f"   - {agent}: {url}")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)