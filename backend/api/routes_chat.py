from __future__ import annotations

import json
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.agents.orchestrator import Orchestrator
from backend.core.config import settings
from backend.core.session_store import session_store

router = APIRouter()

# Create orchestrator (shared across connections)
orchestrator = Orchestrator()


def _get_client():
    """Get the appropriate LLM client based on config.

    - use_mock=true  → pure mock (no API key needed)
    - use_mock=false → hybrid: mock for PresentMon queries, Claude for the rest
    """
    if settings.use_mock:
        from backend.core.mock_client import MockClient
        return MockClient()
    else:
        from backend.core.hybrid_client import HybridClient
        return HybridClient(
            api_key=settings.anthropic_api_key,
            model=settings.model_name,
            max_tokens=settings.max_tokens,
        )


def _build_context_message(session_id: str) -> str:
    """Build a context message telling the agent what files are available."""
    session = session_store.get_session(session_id)
    if session is None or not session.has_files:
        return "No files have been uploaded to this session yet."

    lines = ["Available files in this session:"]
    for f in session.files.values():
        lines.append(
            f"- file_id: \"{f.file_id}\" | {f.original_name} | "
            f"{f.application} | {f.row_count:,} rows | {f.duration_seconds}s | "
            f"Source: {f.source_tool}"
        )
    return "\n".join(lines)


@router.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Ensure session exists
    session = session_store.get_or_create_session(session_id)
    client = _get_client()

    try:
        while True:
            # Receive user message
            data = await websocket.receive_json()
            user_message = data.get("message", "").strip()

            if not user_message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            # Add to chat history
            session.chat_history.append({"role": "user", "content": user_message})

            try:
                # Route to appropriate agent
                agent = orchestrator.route(user_message)

                # Build messages with context
                context = _build_context_message(session_id)
                messages = [
                    {"role": "user", "content": f"[Session context]\n{context}"},
                    {"role": "assistant", "content": "Understood. I have access to the files listed above. How can I help you analyze the performance data?"},
                ]

                # Add recent chat history (last 20 messages for context)
                recent_history = session.chat_history[-20:]
                for msg in recent_history:
                    messages.append({"role": msg["role"], "content": msg["content"]})

                # Run agent loop, streaming results to frontend
                full_text = ""
                charts = []
                token_usage = None

                async for chunk in client.run_agent_loop(
                    agent=agent,
                    session_id=session_id,
                    messages=messages,
                ):
                    if chunk["type"] == "text":
                        full_text += chunk["content"]
                        await websocket.send_json({
                            "type": "text_delta",
                            "content": chunk["content"],
                        })
                    elif chunk["type"] == "chart":
                        charts.append(chunk["data"])
                    elif chunk["type"] == "tool_start":
                        await websocket.send_json({
                            "type": "tool_status",
                            "content": f"Using {chunk['tool_name']}...",
                        })
                    elif chunk["type"] == "tool_end":
                        # Don't send "complete" status — the "Using..." message
                        # stays until next tool_start or message_end clears it
                        pass
                    elif chunk["type"] == "token_usage":
                        token_usage = {
                            "input_tokens": chunk["input_tokens"],
                            "output_tokens": chunk["output_tokens"],
                            "model": chunk["model"],
                        }

                # Signal end of response (bundle charts + token_usage)
                end_msg: dict = {"type": "message_end"}
                if charts:
                    end_msg["charts"] = charts
                if token_usage:
                    end_msg["token_usage"] = token_usage
                await websocket.send_text(json.dumps(end_msg))

                # Save assistant response to history
                session.chat_history.append({
                    "role": "assistant",
                    "content": full_text,
                })

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                print(f"Chat error: {traceback.format_exc()}")
                await websocket.send_json({
                    "type": "text_delta",
                    "content": error_msg,
                })
                await websocket.send_json({"type": "message_end"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
