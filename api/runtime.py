from __future__ import annotations

from collections import defaultdict
import json
import logging
import os
import threading
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("khasilex.request")

_RATE_LOCK = threading.Lock()
_RATE_BUCKETS: dict[str, tuple[int, int]] = {}


def environment() -> str:
    value = (os.getenv("KHASILEX_ENV") or "development").strip().lower()
    return value if value in {"development", "test", "staging", "production"} else "development"


def is_production() -> bool:
    return environment() == "production"


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(minimum, min(maximum, value))


def request_limit_bytes() -> int:
    return env_int("KHASILEX_MAX_BODY_BYTES", 65536, 1024, 1048576)


def rate_limit_per_minute() -> int:
    return env_int("KHASILEX_RATE_LIMIT_PER_MINUTE", 120, 10, 10000)


def docs_enabled() -> bool:
    return not is_production() or env_bool("KHASILEX_ENABLE_DOCS", False)


def client_key(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def rate_allowed(key: str, limit: int | None = None) -> tuple[bool, int]:
    limit = limit or rate_limit_per_minute()
    window = int(time.time() // 60)
    with _RATE_LOCK:
        current_window, count = _RATE_BUCKETS.get(key, (window, 0))
        if current_window != window:
            current_window, count = window, 0
        count += 1
        _RATE_BUCKETS[key] = (current_window, count)
    remaining = max(0, limit - count)
    return count <= limit, remaining


async def production_guard(request: Request, call_next):
    request_id = (request.headers.get("x-request-id") or "").strip()
    if not request_id or len(request_id) > 128:
        request_id = str(uuid.uuid4())

    if is_production() and request.url.path not in {"/health", "/ready"}:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > request_limit_bytes():
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large", "request_id": request_id},
                        headers={"X-Request-ID": request_id},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length", "request_id": request_id},
                    headers={"X-Request-ID": request_id},
                )

        allowed, remaining = rate_allowed(client_key(request))
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "request_id": request_id},
                headers={
                    "X-Request-ID": request_id,
                    "Retry-After": "60",
                    "X-RateLimit-Remaining": "0",
                },
            )
    else:
        remaining = -1

    started = time.monotonic()
    response = await call_next(request)
    elapsed_ms = round((time.monotonic() - started) * 1000, 2)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if is_production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if remaining >= 0:
            response.headers["X-RateLimit-Remaining"] = str(remaining)

    logger.info(
        json.dumps(
            {
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": elapsed_ms,
                "environment": environment(),
            },
            ensure_ascii=False,
        )
    )
    return response
