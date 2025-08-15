"""
Reviewer Agent for Patent Agent System
Reviews patent drafts for quality, accuracy, and compliance
"""

import asyncio
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..google_a2a_client import get_google_a2a_client, PatentDraft

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
        self.google_a2a_client = None
        self.review_criteria = self._load_review_criteria()
        self.quality_standards = self._load_quality_standards()
        
    async def start(self):
        """Start the reviewer agent"""
        await super().start()
        self.google_a2a_client = await get_google_a2a_client()
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
        """Conduct a comprehensive review of the patent draft"""
        try:
            patent_draft = review_task.patent_draft
            
            # Review each section
            section_scores = {}
            issues_found = []
            
            # Review title
            title_review = await self._review_title(patent_draft.title)
            section_scores["title"] = title_review["score"]
            issues_found.extend(title_review["issues"])
            
            # Review abstract
            abstract_review = await self._review_abstract(patent_draft.abstract)
            section_scores["abstract"] = abstract_review["score"]
            issues_found.extend(abstract_review["issues"])
            
            # Review background
            background_review = await self._review_background(patent_draft.background)
            section_scores["background"] = background_review["score"]
            issues_found.extend(background_review["issues"])
            
            # Review summary
            summary_review = await self._review_summary(patent_draft.summary)
            section_scores["summary"] = summary_review["score"]
            issues_found.extend(summary_review["issues"])
            
            # Review detailed description
            description_review = await self._review_detailed_description(patent_draft.detailed_description)
            section_scores["description"] = description_review["score"]
            issues_found.extend(description_review["issues"])
            
            # Review claims
            claims_review = await self._review_claims(patent_draft.claims)
            section_scores["claims"] = claims_review["score"]
            issues_found.extend(claims_review["issues"])
            
            # Review drawings
            drawings_review = await self._review_drawings(patent_draft.technical_diagrams)
            section_scores["drawings"] = drawings_review["score"]
            issues_found.extend(drawings_review["issues"])
            
            # Calculate overall score
            overall_score = sum(section_scores.values()) / len(section_scores)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(issues_found, section_scores)
            
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
        """Review the detailed description section"""
        try:
            score = 10.0
            issues = []
            
            if not description:
                score -= 10.0
                issues.append({
                    "type": "missing",
                    "severity": "critical",
                    "description": "Detailed description is missing",
                    "recommendation": "Add comprehensive detailed description"
                })
                return {"score": 0, "issues": issues}
                
            # Check length
            word_count = len(description.split())
            if word_count < 500:
                score -= 4.0
                issues.append({
                    "type": "length",
                    "severity": "high",
                    "description": "Detailed description too short",
                    "recommendation": "Expand with more technical details"
                })
            elif word_count > 5000:
                score -= 1.0
                issues.append({
                    "type": "length",
                    "severity": "low",
                    "description": "Description very long",
                    "recommendation": "Consider condensing to essential information"
                })
                
            # Check technical content
            technical_elements = ["embodiment", "implementation", "method", "step", "component"]
            technical_count = sum(1 for element in technical_elements if element in description.lower())
            if technical_count < 3:
                score -= 2.0
                issues.append({
                    "type": "content",
                    "severity": "medium",
                    "description": "Description lacks technical depth",
                    "recommendation": "Add more technical implementation details"
                })
                
            return {
                "score": max(0, score),
                "issues": issues
            }
            
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