from __future__ import annotations

import pandas as pd
import numpy as np

from backend.tools.data_tools import get_dataframe, filter_by_time_range


def compute_fps_statistics(
    session_id: str, file_id: str, time_range: dict | None = None
) -> dict:
    """Compute comprehensive FPS statistics from frame time data."""
    df = get_dataframe(session_id, file_id)

    if time_range:
        df = filter_by_time_range(df, time_range.get("start_sec"), time_range.get("end_sec"))

    if "FrameTime" not in df.columns or len(df) == 0:
        return {"error": "No FrameTime data available"}

    frame_times = df["FrameTime"].dropna().values
    if len(frame_times) == 0:
        return {"error": "All FrameTime values are NA"}

    fps = 1000.0 / frame_times

    duration = 0.0
    if "CPUStartTime" in df.columns and len(df) > 1:
        duration = float(df["CPUStartTime"].iloc[-1] - df["CPUStartTime"].iloc[0])

    return {
        "frame_count": int(len(frame_times)),
        "duration_seconds": round(duration, 2),
        "fps": {
            "average": round(float(np.mean(fps)), 1),
            "median": round(float(np.median(fps)), 1),
            "p5": round(float(np.percentile(fps, 5)), 1),
            "p1": round(float(np.percentile(fps, 1)), 1),
            "p0_1": round(float(np.percentile(fps, 0.1)), 1),
            "min": round(float(np.min(fps)), 1),
            "max": round(float(np.max(fps)), 1),
        },
        "frametime_ms": {
            "average": round(float(np.mean(frame_times)), 2),
            "median": round(float(np.median(frame_times)), 2),
            "p95": round(float(np.percentile(frame_times, 95)), 2),
            "p99": round(float(np.percentile(frame_times, 99)), 2),
            "p99_9": round(float(np.percentile(frame_times, 99.9)), 2),
            "max": round(float(np.max(frame_times)), 2),
            "min": round(float(np.min(frame_times)), 2),
        },
    }


def detect_stutters(
    session_id: str, file_id: str, threshold_multiplier: float = 2.0
) -> dict:
    """Detect frame time spikes/stutters using rolling average comparison."""
    df = get_dataframe(session_id, file_id)

    if "FrameTime" not in df.columns:
        return {"error": "No FrameTime data available"}

    ft = df["FrameTime"].dropna().values
    if len(ft) < 10:
        return {"error": "Not enough frames for stutter analysis"}

    rolling_avg = pd.Series(ft).rolling(window=60, min_periods=1).mean().values
    stutter_mask = ft > (rolling_avg * threshold_multiplier)
    stutter_indices = np.where(stutter_mask)[0]

    # Get timestamps if available
    timestamps = None
    if "CPUStartTime" in df.columns:
        timestamps = df["CPUStartTime"].dropna().values

    # Top 10 worst stutters
    worst_stutters = []
    if len(stutter_indices) > 0:
        sorted_by_severity = stutter_indices[np.argsort(ft[stutter_indices])[::-1]][:10]
        for i in sorted_by_severity:
            stutter = {
                "frame_index": int(i),
                "frametime_ms": round(float(ft[i]), 2),
                "expected_ms": round(float(rolling_avg[i]), 2),
                "severity_multiplier": round(float(ft[i] / rolling_avg[i]), 2),
            }
            if timestamps is not None and i < len(timestamps):
                stutter["time_sec"] = round(float(timestamps[i]), 2)
            worst_stutters.append(stutter)

    return {
        "total_frames": int(len(ft)),
        "stutter_count": int(stutter_mask.sum()),
        "stutter_percentage": round(float(stutter_mask.sum() / len(ft) * 100), 2),
        "threshold_multiplier": threshold_multiplier,
        "avg_frametime_ms": round(float(np.mean(ft)), 2),
        "worst_stutters": worst_stutters,
    }


