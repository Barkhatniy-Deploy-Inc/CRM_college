"""Check the frontend and database health through the shared gateway."""
import json
import sys
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


def check(base_url: str) -> None:
    # System HTTP proxies must not intercept requests to the local Compose stack.
    local_hosts = {"localhost", "127.0.0.1", "::1"}
    opener = build_opener(ProxyHandler({})) if urlsplit(base_url).hostname in local_hosts else build_opener()
    for path in ("/", "/healthz", "/api/auth/health", "/api/schedule/health", "/api/techcard/health"):
        # The header bypasses the browser interstitial on free ngrok tunnels.
        request = Request(base_url.rstrip("/") + path, headers={"ngrok-skip-browser-warning": "1"})
        with opener.open(request, timeout=10) as response:
            body = response.read()
            if response.status != 200:
                raise RuntimeError(f"{path}: HTTP {response.status}")
            if path.startswith("/api/") and json.loads(body).get("status") != "healthy":
                raise RuntimeError(f"{path}: service is unhealthy")
            if path == "/" and b'<div id="app">' not in body:
                raise RuntimeError("Frontend response does not contain the Vue app")
        print(f"OK {path}")


if __name__ == "__main__":
    try:
        check(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080")
    except (URLError, RuntimeError, ValueError) as error:
        sys.exit(f"Check failed: {error}")
