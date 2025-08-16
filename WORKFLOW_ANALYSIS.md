# 多智能体工作流程分析

## 🔍 当前工作流程架构

### 1. 智能体组成
```
CoordinatorAgent (协调器)
├── PlannerAgent (规划器)
├── SearcherAgent (检索器)
├── DiscusserAgent (讨论器)
├── WriterAgent (撰写器)
├── ReviewerAgent (审查器)
└── RewriterAgent (重写器)
```

### 2. 工作流程阶段
```
1. Planning & Strategy (规划策略)
2. Prior Art Search (现有技术检索)
3. Innovation Discussion (创新讨论)
4. Patent Drafting (专利撰写)
5. Quality Review (质量审查)
6. Final Rewrite (最终重写)
```

## 📋 任务安排机制

### 1. 协调器任务分发流程
```python
# CoordinatorAgent._execute_workflow_stage()
async def _execute_workflow_stage(self, workflow_id: str, stage_index: int):
    # 1. 获取工作流和阶段信息
    workflow = self.active_workflows.get(workflow_id)
    stage = workflow.stages[stage_index]
    
    # 2. 获取上下文数据
    context_data = await context_manager.get_context_for_agent(
        workflow_id, 
        stage.agent_name,
        self._get_context_types_for_stage(stage.stage_name)
    )
    
    # 3. 构建任务内容
    task_content = {
        "task": {
            "id": f"{workflow_id}_stage_{stage_index}",
            "type": task_type,
            "workflow_id": workflow_id,
            "stage_index": stage_index,
            "topic": workflow.topic,
            "description": workflow.description,
            "previous_results": workflow.results,
            "context": context_data  # 上下文数据注入
        }
    }
    
    # 4. 发送消息给目标智能体
    await self.send_message(
        recipient=stage.agent_name,
        message_type=MessageType.COORDINATION,
        content=task_content,
        priority=5
    )
```

### 2. 智能体任务执行流程
```python
# BaseAgent._handle_coordination_message()
async def _handle_coordination_message(self, message: Message):
    # 1. 提取任务数据
    task_data = message.content.get("task", {})
    task_type = task_data.get("type")
    
    # 2. 检查能力匹配
    if task_type in self.capabilities:
        # 3. 执行任务
        await self._execute_task(task_data)
    else:
        logger.warning(f"Agent {self.name} cannot handle task type: {task_type}")

# BaseAgent._execute_task()
async def _execute_task(self, task_data: Dict[str, Any]):
    # 1. 提取上下文信息
    context_data = task_data.get("context", {})
    workflow_id = task_data.get("workflow_id")
    
    # 2. 存储上下文
    self.current_context = context_data
    self.current_workflow_id = workflow_id
    
    # 3. 执行具体任务
    result = await self.execute_task(task_data)
    
    # 4. 发送完成消息
    completion_message = Message(
        type=MessageType.STATUS,
        sender=self.name,
        recipient="coordinator_agent",
        content={
            "task_id": task_id,
            "status": "completed",
            "result": result.data,
            "success": result.success
        }
    )
    await self.broker.send_message(completion_message)
```

## 🔄 上下文管理器集成

### 1. 上下文初始化
```python
# CoordinatorAgent._start_patent_workflow()
# 初始化上下文
theme_definition = await context_manager.initialize_workflow_context(
    workflow_id, topic, description
)
```

### 2. 上下文传递
```python
# 为每个阶段获取相关上下文
context_data = await context_manager.get_context_for_agent(
    workflow_id, 
    stage.agent_name,
    self._get_context_types_for_stage(stage.stage_name)
)
```

### 3. 上下文验证和更新
```python
# 阶段完成后验证和更新上下文
await self._validate_and_update_context(workflow_id, stage_index, result, stage.stage_name)
```

## ⚠️ 发现的问题

### 1. 审查和重写智能体可能没有执行的原因

#### 问题1: 迭代循环逻辑复杂
```python
# CoordinatorAgent._handle_stage_completion()
if stage_name == "Patent Drafting":
    # 启动审查迭代
    await self._start_review_iteration(workflow_id)
    return

if stage_name == "Quality Review":
    # 检查是否需要重写
    if (compliance in ("needs_major_revision", "needs_minor_revision", "non_compliant")
        or outcome in ("needs_revision", "major_revision_required")
        or (quality_score is not None and quality_score < iteration.get("target_score", 8.8))):
        await self._trigger_rewrite_cycle(workflow_id, stage_index)
        return

if stage_name == "Final Rewrite":
    # 重写完成后重新讨论和审查
    await self._post_rewrite_next_steps(workflow_id, stage_index)
    return
```

