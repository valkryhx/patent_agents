#!/usr/bin/env python3
"""
生成剩余的专利章节
"""

import asyncio
import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def generate_remaining_sections():
    """生成剩余的专利章节"""
    
    try:
        print("🚀 开始生成剩余的专利章节...")
        
        # 直接使用GLM Client
        from patent_agent_demo.glm_client import GLMA2AClient
        
        client = GLMA2AClient()
        
        # 输出目录
        output_dir = "./output/progress/基于语义理解的复杂函数参数智能推断与分层调用重试优化方法_conservative"
        
        print("📁 使用输出目录:", output_dir)
        
        # 1. 生成发明内容总述
        print("📝 步骤1: 生成发明内容总述...")
        print("⏳ 等待60秒，让GLM API恢复...")
        await asyncio.sleep(60)
        
        summary_prompt = """
请为以下专利主题撰写发明内容总述：

专利主题：基于语义理解的复杂函数参数智能推断与分层调用重试优化方法

要求：
1. 详细描述核心创新点和技术方案
2. 说明系统架构和关键技术
3. 突出技术优势和创新性
4. 字数≥800字，内容专业具体

请按照以下格式输出：
# 发明内容总述

## 核心创新点
[具体内容]

## 技术方案
[具体内容]

## 系统架构
[具体内容]

## 技术优势
[具体内容]
"""
        
        print("🔄 正在生成发明内容总述...")
        summary = await client._generate_response(summary_prompt)
        
        # 保存发明内容总述
        with open(f"{output_dir}/03_summary.md", "w", encoding="utf-8") as f:
            f.write("# 发明内容总述\n\n")
            f.write(summary)
        
        print("✅ 发明内容总述生成完成")
        
        # 2. 生成具体实施方式
        print("📝 步骤2: 生成具体实施方式...")
        print("⏳ 等待60秒，让GLM API恢复...")
        await asyncio.sleep(60)
        
        implementation_prompt = """
请为以下专利主题撰写具体实施方式：

专利主题：基于语义理解的复杂函数参数智能推断与分层调用重试优化方法

要求：
1. 详细描述技术实现方案
2. 包含算法流程和伪代码
3. 说明关键模块的功能和实现
4. 字数≥1000字，内容专业具体

请按照以下格式输出：
# 具体实施方式

## 5.1 系统整体架构
[具体内容]

## 5.2 语义理解模块
[具体内容]

## 5.3 参数推断引擎
[具体内容]

## 5.4 分层调用机制
[具体内容]

## 5.5 重试优化策略
[具体内容]
"""
        
        print("🔄 正在生成具体实施方式...")
        implementation = await client._generate_response(implementation_prompt)
        
        # 保存具体实施方式
        with open(f"{output_dir}/04_implementation.md", "w", encoding="utf-8") as f:
            f.write("# 具体实施方式\n\n")
            f.write(implementation)
        
        print("✅ 具体实施方式生成完成")
        
        # 3. 生成权利要求
        print("📝 步骤3: 生成权利要求...")
        print("⏳ 等待60秒，让GLM API恢复...")
        await asyncio.sleep(60)
        
        claims_prompt = """
请为以下专利主题撰写权利要求：

专利主题：基于语义理解的复杂函数参数智能推断与分层调用重试优化方法

要求：
1. 生成至少5个权利要求
2. 权利要求要层次分明，从独立权利要求到从属权利要求
3. 覆盖核心技术特征：语义理解、参数推断、分层调用、重试优化
4. 符合专利法要求，保护范围合理

请按照以下格式输出：
# 权利要求

## 权利要求1
[独立权利要求内容]

## 权利要求2
[从属权利要求内容]

## 权利要求3
[从属权利要求内容]

## 权利要求4
[从属权利要求内容]

## 权利要求5
[从属权利要求内容]
"""
        
        print("🔄 正在生成权利要求...")
        claims = await client._generate_response(claims_prompt)
        
        # 保存权利要求
        with open(f"{output_dir}/05_claims.md", "w", encoding="utf-8") as f:
            f.write("# 权利要求\n\n")
            f.write(claims)
        
        print("✅ 权利要求生成完成")
        
        # 4. 生成进度文件
        progress_content = f"""# 专利撰写进度

## 专利主题
基于语义理解的复杂函数参数智能推断与分层调用重试优化方法

## 生成时间
{time.strftime('%Y-%m-%d %H:%M:%S')}

## 已完成章节
1. ✅ 专利标题和摘要 (00_title_abstract.md)
2. ✅ 专利大纲 (01_outline.md)
3. ✅ 背景技术 (02_background.md)
4. ✅ 发明内容总述 (03_summary.md)
5. ✅ 具体实施方式 (04_implementation.md)
6. ✅ 权利要求 (05_claims.md)

## 输出目录
{output_dir}

## 技术特点
- 语义理解：基于自然语言处理技术理解函数参数语义
- 智能推断：使用机器学习算法自动推断最优参数
- 分层调用：实现多层次的函数调用机制
- 重试优化：智能重试策略提高系统稳定性

## 应用前景
该系统可广泛应用于软件开发、API集成、微服务架构、智能运维等领域，显著提高系统参数配置的准确性和系统运行的稳定性。

## 生成策略
采用分步骤生成策略，每个章节之间等待足够时间，确保GLM API完全恢复，避免并发限制问题。
"""
        
        with open(f"{output_dir}/progress.md", "w", encoding="utf-8") as f:
            f.write(progress_content)
        
        print("✅ 进度文件生成完成")
        
        print(f"\n🎉 剩余章节生成完成！")
        print(f"📁 输出目录: {output_dir}")
        print(f"📄 生成文件:")
        print(f"   - 00_title_abstract.md (标题和摘要)")
        print(f"   - 01_outline.md (专利大纲)")
        print(f"   - 02_background.md (背景技术)")
        print(f"   - 03_summary.md (发明内容总述)")
        print(f"   - 04_implementation.md (具体实施方式)")
        print(f"   - 05_claims.md (权利要求)")
        print(f"   - progress.md (进度文件)")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成剩余章节失败: {e}")
        import traceback
        print(f"📋 详细错误: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔍 开始生成剩余的专利章节...")
    success = asyncio.run(generate_remaining_sections())
    if success:
        print("✅ 剩余章节生成成功！")
        sys.exit(0)
    else:
        print("❌ 剩余章节生成失败！")
        sys.exit(1)