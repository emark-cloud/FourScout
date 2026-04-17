"""Position tracker — background job that updates prices, computes PnL,
proposes exits (configurable thresholds + AI analysis), and optionally auto-sells."""

import asyncio
import json
from datetime import datetime, timezone

from config import settings
from database import get_db, get_all_config
from clients.bsc_web3 import BSCWeb3Client

_cycle_count = 0

# Per-position cooldown: token_address -> (last_ai_check_ts, pnl_pct_at_check).
# Suppresses LLM exit calls that would just re-confirm unchanged state.
_last_ai_check: dict[str, tuple[datetime, float]] = {}
_AI_COOLDOWN_MINUTES = 15
_AI_PNL_DELTA_PCT = 3.0


async def start_position_tracker(ws_manager, interval: int = 60):
    """Periodically update active position prices and PnL."""
    global _cycle_count
    web3 = BSCWeb3Client()
    ai_interval = max(1, settings.ai_exit_interval_cycles)

    try:
        while True:
            _cycle_count += 1
            do_ai = (_cycle_count % ai_interval == 0)
            try:
                await update_positions(web3, ws_manager, do_ai_analysis=do_ai)
            except Exception as e:
                print(f"[PositionTracker] Error: {e}")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass


async def update_positions(web3: BSCWeb3Client, ws_manager, do_ai_analysis: bool = False):
    """Fetch current prices for all active positions and update PnL."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT p.*, t.name as token_name FROM positions p
               LEFT JOIN tokens t ON p.token_address = t.address
               WHERE p.status = 'active'"""
        )
        positions = [dict(row) for row in await cursor.fetchall()]

        if not positions:
            return

        now = datetime.now(timezone.utc).isoformat()

        # Read user-configurable thresholds
        config = await get_all_config()
        take_profit_pct = float(config.get("take_profit_pct", "100"))
        stop_loss_pct = float(config.get("stop_loss_pct", "-50"))

        ai_calls_remaining = 3  # Cap LLM calls per cycle

        for pos in positions:
            try:
                info = web3.get_token_info(pos["token_address"])
                if not info:
                    continue

                last_price = info.get("lastPrice", 0)
                current_price = last_price / 10**18 if last_price else 0

                entry_amount = pos.get("entry_amount_bnb", 0) or 0
                token_qty = pos.get("token_quantity", 0) or 0

                # PnL = (current_value - entry_cost)
                current_value = token_qty * current_price if current_price > 0 else 0
                pnl = current_value - entry_amount

                await db.execute(
                    "UPDATE positions SET current_price = ?, pnl_bnb = ? WHERE id = ?",
                    (current_price, round(pnl, 8), pos["id"]),
                )

                # Broadcast position update
                if ws_manager:
                    await ws_manager.broadcast("position_update", {
                        "position_id": pos["id"],
                        "token_address": pos["token_address"],
                        "token_name": pos.get("token_name") or pos["token_address"][:10] + "...",
                        "current_price": current_price,
                        "pnl_bnb": round(pnl, 8),
                        "entry_amount_bnb": entry_amount,
                    })

                # Check exit conditions against user-configured thresholds
                if entry_amount > 0:
                    pnl_pct = (pnl / entry_amount) * 100
                    if pnl_pct >= take_profit_pct:
                        await _propose_exit(
                            db, pos, "take_profit",
                            f"Take profit triggered ({pnl_pct:.0f}% >= {take_profit_pct:.0f}% threshold)",
                            ws_manager,
                        )
                    elif pnl_pct <= stop_loss_pct:
                        await _propose_exit(
                            db, pos, "stop_loss",
                            f"Stop loss triggered ({pnl_pct:.0f}% <= {stop_loss_pct:.0f}% threshold)",
                            ws_manager,
                        )
                    elif do_ai_analysis and ai_calls_remaining > 0:
                        # AI analysis only when the position is meaningfully close
                        # to either exit threshold, or has been sitting dormant.
                        # Tighter bands than before so mid-range positions don't
                        # burn LLM budget on "still holding" checks.
                        in_band = (
                            (stop_loss_pct * 0.7 <= pnl_pct <= stop_loss_pct * 0.4)  # last 30% toward SL
                            or (take_profit_pct * 0.7 <= pnl_pct < take_profit_pct)  # last 30% toward TP
                            or _is_stale_position(pos, now)
                        )
                        if in_band and _should_call_ai(pos["token_address"], pnl_pct):
                            ai_result = await _ai_analyze_position(pos, pnl_pct, web3)
                            ai_calls_remaining -= 1
                            _last_ai_check[pos["token_address"]] = (datetime.now(timezone.utc), pnl_pct)
                            if ai_result and ai_result.get("recommendation") == "exit" and ai_result.get("confidence", 0) >= 70:
                                await _propose_exit(
                                    db, pos, "ai_analysis",
                                    f"[AI confidence {ai_result['confidence']}%] {ai_result.get('reasoning', 'AI recommends exit')}",
                                    ws_manager,
                                )

            except Exception as e:
                print(f"[PositionTracker] Error updating {pos['token_address']}: {e}")

        await db.commit()
    finally:
        await db.close()


