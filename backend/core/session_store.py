from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd


@dataclass
class FileInfo:
    file_id: str
    original_name: str
    source_tool: str  # e.g. "PresentMon", "OCAT"
    application: str  # e.g. "dota2.exe"
    row_count: int
    duration_seconds: float
    available_columns: list[str]  # columns with actual data
    na_columns: list[str]  # columns that are entirely NA
    upload_time: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)  # extra info (present modes, etc.)


@dataclass
class Session:
    session_id: str
    files: dict[str, FileInfo] = field(default_factory=dict)
    dataframes: dict[str, pd.DataFrame] = field(default_factory=dict)
    chat_history: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def has_files(self) -> bool:
        return len(self.files) > 0

    @property
    def file_ids(self) -> list[str]:
        return list(self.files.keys())

    def get_default_file_id(self) -> str | None:
        """Return the most recently uploaded file ID, or None."""
        if not self.files:
            return None
        return max(self.files.values(), key=lambda f: f.upload_time).file_id


class SessionStore:
    """In-memory session store. Replace with Redis for production."""

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create_session(self) -> Session:
        session_id = uuid.uuid4().hex[:12]
        session = Session(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def get_or_create_session(self, session_id: str) -> Session:
        session = self.get_session(session_id)
        if session is None:
            session = Session(session_id=session_id)
            self._sessions[session_id] = session
        return session

    def add_file(
        self,
        session_id: str,
        file_id: str,
        df: pd.DataFrame,
        info: FileInfo,
    ) -> None:
        session = self.get_or_create_session(session_id)
        session.files[file_id] = info
        session.dataframes[file_id] = df

    def get_dataframe(self, session_id: str, file_id: str) -> pd.DataFrame | None:
        session = self.get_session(session_id)
        if session is None:
            return None
        return session.dataframes.get(file_id)

    def get_file_info(self, session_id: str, file_id: str) -> FileInfo | None:
        session = self.get_session(session_id)
        if session is None:
            return None
        return session.files.get(file_id)

    def list_sessions(self) -> list[dict]:
        return [
            {
                "session_id": s.session_id,
                "created_at": s.created_at.isoformat(),
                "file_count": len(s.files),
                "files": [
                    {"file_id": f.file_id, "name": f.original_name, "application": f.application}
                    for f in s.files.values()
                ],
            }
            for s in self._sessions.values()
        ]

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_expired(self, max_age_hours: int = 24) -> int:
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired = [sid for sid, s in self._sessions.items() if s.created_at < cutoff]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


# Global instance
session_store = SessionStore()
