#!/usr/bin/env python3
"""
Unified Patent Agent System - Single FastAPI Service
Hosts coordinator and all agent services on one port with different URL paths
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import time
import uuid
import asyncio
import logging
import httpx # Added for patent-specific API calls
import os
import json

from models import WorkflowRequest, WorkflowResponse, WorkflowStatus, WorkflowState, WorkflowStatusEnum, StageStatusEnum
from workflow_manager import WorkflowManager

# 导入GLM客户端
try:
    from glm_wrapper import get_glm_client
    GLM_AVAILABLE = True
except ImportError:
    GLM_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GLM客户端状态日志
if GLM_AVAILABLE:
    logger.info("✅ GLM客户端导入成功")
else:
    logger.warning("⚠️ 无法导入GLM客户端，将使用mock数据")

# Test mode configuration - DEPRECATED: Now using workflow-specific test_mode
# This global configuration is kept for backward compatibility but should not be used
TEST_MODE = {
    "enabled": False,  # Default to real mode
    "mock_delay": 0.5,  # seconds
    "mock_results": False,
    "skip_llm_calls": False
}

# Initialize FastAPI app
app = FastAPI(
    title="Unified Patent Agent System",
    description="Single service hosting coordinator and all agent services",
    version="2.0.0"
)

# Initialize workflow manager (in-memory)
workflow_manager = WorkflowManager()

# WebSocket connection manager for real-time notifications
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.workflow_subscribers: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workflow_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if workflow_id:
            if workflow_id not in self.workflow_subscribers:
                self.workflow_subscribers[workflow_id] = []
            self.workflow_subscribers[workflow_id].append(websocket)
        
        logger.info(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, workflow_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if workflow_id and workflow_id in self.workflow_subscribers:
            if websocket in self.workflow_subscribers[workflow_id]:
                self.workflow_subscribers[workflow_id].remove(websocket)
        
        logger.info(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.disconnect(websocket)

    async def broadcast_workflow_update(self, workflow_id: str, message: Dict[str, Any]):
        """Broadcast workflow update to all subscribers"""
        if workflow_id in self.workflow_subscribers:
            disconnected = []
            for websocket in self.workflow_subscribers[workflow_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to websocket: {e}")
                    disconnected.append(websocket)
            
            # Remove disconnected websockets
            for websocket in disconnected:
                self.disconnect(websocket, workflow_id)

manager = ConnectionManager()

# ============================================================================
# PATENT-SPECIFIC API ENDPOINTS
# ============================================================================

async def create_workflow_directory(workflow_id: str, topic: str) -> str:
    """Create a directory for storing individual stage results"""
    try:
        # Create workflow-specific directory
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length and replace spaces
        
        dir_name = f"{workflow_id}_{safe_topic}"
        dir_path = f"workflow_stages/{dir_name}"
        
        # Create directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        
        # Create a metadata file
        metadata = {
            "workflow_id": workflow_id,
            "topic": topic,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "stages": ["planning", "search", "discussion", "drafting", "review", "rewrite"],
            "status": "created"
        }
        
        with open(f"{dir_path}/metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Create workflow metadata file for tracking all files
        workflow_metadata = {
            "workflow_id": workflow_id,
            "topic": topic,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "files": {}
        }
        
        with open(f"{dir_path}/workflow_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(workflow_metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 Created workflow directory: {dir_path}")
        return dir_path
        
    except Exception as e:
        logger.error(f"Failed to create workflow directory: {e}")
        raise

async def save_stage_result(workflow_id: str, topic: str, stage: str, result: Any, test_mode: bool = False) -> str:
    """Save individual stage result to file"""
    try:
        # Get or create workflow directory
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')[:50]
        dir_name = f"{workflow_id}_{safe_topic}"
        dir_path = f"workflow_stages/{dir_name}"
        
        # Create directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        
        # Create stage result file
        timestamp = int(time.time())
        filename = f"{stage}_{timestamp}.md"
        file_path = f"{dir_path}/{filename}"
        
        # Generate stage content
        stage_content = generate_stage_content(stage, result, test_mode)
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(stage_content)
        
        # Update stage index and workflow metadata
        await update_stage_index(dir_path, stage, filename, timestamp)
        await update_workflow_metadata(dir_path, stage, filename, timestamp)
        
        logger.info(f"💾 Saved {stage} stage result: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save {stage} stage result: {e}")
        raise

def generate_stage_content(stage: str, result: Any, test_mode: bool = False) -> str:
    """Generate content for individual stage result"""
    content = []
    
    # Header
    content.append(f"# {stage.title()} 阶段结果")
    content.append(f"")
    content.append(f"**阶段**: {stage}")
    content.append(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    content.append(f"**模式**: {'测试模式' if test_mode else '真实模式'}")
    content.append(f"")
    
    if test_mode:
        # Test mode content
        content.append("## 📝 测试模式结果")
        content.append("")
        content.append(f"{result}")
        content.append("")
        content.append("**注意**: 这是测试模式生成的内容，用于验证功能。")
    else:
        # Real mode content
        content.append("## 🔍 详细结果")
        content.append("")
        if isinstance(result, dict):
            for key, value in result.items():
                content.append(f"### {key}")
                content.append(f"{value}")
                content.append("")
        else:
            content.append(f"{result}")
    
    return "\n".join(content)

async def update_stage_index(dir_path: str, stage: str, filename: str, timestamp: int):
    """Update stage index file"""
    try:
        index_file = f"{dir_path}/stage_index.json"
        
        # Load existing index or create new one
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"stages": {}, "final_patent": None}
        
        # Update stage information
        index["stages"][stage] = {
            "filename": filename,
            "timestamp": timestamp,
            "generated_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save updated index
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to update stage index: {e}")

async def update_workflow_metadata(dir_path: str, file_type: str, filename: str, timestamp: int):
    """Update workflow metadata file"""
    try:
        metadata_file = f"{dir_path}/workflow_metadata.json"
        
        # Load existing metadata or create new one
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {"files": {}}
        
        # Update file information
        metadata["files"][file_type] = {
            "filename": filename,
            "timestamp": timestamp,
            "generated_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save updated metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to update workflow metadata: {e}")

async def save_patent_to_file(workflow_id: str, topic: str, results: Dict[str, Any]) -> str:
    """Save final patent document to workflow directory"""
    try:
        # Create patent content
        patent_content = generate_patent_content(topic, results)
        
        # Get workflow directory path
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')[:50]
        dir_name = f"{workflow_id}_{safe_topic}"
        dir_path = f"workflow_stages/{dir_name}"
        
        # Create directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)
        
        # Save final patent document to workflow directory
        timestamp = int(time.time())
        filename = f"final_patent_{timestamp}.md"
        file_path = f"{dir_path}/{filename}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(patent_content)
        
        # Update metadata to include final patent
        await update_workflow_metadata(dir_path, "final_patent", filename, timestamp)
        
        logger.info(f"💾 Final patent saved to workflow directory: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save final patent: {e}")
        raise

def generate_patent_content(topic: str, results: Dict[str, Any]) -> str:
    """Generate formatted patent content from workflow results"""
    content = []
    
    # Header
    content.append(f"# 专利撰写结果")
    content.append(f"")
    content.append(f"**主题**: {topic}")
    content.append(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    content.append(f"**工作流ID**: {list(results.keys())[0] if results else 'Unknown'}")
    content.append(f"")
    
    # Check if this is test mode (simple string results) or real mode (complex dict results)
    is_test_mode = any(isinstance(result, str) for result in results.values())
    
    if is_test_mode:
        # Test mode - generate simple content from mock results
        content.append("## 📝 测试模式专利内容")
        content.append("")
        content.append("**注意**: 这是测试模式生成的内容，用于验证工作流功能。")
        content.append("")
        
        for stage, result in results.items():
            content.append(f"### {stage.title()} 阶段")
            content.append(f"{result}")
            content.append("")
        
        content.append("## 🔄 真实模式说明")
        content.append("")
        content.append("在真实模式下，每个阶段将包含详细的专利内容：")
        content.append("- **规划阶段**: 策略分析、开发阶段规划")
        content.append("- **搜索阶段**: 现有技术搜索结果、新颖性评分")
        content.append("- **讨论阶段**: 创新点、技术洞察")
        content.append("- **草稿阶段**: 专利标题、摘要、权利要求、详细描述")
        content.append("- **审查阶段**: 质量评分、审查反馈")
        content.append("- **重写阶段**: 改进后的专利内容")
        
    else:
        # Real mode - generate detailed content from agent results
        # Planning stage
        if "planning" in results:
            planning = results["planning"]
            content.append("## 1. 专利规划阶段")
            content.append("")
            if "strategy" in planning:
                strategy = planning["strategy"]
                content.append(f"### 策略分析")
                content.append(f"- **新颖性评分**: {strategy.get('novelty_score', 'N/A')}")
                content.append(f"- **创造性评分**: {strategy.get('inventive_step_score', 'N/A')}")
                content.append(f"- **可专利性评估**: {strategy.get('patentability_assessment', 'N/A')}")
                content.append("")
                content.append(f"### 开发阶段")
                for phase in strategy.get('development_phases', []):
                    content.append(f"- **{phase.get('phase_name', 'Unknown')}**: {phase.get('duration_estimate', 'N/A')}")
                content.append("")
            
            if "analysis" in planning:
                analysis = planning["analysis"]
                content.append(f"### 专利性分析")
                content.append(f"- **工业实用性**: {analysis.get('industrial_applicability', 'N/A')}")
                content.append(f"- **商业潜力**: {analysis.get('commercial_potential', 'N/A')}")
                content.append(f"- **改进建议**: {', '.join(analysis.get('recommendations', []))}")
                content.append("")
        
        # Search stage
        if "search" in results:
            search = results["search"]
            content.append("## 2. 现有技术搜索")
            content.append("")
            content.append(f"- **找到相关专利**: {search.get('patents_found', 0)} 件")
            content.append(f"- **新颖性评分**: {search.get('novelty_score', 'N/A')}")
            content.append(f"- **风险等级**: {search.get('risk_level', 'N/A')}")
            content.append("")
            if "search_results" in search and "results" in search["search_results"]:
                content.append("### 相关专利")
                for patent in search["search_results"]["results"]:
                    content.append(f"- **{patent.get('title', 'Unknown')}** (ID: {patent.get('patent_id', 'N/A')})")
                    content.append(f"  - 相关性: {patent.get('relevance_score', 'N/A')}")
                content.append("")
            
            if "recommendations" in search:
                content.append(f"### 检索建议")
                for rec in search["recommendations"]:
                    content.append(f"- {rec}")
                content.append("")
        
        # Discussion stage
        if "discussion" in results:
            discussion = results["discussion"]
            content.append("## 3. 创新讨论")
            content.append("")
            if "innovations" in discussion:
                content.append("### 创新点")
                for innovation in discussion["innovations"]:
                    content.append(f"- {innovation}")
                content.append("")
            if "technical_insights" in discussion:
                content.append("### 技术洞察")
                for insight in discussion["technical_insights"]:
                    content.append(f"- {insight}")
                content.append("")
            if "novelty_score" in discussion:
                content.append(f"### 新颖性评分")
                content.append(f"- **评分**: {discussion['novelty_score']}/10")
                content.append("")
        
        # Drafting stage
        if "drafting" in results:
            drafting = results["drafting"]
            content.append("## 4. 专利草稿")
            content.append("")
            content.append(f"### 专利标题")
            content.append(f"{drafting.get('title', 'N/A')}")
            content.append("")
            content.append(f"### 专利摘要")
            content.append(f"{drafting.get('abstract', 'N/A')}")
            content.append("")
            if "claims" in drafting:
                content.append("### 权利要求")
                for i, claim in enumerate(drafting["claims"], 1):
                    content.append(f"{i}. {claim}")
                content.append("")
            if "detailed_description" in drafting:
                content.append("### 详细描述")
                content.append(f"{drafting.get('detailed_description', 'N/A')}")
                content.append("")
        
        # Review stage
        if "review" in results:
            review = results["review"]
            content.append("## 5. 质量审查")
            content.append("")
            content.append(f"- **质量评分**: {review.get('quality_score', 'N/A')}")
            content.append(f"- **一致性评分**: {review.get('consistency_score', 'N/A')}")
            content.append("")
            if "feedback" in review:
                content.append("### 审查反馈")
                for feedback in review["feedback"]:
                    content.append(f"- {feedback}")
                content.append("")
            if "recommendations" in review:
                content.append(f"### 改进建议")
                for rec in review["recommendations"]:
                    content.append(f"- {rec}")
                content.append("")
        
        # Rewrite stage
        if "rewrite" in results:
            rewrite = results["rewrite"]
            content.append("## 6. 最终专利")
            content.append("")
            content.append(f"### 改进后的专利标题")
            content.append(f"{rewrite.get('title', 'N/A')}")
            content.append("### 改进后的专利摘要")
            content.append(f"{rewrite.get('abstract', 'N/A')}")
            content.append("")
            if "improvements" in rewrite:
                content.append("### 主要改进")
                for improvement in rewrite["improvements"]:
                    content.append(f"- {improvement}")
                content.append("")
            if "unified_content_summary" in rewrite:
                summary = rewrite["unified_content_summary"]
                content.append(f"### 统一内容总结")
                content.append(f"- **最终新颖性评分**: {summary.get('final_novelty_score', 'N/A')}/10")
                content.append("")
    
    return "\n".join(content)

async def execute_patent_workflow(workflow_id: str, topic: str, description: str, test_mode: bool):
    """Execute the complete patent workflow"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return
        
        workflow = app.state.workflows[workflow_id]
        workflow["status"] = "running"
        
        # Create workflow directory for stage results
        workflow_dir = await create_workflow_directory(workflow_id, topic)
        workflow["workflow_directory"] = workflow_dir
        
        # Execute each stage
        stages = ["planning", "search", "discussion", "drafting", "review", "rewrite"]
        
        for stage in stages:
            try:
                workflow["current_stage"] = stage
                workflow["stages"][stage]["status"] = "running"
                workflow["stages"][stage]["started_at"] = time.time()
                
                logger.info(f"🚀 Starting {stage} stage for workflow {workflow_id}")
                
                # Send real-time notification
                await manager.broadcast_workflow_update(workflow_id, {
                    "type": "stage_started",
                    "workflow_id": workflow_id,
                    "stage": stage,
                    "status": "running",
                    "timestamp": time.time(),
                    "message": f"Stage {stage} started"
                })
                
                # Execute stage based on test mode
                if test_mode:
                    # Test mode - use mock execution
                    await asyncio.sleep(2)  # Simulate processing time
                    stage_result = f"Mock {stage} completed for topic: {topic}"
                else:
                    # Real mode - call actual agent
                    stage_result = await execute_stage_with_agent(stage, topic, description, test_mode, workflow_id)
                
                # Check if stage execution failed
                if isinstance(stage_result, dict) and stage_result.get("error"):
                    logger.error(f"❌ {stage} stage execution failed: {stage_result}")
                    workflow["stages"][stage]["status"] = "failed"
                    workflow["stages"][stage]["error"] = stage_result.get("message", "Unknown error")
                    workflow["results"][stage] = stage_result
                    continue  # Skip to next stage instead of marking as completed
                
                workflow["stages"][stage]["status"] = "completed"
                workflow["stages"][stage]["completed_at"] = time.time()
                workflow["results"][stage] = stage_result
                
                # Immediately save stage result to file
                try:
                    stage_file_path = await save_stage_result(workflow_id, topic, stage, stage_result, test_mode)
                    workflow["stages"][stage]["file_path"] = stage_file_path
                    logger.info(f"💾 Stage {stage} result saved: {stage_file_path}")
                except Exception as save_error:
                    logger.error(f"⚠️ Failed to save {stage} stage result: {save_error}")
                    workflow["stages"][stage]["file_path"] = None
                
                logger.info(f"✅ {stage} stage completed for workflow {workflow_id}")
                
                # Send real-time notification
                await manager.broadcast_workflow_update(workflow_id, {
                    "type": "stage_completed",
                    "workflow_id": workflow_id,
                    "stage": stage,
                    "status": "completed",
                    "timestamp": time.time(),
                    "message": f"Stage {stage} completed",
                    "progress": f"{list(workflow['results'].keys()).index(stage) + 1}/{len(workflow['stages'])}"
                })
                
            except Exception as e:
                logger.error(f"❌ {stage} stage failed for workflow {workflow_id}: {e}")
                workflow["stages"][stage]["status"] = "failed"
                workflow["stages"][stage]["error"] = str(e)
                workflow["status"] = "failed"
                return
        
        # All stages completed successfully
        workflow["status"] = "completed"
        workflow["completed_at"] = time.time()
        
        # Update workflow metadata status
        try:
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_topic = safe_topic.replace(' ', '_')[:50]
            dir_name = f"{workflow_id}_{safe_topic}"
            dir_path = f"workflow_stages/{dir_name}"
            
            # Update metadata status
            metadata_file = f"{dir_path}/metadata.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                metadata["status"] = "completed"
                metadata["completed_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to update workflow metadata status: {e}")
        
        # Save final patent document to workflow directory
        try:
            patent_file_path = await save_patent_to_file(workflow_id, topic, workflow["results"])
            workflow["patent_file_path"] = patent_file_path
            workflow["download_url"] = f"/download/workflow/{workflow_id}"
            logger.info(f"💾 Final patent saved to workflow directory: {patent_file_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save final patent: {e}")
            workflow["patent_file_path"] = None
            workflow["download_url"] = None
        
        logger.info(f"🎉 Patent workflow {workflow_id} completed successfully")
        
        # Send workflow completion notification
        await manager.broadcast_workflow_update(workflow_id, {
            "type": "workflow_completed",
            "workflow_id": workflow_id,
            "status": "completed",
            "timestamp": time.time(),
            "message": "Patent workflow completed successfully!",
            "download_url": workflow.get("download_url"),
            "patent_file_path": workflow.get("patent_file_path")
        })
        
    except Exception as e:
        logger.error(f"❌ Patent workflow {workflow_id} failed: {e}")
        if hasattr(app.state, 'workflows') and workflow_id in app.state.workflows:
            app.state.workflows[workflow_id]["status"] = "failed"
            app.state.workflows[workflow_id]["error"] = str(e)

