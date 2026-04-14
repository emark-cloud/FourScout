"""Position tracking endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Query
from database import get_db

router = APIRouter(tags=["positions"])


@router.get("/positions")
async def list_positions(
    status: str | None = Query("active", description="Filter: active/closed/all"),
    limit: int = Query(50, ge=1, le=200),
):
    """Get positions with PnL."""
    db = await get_db()
    try:
        if status == "all":
            cursor = await db.execute(
                "SELECT * FROM positions ORDER BY opened_at DESC LIMIT ?", (limit,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM positions WHERE status = ? ORDER BY opened_at DESC LIMIT ?",
                (status, limit),
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


@router.get("/trades/daily")
async def daily_trade_stats():
    """Get today's trade count and total BNB spent."""
    db = await get_db()
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        cursor = await db.execute(
            "SELECT COALESCE(SUM(amount_bnb), 0) as spent, COUNT(*) as count FROM trades WHERE executed_at >= ?",
            (today,),
        )
        row = await cursor.fetchone()
        return {
            "spent_today_bnb": round(row["spent"], 6),
            "trades_today": row["count"],
        }
    finally:
        await db.close()
