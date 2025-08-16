#!/usr/bin/env python3
"""
测试API调用速度
"""

import asyncio
import sys
import os
import logging
import time

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patent_agent_demo'))

from patent_agent_demo.openai_client import OpenAIClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_api_speed():
    """测试API调用速度"""
    try:
        logger.info("🚀 开始测试API调用速度")
        
        # 创建客户端
        client = OpenAIClient()
        logger.info("✅ 客户端创建成功")
        
        # 测试数据
        topic = "基于智能分层推理的多参数工具自适应调用系统"
        description = "一种通过智能分层推理技术实现多参数工具自适应调用的系统"
        
        # 测试analyze_patent_topic
        logger.info("🔧 测试 analyze_patent_topic...")
        start_time = time.time()
        
        try:
            analysis = await client.analyze_patent_topic(topic, description)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(f"✅ analyze_patent_topic 成功")
            logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
            logger.info(f"   新颖性评分: {analysis.novelty_score}")
            logger.info(f"   创造性评分: {analysis.inventive_step_score}")
            
        except Exception as e:
            logger.error(f"❌ analyze_patent_topic 失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试_generate_response
        logger.info("🔧 测试 _generate_response...")
        start_time = time.time()
        
        try:
            prompt = f"请分析专利主题'{topic}'的创新领域"
            response = await client._generate_response(prompt)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(f"✅ _generate_response 成功")
            logger.info(f"⏱️ 执行时间: {execution_time:.2f}秒")
            logger.info(f"   响应长度: {len(response)} 字符")
            
        except Exception as e:
            logger.error(f"❌ _generate_response 失败: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("✅ API速度测试完成")
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    try:
        await test_api_speed()
    except Exception as e:
        logger.error(f"❌ 主函数出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())