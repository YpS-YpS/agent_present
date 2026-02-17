from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.tool_registry import execute_tool
from backend.tools.comparison_tools import compare_files

SYSTEM_PROMPT = """You are a performance comparison specialist. You help users compare GPU/CPU performance across multiple PresentMon captures.

When the user wants to compare files, use the compare_files tool to get side-by-side statistics.
Present results as a clear comparison table highlighting:
- Which file/configuration is faster
- The magnitude of the difference (absolute and percentage)
- Any notable differences in stuttering, throttling, or bottleneck patterns

If the user uploaded only one file, let them know they need at least two files to compare.
"""


class ComparisonAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "comparison"

    @property
    def description(self) -> str:
        return "Compares performance metrics across multiple log files"

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "compare_files",
                "description": "Compare FPS and frame time statistics across multiple uploaded files. Returns per-file stats and deltas.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file IDs to compare (at least 2)",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional labels for each file (e.g. 'Before', 'After')",
                        },
                    },
                    "required": ["file_ids"],
                },
            },
            {
                "name": "compute_fps_statistics",
                "description": "Compute FPS statistics for a single file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "File ID to analyze"},
                    },
                    "required": ["file_id"],
                },
            },
        ]

    async def execute_tool(self, tool_name: str, tool_input: dict, session_id: str) -> Any:
        if tool_name == "compare_files":
            file_ids = tool_input.get("file_ids", [])
            labels = tool_input.get("labels")
            return compare_files(session_id, file_ids, labels)
        else:
            return execute_tool(tool_name, tool_input, session_id)
