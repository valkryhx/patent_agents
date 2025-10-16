# 多智能体专利撰写系统 - 完整API文档

## 📖 概述

本文档提供了多智能体专利撰写系统的完整API文档，包括所有公共接口、函数、组件和使用示例。该系统是一个基于多智能体架构的专利撰写平台，通过协调器统一管理多个专业智能体，实现从专利主题到最终专利文档的完整工作流程。

## 🏗️ 系统架构

### 核心组件
- **统一服务 (Unified Service)**: 单端口提供所有服务接口
- **工作流管理器 (Workflow Manager)**: 管理专利撰写流程状态
- **智能体系统 (Agent System)**: 6个专业智能体协同工作
- **LLM服务管理**: 统一的OpenAI Client管理，支持GLM-4.5-flash回退
- **消息总线 (Message Bus)**: 智能体间通信机制

### 智能体分工
1. **规划智能体 (Planner)**: 分析专利主题，制定撰写计划
2. **搜索智能体 (Searcher)**: 3轮迭代式检索（DuckDuckGo + GLM分析）
3. **讨论智能体 (Discussion)**: 分析技术方案，确定创新点
4. **撰写智能体 (Writer)**: 生成专利文档初稿
5. **审查智能体 (Reviewer)**: 审查文档质量和合规性
6. **重写智能体 (Rewriter)**: 根据审查意见优化文档

---

## 🚀 主要API接口

### 1. 统一服务接口 (Unified Service)

#### 基础信息
- **服务地址**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`
- **健康检查**: `http://localhost:8000/health`

#### 1.1 工作流管理接口

##### 启动专利工作流
```http
POST /coordinator/workflow/start
Content-Type: application/json

{
  "topic": "基于量子计算的机器学习算法优化系统",
  "description": "基于多智能体系统的参数传递和调用机制",
  "workflow_type": "patent",
  "test_mode": true
}
```

**响应示例**:
```json
{
  "workflow_id": "2219e3da-6cdb-41f6-86ba-06e01b525331",
  "status": "started",
  "message": "Patent workflow started successfully for topic: 基于量子计算的机器学习算法优化系统"
}
```

##### 查询工作流状态
```http
GET /coordinator/workflow/{workflow_id}/status
```

**响应示例**:
```json
{
  "workflow_id": "uuid-string",
  "topic": "基于量子计算的机器学习算法优化系统",
  "status": "running",
  "current_stage": "planning",
  "stages": {
    "planning": {"status": "completed", "started_at": 1234567890, "completed_at": 1234567891},
    "search": {"status": "running", "started_at": 1234567892, "completed_at": null},
    "discussion": {"status": "pending", "started_at": null, "completed_at": null},
    "drafting": {"status": "pending", "started_at": null, "completed_at": null},
    "review": {"status": "pending", "started_at": null, "completed_at": null},
    "rewrite": {"status": "pending", "started_at": null, "completed_at": null}
  },
  "test_mode": true,
  "created_at": 1234567890
}
```

##### 获取工作流结果
```http
GET /coordinator/workflow/{workflow_id}/results
```

**响应示例**:
```json
{
  "workflow_id": "uuid-string",
  "topic": "基于量子计算的机器学习算法优化系统",
  "status": "completed",
  "results": {
    "planning": "专利撰写计划已制定完成...",
    "search": "相关技术检索完成...",
    "discussion": "技术方案讨论完成...",
    "drafting": "专利文档初稿已生成...",
    "review": "文档审查完成...",
    "rewrite": "文档重写完成..."
  },
  "download_url": "/download/workflow/{workflow_id}",
  "patent_file_path": "workflow_stages/{workflow_id}_{topic}/final_patent_{timestamp}.md"
}
```

##### 重启工作流
```http
POST /coordinator/workflow/{workflow_id}/restart
```

##### 删除工作流
```http
DELETE /coordinator/workflow/{workflow_id}
```

