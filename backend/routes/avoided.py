"""What I Avoided endpoints."""

from fastapi import APIRouter, Query
from database import get_db

router = APIRouter(tags=["avoided"])


@router.get("/avoided")
async def list_avoided(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get tokens the agent flagged as dangerous."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM avoided ORDER BY flagged_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


@router.get("/avoided/stats")
async def avoided_stats():
    """Get aggregate avoided statistics."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as total FROM avoided")
        total = (await cursor.fetchone())["total"]

        cursor = await db.execute(
            "SELECT COUNT(*) as confirmed FROM avoided WHERE confirmed_rug = 1"
        )
        confirmed = (await cursor.fetchone())["confirmed"]

        cursor = await db.execute(
            "SELECT COALESCE(SUM(estimated_savings_bnb), 0) as savings FROM avoided WHERE confirmed_rug = 1"
        )
        savings = (await cursor.fetchone())["savings"]

        return {
            "total_flagged": total,
            "confirmed_rugs": confirmed,
            "estimated_savings_bnb": round(savings, 4),
        }
    finally:
        await db.close()
