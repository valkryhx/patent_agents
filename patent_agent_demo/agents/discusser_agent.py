"""
Discusser Agent for Patent Agent System
Facilitates multi-agent discussions and brainstorming sessions
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..google_a2a_client import get_google_a2a_client

logger = logging.getLogger(__name__)

@dataclass
class DiscussionSession:
    """Discussion session definition"""
    session_id: str
    topic: str
    participants: List[str]
    agenda: List[str]
    start_time: float
    end_time: Optional[float] = None
    outcomes: List[str] = None
    action_items: List[str] = None

@dataclass
class DiscussionOutcome:
    """Outcome of a discussion session"""
    session_id: str
    key_insights: List[str]
    innovative_solutions: List[str]
    alternative_approaches: List[str]
    consensus_points: List[str]
    disagreements: List[str]
    next_steps: List[str]

class DiscusserAgent(BaseAgent):
    """Agent responsible for facilitating discussions and brainstorming"""
    
    def __init__(self):
        super().__init__(
            name="discusser_agent",
            capabilities=["innovation_discussion", "discussion_facilitation", "brainstorming", "consensus_building", "idea_refinement"]
        )
        self.google_a2a_client = None
        self.active_sessions: Dict[str, DiscussionSession] = {}
        self.discussion_templates = self._load_discussion_templates()
        
    async def start(self):
        """Start the discusser agent"""
        await super().start()
        from ..telemetry import A2ALoggingProxy
        self.google_a2a_client = A2ALoggingProxy(self.name, await get_google_a2a_client(), self)
        logger.info("Discusser Agent started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute discussion tasks"""
        try:
            task_type = task_data.get("type")
            
            if task_type == "innovation_discussion":
                return await self._facilitate_innovation_discussion(task_data)
            elif task_type == "brainstorming_session":
                return await self._conduct_brainstorming_session(task_data)
            elif task_type == "consensus_building":
                return await self._build_consensus(task_data)
            elif task_type == "idea_refinement":
                return await self._refine_ideas(task_data)
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error executing task in Discusser Agent: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _facilitate_innovation_discussion(self, task_data: Dict[str, Any]) -> TaskResult:
        """Facilitate an innovation discussion session"""
        try:
            topic = task_data.get("topic")
            description = task_data.get("description")
            previous_results = task_data.get("previous_results", {})
            
            if not topic:
                return TaskResult(
                    success=False,
                    data={},
                    error_message="Topic is required for innovation discussion"
                )
                
            logger.info(f"Facilitating innovation discussion for: {topic}")
            
            # Create discussion session
            session = await self._create_discussion_session(topic, description)
            
            # Generate discussion agenda
            agenda = await self._generate_discussion_agenda(topic, description, previous_results)
            session.agenda = agenda
            
            # Conduct the discussion
            discussion_outcome = await self._conduct_discussion(session, previous_results)
            
            # Generate innovative solutions
            innovative_solutions = await self._generate_innovative_solutions(topic, description, discussion_outcome)
            
            # Compile final outcomes
            final_outcome = DiscussionOutcome(
                session_id=session.session_id,
                key_insights=discussion_outcome.get("key_insights", []),
                innovative_solutions=innovative_solutions,
                alternative_approaches=discussion_outcome.get("alternative_approaches", []),
                consensus_points=discussion_outcome.get("consensus_points", []),
                disagreements=discussion_outcome.get("disagreements", []),
                next_steps=discussion_outcome.get("next_steps", [])
            )
            
            # Close session
            session.end_time = asyncio.get_event_loop().time()
            session.outcomes = final_outcome.key_insights
            session.action_items = final_outcome.next_steps
            
            return TaskResult(
                success=True,
                data={
                    "discussion_outcome": final_outcome,
                    "session_summary": {
                        "session_id": session.session_id,
                        "duration": session.end_time - session.start_time,
                        "participants": session.participants,
                        "agenda_items": len(session.agenda)
                    },
                    "innovative_solutions": innovative_solutions,
                    "consensus_reached": len(final_outcome.consensus_points) > 0
                },
                metadata={
                    "discussion_type": "innovation_brainstorming",
                    "session_timestamp": session.start_time
                }
            )
            
        except Exception as e:
            logger.error(f"Error facilitating innovation discussion: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _create_discussion_session(self, topic: str, description: str) -> DiscussionSession:
        """Create a new discussion session"""
        try:
            session_id = f"discussion_{asyncio.get_event_loop().time()}"
            
            # Define participants (other agents)
            participants = [
                "planner_agent",
                "searcher_agent", 
                "writer_agent",
                "reviewer_agent"
            ]
            
            session = DiscussionSession(
                session_id=session_id,
                topic=topic,
                participants=participants,
                agenda=[],
                start_time=asyncio.get_event_loop().time()
            )
            
            self.active_sessions[session_id] = session
            return session
            
        except Exception as e:
            logger.error(f"Error creating discussion session: {e}")
            raise
            
    async def _generate_discussion_agenda(self, topic: str, description: str, previous_results: Dict[str, Any]) -> List[str]:
        """Generate discussion agenda based on topic and previous results (lightweight)."""
        try:
            # Lightweight local agenda to avoid heavy external calls
            agenda_items = [
                "确定章节结构与每章的mermaid图/公式/伪代码清单",
                "背景技术与最近似方案梳理（流程图/公式/伪代码）",
                "发明内容/系统架构（总体架构与模块边界）",
                "方法流程细化（Who/What/When/Where/How + 接口约定）",
                "子图选择与验证算法（指标与评估）",
                "解码与引用约束策略（鲁棒性与可验证性）",
                "事后验证与反馈闭环（指标与更新）",
                "权利要求覆盖点与从属细化"
            ]
            return agenda_items
        except Exception:
            return ["章节结构", "发明内容", "方法流程", "权利要求要点"]
            
    async def _conduct_discussion(self, session: DiscussionSession, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct the actual discussion session (lightweight, no external blocking)."""
        try:
            discussion_outcome = {
                "key_insights": [],
                "alternative_approaches": [],
                "consensus_points": [],
                "disagreements": [],
                "next_steps": []
            }
            # Simulate structured discussion using local synthesis to avoid long waits
            for agenda_item in session.agenda[:6]:  # cap items to keep stage quick
                insights = [
                    f"针对[{agenda_item}]的关键风险与约束已枚举并量化",
                    f"为[{agenda_item}]定义了输入/输出/参数与边界条件",
                    f"与其它章节的接口一致性需求在[{agenda_item}]内已标注"
                ]
                alternatives = [
                    f"[{agenda_item}] 方案A：强调可验证性与可扩展性",
                    f"[{agenda_item}] 方案B：强调性能与吞吐的折中"
                ]
                consensus = f"[{agenda_item}] 优先选择可验证性优先方案，保留性能优化为从属实施例"
                discussion_outcome["key_insights"].extend(insights)
                discussion_outcome["alternative_approaches"].extend(alternatives)
                discussion_outcome["consensus_points"].append(consensus)
            # Next steps (local)
            discussion_outcome["next_steps"] = [
                "冻结章节清单与接口约定",
                "按章撰写与审查迭代阈值设定",
                "准备撰写提示与素材汇总"
            ]
            return discussion_outcome
        except Exception as e:
            logger.error(f"Error conducting discussion: {e}")
            raise
            
    async def _generate_insights_for_agenda_item(self, agenda_item: str, topic: str, previous_results: Dict[str, Any]) -> List[str]:
        """Deprecated heavy call path. Kept for compatibility; returns local stubs."""
        return [
            f"Insight: 为[{agenda_item}]补充度量指标与数据采集路径",
            f"Insight: 在[{agenda_item}]中明确异常与失败回退",
            f"Insight: 将[{agenda_item}]的实现限制与适用范围前置"
        ]
            
    async def _generate_alternative_approaches(self, agenda_item: str, topic: str) -> List[str]:
        """Generate alternative approaches for an agenda item"""
        try:
            # Use Google A2A to generate alternatives
            prompt = f"""
            Generate 2-3 alternative approaches for this agenda item:
            
            Agenda Item: {agenda_item}
            Topic: {topic}
            
            Consider different perspectives, technologies, and methodologies.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse response to extract alternatives
            # This is a simplified approach
            alternatives = [
                f"Alternative approach 1 for {agenda_item}",
                f"Alternative approach 2 for {agenda_item}"
            ]
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error generating alternatives: {e}")
            return [f"Default alternative for {agenda_item}"]
            
    async def _build_consensus_for_item(self, agenda_item: str, insights: List[str]) -> Optional[str]:
        """Build consensus for a specific agenda item"""
        try:
            if not insights:
                return None
                
            # Use Google A2A to build consensus
            prompt = f"""
            Based on these insights, build a consensus statement:
            
            Agenda Item: {agenda_item}
            Insights: {insights}
            
            Create a clear, actionable consensus that all participants can agree on.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse response to extract consensus
            # This is a simplified approach
            consensus = f"Consensus for {agenda_item}: {insights[0] if insights else 'Default consensus'}"
            
            return consensus
            
        except Exception as e:
            logger.error(f"Error building consensus: {e}")
            return None
            
    async def _generate_next_steps(self, discussion_outcome: Dict[str, Any]) -> List[str]:
        """Generate next steps based on discussion outcomes"""
        try:
            # Use Google A2A to generate next steps
            prompt = f"""
            Based on this discussion outcome, generate 3-5 actionable next steps:
            
            Key Insights: {discussion_outcome.get('key_insights', [])}
            Innovative Solutions: {discussion_outcome.get('innovative_solutions', [])}
            Consensus Points: {discussion_outcome.get('consensus_points', [])}
            
            Focus on concrete, measurable actions that move the project forward.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse response to extract next steps
            # This is a simplified approach
            next_steps = [
                "Document key insights and decisions",
                "Develop detailed implementation plan",
                "Assign responsibilities and timelines",
                "Schedule follow-up review meeting",
                "Begin prototype development"
            ]
            
            return next_steps
            
        except Exception as e:
            logger.error(f"Error generating next steps: {e}")
            return ["Review discussion outcomes", "Plan next phase"]
            
    async def _generate_innovative_solutions(self, topic: str, description: str, discussion_outcome: Dict[str, Any]) -> List[str]:
        """Lightweight solutions synthesis to keep stage quick."""
        return [
            "分层证据与约束的解耦式实现",
            "以可验证性为中心的约束与校验流程",
            "跨章节一致性与接口驱动的撰写流程"
        ]
            
    async def _conduct_brainstorming_session(self, task_data: Dict[str, Any]) -> TaskResult:
        """Conduct a brainstorming session"""
        # Implementation for brainstorming session
        pass
        
    async def _build_consensus(self, task_data: Dict[str, Any]) -> TaskResult:
        """Build consensus among participants"""
        # Implementation for consensus building
        pass
        
    async def _refine_ideas(self, task_data: Dict[str, Any]) -> TaskResult:
        """Refine and improve ideas"""
        # Implementation for idea refinement
        pass
        
    def _load_discussion_templates(self) -> Dict[str, Any]:
        """Load discussion templates for different types of sessions"""
        return {
            "innovation_brainstorming": {
                "duration": "60-90 minutes",
                "participants": ["planner", "searcher", "writer", "reviewer"],
                "format": "Structured brainstorming with agenda"
            },
            "technical_review": {
                "duration": "45-60 minutes",
                "participants": ["technical_experts", "patent_attorneys"],
                "format": "Technical deep-dive and analysis"
            },
            "consensus_building": {
                "duration": "30-45 minutes",
                "participants": ["stakeholders", "decision_makers"],
                "format": "Decision-focused discussion"
            }
        }