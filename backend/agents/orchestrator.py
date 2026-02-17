from __future__ import annotations

from backend.agents.base_agent import BaseAgent
from backend.agents.comparison_agent import ComparisonAgent
from backend.agents.performance_agent import PerformanceAgent
from backend.agents.visualization_agent import VisualizationAgent


class Orchestrator:
    """Routes user queries to the appropriate specialist agent.

    Uses fast keyword-based routing. Falls back to a default agent for ambiguous queries.
    """

    ROUTING_RULES: list[tuple[list[str], str]] = [
        # Visualization keywords (check first — more specific)
        (["chart", "plot", "graph", "visualize", "show me", "draw", "display chart"], "visualization"),

        # Performance keywords
        (["fps", "frame time", "frametime", "stutter", "jitter", "latency",
          "cpu bound", "gpu bound", "cpu-bound", "gpu-bound", "bottleneck",
          "cpu busy", "gpu busy", "cpubusy", "gpubusy", "cpu wait", "gpu wait",
          "workload", "bound analysis",
          "percentile", "p99", "p95",
          "1% low", "0.1% low", "performance", "analyze", "analysis",
          "throttle", "throttling", "thermal", "power limit"], "performance"),

        # Comparison keywords
        (["compare", "comparison", "difference", "vs", "versus", "side by side",
          "before and after", "benchmark"], "comparison"),

        # Data/upload keywords
        (["upload", "load", "file", "columns", "profile", "what data", "what's in"], "performance"),
    ]

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {
            "performance": PerformanceAgent(),
            "visualization": VisualizationAgent(),
            "comparison": ComparisonAgent(),
        }

    def register_agent(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def classify_intent(self, message: str) -> str:
        """Fast keyword-based intent classification."""
        lower = message.lower()

        for keywords, agent_name in self.ROUTING_RULES:
            for keyword in keywords:
                if keyword in lower:
                    return agent_name

        # Default to performance agent for general queries
        return "performance"

    def route(self, message: str) -> BaseAgent:
        """Route a message to the appropriate agent."""
        intent = self.classify_intent(message)
        agent = self._agents.get(intent)
        if agent is None:
            # Fallback to performance agent
            agent = self._agents["performance"]
        return agent

    def get_available_agents(self) -> list[dict]:
        """List all registered agents."""
        return [
            {"name": a.name, "description": a.description}
            for a in self._agents.values()
        ]
