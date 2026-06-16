"""Binance public historical market data client."""

import json
from collections.abc import Callable
from datetime import datetime, timedelta
from json import JSONDecodeError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cq.domain import Symbol
from cq.exchanges.binance.klines import BinanceKline, millis_from_datetime

UrlReader = Callable[[str, float], bytes]


class BinancePublicRestClient:
    def __init__(
        self,
        base_url: str = "https://api.binance.com",
        timeout: float = 10.0,
        url_reader: UrlReader | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.url_reader = read_url if url_reader is None else url_reader

    def fetch_klines(
        self,
        symbol: Symbol,
        interval: str,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> tuple[BinanceKline, ...]:
        if end <= start:
            raise ValueError("end must be after start")
        if limit <= 0 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")

        query = urlencode(
            {
                "symbol": symbol.value,
                "interval": interval,
                "startTime": millis_from_datetime(start),
                "endTime": millis_from_datetime(end - timedelta(milliseconds=1)),
                "limit": limit,
            }
        )
        payload = self.url_reader(f"{self.base_url}/api/v3/klines?{query}", self.timeout)
        try:
            parsed = json.loads(payload.decode("utf-8"))
        except (JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("invalid Binance klines response") from exc
        if not isinstance(parsed, list):
            raise ValueError("Binance klines response must be a list")
        return tuple(parse_raw_kline(item) for item in parsed)


def read_url(url: str, timeout: float) -> bytes:
    request = Request(url, headers={"User-Agent": "crypto-quant/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def parse_raw_kline(value: object) -> BinanceKline:
    if not isinstance(value, list):
        raise ValueError("Binance kline item must be a list")
    return tuple(value)