##### 列出所有工作流
```http
GET /coordinator/workflows
```

#### 1.2 实时监控接口

##### WebSocket实时通知
```javascript
const workflowId = "2219e3da-6cdb-41f6-86ba-06e01b525331";
const ws = new WebSocket(`ws://localhost:8000/ws/workflow/${workflowId}`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(`[${data.type}] ${data.message}`);
    
    if (data.type === 'workflow_completed') {
        console.log("🎉 工作流完成！可以下载结果了");
        downloadWorkflowResults(workflowId);
    }
};
```

**通知类型**:
- `connection_established`: 连接建立确认
- `stage_started`: 阶段开始通知
- `stage_completed`: 阶段完成通知（包含进度）
- `workflow_completed`: 工作流完成通知（包含下载链接）

##### 进度查询接口
```http
GET /workflow/{workflow_id}/progress
```

**响应示例**:
```json
{
  "workflow_id": "uuid-string",
  "topic": "基于量子计算的机器学习算法优化系统",
  "status": "running",
  "current_stage": "drafting",
  "progress": "3/6",
  "percentage": 50.0,
  "completed_stages": 3,
  "total_stages": 6,
  "started_at": 1755456920.9572496,
  "estimated_completion": "~6.0 seconds"
}
```

#### 1.3 文件下载接口

##### 下载整个工作流目录
```http
GET /download/workflow/{workflow_id}
```

**下载内容**:
```
workflow_{workflow_id}.zip
├── metadata.json              # 工作流基本信息
├── workflow_metadata.json     # 文件追踪元数据
├── stage_index.json           # 阶段文件索引
├── planning_{timestamp}.md    # 规划阶段结果
├── search_{timestamp}.md      # 搜索阶段结果
├── discussion_{timestamp}.md  # 讨论阶段结果
├── drafting_{timestamp}.md    # 草稿阶段结果
├── review_{timestamp}.md      # 审查阶段结果
├── rewrite_{timestamp}.md     # 重写阶段结果
├── final_patent_{timestamp}.md # 最终专利文档
└── merged_patent_{workflow_id}_{timestamp}.md # 合并后的完整专利文档
```

##### 合并工作流章节
```http
POST /workflow/{workflow_id}/merge
```

**合并章节顺序**:
1. **规划阶段 (Planning)**: 专利主题分析和撰写策略
2. **搜索阶段 (Search)**: 相关技术检索和文献分析
3. **讨论阶段 (Discussion)**: 技术方案讨论和创新点确定
4. **撰写阶段 (Drafting)**: 专利文档初稿生成
5. **审查阶段 (Review)**: 文档质量审查和合规性检查
6. **重写阶段 (Rewrite)**: 根据审查意见优化文档

##### 仅下载最终专利文档
```http
GET /download/patent/{workflow_id}
```

#### 1.4 测试模式管理

##### 查询测试模式状态
```http
GET /test-mode
```

##### 更新测试模式设置
```http
POST /test-mode
Content-Type: application/json

{
  "enabled": true
}
```

---

## 🤖 智能体系统API

### 2. 基础智能体类 (BaseAgent)

#### 2.1 核心方法

##### 启动智能体
```python
async def start(self) -> None
```
启动智能体，注册到消息总线并开始消息处理循环。

##### 停止智能体
```python
async def stop(self) -> None
```
停止智能体，取消消息处理任务并从消息总线注销。

##### 执行任务
```python
async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult
```
执行具体任务，由子类实现。

##### 获取状态
```python
async def get_status(self) -> Dict[str, Any]
```
获取智能体当前状态信息。

**返回示例**:
```json
{
  "name": "planner_agent",
  "status": "idle",
  "capabilities": ["patent_planning", "strategy_development"],
  "performance_metrics": {
    "tasks_completed": 5,
    "tasks_failed": 0,
    "average_execution_time": 2.3,
    "total_execution_time": 11.5
  },
  "task_history_length": 5,
  "test_mode": false,
  "current_workflow_id": "uuid-string",
  "has_context": true
}
```

##### 发送消息
```python
async def send_message(self, recipient: str, message_type: MessageType, 
                      content: Dict[str, Any], priority: int = 5) -> None
