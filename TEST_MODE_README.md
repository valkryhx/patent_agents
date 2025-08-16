# 专利工作流测试模式使用指南

## 概述

测试模式是为了快速排查专利工作流问题而设计的。在测试模式下，所有智能体都不会调用外部模型服务，而是使用预设的测试响应，这样可以：

- 🔍 快速定位问题环节
- ⚡ 快速验证系统架构
- 🛠️ 调试消息传递机制
- 📊 测试工作流逻辑

## 文件结构

```
patent_agent_demo/
├── test_mode_base.py              # 测试模式基础类
├── agents/
│   ├── base_agent_test.py         # 测试模式基础智能体
│   ├── planner_agent_test.py      # 规划智能体测试模式
│   ├── writer_agent_test.py       # 撰写智能体测试模式
│   ├── searcher_agent_test.py     # 检索智能体测试模式
│   ├── reviewer_agent_test.py     # 审查智能体测试模式
│   ├── rewriter_agent_test.py     # 重写智能体测试模式
│   ├── discusser_agent_test.py    # 讨论智能体测试模式
│   └── coordinator_agent_test.py  # 协调智能体测试模式
├── patent_agent_system_test.py    # 测试模式系统
└── main_test.py                   # 测试模式CLI接口

test_patent_agents.py              # 快速测试脚本
```

## 使用方法

### 1. 快速测试脚本

最简单的测试方式，运行：

```bash
# 运行简单测试（测试所有智能体）
python test_patent_agents.py

# 运行工作流测试
python test_patent_agents.py --workflow

# 详细输出
python test_patent_agents.py --verbose
```

### 2. CLI接口测试

使用完整的CLI接口：

```bash
# 进入专利代理演示目录
cd patent_agent_demo

# 运行简单测试
python -m main_test --simple --topic "智能图像识别" --description "基于深度学习的图像识别系统"

# 运行工作流测试
python -m main_test --workflow --topic "智能图像识别" --description "基于深度学习的图像识别系统"

# 交互式测试模式
python -m main_test --topic "智能图像识别" --description "基于深度学习的图像识别系统"

# 查看系统状态
python -m main_test --status
```

### 3. 编程接口测试

```python
import asyncio
from patent_agent_demo.patent_agent_system_test import PatentAgentSystemTestMode

async def test_agents():
    # 创建测试系统
    system = PatentAgentSystemTestMode()
    
    # 启动系统
    await system.start()
    
    # 运行简单测试
    result = await system.run_simple_test(
        topic="智能图像识别系统",
        description="基于深度学习的图像识别系统"
    )
    
    # 查看结果
    if result["success"]:
        for agent_name, agent_result in result["test_results"].items():
            print(f"{agent_name}: {'✅' if agent_result['success'] else '❌'}")
    
    # 关闭系统
    await system.stop()

# 运行测试
asyncio.run(test_agents())
```

## 测试模式特性

### ✅ 优势

1. **快速响应**: 无需等待外部API调用，响应时间通常在0.1秒内
2. **无网络依赖**: 完全离线运行，不依赖任何外部服务
3. **详细输出**: 每个智能体都会生成详细的测试内容
4. **易于调试**: 可以清楚看到每个环节的执行情况
5. **成本为零**: 不消耗任何API调用费用

### 📋 测试内容

每个智能体都会生成相应的测试内容：

- **Planner Agent**: 专利规划策略、风险评估、时间线
- **Searcher Agent**: 专利检索结果、竞争分析
- **Writer Agent**: 专利申请文件草稿
- **Reviewer Agent**: 审查意见、质量评估
- **Rewriter Agent**: 优化后的专利申请文件
- **Discusser Agent**: 技术讨论、团队意见
- **Coordinator Agent**: 工作流协调状态

### 🔧 调试功能

1. **详细日志**: 每个操作都有详细的日志记录
2. **执行时间**: 记录每个任务的执行时间
3. **状态监控**: 实时监控智能体状态
4. **错误追踪**: 详细的错误信息和堆栈跟踪

## 问题排查指南

### 1. 系统启动问题

如果系统无法启动，检查：

```bash
# 检查依赖
pip install -r patent_agent_demo/requirements.txt

# 检查Python版本（需要3.8+）
python --version

# 检查日志
python test_patent_agents.py --verbose
```

### 2. 智能体通信问题

如果智能体之间无法通信，检查：

```bash
# 检查消息总线状态
python -m main_test --status

# 运行简单测试查看详细日志
python test_patent_agents.py --verbose
```

### 3. 工作流卡住问题

如果工作流卡住，检查：

```bash
# 运行工作流测试
python test_patent_agents.py --workflow --verbose

# 查看协调器状态
python -m main_test --status
```

### 4. 特定智能体问题

如果某个智能体有问题，可以单独测试：

```python
# 单独测试某个智能体
from patent_agent_demo.agents.planner_agent_test import PlannerAgentTestMode

async def test_planner():
    agent = PlannerAgentTestMode()
    await agent.start()
    
    result = await agent.execute_task({
        "type": "patent_planning",
        "topic": "测试主题",
        "description": "测试描述"
    })
    
    print(f"Success: {result.success}")
    print(f"Content: {result.data.get('content', '')[:200]}...")
    
    await agent.stop()

asyncio.run(test_planner())
```

## 测试结果解读

### 成功指标

- ✅ 所有智能体都成功启动
- ✅ 每个智能体都能生成内容
- ✅ 执行时间合理（通常<1秒）
- ✅ 工作流能够正常协调

### 失败指标

- ❌ 智能体启动失败
- ❌ 无法生成内容
- ❌ 执行时间异常长
- ❌ 工作流卡住

### 性能基准

- **启动时间**: <5秒
- **单个智能体执行时间**: <0.5秒
- **完整测试时间**: <10秒
- **内存使用**: <100MB

## 扩展测试

### 自定义测试内容

可以修改 `test_mode_base.py` 中的测试内容：

```python
class CustomPlannerTestMode(PlannerTestMode):
    def _generate_test_content(self, task_type: str, task_data: Dict[str, Any]) -> str:
        # 自定义测试内容
        return "自定义的测试内容..."
```

### 添加新的测试场景

```python
# 添加新的测试场景
test_scenarios = [
    {
        "topic": "场景1",
        "description": "描述1"
    },
    {
        "topic": "场景2", 
        "description": "描述2"
    }
]

for scenario in test_scenarios:
    result = await system.run_simple_test(
        scenario["topic"], 
        scenario["description"]
    )
```

## 故障排除

### 常见问题

1. **ImportError**: 检查Python路径和依赖安装
2. **AttributeError**: 检查智能体类是否正确继承
3. **TimeoutError**: 检查消息总线配置
4. **MemoryError**: 检查系统资源使用

### 日志分析

```bash
# 查看详细日志
python test_patent_agents.py --verbose 2>&1 | grep -E "(ERROR|WARNING|CRITICAL)"

# 查看特定智能体日志
python test_patent_agents.py --verbose 2>&1 | grep "planner_agent"
```

### 性能分析

```python
import time
import cProfile
import pstats

def profile_test():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 运行测试
    asyncio.run(quick_test())
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

profile_test()
```

## 总结

测试模式是排查专利工作流问题的强大工具。通过使用测试模式，你可以：

1. 🔍 快速定位问题环节
2. ⚡ 验证系统架构
3. 🛠️ 调试消息传递
4. 📊 测试工作流逻辑
5. 💰 节省API调用成本

建议在开发、调试和问题排查时优先使用测试模式，确保系统基本功能正常后再切换到生产模式。