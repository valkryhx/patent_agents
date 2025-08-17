# 多智能体专利撰写系统 (Multi-Agent Patent Drafting System)

## 📖 项目概述

这是一个基于多智能体架构的专利撰写系统，通过协调器统一管理多个专业智能体，实现从专利主题到最终专利文档的完整工作流程。系统支持测试模式和真实模式，在测试模式下跳过大模型API调用，在真实模式下通过LLM服务生成高质量内容。

## 🏗️ 系统架构

### 核心组件
- **协调器服务 (Coordinator)**: 统一管理工作流执行和任务分配
- **智能体系统 (Agent System)**: 6个专业智能体协同工作
- **工作流管理器 (Workflow Manager)**: 管理专利撰写流程状态
- **统一服务 (Unified Service)**: 单端口提供所有服务接口

### 智能体分工
1. **规划智能体 (Planner)**: 分析专利主题，制定撰写计划
2. **搜索智能体 (Searcher)**: 检索相关技术信息和专利文献
3. **讨论智能体 (Discussion)**: 分析技术方案，确定创新点
4. **撰写智能体 (Writer)**: 生成专利文档初稿
5. **审查智能体 (Reviewer)**: 审查文档质量和合规性
6. **重写智能体 (Rewriter)**: 根据审查意见优化文档

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 依赖包: FastAPI, Uvicorn, Pydantic, httpx

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
├── unified_service.py                  # 统一服务主文件
├── workflow_manager.py                 # 工作流管理器
├── models.py                           # 数据模型定义
├── agents/                             # 智能体模块目录
│   ├── planner_agent.py               # 规划智能体
│   ├── searcher_agent.py              # 搜索智能体
│   ├── discussion_agent.py            # 讨论智能体
│   ├── writer_agent.py                # 撰写智能体
│   ├── reviewer_agent.py              # 审查智能体
│   └── rewriter_agent.py              # 重写智能体
├── test/                               # 测试代码目录
├── to_delete/                          # 待删除文件目录
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
- **完整LLM调用**: 通过大模型API生成高质量内容
- **真实数据**: 基于实际技术信息生成专利文档
- **生产就绪**: 适合正式专利撰写使用

## 📋 工作流程说明

### 专利撰写流程
1. **规划阶段 (Planning)**: 分析主题，制定撰写策略
2. **搜索阶段 (Search)**: 检索相关技术和专利文献
3. **讨论阶段 (Discussion)**: 分析技术方案，确定创新点
4. **撰写阶段 (Drafting)**: 生成专利文档初稿
5. **审查阶段 (Review)**: 审查文档质量和合规性
6. **重写阶段 (Rewrite)**: 根据审查意见优化文档

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

## 🔍 故障排除

### 常见问题
1. **端口占用**: 检查8000端口是否被其他服务占用
2. **依赖缺失**: 确保已安装所有requirements.txt中的包
3. **权限问题**: 确保有足够的文件读写权限
4. **服务未启动**: 检查unified_service.py是否正常运行

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
```

## 📞 技术支持

如有问题，请检查：
1. 服务是否正常启动
2. API接口是否可访问
3. 工作流状态是否正常
4. 测试模式设置是否正确

## 📚 相关文档

- **[DOCS_INDEX.md](DOCS_INDEX.md)** - 文档导航索引，快速找到所需文档
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 项目结构详细说明
- **[API_INTERFACE_TESTING.md](API_INTERFACE_TESTING.md)** - API接口测试文档和结果

---

**版本**: 1.0.0  
**最后更新**: 2024年  
**维护者**: 多智能体专利系统开发团队