```
向其他智能体发送消息。

#### 2.2 数据模型

##### TaskResult
```python
@dataclass
class TaskResult:
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
```

### 3. 协调器智能体 (CoordinatorAgent)

#### 3.1 核心功能

##### 启动专利工作流
```python
async def _start_patent_workflow(self, task_data: Dict[str, Any]) -> TaskResult
```
创建并启动新的专利开发工作流。

**参数**:
- `topic`: 专利主题
- `description`: 专利描述
- `workflow_type`: 工作流类型（默认"patent"）
- `test_mode`: 是否启用测试模式

##### 执行工作流阶段
```python
async def _execute_workflow_stage(self, workflow_id: str, stage_index: int) -> None
```
执行特定的工作流阶段。

##### 处理阶段完成
```python
async def _handle_stage_completion(self, workflow_id: str, stage_index: int, result: Dict[str, Any]) -> None
```
处理工作流阶段完成事件。

##### 获取工作流状态
```python
async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]
```
获取详细的工作流状态信息。

##### 获取所有智能体状态
```python
async def get_all_agents_status(self) -> TaskResult
```
获取系统中所有智能体的状态。

#### 3.2 数据模型

##### PatentWorkflow
```python
@dataclass
class PatentWorkflow:
    workflow_id: str
    topic: str
    description: str
    stages: List[WorkflowStage]
    current_stage: int
    overall_status: str
    start_time: float
    estimated_completion: Optional[float] = None
    results: Dict[str, Any] = None
```

##### WorkflowStage
```python
@dataclass
class WorkflowStage:
    stage_name: str
    agent_name: str
    status: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

### 4. 规划智能体 (PlannerAgent)

#### 4.1 核心功能

##### 专利规划
```python
async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult
```
执行专利规划任务，分析专利主题并制定开发策略。

**任务类型**: `patent_planning`

**输入参数**:
- `topic`: 专利主题
- `description`: 专利描述
- `context`: 上下文数据

**输出结果**:
```json
{
  "strategy": {
    "topic": "专利主题",
    "description": "专利描述",
    "novelty_score": 8.5,
    "inventive_step_score": 7.8,
    "patentability_assessment": "Strong",
    "development_phases": [...],
    "key_innovation_areas": [...],
    "competitive_analysis": {...},
    "risk_assessment": {...},
    "timeline_estimate": "3-6 months",
    "resource_requirements": {...},
    "success_probability": 0.75
  },
  "analysis": {
    "novelty_score": 8.5,
    "inventive_step_score": 7.8,
    "industrial_applicability": true,
    "prior_art_analysis": [],
    "claim_analysis": {},
    "technical_merit": {},
    "commercial_potential": "Medium to High",
    "patentability_assessment": "Strong",
    "recommendations": [...]
  }
}
```

#### 4.2 数据模型

##### PatentStrategy
```python
@dataclass
class PatentStrategy:
    topic: str
    description: str
    novelty_score: float
    inventive_step_score: float
    patentability_assessment: str
    development_phases: List[Dict[str, Any]]
    key_innovation_areas: List[str]
    competitive_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timeline_estimate: str
    resource_requirements: Dict[str, Any]
    success_probability: float
```

### 5. 其他智能体

#### 5.1 搜索智能体 (SearcherAgent)
- **功能**: 执行3轮迭代式检索（DuckDuckGo + GLM分析）
- **任务类型**: `prior_art_search`
- **特点**: 智能关键词优化，多轮检索提升质量

#### 5.2 讨论智能体 (DiscusserAgent)
- **功能**: 分析技术方案，确定创新点
- **任务类型**: `innovation_discussion`
- **特点**: 深度技术分析，创新点识别

