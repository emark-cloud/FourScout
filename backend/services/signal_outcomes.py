"""Signal accuracy tracker — writes per-token outcome rows and aggregates
them into a one-line historical calibration summary for the risk rationale.

Every closed trade and every 24h-resolved avoided token produces one row in
`signal_outcomes`. The risk engine reads back an aggregate filtered by the
token's current grade + creator-score bucket, which is the cleanest way to
express "the agent's past judgments on tokens that look like this".
"""

import json
from datetime import datetime, timedelta, timezone

from database import get_db


# Aggregation window. Matching the plan's "last 30 days" framing.
_SUMMARY_DAYS = 30

# Creator-score bucket boundaries. We bucket to 0-3 (weak), 4-6 (neutral),
# 7-10 (strong) so the aggregate has enough rows to be meaningful.
def _bucket(score: int | None) -> tuple[int, int] | None:
    if score is None:
        return None
    if score <= 3:
        return (0, 3)
    if score <= 6:
        return (4, 6)
    return (7, 10)


def _extract_scores(risk_detail: dict | None) -> dict[str, int | None]:
    """Extract the four tracked signal scores from an in-memory risk_detail dict."""
    out: dict[str, int | None] = {"creator": None, "concentration": None, "velocity": None, "liquidity": None}
    if not isinstance(risk_detail, dict):
        return out
    sig_map = {
        "creator": "creator_history",
        "concentration": "holder_concentration",
        "velocity": "bonding_velocity",
        "liquidity": "liquidity",
    }
    for key, signal_name in sig_map.items():
        sig = risk_detail.get(signal_name)
        if isinstance(sig, dict) and sig.get("score") is not None:
            try:
                out[key] = int(sig["score"])
            except (TypeError, ValueError):
                pass
    return out


async def record_trade_close(
    token_address: str,
    risk_grade: str,
    pnl_pct: float | None,
    recorded_at: str,
) -> None:
    """Insert a `trade_closed` row. Pulls entry signal scores from tokens.risk_detail."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT risk_detail FROM tokens WHERE address = ?",
            (token_address,),
        )
        row = await cursor.fetchone()
        risk_detail = None
        if row and row["risk_detail"]:
            try:
                risk_detail = json.loads(row["risk_detail"])
            except (ValueError, TypeError):
                risk_detail = None
        scores = _extract_scores(risk_detail)
        await db.execute(
            """INSERT INTO signal_outcomes (token_address, entry_risk_grade, entry_risk_percentage,
               creator_score, concentration_score, velocity_score, liquidity_score,
               outcome_type, outcome_pnl_pct, recorded_at)
               VALUES (?, ?, NULL, ?, ?, ?, ?, 'trade_closed', ?, ?)""",
            (
                token_address, risk_grade,
                scores["creator"], scores["concentration"], scores["velocity"], scores["liquidity"],
                pnl_pct, recorded_at,
            ),
        )
        await db.commit()
    finally:
        await db.close()


async def record_avoided_24h(
    token_address: str,
    risk_grade: str,
    price_change_pct: float | None,
    confirmed_rug: bool,
    recorded_at: str,
) -> None:
    """Insert an `avoided_24h` row when the 24h price slot fills."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT risk_detail FROM tokens WHERE address = ?",
            (token_address,),
        )
        row = await cursor.fetchone()
        risk_detail = None
        if row and row["risk_detail"]:
            try:
                risk_detail = json.loads(row["risk_detail"])
            except (ValueError, TypeError):
                risk_detail = None
        scores = _extract_scores(risk_detail)
        await db.execute(
            """INSERT INTO signal_outcomes (token_address, entry_risk_grade, entry_risk_percentage,
               creator_score, concentration_score, velocity_score, liquidity_score,
               outcome_type, outcome_price_change_pct, outcome_confirmed_rug, recorded_at)
               VALUES (?, ?, NULL, ?, ?, ?, ?, 'avoided_24h', ?, ?, ?)""",
            (
                token_address, risk_grade,
                scores["creator"], scores["concentration"], scores["velocity"], scores["liquidity"],
                price_change_pct, 1 if confirmed_rug else 0, recorded_at,
            ),
        )
        await db.commit()
    finally:
        await db.close()


async def get_historical_summary(risk_grade: str, creator_score: int | None) -> str | None:
    """Return a single-line summary of how past tokens of this shape turned out.

    None when there isn't enough history to say anything useful.
    """
    grade = (risk_grade or "").lower()
    since = (datetime.now(timezone.utc) - timedelta(days=_SUMMARY_DAYS)).isoformat()
    bucket = _bucket(creator_score)

    db = await get_db()
    try:
        # Filter by grade; optionally constrain to the creator-score bucket
        # when we have a bucket to filter on.
        if bucket is not None:
            params: tuple = (grade, bucket[0], bucket[1], since)
            where = ("WHERE entry_risk_grade = ? AND creator_score BETWEEN ? AND ? "
                     "AND recorded_at >= ?")
        else:
            params = (grade, since)
            where = "WHERE entry_risk_grade = ? AND recorded_at >= ?"

        cursor = await db.execute(
            f"""SELECT
                SUM(CASE WHEN outcome_type = 'trade_closed' AND outcome_pnl_pct IS NOT NULL
                         AND outcome_pnl_pct > 0 THEN 1 ELSE 0 END) AS profitable,
                SUM(CASE WHEN outcome_type = 'trade_closed' AND outcome_pnl_pct IS NOT NULL
                         AND outcome_pnl_pct <= -20 THEN 1 ELSE 0 END) AS losing,
                SUM(CASE WHEN outcome_type = 'avoided_24h' AND outcome_confirmed_rug = 1
                         THEN 1 ELSE 0 END) AS rugs,
                COUNT(*) AS total
               FROM signal_outcomes
               {where}""",
            params,
        )
        row = await cursor.fetchone()
    finally:
        await db.close()

    if not row or not row["total"] or int(row["total"]) < 3:
        # Too little data to draw a meaningful line.
        return None

    profitable = int(row["profitable"] or 0)
    losing = int(row["losing"] or 0)
    rugs = int(row["rugs"] or 0)
    total = int(row["total"] or 0)

    bucket_label = ""
    if bucket is not None:
        bucket_label = f" with a creator-score {bucket[0]}-{bucket[1]}"
    header = f"Historical ({_SUMMARY_DAYS}d): {total} prior {grade.upper()} tokens{bucket_label}"
    parts = []
    if profitable:
        parts.append(f"{profitable} profitable close{'s' if profitable != 1 else ''}")
    if losing:
        parts.append(f"{losing} closed at >20% loss")
    if rugs:
        parts.append(f"{rugs} confirmed rug{'s' if rugs != 1 else ''}")
    if not parts:
        return None
    return f"{header} — {', '.join(parts)}."
