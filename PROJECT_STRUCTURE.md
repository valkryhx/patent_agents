# 专利智能体系统项目结构

## 项目概述
这是一个基于FastAPI的多智能体专利撰写系统，包含协调器服务和多个专业智能体服务。**所有功能都整合在`unified_service.py`中，避免了端口冲突和架构问题。**

## 核心目录结构

### 根目录
- `unified_service.py` - **主要的统一服务文件，包含协调器、所有智能体服务和专利相关API接口**
- `workflow_manager.py` - 工作流管理器
- `models.py` - 数据模型定义
- `requirements.txt` - Python依赖包
- `LICENSE` - 项目许可证

### patent_agent_demo/ - 核心智能体系统
- `agents/` - 智能体实现目录
  - `base_agent.py` - 智能体基类
  - `coordinator_agent.py` - 协调器智能体
  - `planner_agent.py` - 规划智能体
  - `searcher_agent.py` - 搜索智能体
  - `discusser_agent.py` - 讨论智能体
  - `writer_agent.py` - 撰写智能体
  - `reviewer_agent.py` - 审查智能体
  - `rewriter_agent.py` - 重写智能体
- `openai_client.py` - OpenAI客户端（支持GPT-5和GLM-4.5-fallback）
- `glm_client.py` - GLM客户端
- `message_bus.py` - 消息总线
- `context_manager.py` - 上下文管理器
- `logging_utils.py` - 日志工具
- `telemetry.py` - 遥测功能

### test/ - 测试代码目录
包含所有测试相关的Python脚本和工具：
- 智能体测试文件
- 工作流测试文件
- API测试文件
- 监控和调试工具
- 演示脚本

### to_delete/ - 待删除文件目录
包含有问题的或过时的代码文件：
- `main.py` - **已废弃的启动代码，包含端口冲突和错误的架构假设**
- `README.md` - 说明为什么这些文件被移动到这里

### 其他目录
- `.private/` - 私有配置文件（保留）
- `executors/` - 执行器目录
- `output/` - 输出目录
- `venv/` - Python虚拟环境

## 主要功能

### 1. 专利生成工作流
- `POST /patent/generate` - 启动专利撰写工作流
- 支持测试模式和真实模式
- 自动生成专利描述（基于topic）

### 2. 工作流管理
- `GET /patent/{workflow_id}/status` - 工作流状态查询
- `GET /patent/{workflow_id}/results` - 结果获取
- `POST /patent/{workflow_id}/restart` - 工作流重启
- `DELETE /patent/{workflow_id}` - 工作流删除
- `GET /patents` - 工作流列表查看

### 3. 智能体系统
- 6个专业智能体协同工作
- 支持测试模式（跳过LLM调用）
- 工作流隔离机制

### 4. 协调器服务
- `POST /coordinator/workflow/start` - 启动工作流
- `GET /coordinator/workflows` - 列出所有工作流
- `GET /coordinator/workflow/{workflow_id}/status` - 获取工作流状态

## 启动方式

### ⚠️ 重要：只使用统一服务
```bash
python3 unified_service.py
```

**不要使用其他启动方式，因为：**
- `main.py` 有端口冲突问题
- `main.py` 包含错误的架构假设
- 所有功能都已整合到 `unified_service.py`

## 测试

所有测试代码已整理到 `test/` 目录中，包括：
- `test_patent_api.py` - 专利API测试
- `test_description_generation.py` - 描述生成测试
- `show_workflows.py` - 工作流显示工具

## 注意事项

1. **`.private/` 目录包含重要配置，请勿删除**
2. **核心智能体代码在 `patent_agent_demo/agents/` 目录**
3. **主要服务入口是 `unified_service.py`**
4. **测试代码已整理到 `test/` 目录，便于管理**
5. **`main.py` 已被移动到 `to_delete/` 目录，不要使用**
6. **所有专利相关API接口现在都在 `unified_service.py` 中**

## 架构优势

使用 `unified_service.py` 的优势：
- **单一端口**：避免端口冲突
- **统一管理**：所有服务在一个进程中
- **简化部署**：不需要启动多个服务
- **内部通信**：智能体间通信更高效
- **测试模式**：统一的测试模式控制