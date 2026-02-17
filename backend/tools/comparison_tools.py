from __future__ import annotations

import numpy as np

from backend.tools.data_tools import get_dataframe
from backend.tools.analysis_tools import compute_fps_statistics


def compare_files(
    session_id: str, file_ids: list[str], labels: list[str] | None = None
) -> dict:
    """Compare FPS/frame time statistics across multiple files."""
    if len(file_ids) < 2:
        return {"error": "Need at least 2 files to compare"}

    results = []
    for i, fid in enumerate(file_ids):
        stats = compute_fps_statistics(session_id, fid)
        if "error" in stats:
            return {"error": f"Failed to analyze file {fid}: {stats['error']}"}

        label = labels[i] if labels and i < len(labels) else fid
        results.append({
            "file_id": fid,
            "label": label,
            **stats,
        })

    # Compute deltas between first and second file
    if len(results) >= 2:
        a = results[0]
        b = results[1]
        delta = {
            "avg_fps_delta": round(b["fps"]["average"] - a["fps"]["average"], 1),
            "avg_fps_delta_pct": round(
                (b["fps"]["average"] - a["fps"]["average"]) / a["fps"]["average"] * 100, 1
            ) if a["fps"]["average"] != 0 else 0,
            "p1_fps_delta": round(b["fps"]["p1"] - a["fps"]["p1"], 1),
            "avg_frametime_delta_ms": round(
                b["frametime_ms"]["average"] - a["frametime_ms"]["average"], 2
            ),
        }
    else:
        delta = {}

    return {
        "file_count": len(results),
        "files": results,
        "delta": delta,
    }