#### 5.3 撰写智能体 (WriterAgent)
- **功能**: 生成专利文档初稿
- **任务类型**: `patent_drafting`
- **特点**: 分章节生成，结构化输出

#### 5.4 审查智能体 (ReviewerAgent)
- **功能**: 审查文档质量和合规性
- **任务类型**: `patent_review`
- **特点**: 质量评估，合规性检查

#### 5.5 重写智能体 (RewriterAgent)
- **功能**: 根据审查意见优化文档
- **任务类型**: `patent_rewrite`
- **特点**: 迭代优化，质量提升

---

## 📊 数据模型

### 6. 工作流相关模型

#### 6.1 WorkflowRequest
```python
class WorkflowRequest(BaseModel):
    topic: str = Field(..., description="Patent topic")
    description: Optional[str] = Field(default=None, description="Patent description")
    workflow_type: str = Field(default="enhanced", description="Workflow type")
    test_mode: bool = Field(default=False, description="Enable test mode")
```

#### 6.2 WorkflowResponse
```python
class WorkflowResponse(BaseModel):
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
```

#### 6.3 WorkflowStatus
```python
class WorkflowStatus(BaseModel):
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
```

#### 6.4 StageInfo
```python
class StageInfo(BaseModel):
    name: str = Field(..., description="Stage name")
    status: StageStatusEnum = Field(default=StageStatusEnum.PENDING, description="Stage status")
    start_time: Optional[float] = Field(default=None, description="Stage start time")
    end_time: Optional[float] = Field(default=None, description="Stage end time")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Stage result")
    error: Optional[str] = Field(default=None, description="Stage error message")
```

#### 6.5 WorkflowState
```python
class WorkflowState(BaseModel):
    workflow_id: str = Field(..., description="Unique workflow ID")
    topic: str = Field(..., description="Patent topic")
    description: str = Field(..., description="Patent description")
    workflow_type: str = Field(default="enhanced", description="Workflow type")
    test_mode: bool = Field(default=False, description="Test mode enabled")
    status: WorkflowStatusEnum = Field(default=WorkflowStatusEnum.PENDING, description="Workflow status")
    current_stage: int = Field(default=0, description="Current stage index")
    stages: List[str] = Field(default=["planning", "search", "discussion", "drafting", "review", "rewrite"], description="Stage names")
    stage_results: Dict[str, Any] = Field(default_factory=dict, description="Stage results")
    stage_statuses: Dict[str, StageStatusEnum] = Field(default_factory=dict, description="Stage statuses")
    stage_times: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Stage timing")
    errors: Dict[str, str] = Field(default_factory=dict, description="Stage errors")
    created_at: float = Field(default_factory=time.time, description="Creation timestamp")
    updated_at: float = Field(default_factory=time.time, description="Last update timestamp")
```

### 7. 枚举类型

#### 7.1 WorkflowStatusEnum
```python
class WorkflowStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

#### 7.2 StageStatusEnum
```python
class StageStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 🔧 LLM客户端接口

### 8. OpenAI客户端 (OpenAIClient)

#### 8.1 核心功能

##### 分析专利主题
```python
async def analyze_patent_topic(self, topic: str, description: str) -> PatentAnalysis
```
分析专利主题的可专利性。

**参数**:
- `topic`: 专利主题
- `description`: 专利描述

**返回**: `PatentAnalysis` 对象

##### 搜索现有技术
```python
async def search_prior_art(self, topic: str, keywords: List[str], max_results: int = 20) -> List[SearchResult]
```
搜索相关现有技术。

**参数**:
- `topic`: 专利主题
- `keywords`: 搜索关键词列表
- `max_results`: 最大结果数量

**返回**: `SearchResult` 对象列表

