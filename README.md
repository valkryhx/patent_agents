# 多智能体专利撰写系统 (Multi-Agent Patent Drafting System)

## 📖 项目概述

这是一个基于多智能体架构的专利撰写系统，通过协调器统一管理多个专业智能体，实现从专利主题到最终专利文档的完整工作流程。系统支持测试模式和真实模式，在测试模式下跳过大模型API调用，在真实模式下通过LLM服务生成高质量内容。

## 🏗️ 系统架构

### 核心组件
- **协调器服务 (Coordinator)**: 统一管理工作流执行和任务分配
- **智能体系统 (Agent System)**: 6个专业智能体协同工作
- **工作流管理器 (Workflow Manager)**: 管理专利撰写流程状态
- **统一服务 (Unified Service)**: 单端口提供所有服务接口
- **LLM服务管理**: 统一的OpenAI Client管理，支持GLM-4.5-flash回退

### 智能体分工
1. **规划智能体 (Planner)**: 分析专利主题，制定撰写计划
2. **搜索智能体 (Searcher)**: 3轮迭代式检索（DuckDuckGo + GLM分析）
3. **讨论智能体 (Discussion)**: 分析技术方案，确定创新点
4. **撰写智能体 (Writer)**: 生成专利文档初稿
5. **审查智能体 (Reviewer)**: 审查文档质量和合规性
6. **重写智能体 (Rewriter)**: 根据审查意见优化文档

### 核心技术特性
- **迭代式搜索**: 3轮DuckDuckGo检索 + GLM分析优化关键词
- **并发控制**: 智能信号量控制，避免GLM API 429错误
- **统一LLM管理**: OpenAI Client统一接口，自动GLM回退
- **错误处理**: 完善的超时重试和异常处理机制

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 依赖包: FastAPI, Uvicorn, Pydantic, httpx

### 系统特性

#### 🔄 实时保存与监控
- **WebSocket实时通知**: 阶段开始、完成、工作流完成等事件实时推送
- **进度查询接口**: 实时查询工作流进度和预估完成时间
- **实时保存**: 每个阶段完成后立即保存结果到文件

#### 📁 智能文件管理
- **工作流目录**: 每个工作流创建独立的目录结构
- **阶段结果**: 保存每个阶段的详细结果
- **最终专利**: 生成完整的专利文档
- **元数据管理**: 完整的文件索引和追踪

#### 🛡️ 数据安全保障
- **断点续传**: 支持工作流中断后的恢复
- **文件隔离**: 每个工作流独立存储空间
- **时间戳命名**: 避免文件覆盖和数据丢失
- **错误处理**: 完善的异常处理机制

#### ⚡ 高性能架构
- **并发支持**: 多个工作流可同时运行
- **异步处理**: 非阻塞的工作流执行
- **资源优化**: 高效的内存和存储管理

#### 🤖 智能LLM集成
- **统一接口**: OpenAI Client统一管理所有LLM调用
- **自动回退**: 智能回退到GLM-4.5-flash服务
- **并发控制**: 信号量控制避免API限流
- **迭代优化**: 3轮检索优化提升搜索质量

#### 🔗 章节合并管理
- **智能合并**: 自动识别和匹配工作流章节文件
- **顺序保证**: 严格按照专利撰写流程顺序合并
- **原始保留**: 合并过程中不修改任何原始文件
- **格式统一**: 生成标准化的完整专利文档

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
python3 unified_service.py
```

服务将在 `http://localhost:8000` 启动，API文档可通过 `http://localhost:8000/docs` 访问。

## 📚 文档结构

