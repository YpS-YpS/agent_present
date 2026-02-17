from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    source_tool: str
    application: str
    game_name: str
    rows: int
    duration_seconds: float
    columns_available: int
    columns_na: int
    profile: dict


class FileInfoResponse(BaseModel):
    file_id: str
    name: str
    source_tool: str
    application: str
    rows: int
    duration_seconds: float


class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    file_count: int
    files: list[FileInfoResponse]


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    charts: list[dict] | None = None
    timestamp: str | None = None


class HealthResponse(BaseModel):
    status: str
    mode: str  # "mock" or "claude"
    supported_formats: list[str]
