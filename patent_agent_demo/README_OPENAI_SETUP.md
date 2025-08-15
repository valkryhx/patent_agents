# OpenAI GPT-5 + GLM-4.5 Fallback Setup

## 概述

本系统现在支持OpenAI GPT-5作为主要AI模型，当OpenAI API配额不足或出现错误时，自动降级到GLM-4.5模型。

## 功能特性

### 智能降级系统
- **主要模型**: OpenAI GPT-5 (支持web search工具)
- **备用模型**: GLM-4.5 (本地部署)
- **自动切换**: 当OpenAI API失败时自动降级

### 搜索功能
- **OpenAI模式**: 使用GPT-5的web search工具
- **GLM降级模式**: 使用免费的DuckDuckGo搜索

## 环境配置

### 1. OpenAI API Key 配置

#### Linux/macOS 环境
```bash
# 方法1: 创建私钥文件
echo "your_openai_api_key_here" > patent_agent_demo/private_openai_key

# 方法2: 设置环境变量
export OPENAI_API_KEY="your_openai_api_key_here"

# 方法3: 添加到 ~/.bashrc 或 ~/.zshrc (永久设置)
echo 'export OPENAI_API_KEY="your_openai_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows 环境
```cmd
# 方法1: 创建私钥文件 (PowerShell)
"your_openai_api_key_here" | Out-File -FilePath "patent_agent_demo\private_openai_key" -Encoding UTF8

# 方法2: 设置环境变量 (临时)
set OPENAI_API_KEY=your_openai_api_key_here

# 方法3: 设置环境变量 (永久，需要管理员权限)
setx OPENAI_API_KEY "your_openai_api_key_here"

# 方法4: 在系统属性中设置 (推荐)
# 右键"此电脑" -> 属性 -> 高级系统设置 -> 环境变量 -> 新建
```

### 2. GLM API Key 配置

#### Linux/macOS 环境
```bash
# 方法1: 创建私钥文件
echo "your_glm_api_key_here" > patent_agent_demo/glm_api_key

# 方法2: 设置环境变量
export GLM_API_KEY="your_glm_api_key_here"

# 方法3: 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export GLM_API_KEY="your_glm_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows 环境
```cmd
# 方法1: 创建私钥文件 (PowerShell)
"your_glm_api_key_here" | Out-File -FilePath "patent_agent_demo\glm_api_key" -Encoding UTF8

# 方法2: 设置环境变量 (临时)
set GLM_API_KEY=your_glm_api_key_here

# 方法3: 设置环境变量 (永久)
setx GLM_API_KEY "your_glm_api_key_here"
```

### 3. 配置文件优先级

系统按以下优先级查找API key：

1. **环境变量** (最高优先级)
   - `OPENAI_API_KEY`
   - `GLM_API_KEY`

2. **私钥文件** (次优先级)
   - `patent_agent_demo/private_openai_key`
   - `patent_agent_demo/glm_api_key`

3. **默认配置** (最低优先级)

## 安装步骤

### 1. 创建虚拟环境

#### Linux/macOS
```bash
# 创建虚拟环境
python3 -m venv patent_env

# 激活虚拟环境
source patent_env/bin/activate

# 安装依赖
pip install -r patent_agent_demo/requirements.txt
pip install openai requests
```

#### Windows
```cmd
# 创建虚拟环境
python -m venv patent_env

# 激活虚拟环境
patent_env\Scripts\activate

# 安装依赖
pip install -r patent_agent_demo\requirements.txt
pip install openai requests
```

### 2. 配置API Keys

#### 推荐方式：环境变量
```bash
# Linux/macOS
export OPENAI_API_KEY="sk-proj-your-key-here"
export GLM_API_KEY="your-glm-key-here"

# Windows
set OPENAI_API_KEY=sk-proj-your-key-here
set GLM_API_KEY=your-glm-key-here
```

#### 备选方式：私钥文件
```bash
# Linux/macOS
echo "sk-proj-your-key-here" > patent_agent_demo/private_openai_key
echo "your-glm-key-here" > patent_agent_demo/glm_api_key

# Windows (PowerShell)
"sk-proj-your-key-here" | Out-File -FilePath "patent_agent_demo\private_openai_key" -Encoding UTF8
"your-glm-key-here" | Out-File -FilePath "patent_agent_demo\glm_api_key" -Encoding UTF8
```

### 3. 验证配置

```bash
# 测试降级功能
python test_fallback.py

# 测试DuckDuckGo搜索
python test_duckduckgo.py

# 测试完整系统
python -m patent_agent_demo.main --topic "测试主题" --description "测试描述"
```

## 使用方法

### 基本使用

```python
from patent_agent_demo.openai_client import OpenAIClient

# 初始化客户端 (自动检测环境变量或私钥文件)
client = OpenAIClient()

# 分析专利主题 (自动降级支持)
analysis = await client.analyze_patent_topic("主题", "描述")

# 搜索现有技术 (自动降级支持)
results = await client.search_prior_art("主题", ["关键词1", "关键词2"])

# 生成专利草稿 (自动降级支持)
draft = await client.generate_patent_draft("主题", "描述", analysis)
```

### 环境变量配置示例

#### Linux/macOS (.bashrc 或 .zshrc)
```bash
# OpenAI配置
export OPENAI_API_KEY="sk-proj-your-key-here"
export OPENAI_ORG_ID="org-your-org-id"  # 可选

# GLM配置
export GLM_API_KEY="your-glm-key-here"
export GLM_BASE_URL="http://localhost:8000"  # 可选，GLM服务地址

# 专利系统配置
export PATENT_TOPIC="默认专利主题"
export PATENT_DESC="默认专利描述"
```

#### Windows (系统环境变量)
```
变量名: OPENAI_API_KEY
变量值: sk-proj-your-key-here

变量名: GLM_API_KEY  
变量值: your-glm-key-here

变量名: PATENT_TOPIC
变量值: 默认专利主题
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

### API Key配置错误
```bash
# 检查环境变量
echo $OPENAI_API_KEY
echo $GLM_API_KEY

# 检查私钥文件
cat patent_agent_demo/private_openai_key
cat patent_agent_demo/glm_api_key
```

## 日志和监控

系统会记录以下信息：
- OpenAI API调用状态
- 降级触发原因
- GLM备用模型使用情况
- 搜索功能切换状态

### 日志位置
```bash
# 默认日志目录
/workspace/output/logs/  # Linux容器环境
./output/logs/           # 本地环境
```

## 故障排除

### 常见问题

1. **OpenAI API Key无效**
   ```bash
   # 验证API key格式
   echo $OPENAI_API_KEY | grep -E "^sk-proj-"
   
   # 测试API连接
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

2. **GLM降级失败**
   ```bash
   # 检查GLM服务状态
   curl http://localhost:8000/health  # 默认端口
   
   # 检查GLM API key
   echo $GLM_API_KEY
   ```

3. **DuckDuckGo搜索失败**
   ```bash
   # 检查网络连接
   ping api.duckduckgo.com
   
   # 检查requests库安装
   pip show requests
   ```

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
- 设置适当的文件权限

### 文件权限设置 (Linux/macOS)
```bash
# 设置私钥文件权限
chmod 600 patent_agent_demo/private_openai_key
chmod 600 patent_agent_demo/glm_api_key

# 设置目录权限
chmod 700 patent_agent_demo/
```

### 环境变量安全 (生产环境)
```bash
# 使用专门的配置文件
cat > .env << EOF
OPENAI_API_KEY=sk-proj-your-key-here
GLM_API_KEY=your-glm-key-here
EOF

# 加载环境变量
source .env
```