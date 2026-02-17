from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.core.session_store import session_store

router = APIRouter()


@router.get("/api/sessions")
async def list_sessions():
    return session_store.list_sessions()


@router.post("/api/sessions")
async def create_session():
    session = session_store.create_session()
    return {"session_id": session.session_id}


@router.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    session = session_store.get_session(session_id)
    if session is None:
        raise HTTPException(404, "Session not found")
    return {
        "session_id": session.session_id,
        "created_at": session.created_at.isoformat(),
        "files": [
            {
                "file_id": f.file_id,
                "name": f.original_name,
                "source_tool": f.source_tool,
                "application": f.application,
                "rows": f.row_count,
                "duration_seconds": f.duration_seconds,
            }
            for f in session.files.values()
        ],
    }


@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_store.delete_session(session_id):
        return {"status": "deleted"}
    raise HTTPException(404, "Session not found")
