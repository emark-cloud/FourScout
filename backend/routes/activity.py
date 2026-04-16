"""Activity feed and override stats endpoints."""

from fastapi import APIRouter, Query
from database import get_db

router = APIRouter(tags=["activity"])


@router.get("/activity")
async def list_activity(
    event_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get chronological activity feed."""
    db = await get_db()
    try:
        query = "SELECT * FROM activity"
        params = []

        if event_type:
            query += " WHERE event_type = ?"
            params.append(event_type)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


@router.get("/overrides/stats")
async def override_stats():
    """Get behavioral nudge stats — how often the user overrode the agent."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) as total FROM overrides")
        total = (await cursor.fetchone())["total"]

        # User approved despite agent saying skip (red/amber)
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM overrides WHERE user_action = 'approved'"
        )
        approved_risky = (await cursor.fetchone())["cnt"]

        # User rejected agent's green buy recommendation
        cursor = await db.execute(
            "SELECT COUNT(*) as cnt FROM overrides WHERE user_action = 'rejected'"
        )
        rejected_safe = (await cursor.fetchone())["cnt"]

        # How many overridden approvals turned out bad (token rugged or large loss)
        cursor = await db.execute(
            """SELECT COUNT(*) as cnt FROM overrides o
               JOIN avoided a ON o.token_address = a.token_address
               WHERE o.user_action = 'approved' AND a.confirmed_rug = 1"""
        )
        overrides_rugged = (await cursor.fetchone())["cnt"]

        return {
            "total_overrides": total,
            "approved_risky": approved_risky,
            "rejected_safe": rejected_safe,
            "overrides_rugged": overrides_rugged,
        }
    finally:
        await db.close()
