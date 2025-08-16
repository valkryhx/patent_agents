"""
Context Manager for Patent Agent System
Manages context consistency and theme alignment across all agents
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import hashlib

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Context types for different aspects of patent development"""
    THEME_DEFINITION = "theme_definition"
    TERMINOLOGY = "terminology"
    TECHNICAL_DOMAIN = "technical_domain"
    INNOVATION_POINTS = "innovation_points"
    PRIOR_ART = "prior_art"
    CLAIMS_FOCUS = "claims_focus"
    IMPLEMENTATION = "implementation"

@dataclass
class ContextItem:
    """Individual context item"""
    context_type: ContextType
    key: str
    value: Any
    source_agent: str
    timestamp: float
    confidence: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThemeDefinition:
    """Patent theme definition with consistency constraints"""
    primary_title: str
    alternative_titles: List[str]
    core_concept: str
    technical_domain: str
    key_innovations: List[str]
    target_applications: List[str]
    terminology_standard: Dict[str, str]
    consistency_rules: List[str]

@dataclass
class ContextSnapshot:
    """Snapshot of current context state"""
    workflow_id: str
    timestamp: float
    theme_definition: ThemeDefinition
    context_items: Dict[ContextType, List[ContextItem]]
    consistency_score: float
    validation_errors: List[str]

