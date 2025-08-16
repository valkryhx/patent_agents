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
        
        # Generate variations
        if "RAG" in topic.upper():
            alternatives.extend([
                f"基于{topic}的检索增强生成系统",
                f"{topic}增强的智能问答系统",
                f"证据图驱动的{topic}系统"
            ])
        else:
            alternatives.extend([
                f"{topic}系统",
                f"基于{topic}的技术方案",
                f"{topic}的实现方法"
            ])
            
        return alternatives
        
    async def _identify_technical_domain(self, topic: str, description: str) -> str:
        """Identify the technical domain"""
        domains = {
            "RAG": "自然语言处理与信息检索技术领域",
            "证据图": "知识图谱与证据推理技术领域",
            "检索": "信息检索与搜索引擎技术领域",
            "生成": "自然语言生成技术领域",
            "人工智能": "人工智能与机器学习技术领域"
        }
        
        for keyword, domain in domains.items():
            if keyword in topic or keyword in description:
                return domain
                
        return "人工智能与信息技术领域"
        
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
        """Identify target applications"""
        applications = [
            "智能问答系统",
            "决策支持系统", 
            "知识管理系统",
            "信息检索系统",
            "内容生成系统"
        ]
        
        return applications[:3]
        
    async def _create_terminology_standard(self, topic: str, description: str) -> Dict[str, str]:
        """Create terminology standard"""
        terminology = {
            "RAG": "检索增强生成(Retrieval-Augmented Generation)",
            "证据图": "证据关系图(Evidence Graph)",
            "检索": "信息检索(Information Retrieval)",
            "生成": "内容生成(Content Generation)",
            "增强": "性能增强(Performance Enhancement)",
            "系统": "技术系统(Technical System)"
        }
        
        # Add topic-specific terms
        if "证据图" in topic:
            terminology.update({
                "证据链": "证据推理链(Evidence Chain)",
                "推理": "逻辑推理(Logical Reasoning)",
                "验证": "结果验证(Result Verification)"
            })
            
        return terminology
        
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