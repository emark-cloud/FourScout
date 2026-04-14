"""Market context data: BNB price, Fear & Greed index."""

import httpx


class MarketContext:
    """Fetches external market data for risk scoring context."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_bnb_price(self) -> float:
        """Get current BNB price in USD from CoinGecko."""
        try:
            resp = await self.client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "binancecoin", "vs_currencies": "usd"},
            )
            resp.raise_for_status()
            return resp.json().get("binancecoin", {}).get("usd", 0.0)
        except Exception as e:
            print(f"[Market] BNB price error: {e}")
            return 0.0

    async def get_fear_greed(self) -> dict:
        """Get Crypto Fear & Greed Index."""
        try:
            resp = await self.client.get("https://api.alternative.me/fng/")
            resp.raise_for_status()
            data = resp.json().get("data", [{}])
            if data:
                return {
                    "value": int(data[0].get("value", 50)),
                    "classification": data[0].get("value_classification", "Neutral"),
                }
            return {"value": 50, "classification": "Neutral"}
        except Exception as e:
            print(f"[Market] Fear & Greed error: {e}")
            return {"value": 50, "classification": "Neutral"}

    async def get_bnb_24h_change(self) -> float:
        """Get BNB 24h price change percentage."""
        try:
            resp = await self.client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": "binancecoin",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                },
            )
            resp.raise_for_status()
            return resp.json().get("binancecoin", {}).get("usd_24h_change", 0.0)
        except Exception as e:
            print(f"[Market] BNB 24h change error: {e}")
            return 0.0

    async def close(self):
        await self.client.aclose()
