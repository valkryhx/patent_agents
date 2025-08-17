# 待删除文件说明

## 为什么这些文件被移动到这里

### main.py
**问题分析：**
1. **端口冲突**：试图在端口8000启动，与`unified_service.py`冲突
2. **错误的架构假设**：假设有6个独立的智能体服务在不同端口运行
3. **重复功能**：实现了与`unified_service.py`重复的API接口
4. **无法正常工作**：因为智能体服务实际上都在`unified_service.py`中

**解决方案：**
- 已将`main.py`中的专利相关API接口迁移到`unified_service.py`
- `unified_service.py`现在是唯一的正确服务入口点
- 所有功能都整合在一个服务中，避免了端口冲突和架构问题

## 迁移的功能

以下API接口已从`main.py`迁移到`unified_service.py`：

- `POST /patent/generate` - 启动专利生成工作流
- `GET /patent/{workflow_id}/status` - 获取工作流状态
- `GET /patent/{workflow_id}/results` - 获取工作流结果
- `POST /patent/{workflow_id}/restart` - 重启工作流
- `DELETE /patent/{workflow_id}` - 删除工作流
- `GET /patents` - 列出所有专利工作流

## 当前正确的服务

**使用 `unified_service.py` 启动服务：**
```bash
python3 unified_service.py
```

**服务将在 http://localhost:8000 启动，包含：**
- 协调器服务
- 所有6个智能体服务
- 专利相关的API接口
- 测试模式支持

## 注意事项

1. **不要使用 `main.py`** - 它会导致端口冲突和架构问题
2. **使用 `unified_service.py`** - 这是唯一正确的服务入口点
3. **所有功能都已整合** - 不需要启动多个服务
4. **测试模式支持** - 通过`/test-mode`端点控制

## 清理建议

这些文件可以安全删除，因为：
- 功能已完全迁移到`unified_service.py`
- 保留它们会造成混淆
- 它们包含错误的架构假设