async def execute_stage_with_agent(stage: str, topic: str, description: str, test_mode: bool = False, workflow_id: str = None):
    """Execute a stage using the appropriate agent"""
    try:
        # Map stages to agent endpoints
        stage_to_agent = {
            "planning": "planner",
            "search": "searcher",
            "discussion": "discussion",
            "drafting": "writer",
            "review": "reviewer",
            "rewrite": "rewriter"
        }
        
        agent = stage_to_agent.get(stage)
        if not agent:
            return f"Unknown stage: {stage}"
        
        # Call agent endpoint
        async with httpx.AsyncClient() as client:
            # Provide all required fields for TaskRequest model
            # Ensure description is not None
            safe_description = description if description else f"Patent for topic: {topic}"
            task_payload = {
                "task_id": f"{workflow_id}_{stage}_{int(time.time())}",
                "workflow_id": workflow_id,
                "stage_name": stage,
                "topic": topic,
                "description": safe_description,
                "test_mode": test_mode,
                "previous_results": {},
                "context": {}
            }
            
            response = await client.post(
                f"http://localhost:8000/agents/{agent}/execute",
                json=task_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                # Return the agent execution result, not the API response
                agent_result = result.get("result", {})
                # Ensure test_mode is correctly propagated
                if isinstance(agent_result, dict) and "test_mode" in agent_result:
                    agent_result["test_mode"] = test_mode
                return agent_result
            else:
                logger.error(f"Agent {agent} returned status {response.status_code}: {response.text}")
                # Return a proper error structure instead of string
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": f"{stage} failed: {response.status_code}",
                    "details": response.text
                }
                
    except Exception as e:
        logger.error(f"Failed to execute {stage} stage: {e}")
        return {
            "error": True,
            "exception": str(e),
            "message": f"{stage} failed: {str(e)}"
        }

