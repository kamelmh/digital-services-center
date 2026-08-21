"""SaaS API main — mounts v1 dossiers router alongside legacy api.py routes."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from ..app.core.config import settings
from ..app.middleware.rate_limiter import limiter

app = FastAPI(title=settings.app_name, version="1.0.0")

# Rate limiting — shared limiter with v1 routers (dossiers, billing)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request: JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"}),
)
app.add_middleware(SlowAPIMiddleware)

# CORS — tighten in prod (allow only frontend origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount new v1 routers
try:
    from ..app.routers.dossiers import router as dossiers_router

    app.include_router(dossiers_router)
except Exception as e:
    print(f"Failed to mount dossiers router: {e}")

try:
    from ..app.routers.billing import router as billing_router

    app.include_router(billing_router)
except Exception as e:
    print(f"Failed to mount billing router: {e}")

# Mount legacy tax/finance/pricing/quality routes from root api.py for backward compat
# (import side-effects register routes on the legacy `api` instance; we re-expose health)
try:
    import api as legacy_api

    # Re-export legacy app's routes under /legacy for debugging
    app.mount("/legacy", legacy_api.app)
except Exception as e:
    print(f"Legacy api mount skipped: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env, "storage": settings.storage_backend, "queue": settings.rq_queue_name}


@app.get("/")
def root():
    return {"message": settings.app_name, "docs": "/docs", "health": "/health", "v1": f"{settings.api_v1_prefix}/dossiers/feasibility"}
