# 🤖 智能体系统 (Agentic System)

一个基于MCP (Model Context Protocol) 和GLM-4.5-flash模型的智能体系统，能够自动规划任务并调用工具完成复杂工作流程。

## ✨ 特性

- **智能任务规划**: 使用GLM-4.5-flash模型自动分析用户需求并制定执行计划
- **MCP工具集成**: 提供三个具有逻辑依赖关系的工具
- **自动依赖管理**: 智能检查工具执行顺序，确保依赖关系正确
- **详细执行报告**: 生成完整的任务执行总结和洞察
- **交互式界面**: 支持交互模式和演示模式
- **配置化管理**: 灵活的配置系统，支持自定义参数

## 🛠️ 系统架构

```
用户请求 → 智能体 → 任务规划 → 工具执行 → 结果汇总
    ↓           ↓         ↓         ↓         ↓
  自然语言    GLM模型   执行计划    MCP工具   分析报告
```

### 工具依赖关系

1. **数据收集工具** (`data_collector`)
   - 功能：收集和预处理数据
   - 依赖：无
   - 输出：结构化数据

2. **数据分析工具** (`data_analyzer`)
   - 功能：分析已收集的数据，生成统计信息和洞察
   - 依赖：必须先执行 `data_collector`
   - 输出：分析结果和建议

3. **报告生成工具** (`report_generator`)
   - 功能：基于数据收集和分析结果生成综合报告
   - 依赖：必须先执行 `data_collector` 和 `data_analyzer`
   - 输出：格式化的报告文档

## 🚀 快速开始

### 1. 安装依赖

```bash
cd agentic
pip install -r requirements.txt
```

### 2. 配置API密钥

系统会自动从以下位置查找GLM API密钥（按优先级排序）：

1. 命令行参数：`--api-key <your-key>`
2. 环境变量：`GLM_API_KEY`
3. 配置文件：`config.json`
4. `.private/GLM_API_KEY` 文件

### 3. 运行系统

#### 交互模式（默认）
```bash
python main.py
```

#### 演示模式
```bash
python main.py --mode demo
```

#### 指定API密钥
```bash
python main.py --api-key <your-glm-api-key>
```

## 📖 使用说明

### 交互模式命令

- `plan <任务描述>` - 规划任务执行步骤
- `execute <任务描述>` - 完整执行任务
- `tools` - 查看可用工具
- `status` - 查看系统状态
- `help` - 显示帮助信息
- `quit` - 退出系统

### 示例任务

```
plan 分析电商网站用户行为数据并生成洞察报告
execute 收集社交媒体数据并生成趋势分析报告
```

### 任务执行流程

1. **任务分析**: 智能体分析用户需求
2. **计划制定**: 生成详细的执行计划
3. **依赖检查**: 验证工具执行顺序
4. **工具调用**: 按计划执行各个工具
5. **结果汇总**: 生成执行总结和洞察

## ⚙️ 配置说明

### 配置文件结构

```json
{
  "glm": {
    "api_key": "",
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "model": "glm-4.5-flash",
    "temperature": 0.7,
    "max_tokens": 4000,
    "timeout": 60
  },
  "mcp_server": {
    "name": "agentic-mcp-server",
    "version": "1.0.0",
    "log_level": "INFO"
  },
  "agent": {
    "planning_timeout": 30,
    "execution_timeout": 300,
    "max_retries": 3,
    "retry_delay": 1
  },
  "tools": {
    "data_collector": {
      "enabled": true,
      "timeout": 60,
      "max_data_points": 10000
    },
    "data_analyzer": {
      "enabled": true,
      "timeout": 120,
      "supported_analysis_types": [
        "descriptive", "exploratory", "statistical", "ml_prediction"
      ]
    },
    "report_generator": {
      "enabled": true,
      "timeout": 90,
      "supported_formats": ["markdown", "html", "pdf", "json"],
      "default_format": "markdown"
    }
  }
}
```

### 环境变量

- `GLM_API_KEY`: GLM API密钥
- `GLM_BASE_URL`: GLM API基础URL（可选）
- `LOG_LEVEL`: 日志级别（可选）

## 🔧 开发说明

### 项目结构

```
agentic/
├── mcp_server.py          # MCP服务器实现
├── intelligent_agent.py   # 智能体核心逻辑
├── main.py               # 主程序入口
├── config.py             # 配置管理
├── requirements.txt      # 依赖包列表
└── README.md            # 说明文档
```

### 核心组件

- **AgenticMCPServer**: MCP服务器，提供工具接口
- **IntelligentAgent**: 智能体主类，负责任务规划和执行
- **TaskPlanner**: 任务规划器，使用GLM模型制定执行计划
- **ToolExecutor**: 工具执行器，管理和执行工具调用
- **Config**: 配置管理器，处理系统配置

### 扩展工具

要添加新工具，需要：

1. 在 `AgenticMCPServer.setup_tools()` 中定义工具
2. 在 `AgenticMCPServer.execute_*()` 中实现工具逻辑
3. 在 `IntelligentAgent._check_dependencies()` 中定义依赖关系
4. 更新配置文件和文档

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   - 检查API密钥是否正确
   - 确认API密钥有足够的权限

2. **工具执行失败**
   - 检查依赖关系是否正确
   - 查看日志文件了解详细错误信息

3. **配置问题**
   - 运行 `python config.py` 验证配置
   - 检查配置文件格式是否正确

### 日志文件

系统日志保存在 `agentic.log` 文件中，包含详细的执行信息和错误堆栈。

## 📝 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看本文档的故障排除部分
2. 检查日志文件
3. 提交GitHub Issue

---

**注意**: 本系统需要有效的GLM API密钥才能正常工作。请确保您有足够的API调用额度。