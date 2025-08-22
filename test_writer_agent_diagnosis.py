#!/usr/bin/env python3
"""
专门诊断Writer Agent为什么输出失败内容而不是正常专利内容
"""

import asyncio
import sys
import os
import logging
import json

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

# 设置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_writer_agent_step_by_step():
    """逐步测试Writer Agent的各个组件"""
    
    logger.info("🔍 开始逐步诊断Writer Agent...")
    
    try:
        # 1. 测试导入
        logger.info("📦 步骤1: 测试导入WriterAgentSimple...")
        try:
            from patent_agent_demo.agents.writer_agent_simple import WriterAgentSimple
            logger.info("✅ WriterAgentSimple导入成功")
        except ImportError as e:
            logger.error(f"❌ WriterAgentSimple导入失败: {e}")
            return False
        
        # 2. 测试OpenAI Client
        logger.info("🔧 步骤2: 测试OpenAI Client...")
        try:
            from patent_agent_demo.openai_client import OpenAIClient
            openai_client = OpenAIClient()
            logger.info(f"✅ OpenAI Client初始化成功")
            logger.info(f"   - OpenAI可用: {openai_client.openai_available}")
            logger.info(f"   - GLM回退可用: {openai_client.glm_client is not None}")
            
            # 测试OpenAI Client的状态
            if hasattr(openai_client, 'glm_client') and openai_client.glm_client:
                logger.info(f"   - GLM Client类型: {type(openai_client.glm_client)}")
                logger.info(f"   - GLM API Key: {'已设置' if openai_client.glm_client.api_key else '未设置'}")
        except Exception as e:
            logger.error(f"❌ OpenAI Client初始化失败: {e}")
            import traceback
            logger.error(f"📋 详细错误: {traceback.format_exc()}")
            return False
        
        # 3. 测试Writer Agent实例化
        logger.info("🔧 步骤3: 测试Writer Agent实例化...")
        try:
            writer_agent = WriterAgentSimple(test_mode=False)
            logger.info("✅ Writer Agent实例化成功")
            logger.info(f"   - Writer Agent类型: {type(writer_agent)}")
            logger.info(f"   - OpenAI Client: {type(writer_agent.openai_client)}")
        except Exception as e:
            logger.error(f"❌ Writer Agent实例化失败: {e}")
            import traceback
            logger.error(f"📋 详细错误: {traceback.format_exc()}")
            return False
        
        # 4. 测试Writer Agent启动
        logger.info("🚀 步骤4: 测试Writer Agent启动...")
        try:
            await writer_agent.start()
            logger.info("✅ Writer Agent启动成功")
        except Exception as e:
            logger.error(f"❌ Writer Agent启动失败: {e}")
            import traceback
            logger.error(f"📋 详细错误: {traceback.format_exc()}")
            return False
        
        # 5. 测试OpenAI Client的generate_patent_draft方法
        logger.info("🔧 步骤5: 测试OpenAI Client的generate_patent_draft方法...")
        try:
            # 创建模拟的PatentAnalysis
            from patent_agent_demo.google_a2a_client import PatentAnalysis
            mock_analysis = PatentAnalysis(
                novelty_score=8.5,
                inventive_step_score=7.8,
                industrial_applicability=True,
                prior_art_analysis=[],
                claim_analysis={},
                technical_merit={},
                commercial_potential="Medium to High",
                patentability_assessment="Strong",
                recommendations=["Improve claim specificity", "Add more technical details"]
            )
            
            # 测试OpenAI方法
            logger.info("   - 测试OpenAI方法...")
            try:
                result = await openai_client.generate_patent_draft(
                    "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法", 
                    "一种通过智能分层推理技术实现多参数工具自适应调用的系统", 
                    mock_analysis
                )
                logger.info(f"✅ OpenAI方法调用成功！")
                logger.info(f"   - 结果类型: {type(result)}")
                logger.info(f"   - 标题: {getattr(result, 'title', 'N/A')}")
                logger.info(f"   - 摘要: {getattr(result, 'abstract', 'N/A')[:100]}...")
                logger.info(f"   - 权利要求数量: {len(getattr(result, 'claims', []))}")
                return True
            except Exception as e:
                logger.error(f"❌ OpenAI方法调用失败: {e}")
                logger.info("   - 这是预期的，因为OpenAI API不可用，应该触发GLM回退")
                
                # 测试GLM回退
                logger.info("   - 测试GLM回退方法...")
                try:
                    result = await openai_client.glm_client.generate_patent_draft(
                        "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法", 
                        "一种通过智能分层推理技术实现多参数工具自适应调用的系统", 
                        mock_analysis
                    )
                    logger.info(f"✅ GLM回退方法调用成功！")
                    logger.info(f"   - 结果类型: {type(result)}")
                    logger.info(f"   - 标题: {getattr(result, 'title', 'N/A')}")
                    logger.info(f"   - 摘要: {getattr(result, 'abstract', 'N/A')[:100]}...")
                    logger.info(f"   - 权利要求数量: {len(getattr(result, 'claims', []))}")
                    return True
                except Exception as glm_error:
                    logger.error(f"❌ GLM回退方法也失败: {glm_error}")
                    logger.error(f"📋 GLM错误类型: {type(glm_error).__name__}")
                    import traceback
                    logger.error(f"📋 GLM详细错误: {traceback.format_exc()}")
                    return False
            
        except Exception as e:
            logger.error(f"❌ generate_patent_draft测试失败: {e}")
            import traceback
            logger.error(f"📋 详细错误: {traceback.format_exc()}")
            return False
        
    except Exception as e:
        logger.error(f"❌ 测试过程中发生异常: {e}")
        import traceback
        logger.error(f"📋 详细错误: {traceback.format_exc()}")
        return False

