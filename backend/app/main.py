"""
FinCloud-AI Backend - FastAPI Application
Main entry point for the application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
import json
import time

from app.core.settings import get_settings
from app.core.database import init_db, SessionLocal
from app.api.routes import cost, anomaly, forecast, recommendations, upload

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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _dbg_req(message: str, data: dict, hypothesis_id: str):
    try:
        payload = {
            "sessionId": "e15a98",
            "runId": "pre-fix",
            "hypothesisId": hypothesis_id,
            "location": "backend/app/main.py",
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(r"c:\Users\Haseeb\Desktop\FinCloud-AI\debug-e15a98.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass

@app.middleware("http")
async def debug_request_logger(request, call_next):
    _dbg_req(
        "Incoming request",
        {
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "origin": request.headers.get("origin"),
            "content_type": request.headers.get("content-type"),
        },
        "H1",
    )
    try:
        response = await call_next(request)
        _dbg_req(
            "Request complete",
            {"method": request.method, "path": request.url.path, "status": response.status_code},
            "H1",
        )
        return response
    except Exception as e:
        _dbg_req(
            "Request exception",
            {"method": request.method, "path": request.url.path, "error": str(e)[:500], "type": type(e).__name__},
            "H1",
        )
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
        db.execute("SELECT 1")
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


# Include routers
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
