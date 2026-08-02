"""
Career Assistant SaaS - FastAPI Backend
Main application entry point
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Career Assistant API starting...")
    yield
    # Shutdown
    logger.info("🛑 Career Assistant API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Career Assistant SaaS API",
    description="AI-powered platform for resume optimization and job matching",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware Configuration
# Trust proxy headers (important for deployed environments)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# CORS middleware
if settings.ENVIRONMENT == "development":
    origins = ["http://localhost:3000", "http://localhost:3001"]
else:
    origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
    }


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Career Assistant SaaS API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions"""
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# API Routes
from app.routes import auth, resume, parsing, profile, jobs, matching, optimization, cover_letters, applications, automation, interview, notifications, analytics, admin

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(parsing.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(optimization.router)
app.include_router(cover_letters.router)
app.include_router(applications.router)
app.include_router(automation.router)
app.include_router(interview.router)
app.include_router(notifications.router)
app.include_router(analytics.router)
app.include_router(admin.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

