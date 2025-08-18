#!/usr/bin/env python3
"""
简化版增强审核智能体测试
"""

import asyncio
import logging
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDuckDuckGoSearcher:
    """简化版DuckDuckGo检索器"""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.session = None
    
    async def _get_session(self):
        """获取aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """执行检索"""
        try:
            session = await self._get_session()
            
            # 构建检索参数
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status in [200, 202]:  # DuckDuckGo API返回202是正常的
                    # DuckDuckGo返回的Content-Type是application/x-javascript，需要手动解析
                    text = await response.text()
                    try:
                        data = json.loads(text)
                        return self._parse_search_results(data, max_results)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析失败: {e}")
                        return []
                else:
                    logger.error(f"DuckDuckGo检索失败: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"DuckDuckGo检索异常: {e}")
            return []
    
    def _parse_search_results(self, data: Dict, max_results: int) -> List[Dict[str, Any]]:
        """解析检索结果"""
        results = []
        
        # 解析相关主题
        if "RelatedTopics" in data:
            for topic in data["RelatedTopics"][:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "content": topic.get("Text", ""),
                        "source": "DuckDuckGo RelatedTopics"
                    })
        
        # 解析摘要
        if "Abstract" in data and data["Abstract"]:
            results.append({
                "title": data.get("AbstractText", ""),
                "url": data.get("AbstractURL", ""),
                "content": data["Abstract"],
                "source": "DuckDuckGo Abstract"
            })
        
        # 解析Infobox信息
        if "Infobox" in data and data["Infobox"]:
            infobox = data["Infobox"]
            if "content" in infobox:
                for item in infobox["content"][:max_results]:
                    if isinstance(item, dict) and "label" in item and "value" in item:
                        results.append({
                            "title": f"{item['label']}: {item['value']}",
                            "url": "",
                            "content": f"{item['label']}: {item['value']}",
                            "source": "DuckDuckGo Infobox"
                        })
        
        # 解析Results
        if "Results" in data and data["Results"]:
            for result in data["Results"][:max_results]:
                if isinstance(result, dict) and "Text" in result:
                    results.append({
                        "title": result.get("Text", ""),
                        "url": result.get("FirstURL", ""),
                        "content": result.get("Text", ""),
                        "source": "DuckDuckGo Results"
                    })
        
        return results[:max_results]
    
    async def close(self):
        """关闭session"""
        if self.session:
            await self.session.close()

class SimpleEnhancedReviewer:
    """简化版增强审核智能体"""
    
    def __init__(self):
        self.searcher = SimpleDuckDuckGoSearcher()
    
    async def comprehensive_review(self, 
                                 chapter_3_content: str, 
                                 chapter_4_content: str, 
                                 chapter_5_content: str,
                                 topic: str,
                                 search_results: Dict) -> Dict[str, Any]:
        """综合审核：结合前三章内容，深度检索，提出批判性意见"""
        
        try:
            # 1. 深度检索第五章相关内容
            chapter_5_keywords = self._extract_chapter_5_keywords(chapter_5_content)
            deep_search_results = await self._deep_search_chapter_5(chapter_5_keywords, topic)
            
            # 2. 三性审核（结合前三章内容）
            novelty_analysis = self._analyze_novelty(chapter_3_content, chapter_5_content, deep_search_results)
            inventiveness_analysis = self._analyze_inventiveness(chapter_4_content, chapter_5_content, deep_search_results)
            utility_analysis = self._analyze_utility(chapter_5_content, deep_search_results)
            
            # 3. 批判性分析
            critical_analysis = self._critical_analysis(chapter_3_content, chapter_4_content, chapter_5_content, deep_search_results)
            
            # 4. 改进建议
            improvement_suggestions = self._generate_improvement_suggestions(
                chapter_3_content, chapter_4_content, chapter_5_content, 
                novelty_analysis, inventiveness_analysis, utility_analysis, critical_analysis
            )
            
            # 5. 总体评估
            overall_assessment = self._generate_overall_assessment(
                novelty_analysis, inventiveness_analysis, utility_analysis, critical_analysis
            )
            
            return {
                "deep_search_results": deep_search_results,
                "novelty_analysis": novelty_analysis,
                "inventiveness_analysis": inventiveness_analysis,
                "utility_analysis": utility_analysis,
                "critical_analysis": critical_analysis,
                "improvement_suggestions": improvement_suggestions,
                "overall_assessment": overall_assessment
            }
            
        except Exception as e:
            logger.error(f"综合审核失败: {e}")
            return self._generate_fallback_review_results()
    
    def _extract_chapter_5_keywords(self, chapter_5_content: str) -> List[str]:
        """提取第五章关键技术词用于深度检索"""
        # 简单的关键词提取
        common_tech_keywords = [
            "算法", "系统", "方法", "技术", "创新", "架构", "实现", "优化", 
            "处理", "分析", "计算", "模型", "数据", "接口", "协议", "机制",
            "智能", "函数", "参数", "调用", "重试", "推断", "语义", "理解"
        ]
        
        keywords = []
        for keyword in common_tech_keywords:
            if keyword in chapter_5_content:
                keywords.append(keyword)
        
        return keywords[:10]  # 限制数量
    
    async def _deep_search_chapter_5(self, keywords: List[str], topic: str) -> Dict[str, Any]:
        """对第五章内容进行深度检索"""
        search_results = {}
        
        for keyword in keywords[:5]:  # 限制检索数量避免过载
            try:
                # 构建检索查询
                search_query = f"{topic} {keyword} 专利 技术方案"
                results = await self.searcher.search(search_query, max_results=3)
                search_results[keyword] = results
                
                # 添加延迟避免请求过快
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"检索关键词 {keyword} 失败: {e}")
                search_results[keyword] = []
        
        return search_results
    
    def _analyze_novelty(self, chapter_3_content: str, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """分析新颖性（结合第三章现有技术）"""
        # 简单的分析逻辑
        novelty_score = 75  # 默认评分
        
        # 检查是否有重复内容
        if chapter_3_content and chapter_5_content:
            # 简单的重复度检查
            common_words = set(chapter_3_content.split()) & set(chapter_5_content.split())
            if len(common_words) > 50:  # 如果共同词汇过多，降低新颖性评分
                novelty_score = 65
        
        return {
            "analysis": f"基于第三章现有技术和第五章技术方案的对比分析，技术方案具有中等程度的新颖性。",
            "novelty_score": novelty_score,
            "risk_level": "中等",
            "improvement_suggestions": ["增强技术方案的独特性", "明确与现有技术的区别"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_inventiveness(self, chapter_4_content: str, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """分析创造性（结合第四章技术问题）"""
        # 简单的分析逻辑
        inventiveness_score = 80
        
        # 检查是否解决了第四章提出的问题
        if chapter_4_content and chapter_5_content:
            # 简单的关键词匹配
            problem_keywords = ["问题", "困难", "不足", "缺陷", "限制"]
            solution_keywords = ["解决", "改进", "优化", "创新", "方案"]
            
            problem_count = sum(1 for word in problem_keywords if word in chapter_4_content)
            solution_count = sum(1 for word in solution_keywords if word in chapter_5_content)
            
            if solution_count > problem_count:
                inventiveness_score = 85
        
        return {
            "analysis": f"基于第四章技术问题和第五章技术方案的分析，技术方案具有较强的创造性。",
            "inventiveness_score": inventiveness_score,
            "problem_difficulty": "高",
            "improvement_suggestions": ["增强技术方案的创新性", "明确技术贡献"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_utility(self, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """分析实用性"""
        # 简单的分析逻辑
        utility_score = 85
        
        # 检查技术方案的可行性
        feasibility_keywords = ["实现", "应用", "部署", "使用", "制造"]
        feasibility_count = sum(1 for word in feasibility_keywords if word in chapter_5_content)
        
        if feasibility_count > 3:
            utility_score = 90
        
        return {
            "analysis": f"基于第五章技术方案的分析，技术方案具有较强的实用性。",
            "utility_score": utility_score,
            "feasibility": "高",
            "market_potential": "良好",
            "improvement_suggestions": ["增强实用性", "明确应用场景"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _critical_analysis(self, chapter_3_content: str, chapter_4_content: str, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """批判性分析"""
        # 简单的批判性分析
        critical_score = 70
        
        # 检查逻辑一致性
        if chapter_3_content and chapter_4_content and chapter_5_content:
            # 简单的逻辑检查
            if len(chapter_5_content) > len(chapter_3_content) + len(chapter_4_content):
                critical_score = 75  # 技术方案内容充分
        
        return {
            "analysis": f"基于前三章内容的批判性分析，技术方案具有中等程度的逻辑一致性和实现可行性。",
            "critical_score": critical_score,
            "risk_level": "中等",
            "implementation_difficulty": "中等",
            "improvement_space": "较大",
            "improvement_suggestions": ["增强逻辑一致性", "降低技术风险"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_improvement_suggestions(self, 
                                        chapter_3_content: str, 
                                        chapter_4_content: str, 
                                        chapter_5_content: str,
                                        novelty_analysis: Dict,
                                        inventiveness_analysis: Dict,
                                        utility_analysis: Dict,
                                        critical_analysis: Dict) -> Dict[str, Any]:
        """生成改进建议"""
        suggestions = [
            "增强技术方案与现有技术的区别度",
            "明确技术方案的创新点和优势",
            "提供更详细的技术实现方案",
            "增加应用场景和效果分析",
            "完善风险控制和错误处理机制"
        ]
        
        return {
            "suggestions": "基于全面分析，建议从技术独特性、创新性、实用性等方面进行改进。",
            "priority_levels": ["高", "中", "低"],
            "expected_effects": ["提升专利质量", "增强创新性", "降低风险"],
            "implementation_steps": ["立即实施", "分阶段实施", "长期规划"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_overall_assessment(self, 
                                   novelty_analysis: Dict,
                                   inventiveness_analysis: Dict,
                                   utility_analysis: Dict,
                                   critical_analysis: Dict) -> Dict[str, Any]:
        """生成总体评估"""
        # 计算综合评分
        novelty_score = novelty_analysis.get("novelty_score", 70)
        inventiveness_score = inventiveness_analysis.get("inventiveness_score", 75)
        utility_score = utility_analysis.get("utility_score", 80)
        critical_score = critical_analysis.get("critical_score", 70)
        
        overall_score = (novelty_score + inventiveness_score + utility_score + critical_score) // 4
        
        # 确定质量等级
        if overall_score >= 85:
            quality_grade = "A"
        elif overall_score >= 75:
            quality_grade = "B"
        elif overall_score >= 65:
            quality_grade = "C"
        else:
            quality_grade = "D"
        
        return {
            "assessment": f"基于新颖性、创造性、实用性、批判性四个维度的综合评估，专利质量等级为{quality_grade}。",
            "overall_score": overall_score,
            "quality_grade": quality_grade,
            "risk_level": "中等",
            "improvement_potential": "良好",
            "market_prospect": "良好",
            "application_recommendation": "建议申请",
            "decision_suggestion": "继续完善后申请",
            "next_actions": ["完善技术方案", "增强创新性", "降低风险"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_fallback_review_results(self) -> Dict[str, Any]:
        """生成fallback审核结果"""
        return {
            "deep_search_results": {},
            "novelty_analysis": {
                "analysis": "新颖性分析暂时不可用",
                "novelty_score": 70,
                "risk_level": "中等",
                "improvement_suggestions": ["需要进一步分析"],
                "timestamp": datetime.now().isoformat()
            },
            "inventiveness_analysis": {
                "analysis": "创造性分析暂时不可用",
                "inventiveness_score": 75,
                "problem_difficulty": "中等",
                "improvement_suggestions": ["需要进一步分析"],
                "timestamp": datetime.now().isoformat()
            },
            "utility_analysis": {
                "analysis": "实用性分析暂时不可用",
                "utility_score": 80,
                "feasibility": "中等",
                "market_potential": "一般",
                "improvement_suggestions": ["需要进一步分析"],
                "timestamp": datetime.now().isoformat()
            },
            "critical_analysis": {
                "analysis": "批判性分析暂时不可用",
                "critical_score": 65,
                "risk_level": "中等",
                "implementation_difficulty": "中等",
                "improvement_space": "一般",
                "improvement_suggestions": ["需要进一步分析"],
                "timestamp": datetime.now().isoformat()
            },
            "improvement_suggestions": {
                "suggestions": "改进建议暂时不可用",
                "priority_levels": ["需要进一步分析"],
                "expected_effects": ["需要进一步分析"],
                "implementation_steps": ["需要进一步分析"],
                "timestamp": datetime.now().isoformat()
            },
            "overall_assessment": {
                "assessment": "总体评估暂时不可用",
                "overall_score": 70,
                "quality_grade": "C",
                "risk_level": "中等",
                "improvement_potential": "一般",
                "market_prospect": "一般",
                "application_recommendation": "需要进一步分析",
                "decision_suggestion": "需要进一步分析",
                "next_actions": ["需要进一步分析"],
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def close(self):
        """关闭资源"""
        await self.searcher.close()

async def test_enhanced_reviewer():
    """测试增强版审核智能体"""
    
    # 初始化增强版审核智能体
    enhanced_reviewer = SimpleEnhancedReviewer()
    
    # 测试数据
    topic = "基于语义理解的复杂函数参数智能推断与分层调用重试优化方法"
    
    # 模拟第三章内容（现有技术）
    chapter_3_content = """
    第三章 现有技术
    
    目前，在智能函数调用领域存在以下主要技术：
    
    1. 传统函数调用方法
    - 基于固定参数列表的调用方式
    - 缺乏智能推断能力
    - 错误处理机制简单
    
    2. 现有智能调用技术
    - 基于规则的模式匹配
    - 简单的参数推断
    - 有限的错误恢复能力
    
    3. 相关专利技术
    - US12345678: 智能函数调用系统
    - CN98765432: 参数推断方法
    """
    
    # 模拟第四章内容（技术问题）
    chapter_4_content = """
    第四章 技术问题
    
    现有技术存在以下主要问题：
    
    1. 参数推断准确率低
    - 复杂参数类型推断困难
    - 上下文理解能力有限
    - 多参数组合推断效果差
    
    2. 错误处理机制不完善
    - 失败重试策略简单
    - 缺乏智能诊断能力
    - 恢复成功率低
    
    3. 系统性能问题
    - 调用延迟高
    - 资源消耗大
    - 扩展性差
    """
    
    # 模拟第五章内容（技术方案）
    chapter_5_content = """
    第五章 技术方案详细阐述
    
    5.1 系统架构设计
    
    本发明采用分层架构设计，包括：
    - 语义理解层：负责自然语言解析
    - 参数推断层：实现智能参数推断
    - 调用执行层：执行函数调用
    - 重试优化层：处理失败重试
    
    5.2 核心算法实现
    
    创新算法包括：
    - 语义理解算法：基于深度学习的自然语言处理
    - 参数推断算法：多维度参数智能推断
    - 重试优化算法：自适应重试策略
    
    5.3 数据流程设计
    
    数据处理流程：
    - 输入预处理
    - 语义分析
    - 参数推断
    - 调用执行
    - 结果验证
    - 失败重试
    """
    
    # 模拟检索结果
    search_results = {
        "智能函数调用": [
            {"title": "智能函数调用技术", "content": "相关技术内容"},
            {"title": "参数推断方法", "content": "现有推断技术"}
        ],
        "重试机制": [
            {"title": "失败重试策略", "content": "现有重试技术"},
            {"title": "错误恢复方法", "content": "恢复机制研究"}
        ]
    }
    
    try:
        logger.info("🚀 开始测试增强版审核智能体")
        
        # 执行综合审核
        review_results = await enhanced_reviewer.comprehensive_review(
            chapter_3_content=chapter_3_content,
            chapter_4_content=chapter_4_content,
            chapter_5_content=chapter_5_content,
            topic=topic,
            search_results=search_results
        )
        
        logger.info("✅ 综合审核完成")
        
        # 输出审核结果
        print("\n" + "="*80)
        print("增强版审核智能体测试结果")
        print("="*80)
        
        # 深度检索结果
        print("\n🔍 深度检索结果:")
        deep_search = review_results.get("deep_search_results", {})
        for keyword, results in deep_search.items():
            print(f"  - {keyword}: {len(results)} 条结果")
        
        # 新颖性分析
        print("\n📋 新颖性分析:")
        novelty = review_results.get("novelty_analysis", {})
        print(f"  - 评分: {novelty.get('novelty_score', 'N/A')}")
        print(f"  - 风险等级: {novelty.get('risk_level', 'N/A')}")
        print(f"  - 分析: {novelty.get('analysis', 'N/A')}")
        
        # 创造性分析
        print("\n💡 创造性分析:")
        inventiveness = review_results.get("inventiveness_analysis", {})
        print(f"  - 评分: {inventiveness.get('inventiveness_score', 'N/A')}")
        print(f"  - 问题难度: {inventiveness.get('problem_difficulty', 'N/A')}")
        print(f"  - 分析: {inventiveness.get('analysis', 'N/A')}")
        
        # 实用性分析
        print("\n🔧 实用性分析:")
        utility = review_results.get("utility_analysis", {})
        print(f"  - 评分: {utility.get('utility_score', 'N/A')}")
        print(f"  - 可行性: {utility.get('feasibility', 'N/A')}")
        print(f"  - 分析: {utility.get('analysis', 'N/A')}")
        
        # 批判性分析
        print("\n🤔 批判性分析:")
        critical = review_results.get("critical_analysis", {})
        print(f"  - 评分: {critical.get('critical_score', 'N/A')}")
        print(f"  - 风险等级: {critical.get('risk_level', 'N/A')}")
        print(f"  - 分析: {critical.get('analysis', 'N/A')}")
        
        # 总体评估
        print("\n📊 总体评估:")
        overall = review_results.get("overall_assessment", {})
        print(f"  - 综合评分: {overall.get('overall_score', 'N/A')}")
        print(f"  - 质量等级: {overall.get('quality_grade', 'N/A')}")
        print(f"  - 申请建议: {overall.get('application_recommendation', 'N/A')}")
        print(f"  - 分析: {overall.get('assessment', 'N/A')}")
        
        # 改进建议
        print("\n💡 改进建议:")
        improvements = review_results.get("improvement_suggestions", {})
        suggestions = improvements.get("suggestions", "暂无具体建议")
        print(f"  - {suggestions}")
        
        print("\n" + "="*80)
        print("测试完成")
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        print(f"测试失败: {e}")
    
    finally:
        # 关闭资源
        await enhanced_reviewer.close()

async def test_duckduckgo_search():
    """测试DuckDuckGo检索功能"""
    
    searcher = SimpleDuckDuckGoSearcher()
    
    try:
        logger.info("🔍 测试DuckDuckGo检索功能")
        
        # 测试检索
        query = "智能函数调用 专利 技术方案"
        results = await searcher.search(query, max_results=5)
        
        print(f"\n检索查询: {query}")
        print(f"检索结果数量: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"  标题: {result.get('title', 'N/A')}")
            print(f"  来源: {result.get('source', 'N/A')}")
            print(f"  内容: {result.get('content', 'N/A')[:100]}...")
        
    except Exception as e:
        logger.error(f"❌ DuckDuckGo检索测试失败: {e}")
        print(f"DuckDuckGo检索测试失败: {e}")
    
    finally:
        await searcher.close()

if __name__ == "__main__":
    print("🧪 开始测试增强版审核智能体")
    
    # 运行测试
    asyncio.run(test_enhanced_reviewer())
    
    print("\n" + "-"*80)
    
    # 测试DuckDuckGo检索
    asyncio.run(test_duckduckgo_search())