async def test_writer_agent_full_execution():
    """测试Writer Agent的完整执行流程"""
    
    logger.info("🔍 开始测试Writer Agent完整执行流程...")
    
    try:
        # 导入必要的组件
        from patent_agent_demo.agents.writer_agent_simple import WriterAgentSimple
        
        # 创建Writer Agent
        writer_agent = WriterAgentSimple(test_mode=False)
        await writer_agent.start()
        
        # 准备任务数据
        task_data = {
            "type": "patent_drafting",
            "topic": "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法",
            "description": "一种通过智能分层推理技术实现多参数工具自适应调用的系统",
            "previous_results": {
                "planning": {
                    "strategy": {
                        "key_innovation_areas": ["layered reasoning", "multi-parameter optimization", "context-aware processing"],
                        "novelty_score": 8.5,
                        "topic": "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
                    }
                },
                "search": {
                    "search_results": {
                        "results": [
                            {
                                "title": "智能参数推断系统",
                                "abstract": "一种基于机器学习的参数自动推断方法",
                                "relevance_score": 0.9
                            }
                        ],
                        "total_count": 1,
                        "search_topic": "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
                    }
                },
                "discussion": {
                    "core_strategy": {
                        "key_innovation_areas": ["layered reasoning", "multi-parameter optimization", "context-aware processing"],
                        "novelty_score": 8.5,
                        "topic": "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
                    },
                    "search_context": {
                        "results": [
                            {
                                "title": "智能参数推断系统",
                                "abstract": "一种基于机器学习的参数自动推断方法",
                                "relevance_score": 0.9
                            }
                        ],
                        "total_count": 1,
                        "search_topic": "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
                    }
                }
            },
            "workflow_id": "test_writer_agent",
            "test_mode": False
        }
        
        logger.info("📋 任务数据准备完成，开始执行...")
        logger.info(f"📋 任务数据: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
        
        # 执行任务
        result = await writer_agent.execute_task(task_data)
        
        logger.info(f"✅ Writer Agent执行完成！")
        logger.info(f"📊 执行结果: {result.success}")
        
        if result.success:
            logger.info(f"📄 生成的数据: {json.dumps(result.data, ensure_ascii=False, indent=2)}")
            
            # 检查专利草稿
            patent_draft = result.data.get("patent_draft")
            if patent_draft:
                logger.info(f"📄 专利草稿生成成功！")
                logger.info(f"   - 标题: {getattr(patent_draft, 'title', 'N/A')}")
                logger.info(f"   - 摘要: {getattr(patent_draft, 'abstract', 'N/A')[:200]}...")
                logger.info(f"   - 权利要求数量: {len(getattr(patent_draft, 'claims', []))}")
                logger.info(f"   - 详细描述长度: {len(getattr(patent_draft, 'detailed_description', ''))}")
            else:
                logger.warning(f"⚠️ 没有生成专利草稿")
                logger.info(f"📋 完整结果数据: {result.data}")
        else:
            logger.error(f"❌ Writer Agent执行失败: {result.error_message}")
            logger.error(f"📋 错误详情: {result.error_details if hasattr(result, 'error_details') else 'N/A'}")
        
        return result.success
        
    except Exception as e:
        logger.error(f"❌ Writer Agent完整执行测试失败: {e}")
        import traceback
        logger.error(f"📋 详细错误: {traceback.format_exc()}")
        return False

async def main():
    """主测试函数"""
    logger.info("🚀 开始Writer Agent诊断测试...")
    
    # 步骤1: 逐步测试
    logger.info("=" * 60)
    logger.info("步骤1: 逐步测试各个组件")
    logger.info("=" * 60)
    step_success = await test_writer_agent_step_by_step()
    
    if step_success:
        logger.info("✅ 逐步测试通过，开始完整执行测试...")
        
        # 步骤2: 完整执行测试
        logger.info("=" * 60)
        logger.info("步骤2: 完整执行测试")
        logger.info("=" * 60)
        full_success = await test_writer_agent_full_execution()
        
        if full_success:
            logger.info("🎉 所有测试通过！Writer Agent工作正常")
            return True
        else:
            logger.error("❌ 完整执行测试失败")
            return False
    else:
        logger.error("❌ 逐步测试失败，无法进行完整执行测试")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("✅ Writer Agent诊断测试成功")
        sys.exit(0)
    else:
        print("❌ Writer Agent诊断测试失败")
        sys.exit(1)