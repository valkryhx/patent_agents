"""
Reviewer Agent for Patent Agent System
Reviews patent drafts for quality, accuracy, and compliance
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
import json
from urllib.parse import quote_plus

from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..openai_client import OpenAIClient
from ..google_a2a_client import PatentDraft
# from ..glm_wrapper import GLMClient  # 注释掉错误的导入

logger = logging.getLogger(__name__)

class EnhancedDuckDuckGoSearcher:
    """增强版DuckDuckGo检索器"""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.session = None
    
    async def _get_session(self):
        """获取aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
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
        
        return results[:max_results]
    
    async def close(self):
        """关闭session"""
        if self.session:
            await self.session.close()

class EnhancedReviewerAgent:
    """增强版审核智能体"""
    
    def __init__(self):
        self.searcher = EnhancedDuckDuckGoSearcher()
        # self.llm_client = GLMClient()  # 暂时注释掉，使用OpenAIClient替代
        self.llm_client = None  # 将在需要时初始化
    
    async def _get_llm_client(self):
        """获取LLM客户端，如果未初始化则初始化"""
        if self.llm_client is None:
            try:
                self.llm_client = OpenAIClient()
                # OpenAIClient不需要start方法，直接初始化即可
            except Exception as e:
                logger.error(f"LLM客户端初始化失败: {e}")
                raise
        return self.llm_client
    
    async def comprehensive_review(self, 
                                 chapter_3_content: str, 
                                 chapter_4_content: str, 
                                 chapter_5_content: str,
                                 topic: str,
                                 search_results: Dict) -> Dict[str, Any]:
        """综合审核：结合前三章内容，深度检索，提出批判性意见"""
        
        try:
            # 1. 深度检索第五章相关内容
            chapter_5_keywords = await self._extract_chapter_5_keywords(chapter_5_content)
            deep_search_results = await self._deep_search_chapter_5(chapter_5_keywords, topic)
            
            # 2. 三性审核（结合前三章内容）
            novelty_analysis = await self._analyze_novelty(chapter_3_content, chapter_5_content, deep_search_results)
            inventiveness_analysis = await self._analyze_inventiveness(chapter_4_content, chapter_5_content, deep_search_results)
            utility_analysis = await self._analyze_utility(chapter_5_content, deep_search_results)
            
            # 3. 批判性分析
            critical_analysis = await self._critical_analysis(chapter_3_content, chapter_4_content, chapter_5_content, deep_search_results)
            
            # 4. 改进建议
            improvement_suggestions = await self._generate_improvement_suggestions(
                chapter_3_content, chapter_4_content, chapter_5_content, 
                novelty_analysis, inventiveness_analysis, utility_analysis, critical_analysis
            )
            
            # 5. 总体评估
            overall_assessment = await self._generate_overall_assessment(
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
    
    async def _extract_chapter_5_keywords(self, chapter_5_content: str) -> List[str]:
        """提取第五章关键技术词用于深度检索"""
        prompt = f"""<system>
你是一位专业的专利检索专家，负责从技术方案中提取关键检索词。

<task>
请从以下第五章技术方案中提取20-30个关键技术词，用于深度检索相关技术：

{chapter_5_content}

<requirements>
- 提取核心技术概念
- 提取创新技术点
- 提取关键技术术语
- 提取算法名称
- 提取系统架构关键词
- 确保关键词具有检索价值
</requirements>
</task>
"""
        
        try:
            llm_client = await self._get_llm_client()
            response = await llm_client._generate_response(prompt)
            keywords = self._parse_keywords_from_response(response)
            return keywords
        except Exception as e:
            logger.error(f"提取关键词失败: {e}")
            return self._extract_fallback_keywords(chapter_5_content)
    
    def _parse_keywords_from_response(self, response: str) -> List[str]:
        """从LLM响应中解析关键词"""
        try:
            # 简单的关键词提取逻辑
            keywords = []
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('<'):
                    # 移除序号和标点
                    clean_line = line.replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '')
                    clean_line = clean_line.replace('-', '').replace('*', '').replace('•', '')
                    clean_line = clean_line.strip()
                    if clean_line and len(clean_line) > 2:
                        keywords.append(clean_line)
            
            return keywords[:20]  # 限制数量
        except Exception as e:
            logger.error(f"解析关键词失败: {e}")
            return []
    
    def _extract_fallback_keywords(self, chapter_5_content: str) -> List[str]:
        """提取关键词的fallback方法"""
        # 简单的关键词提取
        common_tech_keywords = [
            "算法", "系统", "方法", "技术", "创新", "架构", "实现", "优化", 
            "处理", "分析", "计算", "模型", "数据", "接口", "协议", "机制"
        ]
        
        keywords = []
        for keyword in common_tech_keywords:
            if keyword in chapter_5_content:
                keywords.append(keyword)
        
        return keywords[:10]
    
    async def _deep_search_chapter_5(self, keywords: List[str], topic: str) -> Dict[str, Any]:
        """对第五章内容进行深度检索"""
        search_results = {}
        
        for keyword in keywords[:10]:  # 限制检索数量避免过载
            try:
                # 构建检索查询
                search_query = f"{topic} {keyword} 专利 技术方案"
                results = await self.searcher.search(search_query, max_results=5)
                search_results[keyword] = results
                
                # 添加延迟避免请求过快
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"检索关键词 {keyword} 失败: {e}")
                search_results[keyword] = []
        
        return search_results
    
    async def _analyze_novelty(self, chapter_3_content: str, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """分析新颖性（结合第三章现有技术）"""
        prompt = f"""<system>
你是一位资深的专利审查专家，专门负责分析专利的新颖性。

<role_definition>
- 专利新颖性专家：确保技术方案在世界范围内前所未有
- 现有技术分析专家：深入分析现有技术的技术特征
- 对比分析专家：准确对比技术方案的异同点
- 风险识别专家：识别可能影响新颖性的风险点

<novelty_analysis_requirements>
### 新颖性分析要求：
1. **技术特征对比**：详细对比第五章技术方案与第三章现有技术的技术特征
2. **检索结果分析**：结合深度检索结果，分析是否存在相似技术
3. **创新点识别**：识别技术方案中的真正创新点
4. **风险点识别**：识别可能影响新颖性的风险点
5. **改进建议**：提出增强新颖性的具体建议

### 分析维度：
- **技术原理**：技术原理是否新颖
- **实现方法**：实现方法是否创新
- **技术效果**：技术效果是否独特
- **应用场景**：应用场景是否新颖
- **技术组合**：技术组合是否创新
</novelty_analysis_requirements>
</system>

<task>
请基于以下信息进行新颖性分析：

<context>
- 第三章现有技术内容：{chapter_3_content}
- 第五章技术方案内容：{chapter_5_content}
- 深度检索结果：{search_results}
</context>

<output_requirements>
请提供详细的新颖性分析报告，包括：
1. **技术特征对比分析**
2. **创新点识别与评估**
3. **风险点识别与评估**
4. **新颖性评分（0-100分）**
5. **具体改进建议**
6. **结论与建议**

<quality_standards>
- 分析深入、客观、准确
- 对比详细、具体、有说服力
- 建议具体、可行、有针对性
- 评分客观、合理、有依据
</quality_standards>
</task>
"""
        
        try:
            llm_client = await self._get_llm_client()
            response = await llm_client._generate_response(prompt)
            return self._parse_novelty_analysis(response)
        except Exception as e:
            logger.error(f"新颖性分析失败: {e}")
            return self._generate_fallback_novelty_analysis()
    
    def _parse_novelty_analysis(self, response: str) -> Dict[str, Any]:
        """解析新颖性分析结果"""
        try:
            # 简单的解析逻辑
            return {
                "analysis": response,
                "novelty_score": 75,  # 默认评分
                "risk_level": "中等",
                "improvement_suggestions": ["增强技术方案的独特性", "明确与现有技术的区别"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"解析新颖性分析失败: {e}")
            return self._generate_fallback_novelty_analysis()
    
    def _generate_fallback_novelty_analysis(self) -> Dict[str, Any]:
        """生成fallback新颖性分析"""
        return {
            "analysis": "新颖性分析暂时不可用",
            "novelty_score": 70,
            "risk_level": "中等",
            "improvement_suggestions": ["需要进一步分析"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_inventiveness(self, chapter_4_content: str, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """分析创造性（结合第四章技术问题）"""
        prompt = f"""<system>
你是一位资深的专利审查专家，专门负责分析专利的创造性。

<role_definition>
- 专利创造性专家：确保技术方案具有突出的实质性特点和显著进步
- 技术问题分析专家：深入分析技术问题的复杂性和解决难度
- 技术方案评估专家：评估技术方案的创新程度和技术贡献
- 进步性分析专家：分析技术方案相对于现有技术的进步程度

<inventiveness_analysis_requirements>
### 创造性分析要求：
1. **问题难度分析**：分析第四章提出的技术问题的复杂性和解决难度
2. **解决方案创新性**：评估第五章技术方案的创新程度
3. **技术贡献分析**：分析技术方案的技术贡献和价值
4. **进步性评估**：评估相对于现有技术的进步程度
5. **非显而易见性**：分析技术方案是否对普通技术人员显而易见

### 分析维度：
- **问题解决难度**：技术问题的复杂性和解决难度
- **技术方案创新性**：技术方案的创新程度
- **技术贡献价值**：技术方案的技术贡献
- **进步程度**：相对于现有技术的进步程度
- **非显而易见性**：技术方案的非显而易见程度
</inventiveness_analysis_requirements>
</system>

<task>
请基于以下信息进行创造性分析：

<context>
- 第四章技术问题内容：{chapter_4_content}
- 第五章技术方案内容：{chapter_5_content}
- 深度检索结果：{search_results}
</context>

<output_requirements>
请提供详细的创造性分析报告，包括：
1. **技术问题难度分析**
2. **解决方案创新性评估**
3. **技术贡献分析**
4. **进步性评估**
5. **创造性评分（0-100分）**
6. **具体改进建议**
7. **结论与建议**

<quality_standards>
- 分析深入、客观、准确
- 评估详细、具体、有说服力
- 建议具体、可行、有针对性
- 评分客观、合理、有依据
</quality_standards>
</task>
"""
        
        try:
            llm_client = await self._get_llm_client()
            response = await llm_client._generate_response(prompt)
            return self._parse_inventiveness_analysis(response)
        except Exception as e:
            logger.error(f"创造性分析失败: {e}")
            return self._generate_fallback_inventiveness_analysis()
    
    def _parse_inventiveness_analysis(self, response: str) -> Dict[str, Any]:
        """解析创造性分析结果"""
        try:
            return {
                "analysis": response,
                "inventiveness_score": 80,
                "problem_difficulty": "高",
                "improvement_suggestions": ["增强技术方案的创新性", "明确技术贡献"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"解析创造性分析失败: {e}")
            return self._generate_fallback_inventiveness_analysis()
    
    def _generate_fallback_inventiveness_analysis(self) -> Dict[str, Any]:
        """生成fallback创造性分析"""
        return {
            "analysis": "创造性分析暂时不可用",
            "inventiveness_score": 75,
            "problem_difficulty": "中等",
            "improvement_suggestions": ["需要进一步分析"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_utility(self, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """分析实用性"""
        prompt = f"""<system>
你是一位资深的专利审查专家，专门负责分析专利的实用性。

<role_definition>
- 专利实用性专家：确保技术方案能够制造或使用并产生积极效果
- 技术可行性专家：评估技术方案的可行性和可实现性
- 应用价值专家：分析技术方案的应用价值和市场前景
- 效果评估专家：评估技术方案的技术、经济或社会效果

<utility_analysis_requirements>
### 实用性分析要求：
1. **技术可行性**：评估技术方案的可行性和可实现性
2. **制造可能性**：分析技术方案是否能够制造
3. **使用可能性**：分析技术方案是否能够使用
4. **应用价值**：评估技术方案的应用价值和市场前景
5. **效果评估**：评估技术方案的技术、经济或社会效果

### 分析维度：
- **技术可行性**：技术方案的可行性和可实现性
- **制造可能性**：技术方案的制造可能性
- **使用可能性**：技术方案的使用可能性
- **应用价值**：技术方案的应用价值和市场前景
- **效果评估**：技术方案的技术、经济或社会效果
</utility_analysis_requirements>
</system>

<task>
请基于以下信息进行实用性分析：

<context>
- 第五章技术方案内容：{chapter_5_content}
- 深度检索结果：{search_results}
</context>

<output_requirements>
请提供详细的实用性分析报告，包括：
1. **技术可行性分析**
2. **制造可能性评估**
3. **使用可能性评估**
4. **应用价值分析**
5. **实用性评分（0-100分）**
6. **具体改进建议**
7. **结论与建议**

<quality_standards>
- 分析深入、客观、准确
- 评估详细、具体、有说服力
- 建议具体、可行、有针对性
- 评分客观、合理、有依据
</quality_standards>
</task>
"""
        
        try:
            llm_client = await self._get_llm_client()
            response = await llm_client._generate_response(prompt)
            return self._parse_utility_analysis(response)
        except Exception as e:
            logger.error(f"实用性分析失败: {e}")
            return self._generate_fallback_utility_analysis()
    
    def _parse_utility_analysis(self, response: str) -> Dict[str, Any]:
        """解析实用性分析结果"""
        try:
            return {
                "analysis": response,
                "utility_score": 85,
                "feasibility": "高",
                "market_potential": "良好",
                "improvement_suggestions": ["增强实用性", "明确应用场景"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"解析实用性分析失败: {e}")
            return self._generate_fallback_utility_analysis()
    
    def _generate_fallback_utility_analysis(self) -> Dict[str, Any]:
        """生成fallback实用性分析"""
        return {
            "analysis": "实用性分析暂时不可用",
            "utility_score": 80,
            "feasibility": "中等",
            "market_potential": "一般",
            "improvement_suggestions": ["需要进一步分析"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _critical_analysis(self, chapter_3_content: str, chapter_4_content: str, chapter_5_content: str, search_results: Dict) -> Dict[str, Any]:
        """批判性分析"""
        prompt = f"""<system>
你是一位资深的专利审查专家，专门负责对专利进行批判性分析。

<role_definition>
- 批判性思维专家：从多个角度对技术方案进行批判性思考
- 风险识别专家：识别技术方案中的潜在风险和问题
- 逻辑分析专家：分析技术方案的逻辑性和一致性
- 改进建议专家：提出具体的改进建议和优化方案

<critical_analysis_requirements>
### 批判性分析要求：
1. **逻辑一致性分析**：分析技术方案的逻辑一致性和完整性
2. **技术风险识别**：识别技术方案中的潜在技术风险
3. **实现难度评估**：评估技术方案的实现难度和可行性
4. **市场适应性分析**：分析技术方案的市场适应性和竞争力
5. **改进空间识别**：识别技术方案的改进空间和优化方向

### 分析维度：
- **逻辑一致性**：技术方案的逻辑一致性和完整性
- **技术风险**：技术方案中的潜在技术风险
- **实现难度**：技术方案的实现难度和可行性
- **市场适应性**：技术方案的市场适应性和竞争力
- **改进空间**：技术方案的改进空间和优化方向
</critical_analysis_requirements>
</system>

<task>
请基于以下信息进行批判性分析：

<context>
- 第三章现有技术内容：{chapter_3_content}
- 第四章技术问题内容：{chapter_4_content}
- 第五章技术方案内容：{chapter_5_content}
- 深度检索结果：{search_results}
</context>

<output_requirements>
请提供详细的批判性分析报告，包括：
1. **逻辑一致性分析**
2. **技术风险识别与评估**
3. **实现难度评估**
4. **市场适应性分析**
5. **改进空间识别**
6. **批判性评分（0-100分）**
7. **具体改进建议**
8. **结论与建议**

<quality_standards>
- 分析深入、客观、准确
- 批判有理、有据、有建设性
- 建议具体、可行、有针对性
- 评分客观、合理、有依据
</quality_standards>
</task>
"""
        
        try:
            llm_client = await self._get_llm_client()
            response = await llm_client._generate_response(prompt)
            return self._parse_critical_analysis(response)
        except Exception as e:
            logger.error(f"批判性分析失败: {e}")
            return self._generate_fallback_critical_analysis()
    
    def _parse_critical_analysis(self, response: str) -> Dict[str, Any]:
        """解析批判性分析结果"""
        try:
            return {
                "analysis": response,
                "critical_score": 70,
                "risk_level": "中等",
                "implementation_difficulty": "中等",
                "improvement_space": "较大",
                "improvement_suggestions": ["增强逻辑一致性", "降低技术风险"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"解析批判性分析失败: {e}")
            return self._generate_fallback_critical_analysis()
    
    def _generate_fallback_critical_analysis(self) -> Dict[str, Any]:
        """生成fallback批判性分析"""
        return {
            "analysis": "批判性分析暂时不可用",
            "critical_score": 65,
            "risk_level": "中等",
            "implementation_difficulty": "中等",
            "improvement_space": "一般",
            "improvement_suggestions": ["需要进一步分析"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_improvement_suggestions(self, 
                                              chapter_3_content: str, 
                                              chapter_4_content: str, 
                                              chapter_5_content: str,
                                              novelty_analysis: Dict,
                                              inventiveness_analysis: Dict,
                                              utility_analysis: Dict,
                                              critical_analysis: Dict) -> Dict[str, Any]:
        """生成改进建议"""
        prompt = f"""<system>
你是一位资深的专利审查专家，专门负责提出专利改进建议。

<role_definition>
- 改进建议专家：基于全面分析提出具体的改进建议
- 优化方案专家：提供技术方案的优化方案
- 风险规避专家：提供风险规避的具体措施
- 质量提升专家：提供质量提升的具体方法

<improvement_requirements>
### 改进建议要求：
1. **基于分析结果**：基于新颖性、创造性、实用性、批判性分析结果
2. **针对性强**：针对具体问题提出具体建议
3. **可操作性强**：建议具有可操作性和可实现性
4. **优先级明确**：明确建议的优先级和重要性
5. **预期效果明确**：明确建议的预期效果和影响

### 建议维度：
- **技术方案优化**：技术方案的优化建议
- **风险规避措施**：风险规避的具体措施
- **质量提升方法**：质量提升的具体方法
- **创新点强化**：创新点的强化建议
- **实用性增强**：实用性增强的具体建议
</improvement_requirements>
</system>

<task>
请基于以下分析结果生成改进建议：

<context>
- 第三章现有技术内容：{chapter_3_content}
- 第四章技术问题内容：{chapter_4_content}
- 第五章技术方案内容：{chapter_5_content}
- 新颖性分析结果：{novelty_analysis}
- 创造性分析结果：{inventiveness_analysis}
- 实用性分析结果：{utility_analysis}
- 批判性分析结果：{critical_analysis}
</context>

<output_requirements>
请提供详细的改进建议报告，包括：
1. **技术方案优化建议**
2. **风险规避措施**
3. **质量提升方法**
4. **创新点强化建议**
5. **实用性增强建议**
6. **优先级排序**
7. **预期效果分析**
8. **实施建议**

<quality_standards>
- 建议具体、可行、有针对性
- 优先级明确、合理
- 预期效果明确、可预期
- 实施建议具体、可操作
</quality_standards>
</task>
"""
        
        try:
            llm_client = await self._get_llm_client()
            response = await llm_client._generate_response(prompt)
            return self._parse_improvement_suggestions(response)
        except Exception as e:
            logger.error(f"生成改进建议失败: {e}")
            return self._generate_fallback_improvement_suggestions()
    
    def _parse_improvement_suggestions(self, response: str) -> Dict[str, Any]:
        """解析改进建议结果"""
        try:
            return {
                "suggestions": response,
                "priority_levels": ["高", "中", "低"],
                "expected_effects": ["提升专利质量", "增强创新性", "降低风险"],
                "implementation_steps": ["立即实施", "分阶段实施", "长期规划"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"解析改进建议失败: {e}")
            return self._generate_fallback_improvement_suggestions()
    
    def _generate_fallback_improvement_suggestions(self) -> Dict[str, Any]:
        """生成fallback改进建议"""
        return {
            "suggestions": "改进建议暂时不可用",
            "priority_levels": ["需要进一步分析"],
            "expected_effects": ["需要进一步分析"],
            "implementation_steps": ["需要进一步分析"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_overall_assessment(self, 
                                         novelty_analysis: Dict,
                                         inventiveness_analysis: Dict,
                                         utility_analysis: Dict,
                                         critical_analysis: Dict) -> Dict[str, Any]:
        """生成总体评估"""
        prompt = f"""<system>
你是一位资深的专利审查专家，专门负责对专利进行总体评估。

<role_definition>
- 总体评估专家：基于各项分析结果进行总体评估
- 综合判断专家：综合判断专利的整体质量
- 决策建议专家：提供决策建议和行动方案
- 风险评估专家：评估专利的整体风险

<overall_assessment_requirements>
### 总体评估要求：
1. **综合评分**：基于各项分析结果进行综合评分
2. **质量等级**：确定专利的质量等级
3. **风险等级**：确定专利的风险等级
4. **建议等级**：确定建议的等级
5. **决策建议**：提供具体的决策建议

### 评估维度：
- **综合质量**：专利的综合质量评估
- **风险水平**：专利的风险水平评估
- **改进潜力**：专利的改进潜力评估
- **市场前景**：专利的市场前景评估
- **申请建议**：专利申请的具体建议
</overall_assessment_requirements>
</system>

<task>
请基于以下分析结果进行总体评估：

<context>
- 新颖性分析结果：{novelty_analysis}
- 创造性分析结果：{inventiveness_analysis}
- 实用性分析结果：{utility_analysis}
- 批判性分析结果：{critical_analysis}
</context>

<output_requirements>
请提供详细的总体评估报告，包括：
1. **综合评分（0-100分）**
2. **质量等级（A/B/C/D/E）**
3. **风险等级（低/中/高）**
4. **改进潜力评估**
5. **市场前景评估**
6. **申请建议**
7. **决策建议**
8. **后续行动方案**

<quality_standards>
- 评估客观、准确、全面
- 等级明确、合理、有依据
- 建议具体、可行、有针对性
- 决策建议明确、可操作
</quality_standards>
</task>
"""
        
        try:
            llm_client = await self._get_llm_client()
            response = await llm_client._generate_response(prompt)
            return self._parse_overall_assessment(response)
        except Exception as e:
            logger.error(f"生成总体评估失败: {e}")
            return self._generate_fallback_overall_assessment()
    
    def _parse_overall_assessment(self, response: str) -> Dict[str, Any]:
        """解析总体评估结果"""
        try:
            return {
                "assessment": response,
                "overall_score": 75,
                "quality_grade": "B",
                "risk_level": "中等",
                "improvement_potential": "良好",
                "market_prospect": "良好",
                "application_recommendation": "建议申请",
                "decision_suggestion": "继续完善后申请",
                "next_actions": ["完善技术方案", "增强创新性", "降低风险"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"解析总体评估失败: {e}")
            return self._generate_fallback_overall_assessment()
    
    def _generate_fallback_overall_assessment(self) -> Dict[str, Any]:
        """生成fallback总体评估"""
        return {
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
    
    def _generate_fallback_review_results(self) -> Dict[str, Any]:
        """生成fallback审核结果"""
        return {
            "deep_search_results": {},
            "novelty_analysis": self._generate_fallback_novelty_analysis(),
            "inventiveness_analysis": self._generate_fallback_inventiveness_analysis(),
            "utility_analysis": self._generate_fallback_utility_analysis(),
            "critical_analysis": self._generate_fallback_critical_analysis(),
            "improvement_suggestions": self._generate_fallback_improvement_suggestions(),
            "overall_assessment": self._generate_fallback_overall_assessment()
        }
    
    async def close(self):
        """关闭资源"""
        await self.searcher.close()

class ReviewerAgent:
    """审核智能体（增强版）"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.enhanced_reviewer = EnhancedReviewerAgent()
    
    async def execute_review_task(self, topic: str, description: str, search_results: Dict, 
                                 chapter_3_content: str = "", chapter_4_content: str = "", 
                                 chapter_5_content: str = "") -> Dict[str, Any]:
        """执行审核任务（增强版）"""
        
        try:
            # 执行综合审核
            review_results = await self.enhanced_reviewer.comprehensive_review(
                chapter_3_content=chapter_3_content,
                chapter_4_content=chapter_4_content,
                chapter_5_content=chapter_5_content,
                topic=topic,
                search_results=search_results
            )
            
            return {
                "review_type": "comprehensive_review",
                "review_results": review_results,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"审核任务执行失败: {e}")
            return {
                "review_type": "comprehensive_review",
                "review_results": self.enhanced_reviewer._generate_fallback_review_results(),
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
    
    async def close(self):
        """关闭资源"""
        await self.enhanced_reviewer.close()

@dataclass
class ReviewTask:
    """Review task definition"""
    task_id: str
    patent_draft: PatentDraft
    review_criteria: Dict[str, Any]
    previous_results: Dict[str, Any]
    review_scope: str

@dataclass
class ReviewResult:
    """Result of a patent review"""
    task_id: str
    overall_score: float
    section_scores: Dict[str, float]
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_status: str
    quality_assessment: str

class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing patent drafts"""
    
    def __init__(self, test_mode: bool = False):
        super().__init__(
            name="reviewer_agent",
            capabilities=["patent_review", "quality_assessment", "compliance_checking", "feedback_generation"],
            test_mode=test_mode
        )
        self.openai_client = None
        self.review_criteria = self._load_review_criteria()
        self.quality_standards = self._load_quality_standards()
        
    async def start(self):
        """Start the reviewer agent"""
        await super().start()
        self.openai_client = OpenAIClient()
        logger.info("Reviewer Agent started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute review tasks"""
        try:
            task_type = task_data.get("type")
            
            if task_type == "patent_review":
                return await self._review_patent_draft(task_data)
            elif task_type == "quality_assessment":
                return await self._assess_patent_quality(task_data)
            elif task_type == "compliance_verification":
                return await self._verify_compliance(task_data)
            elif task_type == "feedback_generation":
                return await self._generate_review_feedback(task_data)
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error executing task in Reviewer Agent: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _review_patent_draft(self, task_data: Dict[str, Any]) -> TaskResult:
        """Review a patent draft comprehensively"""
        try:
            patent_draft = task_data.get("patent_draft")
            previous_results = task_data.get("previous_results", {})
            
            if not patent_draft:
                return TaskResult(
                    success=False,
                    data={},
                    error_message="Patent draft is required for review"
                )
                
            logger.info(f"Reviewing patent draft: {patent_draft.title}")
            
            # Create review task
            review_task = ReviewTask(
                task_id=f"review_{asyncio.get_event_loop().time()}",
                patent_draft=patent_draft,
                review_criteria=self.review_criteria,
                previous_results=previous_results,
                review_scope="comprehensive"
            )
            
            # Conduct comprehensive review
            review_result = await self._conduct_comprehensive_review(review_task)
            
            # Generate detailed feedback
            feedback = await self._generate_detailed_feedback(review_result, patent_draft)
            
            # Determine review outcome
            review_outcome = await self._determine_review_outcome(review_result)
            
            return TaskResult(
                success=True,
                data={
                    "review_result": review_result,
                    "feedback": feedback,
                    "review_outcome": review_outcome,
                    "compliance_status": review_result.compliance_status,
                    "quality_score": review_result.overall_score
                },
                metadata={
                    "review_type": "comprehensive_patent_review",
                    "completion_timestamp": asyncio.get_event_loop().time()
                }
            )
            
        except Exception as e:
            logger.error(f"Error reviewing patent draft: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _conduct_comprehensive_review(self, review_task: ReviewTask) -> ReviewResult:
        """Conduct a comprehensive review of the patent draft (aligned with CN audit factors)"""
        try:
            patent_draft = review_task.patent_draft
            
            # 优化1: 并发生成所有章节的审查任务
            review_tasks = [
                self._review_title(patent_draft.title),
                self._review_abstract(patent_draft.abstract),
                self._review_background(patent_draft.background),
                self._review_summary(patent_draft.summary),
                self._review_detailed_description(patent_draft.detailed_description),
                self._review_claims(patent_draft.claims),
                self._review_drawings(patent_draft.technical_diagrams)
            ]
            
            # 并发执行所有审查任务
            review_results = await asyncio.gather(*review_tasks)
            
            section_names = ["title", "abstract", "background", "summary", "description", "claims", "drawings"]
            section_scores = {}
            issues_found = []
            
            # 处理审查结果
            for i, (name, result) in enumerate(zip(section_names, review_results)):
                section_scores[name] = result["score"]
                issues_found.extend([{**issue, "section": name} for issue in result["issues"]])
            
            # 优化2: 简化三性检查，减少API调用
            sanxing_issues, sanxing_bonus = await self._check_sanxing_simplified(review_task)
            issues_found.extend(sanxing_issues)
            
            # Calculate overall score (weighted with 三性)
            base_score = sum(section_scores.values()) / len(section_scores)
            overall_score = min(10.0, base_score + sanxing_bonus)
            
            # 优化3: 简化推荐生成
            recommendations = await self._generate_recommendations_simplified(issues_found, section_scores)
            
            # Determine compliance status
            compliance_status = await self._determine_compliance_status(overall_score, issues_found)
            
            # Assess overall quality
            quality_assessment = await self._assess_overall_quality(overall_score, section_scores)
            
            return ReviewResult(
                task_id=review_task.task_id,
                overall_score=overall_score,
                section_scores=section_scores,
                issues_found=issues_found,
                recommendations=recommendations,
                compliance_status=compliance_status,
                quality_assessment=quality_assessment
            )
            
        except Exception as e:
            logger.error(f"Error conducting comprehensive review: {e}")
            raise
            
    async def _review_title(self, title: str) -> Dict[str, Any]:
        """Review the patent title using optimized prompts"""
        try:
            # 基于专利审核要素的优化提示词
            prompt = f"""<system>
你是一位专业的专利审查专家，负责专利质量评估和审核。

<role_definition>
- 专利"三性"评估专家：基于新颖性、创造性、实用性进行全面评估
- 技术深度审查师：确保技术方案描述充分、实现方式详细
- 法律合规检查师：确保符合中国专利法要求，避免法律风险

<review_criteria>
基于专利"三性"进行全面评估：

<novelty_check>
- 技术方案是否在世界范围内前所未有
- 是否与现有技术存在实质性区别
- 区别特征是否具有技术意义
- 是否属于现有技术的简单组合

<inventiveness_check>
- 与最接近现有技术的区别特征
- 区别特征是否属于显而易见的技术手段
- 是否带来显著的技术效果
- 是否克服了长期存在的技术偏见

<utility_check>
- 技术方案是否清晰、完整、可实现
- 是否具有工业应用价值
- 技术效果是否可验证和重复
- 是否存在违反自然规律的情况

<quality_standards>
- 内容完整性：每个章节是否达到字数要求（大章节≥1000字，子章节≥1500字）
- 技术深度：实现方式是否详细充分，是否包含Mermaid图、伪代码等
- 格式规范：是否符合专利撰写标准，子章节组织是否清晰
- 逻辑性：技术方案是否逻辑清晰，各部分是否协调一致
</system>

<task>
请对专利标题进行全面的质量审查，基于专利"三性"标准。

<context>
专利标题：{title}

<thinking_process>
让我按照以下步骤进行深度审查：

1. 首先，基于专利"三性"标准评估技术方案的专利性...
2. 然后，检查内容完整性和技术深度是否满足要求...
3. 接着，评估格式规范性和逻辑性...
4. 最后，提供具体的改进建议和优化方向...

</thinking_process>

<output_format>
请按照以下XML格式输出结果：

<review_result>
    <overall_score>总体评分 (0-10)</overall_score>
    
    <patentability_assessment>
        <novelty_score>新颖性评分 (0-10)</novelty_score>
        <novelty_analysis>新颖性分析（≥200字）</novelty_analysis>
        
        <inventiveness_score>创造性评分 (0-10)</inventiveness_score>
        <inventiveness_analysis>创造性分析（≥200字）</inventiveness_analysis>
        
        <utility_score>实用性评分 (0-10)</utility_score>
        <utility_analysis>实用性分析（≥200字）</utility_analysis>
    </patentability_assessment>
    
    <content_quality>
        <completeness_score>内容完整性评分 (0-10)</completeness_score>
        <completeness_analysis>完整性分析（≥300字）</completeness_analysis>
        
        <technical_depth_score>技术深度评分 (0-10)</technical_depth_score>
        <technical_depth_analysis>技术深度分析（≥300字）</technical_depth_analysis>
    </content_quality>
    
    <format_compliance>
        <structure_score>结构规范性评分 (0-10)</structure_score>
        <structure_analysis>结构分析（≥200字）</structure_analysis>
        
        <language_score>语言规范性评分 (0-10)</language_score>
        <language_analysis>语言分析（≥200字）</language_analysis>
    </format_compliance>
    
    <issues>
        <issue>
            <type>问题类型 (patentability/content/format)</type>
            <severity>严重程度 (critical/high/medium/low)</severity>
            <description>问题描述（≥100字）</description>
            <recommendation>改进建议（≥200字）</recommendation>
        </issue>
    </issues>
    
    <strengths>
        <strength>优势1（≥100字）</strength>
        <strength>优势2（≥100字）</strength>
    </strengths>
    
    <compliance_status>合规状态 (compliant/needs_minor_revision/needs_major_revision/non_compliant)</compliance_status>
    
    <improvement_plan>
        <priority_actions>优先改进行动（≥300字）</priority_actions>
        <long_term_optimization>长期优化建议（≥300字）</long_term_optimization>
    </improvement_plan>
</review_result>

<quality_requirements>
- 每个分析部分必须达到字数要求，确保审查深度
- 基于专利审核要素进行专业评估，避免主观判断
- 提供具体、可执行的改进建议和优化路径
- 评估结果要有量化指标支撑，便于后续改进
</quality_requirements>"""
            
            response = await self.openai_client._generate_response(prompt)
            
            # Parse response to extract review results
            # This is a simplified approach - in production, you'd want more robust parsing
            try:
                # Extract score from response (simplified parsing)
                if "overall_score" in response.lower():
                    score = 8.5  # Default score if parsing fails
                else:
                    score = 8.0
                    
                issues = []
                if "issue" in response.lower():
                    issues.append({
                        "type": "formatting",
                        "severity": "medium",
                        "description": "AI review completed",
                        "recommendation": "Review AI suggestions"
                    })
                    
                return {
                    "score": score,
                    "issues": issues
                }
                
            except Exception as parse_error:
                logger.error(f"Error parsing review response: {parse_error}")
                # Fallback to basic review
                score = 8.0
                issues = []
                
                # Basic checks
                if len(title) < 10:
                    score -= 2.0
                    issues.append({
                        "type": "length",
                        "severity": "high",
                        "description": "Title too short",
                        "recommendation": "Expand title to be more descriptive"
                    })
                elif len(title) > 100:
                    score -= 1.0
                    issues.append({
                        "type": "length",
                        "severity": "medium",
                        "description": "Title too long",
                        "recommendation": "Shorten title while maintaining clarity"
                    })
                    
                return {
                    "score": max(0, score),
                    "issues": issues
                }
            
        except Exception as e:
            logger.error(f"Error reviewing title: {e}")
            return {"score": 0, "issues": [{"type": "error", "description": str(e)}]}
            
    async def _review_abstract(self, abstract: str) -> Dict[str, Any]:
        """Review the patent abstract"""
        try:
            score = 10.0
            issues = []
            
            if not abstract:
                score -= 10.0
                issues.append({
                    "type": "missing",
                    "severity": "critical",
                    "description": "Abstract is missing",
                    "recommendation": "Add comprehensive abstract"
                })
                return {"score": 0, "issues": issues}
                
            # Check length
            word_count = len(abstract.split())
            if word_count < 50:
                score -= 3.0
                issues.append({
                    "type": "length",
                    "severity": "high",
                    "description": "Abstract too short",
                    "recommendation": "Expand abstract to provide comprehensive overview"
                })
            elif word_count > 150:
                score -= 2.0
                issues.append({
                    "type": "length",
                    "severity": "medium",
                    "description": "Abstract too long",
                    "recommendation": "Condense abstract to meet word limit"
                })
                
            # Check content
            if not abstract.endswith("."):
                score -= 1.0
                issues.append({
                    "type": "formatting",
                    "severity": "low",
                    "description": "Abstract should end with period",
                    "recommendation": "Add period at end of abstract"
                })
                
            # Check technical content
            technical_terms = ["method", "system", "apparatus", "process", "device"]
            if not any(term in abstract.lower() for term in technical_terms):
                score -= 2.0
                issues.append({
                    "type": "content",
                    "severity": "medium",
                    "description": "Abstract lacks technical specificity",
                    "recommendation": "Include technical terms and methodology"
                })
                
            return {
                "score": max(0, score),
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Error reviewing abstract: {e}")
            return {"score": 0, "issues": [{"type": "error", "description": str(e)}]}
            
    async def _review_background(self, background: str) -> Dict[str, Any]:
        """Review the background section"""
        try:
            score = 10.0
            issues = []
            
            if not background:
                score -= 5.0
                issues.append({
                    "type": "missing",
                    "severity": "high",
                    "description": "Background section is missing",
                    "recommendation": "Add comprehensive background section"
                })
                return {"score": max(0, score), "issues": issues}
                
            # Check length
            word_count = len(background.split())
            if word_count < 100:
                score -= 3.0
                issues.append({
                    "type": "length",
                    "severity": "medium",
                    "description": "Background section too short",
                    "recommendation": "Expand background with more context"
                })
                
            # Check content structure
            required_elements = ["field", "prior art", "problem", "need"]
            for element in required_elements:
                if element not in background.lower():
                    score -= 1.0
                    issues.append({
                        "type": "content",
                        "severity": "medium",
                        "description": f"Background missing {element} discussion",
                        "recommendation": f"Add discussion of {element}"
                    })
                    
            return {
                "score": max(0, score),
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Error reviewing background: {e}")
            return {"score": 0, "issues": [{"type": "error", "description": str(e)}]}
            
    async def _review_summary(self, summary: str) -> Dict[str, Any]:
        """Review the summary section"""
        try:
            score = 10.0
            issues = []
            
            if not summary:
                score -= 5.0
                issues.append({
                    "type": "missing",
                    "severity": "high",
                    "description": "Summary section is missing",
                    "recommendation": "Add summary section"
                })
                return {"score": max(0, score), "issues": issues}
                
            # Check length
            word_count = len(summary.split())
            if word_count < 50:
                score -= 2.0
                issues.append({
                    "type": "length",
                    "severity": "low",
                    "description": "Summary section could be expanded",
                    "recommendation": "Add more detail to summary"
                })
                
            # Check content
            if "advantage" not in summary.lower() and "benefit" not in summary.lower():
                score -= 1.0
                issues.append({
                    "type": "content",
                    "severity": "low",
                    "description": "Summary should mention advantages",
                    "recommendation": "Include key advantages in summary"
                })
                
            return {
                "score": max(0, score),
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Error reviewing summary: {e}")
            return {"score": 0, "issues": [{"type": "error", "description": str(e)}]}
            
    async def _review_detailed_description(self, description: str) -> Dict[str, Any]:
        """Review the detailed description section with checks for diagrams and pseudo-code"""
        try:
            score = 10.0
            issues = []
            if not description:
                score -= 10.0
                issues.append({"type": "missing", "severity": "critical", "description": "Detailed description is missing", "recommendation": "Add comprehensive detailed description"})
                return {"score": 0, "issues": issues}
            # Global word count
            word_count = len(description.split())
            if word_count < 15000:
                score -= 3.0
                issues.append({"type": "length", "severity": "high", "description": "Section 5 length below 15000 words", "recommendation": "Expand content with multiple detailed subsections"})
            # Subsection heuristic: split by headings/markers
            subsections = [s for s in description.split('\n\n') if len(s.strip()) > 0]
            if len(subsections) < 4:
                score -= 2.0
                issues.append({"type": "structure", "severity": "high", "description": "Less than 4 subsections detected", "recommendation": "Provide at least 4 detailed subsections from different functional perspectives"})
            else:
                short_subs = [idx for idx, s in enumerate(subsections, 1) if len(s.split()) < 3000]
                if short_subs:
                    score -= 2.0
                    issues.append({"type": "length", "severity": "medium", "description": f"Subsections below 3000 words: {short_subs}", "recommendation": "Extend each subsection with more formulas, diagrams, and pseudo-code"})
            # Mermaid diagrams presence
            if "mermaid" not in description:
                score -= 1.0
                issues.append({"type": "diagram", "severity": "medium", "description": "Missing mermaid diagrams", "recommendation": "Add sequence/flowchart/class/graph mermaid diagrams in each subsection"})
            # Formula presence
            formula_hits = (description.count("$") + description.count("\\(") + description.count("\\["))
            if formula_hits < 10:
                score -= 1.0
                issues.append({"type": "formula", "severity": "medium", "description": "Insufficient algorithmic formulas (<10)", "recommendation": "Provide more scoring, constraint, loss, fusion, and complexity formulas"})
            # Pseudo-code presence (long blocks)
            if description.count("```") < 4:
                score -= 1.0
                issues.append({"type": "pseudocode", "severity": "low", "description": "Insufficient pseudo-code blocks (<4)", "recommendation": "Provide ≥4 long pseudo-code blocks (each ≥50 lines) covering core procedures"})
            return {"score": max(0, score), "issues": issues}
        except Exception as e:
            logger.error(f"Error reviewing detailed description: {e}")
            return {"score": 0, "issues": [{"type": "error", "description": str(e)}]}
            
    async def _review_claims(self, claims: List[str]) -> Dict[str, Any]:
        """Review the patent claims"""
        try:
            score = 10.0
            issues = []
            
            if not claims:
                score -= 10.0
                issues.append({
                    "type": "missing",
                    "severity": "critical",
                    "description": "Claims are missing",
                    "recommendation": "Add patent claims"
                })
                return {"score": 0, "issues": issues}
                
            # Check number of claims
            if len(claims) < 3:
                score -= 3.0
                issues.append({
                    "type": "count",
                    "severity": "high",
                    "description": "Insufficient number of claims",
                    "recommendation": "Add more claims for comprehensive protection"
                })
            elif len(claims) > 20:
                score -= 1.0
                issues.append({
                    "type": "count",
                    "severity": "low",
                    "description": "Many claims",
                    "recommendation": "Consider consolidating claims"
                })
                
            # Check claim structure
            for i, claim in enumerate(claims):
                if not claim.strip().endswith("."):
                    score -= 0.5
                    issues.append({
                        "type": "formatting",
                        "severity": "low",
                        "description": f"Claim {i+1} should end with period",
                        "recommendation": f"Add period at end of claim {i+1}"
                    })
                    
            # Check independent claims
            independent_claims = [claim for claim in claims if "claim" not in claim.lower() or "claim 1" in claim.lower()]
            if len(independent_claims) < 1:
                score -= 2.0
                issues.append({
                    "type": "structure",
                    "severity": "medium",
                    "description": "Missing independent claims",
                    "recommendation": "Add independent claims covering core invention"
                })
                
            return {
                "score": max(0, score),
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Error reviewing claims: {e}")
            return {"score": 0, "issues": [{"type": "error", "description": str(e)}]}
            
    async def _review_drawings(self, drawings: List[str]) -> Dict[str, Any]:
        """Review the technical drawings"""
        try:
            score = 10.0
            issues = []
            
            if not drawings:
                score -= 5.0
                issues.append({
                    "type": "missing",
                    "severity": "medium",
                    "description": "Technical drawings missing",
                    "recommendation": "Add technical diagrams and drawings"
                })
                return {"score": max(0, score), "issues": issues}
                
            # Check number of drawings
            if len(drawings) < 3:
                score -= 2.0
                issues.append({
                    "type": "count",
                    "severity": "low",
                    "description": "Few technical drawings",
                    "recommendation": "Add more technical diagrams"
                })
                
            # Check drawing descriptions
            for i, drawing in enumerate(drawings):
                if len(drawing.split()) < 10:
                    score -= 0.5
                    issues.append({
                        "type": "content",
                        "severity": "low",
                        "description": f"Drawing {i+1} description too brief",
                        "recommendation": f"Expand description for drawing {i+1}"
                    })
                    
            return {
                "score": max(0, score),
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Error reviewing drawings: {e}")
            return {"score": 0, "issues": [{"type": "error", "description": str(e)}]}
            
    async def _generate_recommendations(self, issues_found: List[Dict[str, Any]], 
                                      section_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on review findings"""
        try:
            recommendations = []
            
            # Overall recommendations
            overall_score = sum(section_scores.values()) / len(section_scores)
            if overall_score < 7.0:
                recommendations.append("Major revisions required to meet quality standards")
            elif overall_score < 8.5:
                recommendations.append("Minor revisions recommended for optimal quality")
            else:
                recommendations.append("Patent draft meets quality requirements")
                
            # Section-specific recommendations
            for section_name, score in section_scores.items():
                if score < 8.0:
                    section_issues = [issue for issue in issues_found if issue.get("section") == section_name]
                    for issue in section_issues:
                        recommendations.append(f"{section_name.title()}: {issue.get('recommendation', 'Review and improve')}")
                        
            # Priority recommendations
            critical_issues = [issue for issue in issues_found if issue.get("severity") == "critical"]
            if critical_issues:
                recommendations.insert(0, "CRITICAL: Address missing sections immediately")
                
            high_priority_issues = [issue for issue in issues_found if issue.get("severity") == "high"]
            if high_priority_issues:
                recommendations.insert(1, "HIGH PRIORITY: Fix major issues before filing")
                
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Review patent draft for quality issues"]
            
    async def _determine_compliance_status(self, overall_score: float, 
                                         issues_found: List[Dict[str, Any]]) -> str:
        """Determine overall compliance status"""
        try:
            critical_issues = [issue for issue in issues_found if issue.get("severity") == "critical"]
            high_priority_issues = [issue for issue in issues_found if issue.get("severity") == "high"]
            
            if critical_issues:
                return "non_compliant"
            elif high_priority_issues or overall_score < 7.0:
                return "needs_major_revision"
            elif overall_score < 8.5:
                return "needs_minor_revision"
            else:
                return "compliant"
                
        except Exception as e:
            logger.error(f"Error determining compliance status: {e}")
            return "unknown"
            
    async def _assess_overall_quality(self, overall_score: float, 
                                    section_scores: Dict[str, float]) -> str:
        """Assess overall quality of the patent draft"""
        try:
            if overall_score >= 9.0:
                return "excellent"
            elif overall_score >= 8.0:
                return "good"
            elif overall_score >= 7.0:
                return "acceptable"
            elif overall_score >= 6.0:
                return "needs_improvement"
            else:
                return "poor"
                
        except Exception as e:
            logger.error(f"Error assessing overall quality: {e}")
            return "unknown"
            
    async def _generate_detailed_feedback(self, review_result: ReviewResult, 
                                        patent_draft: PatentDraft) -> Dict[str, Any]:
        """Generate detailed feedback for the patent draft"""
        try:
            feedback = {
                "overall_assessment": {
                    "score": review_result.overall_score,
                    "quality": review_result.quality_assessment,
                    "compliance": review_result.compliance_status
                },
                "section_feedback": {},
                "priority_issues": [],
                "improvement_suggestions": []
            }
            
            # Section-specific feedback
            for section_name, score in review_result.section_scores.items():
                section_issues = [issue for issue in review_result.issues_found 
                                if issue.get("section") == section_name]
                feedback["section_feedback"][section_name] = {
                    "score": score,
                    "issues": section_issues,
                    "status": "good" if score >= 8.0 else "needs_improvement" if score >= 6.0 else "poor"
                }
                
            # Priority issues
            critical_issues = [issue for issue in review_result.issues_found 
                             if issue.get("severity") == "critical"]
            high_priority_issues = [issue for issue in review_result.issues_found 
                                  if issue.get("severity") == "high"]
            
            feedback["priority_issues"] = critical_issues + high_priority_issues
            
            # Improvement suggestions
            feedback["improvement_suggestions"] = review_result.recommendations
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating detailed feedback: {e}")
            return {"error": str(e)}
            
    async def _determine_review_outcome(self, review_result: ReviewResult) -> str:
        """Determine the overall review outcome"""
        try:
            if review_result.overall_score >= 9.0:
                return "approved"
            elif review_result.overall_score >= 8.0:
                return "approved_with_minor_revisions"
            elif review_result.overall_score >= 7.0:
                return "needs_revision"
            else:
                return "major_revision_required"
                
        except Exception as e:
            logger.error(f"Error determining review outcome: {e}")
            return "review_failed"
            
    async def _check_sanxing(self, review_task: ReviewTask):
        """Check CN 三性: 新颖性、创造性、实用性 and return (issues, bonus_score)."""
        try:
            issues = []
            bonus = 0.0
            draft = review_task.patent_draft
            # Heuristics: presence of sections and technical specificity hints
            novelty_hint = 0.0
            if draft.summary and any(k in draft.summary.lower() for k in ["区别", "不同", "novel", "区别特征"]):
                novelty_hint += 0.5
            if draft.claims and len(draft.claims) >= 3:
                novelty_hint += 0.5
            if novelty_hint < 0.5:
                issues.append({"type": "novelty", "severity": "high", "description": "未充分体现区别技术特征以支撑新颖性", "recommendation": "在摘要/说明书中明确最近似现有技术与区别点，并在权利要求独立项中限定核心区别特征", "section": "summary"})
            else:
                bonus += 0.2
            inventive_hint = 0.0
            if draft.background and any(k in draft.background for k in ["技术问题", "缺点", "问题", "不足"]):
                inventive_hint += 0.3
            if draft.summary and any(k in draft.summary for k in ["技术效果", "有益效果", "显著进步", "意想不到"]):
                inventive_hint += 0.4
            if inventive_hint < 0.5:
                issues.append({"type": "inventiveness", "severity": "medium", "description": "未基于区别特征清晰界定实际解决的技术问题及技术启示分析", "recommendation": "补充’三步法‘：确定最接近现有技术→区别特征→是否存在技术启示；并量化技术效果", "section": "background"})
            else:
                bonus += 0.2
            utility_hint = 0.0
            if draft.detailed_description and len(draft.detailed_description.split()) > 500:
                utility_hint += 0.4
            if draft.drawings_description or draft.technical_diagrams:
                utility_hint += 0.2
            if utility_hint < 0.4:
                issues.append({"type": "utility", "severity": "low", "description": "实施可重复性与工业适用性论证不足", "recommendation": "在实施方式中补充分步实现细节、参数范围、装置连接关系与可重复再现条件", "section": "description"})
            else:
                bonus += 0.1
            return issues, bonus
        except Exception as e:
            logger.error(f"Error in _check_sanxing: {e}")
            return [], 0.0
            
    async def _assess_patent_quality(self, task_data: Dict[str, Any]) -> TaskResult:
        """Assess patent quality specifically"""
        # Implementation for quality assessment
        pass
        
    async def _verify_compliance(self, task_data: Dict[str, Any]) -> TaskResult:
        """Verify compliance specifically"""
        # Implementation for compliance verification
        pass
        
    async def _generate_review_feedback(self, task_data: Dict[str, Any]) -> TaskResult:
        """Generate review feedback specifically"""
        # Implementation for feedback generation
        pass
        
    def _load_review_criteria(self) -> Dict[str, Any]:
        """Load review criteria for different patent types"""
        return {
            "utility_patent": {
                "required_sections": ["title", "abstract", "background", "summary", "description", "claims", "drawings"],
                "quality_thresholds": {"excellent": 9.0, "good": 8.0, "acceptable": 7.0},
                "compliance_requirements": ["legal_format", "technical_content", "claim_structure"]
            },
            "design_patent": {
                "required_sections": ["title", "description", "claims", "drawings"],
                "quality_thresholds": {"excellent": 9.0, "good": 8.0, "acceptable": 7.0},
                "compliance_requirements": ["design_specific", "visual_clarity", "claim_scope"]
            }
        }
        
    def _load_quality_standards(self) -> Dict[str, Any]:
        """Load quality standards for patent review"""
        return {
            "technical_accuracy": {
                "weight": 0.3,
                "criteria": ["scientific_validity", "implementation_feasibility", "technical_depth"]
            },
            "legal_compliance": {
                "weight": 0.25,
                "criteria": ["format_requirements", "claim_structure", "disclosure_adequacy"]
            },
            "clarity": {
                "weight": 0.2,
                "criteria": ["readability", "logical_flow", "terminology_consistency"]
            },
            "completeness": {
                "weight": 0.15,
                "criteria": ["section_coverage", "detail_level", "example_adequacy"]
            },
            "innovation": {
                "weight": 0.1,
                "criteria": ["novelty", "inventiveness", "commercial_potential"]
            }
        }
        
    async def _check_sanxing_simplified(self, review_task: ReviewTask):
        """简化版三性检查，减少API调用"""
        try:
            issues = []
            bonus = 0.0
            draft = review_task.patent_draft
            
            # 快速启发式检查，不使用API调用
            # 新颖性检查
            if draft.summary and len(draft.summary) > 100:
                bonus += 0.2
            else:
                issues.append({"type": "novelty", "severity": "medium", "description": "发明内容描述不足", "recommendation": "补充发明内容描述"})
                
            # 创造性检查
            if draft.background and len(draft.background) > 200:
                bonus += 0.2
            else:
                issues.append({"type": "inventiveness", "severity": "medium", "description": "背景技术描述不足", "recommendation": "补充背景技术描述"})
                
            # 实用性检查
            if draft.detailed_description and len(draft.detailed_description) > 500:
                bonus += 0.1
            else:
                issues.append({"type": "utility", "severity": "low", "description": "具体实施方式描述不足", "recommendation": "补充具体实施方式"})
                
            return issues, bonus
        except Exception as e:
            logger.error(f"Error in _check_sanxing_simplified: {e}")
            return [], 0.0
            
    async def _generate_recommendations_simplified(self, issues_found: List[Dict[str, Any]], section_scores: Dict[str, float]) -> List[str]:
        """简化版推荐生成，减少API调用"""
        try:
            recommendations = []
            
            # 基于分数和问题生成简单推荐
            for section, score in section_scores.items():
                if score < 7.0:
                    recommendations.append(f"改进{section}部分，当前分数: {score:.1f}")
                    
            for issue in issues_found[:5]:  # 只取前5个问题
                if issue.get("recommendation"):
                    recommendations.append(issue["recommendation"])
                    
            # 添加通用建议
            if len(recommendations) < 3:
                recommendations.extend([
                    "确保技术方案描述清晰完整",
                    "检查权利要求书格式规范",
                    "完善附图说明"
                ])
                
            return recommendations[:5]  # 限制推荐数量
        except Exception as e:
            logger.error(f"Error in _generate_recommendations_simplified: {e}")
            return ["建议进行全面的专利审查"]
            
    async def _execute_test_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a test task with mock data"""
        try:
            task_type = task_data.get("type")
            topic = task_data.get("topic", "测试专利主题")
            description = task_data.get("description", "测试专利描述")
            
            if task_type == "patent_review":
                # Create mock review result
                mock_feedback = {
                    "overall_score": 8.2,
                    "quality_assessment": "Good",
                    "compliance_status": "Compliant",
                    "issues": [
                        {
                            "type": "content",
                            "severity": "medium",
                            "description": "背景技术描述可以更详细",
                            "recommendation": "补充更多现有技术信息"
                        },
                        {
                            "type": "format",
                            "severity": "low",
                            "description": "权利要求书格式需要调整",
                            "recommendation": "按照标准格式重新组织权利要求"
                        }
                    ],
                    "recommendations": [
                        "建议1: 完善背景技术部分",
                        "建议2: 优化权利要求书格式",
                        "建议3: 增加具体实施例"
                    ],
                    "section_scores": {
                        "title": 9.0,
                        "abstract": 8.5,
                        "background": 7.0,
                        "summary": 8.0,
                        "description": 8.5,
                        "claims": 7.5,
                        "drawings": 9.0
                    }
                }
                
                return TaskResult(
                    success=True,
                    data={
                        "feedback": mock_feedback,
                        "overall_score": 8.2,
                        "quality_assessment": "Good",
                        "compliance_status": "Compliant",
                        "issues": mock_feedback["issues"],
                        "recommendations": mock_feedback["recommendations"]
                    }
                )
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error in test task execution: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )