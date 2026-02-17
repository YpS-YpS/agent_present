from __future__ import annotations

import pandas as pd
import numpy as np

from backend.core.session_store import session_store


def get_dataframe(session_id: str, file_id: str) -> pd.DataFrame:
    """Retrieve a DataFrame from the session store. Raises ValueError if not found."""
    df = session_store.get_dataframe(session_id, file_id)
    if df is None:
        raise ValueError(f"File '{file_id}' not found in session '{session_id}'")
    return df


def profile_data(session_id: str, file_id: str) -> dict:
    """Generate a comprehensive profile of the uploaded file."""
    df = get_dataframe(session_id, file_id)
    info = session_store.get_file_info(session_id, file_id)

    na_cols = [col for col in df.columns if df[col].isna().all()]
    available_cols = [col for col in df.columns if not df[col].isna().all()]

    profile = {
        "file_id": file_id,
        "filename": info.original_name if info else "unknown",
        "source_tool": info.source_tool if info else "unknown",
        "application": info.application if info else "unknown",
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "available_columns": len(available_cols),
        "na_columns": len(na_cols),
        "na_column_names": na_cols,
        "available_column_names": available_cols,
    }

    if "CPUStartTime" in df.columns and len(df) > 1:
        profile["duration_seconds"] = round(float(df["CPUStartTime"].iloc[-1] - df["CPUStartTime"].iloc[0]), 2)

    if "FrameTime" in df.columns:
        ft = df["FrameTime"].dropna()
        if len(ft) > 0:
            profile["avg_fps"] = round(float(1000.0 / ft.mean()), 1)
            profile["avg_frametime_ms"] = round(float(ft.mean()), 2)

    if "Application" in df.columns:
        profile["application"] = str(df["Application"].iloc[0])

    if "PresentMode" in df.columns:
        profile["present_modes"] = df["PresentMode"].value_counts().to_dict()

    return profile


def filter_by_time_range(
    df: pd.DataFrame, start_sec: float | None = None, end_sec: float | None = None
) -> pd.DataFrame:
    """Filter DataFrame by time range (CPUStartTime in seconds)."""
    if "CPUStartTime" not in df.columns:
        return df
    mask = pd.Series(True, index=df.index)
    if start_sec is not None:
        mask &= df["CPUStartTime"] >= start_sec
    if end_sec is not None:
        mask &= df["CPUStartTime"] <= end_sec
    return df[mask]


def get_column_stats(df: pd.DataFrame, column: str) -> dict | None:
    """Get basic statistics for a numeric column."""
    if column not in df.columns:
        return None
    series = df[column].dropna()
    if len(series) == 0:
        return None
    return {
        "count": int(len(series)),
        "mean": round(float(series.mean()), 4),
        "std": round(float(series.std()), 4),
        "min": round(float(series.min()), 4),
        "p25": round(float(np.percentile(series, 25)), 4),
        "median": round(float(series.median()), 4),
        "p75": round(float(np.percentile(series, 75)), 4),
        "p95": round(float(np.percentile(series, 95)), 4),
        "p99": round(float(np.percentile(series, 99)), 4),
        "max": round(float(series.max()), 4),
    }
