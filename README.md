# 专利多智能体撰写系统（GLM-4.5-flash 驱动）

本项目实现了一个面向专利交底书撰写的多智能体系统（Planner、Searcher、Discusser、Writer、Reviewer、Rewriter、Coordinator），通过“思考-讨论-撰写-审查-改写”的迭代流程，自动产出高质量的专利交底书草稿并导出 Markdown 文档。

- 模型：已强制使用 GLM-4.5-flash（ZHIPUAI），禁用 Google/Gemini 与任何回退模式
- 导出目录：`/workspace/output/`
- 日志目录：`/workspace/output/logs/`（每个智能体各有独立日志）

## 主要特性
- 多智能体工作流：规划 → 检索 → 讨论 → 撰写（按子章节拆分生成）→ 审查 → 改写（循环直到达标）
- 章节分治生成：具体实施方式按 A/B/C/D 子章节独立生成并合并，提高长文稳定性
- 质量与合规：审查器对字数、Mermaid、公式、伪代码等硬指标做结构化校验
- 可观测性：每个智能体独立日志，系统级日志；统计 API 调用与输出 token 近似值

## 环境要求
- Python 3.10+
- GLM API Key（ZHIPUAI）：通过环境变量或私有文件加载

## 安装
```bash
pip install -r requirements.txt
```

requirements.txt（最小化依赖）：
```text
rich>=13.7.0
```

## 配置 GLM API Key（必需）
支持以下任一方式：
- 环境变量：
  ```bash
  export ZHIPUAI_API_KEY="你的GLM_API_KEY"
  ```
- 私有文件（推荐）：将密钥写入以下任一文件（支持 `GLM_API_KEY=...` 或纯 Key 格式）：
  - `/workspace/glm_api_key`
  - `/workspace/.private/GLM_API_KEY`
  - `~/.private/GLM_API_KEY`
  
  示例：
  ```bash
  mkdir -p /workspace/.private
  echo 'GLM_API_KEY=你的GLM_API_KEY' > /workspace/.private/GLM_API_KEY
  ```

## 快速运行
- 后台长流程（推荐）：
  ```bash
  PATENT_TOPIC="证据图增强的检索增强RAG系统" \
  PATENT_DESC="构建证据图以提升RAG可验证性与准确性" \
  python3 /workspace/run_patent_workflow.py | cat
  ```
  Windows 等价命令：
  - PowerShell
    ```powershell
    $env:PATENT_TOPIC="证据图增强的检索增强RAG系统"; $env:PATENT_DESC="构建证据图以提升RAG可验证性与准确性"; python .\run_patent_workflow.py
    ```
  - CMD
    ```cmd
    set "PATENT_TOPIC=证据图增强的检索增强RAG系统" && set "PATENT_DESC=构建证据图以提升RAG可验证性与准确性" && python run_patent_workflow.py
    ```
  完成后导出到：`/workspace/output/证据图增强的检索增强RAG系统_<workflow_id前8位>.md`

- 单次脚本（示例）：
  ```bash
  python3 - << 'PY'
  import asyncio
  from patent_agent_demo.patent_agent_system import PatentAgentSystem
  async def run():
      system = PatentAgentSystem()
      await system.start()
      await system.develop_patent(
          topic="证据图增强的检索增强RAG系统",
          description="构建证据图以提升RAG可验证性与准确性"
      )
      await system.stop()
  asyncio.run(run())
  PY
  ```

## 监控日志与进度
```bash
# 协调器推进
tail -f /workspace/output/logs/coordinator_agent.log | cat
# 撰写子章节进度
tail -f /workspace/output/logs/writer_agent.log | cat
# 系统级事件
tail -f /workspace/output/logs/system.log | cat
```

## 目录结构（核心）
```text
patent_agent_demo/
  agents/                 # 各智能体实现
  message_bus.py          # 消息总线（原 fastmcp_config.py）
  google_a2a_client.py    # A2A 客户端工厂（已强制GLM）
  glm_client.py           # GLM-4.5-flash HTTP 客户端
  telemetry.py            # API 调用统计与日志代理
run_patent_workflow.py    # 后台长流程运行器
```

## 常见问题
- 报错 “ZHIPUAI_API_KEY is required ...”：未正确配置 GLM Key，按上文配置环境变量或私有文件
- 导出文件未出现：查看协调器、撰写者日志；等待撰写/审查阶段结束；确保 `/workspace/output/` 可写
- 内容过长超时：系统已将章节分治并提升了 GLM 请求超时；如需进一步加大可在 `glm_client.py` 调整 `timeout`

## 许可证
本仓库仅用于演示用途，请根据实际业务与法律合规要求使用。
