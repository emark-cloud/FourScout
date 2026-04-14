"""Async subprocess wrapper for the @four-meme/four-meme-ai CLI.

Uses asyncio.create_subprocess_exec (not shell) to prevent command injection.
All arguments are passed as a list, never interpolated into a shell string.
"""

import asyncio
import json
import os
from pathlib import Path

from config import settings


class FourMemeError(Exception):
    pass


class FourMemeCLI:
    """Wraps the fourmeme CLI binary for async Python usage.

    Security: Uses create_subprocess_exec with argument lists (no shell).
    """

    def __init__(self):
        # Resolve CLI path
        cli_dir = Path(__file__).resolve().parent.parent.parent / "fourmeme-cli"
        self.cli_path = str(cli_dir / "node_modules" / ".bin" / "fourmeme")
        self.cli_dir = str(cli_dir)
        self.timeout = 30

    def _env(self) -> dict:
        """Build environment vars for the CLI subprocess."""
        env = os.environ.copy()
        if settings.private_key:
            env["PRIVATE_KEY"] = settings.private_key
        if settings.bsc_rpc_url:
            env["BSC_RPC_URL"] = settings.bsc_rpc_url
        return env

    async def _run(self, args: list[str]) -> dict | list | str:
        """Run a CLI command and return parsed JSON output.

        Uses create_subprocess_exec (not shell) to avoid injection.
        """
        cmd = [self.cli_path] + args

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._env(),
                cwd=self.cli_dir,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise FourMemeError(f"CLI command timed out after {self.timeout}s: {args[0] if args else 'unknown'}")
        except FileNotFoundError:
            raise FourMemeError(f"CLI binary not found at {self.cli_path}")

        if proc.returncode != 0:
            err_msg = stderr.decode().strip() if stderr else "Unknown error"
            raise FourMemeError(f"CLI error (exit {proc.returncode}): {err_msg}")

        output = stdout.decode().strip()
        if not output:
            return {}

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output

    # --- Token queries ---

    async def get_config(self) -> dict:
        return await self._run(["config"])

    async def token_info(self, address: str) -> dict:
        return await self._run(["token-info", address])

    async def token_list(self, **kwargs) -> list:
        args = ["token-list"]
        for key, val in kwargs.items():
            args.extend([f"--{key}", str(val)])
        result = await self._run(args)
        return result if isinstance(result, list) else []

    async def token_rankings(self, order_by: str = "hot", **kwargs) -> list:
        args = ["token-rankings", order_by]
        for key, val in kwargs.items():
            args.extend([f"--{key}", str(val)])
        result = await self._run(args)
        return result if isinstance(result, list) else []

    # --- Trading ---

    async def quote_buy(self, token: str, amount_wei: str, funds_wei: str = None) -> dict:
        args = ["quote-buy", token, amount_wei]
        if funds_wei:
            args.append(funds_wei)
        return await self._run(args)

    async def quote_sell(self, token: str, amount_wei: str) -> dict:
        return await self._run(["quote-sell", token, amount_wei])

    async def buy_by_funds(self, token: str, funds_wei: str, min_amount_wei: str) -> dict:
        return await self._run(["buy", token, "funds", funds_wei, min_amount_wei])

    async def sell(self, token: str, amount_wei: str, min_funds_wei: str = None) -> dict:
        args = ["sell", token, amount_wei]
        if min_funds_wei:
            args.append(min_funds_wei)
        return await self._run(args)

    # --- Events ---

    async def get_events(self, from_block: int, to_block: int = None) -> list:
        args = ["events", str(from_block)]
        if to_block:
            args.append(str(to_block))
        result = await self._run(args)
        return result if isinstance(result, list) else []

    # --- Tax info ---

    async def tax_info(self, token: str) -> dict:
        return await self._run(["tax-info", token])

    # --- ERC-8004 Agent Identity ---

    async def register_8004(self, name: str, image_url: str = None, description: str = None) -> dict:
        args = ["8004-register", name]
        if image_url:
            args.append(image_url)
        if description:
            args.append(description)
        return await self._run(args)

    async def balance_8004(self, owner: str) -> dict:
        return await self._run(["8004-balance", owner])

    # --- Transfer ---

    async def send(self, to: str, amount_wei: str, token: str = None) -> dict:
        args = ["send", to, amount_wei]
        if token:
            args.extend(["--token", token])
        return await self._run(args)