```
项目根目录/
├── README.md                           # 项目主页 (本文档)
├── DOCS_INDEX.md                       # 文档导航索引
├── PROJECT_STRUCTURE.md                # 项目结构详细说明
├── API_INTERFACE_TESTING.md            # API接口测试文档
├── CLEANUP_SUMMARY.md                  # 代码清理总结
├── FINAL_CLEANUP_SUMMARY.md           # 最终清理总结
├── PR_PATENT_GENERATION_COMPLETE.md   # 专利生成系统完成PR总结
├── unified_service.py                  # 统一服务主文件
├── workflow_manager.py                 # 工作流管理器
├── models.py                           # 数据模型定义
├── patent_agent_demo/                  # 核心智能体模块
│   ├── openai_client.py               # OpenAI Client统一接口
│   ├── glm_client.py                  # GLM-4.5-flash客户端
│   ├── agents/                        # 智能体实现
│   │   ├── writer_agent_simple.py     # 撰写智能体（核心）
│   │   ├── planner_agent.py           # 规划智能体
│   │   ├── searcher_agent.py          # 搜索智能体
│   │   ├── discussion_agent.py        # 讨论智能体
│   │   ├── reviewer_agent.py          # 审查智能体
│   │   └── rewriter_agent.py          # 重写智能体
├── test/                               # 测试代码目录
├── output/                             # 专利生成输出目录
│   └── progress/                       # 专利撰写进度文件
├── workflow_stages/                    # 工作流阶段结果
└── requirements.txt                    # 项目依赖
```

> 📖 **快速导航**: 查看 [DOCS_INDEX.md](DOCS_INDEX.md) 了解所有文档的用途和导航方式

## 🔌 服务启动

### 启动方式
```bash
# 直接启动
python3 unified_service.py

# 后台启动
nohup python3 unified_service.py > service.log 2>&1 &

# 检查服务状态
ps aux | grep "python3 unified_service.py"
```

### 启动信息
启动成功后，终端会显示：
```
🚀 Starting Multi-Agent Patent System...
📡 Single service will be available at: http://localhost:8000
📚 API docs will be available at: http://localhost:8000/docs
🤖 All agents available at:
   - Coordinator: /coordinator/* (Patent workflows only)
   - Planner: /agents/planner/*
   - Searcher: /agents/searcher/*
   - Discussion: /agents/discussion/*
   - Writer: /agents/writer/*
   - Reviewer: /agents/reviewer/*
   - Rewriter: /agents/rewriter/*
📋 Coordinator API endpoints (Patent workflows only):
   - POST /coordinator/workflow/start - Start patent workflow
   - GET /coordinator/workflow/{workflow_id}/status - Get patent workflow status
   - GET /coordinator/workflow/{workflow_id}/results - Get patent workflow results
   - POST /coordinator/workflow/{workflow_id}/restart - Restart patent workflow
   - DELETE /coordinator/workflow/{workflow_id} - Delete patent workflow
   - GET /coordinator/workflows - List all patent workflows
🔧 Test mode endpoints:
   - GET /test-mode - Check test mode status
   - POST /test-mode - Update test mode settings
```

## 📡 API接口调用

### 基础信息
- **服务地址**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`
- **健康检查**: `http://localhost:8000/health`
- **WebSocket**: `ws://localhost:8000/ws/workflow/{workflow_id}`

### 完整使用流程示例

以下是一个完整的工作流使用示例，展示如何启动、监控和下载专利撰写结果：

#### 步骤1: 启动专利工作流
```bash
# 启动工作流
curl -X POST "http://localhost:8000/coordinator/workflow/start" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "基于量子计算的机器学习算法优化系统",
    "workflow_type": "patent",
    "test_mode": true
  }'

# 响应示例
{
  "workflow_id": "2219e3da-6cdb-41f6-86ba-06e01b525331",
  "status": "started",
  "message": "Patent workflow started successfully for topic: 基于量子计算的机器学习算法优化系统"
}
```

#### 步骤2: 实时监控进度（WebSocket）
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

#### 步骤3: 查询进度状态
```bash
# 查询实时进度
curl "http://localhost:8000/workflow/2219e3da-6cdb-41f6-86ba-06e01b525331/progress"

# 响应示例
{
  "workflow_id": "2219e3da-6cdb-41f6-86ba-06e01b525331",
  "topic": "基于量子计算的机器学习算法优化系统",
  "status": "completed",
  "progress": "6/6",
  "percentage": 100.0,
  "download_url": "/download/workflow/2219e3da-6cdb-41f6-86ba-06e01b525331"
}
```

#### 步骤4: 下载完整工作流结果
```bash
# 下载整个工作流目录（ZIP格式）
curl -X GET "http://localhost:8000/download/workflow/2219e3da-6cdb-41f6-86ba-06e01b525331" \
  -o "quantum_ml_workflow.zip"

# 解压查看内容
unzip quantum_ml_workflow.zip
ls -la
```

