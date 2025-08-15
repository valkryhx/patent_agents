"""
Reviewer Agent for Patent Agent System
Reviews patent drafts for quality, accuracy, and compliance
"""

import asyncio
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..openai_client import OpenAIClient
from ..google_a2a_client import PatentDraft

logger = logging.getLogger(__name__)

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
    
    def __init__(self):
        super().__init__(
            name="reviewer_agent",
            capabilities=["patent_review", "quality_assessment", "compliance_checking", "feedback_generation"]
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
        """Review the patent title"""
        try:
            score = 10.0
            issues = []
            
            # Check length
            if len(title) < 10:
                score -= 3.0
                issues.append({
                    "type": "length",
                    "severity": "high",
                    "description": "Title too short",
                    "recommendation": "Expand title to be more descriptive"
                })
            elif len(title) > 100:
                score -= 2.0
                issues.append({
                    "type": "length",
                    "severity": "medium",
                    "description": "Title too long",
                    "recommendation": "Shorten title while maintaining clarity"
                })
                
            # Check formatting
            if not title[0].isupper():
                score -= 1.0
                issues.append({
                    "type": "formatting",
                    "severity": "low",
                    "description": "Title should start with capital letter",
                    "recommendation": "Capitalize first letter of title"
                })
                
            # Check clarity
            if len(title.split()) < 3:
                score -= 2.0
                issues.append({
                    "type": "clarity",
                    "severity": "medium",
                    "description": "Title lacks sufficient detail",
                    "recommendation": "Add more descriptive terms to title"
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