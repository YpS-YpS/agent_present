from __future__ import annotations

from typing import Any, Callable

from backend.tools import analysis_tools, chart_tools, data_tools


# Maps tool names to their implementation functions.
# Each function takes (session_id, file_id, **kwargs) or similar.
TOOL_FUNCTIONS: dict[str, Callable] = {
    # Data tools
    "profile_data": data_tools.profile_data,

    # Analysis tools
    "compute_fps_statistics": analysis_tools.compute_fps_statistics,
    "detect_stutters": analysis_tools.detect_stutters,
    "analyze_cpu_gpu_bound": analysis_tools.analyze_cpu_gpu_bound,
    "compute_cpu_gpu_busy_stats": analysis_tools.compute_cpu_gpu_busy_stats,
    "compute_latency_stats": analysis_tools.compute_latency_stats,
    "analyze_throttling": analysis_tools.analyze_throttling,
    "get_time_segment_stats": analysis_tools.get_time_segment_stats,

    # Chart tools
    "chart_frametime_timeline": chart_tools.chart_frametime_timeline,
    "chart_fps_histogram": chart_tools.chart_fps_histogram,
    "chart_utilization_timeline": chart_tools.chart_utilization_timeline,
    "chart_gpu_power_thermal": chart_tools.chart_gpu_power_thermal,
    "chart_cpu_gpu_busy_timeline": chart_tools.chart_cpu_gpu_busy_timeline,
}


def execute_tool(tool_name: str, tool_input: dict, session_id: str) -> Any:
    """Look up and execute a tool by name.

    The tool_input dict should include 'file_id' for tools that need data access.
    The session_id is injected as the first argument.
    """
    func = TOOL_FUNCTIONS.get(tool_name)
    if func is None:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        # All analysis/chart tools take session_id and file_id as first two args
        file_id = tool_input.pop("file_id", None)
        if file_id is not None:
            return func(session_id, file_id, **tool_input)
        else:
            return func(session_id, **tool_input)
    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}
