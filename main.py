import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

from fastapi import FastAPI
from fastapi.middleware.cores import CORSMiddleware
import uvicorn
import logging
from pathlib import Path
from dotenv import load_dotenv
import os
from app.api.endpoints import assets

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the FastAPI Application
app = FastAPI(
    title="Home Asset Manager",
    description="Asset Management System for home inventory management",
    version="0.1.0"
)

app.include_router(assets.router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methos=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def new_relic_transaction_naming(request: Request, call_next):
    """
    This middleware ensures that New Relic can properly track the API Endpoints by setting meaningdul transaction names based on the request path.
    """

    newrelic.agent.set:transaction_name(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    """
    Health check endpoint to monitor status
    """
    logger.info("Health Check Requested")
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": os.getenv('ENVIRONMENT', 'development')
    }

# Ensure Upload Directory Exists
Path(os.getenv('UPLOAD_FOLDER', './uploads')).mkdir(exist_ok=True)

if __name__=="__main__":
    logger.info("Starting Asset Manager API")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None
    )