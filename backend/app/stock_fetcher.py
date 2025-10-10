from __future__ import annotations
import asyncio
# import redis.asyncio as redis
import os
import random
import uuid
import httpx
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
# from fastapi.security import OAuth2PasswordBearer
# from datadog import statsd

# --- config & env ------------------------------------------------------------

BASE_URL = "https://finnhub.io/api/v1"

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

if not FINNHUB_API_KEY:
    raise RuntimeError("FINNHUB_API_KEY missing in environment")

# --- errors -----------------------------------------------------------------
class FinnhubError(Exception):
    pass

# --- small helpers -----------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Choose a PE metric with documented precedence
PE_KEYS = ("peBasicExclExtraTTM", "peNormalizedAnnual", "peTTM")

# Type for returned dict
class NormalizedStock(TypedDict, total=False):
    ticker: str
    trade_id: str
    name: Optional[str]
    exchange: Optional[str]
    currency: Optional[str]
    market_cap: Optional[float]  
    pe_ratio: Optional[float]
    price: Optional[float]
    prev_close: Optional[float]
    fetched_at: str
    data_status: str  # "complete" | "partial"
    missing: List[str]

# --- HTTP client with retry/backoff -----------------------------------------
class AsyncFinnhubClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL, timeout: float = 8.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=timeout, headers={"Accept": "application/json"})

    async def close(self) -> None:
        await self.client.aclose()

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None, retries: int = 2) -> Dict[str, Any]:
        params = dict(params or {})
        params["token"] = self.api_key
        url = f"{self.base_url}{path}"
        backoff = 0.25
        for attempt in range(retries + 1):
            try:
                # trade_id = str(uuid.uuid4())  # Unique trade ID generated
                resp = await self.client.get(url, params=params)
                # Retry on rate limit and transient server errors
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    raise FinnhubError(f"Upstream {resp.status_code}: {resp.text[:120]}")
                resp.raise_for_status()
                return resp.json()
            except Exception:
                if attempt >= retries:
                    raise
                # exponential backoff with jitter
                jitter = random.uniform(0, backoff / 2)
                await asyncio.sleep(backoff + jitter)
                backoff = min(backoff * 2, 2.0)

    # --- endpoint wrappers ---
    async def quote(self, symbol: str) -> Dict[str, Any]:
        return await self._get("/quote", {"symbol": symbol})

    async def profile2(self, symbol: str) -> Dict[str, Any]:
        return await self._get("/stock/profile2", {"symbol": symbol})

    async def basic_financials(self, symbol: str, metric: str = "all") -> Dict[str, Any]:
        return await self._get("/stock/metric", {"symbol": symbol, "metric": metric})


# --- field selection & merge -------------------------------------------------

def _select_pe(financials_payload: Dict[str, Any]) -> Optional[float]:
    metric = financials_payload.get("metric") or {}
    for key in PE_KEYS:
        val = metric.get(key)
        if isinstance(val, (int, float)) and val > 0:
            return float(val)
    return None


async def fetch_stock_data(symbol: str, client: Optional[AsyncFinnhubClient] = None) -> NormalizedStock:
    """
        Fetch Profile2 + Basic Financials + Quote concurrently and merge.
        Returns a NormalizedStock dict with missing fields flagged and data_status set.
    """
    sym = symbol.upper().strip()

    own_client = client is None
    client = client or AsyncFinnhubClient(FINNHUB_API_KEY)

    try:
        # Fire the three calls concurrently
        t_profile = asyncio.create_task(client.profile2(sym))
        t_fin = asyncio.create_task(client.basic_financials(sym))
        t_quote = asyncio.create_task(client.quote(sym))

        profile, financials, quote = await asyncio.gather(t_profile, t_fin, t_quote, return_exceptions=True)

        missing: List[str] = []

        # Profile2 mapping
        name = exchange = currency = None
        market_cap: Optional[float] = None
        canonical = sym
        if isinstance(profile, Exception) or not profile:
            missing += ["name", "exchange", "currency", "market_cap"]
        else:
            name = profile.get("name")
            exchange = profile.get("exchange")
            currency = profile.get("currency")
            mc = profile.get("marketCapitalization")
            market_cap = float(mc) if isinstance(mc, (int, float)) else None
            canonical = profile.get("ticker") or sym
            if not name:
                missing.append("name")
            if market_cap is None:
                missing.append("market_cap")
            if not exchange:
                missing.append("exchange")
            if not currency:
                missing.append("currency")

        # Basic financials → PE
        pe_ratio: Optional[float] = None
        if isinstance(financials, Exception) or not financials:
            missing.append("pe_ratio")
        else:
            pe_ratio = _select_pe(financials)
            if pe_ratio is None:
                missing.append("pe_ratio")

        # Quote mapping
        price = prev_close = None
        if isinstance(quote, Exception) or not quote:
            missing += ["price", "prev_close"]
        else:
            c = quote.get("c")
            price = float(c) if isinstance(c, (int, float)) and c else None
            pc = quote.get("pc")
            prev_close = float(pc) if isinstance(pc, (int, float)) else None
            if price is None:
                missing.append("price")
            if prev_close is None:
                missing.append("prev_close")

        data_status = "complete" if not missing else "partial"

        return NormalizedStock(
            trade_id = str(uuid.uuid4()),
            ticker=canonical,
            name=name,
            exchange=exchange,
            currency=currency,
            market_cap=market_cap,
            pe_ratio=pe_ratio,
            price=price,
            prev_close=prev_close,
            fetched_at=_now_iso(),
            data_status=data_status,
            missing=sorted(set(missing))
        )
    finally:
        if own_client:
            await client.close()

# Convenience: quick manual test when run directly
if __name__ == "__main__":
    async def _demo():
        print(await fetch_stock_data("AMZN"))

    asyncio.run(_demo())
