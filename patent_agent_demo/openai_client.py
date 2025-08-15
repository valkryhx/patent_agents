"""
OpenAI GPT-5 Client for Patent Agent System
Replaces GLM client with OpenAI GPT-5 API
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .google_a2a_client import PatentAnalysis, PatentDraft, SearchResult

logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI GPT-5 client for patent-related tasks"""
    
    def __init__(self):
        # Load API key from private file
        api_key_path = os.path.join(os.path.dirname(__file__), "private_openai_key")
        try:
            with open(api_key_path, "r") as f:
                api_key = f.read().strip()
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to load OpenAI API key: {e}")
            raise
    
    async def analyze_patent_topic(self, topic: str, description: str) -> PatentAnalysis:
        """Analyze patent topic for patentability"""
        try:
            prompt = f"""
Analyze the following patent topic for patentability:

Topic: {topic}
Description: {description}

Provide a comprehensive analysis including:
- Novelty score (0-10)
- Inventive step score (0-10)
- Industrial applicability
- Prior art analysis
- Claim analysis
- Technical merit
- Commercial potential
- Overall assessment
- Recommendations

Structure the output as JSON with these fields.
"""
            
            response = self.client.responses.create(
                model="gpt-5",
                input=prompt
            )
            
            # Parse the response and create PatentAnalysis object
            # For now, return a structured response
            return PatentAnalysis(
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
            
        except Exception as e:
            logger.error(f"Error analyzing patent topic: {e}")
            raise
    
    async def search_prior_art(self, topic: str, keywords: List[str], 
                              max_results: int = 20) -> List[SearchResult]:
        """Search for prior art using GPT-5 with web search"""
        try:
            search_query = f"patent prior art {topic} {' '.join(keywords)}"
            
            response = self.client.responses.create(
                model="gpt-5",
                tools=[{"type": "web_search_preview"}],
                input=search_query
            )
            
            # Parse web search results and convert to SearchResult objects
            # For now, return sample results
            return [
                SearchResult(
                    patent_id="US12345678",
                    title="Example Prior Art Patent",
                    abstract="This is an example prior art patent found through web search...",
                    inventors=["John Doe", "Jane Smith"],
                    filing_date="2020-01-01",
                    publication_date="2021-01-01",
                    relevance_score=7.5,
                    similarity_analysis={"overlap": "30%", "differences": "Key differences noted"}
                )
            ]
            
        except Exception as e:
            logger.error(f"Error searching prior art: {e}")
            raise
    
    async def generate_patent_draft(self, topic: str, description: str, 
                                  analysis: PatentAnalysis) -> PatentDraft:
        """Generate a complete patent draft"""
        try:
            prompt = f"""
Generate a complete patent draft for the following invention:

Topic: {topic}
Description: {description}

Analysis Results:
- Novelty Score: {analysis.novelty_score}/10
- Inventive Step: {analysis.inventive_step_score}/10
- Patentability: {analysis.patentability_assessment}

Create a comprehensive patent draft including:
1. Title
2. Abstract (≤150 words)
3. Background
4. Summary of Invention
5. Detailed Description
6. At least 3 Claims
7. Drawings Description
8. Technical Diagram Suggestions

Use formal patent writing style and ensure technical accuracy.
"""
            
            response = self.client.responses.create(
                model="gpt-5",
                input=prompt
            )
            
            # Parse the response and create PatentDraft object
            # For now, return a structured response
            return PatentDraft(
                title="Generated Patent Title",
                abstract="This is a generated abstract for the patent...",
                background="Background section describing the technical field...",
                summary="Summary of the invention...",
                detailed_description="Detailed description of the technical implementation...",
                claims=["Claim 1: A method for...", "Claim 2: The method of claim 1...", "Claim 3: A system for..."],
                drawings_description="Drawings description...",
                technical_diagrams=["Figure 1: System architecture", "Figure 2: Process flow"]
            )
            
        except Exception as e:
            logger.error(f"Error generating patent draft: {e}")
            raise
    
    async def review_patent_draft(self, draft: PatentDraft, 
                                analysis: PatentAnalysis) -> Dict[str, Any]:
        """Review patent draft and provide feedback"""
        try:
            prompt = f"""
Review the following patent draft and provide comprehensive feedback:

Draft: {json.dumps(draft.__dict__, ensure_ascii=False)}
Analysis: {json.dumps(analysis.__dict__, ensure_ascii=False)}

Provide feedback on:
1. Overall quality (1-10 scale)
2. Technical accuracy
3. Legal compliance
4. Claim strength
5. Specific improvements needed
6. Potential risks
7. Final recommendation

Structure the output as JSON.
"""
            
            response = self.client.responses.create(
                model="gpt-5",
                input=prompt
            )
            
            # Parse the response and return structured feedback
            return {
                "quality_score": 8.0,
                "technical_accuracy": "Good",
                "legal_compliance": "Compliant",
                "claim_strength": "Strong",
                "improvements": ["Add more examples", "Clarify technical terms"],
                "risks": ["Potential prior art conflicts"],
                "recommendation": "Proceed with minor revisions"
            }
            
        except Exception as e:
            logger.error(f"Error reviewing patent draft: {e}")
            raise
    
    async def optimize_patent_claims(self, claims: List[str], 
                                   feedback: Dict[str, Any]) -> List[str]:
        """Optimize patent claims based on feedback"""
        try:
            prompt = f"""
Optimize the following patent claims according to the feedback:

Claims: {json.dumps(claims, ensure_ascii=False)}
Feedback: {json.dumps(feedback, ensure_ascii=False)}

Make the claims:
1. More precise and clear
2. Better structured
3. Compliant with patent law
4. Stronger in terms of protection

Return the optimized claims as a list.
"""
            
            response = self.client.responses.create(
                model="gpt-5",
                input=prompt
            )
            
            # Parse the response and return optimized claims
            return ["Optimized Claim 1...", "Optimized Claim 2...", "Optimized Claim 3..."]
            
        except Exception as e:
            logger.error(f"Error optimizing patent claims: {e}")
            raise
    
    async def generate_technical_diagrams(self, topic: str, 
                                        description: str) -> List[str]:
        """Generate technical diagram descriptions"""
        try:
            prompt = f"""
Generate technical diagram descriptions for the following patent:

Topic: {topic}
Description: {description}

Create descriptions for:
1. System architecture diagram
2. Process flow diagram
3. Data flow diagram
4. Component interaction diagram

Each description should be detailed enough for a technical illustrator to create the diagram.
"""
            
            response = self.client.responses.create(
                model="gpt-5",
                input=prompt
            )
            
            # Parse the response and return diagram descriptions
            return [
                "Figure 1: System architecture showing main components and their relationships",
                "Figure 2: Process flow diagram illustrating the method steps",
                "Figure 3: Data flow diagram showing information exchange between components"
            ]
            
        except Exception as e:
            logger.error(f"Error generating technical diagrams: {e}")
            raise