from __future__ import annotations

import io

import pandas as pd

from .base_parser import LogParser


# Columns that identify a PresentMon CSV
_PRESENTMON_SIGNATURE_COLS = {"Application", "ProcessID", "SwapChainAddress", "PresentRuntime", "FrameTime"}


class PresentMonParser(LogParser):
    """Parser for PresentMon CSV log files."""

    def can_parse(self, header_columns: list[str]) -> bool:
        return _PRESENTMON_SIGNATURE_COLS.issubset(set(header_columns))

    def parse(self, file_content: bytes) -> pd.DataFrame:
        df = pd.read_csv(io.BytesIO(file_content), na_values=["NA", ""])

        # Ensure numeric columns are float where expected
        numeric_candidates = [
            "CPUStartTime", "FrameTime", "CPUBusy", "CPUWait",
            "GPULatency", "GPUTime", "GPUBusy", "GPUWait",
            "DisplayLatency", "DisplayedTime", "AnimationError", "AnimationTime",
            "AllInputToPhotonLatency", "ClickToPhotonLatency", "InstrumentedLatency",
            "GPUPower", "GPUVoltage", "GPUFrequency", "GPUTemperature",
            "GPUUtilization", "3D/ComputeUtilization", "MediaUtilization",
            "GPUMemoryPower", "GPUMemoryVoltage", "GPUMemoryFrequency",
            "GPUMemoryEffectiveFrequency", "GPUMemoryTemperature",
            "GPUMemorySize", "GPUMemorySizeUsed", "GPUMemoryMaxBandwidth",
            "GPUMemoryReadBandwidth", "GPUMemoryWriteBandwidth",
            "GPUFanSpeed[0]", "GPUFanSpeed[1]", "GPUFanSpeed[2]", "GPUFanSpeed[3]",
            "CPUUtilization", "CPUPower", "CPUTemperature", "CPUFrequency",
        ]
        for col in numeric_candidates:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def get_source_name(self) -> str:
        return "PresentMon"

    def get_column_mapping(self) -> dict[str, str]:
        return {
            "timestamp_sec": "CPUStartTime",
            "frame_time_ms": "FrameTime",
            "cpu_busy_ms": "CPUBusy",
            "cpu_wait_ms": "CPUWait",
            "gpu_busy_ms": "GPUBusy",
            "gpu_wait_ms": "GPUWait",
            "gpu_time_ms": "GPUTime",
            "gpu_latency_ms": "GPULatency",
            "display_latency_ms": "DisplayLatency",
            "displayed_time_ms": "DisplayedTime",
            "gpu_utilization_pct": "GPUUtilization",
            "gpu_compute_utilization_pct": "3D/ComputeUtilization",
            "cpu_utilization_pct": "CPUUtilization",
            "gpu_power_w": "GPUPower",
            "gpu_temp_c": "GPUTemperature",
            "gpu_freq_mhz": "GPUFrequency",
            "cpu_freq_mhz": "CPUFrequency",
            "gpu_mem_used_bytes": "GPUMemorySizeUsed",
            "gpu_mem_total_bytes": "GPUMemorySize",
        }
