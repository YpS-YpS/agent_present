from __future__ import annotations

import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from backend.tools.data_tools import get_dataframe, filter_by_time_range

# Dark theme constants
DARK_BG = "#09090b"
DARK_PAPER = "#09090b"
DARK_GRID = "#27272a"
DARK_TEXT = "#e4e4e7"
ACCENT = ["#3b82f6", "#ef4444", "#22c55e", "#f97316", "#8b5cf6", "#ec4899"]


def _base_layout(**kwargs) -> dict:
    """Base Plotly layout for dark theme."""
    layout = {
        "template": "plotly_dark",
        "paper_bgcolor": DARK_PAPER,
        "plot_bgcolor": DARK_BG,
        "font": {"color": DARK_TEXT, "family": "Inter, system-ui, sans-serif"},
        "margin": {"l": 60, "r": 20, "t": 50, "b": 50},
        "height": 400,
        "xaxis": {"gridcolor": DARK_GRID, "zeroline": False},
        "yaxis": {"gridcolor": DARK_GRID, "zeroline": False},
        "legend": {"bgcolor": "rgba(0,0,0,0)"},
    }
    layout.update(kwargs)
    return layout


def _downsample(series: pd.Series, max_points: int = 2000) -> pd.Series:
    """Downsample a series for chart rendering using every-Nth-point."""
    if len(series) <= max_points:
        return series
    step = max(1, len(series) // max_points)
    return series.iloc[::step]


def chart_frametime_timeline(
    session_id: str,
    file_id: str,
    downsample: int = 2000,
    show_rolling_avg: bool = True,
    highlight_stutters: bool = True,
) -> dict:
    """Generate a frame time over time line chart."""
    df = get_dataframe(session_id, file_id)

    if "CPUStartTime" not in df.columns or "FrameTime" not in df.columns:
        return {"type": "error", "message": "Missing CPUStartTime or FrameTime columns"}

    # Downsample
    if len(df) > downsample:
        step = max(1, len(df) // downsample)
        df_plot = df.iloc[::step].copy()
    else:
        df_plot = df.copy()

    fig = go.Figure()

    # Main frame time trace
    fig.add_trace(go.Scattergl(
        x=df_plot["CPUStartTime"],
        y=df_plot["FrameTime"],
        mode="lines",
        name="Frame Time",
        line=dict(color=ACCENT[0], width=1),
        hovertemplate="Time: %{x:.1f}s<br>Frame Time: %{y:.2f}ms<extra></extra>",
    ))

    if show_rolling_avg:
        rolling = df_plot["FrameTime"].rolling(window=30, min_periods=1).mean()
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=rolling,
            mode="lines",
            name="Rolling Avg (30)",
            line=dict(color=ACCENT[3], width=2, dash="dot"),
        ))

    if highlight_stutters:
        ft = df_plot["FrameTime"].values
        rolling_avg = pd.Series(ft).rolling(window=60, min_periods=1).mean().values
        stutter_mask = ft > (rolling_avg * 2.0)
        if stutter_mask.any():
            stutter_df = df_plot[stutter_mask]
            fig.add_trace(go.Scattergl(
                x=stutter_df["CPUStartTime"],
                y=stutter_df["FrameTime"],
                mode="markers",
                name="Stutters (>2x avg)",
                marker=dict(color=ACCENT[1], size=6, symbol="circle"),
            ))

    fig.update_layout(**_base_layout(
        title="Frame Time Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Frame Time (ms)",
    ))

    return {"type": "chart", "plotly_json": json.loads(fig.to_json())}


