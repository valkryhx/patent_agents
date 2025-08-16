# 增强的专利撰写系统

## 概述

本项目是一个基于多智能体协作的专利撰写系统，通过引入上下文管理机制解决了不同执行环节智能体之间的主题偏移和漂移问题，显著提升了专利撰写的质量和一致性。

## 主要特性

### 🔧 核心功能
- **多智能体协作**: 6个专业智能体分工协作，覆盖专利撰写的完整流程
- **上下文管理**: 智能维护主题一致性和术语标准化
- **实时监控**: 全程监控工作流执行状态和进度
- **质量保证**: 多轮审查和重写机制确保文档质量
- **多格式输出**: 支持Markdown、JSON等多种文档格式

### 🎯 解决的问题
- **主题偏移**: 通过上下文管理器确保各阶段主题一致性
- **术语漂移**: 建立术语标准库，统一专业术语使用
- **质量不稳定**: 引入审查-重写循环机制
- **缺乏可追溯性**: 完整的执行记录和证据链

## 系统架构

### 智能体组成
1. **规划智能体 (Planner Agent)**: 制定专利开发策略
2. **搜索智能体 (Searcher Agent)**: 检索现有技术和相关专利
3. **讨论智能体 (Discusser Agent)**: 深入讨论创新点和实施方案
4. **撰写智能体 (Writer Agent)**: 起草专利文档
5. **审查智能体 (Reviewer Agent)**: 质量审查和合规性检查
6. **重写智能体 (Rewriter Agent)**: 根据反馈优化文档
7. **协调智能体 (Coordinator Agent)**: 协调各智能体工作流程

### 上下文管理系统
- **主题定义**: 统一专利主题和核心概念
- **术语标准**: 建立专业术语词典
- **一致性验证**: 实时检查内容一致性
- **上下文传递**: 智能体间上下文信息传递

## 安装和配置

### 环境要求
- Python 3.8+
- 异步支持
- 相关依赖包

### 安装步骤
```bash
# 克隆项目
git clone <repository-url>
cd patent-agent-system

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
# 在相应配置文件中设置OpenAI、GLM等API密钥
```

## 使用方法

### 快速开始

#### 1. 基本使用
```python
from generate_complete_patent import CompletePatentGenerator

# 创建生成器
generator = CompletePatentGenerator()

# 定义专利主题
topic = "证据图增强的检索增强生成系统"
description = "一种通过构建跨文档证据关系图并进行子图选择驱动生成与验证的RAG系统"

# 生成专利文档
result = await generator.generate_patent(topic, description)
```

#### 2. 增强工作流
```python
from enhanced_patent_workflow import EnhancedPatentWorkflow

# 创建增强工作流
workflow = EnhancedPatentWorkflow()

# 启动工作流
start_result = await workflow.start_workflow(topic, description)

# 监控进度
monitor_result = await workflow.monitor_workflow()

# 获取结果
patent_result = await workflow.get_final_patent()
```

#### 3. 测试系统
```bash
# 运行测试
python test_enhanced_workflow.py

# 运行完整生成
python generate_complete_patent.py
```

### 高级配置

#### 自定义主题定义
```python
from patent_agent_demo.context_manager import context_manager

# 获取主题定义
theme = await context_manager.get_context_summary(workflow_id)

# 自定义术语标准
custom_terminology = {
    "RAG": "检索增强生成(Retrieval-Augmented Generation)",
    "证据图": "证据关系图(Evidence Graph)"
}
```

#### 工作流监控
```python
# 实时监控工作流状态
status_result = await system.get_workflow_status(workflow_id)

# 获取系统健康状态
health_status = await system.health_check()
```

## 输出格式

### 生成的文件类型
1. **Markdown文档** (`patent_*.md`): 人类可读的专利文档
2. **JSON文档** (`patent_*.json`): 结构化数据格式
3. **结构化文档** (`patent_structured_*.md`): 详细的结构化专利文档
4. **上下文摘要** (`context_summary_*.json`): 上下文管理信息
5. **执行报告** (`execution_report_*.json`): 工作流执行详情

### 文档结构
```
专利文档
├── 基本信息
│   ├── 标题
│   ├── 核心概念
│   └── 技术领域
├── 关键创新点
├── 策略规划
├── 现有技术分析
├── 创新讨论
├── 专利草稿
├── 质量审查
└── 最终版本
```

## 技术特点

### 上下文一致性保证
- **主题约束**: 确保所有内容围绕核心主题
- **术语统一**: 标准化专业术语使用
- **逻辑连贯**: 保持技术逻辑的一致性
- **质量验证**: 多维度质量检查

### 智能体协作机制
- **消息总线**: 异步消息传递系统
- **状态管理**: 实时状态监控和更新
- **错误处理**: 完善的错误恢复机制
- **资源管理**: 智能资源分配和清理

### 质量保证体系
- **多轮审查**: 自动化的审查-重写循环
- **一致性检查**: 实时内容一致性验证
- **合规性验证**: 专利撰写规范检查
- **质量评分**: 客观的质量评估指标

## 性能优化

### 并发处理
- 智能体并行执行
- 异步消息处理
- 资源池化管理

### 缓存机制
- 上下文信息缓存
- 中间结果缓存
- 模板缓存

### 错误恢复
- 自动重试机制
- 降级处理策略
- 状态恢复功能

## 监控和调试

### 日志系统
```python
import logging

# 配置日志级别
logging.basicConfig(level=logging.INFO)

# 查看详细日志
logger = logging.getLogger(__name__)
```

### 性能监控
```python
# 获取性能指标
metrics = await agent.get_performance_metrics()

# 系统状态监控
status = await system.get_system_status()
```

### 调试工具
- 工作流可视化
- 消息追踪
- 状态检查工具

## 扩展开发

### 添加新的智能体
```python
from patent_agent_demo.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="custom_agent",
            capabilities=["custom_capability"]
        )
    
    async def execute_task(self, task_data):
        # 实现自定义任务逻辑
        pass
```

### 自定义上下文类型
```python
from patent_agent_demo.context_manager import ContextType

# 定义新的上下文类型
class CustomContextType(Enum):
    CUSTOM_TYPE = "custom_type"
```

### 扩展验证规则
```python
# 添加自定义验证规则
async def custom_validation(output, context):
    # 实现自定义验证逻辑
    pass
```

## 故障排除

### 常见问题

#### 1. 工作流启动失败
- 检查API密钥配置
- 验证网络连接
- 查看错误日志

#### 2. 主题不一致
- 检查主题定义
- 验证上下文传递
- 查看一致性检查结果

#### 3. 性能问题
- 检查资源使用情况
- 优化并发设置
- 调整超时参数

### 调试步骤
1. 检查日志输出
2. 验证配置参数
3. 测试网络连接
4. 检查依赖包版本

## 贡献指南

### 开发环境设置
```bash
# 设置开发环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 代码规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档
- 编写单元测试
- 提交前运行测试套件

### 提交规范
- 使用清晰的提交信息
- 关联相关Issue
- 包含测试用例

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

## 更新日志

### v2.0.0 (当前版本)
- 新增上下文管理系统
- 解决主题偏移问题
- 增强质量保证机制
- 优化性能表现

### v1.0.0
- 基础多智能体系统
- 基本专利撰写功能
- 简单工作流管理

---

*本文档由增强的专利撰写系统自动生成*