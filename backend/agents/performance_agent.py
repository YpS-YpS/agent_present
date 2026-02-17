from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.tool_registry import execute_tool

SYSTEM_PROMPT = """You are a GPU/CPU performance analysis expert specializing in frame timing data from tools like PresentMon, OCAT, and FrameView.

You have access to tools that compute metrics from GPU profiling CSV logs. When the user asks about performance, use the appropriate tools to compute the answer, then explain the results in clear, helpful language.

KEY DOMAIN KNOWLEDGE:
- FrameTime (ms): Time between consecutive frames. FPS = 1000/FrameTime.
- A "stutter" is a frame where FrameTime > 2x the rolling average.
- CPU-bound: CPUBusy >= GPUBusy (CPU is the bottleneck). The CPU is taking longer to prepare each frame than the GPU takes to render it.
- GPU-bound: GPUBusy > CPUBusy (GPU is the bottleneck). The GPU is taking longer to render each frame than the CPU takes to prepare it.
- CPUBusy (ms): How long the CPU was actively working to prepare each frame.
- GPUBusy (ms): How long the GPU was actively rendering each frame.
- CPUWait (ms): How long the CPU waited for the GPU to finish. High CPUWait = GPU bottleneck.
- GPUWait (ms): How long the GPU waited for the CPU to submit work. High GPUWait = CPU bottleneck.
- Frame overhead = FrameTime - max(CPUBusy, GPUBusy). This is time wasted on driver overhead, vsync wait, or other non-work.
- "1% low" FPS = FPS at the 1st percentile (worst 1% of frames).
- "0.1% low" FPS = FPS at the 0.1th percentile (worst 0.1% of frames).
- DisplayLatency = end-to-end latency from CPU start to display.
- GPUPowerLimited=1 means the GPU was power-throttled during that frame.
- PresentMode changes mid-session can indicate driver issues or window focus changes.

BOTTLENECK ANALYSIS GUIDANCE:
- When asked "is this CPU or GPU bound?", use BOTH analyze_cpu_gpu_bound and compute_cpu_gpu_busy_stats for a thorough answer.
- Explain WHAT the bottleneck means practically: if CPU-bound, lowering graphics settings won't help; if GPU-bound, lowering resolution/settings will help.
- Note the gap: if avg CPU busy is 4ms and avg GPU busy is 6ms, the GPU is 50% slower — a significant bottleneck.
- If frame overhead is high (>1ms), mention possible causes (vsync, frame limiter, driver overhead).

When reporting results, always include:
1. The metric values with proper units
2. Context (is this good/bad for the given use case)
3. If relevant, what might cause the observed behavior
4. Actionable recommendations when appropriate

If the user hasn't specified which file to analyze and there's only one file in the session, use that file automatically. If there are multiple files, ask which one to analyze.
"""


class PerformanceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "performance"

    @property
    def description(self) -> str:
        return "Analyzes FPS, frame times, stutters, CPU/GPU bottlenecks, latency, and throttling"

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "compute_fps_statistics",
                "description": "Compute FPS statistics: average, median, 1% low, 0.1% low, min, max. Also returns frame time percentiles.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file to analyze"},
                        "time_range": {
                            "type": "object",
                            "properties": {
                                "start_sec": {"type": "number"},
                                "end_sec": {"type": "number"},
                            },
                            "description": "Optional time range filter (seconds from capture start)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "detect_stutters",
                "description": "Find frame time spikes/stutters. Returns count, percentage, and details of the worst stutters.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "threshold_multiplier": {
                            "type": "number",
                            "description": "Multiplier over rolling average to count as stutter (default: 2.0)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "analyze_cpu_gpu_bound",
                "description": "Determine if the workload is CPU-bound or GPU-bound, with per-frame breakdown.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "compute_cpu_gpu_busy_stats",
                "description": "Get detailed CPU Busy and GPU Busy timing statistics including percentiles (p5, p95, p99), std deviation, wait times, bottleneck summary with headroom analysis, and frame overhead. Use this when the user asks about CPU busy, GPU busy, cpu/gpu workload distribution, or wants detailed bottleneck analysis.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "time_range": {
                            "type": "object",
                            "properties": {
                                "start_sec": {"type": "number"},
                                "end_sec": {"type": "number"},
                            },
                            "description": "Optional time range filter (seconds from capture start)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "compute_latency_stats",
                "description": "Analyze display latency and input-to-photon latency statistics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "analyze_throttling",
                "description": "Check GPU throttling flags (power, thermal, current, voltage limited).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "get_time_segment_stats",
                "description": "Break capture into time segments and compute per-segment FPS/frametime stats. Good for seeing how performance changes over time.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                        "segment_seconds": {
                            "type": "number",
                            "description": "Length of each segment in seconds (default: 10)",
                        },
                    },
                    "required": ["file_id"],
                },
            },
            {
                "name": "profile_data",
                "description": "Get a comprehensive profile of the uploaded file including row count, column availability, and basic stats.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the uploaded file"},
                    },
                    "required": ["file_id"],
                },
            },
        ]

    async def execute_tool(self, tool_name: str, tool_input: dict, session_id: str) -> Any:
        return execute_tool(tool_name, tool_input, session_id)