def chart_fps_histogram(
    session_id: str,
    file_id: str,
    bins: int = 50,
) -> dict:
    """Generate FPS distribution histogram with percentile markers."""
    df = get_dataframe(session_id, file_id)

    if "FrameTime" not in df.columns:
        return {"type": "error", "message": "Missing FrameTime column"}

    ft = df["FrameTime"].dropna().values
    fps = 1000.0 / ft

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=fps,
        nbinsx=bins,
        name="FPS Distribution",
        marker_color=ACCENT[0],
        opacity=0.8,
    ))

    # Add percentile lines
    percentiles = {
        "1% Low": np.percentile(fps, 1),
        "Average": np.mean(fps),
        "Median": np.median(fps),
    }
    colors = [ACCENT[1], ACCENT[2], ACCENT[3]]
    for (label, val), color in zip(percentiles.items(), colors):
        fig.add_vline(
            x=val,
            line_dash="dash",
            line_color=color,
            annotation_text=f"{label}: {val:.0f}",
            annotation_position="top",
            annotation_font_color=color,
        )

    fig.update_layout(**_base_layout(
        title="FPS Distribution",
        xaxis_title="FPS",
        yaxis_title="Frame Count",
    ))

    return {"type": "chart", "plotly_json": json.loads(fig.to_json())}


def chart_utilization_timeline(
    session_id: str,
    file_id: str,
    downsample: int = 2000,
) -> dict:
    """Generate GPU and CPU utilization over time."""
    df = get_dataframe(session_id, file_id)

    if "CPUStartTime" not in df.columns:
        return {"type": "error", "message": "Missing CPUStartTime column"}

    # Downsample
    if len(df) > downsample:
        step = max(1, len(df) // downsample)
        df_plot = df.iloc[::step].copy()
    else:
        df_plot = df.copy()

    fig = go.Figure()
    traces_added = False

    if "GPUUtilization" in df_plot.columns and not df_plot["GPUUtilization"].isna().all():
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["GPUUtilization"],
            mode="lines",
            name="GPU Utilization",
            line=dict(color=ACCENT[0], width=1),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.15)",
        ))
        traces_added = True

    if "CPUUtilization" in df_plot.columns and not df_plot["CPUUtilization"].isna().all():
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["CPUUtilization"],
            mode="lines",
            name="CPU Utilization",
            line=dict(color=ACCENT[2], width=1),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.15)",
        ))
        traces_added = True

    if "3D/ComputeUtilization" in df_plot.columns and not df_plot["3D/ComputeUtilization"].isna().all():
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["3D/ComputeUtilization"],
            mode="lines",
            name="3D/Compute Utilization",
            line=dict(color=ACCENT[4], width=1, dash="dot"),
        ))
        traces_added = True

    if not traces_added:
        return {"type": "error", "message": "No utilization data available"}

    fig.update_layout(**_base_layout(
        title="GPU & CPU Utilization Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Utilization (%)",
        yaxis_range=[0, 105],
    ))

    return {"type": "chart", "plotly_json": json.loads(fig.to_json())}


def chart_gpu_power_thermal(
    session_id: str,
    file_id: str,
    downsample: int = 2000,
) -> dict:
    """Generate GPU power, temperature, and frequency timeline."""
    df = get_dataframe(session_id, file_id)

    if "CPUStartTime" not in df.columns:
        return {"type": "error", "message": "Missing CPUStartTime column"}

    if len(df) > downsample:
        step = max(1, len(df) // downsample)
        df_plot = df.iloc[::step].copy()
    else:
        df_plot = df.copy()

    fig = go.Figure()
    traces_added = False

    if "GPUPower" in df_plot.columns and not df_plot["GPUPower"].isna().all():
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["GPUPower"],
            mode="lines",
            name="GPU Power (W)",
            line=dict(color=ACCENT[3], width=1),
            yaxis="y",
        ))
        traces_added = True

    if "GPUTemperature" in df_plot.columns and not df_plot["GPUTemperature"].isna().all():
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["GPUTemperature"],
            mode="lines",
            name="GPU Temp (°C)",
            line=dict(color=ACCENT[1], width=1),
            yaxis="y2",
        ))
        traces_added = True

    if not traces_added:
        return {"type": "error", "message": "No GPU power or temperature data available"}

    layout = _base_layout(
        title="GPU Power & Temperature",
        xaxis_title="Time (seconds)",
        yaxis_title="Power (W)",
    )
    layout["yaxis2"] = {
        "title": "Temperature (°C)",
        "overlaying": "y",
        "side": "right",
        "gridcolor": DARK_GRID,
    }

    fig.update_layout(**layout)

    return {"type": "chart", "plotly_json": json.loads(fig.to_json())}


