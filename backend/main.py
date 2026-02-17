from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mode = "mock-only" if settings.use_mock else "hybrid (mock + claude)"
    print(f"Starting PresentMon Analyzer API (mode={mode}, model={settings.model_name})")
    print(f"  API key set: {'yes' if settings.anthropic_api_key else 'NO'}")
    if not settings.use_mock:
        print(f"  PresentMon queries → mock (fast, free)")
        print(f"  Other queries → Claude API")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="PresentMon Analyzer API",
    description="AI-powered GPU/CPU performance log analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
from backend.api.routes_health import router as health_router
from backend.api.routes_upload import router as upload_router
from backend.api.routes_sessions import router as sessions_router

from backend.api.routes_chat import router as chat_router

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(sessions_router)
app.include_router(chat_router)
