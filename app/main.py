"""
NEXUS AI Engine - Main Application
FastAPI service for AI/ML features
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="NEXUS AI Engine",
    description="AI microservice for demand forecasting, invoice OCR, and ML recommendations",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "NEXUS AI Engine",
        "status": "running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "openai_configured": bool(settings.OPENAI_API_KEY),
    }

# Import routers (will be created in next tickets)
# from app.routers import demand, ocr, recommendations, chat
# app.include_router(demand.router, prefix="/api/v1", tags=["Demand Forecasting"])
# app.include_router(ocr.router, prefix="/api/v1", tags=["Invoice OCR"])
# app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
# app.include_router(chat.router, prefix="/api/v1", tags=["Chatbot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )
