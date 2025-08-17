# 专利智能体系统项目结构

## 项目概述
这是一个基于FastAPI的多智能体专利撰写系统，包含协调器服务和多个专业智能体服务。

## 核心目录结构

### 根目录
- `unified_service.py` - 主要的统一服务文件，包含协调器和所有智能体服务
- `main.py` - 协调器服务（包含专利相关API接口）
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

### 其他目录
- `.private/` - 私有配置文件（保留）
- `executors/` - 执行器目录
- `output/` - 输出目录
- `venv/` - Python虚拟环境

## 主要功能

### 1. 专利生成工作流
- POST `/patent/generate` - 启动专利撰写工作流
- 支持测试模式和真实模式
- 自动生成专利描述（基于topic）

### 2. 工作流管理
- 工作流状态查询
- 结果获取
- 工作流重启和删除
- 工作流列表查看

### 3. 智能体系统
- 6个专业智能体协同工作
- 支持测试模式（跳过LLM调用）
- 工作流隔离机制

## 启动方式

### 启动统一服务
```bash
python3 unified_service.py
```

### 启动协调器服务
```bash
python3 main.py
```

## 测试

所有测试代码已整理到 `test/` 目录中，包括：
- `test_patent_api.py` - 专利API测试
- `test_description_generation.py` - 描述生成测试
- `show_workflows.py` - 工作流显示工具

## 注意事项

1. `.private/` 目录包含重要配置，请勿删除
2. 核心智能体代码在 `patent_agent_demo/agents/` 目录
3. 主要服务入口是 `unified_service.py`
4. 测试代码已整理到 `test/` 目录，便于管理