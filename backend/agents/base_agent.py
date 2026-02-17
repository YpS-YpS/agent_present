from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Abstract base class for all specialist agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what this agent does."""
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt that defines this agent's role and expertise."""
        ...

    @abstractmethod
    def get_tools(self) -> list[dict]:
        """Return Claude API tool definitions (name, description, input_schema)."""
        ...

    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: dict, session_id: str) -> Any:
        """Execute a tool call and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool input parameters from Claude
            session_id: Current session ID for data access
        """
        ...
