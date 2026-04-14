"""Watchlist CRUD endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db

router = APIRouter(tags=["watchlist"])


class WatchlistItem(BaseModel):
    item_type: str  # token / creator / pattern
    value: str
    label: str = ""


@router.get("/watchlist")
async def list_watchlist():
    """Get all watchlist items."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM watchlist ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


@router.post("/watchlist")
async def add_watchlist_item(item: WatchlistItem):
    """Add an item to the watchlist."""
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()
        cursor = await db.execute(
            "INSERT INTO watchlist (item_type, value, label, created_at) VALUES (?, ?, ?, ?)",
            (item.item_type, item.value, item.label, now),
        )
        await db.commit()
        return {"status": "ok", "id": cursor.lastrowid}
    finally:
        await db.close()


@router.delete("/watchlist/{item_id}")
async def remove_watchlist_item(item_id: int):
    """Remove an item from the watchlist."""
    db = await get_db()
    try:
        await db.execute("DELETE FROM watchlist WHERE id = ?", (item_id,))
        await db.commit()
        return {"status": "ok"}
    finally:
        await db.close()
