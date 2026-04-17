"""Override pattern aggregates used to nudge the user in proposal rationales.

The persona engine stays deterministic — these helpers only tell the user
what their *past* self did with tokens of similar shape. No decision is
changed based on override history.
"""

from datetime import datetime, timedelta, timezone

from database import get_db


# Loss threshold (fractional) that we treat as a "bad outcome" when
# reporting on approved RED/AMBER overrides. -20% matches the plan's
# "closed at a loss >20%" framing.
_LOSS_THRESHOLD_PCT = -20.0


async def get_recent_pattern(
    risk_grade: str,
    days: int = 7,
) -> dict:
    """Return override counts + loss rate for this risk grade over the window.

    Shape:
      {
        "risk_grade": "amber",
        "days": 7,
        "approved": int,                       # approvals of this grade
        "approved_losing": int,                # of those, how many closed at a >20% loss
        "rejected": int,                       # rejections of this grade
      }

    The join to `positions` is LEFT so approvals that didn't produce a
    trackable position (rejected by executor, still active, etc.) don't
    vanish from the count. Loss accounting ignores positions without a
    resolved pnl_pct, which is the only safe interpretation.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    grade = risk_grade.lower()

    db = await get_db()
    try:
        # Approvals: overrides row was created when user approved a RED/AMBER.
        # The corresponding pending_actions row carries the risk_score used
        # at proposal time — join on token + timing to recover the grade.
        cursor = await db.execute(
            """SELECT COUNT(*) AS cnt
               FROM overrides o
               JOIN pending_actions p
                 ON p.token_address = o.token_address
                AND p.status = 'approved'
               WHERE o.user_action = 'approved'
                 AND o.created_at >= ?
                 AND p.risk_score = ?""",
            (since, grade),
        )
        row = await cursor.fetchone()
        approved = int(row["cnt"]) if row else 0

        # Of those approvals, how many closed at >20% loss? The positions
        # table stores pnl_bnb + entry_amount_bnb; pnl_pct is derived.
        cursor = await db.execute(
            """SELECT COUNT(*) AS cnt
               FROM overrides o
               JOIN pending_actions p
                 ON p.token_address = o.token_address
                AND p.status = 'approved'
               JOIN positions pos
                 ON pos.token_address = o.token_address
                AND pos.status = 'closed'
               WHERE o.user_action = 'approved'
                 AND o.created_at >= ?
                 AND p.risk_score = ?
                 AND pos.pnl_bnb IS NOT NULL
                 AND pos.entry_amount_bnb > 0
                 AND (pos.pnl_bnb / pos.entry_amount_bnb) * 100 <= ?""",
            (since, grade, _LOSS_THRESHOLD_PCT),
        )
        row = await cursor.fetchone()
        approved_losing = int(row["cnt"]) if row else 0

        # Rejections of this grade — useful mainly for the "rejected GREEN"
        # miscalibration hint.
        cursor = await db.execute(
            """SELECT COUNT(*) AS cnt
               FROM overrides o
               JOIN pending_actions p
                 ON p.token_address = o.token_address
                AND p.status = 'rejected'
               WHERE o.user_action = 'rejected'
                 AND o.created_at >= ?
                 AND p.risk_score = ?""",
            (since, grade),
        )
        row = await cursor.fetchone()
        rejected = int(row["cnt"]) if row else 0
    finally:
        await db.close()

    return {
        "risk_grade": grade,
        "days": days,
        "approved": approved,
        "approved_losing": approved_losing,
        "rejected": rejected,
    }


def build_nudge_line(pattern: dict) -> str | None:
    """Render a single-line nudge for the proposal rationale, or None.

    Returns None when there's nothing worth saying (no prior activity on
    this grade in the window).
    """
    grade = pattern["risk_grade"].upper()
    days = pattern["days"]
    approved = pattern["approved"]
    approved_losing = pattern["approved_losing"]
    rejected = pattern["rejected"]

    # Approved a bunch of risky tokens and a meaningful fraction went bad —
    # the nudge worth hearing is "you've done this before and it stung".
    if approved >= 3 and approved_losing >= 2:
        return (
            f"You've approved {approved} {grade} tokens in the last {days} days; "
            f"{approved_losing} closed at a loss >20%."
        )

    # Rejecting lots of GREEN proposals suggests the persona may be mis-tuned.
    if grade == "GREEN" and rejected >= 5 and approved == 0:
        return (
            f"You've rejected {rejected} GREEN tokens in the last {days} days — "
            f"is the persona miscalibrated?"
        )

    if approved >= 1 or rejected >= 1:
        return (
            f"Recent {grade} activity ({days}d): {approved} approved, {rejected} rejected."
        )

    return None
