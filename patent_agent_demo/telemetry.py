import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger("telemetry")


def estimate_tokens_from_text(text: str) -> int:
    if not text:
        return 0
    # Rough heuristic: 1 token ~ 4 characters
    return max(1, len(text) // 4)


class A2ALoggingProxy:
    """Proxy for AI client that logs per-agent API usage and updates metrics."""

    def __init__(self, agent_name: str, client: Any, agent_ref: Any):
        self.agent_name = agent_name
        self._client = client
        self._agent = agent_ref
        # Ensure counters exist
        self._agent.performance_metrics.setdefault("api_calls", 0)
        self._agent.performance_metrics.setdefault("api_output_tokens", 0)

    async def _log_and_update(self, method_name: str, prompt: str, output_text: str, usage: Dict[str, Any] = None):
        out_tokens = 0
        if usage and isinstance(usage, dict):
            out_tokens = usage.get("completion_tokens") or usage.get("total_tokens") or 0
        if not out_tokens:
            out_tokens = estimate_tokens_from_text(output_text)
        self._agent.performance_metrics["api_calls"] += 1
        self._agent.performance_metrics["api_output_tokens"] += out_tokens
        logger.info(
            f"API_CALL agent={self.agent_name} method={method_name} calls={self._agent.performance_metrics['api_calls']} "
            f"out_tokens={out_tokens} prompt_chars={len(prompt) if prompt else 0}")
        # Optionally log output (may be large)
        safe_out = (output_text or "")[:1000]
        logger.info(f"AGENT_API_OUTPUT agent={self.agent_name} method={method_name} preview=\n{safe_out}")

    # Methods used by agents
    async def _generate_response(self, prompt: str) -> str:
        text = await self._client._generate_response(prompt)
        usage = getattr(self._client, "last_usage", None)
        await self._log_and_update("_generate_response", prompt, text, usage)
        return text

    async def analyze_patent_topic(self, *args, **kwargs):
        result = await self._client.analyze_patent_topic(*args, **kwargs)
        await self._log_and_update("analyze_patent_topic", "", str(result), getattr(self._client, "last_usage", None))
        return result

    async def generate_patent_draft(self, *args, **kwargs):
        result = await self._client.generate_patent_draft(*args, **kwargs)
        await self._log_and_update("generate_patent_draft", "", str(result), getattr(self._client, "last_usage", None))
        return result

    async def review_patent_draft(self, *args, **kwargs):
        result = await self._client.review_patent_draft(*args, **kwargs)
        await self._log_and_update("review_patent_draft", "", str(result), getattr(self._client, "last_usage", None))
        return result

    async def optimize_patent_claims(self, *args, **kwargs):
        result = await self._client.optimize_patent_claims(*args, **kwargs)
        await self._log_and_update("optimize_patent_claims", "", str(result), getattr(self._client, "last_usage", None))
        return result

    async def generate_technical_diagrams(self, *args, **kwargs):
        result = await self._client.generate_technical_diagrams(*args, **kwargs)
        await self._log_and_update("generate_technical_diagrams", "", str(result), getattr(self._client, "last_usage", None))
        return result