from __future__ import annotations

import json
from typing import Any, AsyncIterator

from backend.agents.base_agent import BaseAgent
from backend.agents.tool_registry import execute_tool


class MockClient:
    """Mock LLM client for development without an API key.

    Instead of calling Claude, this directly calls tools based on keyword matching
    and wraps results in formatted text. The full tool pipeline (pandas, plotly)
    is still exercised — only the LLM reasoning is simulated.
    """

    async def run_agent_loop(
        self,
        agent: BaseAgent,
        session_id: str,
        messages: list[dict],
        max_iterations: int = 10,
    ) -> AsyncIterator[dict]:
        """Simulate an agent loop by pattern-matching the last user message."""
        # Get the last user message
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

        if not user_message:
            yield {"type": "text", "content": "I didn't receive a message. Please try again."}
            return

        lower = user_message.lower()

        # Find the file_id from the session
        from backend.core.session_store import session_store
        session = session_store.get_session(session_id)
        file_id = None
        if session and session.has_files:
            file_id = session.get_default_file_id()

        if file_id is None:
            yield {"type": "text", "content": "No files have been uploaded yet. Please upload a PresentMon CSV file first, then ask me to analyze it."}
            return

        # Route based on keywords and delegate to handler
        if any(kw in lower for kw in [
            "chart", "plot", "graph", "visualize", "show me", "draw", "display",
            # Direct viz keywords that imply a chart
            "utilization", "usage", "gpu util", "cpu util",
            "power", "temperature",
        ]):
            handler = self._handle_visualization(session_id, file_id, lower)
        elif "show " in lower and any(kw in lower for kw in [
            "utilization", "busy", "fps", "frame", "latency", "throttl",
            "power", "temp", "histogram",
        ]):
            # "Show <something>" patterns that imply visualization
            handler = self._handle_visualization(session_id, file_id, lower)
        elif any(kw in lower for kw in ["cpu busy", "gpu busy", "cpubusy", "gpubusy"]):
            handler = self._handle_cpu_gpu_busy(session_id, file_id)
        elif any(kw in lower for kw in ["stutter", "jitter", "spike"]):
            handler = self._handle_stutters(session_id, file_id)
        elif any(kw in lower for kw in ["bound", "bottleneck", "cpu vs gpu", "cpu or gpu"]):
            handler = self._handle_bound_analysis(session_id, file_id)
        elif any(kw in lower for kw in ["throttl", "thermal", "power limit"]):
            handler = self._handle_throttling(session_id, file_id)
        elif any(kw in lower for kw in ["latency", "input lag", "display lag"]):
            handler = self._handle_latency(session_id, file_id)
        elif any(kw in lower for kw in ["profile", "overview", "summary", "what data", "columns"]):
            handler = self._handle_profile(session_id, file_id)
        else:
            handler = self._handle_fps(session_id, file_id)

        async for item in handler:
            yield item

        # Emit token usage (mock mode — zero real tokens)
        yield {
            "type": "token_usage",
            "input_tokens": 0,
            "output_tokens": 0,
            "model": "mock",
        }

    async def _handle_fps(self, session_id: str, file_id: str) -> AsyncIterator[dict]:
        from backend.tools.analysis_tools import compute_fps_statistics
        result = compute_fps_statistics(session_id, file_id)
        yield {"type": "text", "content": self._format_fps_result(result)}

    async def _handle_stutters(self, session_id: str, file_id: str) -> AsyncIterator[dict]:
        from backend.tools.analysis_tools import detect_stutters
        result = detect_stutters(session_id, file_id)
        yield {"type": "text", "content": self._format_stutter_result(result)}

    async def _handle_cpu_gpu_busy(self, session_id: str, file_id: str) -> AsyncIterator[dict]:
        from backend.tools.analysis_tools import compute_cpu_gpu_busy_stats
        result = compute_cpu_gpu_busy_stats(session_id, file_id)
        yield {"type": "text", "content": self._format_cpu_gpu_busy_result(result)}

    async def _handle_bound_analysis(self, session_id: str, file_id: str) -> AsyncIterator[dict]:
        from backend.tools.analysis_tools import analyze_cpu_gpu_bound
        result = analyze_cpu_gpu_bound(session_id, file_id)
        yield {"type": "text", "content": self._format_bound_result(result)}

    async def _handle_throttling(self, session_id: str, file_id: str) -> AsyncIterator[dict]:
        from backend.tools.analysis_tools import analyze_throttling
        result = analyze_throttling(session_id, file_id)
        yield {"type": "text", "content": self._format_throttling_result(result)}

    async def _handle_latency(self, session_id: str, file_id: str) -> AsyncIterator[dict]:
        from backend.tools.analysis_tools import compute_latency_stats
        result = compute_latency_stats(session_id, file_id)
        yield {"type": "text", "content": self._format_latency_result(result)}

    async def _handle_profile(self, session_id: str, file_id: str) -> AsyncIterator[dict]:
        from backend.tools.data_tools import profile_data
        result = profile_data(session_id, file_id)
        yield {"type": "text", "content": self._format_profile_result(result)}

    async def _handle_visualization(self, session_id: str, file_id: str, query: str) -> AsyncIterator[dict]:
        from backend.tools import chart_tools

        if any(kw in query for kw in ["histogram", "distribution", "fps dist"]):
            result = chart_tools.chart_fps_histogram(session_id, file_id)
        elif any(kw in query for kw in ["cpu busy", "gpu busy", "busy", "bound", "bottleneck"]):
            result = chart_tools.chart_cpu_gpu_busy_timeline(session_id, file_id)
        elif any(kw in query for kw in ["utilization", "usage", "gpu util", "cpu util"]):
            result = chart_tools.chart_utilization_timeline(session_id, file_id)
        elif any(kw in query for kw in ["power", "thermal", "temperature", "temp"]):
            result = chart_tools.chart_gpu_power_thermal(session_id, file_id)
        else:
            result = chart_tools.chart_frametime_timeline(session_id, file_id)

        if result.get("type") == "chart":
            yield {"type": "text", "content": "Here's the chart:"}
            yield {"type": "chart", "data": result["plotly_json"]}
        else:
            yield {"type": "text", "content": f"Could not generate chart: {result.get('message', 'Unknown error')}"}

    # --- Formatting helpers ---

    @staticmethod
    def _format_fps_result(r: dict) -> str:
        if "error" in r:
            return f"Error: {r['error']}"
        fps = r["fps"]
        ft = r["frametime_ms"]
        return (
            f"## FPS Statistics\n\n"
            f"**Duration:** {r['duration_seconds']}s ({r['frame_count']:,} frames)\n\n"
            f"| Metric | Value |\n|--------|-------|\n"
            f"| Average FPS | {fps['average']} |\n"
            f"| Median FPS | {fps['median']} |\n"
            f"| 1% Low FPS | {fps['p1']} |\n"
            f"| 0.1% Low FPS | {fps['p0_1']} |\n"
            f"| Min FPS | {fps['min']} |\n"
            f"| Max FPS | {fps['max']} |\n\n"
            f"**Frame Time:** avg {ft['average']}ms, p99 {ft['p99']}ms, max {ft['max']}ms"
        )

    @staticmethod
    def _format_stutter_result(r: dict) -> str:
        if "error" in r:
            return f"Error: {r['error']}"
        text = (
            f"## Stutter Analysis\n\n"
            f"**{r['stutter_count']}** stutters detected out of **{r['total_frames']:,}** frames "
            f"(**{r['stutter_percentage']}%**)\n\n"
            f"Threshold: >{r['threshold_multiplier']}x rolling average (avg frame time: {r['avg_frametime_ms']}ms)\n"
        )
        if r["worst_stutters"]:
            text += "\n**Worst stutters:**\n\n| Time (s) | Frame Time (ms) | Expected (ms) | Severity |\n|----------|----------------|--------------|----------|\n"
            for s in r["worst_stutters"][:5]:
                text += f"| {s.get('time_sec', 'N/A')} | {s['frametime_ms']} | {s['expected_ms']} | {s['severity_multiplier']}x |\n"
        return text

    @staticmethod
    def _format_cpu_gpu_busy_result(r: dict) -> str:
        if "error" in r:
            return f"Error: {r['error']}"
        text = "## CPU & GPU Busy Time Analysis\n\n"

        for label, display in [("cpu_busy_ms", "CPU Busy"), ("gpu_busy_ms", "GPU Busy")]:
            data = r.get(label)
            if isinstance(data, dict):
                text += (
                    f"**{display}:**\n\n"
                    f"| Metric | Value |\n|--------|-------|\n"
                    f"| Average | {data['average']}ms |\n"
                    f"| Median | {data['median']}ms |\n"
                    f"| P95 | {data['p95']}ms |\n"
                    f"| P99 | {data['p99']}ms |\n"
                    f"| Max | {data['max']}ms |\n"
                    f"| Std Dev | {data['std_dev']}ms |\n\n"
                )
            elif data == "not_available":
                text += f"**{display}:** Column not present in this capture\n\n"

        # Wait times
        for label, display in [("cpu_wait_ms", "CPU Wait"), ("gpu_wait_ms", "GPU Wait")]:
            data = r.get(label)
            if isinstance(data, dict):
                text += f"**{display}:** avg {data['average']}ms, p95 {data['p95']}ms, max {data['max']}ms\n\n"

        # Bottleneck summary
        bs = r.get("bottleneck_summary")
        if bs:
            text += (
                f"### Bottleneck Summary\n\n"
                f"**Overall: {bs['overall']}** "
                f"(CPU-bound {bs['cpu_bound_percentage']}% / GPU-bound {bs['gpu_bound_percentage']}% of frames)\n\n"
                f"{bs['interpretation']}\n\n"
            )

        # Frame overhead
        overhead = r.get("frame_overhead_ms")
        if isinstance(overhead, dict):
            text += f"**Frame Overhead:** avg {overhead['average']}ms — {overhead['description']}\n"

        return text

    @staticmethod
    def _format_bound_result(r: dict) -> str:
        if "error" in r:
            return f"Error: {r['error']}"
        return (
            f"## CPU/GPU Bottleneck Analysis\n\n"
            f"**Overall:** {r['overall_bottleneck']}\n\n"
            f"| Metric | Value |\n|--------|-------|\n"
            f"| CPU-bound frames | {r['cpu_bound_frames']:,} ({r['cpu_bound_percentage']}%) |\n"
            f"| GPU-bound frames | {r['gpu_bound_frames']:,} ({r['gpu_bound_percentage']}%) |\n"
            f"| Avg CPU busy | {r['avg_cpu_busy_ms']}ms |\n"
            f"| Avg GPU busy | {r['avg_gpu_busy_ms']}ms |\n"
        )

    @staticmethod
    def _format_throttling_result(r: dict) -> str:
        if "error" in r:
            return f"Error: {r['error']}"
        text = f"## GPU Throttling Analysis\n\n"
        if not r.get("any_throttling_detected"):
            text += "No throttling detected during this capture.\n"
        else:
            text += "| Throttle Type | Frames | Percentage |\n|--------------|--------|------------|\n"
            for label, data in r.items():
                if isinstance(data, dict) and data.get("throttled_frames", 0) > 0:
                    text += f"| {label} | {data['throttled_frames']:,} | {data['percentage']}% |\n"
        return text

    @staticmethod
    def _format_latency_result(r: dict) -> str:
        text = "## Latency Analysis\n\n"
        for label, data in r.items():
            if isinstance(data, dict):
                text += (
                    f"**{label.replace('_', ' ').title()}:** "
                    f"avg {data['average']}ms, median {data['median']}ms, "
                    f"p99 {data['p99']}ms\n\n"
                )
            elif data == "all_na":
                text += f"**{label.replace('_', ' ').title()}:** No data available (all NA)\n\n"
            elif data == "not_available":
                text += f"**{label.replace('_', ' ').title()}:** Column not present in this capture\n\n"
        return text

    @staticmethod
    def _format_profile_result(r: dict) -> str:
        text = (
            f"## File Profile\n\n"
            f"**File:** {r.get('filename', 'unknown')}\n"
            f"**Source:** {r.get('source_tool', 'unknown')}\n"
            f"**Application:** {r.get('application', 'unknown')}\n"
            f"**Rows:** {r.get('total_rows', 0):,}\n"
            f"**Duration:** {r.get('duration_seconds', 0)}s\n"
            f"**Columns:** {r.get('available_columns', 0)} available, {r.get('na_columns', 0)} empty\n"
        )
        if "avg_fps" in r:
            text += f"**Avg FPS:** {r['avg_fps']}\n"
        return text
