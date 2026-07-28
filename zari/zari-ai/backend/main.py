"""
ZARI.ai Backend — FastAPI Application Entry Point
Stateless ASGI application designed for horizontal scaling.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.routes import router as api_router
from api.whatsapp_webhook import router as webhook_router


app = FastAPI(
    title="ZARI.ai API",
    description="Multi-modal agricultural crop disease diagnosis and advisory API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
app.include_router(api_router, prefix="/api", tags=["Diagnosis"])
app.include_router(webhook_router, prefix="/webhook", tags=["WhatsApp"])


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": "zari-ai-backend",
        "version": "1.0.0",
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    # TODO: Pre-load ONNX model session
    # TODO: Initialize ChromaDB client
    # TODO: Warm up faster-whisper model
    print("🌿 ZARI.ai Backend is starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("🌿 ZARI.ai Backend is shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
