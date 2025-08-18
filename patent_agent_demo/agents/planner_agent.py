"""
Planner Agent for Patent Agent System
Analyzes patent topics and creates comprehensive development strategies
"""

import asyncio
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..openai_client import OpenAIClient
from ..google_a2a_client import PatentAnalysis

logger = logging.getLogger(__name__)

@dataclass
class PatentStrategy:
    """Patent development strategy"""
    topic: str
    description: str
    novelty_score: float
    inventive_step_score: float
    patentability_assessment: str
    development_phases: List[Dict[str, Any]]
    key_innovation_areas: List[str]
    competitive_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timeline_estimate: str
    resource_requirements: Dict[str, Any]
    success_probability: float

@dataclass
class DevelopmentPhase:
    """Development phase definition"""
    phase_name: str
    duration_estimate: str
    key_deliverables: List[str]
    dependencies: List[str]
    resource_requirements: Dict[str, Any]
    success_criteria: List[str]

class PlannerAgent(BaseAgent):
    """Agent responsible for patent planning and strategy development"""
    
    def __init__(self, test_mode: bool = False):
        super().__init__(
            name="planner_agent",
            capabilities=["patent_planning", "strategy_development", "risk_assessment", "timeline_planning"],
            test_mode=test_mode
        )
        self.openai_client = None
        self.strategy_templates = self._load_strategy_templates()
        
    async def start(self):
        """Start the planner agent"""
        await super().start()
        self.openai_client = OpenAIClient()
        logger.info("Planner Agent started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute patent planning tasks"""
        try:
            task_type = task_data.get("type")
            
            if task_type == "patent_planning":
                topic = task_data.get("topic", "Unknown Topic")
                description = task_data.get("description", "No description provided")
                
                # Get context information if available
                context_data = getattr(self, 'current_context', {})
                theme_definition = context_data.get("theme_definition")
                
                if theme_definition:
                    logger.info(f"Using context theme: {theme_definition.primary_title}")
                    # Use context to ensure consistency
                    topic = theme_definition.primary_title
                    description = f"{description} 核心概念：{theme_definition.core_concept}"
                
                # 智能生成description：如果没有description或description太简单，通过大模型API生成
                if not description or description == "No description provided" or description == f"Patent for topic: {topic}":
                    logger.info(f"Auto-generating detailed description for topic: {topic} using AI model")
                    generated_description = await self._generate_description_from_topic(topic)
                    if generated_description:
                        description = generated_description
                        logger.info(f"Generated description: {description[:100]}...")
                    else:
                        logger.warning(f"Failed to generate description for topic: {topic}, using fallback")
                        description = f"Patent for topic: {topic}"
                
                logger.info(f"Creating patent strategy for: {topic}")
                logger.info(f"Description: {description[:100]}...")
                logger.info(f"Starting patent analysis...")
                
                # Analyze patent topic using GLM
                logger.info(f"Calling GLM API for patent analysis...")
                analysis = await self.openai_client.analyze_patent_topic(topic, description)
                logger.info(f"GLM API call completed successfully")
                
                # Create development strategy
                logger.info(f"Creating development strategy...")
                strategy = await self._develop_strategy(topic, description, analysis)
                logger.info(f"Development strategy created")
                
                # Create development phases
                logger.info(f"Creating development phases...")
                phases = await self._create_development_phases(strategy)
                logger.info(f"Development phases created")
                
                # Assess risks and competitive landscape
                logger.info(f"Assessing risks and competitive landscape...")
                risk_assessment = await self._assess_competitive_risks(strategy, analysis)
                logger.info(f"Risk assessment completed")
                
                # Estimate timeline and resources
                logger.info(f"Estimating timeline and resources...")
                timeline_estimate = await self._estimate_timeline(phases)
                resource_requirements = await self._estimate_resources(phases)
                logger.info(f"Timeline and resource estimation completed")
                
                # Calculate success probability
                logger.info(f"Calculating success probability...")
                success_probability = await self._calculate_success_probability(strategy, risk_assessment)
                logger.info(f"Success probability calculated: {success_probability}")
                
                # Compile final strategy
                logger.info(f"Compiling final strategy...")
                final_strategy = PatentStrategy(
                    topic=topic,
                    description=description,
                    novelty_score=analysis.novelty_score,
                    inventive_step_score=analysis.inventive_step_score,
                    patentability_assessment=analysis.patentability_assessment,
                    development_phases=phases,
                    key_innovation_areas=getattr(strategy, 'key_innovation_areas', []),
                    competitive_analysis=risk_assessment.get("competitive_analysis", {}),
                    risk_assessment=risk_assessment,
                    timeline_estimate=timeline_estimate,
                    resource_requirements=resource_requirements,
                    success_probability=success_probability
                )
                
                logger.info(f"Patent strategy creation completed successfully")
                
                return TaskResult(
                    success=True,
                    data={
                        "strategy": final_strategy,
                        "analysis": analysis,
                        "recommendations": analysis.recommendations
                    },
                    metadata={
                        "strategy_type": "comprehensive_patent_strategy",
                        "generation_timestamp": asyncio.get_event_loop().time()
                    }
                )
                
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error creating patent strategy: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _create_patent_strategy(self, task_data: Dict[str, Any]) -> TaskResult:
        """Create a comprehensive patent strategy"""
        try:
            topic = task_data.get("topic")
            description = task_data.get("description")
            
            if not topic or not description:
                return TaskResult(
                    success=False,
                    data={},
                    error_message="Topic and description are required"
                )
                
            logger.info(f"Creating patent strategy for: {topic}")
            logger.info(f"Starting patent analysis...")
            
            # Analyze patent topic using GLM
            logger.info(f"Calling GLM API for patent analysis...")
            analysis = await self.openai_client.analyze_patent_topic(topic, description)
            logger.info(f"GLM API call completed successfully")
            
            # Create development strategy
            logger.info(f"Creating development strategy...")
            strategy = await self._develop_strategy(topic, description, analysis)
            logger.info(f"Development strategy created")
            
            # Create development phases
            logger.info(f"Creating development phases...")
            phases = await self._create_development_phases(strategy)
            logger.info(f"Development phases created")
            
            # Assess risks and competitive landscape
            logger.info(f"Assessing risks and competitive landscape...")
            risk_assessment = await self._assess_competitive_risks(strategy, analysis)
            logger.info(f"Risk assessment completed")
            
            # Estimate timeline and resources
            logger.info(f"Estimating timeline and resources...")
            timeline_estimate = await self._estimate_timeline(phases)
            resource_requirements = await self._estimate_resources(phases)
            logger.info(f"Timeline and resource estimation completed")
            
            # Calculate success probability
            logger.info(f"Calculating success probability...")
            success_probability = await self._calculate_success_probability(strategy, risk_assessment)
            logger.info(f"Success probability calculated: {success_probability}")
            
            # Compile final strategy
            logger.info(f"Compiling final strategy...")
            final_strategy = PatentStrategy(
                topic=topic,
                description=description,
                novelty_score=analysis.novelty_score,
                inventive_step_score=analysis.inventive_step_score,
                patentability_assessment=analysis.patentability_assessment,
                development_phases=phases,
                key_innovation_areas=getattr(strategy, 'key_innovation_areas', []),
                competitive_analysis=risk_assessment.get("competitive_analysis", {}),
                risk_assessment=risk_assessment,
                timeline_estimate=timeline_estimate,
                resource_requirements=resource_requirements,
                success_probability=success_probability
            )
            
            logger.info(f"Patent strategy creation completed successfully")
            
            return TaskResult(
                success=True,
                data={
                    "strategy": final_strategy,
                    "analysis": analysis,
                    "recommendations": analysis.recommendations
                },
                metadata={
                    "strategy_type": "comprehensive_patent_strategy",
                    "generation_timestamp": asyncio.get_event_loop().time()
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating patent strategy: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _develop_strategy(self, topic: str, description: str, 
                               analysis: PatentAnalysis) -> Dict[str, Any]:
        """Develop the core strategy based on analysis"""
        try:
            # Identify key innovation areas
            key_innovation_areas = await self._identify_innovation_areas(topic, description, analysis)
            
            # Define strategic objectives
            strategic_objectives = [
                "Maximize patent protection coverage",
                "Ensure novelty and inventive step requirements",
                "Minimize prior art conflicts",
                "Optimize claim structure for enforcement",
                "Prepare for international filing strategy"
            ]
            
            # Create competitive positioning
            competitive_positioning = {
                "unique_value_proposition": f"Novel approach to {topic}",
                "competitive_advantages": [
                    f"Higher {analysis.novelty_score}/10 novelty score",
                    f"Strong {analysis.inventive_step_score}/10 inventive step",
                    "Clear industrial applicability"
                ],
                "market_differentiation": "First-mover advantage in this specific area"
            }
            
            return {
                "key_innovation_areas": key_innovation_areas,
                "strategic_objectives": strategic_objectives,
                "competitive_positioning": competitive_positioning,
                "patentability_factors": {
                    "novelty": analysis.novelty_score,
                    "inventive_step": analysis.inventive_step_score,
                    "industrial_applicability": analysis.industrial_applicability
                }
            }
            
        except Exception as e:
            logger.error(f"Error developing strategy: {e}")
            raise
            
    async def _identify_innovation_areas(self, topic: str, description: str, 
                                       analysis: PatentAnalysis) -> List[str]:
        """Identify key areas of innovation using optimized prompts"""
        try:
            # 基于专利审核要素和Anthropic技巧的优化提示词
            prompt = f"""<system>
你是一位专业的专利策略分析师，负责专利撰写的整体规划和策略制定。

<role_definition>
- 专利性评估专家：基于新颖性、创造性、实用性进行深度分析
- 技术架构师：设计完整的技术方案和实施路径
- 质量把控师：确保满足专利审核的所有要求

<patent_standards>
- 新颖性：技术方案在世界范围内前所未有，不属于现有技术
- 创造性：与现有技术相比具有突出的实质性特点和显著进步
- 实用性：能够制造或使用，并产生积极的技术、经济或社会效果

<work_style>
- 系统性思考：从整体到细节，从宏观到微观
- 数据驱动：基于事实分析，避免主观判断
- 前瞻性规划：考虑长期发展和技术演进
- 风险意识：主动识别潜在问题和风险点
</system>

<task>
请为专利主题"{topic}"进行全面的创新领域分析和策略规划。

<context>
专利描述：{description}
新颖性评分：{analysis.novelty_score}/10
创造性评分：{analysis.inventive_step_score}/10

<thinking_process>
让我按照以下步骤进行深度分析：

1. 首先，分析技术方案的核心内容和技术特点...
2. 然后，基于专利"三性"标准评估创新价值...
3. 接着，识别最具保护价值的技术突破点...
4. 最后，制定完整的专利保护策略...

</thinking_process>

<output_requirements>
- 创新领域分析：≥1000字，包含技术突破、创新价值、保护必要性
- 技术路线规划：≥1000字，包含实施路径、关键技术、发展阶段
- 竞争策略制定：≥1000字，包含市场定位、竞争优势、风险应对

<output_format>
请按照以下XML格式输出结果：

<innovation_analysis>
    <core_innovation>
        <name>核心创新领域名称</name>
        <description>创新点详细描述（≥300字）</description>
        <novelty_analysis>新颖性分析（≥200字）</novelty_analysis>
        <inventiveness_analysis>创造性分析（≥200字）</inventiveness_analysis>
        <utility_analysis>实用性分析（≥200字）</utility_analysis>
        <protection_priority>保护优先级 (High/Medium/Low)</protection_priority>
    </core_innovation>
    
    <technical_roadmap>
        <implementation_path>技术实施路径（≥500字）</implementation_path>
        <key_technologies>关键技术要素（≥300字）</key_technologies>
        <development_stages>发展阶段规划（≥200字）</development_stages>
    </technical_roadmap>
    
    <competitive_strategy>
        <market_positioning>市场定位分析（≥300字）</market_positioning>
        <competitive_advantages>竞争优势分析（≥400字）</competitive_advantages>
        <risk_mitigation>风险应对策略（≥300字）</risk_mitigation>
    </competitive_strategy>
</innovation_analysis>

<quality_standards>
- 内容深度：每个分析部分必须达到字数要求
- 技术准确性：基于专利审核标准进行专业评估
- 逻辑性：分析过程逻辑清晰，结论有据可依
- 实用性：策略建议具有可操作性和指导价值
</quality_standards>"""
            
            response = await self.openai_client._generate_response(prompt)
            
            # Parse response to extract innovation areas
            # This is a simplified approach - in production, you'd want more robust parsing
            innovation_areas = [
                "Core algorithm innovation",
                "System architecture design",
                "Integration methodology",
                "Performance optimization",
                "Scalability features"
            ]
            
            return innovation_areas
            
        except Exception as e:
            logger.error(f"Error identifying innovation areas: {e}")
            # Return default areas if AI analysis fails
            return ["Core technology", "Implementation method", "System design"]
            
    async def _create_development_phases(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create development phases for the patent strategy"""
        try:
            phases = [
                {
                    "phase_name": "Drafting & Review",
                    "duration_estimate": "3-4 weeks",
                    "key_deliverables": [
                        "Patent application draft",
                        "Technical diagrams",
                        "Review feedback incorporated"
                    ],
                    "dependencies": ["Strategy Development"],
                    "resource_requirements": {
                        "patent_attorneys": 2,
                        "technical_writers": 1,
                        "illustrators": 1
                    },
                    "success_criteria": [
                        "Draft meets legal requirements",
                        "Technical accuracy verified",
                        "Stakeholder approval obtained"
                    ]
                },
                {
                    "phase_name": "Filing & Prosecution",
                    "duration_estimate": "Ongoing",
                    "key_deliverables": [
                        "Patent application filed",
                        "Office action responses",
                        "Patent granted"
                    ],
                    "dependencies": ["Drafting & Review"],
                    "resource_requirements": {
                        "patent_attorneys": 1,
                        "paralegals": 1
                    },
                    "success_criteria": [
                        "Application successfully filed",
                        "Office actions responded to",
                        "Patent granted or allowed"
                    ]
                }
            ]
            return phases
            
        except Exception as e:
            logger.error(f"Error creating development phases: {e}")
            raise
            
    async def _assess_competitive_risks(self, strategy: Dict[str, Any], 
                                      analysis: PatentAnalysis) -> Dict[str, Any]:
        """Assess competitive risks and market challenges"""
        try:
            risk_factors = {
                "prior_art_risks": {
                    "probability": "Medium",
                    "impact": "High",
                    "mitigation": "Comprehensive prior art search and analysis"
                },
                "competitive_filing_risks": {
                    "probability": "Medium",
                    "impact": "Medium",
                    "mitigation": "Accelerated filing strategy"
                },
                "technology_obsolescence": {
                    "probability": "Low",
                    "impact": "Medium",
                    "mitigation": "Focus on fundamental innovations"
                },
                "enforcement_challenges": {
                    "probability": "Medium",
                    "impact": "High",
                    "mitigation": "Strong claim structure and documentation"
                }
            }
            
            competitive_analysis = {
                "market_position": "Emerging technology leader",
                "competitive_advantages": strategy.get("competitive_positioning", {}).get("competitive_advantages", []),
                "threat_level": "Medium",
                "response_strategy": "Proactive patent protection and market positioning"
            }
            
            return {
                "risk_factors": risk_factors,
                "competitive_analysis": competitive_analysis,
                "overall_risk_level": "Medium",
                "risk_mitigation_strategies": [
                    "Comprehensive prior art analysis",
                    "Strong patent documentation",
                    "Strategic filing timeline",
                    "Ongoing competitive monitoring"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error assessing competitive risks: {e}")
            raise
            
    async def _estimate_timeline(self, phases: List[Dict[str, Any]]) -> str:
        """Estimate overall timeline for patent development"""
        try:
            total_duration = "3-6 months"
            
            # Calculate based on phases
            phase_durations = {
                "Research & Analysis": "2-3 weeks",
                "Strategy Development": "1-2 weeks", 
                "Drafting & Review": "3-4 weeks",
                "Filing & Prosecution": "Ongoing (6-18 months)"
            }
            
            return f"Total development time: {total_duration}, Filing to grant: 6-18 months"
            
        except Exception as e:
            logger.error(f"Error estimating timeline: {e}")
            return "3-6 months (development) + 6-18 months (prosecution)"
            
    async def _estimate_resources(self, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        try:
            total_resources = {
                "patent_attorneys": 2,
                "researchers": 2,
                "technical_experts": 1,
                "technical_writers": 1,
                "illustrators": 1,
                "paralegals": 1,
                "strategists": 1
            }
            
            estimated_costs = {
                "legal_fees": "$15,000 - $25,000",
                "filing_fees": "$1,000 - $4,000",
                "technical_services": "$5,000 - $10,000",
                "total_estimated": "$21,000 - $39,000"
            }
            
            return {
                "human_resources": total_resources,
                "estimated_costs": estimated_costs,
                "resource_allocation": "Phased approach with peak during drafting phase"
            }
            
        except Exception as e:
            logger.error(f"Error estimating resources: {e}")
            raise
            
    async def _calculate_success_probability(self, strategy: Dict[str, Any], 
                                          risk_assessment: Dict[str, Any]) -> float:
        """Calculate probability of successful patent development"""
        try:
            # Base success probability
            base_probability = 0.75
            
            # Adjust based on novelty score (assuming it's normalized 0-1)
            novelty_factor = min(strategy.get("patentability_factors", {}).get("novelty", 8.5) / 10, 1.0)
            
            # Adjust based on risk level
            risk_level = risk_assessment.get("overall_risk_level", "Medium")
            risk_factors = {
                "Low": 1.1,
                "Medium": 1.0,
                "High": 0.8
            }
            risk_factor = risk_factors.get(risk_level, 1.0)
            
            # Calculate final probability
            success_probability = base_probability * novelty_factor * risk_factor
            
            # Ensure it's within reasonable bounds
            return max(0.1, min(0.95, success_probability))
            
        except Exception as e:
            logger.error(f"Error calculating success probability: {e}")
            return 0.7  # Default fallback
            
    def _load_strategy_templates(self) -> Dict[str, Any]:
        """Load strategy templates for different patent types"""
        return {
            "software_patent": {
                "focus_areas": ["Algorithm", "System Architecture", "User Interface"],
                "special_considerations": ["Abstract idea exceptions", "Technical implementation details"]
            },
            "hardware_patent": {
                "focus_areas": ["Physical structure", "Material composition", "Manufacturing process"],
                "special_considerations": ["Prior art in related fields", "Industrial applicability"]
            },
            "biotech_patent": {
                "focus_areas": ["Biological process", "Chemical composition", "Medical application"],
                "special_considerations": ["Ethical considerations", "Regulatory compliance"]
            }
        }
        
    async def _optimize_strategy(self, task_data: Dict[str, Any]) -> TaskResult:
        """Optimize an existing patent strategy"""
        # Implementation for strategy optimization
        pass
        
    async def _assess_risks(self, task_data: Dict[str, Any]) -> TaskResult:
        """Assess risks for a specific patent topic"""
        # Implementation for risk assessment
        pass
        
    async def _create_timeline(self, task_data: Dict[str, Any]) -> TaskResult:
        """Create detailed timeline for patent development"""
        # Implementation for timeline creation
        pass
        
    async def _generate_description_from_topic(self, topic: str) -> str:
        """Generate detailed technical description based on topic using AI model"""
        try:
            logger.info(f"Generating description for topic: {topic} using AI model")
            
            # 构建prompt用于大模型生成description
            prompt = f"""
请为以下专利主题生成一个详细的技术描述，要求：

1. 描述要专业、准确，体现技术深度
2. 包含主要技术特点、技术优势和应用领域
3. 语言要符合专利文档的规范
4. 长度控制在200-300字左右

专利主题：{topic}

请生成详细的技术描述：
"""
            
            # 调用大模型API生成description
            if self.openai_client:
                logger.info(f"Calling AI model to generate description for topic: {topic}")
                generated_description = await self.openai_client._generate_response(prompt)
                
                if generated_description and len(generated_description.strip()) > 50:
                    logger.info(f"Successfully generated description using AI model, length: {len(generated_description)}")
                    return generated_description.strip()
                else:
                    logger.warning(f"AI model generated description too short or empty: {generated_description}")
                    return ""
            else:
                logger.error("OpenAI client not available for description generation")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating description from topic using AI model: {e}")
            return ""
    
    async def _execute_test_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a test task with mock data"""
        try:
            task_type = task_data.get("type")
            topic = task_data.get("topic", "测试专利主题")
            description = task_data.get("description", "测试专利描述")
            
            # 在test_mode下，如果description太简单，使用简单的fallback，不调用大模型
            if not description or description == "No description provided" or description == f"Patent for topic: {topic}":
                logger.info(f"Test mode: using simple fallback description for topic: {topic}")
                description = f"Patent for topic: {topic}"
            
            if task_type == "patent_planning":
                # Create mock strategy data
                mock_strategy = PatentStrategy(
                    topic=topic,
                    description=description,
                    novelty_score=8.5,
                    inventive_step_score=7.8,
                    patentability_assessment="Strong",
                    development_phases=[
                        {
                            "phase_name": "Drafting & Review",
                            "duration_estimate": "3-4 weeks",
                            "key_deliverables": ["Patent application draft", "Technical diagrams", "Review feedback incorporated"],
                            "dependencies": ["Strategy Development"],
                            "resource_requirements": {"patent_attorneys": 2, "technical_writers": 1, "illustrators": 1},
                            "success_criteria": ["Draft meets legal requirements", "Technical accuracy verified", "Stakeholder approval obtained"]
                        }
                    ],
                    key_innovation_areas=["Core algorithm innovation", "System architecture design", "Integration methodology"],
                    competitive_analysis={
                        "market_position": "Emerging technology leader",
                        "competitive_advantages": ["Higher novelty score", "Strong inventive step", "Clear industrial applicability"],
                        "threat_level": "Medium",
                        "response_strategy": "Proactive patent protection and market positioning"
                    },
                    risk_assessment={
                        "risk_factors": {
                            "prior_art_risks": {"probability": "Medium", "impact": "High", "mitigation": "Comprehensive prior art search"},
                            "competitive_filing_risks": {"probability": "Medium", "impact": "Medium", "mitigation": "Accelerated filing strategy"}
                        },
                        "overall_risk_level": "Medium",
                        "risk_mitigation_strategies": ["Comprehensive prior art analysis", "Strong patent documentation"]
                    },
                    timeline_estimate="Total development time: 3-6 months, Filing to grant: 6-18 months",
                    resource_requirements={
                        "human_resources": {"patent_attorneys": 2, "researchers": 2, "technical_experts": 1},
                        "estimated_costs": {"total_estimated": "$21,000 - $39,000"},
                        "resource_allocation": "Phased approach with peak during drafting phase"
                    },
                    success_probability=0.75
                )
                
                # Create mock analysis
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
                
                return TaskResult(
                    success=True,
                    data={
                        "strategy": mock_strategy,
                        "analysis": mock_analysis,
                        "recommendations": ["Improve claim specificity", "Add more technical details"]
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

