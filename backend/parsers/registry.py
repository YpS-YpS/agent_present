from __future__ import annotations

import io

from .base_parser import LogParser
from .presentmon_parser import PresentMonParser

# Register all parsers here. Order matters — first match wins.
_PARSERS: list[LogParser] = [
    PresentMonParser(),
]


def register_parser(parser: LogParser) -> None:
    """Register a new parser. It will be tried after existing parsers."""
    _PARSERS.append(parser)


def detect_parser(file_content: bytes) -> LogParser | None:
    """Auto-detect the correct parser for a file by inspecting its header.

    Returns the matching parser, or None if no parser can handle the file.
    """
    # Read just the first line to get column headers
    first_line = file_content.split(b"\n", 1)[0].decode("utf-8", errors="replace").strip()
    if not first_line:
        return None

    # Handle potential BOM
    if first_line.startswith("\ufeff"):
        first_line = first_line[1:]

    header_columns = [col.strip() for col in first_line.split(",")]

    for parser in _PARSERS:
        if parser.can_parse(header_columns):
            return parser

    return None


def get_registered_parsers() -> list[str]:
    """Return names of all registered parsers."""
    return [p.get_source_name() for p in _PARSERS]
