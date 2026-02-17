from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File

from backend.core.config import settings
from backend.core.session_store import session_store, FileInfo
from backend.models.schemas import UploadResponse
from backend.parsers.registry import detect_parser

router = APIRouter()


@router.post("/api/upload/{session_id}", response_model=UploadResponse)
async def upload_file(session_id: str, file: UploadFile = File(...)):
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported. Upload a .csv file.")

    # Read content
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(413, f"File exceeds {settings.max_file_size_mb}MB limit (got {size_mb:.1f}MB)")

    # Auto-detect parser
    parser = detect_parser(content)
    if parser is None:
        raise HTTPException(
            400,
            "Unrecognized file format. Supported formats: PresentMon CSV. "
            "Ensure the CSV has the expected column headers.",
        )

    # Parse the CSV
    try:
        df = parser.parse(content)
    except Exception as e:
        raise HTTPException(400, f"Failed to parse CSV: {e}")

    # Validate row count
    if len(df) > settings.max_rows_per_file:
        raise HTTPException(
            413,
            f"File has {len(df):,} rows, exceeding the {settings.max_rows_per_file:,} row limit.",
        )

    if len(df) == 0:
        raise HTTPException(400, "CSV file is empty (no data rows).")

    # Profile the data
    file_id = uuid.uuid4().hex[:8]
    na_columns = [col for col in df.columns if df[col].isna().all()]
    available_columns = [col for col in df.columns if not df[col].isna().all()]

    # Extract application name
    application = "Unknown"
    if "Application" in df.columns:
        application = str(df["Application"].iloc[0])

    # Compute duration
    duration_seconds = 0.0
    if "CPUStartTime" in df.columns and len(df) > 1:
        duration_seconds = float(df["CPUStartTime"].iloc[-1] - df["CPUStartTime"].iloc[0])

    # Build metadata
    metadata = {}
    if "PresentMode" in df.columns:
        metadata["present_modes"] = df["PresentMode"].value_counts().to_dict()
    if "FrameType" in df.columns:
        metadata["frame_types"] = df["FrameType"].value_counts().to_dict()

    # Build profile summary
    profile = {**metadata}
    if "FrameTime" in df.columns:
        ft = df["FrameTime"].dropna()
        if len(ft) > 0:
            profile["avg_fps"] = round(float(1000.0 / ft.mean()), 1)
            profile["avg_frametime_ms"] = round(float(ft.mean()), 2)

    file_info = FileInfo(
        file_id=file_id,
        original_name=file.filename,
        source_tool=parser.get_source_name(),
        application=application,
        row_count=len(df),
        duration_seconds=round(duration_seconds, 2),
        available_columns=available_columns,
        na_columns=na_columns,
        metadata=metadata,
    )

    session_store.add_file(session_id, file_id, df, file_info)

    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        source_tool=parser.get_source_name(),
        application=application,
        rows=len(df),
        duration_seconds=round(duration_seconds, 2),
        columns_available=len(available_columns),
        columns_na=len(na_columns),
        profile=profile,
    )