##### 生成专利草稿
```python
async def generate_patent_draft(self, topic: str, description: str, analysis: PatentAnalysis) -> PatentDraft
```
生成完整的专利草稿。

**参数**:
- `topic`: 专利主题
- `description`: 专利描述
- `analysis`: 专利分析结果

**返回**: `PatentDraft` 对象

##### 审查专利草稿
```python
async def review_patent_draft(self, draft: PatentDraft, analysis: PatentAnalysis) -> Dict[str, Any]
```
审查专利草稿并提供反馈。

**参数**:
- `draft`: 专利草稿
- `analysis`: 专利分析结果

**返回**: 审查反馈字典

##### 优化专利权利要求
```python
async def optimize_patent_claims(self, claims: List[str], feedback: Dict[str, Any]) -> List[str]
```
根据反馈优化专利权利要求。

**参数**:
- `claims`: 原始权利要求列表
- `feedback`: 审查反馈

**返回**: 优化后的权利要求列表

##### 生成技术图表
```python
async def generate_technical_diagrams(self, topic: str, description: str) -> List[str]
```
生成技术图表描述。

**参数**:
- `topic`: 专利主题
- `description`: 专利描述

**返回**: 技术图表描述列表

#### 8.2 回退机制

OpenAI客户端支持自动回退到GLM-4.5-flash服务：

- **主要服务**: OpenAI GPT-5（需要API密钥）
- **回退服务**: GLM-4.5-flash（免费，需要API密钥）
- **并发限制**: 最大并发数1，避免429错误
- **重试机制**: 429错误自动等待30秒后重试

---

## 🛠️ 工作流管理器

### 9. WorkflowManager

#### 9.1 核心功能

##### 创建工作流
```python
def create_workflow(self, topic: str, description: str, workflow_type: str = "enhanced", test_mode: bool = False) -> str
```
创建新的工作流实例。

**参数**:
- `topic`: 专利主题
- `description`: 专利描述
- `workflow_type`: 工作流类型
- `test_mode`: 是否启用测试模式

**返回**: 工作流ID

##### 执行工作流
```python
async def execute_workflow_with_agents(self, workflow_id: str) -> None
```
通过智能体服务执行工作流。

**参数**:
- `workflow_id`: 工作流ID

##### 获取工作流状态
```python
def get_workflow_status(self, workflow_id: str) -> WorkflowStatus
```
获取工作流状态信息。

**参数**:
- `workflow_id`: 工作流ID

**返回**: `WorkflowStatus` 对象

##### 获取工作流结果
```python
def get_workflow_results(self, workflow_id: str) -> Dict[str, Any]
```
获取工作流执行结果。

**参数**:
- `workflow_id`: 工作流ID

**返回**: 结果字典

##### 列出所有工作流
```python
def list_workflows(self) -> List[Dict[str, Any]]
```
列出所有工作流。

**返回**: 工作流列表

##### 重置工作流
```python
def reset_workflow(self, workflow_id: str) -> None
```
重置工作流到初始状态。

**参数**:
- `workflow_id`: 工作流ID

##### 删除工作流
```python
def delete_workflow(self, workflow_id: str) -> None
```
删除工作流。

**参数**:
- `workflow_id`: 工作流ID

#### 9.2 智能体服务配置

```python
AGENT_SERVICES = {
    "planning": "http://localhost:8000/agents/planner",
    "search": "http://localhost:8000/agents/searcher", 
    "discussion": "http://localhost:8000/agents/discussion",
    "drafting": "http://localhost:8000/agents/writer",
    "review": "http://localhost:8000/agents/reviewer",
    "rewrite": "http://localhost:8000/agents/rewriter",
    "compressor": "http://localhost:8000/agents/compressor"
}
```

---

## 📝 使用示例

### 10. 完整工作流示例

#### 10.1 启动专利工作流