class ContextManager:
    """Manages context consistency across patent development workflow"""
    
    def __init__(self):
        self.active_contexts: Dict[str, Dict[ContextType, List[ContextItem]]] = {}
        self.theme_definitions: Dict[str, ThemeDefinition] = {}
        self.consistency_rules: Dict[str, List[str]] = {}
        self.validation_history: Dict[str, List[ContextSnapshot]] = {}
        self.terminology_registry: Dict[str, Dict[str, str]] = {}
        
    async def initialize_workflow_context(self, workflow_id: str, topic: str, description: str) -> ThemeDefinition:
        """Initialize context for a new workflow"""
        try:
            logger.info(f"Initializing context for workflow {workflow_id}")
            
            # Create theme definition
            theme = await self._create_theme_definition(topic, description)
            self.theme_definitions[workflow_id] = theme
            
            # Initialize context structure
            self.active_contexts[workflow_id] = {
                context_type: [] for context_type in ContextType
            }
            
            # Add initial context items
            await self._add_initial_context_items(workflow_id, theme)
            
            # Initialize terminology registry
            self.terminology_registry[workflow_id] = theme.terminology_standard.copy()
            
            logger.info(f"Context initialized for workflow {workflow_id}")
            return theme
            
        except Exception as e:
            logger.error(f"Error initializing context for workflow {workflow_id}: {e}")
            raise
            
    async def _create_theme_definition(self, topic: str, description: str) -> ThemeDefinition:
        """Create a comprehensive theme definition"""
        try:
            # Extract core concept from topic and description
            core_concept = await self._extract_core_concept(topic, description)
            
            # Generate alternative titles
            alternative_titles = await self._generate_alternative_titles(topic, core_concept)
            
            # Identify technical domain
            technical_domain = await self._identify_technical_domain(topic, description)
            
            # Extract key innovations
            key_innovations = await self._extract_key_innovations(description)
            
            # Identify target applications
            target_applications = await self._identify_target_applications(description)
            
            # Create terminology standard
            terminology_standard = await self._create_terminology_standard(topic, description)
            
            # Define consistency rules
            consistency_rules = [
                f"所有内容必须围绕核心概念：{core_concept}",
                f"技术领域必须限定在：{technical_domain}",
                "术语使用必须遵循术语标准",
                "创新点必须与已识别的关键创新保持一致",
                "应用场景必须与目标应用领域相关"
            ]
            
            return ThemeDefinition(
                primary_title=topic,
                alternative_titles=alternative_titles,
                core_concept=core_concept,
                technical_domain=technical_domain,
                key_innovations=key_innovations,
                target_applications=target_applications,
                terminology_standard=terminology_standard,
                consistency_rules=consistency_rules
            )
            
        except Exception as e:
            logger.error(f"Error creating theme definition: {e}")
            raise
            
    async def _extract_core_concept(self, topic: str, description: str) -> str:
        """Extract the core concept from topic and description"""
        # Simple extraction logic - can be enhanced with NLP
        keywords = ["系统", "方法", "装置", "技术", "算法", "模型"]
        for keyword in keywords:
            if keyword in topic:
                return f"{topic}的核心技术"
        return f"{topic}的创新方法"
        
    async def _generate_alternative_titles(self, topic: str, core_concept: str) -> List[str]:
        """Generate alternative titles for consistency"""
        alternatives = []
        
        # Generate variations based on topic content
        topic_lower = topic.lower()
        
        # Check for common technology patterns
        if any(keyword in topic_lower for keyword in ["系统", "system"]):
            alternatives.extend([
                f"{topic}",
                f"基于{topic}的技术方案",
                f"{topic}的实现方法",
                f"{topic}的优化方案"
            ])
        elif any(keyword in topic_lower for keyword in ["方法", "method", "算法", "algorithm"]):
            alternatives.extend([
                f"{topic}",
                f"{topic}的实现系统",
                f"基于{topic}的技术方案",
                f"{topic}的应用系统"
            ])
        elif any(keyword in topic_lower for keyword in ["装置", "device", "设备"]):
            alternatives.extend([
                f"{topic}",
                f"{topic}的控制系统",
                f"基于{topic}的技术方案",
                f"{topic}的监控系统"
            ])
        else:
            # Generic alternatives for any topic
            alternatives.extend([
                f"{topic}系统",
                f"基于{topic}的技术方案",
                f"{topic}的实现方法",
                f"{topic}的优化方案",
                f"{topic}的应用系统"
            ])
            
        return alternatives
        
    async def _identify_technical_domain(self, topic: str, description: str) -> str:
        """Identify the technical domain"""
        # Comprehensive domain mapping
        domains = {
            # AI and ML domains
            "人工智能": "人工智能与机器学习技术领域",
            "机器学习": "人工智能与机器学习技术领域",
            "深度学习": "人工智能与机器学习技术领域",
            "神经网络": "人工智能与机器学习技术领域",
            "自然语言": "自然语言处理技术领域",
            "计算机视觉": "计算机视觉与图像处理技术领域",
            "语音识别": "语音识别与处理技术领域",
            
            # Information retrieval and search
            "检索": "信息检索与搜索引擎技术领域",
            "搜索": "信息检索与搜索引擎技术领域",
            "RAG": "自然语言处理与信息检索技术领域",
            "信息检索": "信息检索与搜索引擎技术领域",
            
            # Knowledge and reasoning
            "知识图谱": "知识图谱与知识表示技术领域",
            "推理": "知识推理与逻辑推理技术领域",
            "证据图": "知识图谱与证据推理技术领域",
            "知识管理": "知识管理与知识工程技术领域",
            
            # Data and analytics
            "大数据": "大数据处理与分析技术领域",
            "数据分析": "数据分析与挖掘技术领域",
            "数据挖掘": "数据分析与挖掘技术领域",
            "数据科学": "数据科学与分析技术领域",
            
            # Blockchain and security
            "区块链": "区块链与分布式技术领域",
            "密码学": "密码学与信息安全技术领域",
            "安全": "信息安全与网络安全技术领域",
            "隐私": "隐私保护与数据安全技术领域",
            
            # IoT and embedded systems
            "物联网": "物联网与嵌入式系统技术领域",
            "传感器": "传感器与物联网技术领域",
            "嵌入式": "嵌入式系统与物联网技术领域",
            
            # Cloud and distributed systems
            "云计算": "云计算与分布式系统技术领域",
            "分布式": "分布式系统与云计算技术领域",
            "微服务": "微服务与分布式架构技术领域",
            
            # Mobile and wireless
            "移动": "移动计算与无线通信技术领域",
            "无线": "无线通信与移动网络技术领域",
            "5G": "5G通信与移动网络技术领域",
            
            # Software and systems
            "软件": "软件工程与系统开发技术领域",
            "系统": "软件系统与架构技术领域",
            "架构": "软件架构与系统设计技术领域",
            
            # Hardware and electronics
            "硬件": "硬件设计与电子技术领域",
            "芯片": "芯片设计与集成电路技术领域",
            "电路": "电子电路与硬件设计技术领域",
            
            # Medical and healthcare
            "医疗": "医疗健康与生物医学技术领域",
            "生物": "生物医学与健康技术领域",
            "诊断": "医疗诊断与健康监测技术领域",
            
            # Financial and fintech
            "金融": "金融科技与金融服务技术领域",
            "支付": "支付系统与金融服务技术领域",
            "风控": "风险控制与金融安全技术领域",
            
            # Manufacturing and automation
            "制造": "智能制造与自动化技术领域",
            "自动化": "自动化控制与智能制造技术领域",
            "机器人": "机器人技术与自动化技术领域"
        }
        
        # Check for domain keywords in topic and description
        topic_lower = topic.lower()
        desc_lower = description.lower()
        
        for keyword, domain in domains.items():
            if keyword in topic_lower or keyword in desc_lower:
                return domain
                
        # Default domain based on common patterns
        if any(word in topic_lower for word in ["系统", "方法", "装置", "技术", "算法", "模型"]):
            return "信息技术与软件工程领域"
        elif any(word in topic_lower for word in ["设备", "硬件", "芯片", "电路"]):
            return "电子工程与硬件技术领域"
        else:
            return "信息技术与人工智能技术领域"
        
    async def _extract_key_innovations(self, description: str) -> List[str]:
        """Extract key innovations from description"""
        innovations = []
        
        # Simple keyword-based extraction
        innovation_keywords = ["增强", "改进", "优化", "创新", "新方法", "新技术"]
        sentences = description.split("。")
        
        for sentence in sentences:
            for keyword in innovation_keywords:
                if keyword in sentence:
                    innovations.append(sentence.strip())
                    break
                    
        if not innovations:
            innovations.append("通过技术创新提升系统性能")
            
        return innovations[:3]  # Limit to top 3
        
    async def _identify_target_applications(self, description: str) -> List[str]:
        """Identify target applications based on description content"""
        # Comprehensive application mapping
        application_keywords = {
            # AI and ML applications
            "智能问答": "智能问答系统",
            "问答": "智能问答系统",
            "对话": "智能对话系统",
            "聊天": "智能聊天系统",
            "推荐": "智能推荐系统",
            "预测": "智能预测系统",
            "决策": "决策支持系统",
            "分析": "数据分析系统",
            
            # Information and knowledge management
            "知识管理": "知识管理系统",
            "信息检索": "信息检索系统",
            "搜索": "搜索引擎系统",
            "文档": "文档管理系统",
            "内容": "内容管理系统",
            "数据": "数据处理系统",
            
            # Content generation and processing
            "生成": "内容生成系统",
            "创作": "内容创作系统",
            "翻译": "机器翻译系统",
            "摘要": "文本摘要系统",
            "分类": "智能分类系统",
            
            # Security and privacy
            "安全": "安全防护系统",
            "隐私": "隐私保护系统",
            "认证": "身份认证系统",
            "加密": "数据加密系统",
            "风控": "风险控制系统",
            
            # Healthcare and medical
            "医疗": "医疗诊断系统",
            "健康": "健康监测系统",
            "诊断": "医疗诊断系统",
            "药物": "药物研发系统",
            "基因": "基因分析系统",
            
            # Financial and business
            "金融": "金融服务系统",
            "支付": "支付处理系统",
            "交易": "交易处理系统",
            "投资": "投资分析系统",
            "保险": "保险评估系统",
            
            # Manufacturing and automation
            "制造": "智能制造系统",
            "生产": "生产管理系统",
            "质量": "质量控制系统",
            "监控": "监控管理系统",
            "自动化": "自动化控制系统",
            
            # IoT and embedded
            "物联网": "物联网管理系统",
            "传感器": "传感器数据处理系统",
            "监控": "监控管理系统",
            "控制": "智能控制系统",
            
            # Cloud and distributed
            "云计算": "云计算管理系统",
            "分布式": "分布式处理系统",
            "微服务": "微服务管理系统",
            "容器": "容器管理系统",
            
            # Mobile and communication
            "移动": "移动应用系统",
            "通信": "通信管理系统",
            "网络": "网络管理系统",
            "5G": "5G通信系统"
        }
        
        # Extract applications from description
        desc_lower = description.lower()
        found_applications = []
        
        for keyword, application in application_keywords.items():
            if keyword in desc_lower and application not in found_applications:
                found_applications.append(application)
                if len(found_applications) >= 3:
                    break
        
        # If no specific applications found, return generic ones
        if not found_applications:
            found_applications = [
                "智能处理系统",
                "数据分析系统",
                "信息管理系统"
            ]
        
        return found_applications[:3]
        
    async def _create_terminology_standard(self, topic: str, description: str) -> Dict[str, str]:
        """Create terminology standard based on topic and description content"""
        # Comprehensive terminology mapping
        terminology = {
            # General technical terms
            "系统": "技术系统(Technical System)",
            "方法": "技术方法(Technical Method)",
            "装置": "技术装置(Technical Device)",
            "算法": "算法(Algorithm)",
            "模型": "模型(Model)",
            "技术": "技术(Technology)",
            "增强": "性能增强(Performance Enhancement)",
            "优化": "性能优化(Performance Optimization)",
            "改进": "技术改进(Technical Improvement)",
            "创新": "技术创新(Technical Innovation)",
            
            # AI and ML terms
            "人工智能": "人工智能(Artificial Intelligence)",
            "机器学习": "机器学习(Machine Learning)",
            "深度学习": "深度学习(Deep Learning)",
            "神经网络": "神经网络(Neural Network)",
            "自然语言": "自然语言(Natural Language)",
            "计算机视觉": "计算机视觉(Computer Vision)",
            "语音识别": "语音识别(Speech Recognition)",
            
            # Information retrieval and search
            "检索": "信息检索(Information Retrieval)",
            "搜索": "搜索(Search)",
            "RAG": "检索增强生成(Retrieval-Augmented Generation)",
            "信息检索": "信息检索(Information Retrieval)",
            "搜索引擎": "搜索引擎(Search Engine)",
            
            # Knowledge and reasoning
            "知识图谱": "知识图谱(Knowledge Graph)",
            "推理": "推理(Reasoning)",
            "证据图": "证据关系图(Evidence Graph)",
            "知识管理": "知识管理(Knowledge Management)",
            "逻辑": "逻辑(Logic)",
            "因果": "因果关系(Causality)",
            
            # Data and analytics
            "大数据": "大数据(Big Data)",
            "数据分析": "数据分析(Data Analysis)",
            "数据挖掘": "数据挖掘(Data Mining)",
            "数据科学": "数据科学(Data Science)",
            "统计": "统计分析(Statistical Analysis)",
            
            # Blockchain and security
            "区块链": "区块链(Blockchain)",
            "密码学": "密码学(Cryptography)",
            "安全": "安全(Security)",
            "隐私": "隐私(Privacy)",
            "加密": "加密(Encryption)",
            "认证": "认证(Authentication)",
            
            # IoT and embedded systems
            "物联网": "物联网(Internet of Things)",
            "传感器": "传感器(Sensor)",
            "嵌入式": "嵌入式(Embedded)",
            "智能设备": "智能设备(Smart Device)",
            
            # Cloud and distributed systems
            "云计算": "云计算(Cloud Computing)",
            "分布式": "分布式(Distributed)",
            "微服务": "微服务(Microservice)",
            "容器": "容器(Container)",
            "虚拟化": "虚拟化(Virtualization)",
            
            # Mobile and wireless
            "移动": "移动(Mobile)",
            "无线": "无线(Wireless)",
            "5G": "5G通信(5G Communication)",
            "通信": "通信(Communication)",
            "网络": "网络(Network)",
            
            # Software and systems
            "软件": "软件(Software)",
            "架构": "架构(Architecture)",
            "接口": "接口(Interface)",
            "协议": "协议(Protocol)",
            "框架": "框架(Framework)",
            
            # Hardware and electronics
            "硬件": "硬件(Hardware)",
            "芯片": "芯片(Chip)",
            "电路": "电路(Circuit)",
            "处理器": "处理器(Processor)",
            "存储器": "存储器(Memory)",
            
            # Medical and healthcare
            "医疗": "医疗(Medical)",
            "生物": "生物(Biological)",
            "诊断": "诊断(Diagnosis)",
            "治疗": "治疗(Treatment)",
            "药物": "药物(Drug)",
            
            # Financial and fintech
            "金融": "金融(Financial)",
            "支付": "支付(Payment)",
            "交易": "交易(Transaction)",
            "投资": "投资(Investment)",
            "风控": "风险控制(Risk Control)",
            
            # Manufacturing and automation
            "制造": "制造(Manufacturing)",
            "生产": "生产(Production)",
            "自动化": "自动化(Automation)",
            "机器人": "机器人(Robot)",
            "质量控制": "质量控制(Quality Control)"
        }
        
        # Extract topic-specific terms from topic and description
        topic_lower = topic.lower()
        desc_lower = description.lower()
        
        # Find relevant terms from the comprehensive mapping
        relevant_terms = {}
        for term, definition in terminology.items():
            if term in topic_lower or term in desc_lower:
                relevant_terms[term] = definition
        
        # Add some general terms that are commonly used
        relevant_terms.update({
            "技术": "技术(Technology)",
            "系统": "技术系统(Technical System)",
            "方法": "技术方法(Technical Method)",
            "算法": "算法(Algorithm)"
        })
        
        return relevant_terms
        
    async def _add_initial_context_items(self, workflow_id: str, theme: ThemeDefinition):
        """Add initial context items"""
        initial_items = [
            ContextItem(
                context_type=ContextType.THEME_DEFINITION,
                key="primary_title",
                value=theme.primary_title,
                source_agent="context_manager",
                timestamp=time.time()
            ),
            ContextItem(
                context_type=ContextType.THEME_DEFINITION,
                key="core_concept",
                value=theme.core_concept,
                source_agent="context_manager",
                timestamp=time.time()
            ),
            ContextItem(
                context_type=ContextType.TECHNICAL_DOMAIN,
                key="domain",
                value=theme.technical_domain,
                source_agent="context_manager",
                timestamp=time.time()
            )
        ]
        
        for item in initial_items:
            await self.add_context_item(workflow_id, item)
            
    async def add_context_item(self, workflow_id: str, context_item: ContextItem):
        """Add a context item to the workflow"""
        try:
            if workflow_id not in self.active_contexts:
                logger.warning(f"Workflow {workflow_id} not found in active contexts")
                return
                
            context_type = context_item.context_type
            self.active_contexts[workflow_id][context_type].append(context_item)
            
            # Validate consistency
            await self._validate_context_consistency(workflow_id, context_item)
            
            logger.info(f"Added context item {context_item.key} to workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Error adding context item: {e}")
            
    async def get_context_for_agent(self, workflow_id: str, agent_name: str, 
                                  context_types: List[ContextType] = None) -> Dict[str, Any]:
        """Get relevant context for a specific agent"""
        try:
            if workflow_id not in self.active_contexts:
                return {}
                
            if context_types is None:
                context_types = list(ContextType)
                
            context_data = {
                "theme_definition": self.theme_definitions.get(workflow_id),
                "terminology": self.terminology_registry.get(workflow_id, {}),
                "context_items": {}
            }
            
            for context_type in context_types:
                items = self.active_contexts[workflow_id].get(context_type, [])
                context_data["context_items"][context_type.value] = [
                    {
                        "key": item.key,
                        "value": item.value,
                        "source": item.source_agent,
                        "timestamp": item.timestamp
                    }
                    for item in items
                ]
                
            return context_data
            
        except Exception as e:
            logger.error(f"Error getting context for agent: {e}")
            return {}
            
    async def validate_agent_output(self, workflow_id: str, agent_name: str, 
                                  output: str, output_type: str) -> Dict[str, Any]:
        """Validate agent output against context consistency"""
        try:
            validation_result = {
                "is_consistent": True,
                "score": 1.0,
                "issues": [],
                "suggestions": []
            }
            
            theme = self.theme_definitions.get(workflow_id)
            if not theme:
                validation_result["is_consistent"] = False
                validation_result["issues"].append("No theme definition found")
                return validation_result
                
            # Check title consistency
            if output_type == "title" or "标题" in output_type:
                title_consistency = await self._check_title_consistency(output, theme)
                if not title_consistency["is_consistent"]:
                    validation_result["is_consistent"] = False
                    validation_result["issues"].extend(title_consistency["issues"])
                    
            # Check terminology consistency
            terminology_issues = await self._check_terminology_consistency(output, theme.terminology_standard)
            if terminology_issues:
                validation_result["issues"].extend(terminology_issues)
                validation_result["score"] *= 0.9
                
            # Check technical domain consistency
            domain_consistency = await self._check_domain_consistency(output, theme.technical_domain)
            if not domain_consistency["is_consistent"]:
                validation_result["is_consistent"] = False
                validation_result["issues"].extend(domain_consistency["issues"])
                
            # Check innovation consistency
            innovation_consistency = await self._check_innovation_consistency(output, theme.key_innovations)
            if not innovation_consistency["is_consistent"]:
                validation_result["score"] *= 0.8
                validation_result["suggestions"].extend(innovation_consistency["suggestions"])
                
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating agent output: {e}")
            return {
                "is_consistent": False,
                "score": 0.0,
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": []
            }
            
    async def _check_title_consistency(self, output: str, theme: ThemeDefinition) -> Dict[str, Any]:
        """Check if output title is consistent with theme"""
        result = {"is_consistent": True, "issues": []}
        
        # Check if output contains any of the approved titles
        approved_titles = [theme.primary_title] + theme.alternative_titles
        
        title_found = False
        for title in approved_titles:
            if title.lower() in output.lower() or output.lower() in title.lower():
                title_found = True
                break
                
        if not title_found:
            result["is_consistent"] = False
            result["issues"].append(f"标题不一致，建议使用：{theme.primary_title}")
            
        return result
        
    async def _check_terminology_consistency(self, output: str, terminology: Dict[str, str]) -> List[str]:
        """Check terminology consistency"""
        issues = []
        
        for term, definition in terminology.items():
            if term in output and definition not in output:
                issues.append(f"术语'{term}'应使用标准定义：{definition}")
                
        return issues
        
    async def _check_domain_consistency(self, output: str, domain: str) -> Dict[str, Any]:
        """Check technical domain consistency"""
        result = {"is_consistent": True, "issues": []}
        
        domain_keywords = domain.split("与")
        found_keywords = []
        
        for keyword in domain_keywords:
            if keyword in output:
                found_keywords.append(keyword)
                
        if not found_keywords:
            result["is_consistent"] = False
            result["issues"].append(f"技术领域不匹配，应包含：{domain}")
            
        return result
        
    async def _check_innovation_consistency(self, output: str, innovations: List[str]) -> Dict[str, Any]:
        """Check innovation consistency"""
        result = {"is_consistent": True, "suggestions": []}
        
        innovation_mentions = 0
        for innovation in innovations:
            if any(keyword in output for keyword in innovation.split()):
                innovation_mentions += 1
                
        if innovation_mentions == 0:
            result["is_consistent"] = False
            result["suggestions"].append(f"建议提及关键创新点：{innovations[0]}")
            
        return result
        
    async def _validate_context_consistency(self, workflow_id: str, new_item: ContextItem):
        """Validate new context item against existing context"""
        try:
            # Check for conflicts with existing items
            existing_items = self.active_contexts[workflow_id].get(new_item.context_type, [])
            
            for existing_item in existing_items:
                if existing_item.key == new_item.key and existing_item.source_agent != new_item.source_agent:
                    logger.warning(f"Potential context conflict: {new_item.key} from {new_item.source_agent} vs {existing_item.source_agent}")
                    
        except Exception as e:
            logger.error(f"Error validating context consistency: {e}")
            
    async def get_context_summary(self, workflow_id: str) -> Dict[str, Any]:
        """Get a summary of current context"""
        try:
            theme = self.theme_definitions.get(workflow_id)
            if not theme:
                return {}
                
            context_items = self.active_contexts.get(workflow_id, {})
            
            summary = {
                "workflow_id": workflow_id,
                "theme": {
                    "primary_title": theme.primary_title,
                    "core_concept": theme.core_concept,
                    "technical_domain": theme.technical_domain,
                    "key_innovations": theme.key_innovations
                },
                "context_items_count": {
                    context_type.value: len(items)
                    for context_type, items in context_items.items()
                },
                "terminology_count": len(self.terminology_registry.get(workflow_id, {})),
                "last_updated": time.time()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting context summary: {e}")
            return {}
            
    async def cleanup_workflow_context(self, workflow_id: str):
        """Clean up context for completed workflow"""
        try:
            if workflow_id in self.active_contexts:
                del self.active_contexts[workflow_id]
            if workflow_id in self.theme_definitions:
                del self.theme_definitions[workflow_id]
            if workflow_id in self.terminology_registry:
                del self.terminology_registry[workflow_id]
                
            logger.info(f"Cleaned up context for workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up workflow context: {e}")

# Global context manager instance
context_manager = ContextManager()