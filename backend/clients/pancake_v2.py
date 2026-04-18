"""PancakeSwap V2 router client — sell-side fallback for graduated Four.meme tokens.

Once a Four.meme token graduates, its bonding curve closes and liquidity
migrates to a PancakeSwap V2 pair. The Four.meme CLI's `sell` targets the
TokenManager contract and reverts for graduated tokens, so we swap directly
against the V2 router instead.
"""

import json
import time
from pathlib import Path

from eth_account import Account
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from config import settings, Contracts

ABI_DIR = Path(__file__).resolve().parent.parent / "abis"

# Approve the router for MAX_UINT256 once per token. Re-approving per sell
# doubles the tx cost for no safety benefit — the agent wallet holds nothing
# but throwaway trading positions.
_MAX_UINT256 = (1 << 256) - 1

# Deadline window for swap txs. 10 min is long enough to survive RPC retries
# without leaving a stale signed-tx hanging around the mempool.
_DEADLINE_SECONDS = 600


def _load_abi(name: str) -> list:
    with open(ABI_DIR / f"{name}.json") as f:
        return json.load(f)


class PancakeV2Client:
    """Sign + send transactions against PancakeSwap V2 Router."""

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.bsc_rpc_url))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(Contracts.PANCAKE_ROUTER_V2),
            abi=_load_abi("PancakeRouterV2"),
        )
        self.wbnb = Web3.to_checksum_address(Contracts.WBNB)
        self.erc20_abi = _load_abi("ERC20")

        if not settings.private_key:
            raise RuntimeError("PRIVATE_KEY not configured — cannot sign swaps")
        self.account = Account.from_key(settings.private_key)

    def _erc20(self, token_address: str):
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=self.erc20_abi,
        )

    def quote_sell(self, token_address: str, amount_in_wei: int) -> int:
        """Return estimated BNB wei out for selling `amount_in_wei` tokens."""
        path = [Web3.to_checksum_address(token_address), self.wbnb]
        amounts = self.router.functions.getAmountsOut(amount_in_wei, path).call()
        return int(amounts[-1]) if amounts else 0

    def _send_tx(self, tx_builder, gas_estimate_fallback: int):
        """Build, sign, send a tx; return the raw tx_hash HexBytes so callers
        can pass it to wait_for_transaction_receipt without conversion."""
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price
        tx = tx_builder.build_transaction({
            "from": self.account.address,
            "nonce": nonce,
            "gasPrice": gas_price,
            "chainId": 56,
        })
        # Some calls fail estimate_gas (e.g., fresh token with no pair yet) —
        # fall back to a conservative hardcoded limit so we still surface the
        # actual revert reason on-chain instead of bailing pre-flight.
        try:
            tx["gas"] = int(self.w3.eth.estimate_gas(tx) * 1.2)
        except Exception:
            tx["gas"] = gas_estimate_fallback
        signed = self.account.sign_transaction(tx)
        return self.w3.eth.send_raw_transaction(signed.raw_transaction)

    def approve_if_needed(self, token_address: str) -> str | None:
        """Approve the router to spend `token_address` if allowance is too low.
        Returns the approval tx_hash hex, or None if no approval was needed."""
        token = self._erc20(token_address)
        current = token.functions.allowance(
            self.account.address,
            self.router.address,
        ).call()
        # Any value over the halfway mark means we've already done an unlimited
        # approve — don't repay gas to re-approve.
        if current > (_MAX_UINT256 >> 1):
            return None
        tx_hash = self._send_tx(
            token.functions.approve(self.router.address, _MAX_UINT256),
            gas_estimate_fallback=80_000,
        )
        # Block until mined so the swap's allowance check passes.
        self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        return tx_hash.hex()

    def sell_to_bnb(
        self,
        token_address: str,
        amount_in_wei: int,
        min_out_wei: int,
        is_fee_on_transfer: bool = False,
    ) -> dict:
        """Swap `amount_in_wei` of `token_address` to BNB.

        `is_fee_on_transfer` routes through the tax-safe variant for TaxToken
        contracts — the non-supporting variant reverts with "INSUFFICIENT_OUTPUT"
        whenever transfer fees shave any tokens off mid-swap.
        """
        approve_hash = self.approve_if_needed(token_address)

        path = [Web3.to_checksum_address(token_address), self.wbnb]
        deadline = int(time.time()) + _DEADLINE_SECONDS
        if is_fee_on_transfer:
            builder = self.router.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_in_wei, min_out_wei, path, self.account.address, deadline,
            )
        else:
            builder = self.router.functions.swapExactTokensForETH(
                amount_in_wei, min_out_wei, path, self.account.address, deadline,
            )
        tx_hash = self._send_tx(builder, gas_estimate_fallback=300_000)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        tx_hash_hex = tx_hash.hex()
        if receipt["status"] != 1:
            raise RuntimeError(f"swap reverted: tx={tx_hash_hex}")
        return {"txHash": tx_hash_hex, "approveTxHash": approve_hash}
