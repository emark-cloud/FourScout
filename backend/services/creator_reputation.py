"""Creator reputation cache + outcome feedback.

Problem it solves:
- `score_creator_history` scans ~50k blocks per call. Same creator scanned
  5 times in an hour means 5 identical expensive chain queries.
- The raw signal only counts launches; it doesn't know how those launches
  turned out. A creator with 3 prior rugs ought to score lower than a
  creator with 3 prior profitable closes.

This module writes a row per creator, updated on:
  - scan time: set/refresh launch_count from chain (TTL-gated)
  - position close: bump profitable_closes / losing_closes
  - avoided 24h confirm: bump confirmed_rugs

The risk engine reads from the cache when fresh, otherwise recomputes.
"""

from datetime import datetime, timedelta, timezone

from database import get_db


# Refresh launch_count from chain every hour. Launches are a slow-moving
# signal; a fresher cache isn't worth the RPC cost.
CACHE_TTL_MINUTES = 60


async def get_cached(creator_address: str) -> dict | None:
    """Return the cached row, or None if it doesn't exist."""
    if not creator_address:
        return None
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM creator_reputation WHERE creator_address = ?",
            (creator_address,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


def is_fresh(row: dict | None, now: datetime | None = None) -> bool:
    """True when the cached row was refreshed within CACHE_TTL_MINUTES."""
    if not row or not row.get("last_updated"):
        return False
    try:
        last = datetime.fromisoformat(str(row["last_updated"]).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return False
    now = now or datetime.now(timezone.utc)
    return (now - last) < timedelta(minutes=CACHE_TTL_MINUTES)


async def upsert_launch_count(creator_address: str, launch_count: int) -> None:
    """Write a fresh launch_count + timestamp, preserving outcome counters."""
    if not creator_address:
        return
    now = datetime.now(timezone.utc).isoformat()
    db = await get_db()
    try:
        # Upsert: keep existing outcome counters, update launch_count + ts.
        await db.execute(
            """INSERT INTO creator_reputation (creator_address, launch_count, last_updated)
               VALUES (?, ?, ?)
               ON CONFLICT(creator_address) DO UPDATE SET
                   launch_count = excluded.launch_count,
                   last_updated = excluded.last_updated""",
            (creator_address, launch_count, now),
        )
        await db.commit()
    finally:
        await db.close()


async def record_close(creator_address: str, pnl_bnb: float | None) -> None:
    """Increment profitable_closes or losing_closes when a position closes."""
    if not creator_address or pnl_bnb is None:
        return
    column = "profitable_closes" if pnl_bnb > 0 else "losing_closes"
    now = datetime.now(timezone.utc).isoformat()
    db = await get_db()
    try:
        # INSERT-first ensures we have a row even for creators we haven't
        # scanned via the signal path yet (rare, but can happen if the
        # close hits before a rescan of an already-flagged creator).
        await db.execute(
            """INSERT INTO creator_reputation (creator_address, last_updated)
               VALUES (?, ?)
               ON CONFLICT(creator_address) DO NOTHING""",
            (creator_address, now),
        )
        await db.execute(
            f"UPDATE creator_reputation SET {column} = COALESCE({column}, 0) + 1 WHERE creator_address = ?",
            (creator_address,),
        )
        await db.commit()
    finally:
        await db.close()


async def record_rug(creator_address: str) -> None:
    """Increment confirmed_rugs when the avoided tracker confirms a rug."""
    if not creator_address:
        return
    now = datetime.now(timezone.utc).isoformat()
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO creator_reputation (creator_address, last_updated)
               VALUES (?, ?)
               ON CONFLICT(creator_address) DO NOTHING""",
            (creator_address, now),
        )
        await db.execute(
            "UPDATE creator_reputation SET confirmed_rugs = COALESCE(confirmed_rugs, 0) + 1 WHERE creator_address = ?",
            (creator_address,),
        )
        await db.commit()
    finally:
        await db.close()
