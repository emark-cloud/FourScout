"""Persona-based action engine — maps risk scores + persona rules to trade actions."""

from dataclasses import dataclass

from database import get_all_config
from services.override_stats import build_nudge_line, get_recent_pattern


@dataclass
class TradeAction:
    action: str  # buy / skip / monitor / take_profit / exit / reduce
    reason: str
    amount_bnb: float = 0.0
    slippage: float = 5.0
    recheck_minutes: int = 0


PERSONA_CONFIGS = {
    "conservative": {
        "default_amount_bnb": 0.0001,
        "min_token_age_minutes": 10,
        "max_holder_concentration": 40,
        "required_grade": "green",
        "trade_on_amber": False,
        "bonding_curve_only": False,
    },
    "momentum": {
        "default_amount_bnb": 0.0001,
        "min_token_age_minutes": 3,
        "max_holder_concentration": 50,
        "required_grade": "green",
        "trade_on_amber": True,
        "bonding_curve_only": False,
    },
    "sniper": {
        "default_amount_bnb": 0.0001,
        "min_token_age_minutes": 0,
        "max_holder_concentration": 60,
        "required_grade": "amber",
        "trade_on_amber": True,
        "bonding_curve_only": True,
    },
}


async def decide_action(
    risk_grade: str,
    risk_percentage: float,
    token_data: dict,
    active_positions: int = 0,
    budget_used_today: float = 0.0,
) -> TradeAction:
    """Decide what action the persona should take for a given token.

    The deterministic decision is never changed by override history — that
    stays a pure persona × risk-grade × budget function. We append a single
    trailing nudge line to the reason text so the user sees their own
    pattern on the proposal without the engine quietly adjusting.
    """
    config = await get_all_config()
    persona_name = config.get("persona", "momentum")
    persona = PERSONA_CONFIGS.get(persona_name, PERSONA_CONFIGS["momentum"])

    max_per_trade = float(config.get("max_per_trade_bnb", 0.05))
    max_per_day = float(config.get("max_per_day_bnb", 0.3))
    max_positions = int(config.get("max_active_positions", 3))
    max_slippage = float(config.get("max_slippage_pct", 5.0))

    amount = min(persona["default_amount_bnb"], max_per_trade)

    # Hard budget checks
    if budget_used_today + amount > max_per_day:
        return TradeAction("skip", "Daily budget limit reached", 0)

    if active_positions >= max_positions:
        return TradeAction("skip", f"Max active positions ({max_positions}) reached", 0)

    # Risk grade check
    if risk_grade == "red":
        return TradeAction("skip", "Risk score is RED — too dangerous", 0)

    if risk_grade == "amber" and not persona["trade_on_amber"]:
        return TradeAction("monitor", f"Amber risk — {persona_name} persona requires GREEN", recheck_minutes=10)

    if risk_grade == "green" or (risk_grade == "amber" and persona["trade_on_amber"]):
        # Check token-specific filters
        graduated = token_data.get("graduated", False)
        if persona["bonding_curve_only"] and graduated:
            return TradeAction("skip", "Sniper only trades during bonding curve phase", 0)

        # Token age check
        launch_time = token_data.get("launch_time", "")
        if launch_time and persona["min_token_age_minutes"] > 0:
            from datetime import datetime, timezone
            try:
                age_seconds = (datetime.now(timezone.utc) - datetime.fromisoformat(launch_time.replace("Z", "+00:00"))).total_seconds()
                age_minutes = age_seconds / 60
                if age_minutes < persona["min_token_age_minutes"]:
                    return TradeAction(
                        "monitor",
                        f"Token too new ({age_minutes:.0f}m) — {persona_name} requires {persona['min_token_age_minutes']}m minimum",
                        recheck_minutes=persona["min_token_age_minutes"] - int(age_minutes),
                    )
            except (ValueError, TypeError):
                pass

        reason = f"{persona_name.capitalize()} recommends entry"
        nudge = await _try_build_nudge(risk_grade)
        if nudge:
            reason = f"{reason}. {nudge}"
        return TradeAction("buy", reason, amount, max_slippage)

    return TradeAction("monitor", "Monitoring — conditions not met for entry", recheck_minutes=5)


async def _try_build_nudge(risk_grade: str) -> str | None:
    """Fetch override pattern + render a nudge. Never raises into the caller.

    The nudge is pure observability; a DB hiccup here must not block a
    proposal from being generated.
    """
    try:
        pattern = await get_recent_pattern(risk_grade)
    except Exception as e:
        print(f"[PersonaEngine] override_stats failed: {e}")
        return None
    return build_nudge_line(pattern)
