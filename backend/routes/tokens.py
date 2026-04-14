"""Token endpoints."""

from fastapi import APIRouter, Query
from database import get_db

router = APIRouter(tags=["tokens"])


@router.get("/tokens")
async def list_tokens(
    risk_score: str | None = Query(None, description="Filter by risk score: green/amber/red"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List discovered tokens with risk scores."""
    db = await get_db()
    try:
        query = "SELECT * FROM tokens"
        params = []

        if risk_score:
            query += " WHERE risk_score = ?"
            params.append(risk_score)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


@router.get("/tokens/{address}")
async def get_token(address: str):
    """Get full token detail with risk breakdown."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM tokens WHERE address = ?", (address,))
        token = await cursor.fetchone()
        if not token:
            return {"error": "Token not found"}, 404

        token_dict = dict(token)

        # Get recent scans for this token
        cursor = await db.execute(
            "SELECT * FROM scans WHERE token_address = ? ORDER BY created_at DESC LIMIT 10",
            (address,),
        )
        scans = await cursor.fetchall()
        token_dict["scans"] = [dict(s) for s in scans]

        # Get pending action if any
        cursor = await db.execute(
            "SELECT * FROM pending_actions WHERE token_address = ? AND status = 'pending' ORDER BY created_at DESC LIMIT 1",
            (address,),
        )
        action = await cursor.fetchone()
        token_dict["pending_action"] = dict(action) if action else None

        return token_dict
    finally:
        await db.close()
