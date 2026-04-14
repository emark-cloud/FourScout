"""Activity feed endpoints."""

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