```python
import httpx
import asyncio

async def start_patent_workflow():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/coordinator/workflow/start",
            json={
                "topic": "基于量子计算的机器学习算法优化系统",
                "description": "一种利用量子计算特性优化机器学习算法性能的创新方法",
                "workflow_type": "patent",
                "test_mode": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            workflow_id = result["workflow_id"]
            print(f"工作流启动成功: {workflow_id}")
            return workflow_id
        else:
            print(f"工作流启动失败: {response.text}")
            return None

# 运行示例
workflow_id = asyncio.run(start_patent_workflow())
```

#### 10.2 监控工作流进度

```python
async def monitor_workflow_progress(workflow_id):
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(
                f"http://localhost:8000/workflow/{workflow_id}/progress"
            )
            
            if response.status_code == 200:
                progress = response.json()
                print(f"进度: {progress['progress']} ({progress['percentage']:.1f}%)")
                print(f"当前阶段: {progress['current_stage']}")
                
                if progress['status'] == 'completed':
                    print("工作流完成！")
                    break
                elif progress['status'] == 'failed':
                    print("工作流失败！")
                    break
                    
            await asyncio.sleep(5)  # 每5秒检查一次

# 运行监控
asyncio.run(monitor_workflow_progress(workflow_id))
```

#### 10.3 下载工作流结果

```python
async def download_workflow_results(workflow_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/download/workflow/{workflow_id}"
        )
        
        if response.status_code == 200:
            with open(f"workflow_{workflow_id}.zip", "wb") as f:
                f.write(response.content)
            print(f"工作流结果已下载: workflow_{workflow_id}.zip")
        else:
            print(f"下载失败: {response.text}")

# 运行下载
asyncio.run(download_workflow_results(workflow_id))
```

### 11. WebSocket实时监控示例

```javascript
// 连接WebSocket获取实时更新
const workflowId = "your-workflow-id";
const ws = new WebSocket(`ws://localhost:8000/ws/workflow/${workflowId}`);

ws.onopen = function() {
    console.log("WebSocket连接已建立");
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'connection_established':
            console.log("✅ 已连接到工作流更新");
            break;
        case 'stage_started':
            console.log(`🚀 ${data.stage} 阶段开始`);
            break;
        case 'stage_completed':
            console.log(`✅ ${data.stage} 阶段完成 (${data.progress})`);
            break;
        case 'workflow_completed':
            console.log(`🎉 工作流完成！下载链接: ${data.download_url}`);
            break;
    }
};

ws.onclose = function() {
    console.log("WebSocket连接已关闭");
};

// 保持连接活跃
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
    }
}, 30000);
```

### 12. 智能体直接调用示例

```python
from patent_agent_demo.agents.planner_agent import PlannerAgent
from patent_agent_demo.agents.coordinator_agent import CoordinatorAgent

async def direct_agent_usage():
    # 创建规划智能体
    planner = PlannerAgent(test_mode=True)
    await planner.start()
    
    # 执行规划任务
    task_data = {
        "type": "patent_planning",
        "topic": "智能体多层参数调用",
        "description": "基于多智能体系统的参数传递和调用机制"
    }
    
    result = await planner.execute_task(task_data)
    
    if result.success:
        print("规划任务执行成功")
        print(f"策略: {result.data['strategy']}")
    else:
        print(f"规划任务执行失败: {result.error_message}")
    
    # 停止智能体
    await planner.stop()

# 运行示例
asyncio.run(direct_agent_usage())
```

---

## 🔧 配置和部署

### 13. 环境配置

#### 13.1 依赖安装
```bash
pip install -r requirements.txt
```

#### 13.2 环境变量
```bash
# OpenAI API密钥（可选，用于主要LLM服务）
export OPENAI_API_KEY="your-openai-api-key"

# GLM API密钥（用于回退服务）
export GLM_API_KEY="your-glm-api-key"
```

#### 13.3 服务启动
```bash
# 直接启动
python3 unified_service.py

# 后台启动
nohup python3 unified_service.py > service.log 2>&1 &

