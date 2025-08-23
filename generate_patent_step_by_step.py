#!/usr/bin/env python3
"""
分步骤生成专利内容，避免GLM API并发问题
"""

import asyncio
import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

async def generate_patent_step_by_step():
    """分步骤生成专利内容"""
    
    try:
        print("🚀 开始分步骤生成专利：基于语义理解的复杂函数参数智能推断与分层调用重试优化方法")
        
        # 直接使用GLM Client
        from patent_agent_demo.glm_client import GLMA2AClient
        
        client = GLMA2AClient()
        
        # 创建输出目录
        output_dir = "./output/progress/基于语义理解的复杂函数参数智能推断与分层调用重试优化方法_step_by_step"
        os.makedirs(output_dir, exist_ok=True)
        
        print("📁 输出目录创建成功")
        
        # 1. 生成专利大纲
        print("📝 步骤1: 生成专利大纲...")
        print("⏳ 等待30秒，让GLM API恢复...")
        await asyncio.sleep(30)
        
        outline_prompt = """
请为以下专利主题设计详细的专利大纲：

专利主题：基于语义理解的复杂函数参数智能推断与分层调用重试优化方法

要求：
1. 包含完整的专利章节结构
2. 重点突出语义理解、参数推断、分层调用、重试优化等核心技术
3. 每个章节要有具体的内容要点
4. 包含技术实现细节和算法描述

请按照以下格式输出：
# 专利大纲

## 第一章 术语定义
[具体内容]

## 第二章 技术领域
[具体内容]

## 第三章 背景技术
[具体内容]

## 第四章 发明内容
[具体内容]

## 第五章 具体实施方式
[具体内容]

## 第六章 权利要求
[具体内容]
"""
        
        outline = await client._generate_response(outline_prompt)
        
        # 保存大纲
        with open(f"{output_dir}/01_outline.md", "w", encoding="utf-8") as f:
            f.write("# 专利大纲\n\n")
            f.write(outline)
        
        print("✅ 专利大纲生成完成")
        
        # 2. 生成背景技术
        print("📝 步骤2: 生成背景技术...")
        print("⏳ 等待60秒，让GLM API恢复...")
        await asyncio.sleep(60)
        
        background_prompt = """
请为以下专利主题撰写详细的背景技术：

专利主题：基于语义理解的复杂函数参数智能推断与分层调用重试优化方法

要求：
1. 描述技术领域和现有技术方案
2. 分析现有技术的缺点和问题
3. 说明本发明的技术背景和必要性
4. 字数≥800字，内容专业具体

请按照以下格式输出：
# 背景技术

## 技术领域
[具体内容]

## 现有技术方案
[具体内容]

## 现有技术缺点
[具体内容]

## 技术问题
[具体内容]
"""
        
        background = await client._generate_response(background_prompt)
        
        # 保存背景技术
        with open(f"{output_dir}/02_background.md", "w", encoding="utf-8") as f:
            f.write("# 背景技术\n\n")
            f.write(background)
        
        print("✅ 背景技术生成完成")
        
        # 3. 生成发明内容总述
        print("📝 步骤3: 生成发明内容总述...")
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
        
        summary = await client._generate_response(summary_prompt)
        
        # 保存发明内容总述
        with open(f"{output_dir}/03_summary.md", "w", encoding="utf-8") as f:
            f.write("# 发明内容总述\n\n")
            f.write(summary)
        
        print("✅ 发明内容总述生成完成")
        
        # 4. 生成具体实施方式
        print("📝 步骤4: 生成具体实施方式...")
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
        
        implementation = await client._generate_response(implementation_prompt)
        
        # 保存具体实施方式
        with open(f"{output_dir}/04_implementation.md", "w", encoding="utf-8") as f:
            f.write("# 具体实施方式\n\n")
            f.write(implementation)
        
        print("✅ 具体实施方式生成完成")
        
        # 5. 生成权利要求
        print("📝 步骤5: 生成权利要求...")
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
        
        claims = await client._generate_response(claims_prompt)
        
        # 保存权利要求
        with open(f"{output_dir}/05_claims.md", "w", encoding="utf-8") as f:
            f.write("# 权利要求\n\n")
            f.write(claims)
        
        print("✅ 权利要求生成完成")
        
        # 6. 复制之前生成的标题和摘要
        print("📝 步骤6: 复制标题和摘要...")
        if os.path.exists("./output/progress/基于语义理解的复杂函数参数智能推断与分层调用重试优化方法_urllib/00_title_abstract.md"):
            with open("./output/progress/基于语义理解的复杂函数参数智能推断与分层调用重试优化方法_urllib/00_title_abstract.md", "r", encoding="utf-8") as src:
                content = src.read()
            with open(f"{output_dir}/00_title_abstract.md", "w", encoding="utf-8") as dst:
                dst.write(content)
            print("✅ 标题和摘要复制完成")
        
        # 7. 生成进度文件
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
采用分步骤生成策略，每个章节之间等待足够时间，避免GLM API并发限制问题。
"""
        
        with open(f"{output_dir}/progress.md", "w", encoding="utf-8") as f:
            f.write(progress_content)
        
        print("✅ 进度文件生成完成")
        
        print(f"\n🎉 专利内容生成完成！")
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
        print(f"❌ 生成专利失败: {e}")
        import traceback
        print(f"📋 详细错误: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🔍 开始分步骤生成专利内容...")
    success = asyncio.run(generate_patent_step_by_step())
    if success:
        print("✅ 专利生成成功！")
        sys.exit(0)
    else:
        print("❌ 专利生成失败！")
        sys.exit(1)