@app.post("/patent/generate", response_model=WorkflowResponse)
async def generate_patent(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Generate a patent using the patent workflow"""
    try:
        # Create workflow with patent-specific configuration
        workflow_id = str(uuid.uuid4())
        
        # Initialize workflow state
        workflow_state = {
            "workflow_id": workflow_id,
            "topic": request.topic,
            "description": request.description or f"Patent for topic: {request.topic}",
            "workflow_type": "patent",
            "test_mode": request.test_mode,
            "status": "created",
            "created_at": time.time(),
            "stages": {
                "planning": {"status": "pending", "started_at": None, "completed_at": None},
                "search": {"status": "pending", "started_at": None, "completed_at": None},
                "discussion": {"status": "pending", "started_at": None, "completed_at": None},
                "drafting": {"status": "pending", "started_at": None, "completed_at": None},
                "review": {"status": "pending", "started_at": None, "completed_at": None},
                "rewrite": {"status": "pending", "started_at": None, "completed_at": None}
            },
            "results": {},
            "current_stage": "planning"
        }
        
        # Store workflow in memory (in a real system, this would be in a database)
        if not hasattr(app.state, 'workflows'):
            app.state.workflows = {}
        app.state.workflows[workflow_id] = workflow_state
        
        # Start patent workflow execution in background
        background_tasks.add_task(execute_patent_workflow, workflow_id, request.topic, request.description, request.test_mode)
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="started",
            message=f"Patent generation started for topic: {request.topic} (test_mode: {request.test_mode})"
        )
    except Exception as e:
        logger.error(f"Failed to start patent generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start patent generation: {str(e)}")

@app.get("/patent/{workflow_id}/status")
async def get_patent_workflow_status(workflow_id: str):
    """Get status of a specific patent workflow"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "topic": workflow["topic"],
            "description": workflow["description"],
            "status": workflow["status"],
            "current_stage": workflow["current_stage"],
            "stages": workflow["stages"],
            "test_mode": workflow["test_mode"],
            "created_at": workflow["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get patent workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patent workflow status: {str(e)}")

@app.get("/patent/{workflow_id}/results")
async def get_patent_workflow_results(workflow_id: str):
    """Get results of a completed patent workflow"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        if workflow["status"] != "completed":
            return {
                "workflow_id": workflow_id,
                "status": workflow["status"],
                "message": "Workflow is not yet completed",
                "current_stage": workflow["current_stage"]
            }
        
        return {
            "workflow_id": workflow_id,
            "topic": workflow["topic"],
            "description": workflow["description"],
            "status": workflow["status"],
            "results": workflow["results"],
            "completed_at": workflow.get("completed_at"),
            "patent_file_path": workflow.get("patent_file_path"),
            "download_url": workflow.get("download_url")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get patent workflow results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patent workflow results: {str(e)}")

@app.post("/patent/{workflow_id}/restart")
async def restart_patent_workflow(workflow_id: str):
    """Restart a patent workflow"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        
        # Reset workflow state
        workflow["status"] = "restarted"
        workflow["current_stage"] = "planning"
        for stage in workflow["stages"]:
            workflow["stages"][stage] = {"status": "pending", "started_at": None, "completed_at": None}
        workflow["results"] = {}
        
        # Start workflow execution in background
        background_tasks = BackgroundTasks()
        background_tasks.add_task(execute_patent_workflow, workflow_id, workflow["topic"], workflow["description"], workflow["test_mode"])
        
        return {
            "workflow_id": workflow_id,
            "status": "restarted",
            "message": "Patent workflow restarted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart patent workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart patent workflow: {str(e)}")

@app.delete("/patent/{workflow_id}")
async def delete_patent_workflow(workflow_id: str):
    """Delete a patent workflow"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        del app.state.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": "deleted",
            "message": "Patent workflow deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete patent workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete patent workflow: {str(e)}")

@app.websocket("/ws/workflow/{workflow_id}")
async def websocket_workflow_updates(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time workflow updates"""
    try:
        await manager.connect(websocket, workflow_id)
        
        # Send initial connection confirmation
        await manager.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "workflow_id": workflow_id,
                "message": "Connected to workflow updates",
                "timestamp": time.time()
            }),
            websocket
        )
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for any message from client (ping/pong)
                data = await websocket.receive_text()
                if data == "ping":
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "pong",
                            "timestamp": time.time()
                        }),
                        websocket
                    )
            except WebSocketDisconnect:
                manager.disconnect(websocket, workflow_id)
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")
        manager.disconnect(websocket, workflow_id)

