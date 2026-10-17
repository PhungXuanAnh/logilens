"""Rate-limit behavior through the HTTP application and a timed window."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.rate_limit import RateLimiter, rate_limit_middleware


def test_login_limit_returns_429_with_retry_after():
    from fastapi import FastAPI

    app = FastAPI()
    app.middleware("http")(rate_limit_middleware(RateLimiter(login_limit=2, ask_limit=3)))

    @app.post("/api/auth/login")
    def login():
        return {"ok": True}

    with TestClient(app) as client:
        assert client.post("/api/auth/login").status_code == 200
        assert client.post("/api/auth/login").status_code == 200
        blocked = client.post("/api/auth/login")
        assert blocked.status_code == 429
        assert int(blocked.headers["Retry-After"]) > 0


def test_ask_routes_share_limit_and_ignore_spoofed_forwarded_for():
    from fastapi import FastAPI

    app = FastAPI()
    app.middleware("http")(rate_limit_middleware(RateLimiter(login_limit=2, ask_limit=1)))

    @app.post("/api/ask")
    def ask():
        return {"ok": True}

    @app.post("/api/v2/ask")
    def ask_v2():
        return {"ok": True}

    with TestClient(app) as client:
        assert client.post("/api/ask", headers={"X-Forwarded-For": "1.2.3.4"}).status_code == 200
        assert client.post("/api/v2/ask", headers={"X-Forwarded-For": "5.6.7.8"}).status_code == 429


def test_window_resets_and_clients_are_independent():
    limiter = RateLimiter(login_limit=1, ask_limit=1, window_seconds=60)
    assert limiter.check("user-a", "/api/ask", now=100) == 0
    assert limiter.check("user-a", "/api/v2/ask", now=120) == 40
    assert limiter.check("user-b", "/api/ask", now=120) == 0
    assert limiter.check("user-a", "/api/ask", now=160) == 0
    assert limiter.check("user-a", "/healthz", now=160) == 0
