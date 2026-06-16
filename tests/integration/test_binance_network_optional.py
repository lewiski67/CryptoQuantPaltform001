import os
from datetime import UTC, datetime

import pytest  # type: ignore[reportMissingImports]

from cq.domain import Symbol
from cq.exchanges.binance import BinancePublicRestClient, klines_to_candles


@pytest.mark.skipif(
    os.environ.get("RUN_BINANCE_NETWORK_TESTS") != "1",
    reason="set RUN_BINANCE_NETWORK_TESTS=1 to run Binance network tests",
)
def test_binance_public_rest_client_fetches_real_klines() -> None:
    symbol = Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")
    client = BinancePublicRestClient()

    klines = client.fetch_klines(
        symbol,
        "1h",
        datetime(2026, 1, 1, tzinfo=UTC),
        datetime(2026, 1, 1, 2, tzinfo=UTC),
        limit=2,
    )
    candles = klines_to_candles(symbol, "1h", klines)

    assert len(candles) == 2
    assert candles[0].open_time == datetime(2026, 1, 1, tzinfo=UTC)
    assert candles[1].close_time == datetime(2026, 1, 1, 2, tzinfo=UTC)
