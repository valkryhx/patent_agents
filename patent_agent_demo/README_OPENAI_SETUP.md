# OpenAI GPT-5 + GLM-4.5 Fallback Setup

## 概述

本系统现在支持OpenAI GPT-5作为主要AI模型，当OpenAI API配额不足或出现错误时，自动降级到GLM-4.5模型。

## 功能特性

### 🔄 智能降级系统
- **主要模型**: OpenAI GPT-5 (支持web search工具)
- **备用模型**: GLM-4.5 (本地部署)
- **自动切换**: 当OpenAI API失败时自动降级

### 🌐 搜索功能
- **OpenAI模式**: 使用GPT-5的web search工具
- **GLM降级模式**: 使用免费的DuckDuckGo搜索

## 设置步骤

### 1. 创建OpenAI API Key文件

```bash
# 在patent_agent_demo目录下创建私钥文件
echo "your_openai_api_key_here" > patent_agent_demo/private_openai_key
```

**⚠️ 重要**: 确保此文件已添加到.gitignore中，不要提交到版本控制

### 2. 安装依赖

```bash
# 激活虚拟环境
source patent_env/bin/activate

# 安装OpenAI依赖
pip install openai requests
```

### 3. 验证设置

```bash
# 测试降级功能
python test_fallback.py

# 测试DuckDuckGo搜索
python test_duckduckgo.py
```

## 使用方法

### 基本使用

```python
from patent_agent_demo.openai_client import OpenAIClient

# 初始化客户端
client = OpenAIClient()

# 分析专利主题 (自动降级支持)
analysis = await client.analyze_patent_topic("主题", "描述")

# 搜索现有技术 (自动降级支持)
results = await client.search_prior_art("主题", ["关键词1", "关键词2"])

# 生成专利草稿 (自动降级支持)
draft = await client.generate_patent_draft("主题", "描述", analysis)
```

### 降级行为

1. **首次尝试**: 使用OpenAI GPT-5
2. **检测到错误**: 自动切换到GLM-4.5
3. **搜索降级**: 从OpenAI web search切换到DuckDuckGo

## 错误处理

### OpenAI配额不足 (429错误)
- 自动检测配额错误
- 无缝切换到GLM-4.5
- 记录降级日志

### 网络错误
- 重试机制
- 降级到本地GLM模型
- 保持系统可用性

## 日志和监控

系统会记录以下信息：
- OpenAI API调用状态
- 降级触发原因
- GLM备用模型使用情况
- 搜索功能切换状态

## 故障排除

### 常见问题

1. **OpenAI API Key无效**
   - 检查private_openai_key文件
   - 验证API key格式

2. **GLM降级失败**
   - 检查GLM服务状态
   - 验证GLM客户端配置

3. **DuckDuckGo搜索失败**
   - 检查网络连接
   - 验证requests库安装

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 性能优化

- **智能缓存**: 避免重复API调用
- **批量处理**: 优化多个请求
- **异步支持**: 提高并发性能

## 安全注意事项

- 永远不要提交API key到版本控制
- 使用环境变量或私钥文件
- 定期轮换API key
- 监控API使用量