def chart_cpu_gpu_busy_timeline(
    session_id: str,
    file_id: str,
    downsample: int = 2000,
    show_frame_time: bool = True,
) -> dict:
    """Generate CPU Busy vs GPU Busy timeline to visualize per-frame bottleneck."""
    df = get_dataframe(session_id, file_id)

    if "CPUStartTime" not in df.columns:
        return {"type": "error", "message": "Missing CPUStartTime column"}

    has_cpu = "CPUBusy" in df.columns and not df["CPUBusy"].isna().all()
    has_gpu = "GPUBusy" in df.columns and not df["GPUBusy"].isna().all()

    if not has_cpu and not has_gpu:
        return {"type": "error", "message": "No CPUBusy or GPUBusy data available"}

    # Downsample
    if len(df) > downsample:
        step = max(1, len(df) // downsample)
        df_plot = df.iloc[::step].copy()
    else:
        df_plot = df.copy()

    fig = go.Figure()

    if has_cpu:
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["CPUBusy"],
            mode="lines",
            name="CPU Busy",
            line=dict(color=ACCENT[2], width=1.2),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.1)",
            hovertemplate="Time: %{x:.1f}s<br>CPU Busy: %{y:.2f}ms<extra></extra>",
        ))

    if has_gpu:
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["GPUBusy"],
            mode="lines",
            name="GPU Busy",
            line=dict(color=ACCENT[0], width=1.2),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.1)",
            hovertemplate="Time: %{x:.1f}s<br>GPU Busy: %{y:.2f}ms<extra></extra>",
        ))

    # Optionally overlay FrameTime as reference
    if show_frame_time and "FrameTime" in df_plot.columns:
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["FrameTime"],
            mode="lines",
            name="Frame Time",
            line=dict(color=ACCENT[3], width=1, dash="dot"),
            opacity=0.6,
            hovertemplate="Time: %{x:.1f}s<br>Frame Time: %{y:.2f}ms<extra></extra>",
        ))

    # Add CPU Wait / GPU Wait if available
    if "CPUWait" in df_plot.columns and not df_plot["CPUWait"].isna().all():
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["CPUWait"],
            mode="lines",
            name="CPU Wait",
            line=dict(color=ACCENT[2], width=1, dash="dash"),
            opacity=0.5,
        ))

    if "GPUWait" in df_plot.columns and not df_plot["GPUWait"].isna().all():
        fig.add_trace(go.Scattergl(
            x=df_plot["CPUStartTime"],
            y=df_plot["GPUWait"],
            mode="lines",
            name="GPU Wait",
            line=dict(color=ACCENT[0], width=1, dash="dash"),
            opacity=0.5,
        ))

    fig.update_layout(**_base_layout(
        title="CPU Busy vs GPU Busy Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Time (ms)",
    ))

    return {"type": "chart", "plotly_json": json.loads(fig.to_json())}


def chart_comparison_bars(
    stats_list: list[dict],
    labels: list[str],
    metrics: list[str] | None = None,
) -> dict:
    """Generate side-by-side comparison bar chart for multiple files."""
    if metrics is None:
        metrics = ["avg_fps", "p1_fps", "avg_frametime_ms", "p99_frametime_ms"]

    fig = go.Figure()

    for i, (stats, label) in enumerate(zip(stats_list, labels)):
        values = []
        metric_names = []
        for m in metrics:
            val = stats.get(m, 0)
            if val is not None:
                values.append(float(val))
                metric_names.append(m.replace("_", " ").title())

        fig.add_trace(go.Bar(
            name=label,
            x=metric_names,
            y=values,
            marker_color=ACCENT[i % len(ACCENT)],
        ))

    fig.update_layout(**_base_layout(
        title="Performance Comparison",
        barmode="group",
    ))

    return {"type": "chart", "plotly_json": json.loads(fig.to_json())}
