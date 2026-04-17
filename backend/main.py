"""FourScout FastAPI backend — main entry point."""

import json
import asyncio
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import init_db


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, event_type: str, data: dict):
        message = json.dumps({"type": event_type, "data": data})
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)
        self.active_connections -= disconnected


ws_manager = ConnectionManager()

# Background task references (set during startup)
scanner_task: asyncio.Task | None = None
position_tracker_task: asyncio.Task | None = None
avoided_tracker_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("Database initialized.")

    # Start scanner in background
    from services.scanner import start_scanner
    global scanner_task
    scanner_task = asyncio.create_task(start_scanner(ws_manager))
    print(f"Scanner started (interval: {settings.scan_interval_seconds}s)")

    # Start position tracker in background
    from services.position_tracker import start_position_tracker
    global position_tracker_task
    position_tracker_task = asyncio.create_task(start_position_tracker(ws_manager))
    print("Position tracker started (interval: 60s)")

    # Start avoided tracker in background
    from services.avoided_tracker import start_avoided_tracker
    global avoided_tracker_task
    avoided_tracker_task = asyncio.create_task(start_avoided_tracker(ws_manager))
    print("Avoided tracker started (interval: 300s)")

    yield

    # Shutdown
    for task in [scanner_task, position_tracker_task, avoided_tracker_task]:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    print("Background tasks stopped.")


app = FastAPI(
    title="FourScout API",
    description="AI trading agent for Four.meme",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — reads ALLOWED_ORIGINS from .env (comma-separated).
# Defaults keep localhost dev working without config.
_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Shared-secret auth. If API_KEY is set, every /api/* request (except /api/health)
# must present a matching X-API-Key header. Empty key = auth disabled (local dev).
_AUTH_EXEMPT = {"/api/health"}


@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    if not settings.api_key:
        return await call_next(request)
    path = request.url.path
    if not path.startswith("/api/") or path in _AUTH_EXEMPT:
        return await call_next(request)
    if request.method == "OPTIONS":
        return await call_next(request)
    if request.headers.get("x-api-key") != settings.api_key:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)

# Register routes
from routes.tokens import router as tokens_router
from routes.config_routes import router as config_router
from routes.activity import router as activity_router
from routes.positions import router as positions_router
from routes.actions import router as actions_router
from routes.avoided import router as avoided_router
from routes.watchlist import router as watchlist_router
from routes.chat import router as chat_router
from routes.agent import router as agent_router

app.include_router(tokens_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(activity_router, prefix="/api")
app.include_router(positions_router, prefix="/api")
app.include_router(actions_router, prefix="/api")
app.include_router(avoided_router, prefix="/api")
app.include_router(watchlist_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(agent_router, prefix="/api")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Same shared secret as /api/*, passed as ?key=... (WebSocket can't send
    # custom headers from the browser). Empty api_key = auth disabled.
    if settings.api_key and websocket.query_params.get("key") != settings.api_key:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "scanner_running": scanner_task is not None and not scanner_task.done(),
        "position_tracker_running": position_tracker_task is not None and not position_tracker_task.done(),
        "avoided_tracker_running": avoided_tracker_task is not None and not avoided_tracker_task.done(),
    }