def analyze_cpu_gpu_bound(session_id: str, file_id: str) -> dict:
    """Determine if workload is CPU-bound or GPU-bound."""
    df = get_dataframe(session_id, file_id)

    required = {"CPUBusy", "GPUBusy"}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        return {"error": f"Missing columns: {missing}"}

    cpu_busy = df["CPUBusy"].dropna().values
    gpu_busy = df["GPUBusy"].dropna().values
    min_len = min(len(cpu_busy), len(gpu_busy))
    cpu_busy = cpu_busy[:min_len]
    gpu_busy = gpu_busy[:min_len]

    cpu_bound_mask = cpu_busy >= gpu_busy
    cpu_bound_count = int(cpu_bound_mask.sum())
    gpu_bound_count = int((~cpu_bound_mask).sum())

    result = {
        "overall_bottleneck": "CPU-bound" if cpu_bound_count > gpu_bound_count else "GPU-bound",
        "cpu_bound_frames": cpu_bound_count,
        "gpu_bound_frames": gpu_bound_count,
        "cpu_bound_percentage": round(float(cpu_bound_count / min_len * 100), 1),
        "gpu_bound_percentage": round(float(gpu_bound_count / min_len * 100), 1),
        "avg_cpu_busy_ms": round(float(np.mean(cpu_busy)), 2),
        "avg_gpu_busy_ms": round(float(np.mean(gpu_busy)), 2),
    }

    if "CPUWait" in df.columns:
        result["avg_cpu_wait_ms"] = round(float(df["CPUWait"].dropna().mean()), 2)
    if "GPUWait" in df.columns:
        result["avg_gpu_wait_ms"] = round(float(df["GPUWait"].dropna().mean()), 2)

    return result


def compute_cpu_gpu_busy_stats(
    session_id: str, file_id: str, time_range: dict | None = None
) -> dict:
    """Compute detailed CPU Busy and GPU Busy timing statistics with bottleneck analysis."""
    df = get_dataframe(session_id, file_id)

    if time_range:
        df = filter_by_time_range(df, time_range.get("start_sec"), time_range.get("end_sec"))

    required = {"CPUBusy", "GPUBusy"}
    available = required.intersection(set(df.columns))
    if not available:
        return {"error": f"Missing columns: {required - set(df.columns)}"}

    result: dict = {}

    for col, label in [("CPUBusy", "cpu_busy_ms"), ("GPUBusy", "gpu_busy_ms")]:
        if col in df.columns:
            vals = df[col].dropna().values
            if len(vals) > 0:
                result[label] = {
                    "average": round(float(np.mean(vals)), 3),
                    "median": round(float(np.median(vals)), 3),
                    "p5": round(float(np.percentile(vals, 5)), 3),
                    "p95": round(float(np.percentile(vals, 95)), 3),
                    "p99": round(float(np.percentile(vals, 99)), 3),
                    "min": round(float(np.min(vals)), 3),
                    "max": round(float(np.max(vals)), 3),
                    "std_dev": round(float(np.std(vals)), 3),
                }
            else:
                result[label] = "all_na"
        else:
            result[label] = "not_available"

    # Optional: CPUWait and GPUWait
    for col, label in [("CPUWait", "cpu_wait_ms"), ("GPUWait", "gpu_wait_ms")]:
        if col in df.columns:
            vals = df[col].dropna().values
            if len(vals) > 0:
                result[label] = {
                    "average": round(float(np.mean(vals)), 3),
                    "median": round(float(np.median(vals)), 3),
                    "p95": round(float(np.percentile(vals, 95)), 3),
                    "max": round(float(np.max(vals)), 3),
                }

    # Bottleneck breakdown per frame
    if "CPUBusy" in df.columns and "GPUBusy" in df.columns:
        cpu_busy = df["CPUBusy"].dropna().values
        gpu_busy = df["GPUBusy"].dropna().values
        min_len = min(len(cpu_busy), len(gpu_busy))
        cpu_busy = cpu_busy[:min_len]
        gpu_busy = gpu_busy[:min_len]

        cpu_bound_mask = cpu_busy >= gpu_busy
        cpu_bound_pct = round(float(cpu_bound_mask.sum() / min_len * 100), 1)
        gpu_bound_pct = round(100.0 - cpu_bound_pct, 1)

        # Compute the "headroom" — how much faster the non-bottleneck side is
        diff = cpu_busy - gpu_busy  # positive = CPU is slower (CPU-bound)
        avg_diff = round(float(np.mean(diff)), 3)

        result["bottleneck_summary"] = {
            "overall": "CPU-bound" if cpu_bound_pct > 50 else "GPU-bound",
            "cpu_bound_percentage": cpu_bound_pct,
            "gpu_bound_percentage": gpu_bound_pct,
            "avg_cpu_minus_gpu_ms": avg_diff,
            "interpretation": (
                f"CPU is on average {abs(avg_diff):.2f}ms "
                + ("slower" if avg_diff > 0 else "faster")
                + " than GPU per frame"
            ),
            "total_frames_analyzed": min_len,
        }

    # FrameTime vs busy times — how much idle/overhead
    if "FrameTime" in df.columns and "CPUBusy" in df.columns and "GPUBusy" in df.columns:
        ft = df["FrameTime"].dropna().values
        cpu_b = df["CPUBusy"].dropna().values
        gpu_b = df["GPUBusy"].dropna().values
        min_len3 = min(len(ft), len(cpu_b), len(gpu_b))
        ft = ft[:min_len3]
        max_busy = np.maximum(cpu_b[:min_len3], gpu_b[:min_len3])
        overhead = ft - max_busy
        if len(overhead) > 0:
            result["frame_overhead_ms"] = {
                "average": round(float(np.mean(overhead)), 3),
                "description": "Average time per frame not spent in CPU/GPU work (driver overhead, vsync wait, etc.)",
            }

    return result