@app.get("/workflow/{workflow_id}/progress")
async def get_workflow_progress(workflow_id: str):
    """Get real-time workflow progress"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        
        # Calculate progress
        total_stages = len(workflow["stages"])
        completed_stages = len([s for s in workflow["stages"].values() if s["status"] == "completed"])
        current_stage = workflow.get("current_stage", "unknown")
        
        progress = {
            "workflow_id": workflow_id,
            "topic": workflow.get("topic"),
            "status": workflow.get("status"),
            "current_stage": current_stage,
            "progress": f"{completed_stages}/{total_stages}",
            "percentage": round((completed_stages / total_stages) * 100, 1),
            "completed_stages": completed_stages,
            "total_stages": total_stages,
            "started_at": workflow.get("created_at"),
            "estimated_completion": None
        }
        
        # Add estimated completion time for running workflows
        if workflow["status"] == "running":
            if completed_stages > 0:
                # Estimate based on average time per stage
                avg_time_per_stage = 2.0  # seconds in test mode
                remaining_stages = total_stages - completed_stages
                estimated_remaining = remaining_stages * avg_time_per_stage
                progress["estimated_completion"] = f"~{estimated_remaining:.1f} seconds"
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow progress: {str(e)}")

@app.get("/workflow/{workflow_id}/stages")
async def get_workflow_stages(workflow_id: str):
    """Get all stage files for a workflow"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        workflow_dir = workflow.get("workflow_directory")
        
        if not workflow_dir or not os.path.exists(workflow_dir):
            raise HTTPException(status_code=404, detail="Workflow directory not found")
        
        # Read stage index
        index_file = f"{workflow_dir}/stage_index.json"
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                stage_index = json.load(f)
        else:
            stage_index = {"stages": {}}
        
        # Read metadata
        metadata_file = f"{workflow_dir}/metadata.json"
        metadata = {}
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # List all files in directory
        files = []
        if os.path.exists(workflow_dir):
            for filename in os.listdir(workflow_dir):
                if filename.endswith('.md'):
                    file_path = f"{workflow_dir}/{filename}"
                    file_stat = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "size": file_stat.st_size,
                        "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
                    })
        
        return {
            "workflow_id": workflow_id,
            "topic": workflow.get("topic"),
            "workflow_directory": workflow_dir,
            "metadata": metadata,
            "stage_index": stage_index,
            "files": files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow stages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow stages: {str(e)}")

@app.get("/download/workflow/{workflow_id}")
async def download_workflow_directory(workflow_id: str):
    """Download entire workflow directory as a zip file"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        workflow_dir = workflow.get("workflow_directory")
        
        if not workflow_dir or not os.path.exists(workflow_dir):
            raise HTTPException(status_code=404, detail="Workflow directory not found")
        
        # Create zip file of the entire workflow directory
        import zipfile
        import tempfile
        
        # Create temporary zip file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through the workflow directory
                for root, dirs, files in os.walk(workflow_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate relative path for zip
                        arcname = os.path.relpath(file_path, workflow_dir)
                        zipf.write(file_path, arcname)
            
            # Return zip file for download
            return FileResponse(
                path=tmp_zip.name,
                filename=f"workflow_{workflow_id}.zip",
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename=workflow_{workflow_id}.zip"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download workflow directory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download workflow directory: {str(e)}")

@app.get("/download/patent/{workflow_id}")
async def download_patent_file(workflow_id: str):
    """Download final patent file for a completed workflow"""
    try:
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        if workflow["status"] != "completed":
            raise HTTPException(status_code=400, detail="Workflow is not yet completed")
        
        patent_file_path = workflow.get("patent_file_path")
        if not patent_file_path:
            raise HTTPException(status_code=404, detail="Patent file not found")
        
        # Check if file exists
        if not os.path.exists(patent_file_path):
            raise HTTPException(status_code=404, detail="Patent file not found on disk")
        
        # Return file for download
        try:
            return FileResponse(
                path=patent_file_path,
                filename=f"final_patent_{workflow_id}.md",
                media_type="text/markdown"
            )
        except Exception as file_error:
            logger.error(f"FileResponse error: {file_error}")
            # Fallback: return file content as text
            with open(patent_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return JSONResponse(
                content={"file_content": content, "filename": f"final_patent_{workflow_id}.md"},
                headers={"Content-Disposition": f"attachment; filename=final_patent_{workflow_id}.md"}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download patent file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download patent file: {str(e)}")

@app.get("/patents")
async def list_patent_workflows():
    """List all patent workflows"""
    try:
        if not hasattr(app.state, 'workflows'):
            return {"patent_workflows": [], "total": 0, "summary": {}}
        
        workflows = list(app.state.workflows.values())
        # Filter for patent workflows (workflow_type == "patent")
        patent_workflows = [w for w in workflows if w.get("workflow_type") == "patent"]
        
        # Add summary information for patents
        summary = {
            "total_patents": len(patent_workflows),
            "by_topic": {},
            "by_status": {},
            "by_test_mode": {"test": 0, "real": 0}
        }
        
        for workflow in patent_workflows:
            topic = workflow.get("topic", "Unknown")
            status = workflow.get("status", "Unknown")
            test_mode = workflow.get("test_mode", False)
            
            # Count by topic
            if topic not in summary["by_topic"]:
                summary["by_topic"][topic] = 0
            summary["by_topic"][topic] += 1
            
            # Count by status
            if status not in summary["by_status"]:
                summary["by_status"][status] = 0
            summary["by_status"][status] += 1
            
            # Count by test mode
            if test_mode:
                summary["by_test_mode"]["test"] += 1
            else:
                summary["by_test_mode"]["real"] += 1
        
        return {
            "patent_workflows": patent_workflows,
            "total": len(patent_workflows),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Failed to list patent workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list patent workflows: {str(e)}")

# ============================================================================
# COORDINATOR ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified Patent Agent System v2.0.0", 
        "status": "running",
        "test_mode": False,  # Root endpoint always shows real mode
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
        "test_mode": False,  # Health check always shows real mode
        "active_workflows": len(workflow_manager.workflows),
        "services": ["coordinator", "planner", "searcher", "discussion", "writer", "reviewer", "rewriter"],
        "timestamp": time.time()
    }

@app.get("/test-mode")
async def get_test_mode():
    """Get test mode configuration - DEPRECATED: Use workflow-specific test_mode instead"""
    return {
        "test_mode": TEST_MODE,
        "description": "DEPRECATED: Global test mode configuration. Use workflow-specific test_mode parameter instead.",
        "warning": "This global configuration is deprecated. Test mode is now controlled per workflow."
    }

@app.post("/test-mode")
async def set_test_mode(test_config: Dict[str, Any]):
    """Set test mode configuration - DEPRECATED: Use workflow-specific test_mode instead"""
    global TEST_MODE
    TEST_MODE.update(test_config)
    logger.warning(f"⚠️ DEPRECATED: Global test mode updated: {TEST_MODE}. Use workflow-specific test_mode instead.")
    return {
        "message": "DEPRECATED: Global test mode configuration updated. Use workflow-specific test_mode instead.",
        "test_mode": TEST_MODE,
        "warning": "This global configuration is deprecated. Test mode is now controlled per workflow."
    }

# Coordinator endpoints
@app.post("/coordinator/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Start a new patent workflow"""
    try:
        logger.info(f"🚀 Starting patent workflow in {'TEST' if request.test_mode else 'REAL'} mode")
        logger.info(f"📝 Topic: {request.topic}")
        logger.info(f"🔧 Test mode enabled: {request.test_mode}")
        
        # Only support patent workflows
        if request.workflow_type != "patent":
            raise HTTPException(
                status_code=400, 
                detail=f"Only patent workflows are supported. Received workflow_type: {request.workflow_type}"
            )
        
        # Create patent workflow
        workflow_id = str(uuid.uuid4())
        
        # Initialize patent workflow state
        workflow_state = {
            "workflow_id": workflow_id,
            "topic": request.topic,
            "description": request.description or f"Patent for topic: {request.topic}",
            "workflow_type": "patent",
            "test_mode": request.test_mode,
            "status": "created",
            "created_at": time.time(),
            "stages": {
                "planning": {"status": "pending", "started_at": None, "completed_at": None},
                "search": {"status": "pending", "started_at": None, "completed_at": None},
                "discussion": {"status": "pending", "started_at": None, "completed_at": None},
                "drafting": {"status": "pending", "started_at": None, "completed_at": None},
                "review": {"status": "pending", "started_at": None, "completed_at": None},
                "rewrite": {"status": "pending", "started_at": None, "completed_at": None}
            },
            "results": {},
            "current_stage": "planning"
        }
        
        # Store workflow in memory
        if not hasattr(app.state, 'workflows'):
            app.state.workflows = {}
        app.state.workflows[workflow_id] = workflow_state
        
        # Start patent workflow execution in background
        background_tasks.add_task(execute_patent_workflow, workflow_id, request.topic, request.description, request.test_mode)
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="started",
            message=f"Patent workflow started successfully for topic: {request.topic} (test_mode: {request.test_mode})"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start patent workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start patent workflow: {str(e)}")

@app.get("/coordinator/workflow/{workflow_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get patent workflow status and progress"""
    try:
        # Only support patent workflows
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        if workflow.get("workflow_type") != "patent":
            raise HTTPException(status_code=400, detail="Only patent workflows are supported")
        
        return {
            "workflow_id": workflow_id,
            "topic": workflow["topic"],
            "description": workflow["description"],
            "status": workflow["status"],
            "current_stage": workflow["current_stage"],
            "stages": workflow["stages"],
            "test_mode": workflow["test_mode"],
            "created_at": workflow["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get patent workflow status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patent workflow status: {str(e)}")

@app.get("/coordinator/workflow/{workflow_id}/results")
async def get_workflow_results(workflow_id: str):
    """Get patent workflow results"""
    try:
        # Check if this is a patent workflow
        if hasattr(app.state, 'workflows') and workflow_id in app.state.workflows:
            workflow = app.state.workflows[workflow_id]
            if workflow.get("workflow_type") == "patent":
                if workflow["status"] != "completed":
                    return {
                        "workflow_id": workflow_id,
                        "status": workflow["status"],
                        "message": "Workflow is not yet completed",
                        "current_stage": workflow["current_stage"]
                    }
                
                return {
                    "workflow_id": workflow_id,
                    "topic": workflow["topic"],
                    "description": workflow["description"],
                    "status": workflow["status"],
                    "results": workflow["results"],
                    "completed_at": workflow.get("completed_at"),
                    "test_mode": workflow["test_mode"],
                    "patent_file_path": workflow.get("patent_file_path"),
                    "download_url": workflow.get("download_url")
                }
        
        # Use regular workflow manager
        results = workflow_manager.get_workflow_results(workflow_id)
        return {"workflow_id": workflow_id, "results": results, "test_mode": workflow.get("test_mode", False)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Workflow not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@app.post("/coordinator/workflow/{workflow_id}/restart")
async def restart_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    """Restart a patent workflow"""
    try:
        # Only support patent workflows
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        if workflow.get("workflow_type") != "patent":
            raise HTTPException(status_code=400, detail="Only patent workflows are supported")
        
        # Reset workflow state
        workflow["status"] = "restarted"
        workflow["current_stage"] = "planning"
        for stage in workflow["stages"]:
            workflow["stages"][stage] = {"status": "pending", "started_at": None, "completed_at": None}
        workflow["results"] = {}
        
        # Start workflow execution in background
        background_tasks.add_task(execute_patent_workflow, workflow_id, workflow["topic"], workflow["description"], workflow["test_mode"])
        
        return {"workflow_id": workflow_id, "status": "restarted", "message": "Patent workflow restarted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restart patent workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to restart patent workflow: {str(e)}")

@app.get("/coordinator/workflows")
async def list_workflows():
    """List all patent workflows"""
    try:
        # Only support patent workflows
        patent_workflows = []
        if hasattr(app.state, 'workflows'):
            for workflow in app.state.workflows.values():
                if workflow.get("workflow_type") == "patent":
                    patent_workflows.append({
                        "workflow_id": workflow["workflow_id"],
                        "topic": workflow["topic"],
                        "description": workflow["description"],
                        "workflow_type": "patent",
                        "status": workflow["status"],
                        "current_stage": workflow["current_stage"],
                        "test_mode": workflow["test_mode"],
                        "created_at": workflow["created_at"]
                    })
        
        return {
            "workflows": patent_workflows, 
            "patent_workflows": patent_workflows,
            "total_workflows": len(patent_workflows),
            "test_mode": False  # List endpoint always shows real mode
        }
    except Exception as e:
        logger.error(f"Failed to list patent workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list patent workflows: {str(e)}")

@app.delete("/coordinator/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a patent workflow"""
    try:
        # Only support patent workflows
        if not hasattr(app.state, 'workflows') or workflow_id not in app.state.workflows:
            raise HTTPException(status_code=404, detail="Patent workflow not found")
        
        workflow = app.state.workflows[workflow_id]
        if workflow.get("workflow_type") != "patent":
            raise HTTPException(status_code=400, detail="Only patent workflows are supported")
        
        del app.state.workflows[workflow_id]
        return {"workflow_id": workflow_id, "status": "deleted", "message": "Patent workflow deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete patent workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete patent workflow: {str(e)}")

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
    test_mode: bool = False
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
        "test_mode": False,  # Health check always shows real mode
        "capabilities": ["patent_planning", "strategy_development", "risk_assessment", "timeline_planning"],
        "timestamp": time.time()
    }

@app.post("/agents/planner/execute", response_model=TaskResponse)
async def planner_execute(request: TaskRequest):
    """Execute planner agent task"""
    try:
        logger.info(f"📋 Planner Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {request.test_mode}")
        
        # DEBUG: 详细检查接收到的参数
        logger.info(f"🔍 DEBUG API: 接收到的request.test_mode = {request.test_mode}")
        logger.info(f"🔍 DEBUG API: type(request.test_mode) = {type(request.test_mode)}")
        logger.info(f"🔍 DEBUG API: request.test_mode == False = {request.test_mode == False}")
        logger.info(f"🔍 DEBUG API: request.test_mode == True = {request.test_mode == True}")
        
        result = await execute_planner_task(request)
        logger.info(f"🔍 DEBUG: execute_planner_task returned result with test_mode: {result.get('test_mode', 'NOT_FOUND')}")
        logger.info(f"🔍 DEBUG: request.test_mode: {request.test_mode}")
        logger.info(f"🔍 DEBUG: result type: {type(result)}")
        logger.info(f"🔍 DEBUG: result keys: {list(result.keys()) if isinstance(result, dict) else 'NOT_DICT'}")
        
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Patent planning completed successfully in {'TEST' if request.test_mode else 'REAL'} mode",
            test_mode=request.test_mode
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
        "test_mode": False,  # Health check always shows real mode
        "capabilities": ["prior_art_search", "patent_analysis", "competitive_research", "novelty_assessment"],
        "timestamp": time.time()
    }

@app.post("/agents/searcher/execute", response_model=TaskResponse)
async def searcher_execute(request: TaskRequest):
    """Execute searcher agent task"""
    try:
        logger.info(f"🔍 Searcher Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {request.test_mode}")
        
        result = await execute_searcher_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Prior art search completed successfully in {'TEST' if request.test_mode else 'REAL'} mode",
            test_mode=request.test_mode
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
        "test_mode": False,  # Health check always shows real mode
        "capabilities": ["innovation_discussion", "idea_generation", "technical_analysis"],
        "timestamp": time.time()
    }

@app.post("/agents/discussion/execute", response_model=TaskResponse)
async def discussion_execute(request: TaskRequest):
    """Execute discussion agent task"""
    try:
        logger.info(f"💬 Discussion Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {request.test_mode}")
        
        result = await execute_discussion_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Innovation discussion completed successfully in {'TEST' if request.test_mode else 'REAL'} mode",
            test_mode=request.test_mode
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
        "test_mode": False,  # Health check always shows real mode
        "capabilities": ["patent_drafting", "technical_writing", "claim_writing", "legal_compliance"],
        "timestamp": time.time()
    }

@app.post("/agents/writer/execute", response_model=TaskResponse)
async def writer_execute(request: TaskRequest):
    """Execute writer agent task"""
    try:
        logger.info(f"✍️ Writer Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {request.test_mode}")
        
        result = await execute_writer_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Patent drafting completed successfully in {'TEST' if request.test_mode else 'REAL'} mode",
            test_mode=request.test_mode
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
        "test_mode": False,  # Health check always shows real mode
        "capabilities": ["quality_review", "compliance_check", "feedback_generation"],
        "timestamp": time.time()
    }

