"""نقطه ورود اصلی برنامه FastAPI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import ScamReportException
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_startup", env=settings.app_env)
    yield
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="سامانه گزارش، اعتبارسنجی و اطلاع‌رسانی درباره کلاهبرداری‌های فضای مجازی",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.app_debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ScamReportException)
    async def domain_exception_handler(request: Request, exc: ScamReportException):
        status_map = {
            "NOT_FOUND": 404,
            "PERMISSION_DENIED": 403,
            "USER_BANNED": 403,
            "USER_RESTRICTED": 403,
            "VALIDATION_ERROR": 422,
            "INVALID_STATE_TRANSITION": 409,
            "DUPLICATE_REPORT": 200,
        }
        return JSONResponse(
            status_code=status_map.get(exc.code, 400),
            content={"error_code": exc.code, "message": exc.message},
        )

    app.include_router(api_router)

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