#### 问题2: 消息传递可能失败
- 智能体可能没有正确注册到消息总线
- 消息队列可能没有正确处理
- 任务ID格式可能不匹配

#### 问题3: 智能体能力不匹配
```python
# ReviewerAgent capabilities
capabilities=["patent_review", "quality_assessment", "compliance_checking", "feedback_generation"]

# RewriterAgent capabilities  
capabilities=["patent_rewriting", "patent_rewrite", "feedback_implementation", "quality_improvement", "compliance_optimization"]
```

### 2. 上下文管理器集成问题

#### 问题1: 上下文数据可能为空
- 如果上下文管理器初始化失败，context_data可能为空
- 智能体可能无法正确使用上下文信息

#### 问题2: 上下文验证可能过于严格
- 验证逻辑可能阻止了正常的流程推进
- 一致性检查可能过于严格

## 🔧 修复建议

### 1. 简化迭代循环逻辑
```python
async def _handle_stage_completion(self, workflow_id: str, stage_index: int, result: Dict[str, Any]):
    """简化的阶段完成处理逻辑"""
    try:
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        stage = workflow.stages[stage_index]
        stage.status = "completed"
        stage.end_time = time.time()
        stage.result = result
        workflow.results[f"stage_{stage_index}"] = {"result": result}
        
        # 更新上下文
        await self._validate_and_update_context(workflow_id, stage_index, result, stage.stage_name)
        
        # 简化的流程控制
        if stage.stage_name == "Patent Drafting":
            # 直接进入审查阶段
            await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Quality Review"))
        elif stage.stage_name == "Quality Review":
            # 检查是否需要重写
            needs_rewrite = self._check_if_rewrite_needed(result)
            if needs_rewrite:
                await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Final Rewrite"))
            else:
                # 完成工作流
                await self._complete_workflow(workflow_id)
        elif stage.stage_name == "Final Rewrite":
            # 重写完成后重新审查
            await self._execute_workflow_stage(workflow_id, self._find_stage_index(workflow, "Quality Review"))
        else:
            # 继续下一个阶段
            if stage_index < len(workflow.stages) - 1:
                await self._execute_workflow_stage(workflow_id, stage_index + 1)
            else:
                await self._complete_workflow(workflow_id)
                
    except Exception as e:
        logger.error(f"Error handling stage completion: {e}")
        await self._handle_stage_error(workflow_id, stage_index, str(e))

def _check_if_rewrite_needed(self, result: Dict[str, Any]) -> bool:
    """检查是否需要重写"""
    # 简化的检查逻辑
    quality_score = result.get("quality_score", 0)
    compliance_status = result.get("compliance_status", "unknown")
    
    return (quality_score < 8.0 or 
            compliance_status in ["needs_major_revision", "needs_minor_revision", "non_compliant"])
```

### 2. 增强消息传递可靠性
```python
async def _execute_workflow_stage(self, workflow_id: str, stage_index: int):
    """增强的工作流阶段执行"""
    try:
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return
            
        if stage_index >= len(workflow.stages):
            logger.info(f"Workflow {workflow_id} completed all stages")
            await self._complete_workflow(workflow_id)
            return
            
        stage = workflow.stages[stage_index]
        stage.status = "running"
        stage.start_time = time.time()
        
        logger.info(f"Executing stage {stage_index}: {stage.stage_name} using {stage.agent_name}")
        
        # 检查智能体是否可用
        if not await self._check_agent_availability(stage.agent_name):
            logger.error(f"Agent {stage.agent_name} is not available")
            await self._handle_stage_error(workflow_id, stage_index, f"Agent {stage.agent_name} not available")
            return
        
        # 获取上下文数据
        context_data = await context_manager.get_context_for_agent(
            workflow_id, 
            stage.agent_name,
            self._get_context_types_for_stage(stage.stage_name)
        )
        
        # 构建任务内容
        task_content = self._build_task_content(workflow, stage_index, context_data)
        
        # 发送消息并等待确认
        message_sent = await self._send_task_message(stage.agent_name, task_content)
        if not message_sent:
            logger.error(f"Failed to send task to {stage.agent_name}")
            await self._handle_stage_error(workflow_id, stage_index, f"Failed to send task to {stage.agent_name}")
            return
            
        workflow.current_stage = stage_index
        workflow.overall_status = "running"
        
    except Exception as e:
        logger.error(f"Error executing workflow stage: {e}")
        await self._handle_stage_error(workflow_id, stage_index, str(e))

async def _check_agent_availability(self, agent_name: str) -> bool:
    """检查智能体是否可用"""
    try:
        agent_info = self.broker.agents.get(agent_name)
        if not agent_info:
            return False
        return agent_info.status != AgentStatus.OFFLINE
    except Exception as e:
        logger.error(f"Error checking agent availability: {e}")
        return False

async def _send_task_message(self, agent_name: str, task_content: Dict[str, Any]) -> bool:
    """发送任务消息并等待确认"""
    try:
        message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.COORDINATION,
            sender=self.name,
            recipient=agent_name,
            content=task_content,
            timestamp=time.time(),
            priority=5
        )
        
        await self.broker.send_message(message)
        
        # 等待一小段时间确认消息被接收
        await asyncio.sleep(0.1)
        
        return True
    except Exception as e:
        logger.error(f"Error sending task message: {e}")
        return False
```

