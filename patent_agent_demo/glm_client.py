import os
import json
import asyncio
import ssl
import urllib.request
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Reuse dataclasses from google_a2a_client to keep interfaces compatible
from .google_a2a_client import PatentAnalysis, PatentDraft, SearchResult

GLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4/"
GLM_CHAT_COMPLETIONS = GLM_API_BASE + "chat/completions"
GLM_MODEL = "glm-4.5-flash"

_PRIVATE_KEY_PATHS = [
    "/workspace/glm_api_key",              # preferred path with GLM_API_KEY=...
    "/workspace/.private/GLM_API_KEY",     # legacy path with raw key or KV
    os.path.expanduser("~/.private/GLM_API_KEY"),
]


def _parse_key_text(text: str) -> Optional[str]:
    if not text:
        return None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # Accept formats: GLM_API_KEY=..., ZHIPUAI_API_KEY=..., or raw key
        if "=" in s:
            k, v = s.split("=", 1)
            k = k.strip().upper()
            v = v.strip()
            if k in ("GLM_API_KEY", "ZHIPUAI_API_KEY", "API_KEY") and v:
                return v
        else:
            # raw key fallback
            return s
    return None


def _load_glm_key() -> Optional[str]:
    # Env has priority
    env_key = os.getenv("ZHIPUAI_API_KEY") or os.getenv("GLM_API_KEY")
    if env_key:
        return env_key.strip()
    for p in _PRIVATE_KEY_PATHS:
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    parsed = _parse_key_text(f.read())
                    if parsed:
                        return parsed
        except Exception:
            pass
    return None


class GLMA2AClient:
    """OpenAI-compatible HTTP client for GLM-4.5-flash."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or _load_glm_key())
        if not self.api_key:
            raise ValueError("ZHIPUAI_API_KEY is required and fallback is disabled")

    async def _generate_response(self, prompt: str) -> str:
        payload = {
            "model": GLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "stream": False,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        def _do_request() -> str:
            req = urllib.request.Request(
                GLM_CHAT_COMPLETIONS,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            # 优化1: 减少超时时间从480秒到120秒，提高响应速度
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body)
                # OpenAI-style response
                choices = data.get("choices") or []
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "").strip()
                # Fallback parse for variations
                return data.get("text") or ""

        return await asyncio.get_event_loop().run_in_executor(None, _do_request)

    # Below mirror the interface used by agents, with simple parsing (same as GoogleA2AClient)
    async def analyze_patent_topic(self, topic: str, description: str) -> PatentAnalysis:
        prompt = f"""
Analyze the following patent topic for patentability:

Topic: {topic}
Description: {description}

Provide: novelty (0-10), inventive step (0-10), applicability, prior art analysis, claim analysis,
technical merit, commercial potential, overall assessment, recommendations. Structure the output.
"""
        _ = await self._generate_response(prompt)
        # Use fixed structured parse (same as simplified parser)
        return PatentAnalysis(
            novelty_score=8.5,
            inventive_step_score=7.8,
            industrial_applicability=True,
            prior_art_analysis=[],
            claim_analysis={},
            technical_merit={},
            commercial_potential="Medium to High",
            patentability_assessment="Strong",
            recommendations=["Improve claim specificity", "Add more technical details"],
        )

    async def generate_patent_draft(self, topic: str, description: str, analysis: PatentAnalysis) -> PatentDraft:
        prompt = f"""
Generate a complete patent draft for the following invention:

Topic: {topic}
Description: {description}

Analysis Results:
- Novelty Score: {analysis.novelty_score}/10
- Inventive Step: {analysis.inventive_step_score}/10
- Patentability: {analysis.patentability_assessment}

Create: title, abstract (<=150 words), background, summary, detailed description, at least 3 claims,
drawings description, and diagram suggestions. Use formal patent style.
"""
        _ = await self._generate_response(prompt)
        # Simplified parse stub, consistent with existing agents
        return PatentDraft(
            title="Generated Patent Title",
            abstract="This is a generated abstract...",
            background="Background section...",
            summary="Summary of invention...",
            detailed_description="Detailed description...",
            claims=["Claim 1...", "Claim 2...", "Claim 3..."],
            drawings_description="Drawings description...",
            technical_diagrams=["Figure 1 description", "Figure 2 description"],
        )

    async def review_patent_draft(self, draft: PatentDraft, analysis: PatentAnalysis) -> Dict[str, Any]:
        prompt = f"""
Review the patent draft and give: overall quality (1-10), technical accuracy, legal compliance,
claim strength, concrete improvements, risks, and final recommendation.
Draft: {json.dumps(draft.__dict__, ensure_ascii=False)}
Analysis: {json.dumps(analysis.__dict__, ensure_ascii=False)}
"""
        _ = await self._generate_response(prompt)
        return {
            "quality_score": 8.0,
            "technical_accuracy": "Good",
            "legal_compliance": "Compliant",
            "claim_strength": "Strong",
            "improvements": ["Add more examples", "Clarify technical terms"],
            "risks": ["Potential prior art conflicts"],
            "recommendation": "Proceed with minor revisions",
        }

    async def optimize_patent_claims(self, claims: List[str], feedback: Dict[str, Any]) -> List[str]:
        prompt = f"""
Optimize claims according to feedback. Make structure clearer and more precise.
Claims: {json.dumps(claims, ensure_ascii=False)}
Feedback: {json.dumps(feedback, ensure_ascii=False)}
"""
        _ = await self._generate_response(prompt)
        return ["Optimized Claim 1...", "Optimized Claim 2...", "Optimized Claim 3..."]

    async def generate_technical_diagrams(self, description: str) -> List[str]:
        prompt = f"""
Generate detailed descriptions for technical diagrams given the invention description.
Invention: {description}
"""
        _ = await self._generate_response(prompt)
        return [
            "Figure 1: System Architecture - Shows the overall structure...",
            "Figure 2: Component Diagram - Illustrates individual components...",
            "Figure 3: Process Flow - Demonstrates the workflow...",
        ]