# 检查服务状态
ps aux | grep "python3 unified_service.py"
```

### 14. 测试模式

#### 14.1 测试模式特点
- **智能体正常运行**: 所有智能体都会启动并执行
- **跳过LLM调用**: 不调用大模型API，使用模拟数据
- **快速执行**: 适合开发和调试阶段使用
- **保持完整性**: 工作流程和状态管理完全正常

#### 14.2 真实模式特点
- **完整LLM调用**: 通过OpenAI Client和GLM-4.5-flash生成高质量内容
- **智能回退**: 自动在OpenAI和GLM服务间切换
- **并发控制**: 智能信号量控制避免API限流
- **迭代优化**: 3轮DuckDuckGo检索 + GLM分析优化
- **生产就绪**: 适合正式专利撰写使用

---

## 🚨 注意事项和最佳实践

### 15. 重要注意事项

1. **工作流类型**: 目前只支持 `workflow_type: "patent"`
2. **必填字段**: `topic` 和 `workflow_type` 为必填项
3. **描述字段**: `description` 为可选，不提供时会自动生成
4. **测试模式**: 建议开发阶段使用 `test_mode: true`
5. **服务端口**: 确保8000端口未被占用
6. **LLM服务**: 真实模式需要配置OpenAI或GLM API密钥
7. **并发限制**: GLM API有严格的并发限制，系统已优化处理
8. **搜索策略**: 搜索阶段采用3轮迭代策略，耗时较长但质量更高

### 16. 最佳实践

1. **使用WebSocket**: 推荐使用WebSocket进行实时监控
2. **错误处理**: 实现适当的错误处理和重试机制
3. **资源管理**: 及时下载和清理工作流结果
4. **测试验证**: 在测试模式下验证工作流逻辑
5. **日志监控**: 关注服务日志以排查问题

---

## 📞 技术支持

### 17. 故障排除

#### 17.1 常见问题
1. **端口占用**: 检查8000端口是否被其他服务占用
2. **依赖缺失**: 确保已安装所有requirements.txt中的包
3. **权限问题**: 确保有足够的文件读写权限
4. **服务未启动**: 检查unified_service.py是否正常运行
5. **WebSocket连接失败**: 检查浏览器是否支持WebSocket，网络是否正常
6. **下载失败**: 检查工作流是否已完成，文件是否存在
7. **进度查询异常**: 检查workflow_id是否正确，工作流是否在运行
8. **GLM API 429错误**: 系统已优化并发控制，如仍出现请等待后重试
9. **搜索阶段耗时过长**: 正常现象，3轮迭代搜索需要时间
10. **LLM服务调用失败**: 检查API密钥配置和网络连接

#### 17.2 调试命令
```bash
# 检查服务状态
ps aux | grep "python3 unified_service.py"

# 查看服务日志
tail -f service.log

# 检查端口占用
netstat -tlnp | grep :8000

# 测试服务连通性
curl -X GET "http://localhost:8000/health"

# 测试WebSocket连接
wscat -c ws://localhost:8000/ws/workflow/{workflow_id}

# 检查工作流目录
ls -la workflow_stages/

# 检查特定工作流文件
ls -la workflow_stages/{workflow_id}_{topic}/

# 测试下载接口
curl -I "http://localhost:8000/download/workflow/{workflow_id}"
```

---

## 📚 相关文档

- **[README.md](README.md)** - 项目主页和快速开始指南
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - 文档导航索引
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 项目结构详细说明
- **[API_INTERFACE_TESTING.md](API_INTERFACE_TESTING.md)** - API接口测试文档
- **[PR_PATENT_GENERATION_COMPLETE.md](PR_PATENT_GENERATION_COMPLETE.md)** - 专利生成系统完成PR总结

---

**版本**: 2.0.0  
**最后更新**: 2025年1月23日  
**维护者**: 多智能体专利系统开发团队