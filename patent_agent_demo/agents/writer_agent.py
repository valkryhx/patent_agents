"""
Writer Agent for Patent Agent System
Drafts patent applications and technical documentation
"""

import asyncio
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from .base_agent import BaseAgent, TaskResult
from ..google_a2a_client import get_google_a2a_client, PatentDraft

logger = logging.getLogger(__name__)

@dataclass
class WritingTask:
    """Writing task definition"""
    task_id: str
    topic: str
    description: str
    requirements: Dict[str, Any]
    previous_results: Dict[str, Any]
    target_audience: str
    writing_style: str

@dataclass
class WritingOutput:
    """Output of a writing task"""
    task_id: str
    content: PatentDraft
    writing_metrics: Dict[str, Any]
    quality_score: float
    compliance_check: Dict[str, Any]

class WriterAgent(BaseAgent):
    """Agent responsible for drafting patent applications"""
    
    def __init__(self):
        super().__init__(
            name="writer_agent",
            capabilities=["patent_drafting", "technical_writing", "claim_writing", "legal_compliance"]
        )
        self.google_a2a_client = None
        self.writing_templates = self._load_writing_templates()
        self.legal_requirements = self._load_legal_requirements()
        
    async def start(self):
        """Start the writer agent"""
        await super().start()
        self.google_a2a_client = await get_google_a2a_client()
        logger.info("Writer Agent started successfully")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute writing tasks"""
        try:
            task_type = task_data.get("type")
            
            if task_type == "patent_drafting":
                return await self._draft_patent_application(task_data)
            elif task_type == "claim_writing":
                return await self._write_patent_claims(task_data)
            elif task_type == "technical_description":
                return await self._write_technical_description(task_data)
            elif task_type == "legal_compliance_check":
                return await self._check_legal_compliance(task_data)
            else:
                return TaskResult(
                    success=False,
                    data={},
                    error_message=f"Unknown task type: {task_type}"
                )
                
        except Exception as e:
            logger.error(f"Error executing task in Writer Agent: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _draft_patent_application(self, task_data: Dict[str, Any]) -> TaskResult:
        """Draft a complete patent application"""
        try:
            topic = task_data.get("topic")
            description = task_data.get("description")
            previous_results = task_data.get("previous_results", {})
            
            if not topic or not description:
                return TaskResult(
                    success=False,
                    data={},
                    error_message="Topic and description are required for patent drafting"
                )
                
            logger.info(f"Drafting patent application for: {topic}")
            
            # Create writing task
            writing_task = WritingTask(
                task_id=f"writing_{asyncio.get_event_loop().time()}",
                topic=topic,
                description=description,
                requirements=previous_results.get("requirements", {}),
                previous_results=previous_results,
                target_audience="patent_examiners",
                writing_style="technical_legal"
            )
            
            # Generate patent draft using Google A2A
            patent_draft = await self.google_a2a_client.generate_patent_draft(
                topic, description, previous_results.get("analysis", {})
            )
            
            # Write detailed sections
            detailed_sections = await self._write_detailed_sections(writing_task, patent_draft)
            
            # Generate technical diagrams
            technical_diagrams = await self.google_a2a_client.generate_technical_diagrams(description)
            
            # Update patent draft with detailed content
            patent_draft.detailed_description = detailed_sections.get("detailed_description", "")
            patent_draft.technical_diagrams = technical_diagrams
            
            # Check legal compliance
            compliance_check = await self._check_patent_compliance(patent_draft)
            
            # Calculate quality score
            quality_score = await self._calculate_writing_quality(patent_draft, compliance_check)
            
            # Compile writing output
            writing_output = WritingOutput(
                task_id=writing_task.task_id,
                content=patent_draft,
                writing_metrics={
                    "word_count": len(patent_draft.detailed_description.split()),
                    "sections_completed": 6,
                    "compliance_score": compliance_check.get("overall_score", 0)
                },
                quality_score=quality_score,
                compliance_check=compliance_check
            )
            
            return TaskResult(
                success=True,
                data={
                    "patent_draft": patent_draft,
                    "writing_output": writing_output,
                    "technical_diagrams": technical_diagrams,
                    "compliance_status": "compliant" if compliance_check.get("overall_score", 0) >= 8.0 else "needs_revision"
                },
                metadata={
                    "writing_type": "complete_patent_application",
                    "completion_timestamp": asyncio.get_event_loop().time()
                }
            )
            
        except Exception as e:
            logger.error(f"Error drafting patent application: {e}")
            return TaskResult(
                success=False,
                data={},
                error_message=str(e)
            )
            
    async def _write_detailed_sections(self, writing_task: WritingTask, 
                                     patent_draft: PatentDraft) -> Dict[str, str]:
        """Write detailed sections of the patent application"""
        try:
            detailed_sections = {}
            
            # Write background section
            background = await self._write_background_section(
                writing_task.topic, writing_task.description, writing_task.previous_results
            )
            detailed_sections["background"] = background
            
            # Write summary section
            summary = await self._write_summary_section(
                writing_task.topic, patent_draft.abstract, writing_task.previous_results
            )
            detailed_sections["summary"] = summary
            
            # Write detailed description
            detailed_description = await self._write_detailed_description(
                writing_task.topic, writing_task.description, patent_draft.claims, writing_task.previous_results
            )
            detailed_sections["detailed_description"] = detailed_description
            
            # Write claims
            claims = await self._write_patent_claims(
                writing_task.topic, writing_task.description, writing_task.previous_results
            )
            detailed_sections["claims"] = claims
            
            # Write drawings description
            drawings_description = await self._write_drawings_description(
                writing_task.topic, writing_task.description
            )
            detailed_sections["drawings_description"] = drawings_description
            
            return detailed_sections
            
        except Exception as e:
            logger.error(f"Error writing detailed sections: {e}")
            raise
            
    async def _write_background_section(self, topic: str, description: str, 
                                      previous_results: Dict[str, Any]) -> str:
        """Write the background section"""
        try:
            # Use Google A2A to write background section
            prompt = f"""
            Write a comprehensive background section for a patent application:
            
            Topic: {topic}
            Description: {description}
            
            Previous Analysis: {previous_results.get('analysis', {})}
            
            Include:
            1. Field of the invention
            2. Current state of the art
            3. Problems with existing solutions
            4. Need for the invention
            
            Write in formal patent language, 200-300 words.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse and format response
            background_section = f"""
            BACKGROUND OF THE INVENTION
            
            Field of the Invention
            
            The present invention relates to {topic.lower()}, and more particularly to {description.lower()}.
            
            {response}
            
            Description of the Prior Art
            
            Current solutions in the field of {topic.lower()} suffer from several limitations including [limitations identified from analysis]. There exists a need for improved methods and systems that address these limitations.
            """
            
            return background_section
            
        except Exception as e:
            logger.error(f"Error writing background section: {e}")
            return f"Background section for {topic} - [Error occurred during generation]"
            
    async def _write_summary_section(self, topic: str, abstract: str, 
                                   previous_results: Dict[str, Any]) -> str:
        """Write the summary section"""
        try:
            # Use Google A2A to write summary section
            prompt = f"""
            Write a summary section for a patent application:
            
            Topic: {topic}
            Abstract: {abstract}
            
            Analysis Results: {previous_results.get('analysis', {})}
            
            Include:
            1. Brief summary of the invention
            2. Key advantages
            3. Technical benefits
            
            Write in formal patent language, 150-200 words.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse and format response
            summary_section = f"""
            SUMMARY OF THE INVENTION
            
            {response}
            
            The present invention provides significant advantages over existing solutions, including improved efficiency, enhanced performance, and novel technical approaches to {topic.lower()}.
            """
            
            return summary_section
            
        except Exception as e:
            logger.error(f"Error writing summary section: {e}")
            return f"Summary section for {topic} - [Error occurred during generation]"
            
    async def _write_detailed_description(self, topic: str, description: str, 
                                        claims: List[str], previous_results: Dict[str, Any]) -> str:
        """Write the detailed description section"""
        try:
            # Use Google A2A to write detailed description
            prompt = f"""
            Write a detailed description section for a patent application:
            
            Topic: {topic}
            Description: {description}
            Claims: {claims}
            
            Previous Results: {previous_results}
            
            Include:
            1. Detailed technical implementation
            2. Step-by-step methodology
            3. Alternative embodiments
            4. Technical advantages
            
            Write in formal patent language, 500-800 words.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse and format response
            detailed_description = f"""
            DETAILED DESCRIPTION OF THE INVENTION
            
            {response}
            
            The invention will now be described in detail with reference to the accompanying drawings and preferred embodiments. It should be understood that the invention is not limited to the specific embodiments described herein.
            """
            
            return detailed_description
            
        except Exception as e:
            logger.error(f"Error writing detailed description: {e}")
            return f"Detailed description for {topic} - [Error occurred during generation]"
            
    async def _write_patent_claims(self, topic: str, description: str, 
                                 previous_results: Dict[str, Any]) -> List[str]:
        """Write patent claims"""
        try:
            # Use Google A2A to write claims
            prompt = f"""
            Write 3-5 patent claims for this invention:
            
            Topic: {topic}
            Description: {description}
            
            Analysis: {previous_results.get('analysis', {})}
            
            Include:
            1. One independent claim covering the core invention
            2. 2-4 dependent claims with specific limitations
            3. Clear, precise language
            4. Proper patent claim structure
            
            Format each claim as a numbered list.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse response to extract claims
            # This is a simplified approach
            claims = [
                f"1. A method for {topic.lower()}, comprising: {description.lower()}.",
                f"2. The method of claim 1, further comprising: additional step.",
                f"3. The method of claim 1, wherein: specific limitation.",
                f"4. A system for {topic.lower()}, comprising: system components.",
                f"5. A computer-readable medium storing instructions for {topic.lower()}."
            ]
            
            return claims
            
        except Exception as e:
            logger.error(f"Error writing patent claims: {e}")
            return [f"Claim 1: A method for {topic.lower()}."]
            
    async def _write_drawings_description(self, topic: str, description: str) -> str:
        """Write the drawings description section"""
        try:
            # Use Google A2A to write drawings description
            prompt = f"""
            Write a drawings description section for a patent application:
            
            Topic: {topic}
            Description: {description}
            
            Include descriptions for:
            1. Figure 1: Overall system architecture
            2. Figure 2: Detailed component diagram
            3. Figure 3: Process flow diagram
            4. Figure 4: Implementation example
            5. Figure 5: Alternative embodiments
            
            Write in formal patent language, 200-300 words.
            """
            
            response = await self.google_a2a_client._generate_response(prompt)
            
            # Parse and format response
            drawings_description = f"""
            BRIEF DESCRIPTION OF THE DRAWINGS
            
            {response}
            
            The drawings illustrate preferred embodiments of the invention and are not intended to limit the scope of the invention.
            """
            
            return drawings_description
            
        except Exception as e:
            logger.error(f"Error writing drawings description: {e}")
            return f"Drawings description for {topic} - [Error occurred during generation]"
            
    async def _check_patent_compliance(self, patent_draft: PatentDraft) -> Dict[str, Any]:
        """Check legal compliance of the patent draft"""
        try:
            compliance_check = {
                "overall_score": 8.5,
                "sections": {},
                "issues": [],
                "recommendations": []
            }
            
            # Check title compliance
            title_check = await self._check_title_compliance(patent_draft.title)
            compliance_check["sections"]["title"] = title_check
            
            # Check abstract compliance
            abstract_check = await self._check_abstract_compliance(patent_draft.abstract)
            compliance_check["sections"]["abstract"] = abstract_check
            
            # Check claims compliance
            claims_check = await self._check_claims_compliance(patent_draft.claims)
            compliance_check["sections"]["claims"] = claims_check
            
            # Check description compliance
            description_check = await self._check_description_compliance(patent_draft.detailed_description)
            compliance_check["sections"]["description"] = description_check
            
            # Calculate overall compliance score
            section_scores = [check.get("score", 0) for check in compliance_check["sections"].values()]
            if section_scores:
                compliance_check["overall_score"] = sum(section_scores) / len(section_scores)
                
            # Generate recommendations
            compliance_check["recommendations"] = await self._generate_compliance_recommendations(compliance_check)
            
            return compliance_check
            
        except Exception as e:
            logger.error(f"Error checking patent compliance: {e}")
            return {"overall_score": 0, "error": str(e)}
            
    async def _check_title_compliance(self, title: str) -> Dict[str, Any]:
        """Check title compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            if len(title) < 10:
                score -= 2.0
                issues.append("Title too short")
                recommendations.append("Expand title to be more descriptive")
                
            if len(title) > 100:
                score -= 1.0
                issues.append("Title too long")
                recommendations.append("Shorten title while maintaining clarity")
                
            if not title[0].isupper():
                score -= 0.5
                issues.append("Title should start with capital letter")
                recommendations.append("Capitalize first letter of title")
                
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking title compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _check_abstract_compliance(self, abstract: str) -> Dict[str, Any]:
        """Check abstract compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            word_count = len(abstract.split())
            if word_count < 50:
                score -= 2.0
                issues.append("Abstract too short")
                recommendations.append("Expand abstract to provide comprehensive overview")
            elif word_count > 150:
                score -= 1.0
                issues.append("Abstract too long")
                recommendations.append("Condense abstract to meet word limit")
                
            if not abstract.endswith("."):
                score -= 0.5
                issues.append("Abstract should end with period")
                recommendations.append("Add period at end of abstract")
                
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking abstract compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _check_claims_compliance(self, claims: List[str]) -> Dict[str, Any]:
        """Check claims compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            if len(claims) < 3:
                score -= 2.0
                issues.append("Insufficient number of claims")
                recommendations.append("Add more claims for comprehensive protection")
                
            if len(claims) > 20:
                score -= 1.0
                issues.append("Too many claims")
                recommendations.append("Consolidate or remove redundant claims")
                
            # Check claim structure
            for i, claim in enumerate(claims):
                if not claim.strip().endswith("."):
                    score -= 0.5
                    issues.append(f"Claim {i+1} should end with period")
                    recommendations.append(f"Add period at end of claim {i+1}")
                    
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking claims compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _check_description_compliance(self, description: str) -> Dict[str, Any]:
        """Check description compliance"""
        try:
            score = 9.0
            issues = []
            recommendations = []
            
            word_count = len(description.split())
            if word_count < 500:
                score -= 2.0
                issues.append("Description too short")
                recommendations.append("Expand description with more technical details")
            elif word_count > 5000:
                score -= 1.0
                issues.append("Description too long")
                recommendations.append("Condense description to essential information")
                
            if not description:
                score -= 5.0
                issues.append("Missing description")
                recommendations.append("Add detailed description section")
                
            return {
                "score": max(0, score),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking description compliance: {e}")
            return {"score": 0, "error": str(e)}
            
    async def _generate_compliance_recommendations(self, compliance_check: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations"""
        try:
            recommendations = []
            
            overall_score = compliance_check.get("overall_score", 0)
            
            if overall_score < 7.0:
                recommendations.append("Major revisions required to meet compliance standards")
            elif overall_score < 8.5:
                recommendations.append("Minor revisions recommended for optimal compliance")
            else:
                recommendations.append("Patent draft meets compliance requirements")
                
            # Add specific recommendations from sections
            for section_name, section_check in compliance_check.get("sections", {}).items():
                section_score = section_check.get("score", 0)
                if section_score < 8.0:
                    recommendations.extend(section_check.get("recommendations", []))
                    
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating compliance recommendations: {e}")
            return ["Review patent draft for compliance issues"]
            
    async def _calculate_writing_quality(self, patent_draft: PatentDraft, 
                                       compliance_check: Dict[str, Any]) -> float:
        """Calculate overall writing quality score"""
        try:
            # Base quality score
            base_score = 8.0
            
            # Adjust based on compliance
            compliance_score = compliance_check.get("overall_score", 0)
            compliance_factor = compliance_score / 10.0
            
            # Adjust based on content completeness
            content_score = 0
            if patent_draft.title:
                content_score += 1
            if patent_draft.abstract:
                content_score += 1
            if patent_draft.claims:
                content_score += 2
            if patent_draft.detailed_description:
                content_score += 2
            if patent_draft.technical_diagrams:
                content_score += 1
                
            content_factor = content_score / 7.0
            
            # Calculate final quality score
            quality_score = base_score * 0.4 + compliance_factor * 10 * 0.4 + content_factor * 10 * 0.2
            
            return max(1.0, min(10.0, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating writing quality: {e}")
            return 7.0  # Default fallback score
            
    async def _write_patent_claims(self, task_data: Dict[str, Any]) -> TaskResult:
        """Write patent claims specifically"""
        # Implementation for claim writing
        pass
        
    async def _write_technical_description(self, task_data: Dict[str, Any]) -> TaskResult:
        """Write technical description"""
        # Implementation for technical description writing
        pass
        
    async def _check_legal_compliance(self, task_data: Dict[str, Any]) -> TaskResult:
        """Check legal compliance"""
        # Implementation for legal compliance checking
        pass
        
    def _load_writing_templates(self) -> Dict[str, Any]:
        """Load writing templates for different patent types"""
        return {
            "utility_patent": {
                "sections": ["Title", "Abstract", "Background", "Summary", "Description", "Claims", "Drawings"],
                "word_limits": {"abstract": 150, "description": "unlimited"}
            },
            "design_patent": {
                "sections": ["Title", "Description", "Claims", "Drawings"],
                "word_limits": {"description": 100}
            },
            "provisional_patent": {
                "sections": ["Title", "Description", "Drawings"],
                "word_limits": {"description": "unlimited"}
            }
        }
        
    def _load_legal_requirements(self) -> Dict[str, Any]:
        """Load legal requirements for patent applications"""
        return {
            "uspto": {
                "title_max_length": 500,
                "abstract_max_words": 150,
                "claims_max_count": 20,
                "drawings_required": True
            },
            "epo": {
                "title_max_length": 400,
                "abstract_max_words": 150,
                "claims_max_count": 15,
                "drawings_required": True
            },
            "wipo": {
                "title_max_length": 500,
                "abstract_max_words": 150,
                "claims_max_count": 20,
                "drawings_required": True
            }
        }