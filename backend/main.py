"""MemeGuard FastAPI backend — main entry point."""

import json
import asyncio
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

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

# Scanner task reference (set during startup)
scanner_task: asyncio.Task | None = None


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

    yield

    # Shutdown
    if scanner_task:
        scanner_task.cancel()
        try:
            await scanner_task
        except asyncio.CancelledError:
            pass
    print("Scanner stopped.")


app = FastAPI(
    title="MemeGuard API",
    description="AI trading agent for Four.meme",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
from routes.tokens import router as tokens_router
from routes.config_routes import router as config_router
from routes.activity import router as activity_router
from routes.positions import router as positions_router
from routes.actions import router as actions_router
from routes.avoided import router as avoided_router
from routes.watchlist import router as watchlist_router

app.include_router(tokens_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(activity_router, prefix="/api")
app.include_router(positions_router, prefix="/api")
app.include_router(actions_router, prefix="/api")
app.include_router(avoided_router, prefix="/api")
app.include_router(watchlist_router, prefix="/api")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive any client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "scanner_running": scanner_task is not None and not scanner_task.done(),
    }
