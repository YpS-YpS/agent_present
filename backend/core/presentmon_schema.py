from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ColumnGroup(Enum):
    METADATA = "metadata"
    CPU_TIMING = "cpu_timing"
    GPU_TIMING = "gpu_timing"
    LATENCY = "latency"
    GPU_POWER = "gpu_power"
    GPU_MEMORY = "gpu_memory"
    GPU_THROTTLING = "gpu_throttling"
    CPU_METRICS = "cpu_metrics"


@dataclass(frozen=True)
class ColumnDef:
    name: str
    group: ColumnGroup
    dtype: str  # "str", "float", "int"
    unit: str | None  # "ms", "W", "MHz", "C", "%", "bytes", etc.
    description: str


PRESENTMON_COLUMNS: dict[str, ColumnDef] = {
    # --- Metadata ---
    "Application": ColumnDef("Application", ColumnGroup.METADATA, "str", None, "Executable name of the profiled application"),
    "ProcessID": ColumnDef("ProcessID", ColumnGroup.METADATA, "int", None, "OS process ID"),
    "SwapChainAddress": ColumnDef("SwapChainAddress", ColumnGroup.METADATA, "str", None, "Memory address of the swap chain"),
    "PresentRuntime": ColumnDef("PresentRuntime", ColumnGroup.METADATA, "str", None, "Graphics runtime (DXGI, D3D9, etc.)"),
    "SyncInterval": ColumnDef("SyncInterval", ColumnGroup.METADATA, "int", None, "V-sync interval (0=off)"),
    "PresentFlags": ColumnDef("PresentFlags", ColumnGroup.METADATA, "int", None, "Present API flags"),
    "AllowsTearing": ColumnDef("AllowsTearing", ColumnGroup.METADATA, "int", None, "Whether tearing is allowed (1=yes)"),
    "PresentMode": ColumnDef("PresentMode", ColumnGroup.METADATA, "str", None, "Presentation mode (Hardware Flip, Composed, etc.)"),
    "FrameType": ColumnDef("FrameType", ColumnGroup.METADATA, "str", None, "Frame type (Application, Reprojected, etc.)"),

    # --- CPU Timing ---
    "CPUStartTime": ColumnDef("CPUStartTime", ColumnGroup.CPU_TIMING, "float", "s", "Timestamp of CPU frame start (seconds from capture start)"),
    "FrameTime": ColumnDef("FrameTime", ColumnGroup.CPU_TIMING, "float", "ms", "Total time between consecutive frame starts"),
    "CPUBusy": ColumnDef("CPUBusy", ColumnGroup.CPU_TIMING, "float", "ms", "Time CPU spent actively working on the frame"),
    "CPUWait": ColumnDef("CPUWait", ColumnGroup.CPU_TIMING, "float", "ms", "Time CPU spent waiting (for GPU, etc.)"),

    # --- GPU Timing ---
    "GPULatency": ColumnDef("GPULatency", ColumnGroup.GPU_TIMING, "float", "ms", "Latency from CPU submission to GPU start"),
    "GPUTime": ColumnDef("GPUTime", ColumnGroup.GPU_TIMING, "float", "ms", "Total GPU time for the frame"),
    "GPUBusy": ColumnDef("GPUBusy", ColumnGroup.GPU_TIMING, "float", "ms", "Time GPU spent actively rendering"),
    "GPUWait": ColumnDef("GPUWait", ColumnGroup.GPU_TIMING, "float", "ms", "Time GPU spent idle/waiting"),
    "DisplayLatency": ColumnDef("DisplayLatency", ColumnGroup.GPU_TIMING, "float", "ms", "End-to-end latency from CPU start to display"),
    "DisplayedTime": ColumnDef("DisplayedTime", ColumnGroup.GPU_TIMING, "float", "ms", "Time the frame was displayed on screen"),

    # --- Latency ---
    "AnimationError": ColumnDef("AnimationError", ColumnGroup.LATENCY, "float", "ms", "Animation timing error"),
    "AnimationTime": ColumnDef("AnimationTime", ColumnGroup.LATENCY, "float", "ms", "Cumulative animation time"),
    "AllInputToPhotonLatency": ColumnDef("AllInputToPhotonLatency", ColumnGroup.LATENCY, "float", "ms", "Input-to-display latency (all inputs)"),
    "ClickToPhotonLatency": ColumnDef("ClickToPhotonLatency", ColumnGroup.LATENCY, "float", "ms", "Mouse click to photon latency"),
    "InstrumentedLatency": ColumnDef("InstrumentedLatency", ColumnGroup.LATENCY, "float", "ms", "Total instrumented latency"),

    # --- GPU Power ---
    "GPUPower": ColumnDef("GPUPower", ColumnGroup.GPU_POWER, "float", "W", "GPU power draw"),
    "GPUVoltage": ColumnDef("GPUVoltage", ColumnGroup.GPU_POWER, "float", "V", "GPU voltage"),
    "GPUFrequency": ColumnDef("GPUFrequency", ColumnGroup.GPU_POWER, "float", "MHz", "GPU clock frequency"),
    "GPUTemperature": ColumnDef("GPUTemperature", ColumnGroup.GPU_POWER, "float", "C", "GPU temperature"),
    "GPUUtilization": ColumnDef("GPUUtilization", ColumnGroup.GPU_POWER, "float", "%", "Overall GPU utilization"),
    "3D/ComputeUtilization": ColumnDef("3D/ComputeUtilization", ColumnGroup.GPU_POWER, "float", "%", "3D/compute engine utilization"),
    "MediaUtilization": ColumnDef("MediaUtilization", ColumnGroup.GPU_POWER, "float", "%", "Media engine utilization"),

    # --- GPU Memory ---
    "GPUMemoryPower": ColumnDef("GPUMemoryPower", ColumnGroup.GPU_MEMORY, "float", "W", "GPU memory power draw"),
    "GPUMemoryVoltage": ColumnDef("GPUMemoryVoltage", ColumnGroup.GPU_MEMORY, "float", "V", "GPU memory voltage"),
    "GPUMemoryFrequency": ColumnDef("GPUMemoryFrequency", ColumnGroup.GPU_MEMORY, "float", "MHz", "GPU memory clock frequency"),
    "GPUMemoryEffectiveFrequency": ColumnDef("GPUMemoryEffectiveFrequency", ColumnGroup.GPU_MEMORY, "float", "MHz", "GPU memory effective frequency"),
    "GPUMemoryTemperature": ColumnDef("GPUMemoryTemperature", ColumnGroup.GPU_MEMORY, "float", "C", "GPU memory temperature"),
    "GPUMemorySize": ColumnDef("GPUMemorySize", ColumnGroup.GPU_MEMORY, "float", "bytes", "Total GPU memory"),
    "GPUMemorySizeUsed": ColumnDef("GPUMemorySizeUsed", ColumnGroup.GPU_MEMORY, "float", "bytes", "GPU memory in use"),
    "GPUMemoryMaxBandwidth": ColumnDef("GPUMemoryMaxBandwidth", ColumnGroup.GPU_MEMORY, "float", "bytes/s", "Maximum memory bandwidth"),
    "GPUMemoryReadBandwidth": ColumnDef("GPUMemoryReadBandwidth", ColumnGroup.GPU_MEMORY, "float", "bytes/s", "Memory read bandwidth"),
    "GPUMemoryWriteBandwidth": ColumnDef("GPUMemoryWriteBandwidth", ColumnGroup.GPU_MEMORY, "float", "bytes/s", "Memory write bandwidth"),

    # --- GPU Fan ---
    "GPUFanSpeed[0]": ColumnDef("GPUFanSpeed[0]", ColumnGroup.GPU_POWER, "float", "RPM", "GPU fan 0 speed"),
    "GPUFanSpeed[1]": ColumnDef("GPUFanSpeed[1]", ColumnGroup.GPU_POWER, "float", "RPM", "GPU fan 1 speed"),
    "GPUFanSpeed[2]": ColumnDef("GPUFanSpeed[2]", ColumnGroup.GPU_POWER, "float", "RPM", "GPU fan 2 speed"),
    "GPUFanSpeed[3]": ColumnDef("GPUFanSpeed[3]", ColumnGroup.GPU_POWER, "float", "RPM", "GPU fan 3 speed"),

    # --- GPU Throttling ---
    "GPUPowerLimited": ColumnDef("GPUPowerLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU is power-limited (1=yes)"),
    "GPUTemperatureLimited": ColumnDef("GPUTemperatureLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU is temperature-limited (1=yes)"),
    "GPUCurrentLimited": ColumnDef("GPUCurrentLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU is current-limited (1=yes)"),
    "GPUVoltageLimited": ColumnDef("GPUVoltageLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU is voltage-limited (1=yes)"),
    "GPUUtilizationLimited": ColumnDef("GPUUtilizationLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU is utilization-limited (1=yes)"),
    "GPUMemoryPowerLimited": ColumnDef("GPUMemoryPowerLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU memory is power-limited (1=yes)"),
    "GPUMemoryTemperatureLimited": ColumnDef("GPUMemoryTemperatureLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU memory is temperature-limited (1=yes)"),
    "GPUMemoryCurrentLimited": ColumnDef("GPUMemoryCurrentLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU memory is current-limited (1=yes)"),
    "GPUMemoryVoltageLimited": ColumnDef("GPUMemoryVoltageLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU memory is voltage-limited (1=yes)"),
    "GPUMemoryUtilizationLimited": ColumnDef("GPUMemoryUtilizationLimited", ColumnGroup.GPU_THROTTLING, "int", None, "GPU memory is utilization-limited (1=yes)"),

    # --- CPU Metrics ---
    "CPUUtilization": ColumnDef("CPUUtilization", ColumnGroup.CPU_METRICS, "float", "%", "CPU utilization percentage"),
    "CPUPower": ColumnDef("CPUPower", ColumnGroup.CPU_METRICS, "float", "W", "CPU power draw"),
    "CPUTemperature": ColumnDef("CPUTemperature", ColumnGroup.CPU_METRICS, "float", "C", "CPU temperature"),
    "CPUFrequency": ColumnDef("CPUFrequency", ColumnGroup.CPU_METRICS, "float", "MHz", "CPU clock frequency"),
}

# Required columns for a valid PresentMon log
REQUIRED_COLUMNS = {"Application", "FrameTime", "CPUStartTime"}

# Standard column names for cross-format compatibility
STANDARD_COLUMN_MAP = {
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