### 1. 启动专利工作流

**接口**: `POST /coordinator/workflow/start`

**请求体**:
```json
{
  "topic": "智能体多层参数调用",
  "description": "基于多智能体系统的参数传递和调用机制",
  "workflow_type": "patent",
  "test_mode": true
}
```

**cURL调用**:
```bash
curl -X POST "http://localhost:8000/coordinator/workflow/start" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "智能体多层参数调用",
    "description": "基于多智能体系统的参数传递和调用机制",
    "workflow_type": "patent",
    "test_mode": true
  }'
```

**预期响应**:
```json
{
  "workflow_id": "uuid-string",
  "status": "started",
  "message": "Patent workflow started successfully for topic: 智能体多层参数调用 (test_mode: true)"
}
```

### 2. 查询工作流状态

**接口**: `GET /coordinator/workflow/{workflow_id}/status`

**cURL调用**:
```bash
curl -X GET "http://localhost:8000/coordinator/workflow/{workflow_id}/status"
```

**预期响应**:
```json
{
  "workflow_id": "uuid-string",
  "topic": "智能体多层参数调用",
  "description": "基于多智能体系统的参数传递和调用机制",
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

### 3. 获取工作流结果

**接口**: `GET /coordinator/workflow/{workflow_id}/results`

**cURL调用**:
```bash
curl -X GET "http://localhost:8000/coordinator/workflow/{workflow_id}/results"
```

**预期响应**:
```json
{
  "workflow_id": "uuid-string",
  "topic": "智能体多层参数调用",
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

### 4. 实时监控工作流进度

#### 4.1 WebSocket实时通知（推荐）

**接口**: `WS /ws/workflow/{workflow_id}`

**JavaScript示例**:
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

**通知类型说明**:
- **`connection_established`**: 连接建立确认
- **`stage_started`**: 阶段开始通知
- **`stage_completed`**: 阶段完成通知（包含进度）
- **`workflow_completed`**: 工作流完成通知（包含下载链接）

#### 4.2 进度查询接口

**接口**: `GET /workflow/{workflow_id}/progress`

**cURL调用**:
```bash
curl -X GET "http://localhost:8000/workflow/{workflow_id}/progress"
```

**预期响应**:
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

### 5. 下载工作流结果

#### 5.1 下载整个工作流目录（推荐）

**接口**: `GET /download/workflow/{workflow_id}`

**功能**: 下载包含所有阶段结果和最终专利文档的完整工作流目录（ZIP格式）

**cURL调用**:
```bash
curl -X GET "http://localhost:8000/download/workflow/{workflow_id}" \
  -o "workflow_{workflow_id}.zip"
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

### 5.2 合并工作流章节（新增功能）

**接口**: `POST /workflow/{workflow_id}/merge`

**功能**: 将工作流的所有章节按顺序合并为完整的专利文档，同时保留原始文件

**cURL调用**:
```bash
curl -X POST "http://localhost:8000/workflow/{workflow_id}/merge" \
  -H "Content-Type: application/json"
```

**合并章节顺序**:
1. **规划阶段 (Planning)**: 专利主题分析和撰写策略
2. **搜索阶段 (Search)**: 相关技术检索和文献分析
3. **讨论阶段 (Discussion)**: 技术方案讨论和创新点确定
4. **撰写阶段 (Drafting)**: 专利文档初稿生成
5. **审查阶段 (Review)**: 文档质量审查和合规性检查
6. **重写阶段 (Rewrite)**: 根据审查意见优化文档

**响应示例**:
```json
{
  "workflow_id": "workflow_id",
  "topic": "专利主题",
  "merged_filename": "merged_patent_workflow_id_timestamp.md",
  "merged_file_path": "workflow_stages/workflow_id_专利主题/merged_patent_workflow_id_timestamp.md",
  "total_size": 37305,
  "section_count": 6,
  "sections": [
    {
      "section": "规划阶段",
      "file": "planning_timestamp.md",
      "size": 1269,
      "status": "merged"
    }
  ],
  "message": "Workflow sections merged successfully",
  "download_url": "/download/workflow/{workflow_id}"
}
```

**合并文档存储位置**:
```
./workflow_stages/{workflow_id}_{专利主题}/merged_patent_{workflow_id}_{timestamp}.md
```

**功能特点**:
- ✅ **智能合并**: 自动识别和匹配章节文件
- ✅ **顺序保证**: 严格按照专利撰写流程顺序合并
- ✅ **原始保留**: 合并过程中不修改任何原始文件
- ✅ **版本选择**: 按时间戳自动选择最新的章节文件
- ✅ **错误容错**: 优雅处理缺失或损坏的文件
- ✅ **格式统一**: 生成标准化的完整专利文档

#### 5.2 仅下载最终专利文档

**接口**: `GET /download/patent/{workflow_id}`

**功能**: 仅下载最终生成的专利文档

**cURL调用**:
```bash
curl -X GET "http://localhost:8000/download/patent/{workflow_id}" \
  -o "final_patent_{workflow_id}.md"
```

### 6. 查看工作流文件结构

**接口**: `GET /workflow/{workflow_id}/stages`

**功能**: 查看工作流目录中的所有文件和元数据

**cURL调用**:
```bash
curl -X GET "http://localhost:8000/workflow/{workflow_id}/stages"
```

### 7. 合并工作流章节（新增功能）

**接口**: `POST /workflow/{workflow_id}/merge`

**功能**: 将工作流的所有章节按顺序合并为完整的专利文档

**cURL调用**:
```bash
curl -X POST "http://localhost:8000/workflow/{workflow_id}/merge"
```

**使用场景**:
- 需要查看完整专利文档时
- 需要将分章节文件整合为一个文档时
- 需要分享完整专利内容时
- 需要存档完整专利文档时

**注意事项**:
- 合并过程中会保留所有原始章节文件
- 合并文件会保存在原工作流目录中
- 文件名包含时间戳，确保唯一性
- 支持缺失章节的优雅处理

**预期响应**:
```json
{
  "workflow_id": "uuid-string",
  "topic": "基于量子计算的机器学习算法优化系统",
  "workflow_directory": "workflow_stages/{workflow_id}_{topic}",
  "metadata": {
    "workflow_id": "uuid-string",
    "topic": "基于量子计算的机器学习算法优化系统",
    "created_at": "2025-08-17 18:55:20",
    "status": "completed",
    "completed_at": "2025-08-17 18:55:32"
  },
  "stage_index": {
    "stages": {
      "planning": {
        "filename": "planning_1755456922.md",
        "timestamp": 1755456922,
        "generated_at": "2025-08-17 18:55:22"
      }
    }
  },
  "files": [
    {
      "filename": "planning_1755456922.md",
      "size": 301,
      "modified": "2025-08-17 18:55:22"
    }
  ]
}
```
    "rewrite": "最终专利文档已优化完成..."
  },
  "test_mode": true
}
```

### 4. 重启工作流

**接口**: `POST /coordinator/workflow/{workflow_id}/restart`

**cURL调用**:
```bash
curl -X POST "http://localhost:8000/coordinator/workflow/{workflow_id}/restart"
```

**预期响应**:
```json
{
  "workflow_id": "uuid-string",
  "status": "restarted",
  "message": "Patent workflow restarted"
}
```

### 5. 删除工作流

**接口**: `DELETE /coordinator/workflow/{workflow_id}`

**cURL调用**:
```bash
curl -X DELETE "http://localhost:8000/coordinator/workflow/{workflow_id}"
```

**预期响应**:
```json
{
  "workflow_id": "uuid-string",
  "status": "deleted",
  "message": "Patent workflow deleted"
}
```

### 6. 列出所有工作流

**接口**: `GET /coordinator/workflows`

**cURL调用**:
```bash
curl -X GET "http://localhost:8000/coordinator/workflows"
```

**预期响应**:
```json
{
  "workflows": [
    {
      "workflow_id": "uuid-string-1",
      "topic": "智能体多层参数调用",
      "description": "基于多智能体系统的参数传递和调用机制",
      "workflow_type": "patent",
      "status": "completed",
      "current_stage": "rewrite",
      "test_mode": true,
      "created_at": 1234567890
    }
  ],
  "patent_workflows": [...],
  "total_workflows": 1,
  "test_mode": true
}
```

### 7. 测试模式管理

**查询测试模式状态**:
```bash
curl -X GET "http://localhost:8000/test-mode"
```

**更新测试模式设置**:
```bash
curl -X POST "http://localhost:8000/test-mode" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

## 🔧 测试模式说明

### 测试模式特点
- **智能体正常运行**: 所有智能体都会启动并执行
- **跳过LLM调用**: 不调用大模型API，使用模拟数据
- **快速执行**: 适合开发和调试阶段使用
- **保持完整性**: 工作流程和状态管理完全正常

### 真实模式特点
- **完整LLM调用**: 通过OpenAI Client和GLM-4.5-flash生成高质量内容
- **智能回退**: 自动在OpenAI和GLM服务间切换
- **并发控制**: 智能信号量控制避免API限流
- **迭代优化**: 3轮DuckDuckGo检索 + GLM分析优化
- **生产就绪**: 适合正式专利撰写使用

### LLM服务配置
- **主要服务**: OpenAI GPT-5（需要API密钥）
- **回退服务**: GLM-4.5-flash（免费，需要API密钥）
- **并发限制**: 最大并发数1，避免429错误
- **重试机制**: 429错误自动等待30秒后重试

## 📋 工作流程说明

### 专利撰写流程
1. **规划阶段 (Planning)**: 分析主题，制定撰写策略
2. **搜索阶段 (Search)**: 3轮迭代式检索（DuckDuckGo + GLM分析优化）
3. **讨论阶段 (Discussion)**: 分析技术方案，确定创新点
4. **撰写阶段 (Drafting)**: 生成专利文档初稿
5. **审查阶段 (Review)**: 审查文档质量和合规性
6. **重写阶段 (Rewrite)**: 根据审查意见优化文档

### 迭代式搜索策略
- **第1轮**: 使用初始关键词进行DuckDuckGo检索
- **第2轮**: GLM分析第1轮结果，生成优化关键词，再次检索
- **第3轮**: GLM分析前两轮结果，生成最终关键词，最终检索
- **结果整合**: GLM对所有检索结果进行最终分析和增强

### 状态说明
- **pending**: 等待执行
- **running**: 正在执行
- **completed**: 执行完成
- **failed**: 执行失败

## 🚨 注意事项

1. **工作流类型**: 目前只支持 `workflow_type: "patent"`
2. **必填字段**: `topic` 和 `workflow_type` 为必填项
3. **描述字段**: `description` 为可选，不提供时会自动生成
4. **测试模式**: 建议开发阶段使用 `test_mode: true`
5. **服务端口**: 确保8000端口未被占用
6. **LLM服务**: 真实模式需要配置OpenAI或GLM API密钥
7. **并发限制**: GLM API有严格的并发限制，系统已优化处理
8. **搜索策略**: 搜索阶段采用3轮迭代策略，耗时较长但质量更高

## 🔍 故障排除

### 常见问题
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

### 调试命令
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

## 📞 技术支持

如有问题，请检查：
1. 服务是否正常启动
2. API接口是否可访问
3. 工作流状态是否正常
4. 测试模式设置是否正确
5. WebSocket连接是否正常建立
6. 工作流目录是否成功创建
7. 下载接口是否返回正确状态码
8. 文件权限是否正确设置

## 📚 相关文档

- **[DOCS_INDEX.md](DOCS_INDEX.md)** - 文档导航索引，快速找到所需文档
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 项目结构详细说明
- **[API_INTERFACE_TESTING.md](API_INTERFACE_TESTING.md)** - API接口测试文档和结果
- **[PR_PATENT_GENERATION_COMPLETE.md](PR_PATENT_GENERATION_COMPLETE.md)** - 专利生成系统完成PR总结
- **[GLM_API_TIMEOUT_FIX_SUMMARY.md](GLM_API_TIMEOUT_FIX_SUMMARY.md)** - GLM API超时问题修复总结
- **[ITERATIVE_SEARCH_AGENT_SUMMARY.md](ITERATIVE_SEARCH_AGENT_SUMMARY.md)** - 迭代式搜索智能体升级总结
- **[DATA_PASSING_BUG_FIX_SUMMARY.md](DATA_PASSING_BUG_FIX_SUMMARY.md)** - 数据传递Bug修复总结

---

**版本**: 2.0.0  
**最后更新**: 2025年8月23日  
**维护者**: 多智能体专利系统开发团队