def _should_call_ai(token_address: str, pnl_pct: float) -> bool:
    """Skip LLM if we checked this position recently AND the PnL hasn't moved.

    Drift gating alone isn't enough — a position sitting at -35% with SL=-50
    will keep re-entering the "approaching SL" band every cycle. Without a
    cooldown we pay for the same analysis over and over.
    """
    last = _last_ai_check.get(token_address)
    if not last:
        return True
    last_ts, last_pnl = last
    age_min = (datetime.now(timezone.utc) - last_ts).total_seconds() / 60
    if age_min >= _AI_COOLDOWN_MINUTES:
        return True
    return abs(pnl_pct - last_pnl) >= _AI_PNL_DELTA_PCT


def _is_stale_position(pos: dict, now_iso: str) -> bool:
    """Check if a position has been open 30+ minutes."""
    opened_at = pos.get("opened_at", "")
    if not opened_at:
        return False
    try:
        opened = datetime.fromisoformat(opened_at.replace("Z", "+00:00"))
        now_dt = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
        age_minutes = (now_dt - opened).total_seconds() / 60
        return age_minutes >= 30
    except (ValueError, TypeError):
        return False


async def _ai_analyze_position(position: dict, pnl_pct: float, web3: BSCWeb3Client) -> dict | None:
    """Use LLM to analyze whether a position should be exited."""
    try:
        from services.llm_service import get_llm_service
        llm = get_llm_service()
        if not llm.client:
            return None

        token_address = position["token_address"]

        # Gather current on-chain data
        holder_data = {}
        try:
            holder_data = web3.get_holder_balances(token_address)
        except Exception:
            pass

        # Compute position age
        age_str = "unknown"
        opened_at = position.get("opened_at", "")
        if opened_at:
            try:
                opened = datetime.fromisoformat(opened_at.replace("Z", "+00:00"))
                age_min = (datetime.now(timezone.utc) - opened).total_seconds() / 60
                age_str = f"{age_min:.0f} minutes"
            except (ValueError, TypeError):
                pass

        return await llm.analyze_position_exit({
            "token_address": token_address,
            "entry_price": position.get("entry_price", 0),
            "entry_amount_bnb": position.get("entry_amount_bnb", 0),
            "token_quantity": position.get("token_quantity", 0),
            "current_price": position.get("current_price", 0),
            "pnl_pct": pnl_pct,
            "position_age": age_str,
            "entry_risk_score": position.get("entry_risk_score", "unknown"),
            "top5_holder_pct": holder_data.get("top5_pct", "unknown"),
            "max_single_holder_pct": holder_data.get("max_single_pct", "unknown"),
            "unique_holders": holder_data.get("unique_holders", "unknown"),
        })
    except Exception as e:
        print(f"[PositionTracker] AI analysis error: {e}")
        return None


async def _propose_exit(db, position: dict, reason_type: str, rationale: str, ws_manager):
    """Create a pending sell action for position exit. Auto-executes if auto_sell_enabled."""
    now = datetime.now(timezone.utc).isoformat()

    # Check if there's already a pending exit for this position
    cursor = await db.execute(
        "SELECT id FROM pending_actions WHERE token_address = ? AND action_type = 'sell' AND status = 'pending'",
        (position["token_address"],),
    )
    if await cursor.fetchone():
        return

    config = await get_all_config()
    auto_sell = config.get("auto_sell_enabled", "false") == "true"
    status = "pending"

    await db.execute(
        """INSERT INTO pending_actions (token_address, action_type, amount_bnb, slippage,
           persona, risk_score, rationale, tx_preview, status, created_at)
           VALUES (?, 'sell', ?, 5.0, ?, ?, ?, ?, ?, ?)""",
        (
            position["token_address"],
            position["entry_amount_bnb"],
            "",
            position.get("entry_risk_score", ""),
            f"[{reason_type.upper()}] {rationale}",
            json.dumps({"token_amount": position.get("token_quantity", 0)}),
            status,
            now,
        ),
    )
    await db.commit()

    # Broadcast the proposal
    if ws_manager:
        await ws_manager.broadcast("action_proposed", {
            "token_address": position["token_address"],
            "action_type": "sell",
            "reason": reason_type,
            "rationale": rationale,
        })

    # Auto-execute if enabled
    if auto_sell:
        cursor = await db.execute(
            "SELECT * FROM pending_actions WHERE token_address = ? AND action_type = 'sell' AND status = 'pending' ORDER BY id DESC LIMIT 1",
            (position["token_address"],),
        )
        pending = await cursor.fetchone()
        if pending:
            await db.execute(
                "UPDATE pending_actions SET status = 'approved', resolved_at = ? WHERE id = ?",
                (now, pending["id"]),
            )
            await db.commit()
            from services.executor import execute_approved_action
            await execute_approved_action(dict(pending), ws_manager)
            print(f"[PositionTracker] Auto-sold {position['token_address']} ({reason_type})")
