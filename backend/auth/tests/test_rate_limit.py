from starlette.requests import Request

from middleware.rate_limit import get_client_ip


def _request(headers: list[tuple[bytes, bytes]], client: tuple[str, int]) -> Request:
    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": headers,
            "client": client,
            "server": ("test", 80),
        }
    )


def test_rate_limit_uses_gateway_forwarded_real_ip():
    request = _request(
        [(b"x-real-ip", b"203.0.113.10"), (b"x-forwarded-for", b"198.51.100.2, 203.0.113.10")],
        ("172.20.0.5", 8000),
    )

    assert get_client_ip(request) == "203.0.113.10"


def test_rate_limit_falls_back_to_socket_peer_without_proxy_headers():
    request = _request([], ("127.0.0.1", 9000))

    assert get_client_ip(request) == "127.0.0.1"