@app.post("/agents/reviewer/execute", response_model=TaskResponse)
async def reviewer_execute(request: TaskRequest):
    """Execute reviewer agent task"""
    try:
        logger.info(f"🔍 Reviewer Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {request.test_mode}")
        
        result = await execute_reviewer_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Quality review completed successfully in {'TEST' if request.test_mode else 'REAL'} mode",
            test_mode=request.test_mode
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
        "test_mode": False,  # Health check always shows real mode
        "capabilities": ["patent_rewriting", "improvement_generation", "final_polish"],
        "timestamp": time.time()
    }

@app.post("/agents/rewriter/execute", response_model=TaskResponse)
async def rewriter_execute(request: TaskRequest):
    """Execute rewriter agent task"""
    try:
        logger.info(f"✏️ Rewriter Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {request.test_mode}")
        
        result = await execute_rewriter_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Patent rewriting completed successfully in {'TEST' if request.test_mode else 'REAL'} mode",
            test_mode=request.test_mode
        )
    except Exception as e:
        logger.error(f"❌ Rewriter Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# ============================================================================
# COMPRESSION AGENT ENDPOINTS
# ============================================================================

# Compression Agent
@app.get("/agents/compressor/health")
async def compressor_health():
    """Compression agent health check"""
    return {
        "status": "healthy",
        "service": "compression_agent",
        "test_mode": False,  # Health check always shows real mode
        "capabilities": ["context_compression", "content_summarization", "key_insight_extraction", "unified_content_preservation"],
        "timestamp": time.time()
    }

@app.post("/agents/compressor/execute", response_model=TaskResponse)
async def compressor_execute(request: TaskRequest):
    """Execute compression agent task"""
    try:
        logger.info(f"🗜️ Compression Agent received task: {request.task_id}")
        logger.info(f"🔧 Test mode: {request.test_mode}")
        
        result = await execute_compression_task(request)
        return TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result,
            message=f"Context compression completed successfully in {'TEST' if request.test_mode else 'REAL'} mode",
            test_mode=request.test_mode
        )
    except Exception as e:
        logger.error(f"❌ Compression Agent failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

# ============================================================================
# AGENT TASK EXECUTION FUNCTIONS
# ============================================================================

async def execute_planner_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute planner task using old system prompts with workflow isolation"""
    topic = request.topic
    description = request.description
    workflow_id = request.workflow_id
    context = request.context
    
    logger.info(f"🚀 Starting patent planning for workflow {workflow_id}: {topic}")
    logger.info(f"🔧 Test mode: {request.test_mode}")
    logger.info(f"🔒 Workflow isolation: {context.get('isolation_level', 'unknown')}")
    
    # DEBUG: 详细追踪test_mode
    logger.info(f"🔍 DEBUG STEP 1: request.test_mode = {request.test_mode}")
    logger.info(f"🔍 DEBUG STEP 1: type(request.test_mode) = {type(request.test_mode)}")
    logger.info(f"🔍 DEBUG STEP 1: request.test_mode == False = {request.test_mode == False}")
    logger.info(f"🔍 DEBUG STEP 1: request.test_mode == True = {request.test_mode == True}")
    
    # Validate workflow context
    if context.get("workflow_id") != workflow_id:
        logger.warning(f"⚠️ Workflow ID mismatch in context: expected {workflow_id}, got {context.get('workflow_id')}")
    
    # Add test mode delay
    if request.test_mode:
        await asyncio.sleep(0.5)  # Simulate processing time
        logger.info(f"⏱️ Test mode delay: 0.5s")
    
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
    
    # DEBUG: 在返回结果构建之前检查test_mode
    logger.info(f"🔍 DEBUG STEP 2: 准备构建返回结果")
    logger.info(f"🔍 DEBUG STEP 2: request.test_mode = {request.test_mode}")
    logger.info(f"🔍 DEBUG STEP 2: execution_time 计算: {0.5 if request.test_mode else 1.0}")
    logger.info(f"🔍 DEBUG STEP 2: mock_delay_applied 计算: {0.5 if request.test_mode else 0}")
    
    result_dict = {
        "workflow_id": workflow_id,  # Include workflow ID in result
        "strategy": final_strategy,
        "analysis": analysis,
        "recommendations": analysis.get("recommendations", []),
        "execution_time": 0.5 if request.test_mode else 1.0,
        "test_mode": request.test_mode,
        "mock_delay_applied": 0.5 if request.test_mode else 0,
        "isolation_timestamp": time.time()
    }
    
    # DEBUG: 检查构建后的结果
    logger.info(f"🔍 DEBUG STEP 3: 构建完成的结果")
    logger.info(f"🔍 DEBUG STEP 3: result_dict['test_mode'] = {result_dict['test_mode']}")
    logger.info(f"🔍 DEBUG STEP 3: result_dict keys = {list(result_dict.keys())}")
    
    return result_dict

async def execute_searcher_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute searcher task using old system prompts with workflow isolation"""
    topic = request.topic
    description = request.description
    workflow_id = request.workflow_id
    context = request.context
    
    logger.info(f"🚀 Starting prior art search for workflow {workflow_id}: {topic}")
    logger.info(f"🔧 Test mode: {request.test_mode}")
    logger.info(f"🔒 Workflow isolation: {context.get('isolation_level', 'unknown')}")
    
    # Validate workflow context
    if context.get("workflow_id") != workflow_id:
        logger.warning(f"⚠️ Workflow ID mismatch in context: expected {workflow_id}, got {context.get('workflow_id')}")
    
    # Add test mode delay
    if request.test_mode:
        await asyncio.sleep(0.5)  # Simulate processing time
        logger.info(f"⏱️ Test mode delay: 0.5s")
    
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
        "workflow_id": workflow_id,  # Include workflow ID in result
        "search_results": search_report,
        "patents_found": len(search_results),
        "novelty_score": novelty_assessment.get("novelty_score", 8.0),
        "risk_level": novelty_assessment.get("risk_level", "Low"),
        "recommendations": recommendations,
        "execution_time": 0.5 if request.test_mode else 1.0,
        "test_mode": request.test_mode,
        "mock_delay_applied": 0.5 if request.test_mode else 0,
        "isolation_timestamp": time.time()
    }

