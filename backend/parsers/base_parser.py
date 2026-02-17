from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class LogParser(ABC):
    """Abstract base class for GPU profiling log parsers.

    To add a new format (e.g. OCAT, FrameView, MangoHud):
    1. Subclass LogParser
    2. Implement can_parse(), parse(), get_source_name(), get_column_mapping()
    3. Register the parser in parsers/registry.py
    """

    @abstractmethod
    def can_parse(self, header_columns: list[str]) -> bool:
        """Return True if this parser can handle a file with the given header columns."""
        ...

    @abstractmethod
    def parse(self, file_content: bytes) -> pd.DataFrame:
        """Parse raw file bytes into a pandas DataFrame.

        Should handle NA values, type conversions, and column cleanup.
        Returns a DataFrame with the original column names from the source tool.
        """
        ...

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of the profiling tool (e.g. 'PresentMon', 'OCAT')."""
        ...

    @abstractmethod
    def get_column_mapping(self) -> dict[str, str]:
        """Return a mapping from standard column names to source-specific column names.

        Standard names: frame_time_ms, timestamp_sec, cpu_busy_ms, gpu_busy_ms,
        gpu_utilization_pct, cpu_utilization_pct, display_latency_ms, gpu_power_w,
        gpu_temp_c, gpu_freq_mhz, cpu_freq_mhz, gpu_mem_used_bytes, gpu_mem_total_bytes
        """
        ...

    def get_available_standard_columns(self, df: pd.DataFrame) -> list[str]:
        """Return which standard column names are available (non-NA) in this DataFrame."""
        mapping = self.get_column_mapping()
        available = []
        for std_name, source_name in mapping.items():
            if source_name in df.columns and not df[source_name].isna().all():
                available.append(std_name)
        return available

    def to_standard_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a copy of the DataFrame with standard column names added.

        Keeps original columns and adds standard-named aliases for columns that exist.
        """
        mapping = self.get_column_mapping()
        result = df.copy()
        for std_name, source_name in mapping.items():
            if source_name in result.columns:
                result[std_name] = result[source_name]
        return result
