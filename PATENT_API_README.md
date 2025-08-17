# 专利生成智能体系统 API

## 概述

这是一个基于FastAPI的专利撰写智能体系统，提供RESTful API接口来生成专利。系统支持测试模式和真实模式，可以处理不同的专利主题。

## 主要功能

- 🚀 **专利生成**: 通过POST接口启动专利撰写工作流
- 🔍 **状态查询**: 实时查询工作流执行状态和进度
- 📋 **工作流管理**: 列出、重启、删除工作流
- 🧪 **测试模式**: 支持测试模式，快速验证功能
- 🔒 **工作流隔离**: 每个工作流都有独立的执行环境

## API 端点

### 1. 专利生成

#### POST `/patent/generate`
启动一个新的专利撰写工作流

**请求体:**
```json
{
    "topic": "区块链",
    "description": "基于区块链技术的知识产权管理系统",
    "test_mode": true
}
```

**参数说明:**
- `topic` (必需): 专利主题
- `description` (可选): 专利描述，如果不提供会自动生成
- `test_mode` (可选): 是否启用测试模式，默认false

**响应示例:**
```json
{
    "workflow_id": "3e8cc09f-dc42-4955-9faa-0d63bf80d3ac",
    "status": "started",
    "message": "Patent generation started for topic: 区块链 (test_mode: True)"
}
```

### 2. 状态查询

#### GET `/patent/{workflow_id}/status`
查询专利工作流的状态和进度

**响应示例:**
```json
{
    "workflow_id": "3e8cc09f-dc42-4955-9faa-0d63bf80d3ac",
    "topic": "区块链",
    "status": "running",
    "test_mode": true,
    "current_stage": 0,
    "total_stages": 6,
    "progress": 0.0,
    "stages": [
        {
            "name": "planning",
            "status": "running",
            "start_time": 1755446618.236344,
            "end_time": null,
            "result": null,
            "error": null
        }
    ],
    "created_at": 1755446618.2360127,
    "updated_at": 1755446618.2593486
}
```

### 3. 工作流管理

#### GET `/patents`
列出所有专利工作流

#### GET `/workflows`
列出所有工作流（包括非专利工作流）

#### POST `/patent/{workflow_id}/restart`
重启失败的专利工作流

#### DELETE `/patent/{workflow_id}`
删除专利工作流

### 4. 系统状态

#### GET `/health`
系统健康检查

#### GET `/`
根端点，显示系统信息

## 使用示例

### 1. 启动区块链专利生成（测试模式）

```bash
curl -X POST "http://localhost:8000/patent/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "区块链",
    "description": "基于区块链技术的知识产权管理系统",
    "test_mode": true
  }'
```

### 2. 启动AI专利生成（真实模式）

```bash
curl -X POST "http://localhost:8000/patent/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能",
    "description": "基于深度学习的智能图像识别系统",
    "test_mode": false
  }'
```

### 3. 查询工作流状态

```bash
curl "http://localhost:8000/patent/{workflow_id}/status"
```

### 4. 列出所有专利工作流

```bash
curl "http://localhost:8000/patents"
```

## 工作流阶段

系统包含以下6个阶段：

1. **Planning** (规划): 制定专利撰写策略
2. **Search** (搜索): 搜索现有技术和专利
3. **Discussion** (讨论): 讨论创新点和优势
4. **Drafting** (撰写): 撰写专利文档
5. **Review** (审查): 审查专利质量
6. **Rewrite** (重写): 根据反馈进行修改

## 测试模式 vs 真实模式

### 测试模式 (`test_mode: true`)
- 快速执行，用于功能验证
- 跳过LLM调用，使用模拟数据
- 适合开发和测试环境

### 真实模式 (`test_mode: false`)
- 完整执行所有阶段
- 调用真实的AI服务
- 适合生产环境

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │ WorkflowManager │    │  Agent Services │
│                 │    │                 │    │                 │
│  /patent/*      │◄──►│  Task Assignment│◄──►│  Planner       │
│  /workflow/*    │    │  State Mgmt     │    │  Searcher      │
│  /health        │    │  Progress Track │    │  Discusser     │
└─────────────────┘    └─────────────────┘    │  Writer        │
                                              │  Reviewer      │
                                              │  Rewriter      │
                                              └─────────────────┘
```

## 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python3 main.py
```

服务将在 `http://localhost:8000` 启动

## API 文档

启动服务后，可以通过以下地址访问API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## 注意事项

1. **Agent服务**: 当前只启动了协调器服务，agent服务需要单独启动
2. **工作流状态**: 由于agent服务未运行，工作流会显示为failed状态
3. **测试模式**: 建议在开发阶段使用测试模式
4. **错误处理**: 系统包含完整的错误处理和状态跟踪

## 故障排除

### 常见问题

1. **服务无法启动**: 检查端口8000是否被占用
2. **导入错误**: 确保所有依赖已正确安装
3. **工作流失败**: 检查agent服务是否正常运行

### 日志查看

服务启动时会显示详细的日志信息，包括：
- 工作流创建和状态更新
- 任务分配和执行
- 错误信息和调试信息

## 开发说明

### 代码结构

- `main.py`: FastAPI应用主文件
- `models.py`: 数据模型定义
- `workflow_manager.py`: 工作流管理器
- `test_patent_api.py`: API测试脚本

### 扩展功能

系统设计为可扩展架构，可以轻松添加：
- 新的agent服务
- 不同的工作流类型
- 自定义的测试模式配置
- 更多的API端点