async def execute_discussion_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute discussion task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting innovation discussion for: {topic}")
    logger.info(f"🔧 Test mode: {request.test_mode}")
    
    # Add test mode delay
    if request.test_mode:
        await asyncio.sleep(0.5)  # Simulate processing time
        logger.info(f"⏱️ Test mode delay: 0.5s")
    
    # Extract core strategy from planning stage
    planning_strategy = previous_results.get("planning", {}).get("result", {}).get("strategy", {})
    search_results = previous_results.get("search", {}).get("result", {}).get("search_results", {})
    
    # Build on previous stages' insights
    core_innovation_areas = planning_strategy.get("key_innovation_areas", [])
    novelty_score = planning_strategy.get("novelty_score", 8.5)
    search_findings = search_results.get("results", [])
    
    logger.info(f"📋 Building on planning strategy: {core_innovation_areas}")
    logger.info(f"🔍 Incorporating search findings: {len(search_findings)} patents found")
    
    discussion_result = {
        "topic": topic,
        "core_strategy": planning_strategy,
        "search_context": search_results,
        "innovations": [
            f"Enhanced {core_innovation_areas[0] if core_innovation_areas else 'layered reasoning'} architecture",
            f"Improved {core_innovation_areas[1] if len(core_innovation_areas) > 1 else 'multi-parameter'} optimization",
            f"Advanced {core_innovation_areas[2] if len(core_innovation_areas) > 2 else 'context-aware'} processing"
        ],
        "technical_insights": [
            f"Novel approach to {topic.lower()} parameter inference",
            f"Unique {topic.lower()} system integration methodology",
            f"Innovative {topic.lower()} user intent modeling"
        ],
        "recommendations": [
            f"Focus on {core_innovation_areas[0] if core_innovation_areas else 'layered reasoning'} as key differentiator",
            f"Emphasize {core_innovation_areas[1] if len(core_innovation_areas) > 1 else 'adaptive parameter'} optimization",
            f"Highlight {core_innovation_areas[2] if len(core_innovation_areas) > 2 else 'context-aware'} capabilities"
        ],
        "novelty_score": novelty_score,
        "execution_time": 0.5 if request.test_mode else 1.0,
        "test_mode": request.test_mode,
        "mock_delay_applied": 0.5 if request.test_mode else 0
    }
    
    return discussion_result

async def execute_writer_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute writer task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting patent drafting for: {topic}")
    logger.info(f"🔧 Test mode: {request.test_mode}")
    
    # Add test mode delay
    if request.test_mode:
        await asyncio.sleep(0.5)  # Simulate processing time
        logger.info(f"⏱️ Test mode delay: 0.5s")
    
    # Check if compressed context is available (look for any compression result)
    compressed_context = None
    for key, value in previous_results.items():
        if key.startswith("compression_before_"):
            compressed_context = value.get("result", {}).get("compressed_context", {})
            if compressed_context:
                break
    
    # Initialize variables
    core_strategy = {}
    key_insights = []
    critical_findings = []
    unified_theme = topic
    search_results = {}
    discussion_insights = {}
    planning_strategy = {}  # Initialize planning_strategy
    
    if compressed_context:
        logger.info(f"🗜️ Using compressed context for drafting")
        # Use compressed context
        core_strategy = compressed_context.get("core_strategy", {})
        key_insights = compressed_context.get("key_insights", [])
        critical_findings = compressed_context.get("critical_findings", [])
        unified_theme = compressed_context.get("unified_theme", topic)
    else:
        logger.info(f"📋 Using full context for drafting")
        # Extract unified content from all previous stages
        planning_strategy = previous_results.get("planning", {}).get("result", {}).get("strategy", {})
        search_results = previous_results.get("search", {}).get("result", {}).get("search_results", {})
        discussion_insights = previous_results.get("discussion", {}).get("result", {})
        
        # Build unified patent content
        core_strategy = planning_strategy
        key_insights = []
        critical_findings = []
        unified_theme = topic
    
    # Build unified patent content
    core_innovation_areas = core_strategy.get("key_innovation_areas", [])
    novelty_score = core_strategy.get("novelty_score", 8.5)
    search_findings = search_results.get("results", []) if search_results else []
    discussion_innovations = key_insights
    
    logger.info(f"📋 Using unified strategy: {core_innovation_areas}")
    logger.info(f"🔍 Incorporating {len(search_findings)} search findings")
    logger.info(f"💡 Building on discussion insights: {discussion_innovations}")
    
    # Create claims based on unified strategy
    claims = []
    if core_innovation_areas:
        claims.append(f"A system for {core_innovation_areas[0].lower()} comprising...")
        if len(core_innovation_areas) > 1:
            claims.append(f"The system of claim 1, further comprising {core_innovation_areas[1].lower()}...")
        if len(core_innovation_areas) > 2:
            claims.append(f"A method for {core_innovation_areas[2].lower()} comprising...")
    else:
        claims = [
            "A system for intelligent parameter inference comprising...",
            "The system of claim 1, further comprising...",
            "A method for adaptive tool calling comprising..."
        ]
    
    patent_draft = {
        "title": f"Patent Application: {topic}",
        "abstract": f"An innovative system for {topic.lower()} that provides enhanced functionality and efficiency through {', '.join(core_innovation_areas[:2]) if core_innovation_areas else 'intelligent processing'}.",
        "claims": claims,
        "detailed_description": f"Detailed technical description of the {topic} system incorporating {', '.join(core_innovation_areas) if core_innovation_areas else 'advanced features'}...",
        "technical_diagrams": ["Figure 1: System Architecture", "Figure 2: Process Flow"],
        "unified_content": {
            "core_strategy": core_strategy,
            "search_context": search_results,
            "discussion_insights": discussion_insights,
            "novelty_score": novelty_score,
            "innovation_areas": core_innovation_areas
        },
        "execution_time": 0.5 if request.test_mode else 1.0,
        "test_mode": request.test_mode,
        "mock_delay_applied": 0.5 if request.test_mode else 0
    }
    
    return patent_draft

async def execute_reviewer_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute reviewer task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting quality review for: {topic}")
    logger.info(f"🔧 Test mode: {request.test_mode}")
    
    # Add test mode delay
    if request.test_mode:
        await asyncio.sleep(0.5)  # Simulate processing time
        logger.info(f"⏱️ Test mode delay: 0.5s")
    
    # Check if compressed context is available (look for any compression result)
    compressed_context = None
    for key, value in previous_results.items():
        if key.startswith("compression_before_"):
            compressed_context = value.get("result", {}).get("compressed_context", {})
            if compressed_context:
                break
    
    if compressed_context:
        logger.info(f"🗜️ Using compressed context for review")
        # Use compressed context
        core_strategy = compressed_context.get("core_strategy", {})
        key_insights = compressed_context.get("key_insights", [])
        critical_findings = compressed_context.get("critical_findings", [])
        unified_theme = compressed_context.get("unified_theme", topic)
        writer_draft = previous_results.get("drafting", {}).get("result", {})
    else:
        logger.info(f"📋 Using full context for review")
        # Extract unified content for review
        planning_strategy = previous_results.get("planning", {}).get("result", {}).get("strategy", {})
        search_results = previous_results.get("search", {}).get("result", {}).get("search_results", {})
        discussion_insights = previous_results.get("discussion", {}).get("result", {})
        writer_draft = previous_results.get("drafting", {}).get("result", {})
        
        # Build review context
        core_strategy = planning_strategy
        key_insights = []
        critical_findings = []
        unified_theme = topic
    
    # Review against unified strategy
    core_innovation_areas = core_strategy.get("key_innovation_areas", [])
    novelty_score = core_strategy.get("novelty_score", 8.5)
    search_findings = critical_findings
    
    logger.info(f"📋 Reviewing against unified strategy: {core_innovation_areas}")
    logger.info(f"🔍 Checking consistency with {len(search_findings)} search findings")
    
    # Assess consistency and quality
    consistency_score = 9.0 if core_innovation_areas else 7.0
    overall_quality = (novelty_score + consistency_score) / 2
    
    review_result = {
        "quality_score": overall_quality,
        "consistency_score": consistency_score,
        "compliance_check": {
            "legal_requirements": "Pass",
            "technical_accuracy": "Pass", 
            "clarity": "Pass",
            "unified_content_consistency": "Pass"
        },
        "feedback": [
            f"Excellent technical description aligned with {core_innovation_areas[0] if core_innovation_areas else 'core strategy'}",
            "Claims are well-structured and consistent with unified approach",
            f"Consider adding more examples for {core_innovation_areas[1] if len(core_innovation_areas) > 1 else 'key features'}"
        ],
        "recommendations": [
            "Proceed with filing - unified content is consistent",
            "Minor improvements suggested for enhanced clarity",
            "Overall quality is high and maintains topic consistency"
        ],
        "unified_content_review": {
            "strategy_alignment": "Strong",
            "innovation_consistency": "High",
            "topic_coherence": "Excellent",
            "search_integration": "Good"
        },
        "execution_time": 0.5 if request.test_mode else 1.0,
        "test_mode": request.test_mode,
        "mock_delay_applied": 0.5 if request.test_mode else 0
    }
    
    return review_result

