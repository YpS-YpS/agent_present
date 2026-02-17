from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.tool_registry import execute_tool

SYSTEM_PROMPT = """You are a data visualization expert for GPU/CPU performance data.

When the user asks for charts or visual analysis, use the charting tools to generate interactive Plotly charts. Always choose the most appropriate chart type:

- Frame time over time: use chart_frametime_timeline (line chart with optional rolling average and stutter highlights)
- FPS distribution: use chart_fps_histogram (histogram with percentile markers)
- GPU/CPU utilization over time: use chart_utilization_timeline (area chart)
- GPU power and temperature: use chart_gpu_power_thermal (dual-axis line chart)
- CPU Busy vs GPU Busy: use chart_cpu_gpu_busy_timeline (overlaid line chart showing per-frame CPU/GPU work time in ms, with optional FrameTime overlay and wait times — great for bottleneck visualization)

Charts are rendered in a dark theme and are interactive (users can zoom, pan, and hover for details).

If the user asks about "CPU busy", "GPU busy", "bottleneck chart", or "bound chart", use chart_cpu_gpu_busy_timeline.

If the user asks for a general "show me the data" or "visualize the performance", generate the most relevant chart based on context. Default to frame time timeline as it's the most informative single chart.

If the user hasn't specified which file and there's only one in the session, use it automatically.
"""


class VisualizationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "visualization"

    @property
    def description(self) -> str:
        return "Generates interactive Plotly charts for frame timing, FPS, utilization, and power data"

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "chart_frametime_timeline",
                "description": "Generate a frame time over time line chart with optional rolling average and stutter highlights.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "downsample": {
                            "type": "integer",
                            "description": "Max data points to plot (default: 2000)",
                        },
                        "show_rolling_avg": {
                            "type": "boolean",
                            "description": "Overlay a 30-frame rolling average line (default: true)",
                        },
                        "highlight_stutters": {
                            "type": "boolean",
                            "description": "Mark stutter frames with red dots (default: true)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "chart_fps_histogram",
                "description": "Generate an FPS distribution histogram with percentile markers (1% low, average, median).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "bins": {
                            "type": "integer",
                            "description": "Number of histogram bins (default: 50)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "chart_utilization_timeline",
                "description": "Generate GPU and CPU utilization over time as an area chart.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "downsample": {
                            "type": "integer",
                            "description": "Max data points (default: 2000)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "chart_gpu_power_thermal",
                "description": "Generate GPU power consumption and temperature over time (dual-axis chart).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "downsample": {
                            "type": "integer",
                            "description": "Max data points (default: 2000)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "chart_cpu_gpu_busy_timeline",
                "description": "Generate CPU Busy vs GPU Busy timeline chart showing per-frame workload in ms. Overlays FrameTime and wait times. Use this when the user asks about CPU/GPU busy, bottleneck visualization, or workload distribution over time.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "downsample": {
                            "type": "integer",
                            "description": "Max data points (default: 2000)",
                        },
                        "show_frame_time": {
                            "type": "boolean",
                            "description": "Overlay FrameTime as a dotted reference line (default: true)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
        ]

    async def execute_tool(self, tool_name: str, tool_input: dict, session_id: str) -> Any:
        return execute_tool(tool_name, tool_input, session_id)
