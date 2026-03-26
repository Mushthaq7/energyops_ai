from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.log_config import setup_logging
from app.core.middleware import PrometheusMiddleware
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# Setup logging before app creation
setup_logging()

# Create database tables automatically
from app.db.session import engine
from app.models.base import Base
import app.models.energy  # Ensure tables are registered

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# ── Middleware (order matters: first added = outermost) ──
app.add_middleware(PrometheusMiddleware)

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


# ── Observability endpoints ──────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/metrics")
def metrics(request: Request):
    """Prometheus-compatible metrics endpoint. Restricted to internal network."""
    client_host = request.client.host if request.client else ""
    # Allow localhost and Docker internal (172.x.x.x) ranges only
    if not (client_host.startswith("172.") or client_host in ("127.0.0.1", "::1")):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