async def execute_rewriter_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute rewriter task"""
    topic = request.topic
    previous_results = request.previous_results
    
    logger.info(f"🚀 Starting patent rewriting for: {topic}")
    logger.info(f"🔧 Test mode: {request.test_mode}")
    
    # Add test mode delay
    if request.test_mode:
        await asyncio.sleep(0.5)  # Simulate processing time
        logger.info(f"⏱️ Test mode delay: 0.5s")
    
    # Initialize variables
    core_strategy = {}
    key_insights = []
    critical_findings = []
    unified_theme = topic
    search_results = {}
    discussion_insights = {}
    planning_strategy = {}  # Initialize planning_strategy
    writer_draft = {}
    review_feedback = {}
    
    # Check if compressed context is available (look for any compression result)
    compressed_context = None
    for key, value in previous_results.items():
        if key.startswith("compression_before_"):
            compressed_context = value.get("result", {}).get("compressed_context", {})
            if compressed_context:
                break
    
    if compressed_context:
        logger.info(f"🗜️ Using compressed context for rewrite")
        # Use compressed context
        core_strategy = compressed_context.get("core_strategy", {})
        key_insights = compressed_context.get("key_insights", [])
        critical_findings = compressed_context.get("critical_findings", [])
        unified_theme = compressed_context.get("unified_theme", topic)
        writer_draft = previous_results.get("drafting", {}).get("result", {})
        review_feedback = previous_results.get("review", {}).get("result", {})
    else:
        logger.info(f"📋 Using full context for rewrite")
        # Extract all unified content for final polish
        planning_strategy = previous_results.get("planning", {}).get("result", {}).get("strategy", {})
        search_results = previous_results.get("search", {}).get("result", {}).get("search_results", {})
        discussion_insights = previous_results.get("discussion", {}).get("result", {})
        writer_draft = previous_results.get("drafting", {}).get("result", {})
        review_feedback = previous_results.get("review", {}).get("result", {})
        
        # Build rewrite context
        core_strategy = planning_strategy
        key_insights = []
        critical_findings = []
        unified_theme = topic
    
    # Build final unified content
    core_innovation_areas = core_strategy.get("key_innovation_areas", [])
    novelty_score = core_strategy.get("novelty_score", 8.5)
    search_findings = critical_findings
    review_recommendations = review_feedback.get("recommendations", []) if review_feedback else []
    
    logger.info(f"📋 Final polish using unified strategy: {core_innovation_areas}")
    logger.info(f"🔍 Incorporating review feedback: {len(review_recommendations)} recommendations")
    
    # Create improved claims based on unified strategy and feedback
    improved_claims = []
    if core_innovation_areas:
        improved_claims.append(f"An improved system for {core_innovation_areas[0].lower()} comprising...")
        if len(core_innovation_areas) > 1:
            improved_claims.append(f"The system of claim 1, further comprising enhanced {core_innovation_areas[1].lower()} features...")
        if len(core_innovation_areas) > 2:
            improved_claims.append(f"An optimized method for {core_innovation_areas[2].lower()} comprising...")
    else:
        improved_claims = [
            "An improved system for intelligent parameter inference comprising...",
            "The system of claim 1, further comprising enhanced features...",
            "An optimized method for adaptive tool calling comprising..."
        ]
    
    improved_draft = {
        "title": f"Improved Patent Application: {topic}",
        "abstract": f"An enhanced system for {topic.lower()} with improved functionality and efficiency through {', '.join(core_innovation_areas[:2]) if core_innovation_areas else 'advanced processing'}.",
        "claims": improved_claims,
        "detailed_description": f"Enhanced technical description of the {topic} system with improvements incorporating {', '.join(core_innovation_areas) if core_innovation_areas else 'advanced features'}...",
        "improvements": [
            f"Enhanced clarity in {core_innovation_areas[0].lower() if core_innovation_areas else 'core'} claims",
            f"Additional technical examples for {core_innovation_areas[1].lower() if len(core_innovation_areas) > 1 else 'key features'}",
            f"Improved abstract description aligned with unified strategy"
        ],
        "unified_content_summary": {
            "core_strategy": core_strategy,
            "search_integration": search_results,
            "discussion_insights": discussion_insights,
            "review_incorporation": review_feedback,
            "final_novelty_score": novelty_score,
            "innovation_areas": core_innovation_areas
        },
        "execution_time": 0.5 if request.test_mode else 1.0,
        "test_mode": request.test_mode,
        "mock_delay_applied": 0.5 if request.test_mode else 0
    }
    
    return improved_draft

# ============================================================================
# COMPRESSION TASK EXECUTION FUNCTION
# ============================================================================

async def execute_compression_task(request: TaskRequest) -> Dict[str, Any]:
    """Execute compression task to compress long context"""
    topic = request.topic
    previous_results = request.previous_results
    context = request.context
    
    logger.info(f"🚀 Starting context compression for: {topic}")
    logger.info(f"🔧 Test mode: {request.test_mode}")
    
    # Add test mode delay
    if request.test_mode:
        await asyncio.sleep(0.5)  # Simulate processing time
        logger.info(f"⏱️ Test mode delay: 0.5s")
    
    # Analyze what needs to be compressed
    compression_needs = analyze_compression_needs(previous_results, context)
    logger.info(f"📊 Compression analysis: {compression_needs}")
    
    # Compress context intelligently
    compressed_context = await compress_context_intelligently(previous_results, topic, compression_needs)
    
    # Create compression summary
    compression_summary = {
        "original_size": compression_needs.get("total_size", 0),
        "compressed_size": len(str(compressed_context)),
        "compression_ratio": calculate_compression_ratio(compression_needs.get("total_size", 0), len(str(compressed_context))),
        "key_elements_preserved": list(compressed_context.keys()),
        "compression_strategy": compression_needs.get("strategy", "selective")
    }
    
    compression_result = {
        "topic": topic,
        "compressed_context": compressed_context,
        "compression_summary": compression_summary,
        "preserved_elements": {
            "core_strategy": compressed_context.get("core_strategy", {}),
            "key_insights": compressed_context.get("key_insights", []),
            "critical_findings": compressed_context.get("critical_findings", []),
            "unified_theme": compressed_context.get("unified_theme", "")
        },
        "execution_time": 0.5 if request.test_mode else 1.0,
        "test_mode": request.test_mode,
        "mock_delay_applied": 0.5 if request.test_mode else 0
    }
    
    return compression_result

def analyze_compression_needs(previous_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze what needs to be compressed and how"""
    logger.info("📊 Analyzing compression needs...")
    
    # Calculate total context size
    total_size = len(str(previous_results)) + len(str(context))
    
    # Determine compression strategy
    if total_size > 10000:  # Large context
        strategy = "aggressive"
        compression_level = "high"
    elif total_size > 5000:  # Medium context
        strategy = "balanced"
        compression_level = "medium"
    else:  # Small context
        strategy = "selective"
        compression_level = "low"
    
    # Identify key elements to preserve
    key_elements = []
    if "planning" in previous_results:
        key_elements.append("core_strategy")
    if "search" in previous_results:
        key_elements.append("critical_findings")
    if "discussion" in previous_results:
        key_elements.append("key_insights")
    
    return {
        "total_size": total_size,
        "strategy": strategy,
        "compression_level": compression_level,
        "key_elements": key_elements,
        "stages_present": list(previous_results.keys())
    }

async def compress_context_intelligently(previous_results: Dict[str, Any], topic: str, compression_needs: Dict[str, Any]) -> Dict[str, Any]:
    """Intelligently compress context while preserving essential unified content"""
    logger.info(f"🗜️ Compressing context using {compression_needs['strategy']} strategy...")
    
    compressed_context = {
        "topic": topic,
        "unified_theme": extract_unified_theme(previous_results, topic),
        "core_strategy": extract_core_strategy(previous_results),
        "key_insights": extract_key_insights(previous_results),
        "critical_findings": extract_critical_findings(previous_results),
        "innovation_focus": extract_innovation_focus(previous_results),
        "quality_metrics": extract_quality_metrics(previous_results)
    }
    
    # Apply compression based on strategy
    if compression_needs["strategy"] == "aggressive":
        compressed_context = apply_aggressive_compression(compressed_context)
    elif compression_needs["strategy"] == "balanced":
        compressed_context = apply_balanced_compression(compressed_context)
    else:  # selective
        compressed_context = apply_selective_compression(compressed_context)
    
    logger.info(f"✅ Context compressed from {compression_needs['total_size']} to {len(str(compressed_context))} characters")
    
    return compressed_context

