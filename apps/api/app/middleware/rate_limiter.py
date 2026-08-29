"""Shared rate limiting for the SaaS API (v1 routers).

Three mechanisms:

1. ``limiter`` — slowapi instance for direct-on-app endpoints (legacy api.py
   pattern). NOTE: slowapi decorators break FastAPI >= 0.141 ``include_router``
   (routes silently vanish), so do NOT use ``@limiter.limit`` inside
   APIRouters.

2. ``make_rate_limit(spec)`` — dependency-based sliding-window limiter.
   Keys by client IP + path. Use inside APIRouters::

       from ..middleware.rate_limiter import make_rate_limit

       router = APIRouter()

       @router.get("/x", dependencies=[Depends(make_rate_limit("60/minute"))])
       def x(): ...

3. ``make_tenant_rate_limit(spec)`` — same sliding-window but keyed by
   tenant UUID (from JWT) instead of IP. Prevents a single tenant from
   abusing from multiple IPs. Use for SaaS endpoints::

       from ..middleware.rate_limiter import make_tenant_rate_limit

       @router.get("/x", dependencies=[Depends(make_tenant_rate_limit("30/minute"))])
       def x(): ...

   In-memory per-process bucket. With multiple workers each enforces its
   own window (effective limit = spec x workers) — acceptable for the
   current Render 2-worker deployment.
"""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

# slowapi instance — kept for main.py exception-handler registration
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

_PERIOD_SECONDS = {
    "second": 1,
    "sec": 1,
    "minute": 60,
    "min": 60,
    "hour": 3600,
    "day": 86400,
}

_buckets: dict[str, deque[float]] = defaultdict(deque)
_lock = threading.Lock()


def _parse_spec(spec: str) -> tuple[int, int]:
    """'60/minute' -> (60, 60). Raises ValueError on malformed input."""
    try:
        count_s, period_s = spec.split("/", 1)
        count = int(count_s.strip())
        period = _PERIOD_SECONDS[period_s.strip().lower()]
        if count <= 0 or period <= 0:
            raise ValueError
        return count, period
    except (KeyError, ValueError) as e:
        raise ValueError(
            f"Invalid rate limit spec {spec!r} — expected '<int>/(second|minute|hour|day)'"
        ) from e


def make_rate_limit(spec: str):
    """Return a FastAPI dependency enforcing ``count/window`` per client IP+path."""
    count, window = _parse_spec(spec)

    def _dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{client_ip}:{request.url.path}"
        now = time.monotonic()
        with _lock:
            bucket = _buckets[key]
            cutoff = now - window
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= count:
                retry_after = max(1, int(window - (now - bucket[0])))
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded ({spec})",
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)
            # Opportunistic cleanup of stale buckets (every append is cheap;
            # cap memory by dropping empty/dead keys occasionally)
            if len(_buckets) > 10_000:
                for k in [k for k, b in _buckets.items() if not b]:
                    del _buckets[k]

    return _dependency


def make_tenant_rate_limit(spec: str):
    """Return a FastAPI dependency enforcing ``count/window`` per tenant UUID.

    Keys by JWT ``sub`` claim (tenant UUID) + path. Falls back to IP if
    no valid tenant context is available (e.g. unauthenticated health checks).
    """
    count, window = _parse_spec(spec)

    def _dependency(request: Request) -> None:
        # Extract tenant UUID from request state (set by get_current_tenant_id)
        # or fall back to IP for unauthenticated endpoints
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            # Try to extract from Authorization header without full validation
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                try:
                    import jwt as pyjwt
                    from ..core.config import settings

                    token = auth[7:]
                    payload = pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
                    tenant_id = str(payload.get("sub", ""))
                except Exception:
                    pass

        if not tenant_id:
            client_ip = request.client.host if request.client else "unknown"
            tenant_id = f"anon:{client_ip}"

        key = f"tenant:{tenant_id}:{request.url.path}"
        now = time.monotonic()
        with _lock:
            bucket = _buckets[key]
            cutoff = now - window
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= count:
                retry_after = max(1, int(window - (now - bucket[0])))
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded ({spec})",
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)
            if len(_buckets) > 10_000:
                for k in [k for k, b in _buckets.items() if not b]:
                    del _buckets[k]

    return _dependency
