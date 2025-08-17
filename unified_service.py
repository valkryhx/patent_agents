#!/usr/bin/env python3
"""
Unified Patent Agent System - Single FastAPI Service
Hosts coordinator and all agent services on one port with different URL paths
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import time
import uuid
import asyncio
import logging

from models import WorkflowRequest, WorkflowResponse, WorkflowStatus, WorkflowState, WorkflowStatusEnum, StageStatusEnum
from workflow_manager import WorkflowManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test mode configuration
TEST_MODE = {
    "enabled": True,
    "mock_delay": 1.0,  # seconds
    "mock_results": True,
    "skip_llm_calls": True
}

# Initialize FastAPI app
app = FastAPI(
    title="Unified Patent Agent System",
    description="Single service hosting coordinator and all agent services",
    version="2.0.0"
)

# Initialize workflow manager (in-memory)
workflow_manager = WorkflowManager()

# ============================================================================
# COORDINATOR ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified Patent Agent System v2.0.0", 
        "status": "running",
        "test_mode": TEST_MODE["enabled"],
        "services": {
            "coordinator": "/coordinator/*",
            "agents": {
                "planner": "/agents/planner/*",
                "searcher": "/agents/searcher/*",
                "discussion": "/agents/discussion/*",
                "writer": "/agents/writer/*",
                "reviewer": "/agents/reviewer/*",
                "rewriter": "/agents/rewriter/*"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "test_mode": TEST_MODE["enabled"],
        "active_workflows": len(workflow_manager.workflows),
        "services": ["coordinator", "planner", "searcher", "discussion", "writer", "reviewer", "rewriter"],
        "timestamp": time.time()
    }

@app.get("/test-mode")
async def get_test_mode():
    """Get test mode configuration"""
    return {
        "test_mode": TEST_MODE,
        "description": "Test mode configuration for the unified service"
    }

@app.post("/test-mode")
async def set_test_mode(test_config: Dict[str, Any]):
    """Set test mode configuration"""
    global TEST_MODE
    TEST_MODE.update(test_config)
    logger.info(f"🔧 Test mode updated: {TEST_MODE}")
    return {
        "message": "Test mode configuration updated",
        "test_mode": TEST_MODE
    }

# Coordinator endpoints
@app.post("/coordinator/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Start a new patent workflow"""
    try:
        logger.info(f"🚀 Starting workflow in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode")
        logger.info(f"📝 Topic: {request.topic}")
        logger.info(f"🔧 Test mode enabled: {TEST_MODE['enabled']}")
        
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
            message=f"Workflow started successfully in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@app.get("/coordinator/workflow/{workflow_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get workflow status and progress"""
    try:
        status = workflow_manager.get_workflow_status(workflow_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.get("/coordinator/workflow/{workflow_id}/results")
async def get_workflow_results(workflow_id: str):
    """Get workflow results"""
    try:
        results = workflow_manager.get_workflow_results(workflow_id)
        return {"workflow_id": workflow_id, "results": results, "test_mode": TEST_MODE["enabled"]}
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@app.post("/coordinator/workflow/{workflow_id}/restart")
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

@app.get("/coordinator/workflows")
async def list_workflows():
    """List all workflows"""
    try:
        workflows = workflow_manager.list_workflows()
        return {"workflows": workflows, "test_mode": TEST_MODE["enabled"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@app.delete("/coordinator/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    try:
        workflow_manager.delete_workflow(workflow_id)
        return {"workflow_id": workflow_id, "status": "deleted", "message": "Workflow deleted"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")

# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

class TaskRequest(BaseModel):
    """Task request model"""
    task_id: str
    workflow_id: str
    stage_name: str
    topic: str
    description: str
    previous_results: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    """Task response model"""
    task_id: str
    status: str
    result: Dict[str, Any]
    message: str
    test_mode: bool

# Planner Agent
@app.get("/agents/planner/health")
async def planner_health():
    """Planner agent health check"""
    return {
        "status": "healthy",
        "service": "planner_agent",
        "test_mode": TEST_MODE["enabled"],
        "capabilities": ["patent_planning", "strategy_development", "risk_assessment", "timeline_planning"],
        "timestamp": time.time()
    }

@app.post("/agents/planner/execute", response_model=TaskResponse)
async def planner_execute(request: TaskRequest):
    """Execute planner agent task"""
    try:
        logger.info(f"📋 Planner Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
        
        result = await execute_planner_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Patent planning completed successfully in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode",
            test_mode=TEST_MODE["enabled"]
        )
    except Exception as e:
        logger.error(f"❌ Planner Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# Searcher Agent
@app.get("/agents/searcher/health")
async def searcher_health():
    """Searcher agent health check"""
    return {
        "status": "healthy",
        "service": "searcher_agent",
        "test_mode": TEST_MODE["enabled"],
        "capabilities": ["prior_art_search", "patent_analysis", "competitive_research", "novelty_assessment"],
        "timestamp": time.time()
    }

@app.post("/agents/searcher/execute", response_model=TaskResponse)
async def searcher_execute(request: TaskRequest):
    """Execute searcher agent task"""
    try:
        logger.info(f"🔍 Searcher Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
        
        result = await execute_searcher_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Prior art search completed successfully in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode",
            test_mode=TEST_MODE["enabled"]
        )
    except Exception as e:
        logger.error(f"❌ Searcher Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# Discussion Agent
@app.get("/agents/discussion/health")
async def discussion_health():
    """Discussion agent health check"""
    return {
        "status": "healthy",
        "service": "discussion_agent",
        "test_mode": TEST_MODE["enabled"],
        "capabilities": ["innovation_discussion", "idea_generation", "technical_analysis"],
        "timestamp": time.time()
    }

@app.post("/agents/discussion/execute", response_model=TaskResponse)
async def discussion_execute(request: TaskRequest):
    """Execute discussion agent task"""
    try:
        logger.info(f"💬 Discussion Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
        
        result = await execute_discussion_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Innovation discussion completed successfully in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode",
            test_mode=TEST_MODE["enabled"]
        )
    except Exception as e:
        logger.error(f"❌ Discussion Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# Writer Agent
@app.get("/agents/writer/health")
async def writer_health():
    """Writer agent health check"""
    return {
        "status": "healthy",
        "service": "writer_agent",
        "test_mode": TEST_MODE["enabled"],
        "capabilities": ["patent_drafting", "technical_writing", "claim_writing", "legal_compliance"],
        "timestamp": time.time()
    }

@app.post("/agents/writer/execute", response_model=TaskResponse)
async def writer_execute(request: TaskRequest):
    """Execute writer agent task"""
    try:
        logger.info(f"✍️ Writer Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
        
        result = await execute_writer_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Patent drafting completed successfully in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode",
            test_mode=TEST_MODE["enabled"]
        )
    except Exception as e:
        logger.error(f"❌ Writer Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# Reviewer Agent
@app.get("/agents/reviewer/health")
async def reviewer_health():
    """Reviewer agent health check"""
    return {
        "status": "healthy",
        "service": "reviewer_agent",
        "test_mode": TEST_MODE["enabled"],
        "capabilities": ["quality_review", "compliance_check", "feedback_generation"],
        "timestamp": time.time()
    }

@app.post("/agents/reviewer/execute", response_model=TaskResponse)
async def reviewer_execute(request: TaskRequest):
    """Execute reviewer agent task"""
    try:
        logger.info(f"🔍 Reviewer Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
        
        result = await execute_reviewer_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Quality review completed successfully in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode",
            test_mode=TEST_MODE["enabled"]
        )
    except Exception as e:
        logger.error(f"❌ Reviewer Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# Rewriter Agent
@app.get("/agents/rewriter/health")
async def rewriter_health():
    """Rewriter agent health check"""
    return {
        "status": "healthy",
        "service": "rewriter_agent",
        "test_mode": TEST_MODE["enabled"],
        "capabilities": ["patent_rewriting", "improvement_generation", "final_polish"],
        "timestamp": time.time()
    }

@app.post("/agents/rewriter/execute", response_model=TaskResponse)
async def rewriter_execute(request: TaskRequest):
    """Execute rewriter agent task"""
    try:
        logger.info(f"✏️ Rewriter Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
        
        result = await execute_rewriter_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Patent rewriting completed successfully in {'TEST' if TEST_MODE['enabled'] else 'REAL'} mode",
            test_mode=TEST_MODE["enabled"]
        )
    except Exception as e:
        logger.error(f"❌ Rewriter Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# ============================================================================
# AGENT TASK EXECUTION FUNCTIONS
# ============================================================================

async def execute_planner_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute planner task using old system prompts"""
    topic = request.topic
    description = request.description
    
    logger.info(f"🚀 Starting patent planning for: {topic}")
    logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
    
    # Add test mode delay
    if TEST_MODE["enabled"]:
        await asyncio.sleep(TEST_MODE["mock_delay"])
        logger.info(f"⏱️ Test mode delay: {TEST_MODE['mock_delay']}s")
    
    # Mock execution with old system prompts
    analysis = await analyze_patent_topic(topic, description)
    strategy = await develop_strategy(topic, description, analysis)
    phases = await create_development_phases(strategy)
    risk_assessment = await assess_competitive_risks(strategy, analysis)
    timeline_estimate = await estimate_timeline(phases)
    resource_requirements = await estimate_resources(phases)
    success_probability = await calculate_success_probability(strategy, risk_assessment)
    
    final_strategy = {
        "topic": topic,
        "description": description,
        "novelty_score": analysis.get("novelty_score", 8.5),
        "inventive_step_score": analysis.get("inventive_step_score", 7.8),
        "patentability_assessment": analysis.get("patentability_assessment", "Strong"),
        "development_phases": phases,
        "key_innovation_areas": strategy.get("key_innovation_areas", []),
        "competitive_analysis": risk_assessment.get("competitive_analysis", {}),
        "risk_assessment": risk_assessment,
        "timeline_estimate": timeline_estimate,
        "resource_requirements": resource_requirements,
        "success_probability": success_probability
    }
    
    return {
        "strategy": final_strategy,
        "analysis": analysis,
        "recommendations": analysis.get("recommendations", []),
        "execution_time": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 1.0,
        "test_mode": TEST_MODE["enabled"],
        "mock_delay_applied": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 0
    }

async def execute_searcher_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute searcher task using old system prompts"""
    topic = request.topic
    description = request.description
    
    logger.info(f"🚀 Starting prior art search for: {topic}")
    logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
    
    # Add test mode delay
    if TEST_MODE["enabled"]:
        await asyncio.sleep(TEST_MODE["mock_delay"])
        logger.info(f"⏱️ Test mode delay: {TEST_MODE['mock_delay']}s")
    
    keywords = await extract_keywords(topic, description)
    search_results = await conduct_prior_art_search(topic, keywords, {})
    analysis = await analyze_search_results(search_results, topic)
    novelty_assessment = await assess_novelty(search_results, analysis)
    recommendations = await generate_recommendations(search_results, analysis, novelty_assessment)
    
    search_report = {
        "query": {"topic": topic, "keywords": keywords, "date_range": "Last 20 years", "jurisdiction": "Global", "max_results": 50},
        "results": search_results,
        "analysis": analysis,
        "recommendations": recommendations,
        "risk_assessment": novelty_assessment.get("risk_assessment", {}),
        "novelty_score": novelty_assessment.get("novelty_score", 8.0)
    }
    
    return {
        "search_results": search_report,
        "patents_found": len(search_results),
        "novelty_score": novelty_assessment.get("novelty_score", 8.0),
        "risk_level": novelty_assessment.get("risk_level", "Low"),
        "recommendations": recommendations,
        "execution_time": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 1.0,
        "test_mode": TEST_MODE["enabled"],
        "mock_delay_applied": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 0
    }

async def execute_discussion_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute discussion task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting innovation discussion for: {topic}")
    logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
    
    # Add test mode delay
    if TEST_MODE["enabled"]:
        await asyncio.sleep(TEST_MODE["mock_delay"])
        logger.info(f"⏱️ Test mode delay: {TEST_MODE['mock_delay']}s")
    
    discussion_result = {
        "topic": topic,
        "innovations": [
            "Enhanced layered reasoning architecture",
            "Improved multi-parameter optimization",
            "Advanced context-aware processing"
        ],
        "technical_insights": [
            "Novel approach to parameter inference",
            "Unique system integration methodology",
            "Innovative user intent modeling"
        ],
        "recommendations": [
            "Focus on layered reasoning as key differentiator",
            "Emphasize adaptive parameter optimization",
            "Highlight context-aware capabilities"
        ],
        "execution_time": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 1.0,
        "test_mode": TEST_MODE["enabled"],
        "mock_delay_applied": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 0
    }
    
    return discussion_result

async def execute_writer_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute writer task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting patent drafting for: {topic}")
    logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
    
    # Add test mode delay
    if TEST_MODE["enabled"]:
        await asyncio.sleep(TEST_MODE["mock_delay"])
        logger.info(f"⏱️ Test mode delay: {TEST_MODE['mock_delay']}s")
    
    patent_draft = {
        "title": f"Patent Application: {topic}",
        "abstract": f"An innovative system for {topic.lower()} that provides enhanced functionality and efficiency.",
        "claims": [
            "A system for intelligent parameter inference comprising...",
            "The system of claim 1, further comprising...",
            "A method for adaptive tool calling comprising..."
        ],
        "detailed_description": f"Detailed technical description of the {topic} system...",
        "technical_diagrams": ["Figure 1: System Architecture", "Figure 2: Process Flow"],
        "execution_time": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 1.0,
        "test_mode": TEST_MODE["enabled"],
        "mock_delay_applied": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 0
    }
    
    return patent_draft

async def execute_reviewer_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute reviewer task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting quality review for: {topic}")
    logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
    
    # Add test mode delay
    if TEST_MODE["enabled"]:
        await asyncio.sleep(TEST_MODE["mock_delay"])
        logger.info(f"⏱️ Test mode delay: {TEST_MODE['mock_delay']}s")
    
    review_result = {
        "quality_score": 8.5,
        "compliance_check": {
            "legal_requirements": "Pass",
            "technical_accuracy": "Pass", 
            "clarity": "Pass"
        },
        "feedback": [
            "Excellent technical description",
            "Claims are well-structured",
            "Consider adding more examples"
        ],
        "recommendations": [
            "Proceed with filing",
            "Minor improvements suggested",
            "Overall quality is high"
        ],
        "execution_time": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 1.0,
        "test_mode": TEST_MODE["enabled"],
        "mock_delay_applied": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 0
    }
    
    return review_result

async def execute_rewriter_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute rewriter task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting patent rewriting for: {topic}")
    logger.info(f"🔧 Test mode: {TEST_MODE['enabled']}")
    
    # Add test mode delay
    if TEST_MODE["enabled"]:
        await asyncio.sleep(TEST_MODE["mock_delay"])
        logger.info(f"⏱️ Test mode delay: {TEST_MODE['mock_delay']}s")
    
    improved_draft = {
        "title": f"Improved Patent Application: {topic}",
        "abstract": f"An enhanced system for {topic.lower()} with improved functionality and efficiency.",
        "claims": [
            "An improved system for intelligent parameter inference comprising...",
            "The system of claim 1, further comprising enhanced features...",
            "An optimized method for adaptive tool calling comprising..."
        ],
        "detailed_description": f"Enhanced technical description of the {topic} system with improvements...",
        "improvements": [
            "Enhanced clarity in claims",
            "Additional technical examples",
            "Improved abstract description"
        ],
        "execution_time": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 1.0,
        "test_mode": TEST_MODE["enabled"],
        "mock_delay_applied": TEST_MODE["mock_delay"] if TEST_MODE["enabled"] else 0
    }
    
    return improved_draft

# ============================================================================
# HELPER FUNCTIONS (from old system)
# ============================================================================

async def analyze_patent_topic(topic: str, description: str) -> Dict[str, Any]:
    """Analyze patent topic (mock implementation using old prompts)"""
    logger.info(f"🔍 Analyzing patent topic: {topic}")
    return {
        "novelty_score": 8.5,
        "inventive_step_score": 7.8,
        "industrial_applicability": True,
        "prior_art_analysis": [],
        "claim_analysis": {},
        "technical_merit": {},
        "commercial_potential": "Medium to High",
        "patentability_assessment": "Strong",
        "recommendations": [
            "Improve claim specificity",
            "Add more technical details",
            "Consider design-around strategies"
        ]
    }

async def develop_strategy(topic: str, description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Develop patent strategy (mock implementation)"""
    logger.info(f"📊 Developing strategy for: {topic}")
    return {
        "key_innovation_areas": [
            "Core algorithm innovation",
            "System architecture design",
            "Integration methodology"
        ],
        "competitive_positioning": "Emerging technology leader",
        "filing_strategy": "Proactive patent protection",
        "market_focus": "Primary and secondary markets"
    }

async def create_development_phases(strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create development phases (mock implementation)"""
    logger.info("📅 Creating development phases")
    return [
        {
            "phase_name": "Drafting & Review",
            "duration_estimate": "3-4 weeks",
            "key_deliverables": [
                "Patent application draft",
                "Technical diagrams",
                "Review feedback incorporated"
            ],
            "dependencies": ["Strategy Development"],
            "resource_requirements": {
                "patent_attorneys": 2,
                "technical_writers": 1,
                "illustrators": 1
            },
            "success_criteria": [
                "Draft meets legal requirements",
                "Technical accuracy verified",
                "Stakeholder approval obtained"
            ]
        }
    ]

async def assess_competitive_risks(strategy: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Assess competitive risks (mock implementation)"""
    logger.info("⚠️ Assessing competitive risks")
    return {
        "overall_risk_level": "Medium",
        "risk_factors": {
            "prior_art_risks": {
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Comprehensive prior art search"
            },
            "competitive_filing_risks": {
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Accelerated filing strategy"
            }
        },
        "competitive_analysis": {
            "market_position": "Emerging technology leader",
            "competitive_advantages": [
                "Higher novelty score",
                "Strong inventive step",
                "Clear industrial applicability"
            ],
            "threat_level": "Medium",
            "response_strategy": "Proactive patent protection and market positioning"
        },
        "risk_mitigation_strategies": [
            "Comprehensive prior art analysis",
            "Strong patent documentation",
            "Accelerated filing timeline"
        ]
    }

async def estimate_timeline(phases: List[Dict[str, Any]]) -> str:
    """Estimate timeline (mock implementation)"""
    logger.info("⏰ Estimating timeline")
    return "Total development time: 3-6 months, Filing to grant: 6-18 months"

async def estimate_resources(phases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Estimate resources (mock implementation)"""
    logger.info("💰 Estimating resources")
    return {
        "human_resources": {
            "patent_attorneys": 2,
            "researchers": 2,
            "technical_experts": 1
        },
        "estimated_costs": {
            "total_estimated": "$21,000 - $39,000"
        },
        "resource_allocation": "Phased approach with peak during drafting phase"
    }

async def calculate_success_probability(strategy: Dict[str, Any], risk_assessment: Dict[str, Any]) -> float:
    """Calculate success probability (mock implementation)"""
    logger.info("📈 Calculating success probability")
    return 0.75

async def extract_keywords(topic: str, description: str) -> List[str]:
    """Extract keywords from topic and description (mock implementation)"""
    logger.info(f"🔑 Extracting keywords from: {topic}")
    return [
        "intelligent", "layered", "reasoning", "multi-parameter", 
        "tool", "adaptive", "calling", "system", "context",
        "user intent", "inference", "accuracy", "efficiency"
    ]

async def conduct_prior_art_search(topic: str, keywords: List[str], previous_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Conduct comprehensive prior art search (mock implementation)"""
    logger.info(f"🔍 Conducting prior art search for: {topic}")
    return [
        {
            "patent_id": "US1234567",
            "title": "Intelligent Parameter Inference System",
            "abstract": "A system for automatically inferring parameters for tool calls based on context and user intent",
            "filing_date": "2022-01-15",
            "publication_date": "2023-07-20",
            "assignee": "Tech Corp Inc",
            "relevance_score": 0.85,
            "similarity_analysis": {
                "concept_overlap": "High",
                "technical_similarity": "Medium",
                "implementation_differences": "Significant"
            }
        }
    ]

async def analyze_search_results(search_results: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
    """Analyze search results (mock implementation)"""
    logger.info(f"📊 Analyzing search results for: {topic}")
    return {
        "total_patents_found": len(search_results),
        "high_relevance_count": len([r for r in search_results if r.get("relevance_score", 0) > 0.8]),
        "medium_relevance_count": len([r for r in search_results if 0.5 <= r.get("relevance_score", 0) <= 0.8]),
        "low_relevance_count": len([r for r in search_results if r.get("relevance_score", 0) < 0.5]),
        "technology_trends": [
            "Increasing focus on intelligent parameter inference",
            "Growing adoption of context-aware systems",
            "Rising interest in adaptive tool calling"
        ],
        "competitive_landscape": {
            "major_players": ["Tech Corp Inc", "Innovation Labs LLC", "Advanced Systems Corp"],
            "market_concentration": "Medium",
            "entry_barriers": "High"
        },
        "technical_gaps": [
            "Limited focus on layered reasoning approaches",
            "Insufficient attention to user intent modeling",
            "Lack of comprehensive multi-parameter optimization"
        ]
    }

async def assess_novelty(search_results: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Assess novelty and patentability (mock implementation)"""
    logger.info("🎯 Assessing novelty and patentability")
    return {
        "novelty_score": 8.0,
        "inventive_step_score": 7.5,
        "industrial_applicability": True,
        "risk_level": "Low to Medium",
        "risk_factors": {
            "prior_art_risks": {
                "probability": "Low",
                "impact": "Medium",
                "mitigation": "Focus on unique layered reasoning approach"
            },
            "obviousness_risks": {
                "probability": "Medium",
                "impact": "High",
                "mitigation": "Emphasize non-obvious technical solutions"
            }
        },
        "patentability_assessment": "Strong",
        "key_differentiators": [
            "Layered reasoning architecture",
            "Multi-parameter adaptive optimization",
            "Context-aware user intent modeling"
        ]
    }

async def generate_recommendations(search_results: List[Dict[str, Any]], analysis: Dict[str, Any], novelty_assessment: Dict[str, Any]) -> List[str]:
    """Generate recommendations (mock implementation)"""
    logger.info("💡 Generating recommendations")
    return [
        "Proceed with patent filing - strong novelty and inventive step identified",
        "Focus on layered reasoning architecture as key differentiator",
        "Emphasize multi-parameter optimization capabilities",
        "Consider design-around strategies for identified prior art",
        "Accelerate filing timeline to establish priority",
        "Include comprehensive technical diagrams and examples"
    ]

if __name__ == "__main__":
    print("🚀 Starting Unified Patent Agent System v2.0.0...")
    print(f"🔧 Test mode: {'ENABLED' if TEST_MODE['enabled'] else 'DISABLED'}")
    print(f"⏱️ Test delay: {TEST_MODE['mock_delay']}s")
    print("📡 Single service will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🤖 All agents available at:")
    print("   - Coordinator: /coordinator/*")
    print("   - Planner: /agents/planner/*")
    print("   - Searcher: /agents/searcher/*")
    print("   - Discussion: /agents/discussion/*")
    print("   - Writer: /agents/writer/*")
    print("   - Reviewer: /agents/reviewer/*")
    print("   - Rewriter: /agents/rewriter/*")
    print("🔧 Test mode endpoints:")
    print("   - GET /test-mode - Check test mode status")
    print("   - POST /test-mode - Update test mode settings")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)