def compute_latency_stats(session_id: str, file_id: str) -> dict:
    """Analyze display and input-to-photon latency."""
    df = get_dataframe(session_id, file_id)
    result = {}

    for col, label in [
        ("DisplayLatency", "display_latency_ms"),
        ("InstrumentedLatency", "instrumented_latency_ms"),
        ("AllInputToPhotonLatency", "input_to_photon_ms"),
        ("ClickToPhotonLatency", "click_to_photon_ms"),
    ]:
        if col in df.columns:
            vals = df[col].dropna()
            if len(vals) > 0:
                result[label] = {
                    "average": round(float(vals.mean()), 2),
                    "median": round(float(vals.median()), 2),
                    "p95": round(float(np.percentile(vals, 95)), 2),
                    "p99": round(float(np.percentile(vals, 99)), 2),
                    "min": round(float(vals.min()), 2),
                    "max": round(float(vals.max()), 2),
                }
            else:
                result[label] = "all_na"
        else:
            result[label] = "not_available"

    return result


def analyze_throttling(session_id: str, file_id: str) -> dict:
    """Check GPU throttling flags across the capture."""
    df = get_dataframe(session_id, file_id)

    throttle_cols = {
        "GPUPowerLimited": "Power Limited",
        "GPUTemperatureLimited": "Temperature Limited",
        "GPUCurrentLimited": "Current Limited",
        "GPUVoltageLimited": "Voltage Limited",
        "GPUUtilizationLimited": "Utilization Limited",
        "GPUMemoryPowerLimited": "Memory Power Limited",
        "GPUMemoryTemperatureLimited": "Memory Temperature Limited",
        "GPUMemoryCurrentLimited": "Memory Current Limited",
        "GPUMemoryVoltageLimited": "Memory Voltage Limited",
        "GPUMemoryUtilizationLimited": "Memory Utilization Limited",
    }

    result = {}
    any_throttling = False

    for col, label in throttle_cols.items():
        if col in df.columns:
            vals = df[col].dropna()
            if len(vals) > 0:
                throttled_count = int((vals == 1).sum())
                total = int(len(vals))
                pct = round(float(throttled_count / total * 100), 1) if total > 0 else 0.0
                result[label] = {
                    "throttled_frames": throttled_count,
                    "total_frames": total,
                    "percentage": pct,
                }
                if throttled_count > 0:
                    any_throttling = True

    result["any_throttling_detected"] = any_throttling
    return result


def get_time_segment_stats(
    session_id: str, file_id: str, segment_seconds: float = 10.0
) -> dict:
    """Break capture into time segments and compute per-segment stats."""
    df = get_dataframe(session_id, file_id)

    if "CPUStartTime" not in df.columns or "FrameTime" not in df.columns:
        return {"error": "Missing CPUStartTime or FrameTime columns"}

    start = float(df["CPUStartTime"].iloc[0])
    end = float(df["CPUStartTime"].iloc[-1])
    segments = []

    current = start
    while current < end:
        seg_end = current + segment_seconds
        mask = (df["CPUStartTime"] >= current) & (df["CPUStartTime"] < seg_end)
        seg_df = df[mask]

        if len(seg_df) > 0:
            ft = seg_df["FrameTime"].dropna()
            if len(ft) > 0:
                fps = 1000.0 / ft.values
                segments.append({
                    "start_sec": round(current, 1),
                    "end_sec": round(seg_end, 1),
                    "frame_count": int(len(ft)),
                    "avg_fps": round(float(np.mean(fps)), 1),
                    "min_fps": round(float(np.min(fps)), 1),
                    "avg_frametime_ms": round(float(ft.mean()), 2),
                    "max_frametime_ms": round(float(ft.max()), 2),
                })

        current = seg_end

    return {
        "segment_seconds": segment_seconds,
        "segment_count": len(segments),
        "segments": segments,
    }
