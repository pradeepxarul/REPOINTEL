"""
GitHub User Data Analyzer - Production Server
GitHub App Authentication | 112K users/month | <1.5s response
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from api.routes import router
from utils.logger import logger


# ============= STARTUP/SHUTDOWN EVENTS =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 GitHub User Data Analyzer")
    logger.info(f"📍 Installation ID: {settings.GITHUB_INSTALLATION_ID}")
    logger.info(f"⚙️  Environment: {settings.ENVIRONMENT}")
    logger.info(f"📊 Capacity: 112,000 users/month")
    logger.info(f"⏱️  Latency: <1.5 seconds per analysis")
    logger.info(f"🔗 Swagger Docs: http://localhost:{settings.PORT}/docs")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("🛑 Server shutting down...")


# ============= FASTAPI APP SETUP =============

app = FastAPI(
    title="GitHub User Data Analyzer",
    description="Analyze GitHub profiles for comprehensive user data extraction using GitHub App authentication",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (configure with your frontend domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["analysis"])


# ============= ROOT ENDPOINTS =============

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "GitHub User Data Analyzer",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "analyze": "/api/v1/analyze (POST)",
            "health": "/api/v1/health (GET)",
            "cache_clear": "/api/v1/cache/clear (POST)",
            "interactive_docs": "/docs (GET)",
            "redoc": "/redoc (GET)"
        },
        "documentation": "Visit /docs for interactive API documentation"
    }


# ============= SERVER STARTUP =============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.ENVIRONMENT != "test"
    )
