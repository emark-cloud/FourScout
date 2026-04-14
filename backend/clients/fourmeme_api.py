"""Four.meme REST API client for token discovery and metadata."""

import httpx
from config import settings


class FourMemeAPI:
    """Async HTTP client for the Four.meme public API."""

    def __init__(self):
        self.base_url = settings.fourmeme_api_base
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=15.0,
            headers={"Content-Type": "application/json"},
        )

    async def search_tokens(
        self,
        token_type: str = "NEW",
        list_type: str = "NOR",
        page: int = 1,
        size: int = 20,
        status: str = "ALL",
        sort: str = "DESC",
    ) -> list:
        """Search for tokens on Four.meme."""
        try:
            resp = await self.client.post(
                "/public/token/search",
                json={
                    "type": token_type,
                    "listType": list_type,
                    "pageNo": page,
                    "pageSize": size,
                    "status": status,
                    "sort": sort,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            # API returns { code, data: { records: [...] } } or similar
            if isinstance(data, dict):
                if "data" in data:
                    records = data["data"]
                    if isinstance(records, dict) and "records" in records:
                        return records["records"]
                    if isinstance(records, list):
                        return records
                if "records" in data:
                    return data["records"]
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"[FourMemeAPI] search_tokens error: {e}")
            return []

    async def get_token(self, address: str) -> dict:
        """Get detailed token information."""
        try:
            resp = await self.client.get(
                "/private/token/get/v2",
                params={"address": address},
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data
        except Exception as e:
            print(f"[FourMemeAPI] get_token error: {e}")
            return {}

    async def get_rankings(
        self,
        ranking_type: str = "NEW",
        page_size: int = 20,
    ) -> list:
        """Get token rankings."""
        try:
            resp = await self.client.post(
                "/public/token/ranking",
                json={
                    "type": ranking_type,
                    "pageSize": page_size,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                records = data["data"]
                if isinstance(records, dict) and "records" in records:
                    return records["records"]
                if isinstance(records, list):
                    return records
            return []
        except Exception as e:
            print(f"[FourMemeAPI] get_rankings error: {e}")
            return []

    async def get_config(self) -> dict:
        """Get Four.meme public configuration."""
        try:
            resp = await self.client.get("/public/config")
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", data) if isinstance(data, dict) else data
        except Exception as e:
            print(f"[FourMemeAPI] get_config error: {e}")
            return {}

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
