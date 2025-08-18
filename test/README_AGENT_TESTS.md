# 智能体测试脚本说明

本目录包含了用于测试三个智能体（Discussion、Reviewer、Rewriter）在不同GLM模式下的表现的测试脚本。

## 📁 测试文件列表

### 1. 单独测试脚本
- `test_discussion_agent.py` - 测试 Discussion Agent
- `test_reviewer_agent.py` - 测试 Reviewer Agent  
- `test_rewriter_agent.py` - 测试 Rewriter Agent

### 2. 综合测试脚本
- `test_all_agents_glm.py` - 一次性测试所有三个智能体

## 🎯 测试目标

验证三个智能体在以下两种模式下的正确行为：

1. **GLM_AVAILABLE=False** - 应该使用mock数据，快速响应
2. **GLM_AVAILABLE=True** - 应该调用GLM API，生成高质量内容

## 🚀 使用方法

### 单独测试某个智能体

```bash
# 测试 Discussion Agent
cd test
python3 test_discussion_agent.py

# 测试 Reviewer Agent
python3 test_reviewer_agent.py

# 测试 Rewriter Agent
python3 test_rewriter_agent.py
```

### 综合测试所有智能体

```bash
# 一次性测试所有智能体
cd test
python3 test_all_agents_glm.py
```

## 📊 测试内容

每个测试脚本会：

1. **设置GLM模式** - 临时修改 `GLM_AVAILABLE` 变量
2. **准备测试数据** - 使用统一的测试主题和模拟数据
3. **执行智能体任务** - 调用相应的 `execute_*_task` 函数
4. **分析结果** - 检查输出质量和执行时间
5. **验证模式** - 确认是否使用了正确的模式（GLM API vs Mock数据）
6. **保存结果** - 将测试结果保存为JSON文件

## 📋 测试数据

所有测试使用统一的测试主题：
```
基于语义理解的复杂函数参数智能推断与分层调用重试优化方法
```

测试数据包括：
- Planning阶段结果（策略、创新领域、新颖性评分）
- Search阶段结果（搜索结果、现有技术）
- Discussion阶段结果（创新点、技术洞察、建议）
- Drafting阶段结果（专利草稿）
- Review阶段结果（质量评分、反馈、建议）

## 📈 预期结果

### GLM_AVAILABLE=False 模式
- ✅ 执行时间短（< 1秒）
- ✅ 使用mock数据（`mock_delay_applied > 0`）
- ✅ 生成基本内容结构
- ✅ 适合测试模式

### GLM_AVAILABLE=True 模式
- ✅ 执行时间较长（> 1秒，取决于GLM API响应时间）
- ✅ 调用GLM API（`mock_delay_applied = 0`）
- ✅ 生成高质量、详细的内容
- ✅ 适合真实模式

## 📄 输出文件

每个测试会生成以下文件：

### 日志文件
- `test_discussion_agent.log` - Discussion Agent测试日志
- `test_reviewer_agent.log` - Reviewer Agent测试日志
- `test_rewriter_agent.log` - Rewriter Agent测试日志
- `test_all_agents_glm.log` - 综合测试日志

### 结果文件
- `test_discussion_agent_glm_false_output.json` - Discussion Agent (GLM=False) 结果
- `test_discussion_agent_glm_true_output.json` - Discussion Agent (GLM=True) 结果
- `test_reviewer_agent_glm_false_output.json` - Reviewer Agent (GLM=False) 结果
- `test_reviewer_agent_glm_true_output.json` - Reviewer Agent (GLM=True) 结果
- `test_rewriter_agent_glm_false_output.json` - Rewriter Agent (GLM=False) 结果
- `test_rewriter_agent_glm_true_output.json` - Rewriter Agent (GLM=True) 结果

### 综合报告
- `test_all_agents_glm_report.json` - 所有测试的综合报告

## 🔍 结果分析

### Discussion Agent 结果字段
- `innovations` - 创新点列表
- `technical_insights` - 技术洞察列表
- `recommendations` - 建议列表
- `novelty_score` - 新颖性评分

### Reviewer Agent 结果字段
- `quality_score` - 质量评分
- `consistency_score` - 一致性评分
- `feedback` - 反馈列表
- `recommendations` - 建议列表
- `compliance_check` - 合规检查结果

### Rewriter Agent 结果字段
- `title` - 改进后的标题
- `abstract` - 改进后的摘要
- `claims` - 改进后的权利要求
- `detailed_description` - 改进后的详细描述
- `improvements` - 改进点列表

## ⚠️ 注意事项

1. **GLM API依赖** - 如果GLM API不可用，GLM_AVAILABLE=True的测试可能会回退到mock数据
2. **网络连接** - GLM API调用需要网络连接
3. **API限制** - 注意GLM API的调用频率限制
4. **测试环境** - 确保在正确的Python环境中运行测试

## 🐛 故障排除

### 常见问题

1. **ModuleNotFoundError** - 确保在正确的目录中运行，并且项目路径已正确设置
2. **GLM API调用失败** - 检查网络连接和API配置
3. **测试超时** - GLM API调用可能需要较长时间，请耐心等待

### 调试建议

1. 查看详细的日志文件
2. 检查生成的JSON结果文件
3. 确认GLM_AVAILABLE变量的设置
4. 验证测试数据的完整性

## 📞 支持

如果遇到问题，请：
1. 查看日志文件中的详细错误信息
2. 检查生成的JSON结果文件
3. 确认系统配置和依赖项
4. 参考项目主README文档