def extract_unified_theme(previous_results: Dict[str, Any], topic: str) -> str:
    """Extract the unified theme from all previous stages"""
    theme_elements = []
    
    # Extract from planning
    if "planning" in previous_results:
        strategy = previous_results["planning"].get("result", {}).get("strategy", {})
        innovation_areas = strategy.get("key_innovation_areas", [])
        if innovation_areas:
            theme_elements.extend(innovation_areas[:2])  # Top 2 innovation areas
    
    # Extract from discussion
    if "discussion" in previous_results:
        discussion = previous_results["discussion"].get("result", {})
        innovations = discussion.get("innovations", [])
        if innovations:
            theme_elements.append(innovations[0] if innovations else "")
    
    # Create unified theme
    if theme_elements:
        return f"{topic}: {', '.join(theme_elements[:3])}"  # Limit to 3 elements
    else:
        return topic

def extract_core_strategy(previous_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract core strategy from planning stage"""
    if "planning" in previous_results:
        strategy = previous_results["planning"].get("result", {}).get("strategy", {})
        return {
            "key_innovation_areas": strategy.get("key_innovation_areas", [])[:3],  # Top 3
            "novelty_score": strategy.get("novelty_score", 8.0),
            "patentability_assessment": strategy.get("patentability_assessment", "Strong"),
            "success_probability": strategy.get("success_probability", 0.75)
        }
    return {}

def extract_key_insights(previous_results: Dict[str, Any]) -> List[str]:
    """Extract key insights from all stages"""
    insights = []
    
    # From planning
    if "planning" in previous_results:
        strategy = previous_results["planning"].get("result", {}).get("strategy", {})
        insights.append(f"Novelty score: {strategy.get('novelty_score', 8.0)}")
        insights.append(f"Patentability: {strategy.get('patentability_assessment', 'Strong')}")
    
    # From search
    if "search" in previous_results:
        search_results = previous_results["search"].get("result", {}).get("search_results", {})
        patents_found = len(search_results.get("results", []))
        insights.append(f"Prior art found: {patents_found} patents")
    
    # From discussion
    if "discussion" in previous_results:
        discussion = previous_results["discussion"].get("result", {})
        innovations = discussion.get("innovations", [])
        if innovations:
            insights.append(f"Key innovation: {innovations[0]}")
    
    return insights[:5]  # Limit to 5 key insights

def extract_critical_findings(previous_results: Dict[str, Any]) -> List[str]:
    """Extract critical findings that must be preserved"""
    findings = []
    
    # From search
    if "search" in previous_results:
        search_results = previous_results["search"].get("result", {}).get("search_results", {})
        analysis = search_results.get("analysis", {})
        risk_level = analysis.get("risk_level", "Unknown")
        findings.append(f"Risk level: {risk_level}")
    
    # From review
    if "review" in previous_results:
        review = previous_results["review"].get("result", {})
        quality_score = review.get("quality_score", 0)
        findings.append(f"Quality score: {quality_score}")
    
    return findings

def extract_innovation_focus(previous_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract innovation focus areas"""
    focus = {}
    
    if "planning" in previous_results:
        strategy = previous_results["planning"].get("result", {}).get("strategy", {})
        innovation_areas = strategy.get("key_innovation_areas", [])
        if innovation_areas:
            focus["primary"] = innovation_areas[0]
            if len(innovation_areas) > 1:
                focus["secondary"] = innovation_areas[1]
    
    return focus

def extract_quality_metrics(previous_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract quality metrics from review stage"""
    if "review" in previous_results:
        review = previous_results["review"].get("result", {})
        return {
            "quality_score": review.get("quality_score", 0),
            "consistency_score": review.get("consistency_score", 0),
            "strategy_alignment": review.get("unified_content_review", {}).get("strategy_alignment", "Unknown")
        }
    return {}

def apply_aggressive_compression(compressed_context: Dict[str, Any]) -> Dict[str, Any]:
    """Apply aggressive compression - keep only essential elements"""
    logger.info("🗜️ Applying aggressive compression...")
    
    return {
        "topic": compressed_context.get("topic", ""),
        "unified_theme": compressed_context.get("unified_theme", ""),
        "core_strategy": {
            "key_innovation_areas": compressed_context.get("core_strategy", {}).get("key_innovation_areas", [])[:2],
            "novelty_score": compressed_context.get("core_strategy", {}).get("novelty_score", 8.0)
        },
        "key_insights": compressed_context.get("key_insights", [])[:3],
        "critical_findings": compressed_context.get("critical_findings", [])[:2]
    }

def apply_balanced_compression(compressed_context: Dict[str, Any]) -> Dict[str, Any]:
    """Apply balanced compression - keep important elements"""
    logger.info("🗜️ Applying balanced compression...")
    
    return {
        "topic": compressed_context.get("topic", ""),
        "unified_theme": compressed_context.get("unified_theme", ""),
        "core_strategy": compressed_context.get("core_strategy", {}),
        "key_insights": compressed_context.get("key_insights", [])[:4],
        "critical_findings": compressed_context.get("critical_findings", []),
        "innovation_focus": compressed_context.get("innovation_focus", {})
    }

def apply_selective_compression(compressed_context: Dict[str, Any]) -> Dict[str, Any]:
    """Apply selective compression - keep most elements"""
    logger.info("🗜️ Applying selective compression...")
    
    return compressed_context

def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """Calculate compression ratio"""
    if original_size == 0:
        return 0.0
    return round((1 - compressed_size / original_size) * 100, 2)

# ============================================================================
# HELPER FUNCTIONS (from old system)
# ============================================================================

async def analyze_patent_topic(topic: str, description: str) -> Dict[str, Any]:
    """Analyze patent topic using GLM API or fallback to mock"""
    logger.info(f"🔍 Analyzing patent topic: {topic}")
    
    if GLM_AVAILABLE:
        try:
            logger.info("🚀 使用GLM API进行专利主题分析")
            glm_client = get_glm_client()
            result = glm_client.analyze_patent_topic(topic, description)
            logger.info("✅ GLM API调用成功")
            return result
        except Exception as e:
            logger.error(f"❌ GLM API调用失败: {e}")
            logger.info("🔄 回退到mock数据")
    
    # Mock fallback
    logger.info("📝 使用mock数据进行专利主题分析")
    return {
        "novelty_score": 8.5,
        "inventive_step_score": 7.8,
        "industrial_applicability": True,
        "prior_art_analysis": [],
        "claim_analysis": {},
        "technical_merit": {},
        "commercial_potential": "中等到高",
        "patentability_assessment": "强",
        "recommendations": [
            "提高权利要求的具体性",
            "添加更多技术细节",
            "考虑规避设计策略"
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
    """Conduct comprehensive prior art search using GLM API or fallback to mock"""
    logger.info(f"🔍 Conducting prior art search for: {topic}")
    
    if GLM_AVAILABLE:
        try:
            logger.info("🚀 使用GLM API进行现有技术检索")
            glm_client = get_glm_client()
            result = glm_client.search_prior_art(topic, keywords)
            logger.info("✅ GLM API调用成功")
            return result
        except Exception as e:
            logger.error(f"❌ GLM API调用失败: {e}")
            logger.info("🔄 回退到mock数据")
    
    # Mock fallback
    logger.info("📝 使用mock数据进行现有技术检索")
    return [
        {
            "patent_id": "US1234567",
            "title": "智能参数推断系统",
            "abstract": "基于上下文和用户意图自动推断工具调用参数的系统",
            "filing_date": "2022-01-15",
            "publication_date": "2023-07-20",
            "assignee": "科技公司",
            "relevance_score": 0.85,
            "similarity_analysis": {
                "concept_overlap": "高",
                "technical_similarity": "中等",
                "implementation_differences": "显著"
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
    print("🔧 Test mode: DEPRECATED - Now using workflow-specific test_mode")
    print("⏱️ Test delay: Configurable per workflow")
    print("📡 Single service will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🤖 All agents available at:")
    print("   - Coordinator: /coordinator/* (Patent workflows only)")
    print("   - Planner: /agents/planner/*")
    print("   - Searcher: /agents/searcher/*")
    print("   - Discussion: /agents/discussion/*")
    print("   - Writer: /agents/writer/*")
    print("   - Reviewer: /agents/reviewer/*")
    print("   - Rewriter: /agents/rewriter/*")
    print("📋 Coordinator API endpoints (Patent workflows only):")
    print("   - POST /coordinator/workflow/start - Start patent workflow")
    print("   - GET /coordinator/workflow/{workflow_id}/status - Get patent workflow status")
    print("   - GET /coordinator/workflow/{workflow_id}/results - Get patent workflow results")
    print("   - GET /workflow/{workflow_id}/progress - Get real-time workflow progress")
    print("   - GET /workflow/{workflow_id}/stages - Get workflow stage files")
    print("   - WS /ws/workflow/{workflow_id} - Real-time workflow updates (WebSocket)")
    print("   - GET /download/workflow/{workflow_id} - Download entire workflow directory (ZIP)")
    print("   - GET /download/patent/{workflow_id} - Download final patent file only")
    print("   - POST /coordinator/workflow/{workflow_id}/restart - Restart patent workflow")
    print("   - DELETE /coordinator/workflow/{workflow_id} - Delete patent workflow")
    print("   - GET /coordinator/workflows - List all patent workflows")
    print("🔧 Test mode endpoints:")
    print("   - GET /test-mode - Check test mode status")
    print("   - POST /test-mode - Update test mode settings")
    uvicorn.run(app, host="0.0.0.0", port=8000)