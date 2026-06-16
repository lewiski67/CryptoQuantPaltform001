import json
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

from tests.unit.domain.helpers import assert_value_error

from cq.domain import Symbol
from cq.exchanges.binance import BinancePublicRestClient


def test_binance_public_rest_client_builds_kline_request() -> None:
    captured: dict[str, object] = {}

    def read_url(url: str, timeout: float) -> bytes:
        captured["url"] = url
        captured["timeout"] = timeout
        return json.dumps([list(sample_kline())]).encode("utf-8")

    client = BinancePublicRestClient(
        base_url="https://example.test/",
        timeout=3.0,
        url_reader=read_url,
    )

    klines = client.fetch_klines(btc_usdt(), "1h", timestamp(0), timestamp(2), limit=500)

    url = urlparse(str(captured["url"]))
    query = parse_qs(url.query)
    assert url.path == "/api/v3/klines"
    assert captured["timeout"] == 3.0
    assert query["symbol"] == ["BTCUSDT"]
    assert query["interval"] == ["1h"]
    assert query["startTime"] == [str(millis(timestamp(0)))]
    assert query["endTime"] == [str(millis(timestamp(2) - timedelta(milliseconds=1)))]
    assert query["limit"] == ["500"]
    assert klines == (sample_kline(),)


def test_binance_public_rest_client_rejects_invalid_range() -> None:
    client = BinancePublicRestClient(url_reader=lambda url, timeout: b"[]")

    def fetch_invalid_range() -> object:
        return client.fetch_klines(btc_usdt(), "1h", timestamp(1), timestamp(1))

    assert_value_error("end must be after start", fetch_invalid_range)


def test_binance_public_rest_client_rejects_non_list_response() -> None:
    client = BinancePublicRestClient(url_reader=lambda url, timeout: b"{}")

    def fetch_invalid_response() -> object:
        return client.fetch_klines(btc_usdt(), "1h", timestamp(0), timestamp(1))

    assert_value_error("Binance klines response must be a list", fetch_invalid_response)


def test_binance_public_rest_client_rejects_invalid_json_response() -> None:
    client = BinancePublicRestClient(url_reader=lambda url, timeout: b"{bad json")

    def fetch_invalid_response() -> object:
        return client.fetch_klines(btc_usdt(), "1h", timestamp(0), timestamp(1))

    assert_value_error("invalid Binance klines response", fetch_invalid_response)


def sample_kline() -> tuple[object, ...]:
    return (
        millis(timestamp(0)),
        "100.00",
        "110.00",
        "90.00",
        "105.00",
        "12.5",
        millis(timestamp(1) - timedelta(milliseconds=1)),
    )


def btc_usdt() -> Symbol:
    return Symbol("BTCUSDT", base_asset="BTC", quote_asset="USDT")


def timestamp(hour: int) -> datetime:
    return datetime(2026, 1, 1, hour, tzinfo=UTC)


def millis(value: datetime) -> int:
    return int(value.timestamp() * 1000)
