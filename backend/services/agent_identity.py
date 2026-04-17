"""ERC-8004 Agent Identity — register and verify on-chain agent status."""

import asyncio

from config import settings
from clients.fourmeme_cli import FourMemeCLI, FourMemeError
from clients.bsc_web3 import BSCWeb3Client


_cli: FourMemeCLI | None = None
_web3: BSCWeb3Client | None = None


def _get_cli() -> FourMemeCLI:
    global _cli
    if _cli is None:
        _cli = FourMemeCLI()
    return _cli


def _get_web3() -> BSCWeb3Client:
    global _web3
    if _web3 is None:
        _web3 = BSCWeb3Client()
    return _web3


def get_wallet_address() -> str | None:
    """Derive wallet address from configured private key."""
    if not settings.private_key:
        return None
    try:
        from eth_account import Account
        return Account.from_key(settings.private_key).address
    except Exception:
        return None


async def get_agent_status() -> dict:
    """Check current ERC-8004 agent registration status."""
    address = get_wallet_address()
    if not address:
        return {
            "wallet_address": None,
            "is_registered": False,
            "has_private_key": False,
        }

    web3 = _get_web3()
    is_registered, bnb_balance = await asyncio.gather(
        asyncio.to_thread(web3.is_agent, address),
        asyncio.to_thread(web3.get_bnb_balance, address),
    )

    return {
        "wallet_address": address,
        "is_registered": is_registered,
        "has_private_key": True,
        "bnb_balance": round(bnb_balance, 4),
    }


async def register_agent(name: str, image_url: str | None = None, description: str | None = None) -> dict:
    """Register wallet as ERC-8004 agent identity on-chain."""
    address = get_wallet_address()
    if not address:
        return {"success": False, "error": "No private key configured"}

    # Check if already registered
    web3 = _get_web3()
    if await asyncio.to_thread(web3.is_agent, address):
        return {"success": True, "already_registered": True, "wallet_address": address}

    cli = _get_cli()
    try:
        result = await cli.register_8004(name, image_url, description)
        return {
            "success": True,
            "already_registered": False,
            "wallet_address": address,
            "tx_result": result if isinstance(result, dict) else str(result),
        }
    except FourMemeError as e:
        return {"success": False, "error": str(e)}
