"""
FinCloud-AI Backend - FastAPI Application
Main entry point for the application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.core.settings import get_settings
from app.core.database import init_db, SessionLocal
from sqlalchemy import text
from app.api.routes import cost, anomaly, forecast, recommendations, upload, aws, auth

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    """
    # Startup
    logger.info("Initializing FinCloud-AI Backend...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FinCloud-AI Backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade FinOps backend for cloud cost optimization",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    logger.debug(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path}: {e}")
        raise


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "FinCloud-AI Backend API",
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    try:
        # Try to get database session
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": settings.app_name,
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get(f"{settings.api_prefix}/health", tags=["health"])
async def api_health_check():
    """API-prefixed health check endpoint."""
    return await health_check()


# Include routers
app.include_router(
    auth.router,
    prefix=settings.api_prefix,
)
app.include_router(
    cost.router,
    prefix=settings.api_prefix,
)
app.include_router(
    anomaly.router,
    prefix=settings.api_prefix,
)
app.include_router(
    forecast.router,
    prefix=settings.api_prefix,
)
app.include_router(
    recommendations.router,
    prefix=settings.api_prefix,
)
app.include_router(
    upload.router,
    prefix=settings.api_prefix,
)
app.include_router(
    aws.router,
    prefix=settings.api_prefix,
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
