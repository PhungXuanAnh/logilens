"""Per-client rate limits for costly and authentication endpoints."""
from __future__ import annotations

import math
import threading
import time

from fastapi import Request
from starlette.responses import JSONResponse


class RateLimiter:
    def __init__(self, *, login_limit: int, ask_limit: int, window_seconds: int = 60):
        self.login_limit = login_limit
        self.ask_limit = ask_limit
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._requests: dict[tuple[str, str], tuple[int, float]] = {}

    def check(self, client: str, path: str, now: float | None = None) -> int:
        if path == "/api/auth/login":
            limit = self.login_limit
            bucket = "login"
        elif path in ("/api/ask", "/api/v2/ask"):
            limit = self.ask_limit
            bucket = "ask"
        else:
            return 0

        now = time.monotonic() if now is None else now
        key = (client, bucket)
        with self._lock:
            count, started = self._requests.get(key, (0, now))
            if now - started >= self.window_seconds:
                count, started = 0, now

            if count >= limit:
                return max(1, math.ceil(self.window_seconds - (now - started)))

            self._requests[key] = (count + 1, started)
        return 0


def rate_limit_middleware(limiter: RateLimiter):
    async def middleware(request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        retry_after = limiter.check(client, request.url.path)
        if retry_after:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)

    return middleware