### 3. 增强上下文管理器集成
```python
async def _validate_and_update_context(self, workflow_id: str, stage_index: int, result: Dict[str, Any], stage_name: str):
    """增强的上下文验证和更新"""
    try:
        logger.info(f"Validating and updating context for stage {stage_name}")
        
        # 提取输出文本
        output_text = self._extract_output_text(result, stage_name)
        
        if output_text:
            # 验证输出一致性
            validation_result = await context_manager.validate_agent_output(
                workflow_id, f"stage_{stage_index}", output_text, "general"
            )
            
            if not validation_result["is_consistent"]:
                logger.warning(f"Context consistency issues in {stage_name}: {validation_result['issues']}")
            else:
                logger.info(f"Context validation passed for {stage_name}")
            
            # 提取并添加新的上下文项
            await self._extract_context_from_result(workflow_id, stage_index, result, stage_name)
            
    except Exception as e:
        logger.error(f"Error validating and updating context: {e}")
        # 不阻止流程继续，只记录错误

def _extract_output_text(self, result: Dict[str, Any], stage_name: str) -> str:
    """提取输出文本用于验证"""
    try:
        if stage_name == "Patent Drafting":
            return result.get("patent_draft", {}).get("title", "")
        elif stage_name == "Quality Review":
            return result.get("feedback", {}).get("summary", "")
        elif stage_name == "Final Rewrite":
            return result.get("improved_draft", {}).get("title", "")
        else:
            return str(result)
    except Exception:
        return str(result)
```

## 📊 监控和调试建议

### 1. 添加详细的日志记录
```python
# 在每个关键步骤添加日志
logger.info(f"Stage {stage_index} ({stage.stage_name}) started")
logger.info(f"Context data: {context_data}")
logger.info(f"Task content: {task_content}")
logger.info(f"Message sent to {stage.agent_name}")
```

### 2. 添加工作流状态监控
```python
async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
    """获取工作流状态"""
    workflow = self.active_workflows.get(workflow_id)
    if not workflow:
        return {"status": "not_found"}
    
    return {
        "workflow_id": workflow_id,
        "current_stage": workflow.current_stage,
        "current_stage_name": workflow.stages[workflow.current_stage].stage_name if workflow.stages else None,
        "overall_status": workflow.overall_status,
        "stages": [
            {
                "name": stage.stage_name,
                "agent": stage.agent_name,
                "status": stage.status,
                "start_time": stage.start_time,
                "end_time": stage.end_time,
                "error": stage.error
            }
            for stage in workflow.stages
        ],
        "results": workflow.results
    }
```

### 3. 添加智能体状态监控
```python
async def get_all_agents_status(self) -> Dict[str, Any]:
    """获取所有智能体状态"""
    return {
        agent_name: {
            "status": agent_info.status.value,
            "capabilities": agent_info.capabilities,
            "current_task": agent_info.current_task,
            "last_activity": agent_info.last_activity
        }
        for agent_name, agent_info in self.broker.agents.items()
    }
```

## 🎯 总结

当前的多智能体系统架构是合理的，但存在以下需要修复的问题：

1. **迭代循环逻辑过于复杂** - 需要简化审查和重写的触发条件
2. **消息传递可靠性不足** - 需要增强消息发送和接收的可靠性检查
3. **上下文管理器集成不够健壮** - 需要增强错误处理和容错机制
4. **监控和调试能力不足** - 需要添加更详细的状态监控和日志记录

建议按照上述修复建议进行改进，特别是简化迭代循环逻辑和增强消息传递可靠性，这样可以确保审查和重写智能体能够正常执行。