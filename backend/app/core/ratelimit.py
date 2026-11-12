"""Small in-memory rate limiter for abuse-prone endpoints (login, register, AI).

This protects the free Gemini quota and the login endpoint from simple abuse.
State is kept per process, which is sufficient for a single-instance prototype;
a production deployment would use a shared store such as Redis.
"""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

_hits: dict[tuple[str, str], deque] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    # Render and Vercel sit behind a proxy, so the real client is in X-Forwarded-For.
    forwarded = request.headers.get('x-forwarded-for')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


def rate_limit(name: str, limit: int, window_seconds: int = 60):
    """FastAPI dependency allowing `limit` calls per client per `window_seconds`."""
    def dependency(request: Request):
        key = (name, _client_ip(request))
        now = time.monotonic()
        hits = _hits[key]
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            raise HTTPException(status_code=429, detail='Too many requests. Please wait a minute and try again.')
        hits.append(now)
    return dependency


def reset_rate_limits() -> None:
    """Clear all counters (used by tests)."""
    _hits.clear()