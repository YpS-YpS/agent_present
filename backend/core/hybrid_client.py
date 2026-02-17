from __future__ import annotations

from typing import AsyncIterator

from backend.agents.base_agent import BaseAgent
from backend.core.mock_client import MockClient


# Keywords that the mock client can handle (PresentMon domain knowledge)
_MOCK_KEYWORDS: list[str] = [
    # Visualization
    "chart", "plot", "graph", "visualize", "show me", "draw",
    # FPS / frame analysis
    "fps", "frame time", "frametime", "frame rate",
    # Stutter / jitter
    "stutter", "jitter", "spike",
    # CPU/GPU analysis
    "cpu busy", "gpu busy", "cpubusy", "gpubusy",
    "bound", "bottleneck", "cpu vs gpu", "cpu or gpu",
    "cpu-bound", "gpu-bound", "cpu bound", "gpu bound",
    # Throttling
    "throttl", "thermal", "power limit",
    # Latency
    "latency", "input lag", "display lag",
    # Data profile
    "profile", "overview", "summary", "what data", "columns",
    # Percentiles
    "percentile", "p99", "p95", "1% low", "0.1% low",
]


def _is_mock_capable(user_message: str) -> bool:
    """Return True if the mock client can handle this query."""
    lower = user_message.lower()
    return any(kw in lower for kw in _MOCK_KEYWORDS)


class HybridClient:
    """Routes queries to mock (fast, free) or Claude (smart, paid).

    PresentMon-specific queries that the mock can handle via keyword-matching
    and direct tool calls are served locally.  Everything else (general
    questions, complex reasoning, out-of-domain) is forwarded to Claude.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int = 4096):
        self._mock = MockClient()

        # Lazy-init Claude client only when needed
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._claude = None

    def _get_claude(self):
        if self._claude is None:
            from backend.core.claude_client import ClaudeClient
            self._claude = ClaudeClient(
                api_key=self._api_key,
                model=self._model,
                max_tokens=self._max_tokens,
            )
        return self._claude

    async def run_agent_loop(
        self,
        agent: BaseAgent,
        session_id: str,
        messages: list[dict],
        max_iterations: int = 10,
    ) -> AsyncIterator[dict]:
        """Route to mock or Claude based on the user's query."""
        # Extract last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    user_message = content
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            user_message = part["text"]
                            break
                break

        if _is_mock_capable(user_message):
            # PresentMon domain query → mock client (fast, free)
            async for chunk in self._mock.run_agent_loop(
                agent=agent,
                session_id=session_id,
                messages=messages,
                max_iterations=max_iterations,
            ):
                yield chunk
        else:
            # Out-of-domain or complex query → Claude API
            claude = self._get_claude()
            async for chunk in claude.run_agent_loop(
                agent=agent,
                session_id=session_id,
                messages=messages,
                max_iterations=max_iterations,
            ):
                yield chunk
